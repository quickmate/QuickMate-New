# quickmate_bot_complete.py
import logging
import asyncio
import os
import re
import random
from datetime import datetime
import pytz
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaAudio, InputMediaVideo
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator
from keep_alive import keep_alive
import yt_dlp

# -------------------------
# Config
# -------------------------
BOT_TOKEN = "8059468951:AAG2woZiKh05JK10tOtLac0tylsJFie5dMw"
WEATHER_API_KEY = "40222fb44bb4fffeafa1acae2a7bb798"
PHONE_API_KEY = "cf69e1889ca10d81614c72e7060e2475"  # NumVerify API Key

# -------------------------
# Logging
# -------------------------
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Sample Data
# -------------------------
GK_QUIZZES = [
    {"q":"❓ Earth ka sabse bada continent kaunsa hai?", "options":["Asia","Africa","Europe","America"], "answer":"Asia"},
    {"q":"❓ Bharat ka rashtriya vriksh kaunsa hai?", "options":["Peepal","Banyan","Neem","Mango"], "answer":"Banyan"}
]

JOKES = [
    "😂 Ek banda doctor ke paas gaya: 'Doctor sahab, mujhe neend nahi aati.' Doctor: 'Aap din bhar kya karte ho?' Banda: 'Sota hoon.'",
    "😂 Teacher: 'Tumhara result kaisa hai?' Student: 'Sir, suspense movie jaisa.'"
]

QUOTES = [
    "🗨️ Kamyabi ka raaz: 'Consistency'.",
    "🗨️ Sapne wahi sach hote hain jo aap jagte hue dekhte ho.",
    "🗨️ Apni thinking positive rakho.",
    "🗨️ Struggle ke bina success ka maza nahi."
]

FACTS = [
    "💡 Aadmi ke body mein lagbhag 60% paani hota hai.",
    "💡 ISS 90 min mein earth ka ek chakkar lagata hai."
]

user_state = {}

# -------------------------
# Helpers
# -------------------------
def ensure_user(user_id):
    if user_id not in user_state:
        user_state[user_id] = {}

def get_randomized_list(items):
    lst = items.copy()
    random.shuffle(lst)
    return lst

def main_buttons():
    keyboard = [
        [InlineKeyboardButton("Pin Code Finder", callback_data="pin_code"),
         InlineKeyboardButton("Translator", callback_data="translator")],
        [InlineKeyboardButton("GK Quizzes", callback_data="gk_quiz"),
         InlineKeyboardButton("Jokes", callback_data="jokes")],
        [InlineKeyboardButton("Quotes", callback_data="quotes"),
         InlineKeyboardButton("Time & Date", callback_data="time_date")],
        [InlineKeyboardButton("Facts", callback_data="facts"),
         InlineKeyboardButton("Weather Info", callback_data="weather")],
        [InlineKeyboardButton("Audio Download", callback_data="audio_download"),
         InlineKeyboardButton("Phone Number Info", callback_data="phone_info")],
        [InlineKeyboardButton("Reels & Videos Download", callback_data="reels_download")]
    ]
    return InlineKeyboardMarkup(keyboard)

def fetch_weather(city: str):
    try:
        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        response = requests.get(url, params=params, timeout=10).json()
        if response.get("cod") != "200":
            return None

        city_name = response["city"]["name"]
        forecast_list = response.get("list", [])[:8]

        temps, humidities, descriptions = [], [], []
        rain_events, periods = 0, 0

        for entry in forecast_list:
            temps.append(entry["main"]["temp"])
            humidities.append(entry["main"]["humidity"])
            descriptions.append(entry["weather"][0]["description"].capitalize())
            if entry.get("rain", {}).get("3h", 0) > 0:
                rain_events += 1
            periods += 1

        temp = round(sum(temps)/len(temps),1) if temps else None
        humidity = round(sum(humidities)/len(humidities),1) if humidities else None
        desc = max(set(descriptions), key=descriptions.count) if descriptions else ""
        pop = (rain_events/periods)*100 if periods>0 else 0

        return {"city": city_name, "temp": temp, "humidity": humidity, "pop": pop, "desc": desc}
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

# -------------------------
# Pin Code Handler
# -------------------------
async def handle_pin_code(update: Update, context: ContextTypes.DEFAULT_TYPE, waiting_msg=None):
    user = update.effective_user
    ensure_user(user.id)

    if waiting_msg is None:
        waiting_msg = await update.message.reply_text("⌛ Please Wait A Moment ...")

    pin_code = update.message.text.strip()
    if not pin_code.isdigit() or len(pin_code) != 6:
        await waiting_msg.edit_text("❌ Please enter a valid 6-digit pin code.")
        return

    url = f"https://api.postalpincode.in/pincode/{pin_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = await asyncio.to_thread(requests.get, url, headers=headers, timeout=10)
        response = response.json()
    except Exception as e:
        await waiting_msg.edit_text(f"⚠ Error fetching pin code info: {e}")
        return

    if response and response[0]['Status'] == 'Success':
        office_data = response[0]['PostOffice'][0]
        result = (
            f"📌 **Pincode Information**\n"
            f"✅ Name: {office_data['Name']}\n"
            f"✅ District: {office_data['District']}\n"
            f"✅ State: {office_data['State']}\n"
            f"✅ Country: {office_data['Country']}"
        )
        await waiting_msg.edit_text(result, parse_mode="Markdown")
    else:
        await waiting_msg.edit_text("❌ Invalid PIN code. Please Try Again.")
    user_state[user.id]["mode"] = "PIN_CODE_WAIT"

# -------------------------
# Audio Download
# -------------------------
async def handle_audio_download(update: Update, context: ContextTypes.DEFAULT_TYPE, waiting_msg):
    user_id = update.message.from_user.id
    url = update.message.text.strip()
    try:
        await waiting_msg.edit_text("⌛ Please Wait A Moment ...\n🎧 It May Take A Few Minutes.")
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': f'audio_{user_id}.%(ext)s', 'quiet': True}
        await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        for file in os.listdir('.'):
            if file.startswith(f'audio_{user_id}.'):
                with open(file, 'rb') as f:
                    await context.bot.edit_message_media(
                        chat_id=update.effective_chat.id,
                        message_id=waiting_msg.message_id,
                        media=InputMediaAudio(media=f, caption="🎵 Save For Later!")
                    )
                os.remove(file)
                break
    except Exception as e:
        await waiting_msg.edit_text(f"❌ Failed to download audio: {e}")

# -------------------------
# Phone Info
# -------------------------
KNOWN_NUMBERS = {
    "+91112": "Emergency Services (All-in-One)",
    "+91100": "Police Control Room",
    "+91101": "Fire Service",
    "+91102": "Ambulance (Government)",
    "+91108": "Fire Brigade",
    "+91109": "Medical Emergency / Disaster / Women Helpline / Domestic Violence / Gas Leakage Emergency",
    "+91198": "Child Helpline (Childline 1098)"
    # add more as needed...
}

def get_known_number_name(number):
    for prefix, name in KNOWN_NUMBERS.items():
        if number.startswith(prefix):
            return name
    return "Unknown"

def numverify_lookup(number):
    url = f"https://apilayer.net/api/validate?access_key={PHONE_API_KEY}&number={number}&format=1"
    resp = requests.get(url)
    return resp.json()

async def handle_phone_info(update: Update, context: ContextTypes.DEFAULT_TYPE, waiting_msg):
    user_id = update.message.from_user.id
    phone_number = update.message.text.strip()
    try:
        name = get_known_number_name(phone_number)
        data = numverify_lookup(phone_number)
        if "error" in data:
            await waiting_msg.edit_text(f"❌ {data['error']}")
            return

        carrier = data.get("carrier") or "Unknown"
        carrier = re.sub(r"\(.*?\)", "", carrier).strip()
        country = data.get("country_name") or "Unknown"
        country = country.replace("Republic of", "").strip()
        city = data.get("location")
        location_str = f"{city}, {country}" if city and city.lower() != "unknown" else country

        response = (
            f"📞 Number : {phone_number}\n"
            f"👤 Name : {name}\n"
            f"📡 Carrier : {carrier}\n"
            f"🌍 Location : {location_str}"
        )
        await waiting_msg.edit_text(response)
        user_state[user_id]["mode"] = "PHONE_INFO_WAIT"

    except Exception as e:
        await waiting_msg.edit_text(f"⚠ Failed to fetch info: {e}")

# -------------------------
# Reels/Video Download
# -------------------------
async def handle_reels_download(update: Update, context: ContextTypes.DEFAULT_TYPE, waiting_msg):
    url = update.message.text.strip()
    try:
        await waiting_msg.edit_text("⌛ Please Wait A Moment ...\n🚀 It May Take A Few Minutes.")
        ydl_opts = {'outtmpl': f'video_{update.message.from_user.id}.%(ext)s', 'quiet': True}
        await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        for file in os.listdir('.'):
            if file.startswith(f'video_{update.message.from_user.id}.'):
                caption = "🎬 Save This Video For Later!"
                with open(file, 'rb') as f:
                    await context.bot.edit_message_media(
                        chat_id=update.effective_chat.id,
                        message_id=waiting_msg.message_id,
                        media=InputMediaVideo(media=f, caption=caption)
                    )
                os.remove(file)
                break
    except Exception as e:
        await waiting_msg.edit_text(f"❌ Failed to download video: {e}")

# -------------------------
# Start & Buttons
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "QuickMate Mein Aapka Swagat Hai! Neeche Options Me Se Chunen :",
        reply_markup=main_buttons()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    ensure_user(user_id)

    # Map buttons to modes
    button_modes = {
        "pin_code": ("PIN_CODE_WAIT", "📌 Please Enter 6-Digit PIN Code:"),
        "translator": ("TRANSLATOR_WAIT", "📝 Send Text To Translate To English."),
        "audio_download": ("AUDIO_DOWNLOAD_WAIT", "🎵 Send Video Link To Download Audio :"),
        "phone_info": ("PHONE_INFO_WAIT", "📞 Please Enter Phone Number With Country Code Example : +919876543210"),
        "reels_download": ("REELS_DOWNLOAD_WAIT", "🎬 Send Video/Reels Link To Download :"),
        "gk_quiz": ("GK_QUIZ", None),
        "jokes": ("JOKES", None),
        "quotes": ("QUOTES", None),
        "facts": ("FACTS", None),
        "time_date": ("TIME_DATE", None),
        "weather": ("WEATHER_WAIT", "🌤 Please Enter City Name:")
    }

    if data in button_modes:
        mode, prompt = button_modes[data]
        user_state[user_id]["mode"] = mode
        if prompt:
            await query.message.reply_text(prompt)
        if data in ["gk_quiz","jokes","quotes","facts"]:
            # Randomize and reset indices
            if data=="gk_quiz":
                user_state[user_id]["quiz_list"] = get_randomized_list(GK_QUIZZES)
                user_state[user_id]["quiz_index"] = -1
                await send_next_quiz(user_id, query)
            elif data=="jokes":
                user_state[user_id]["joke_list"] = get_randomized_list(JOKES)
                user_state[user_id]["joke_index"] = -1
                await send_next_joke(user_id, query)
            elif data=="quotes":
                user_state[user_id]["quote_list"] = get_randomized_list(QUOTES)
                user_state[user_id]["quote_index"] = -1
                await send_next_quote(user_id, query)
            elif data=="facts":
                user_state[user_id]["fact_list"] = get_randomized_list(FACTS)
                user_state[user_id]["fact_index"] = -1
                await send_next_fact(user_id, query)
    elif data.startswith("quiz_"):
        await quiz_answer_handler(update, context)

# -------------------------
# Message Handler
# -------------------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    waiting_msg = await update.message.reply_text("⌛ Please Wait A Moment ...")
    if user_id not in user_state:
        await waiting_msg.edit_text("❌ Use /start first.")
        return

    mode = user_state[user_id].get("mode", "")

    try:
        if mode == "PIN_CODE_WAIT":
            await handle_pin_code(update, context, waiting_msg)
        elif mode == "TRANSLATOR_WAIT":
            translation = await asyncio.to_thread(GoogleTranslator(source='auto', target='en').translate, text)
            await waiting_msg.edit_text(f"🔤 {translation}")
        elif mode == "WEATHER_WAIT":
            weather = await asyncio.to_thread(fetch_weather, text)
            if weather:
                resp = (f"🌤 Weather in {weather['city']}:\n"
                        f"🌡 Temperature: {weather['temp']}°C\n"
                        f"💧 Humidity: {weather['humidity']}%\n"
                        f"🌦 Rain (Today): {int(weather.get('pop',0))}%\n"
                        f"📝 About: {weather['desc']}")
                await waiting_msg.edit_text(resp)
            else:
                await waiting_msg.edit_text("❌ City Not Found, Please Try Again.")
        elif mode == "AUDIO_DOWNLOAD_WAIT":
            await handle_audio_download(update, context, waiting_msg)
        elif mode == "PHONE_INFO_WAIT":
            await handle_phone_info(update, context, waiting_msg)
        elif mode == "REELS_DOWNLOAD_WAIT":
            await handle_reels_download(update, context, waiting_msg)
        else:
            await waiting_msg.delete()
    except Exception as e:
        await waiting_msg.edit_text(f"❌ Error: {e}")

# -------------------------
# Quiz Handlers
# -------------------------
async def send_next_quiz(user_id, query):
    index = user_state[user_id].get("quiz_index", -1) + 1
    quiz_list = user_state[user_id]["quiz_list"]
    if index >= len(quiz_list):
        await query.message.reply_text("🎉 Completed all quizzes!", reply_markup=main_buttons())
        user_state[user_id]["quiz_index"] = -1
        return
    user_state[user_id]["quiz_index"] = index
    quiz = quiz_list[index]
    keyboard = [
        [InlineKeyboardButton(quiz["options"][0], callback_data=f"quiz_{index}_0"),
         InlineKeyboardButton(quiz["options"][1], callback_data=f"quiz_{index}_1")],
        [InlineKeyboardButton(quiz["options"][2], callback_data=f"quiz_{index}_2"),
         InlineKeyboardButton(quiz["options"][3], callback_data=f"quiz_{index}_3")]
    ]
    await query.message.reply_text(quiz["q"], reply_markup=InlineKeyboardMarkup(keyboard))

async def quiz_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("quiz_"):
        parts = data.split("_")
        q_index, opt_index = int(parts[1]), int(parts[2])
        quiz_list = user_state[user_id]["quiz_list"]
        quiz = quiz_list[q_index]
        correct = quiz["answer"]
        selected = quiz["options"][opt_index]

        if selected == correct:
            await query.message.reply_text(
                "✅ Great!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Next Quiz", callback_data="gk_quiz")]])
            )
        else:
            await query.message.reply_text(
                f"❌ Wrong! Correct answer: {correct}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Next Quiz", callback_data="gk_quiz")]])
            )

# -------------------------
# Jokes/Quotes/Facts Handlers
# -------------------------
async def send_next_joke(user_id, query):
    index = user_state[user_id].get("joke_index", -1) + 1
    joke_list = user_state[user_id]["joke_list"]
    if index >= len(joke_list):
        await query.message.reply_text("🎉 All jokes completed!", reply_markup=main_buttons())
        user_state[user_id]["joke_index"] = -1
        return
    user_state[user_id]["joke_index"] = index
    await query.message.reply_text(joke_list[index], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Next Joke", callback_data="jokes")]]))

async def send_next_quote(user_id, query):
    index = user_state[user_id].get("quote_index", -1) + 1
    quote_list = user_state[user_id]["quote_list"]
    if index >= len(quote_list):
        await query.message.reply_text("🎉 All quotes completed!", reply_markup=main_buttons())
        user_state[user_id]["quote_index"] = -1
        return
    user_state[user_id]["quote_index"] = index
    await query.message.reply_text(quote_list[index], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Next Quote", callback_data="quotes")]]))

async def send_next_fact(user_id, query):
    index = user_state[user_id].get("fact_index", -1) + 1
    fact_list = user_state[user_id]["fact_list"]
    if index >= len(fact_list):
        await query.message.reply_text("🎉 All facts completed!", reply_markup=main_buttons())
        user_state[user_id]["fact_index"] = -1
        return
    user_state[user_id]["fact_index"] = index
    await query.message.reply_text(fact_list[index], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Next Fact", callback_data="facts")]]))

# -------------------------
# Main
# -------------------------
async def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
