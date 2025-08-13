# quickmate_bot.py
import logging
import random
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from googletrans import Translator
import requests

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "8059468951:AAG2woZiKh05JK10tOtLac0tylsJFie5dMw"
WEATHER_API_KEY = "40222fb44bb4fffeafa1acae2a7bb798"

# Sample Pin Code Data
PIN_CODES = {
    "742212": {"Post Office": "Bagdabara", "District": "Murshidabad", "State": "West Bengal"},
    "700001": {"Post Office": "Kolkata GPO", "District": "Kolkata", "State": "West Bengal"},
}

# Sample Data
GK_QUIZZES = [
    {"q": "❓ Bharat ka rashtriya phool kya hai?", "options": ["Rose", "Lotus", "Tulip", "Sunflower"], "answer": "Lotus"},
    # Add 49 more GK questions here
]
JOKES = [
    "😂 Zindagi mein 3 cheezein important: Khana, sona, recharge.",
    # Add 49 more jokes here
]
QUOTES = [
    "🗨️ Kamyabi ka raaz ek word mein — 'Consistency'.",
    # Add 49 more quotes here
]
FACTS = [
    "💡 Pigeons complex memory tasks solve kar sakte hain.",
    # Add 49 more facts here
]

user_state = {}

# Main buttons
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
    ]
    return InlineKeyboardMarkup(keyboard)

# -------------------------
# External API helpers
# -------------------------
import requests

def fetch_weather(city: str):
    try:
        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": OWM_API_KEY,
            "units": "metric"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("cod") != "200":
            return None

        city_name = data["city"]["name"]
        humidity = None
        temp = None
        desc = None
        rain_chance = 0  # We'll calculate rain chance approx from forecasts

        # Extract forecast list (3-hour interval)
        forecast_list = data.get("list", [])

        # We'll look for rain data for today only (first 8 entries = 24 hours)
        today_forecasts = forecast_list[:8]

        rain_periods = 0
        rain_events = 0

        temps = []
        humidities = []
        descriptions = []

        for entry in today_forecasts:
            temps.append(entry["main"]["temp"])
            humidities.append(entry["main"]["humidity"])
            descriptions.append(entry["weather"][0]["description"].capitalize())

            # Check if rain volume exists for 3h period
            rain = entry.get("rain", {}).get("3h", 0)
            if rain > 0:
                rain_events += 1
            rain_periods += 1

        # Average temperature and humidity of today
        if temps:
            temp = sum(temps) / len(temps)
        if humidities:
            humidity = sum(humidities) / len(humidities)

        # Most common description for today (simple way)
        if descriptions:
            desc = max(set(descriptions), key=descriptions.count)

        # Approximate rain chance = (rain events / total periods) * 100
        if rain_periods > 0:
            rain_chance = (rain_events / rain_periods) * 100

        return {
            "city": city_name,
            "temp": round(temp, 1) if temp else None,
            "humidity": round(humidity, 1) if humidity else None,
            "pop": rain_chance,  # percent chance approx
            "desc": desc or "",
        }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None



# -------------------------
# Bot Handlers
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "QuickMate Mein Aapka Swagat Hai! Neeche Options Me Se Chunen :",
        reply_markup=main_buttons()
    )

# Callback handler for button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in user_state:
        user_state[user_id] = {}

    if data == "pin_code":
        user_state[user_id]["mode"] = "PIN_CODE_WAIT"
        await query.message.reply_text("📌 Please Enter 6-Digit PIN Code:")
    elif data == "translator":
        user_state[user_id]["mode"] = "TRANSLATOR_WAIT"
        await query.message.reply_text("📝 Please Send Me The Text You Want To Translate To English.")
    elif data == "gk_quiz":
        user_state[user_id]["mode"] = "GK_QUIZ"
        user_state[user_id]["quiz_index"] = -1
        await send_next_quiz(user_id, query)
    elif data == "jokes":
        user_state[user_id]["mode"] = "JOKES"
        user_state[user_id]["joke_index"] = -1
        await send_next_joke(user_id, query)
    elif data == "quotes":
        user_state[user_id]["mode"] = "QUOTES"
        user_state[user_id]["quote_index"] = -1
        await send_next_quote(user_id, query)
    elif data == "facts":
        user_state[user_id]["mode"] = "FACTS"
        user_state[user_id]["fact_index"] = -1
        await send_next_fact(user_id, query)
    elif data == "time_date":
        now = datetime.now()
        await query.message.reply_text(
            f"⏰ Time: {now.strftime('%I:%M %p')}\n📅 Date: {now.strftime('%d %B %Y')}",
            reply_markup=main_buttons()
        )
    elif data == "weather":
            user_state[user.id]["mode"] = "WEATHER_WAIT"
            await context.bot.send_message(query.message.chat_id, "🌤 Please Enter City Name:")
        return

# Message handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id not in user_state:
        await update.message.reply_text("❌ Please use /start to begin.", reply_markup=main_buttons())
        return

    mode = user_state[user_id].get("mode", "")

    if mode == "PIN_CODE_WAIT":
        # Call live PIN code API instead of local data
        await handle_pin_code(update, context)

    elif mode == "TRANSLATOR_WAIT":
        from googletrans import Translator
        translator = Translator()
        translation = translator.translate(text, dest='en').text
        await update.message.reply_text(f"🔤 {translation}", reply_markup=main_buttons())

    elif mode == "WEATHER_WAIT":
    city = text.strip()
    if not city:
        await update.message.reply_text("❌ Please enter a valid city name.")
        return

    waiting_msg = await update.message.reply_text("⌛ Please Wait A Moment ...")
    weather = await asyncio.to_thread(fetch_weather, city)

    if weather:
        resp = (
            f"🌤 Weather in {weather['city']}:\n"
            f"🌡 Temperature: {weather['temp']}°C\n"
            f"💧 Humidity: {weather['humidity']}%\n"
            f"🌦️ Rain (Today): {int(weather.get('pop',0))}%\n"
            f"📝 About: {weather['desc']}"
        )
        await waiting_msg.edit_text(resp)
    else:
        await waiting_msg.edit_text("❌ City not found or API error. Try another city.")

# Quiz / Jokes / Quotes / Facts helpers
async def send_next_quiz(user_id, query):
    index = user_state[user_id]["quiz_index"] + 1
    if index >= len(GK_QUIZZES):
        await query.message.reply_text("🎉 You have completed all quizzes!", reply_markup=main_buttons())
        return
    user_state[user_id]["quiz_index"] = index
    quiz = GK_QUIZZES[index]
    keyboard = [
        [InlineKeyboardButton(quiz["options"][0], callback_data=f"quiz_{index}_0"),
         InlineKeyboardButton(quiz["options"][1], callback_data=f"quiz_{index}_1")],
        [InlineKeyboardButton(quiz["options"][2], callback_data=f"quiz_{index}_2"),
         InlineKeyboardButton(quiz["options"][3], callback_data=f"quiz_{index}_3")],
    ]
    await query.message.reply_text(quiz["q"], reply_markup=InlineKeyboardMarkup(keyboard))

async def send_next_joke(user_id, query):
    index = user_state[user_id]["joke_index"] + 1
    if index >= len(JOKES):
        await query.message.reply_text("🎉 You have seen all jokes!", reply_markup=main_buttons())
        return
    user_state[user_id]["joke_index"] = index
    joke = JOKES[index]
    keyboard = [[InlineKeyboardButton("Next Joke", callback_data="jokes")]]
    await query.message.reply_text(joke, reply_markup=InlineKeyboardMarkup(keyboard))

async def send_next_quote(user_id, query):
    index = user_state[user_id]["quote_index"] + 1
    if index >= len(QUOTES):
        await query.message.reply_text("🎉 You have seen all quotes!", reply_markup=main_buttons())
        return
    user_state[user_id]["quote_index"] = index
    quote = QUOTES[index]
    keyboard = [[InlineKeyboardButton("Next Quote", callback_data="quotes")]]
    await query.message.reply_text(quote, reply_markup=InlineKeyboardMarkup(keyboard))

async def send_next_fact(user_id, query):
    index = user_state[user_id]["fact_index"] + 1
    if index >= len(FACTS):
        await query.message.reply_text("🎉 You have seen all facts!", reply_markup=main_buttons())
        return
    user_state[user_id]["fact_index"] = index
    fact = FACTS[index]
    keyboard = [[InlineKeyboardButton("Next Fact", callback_data="facts")]]
    await query.message.reply_text(fact, reply_markup=InlineKeyboardMarkup(keyboard))

# Quiz answer handler
async def quiz_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("quiz_"):
        _, q_index, opt_index = data.split("_")
        q_index, opt_index = int(q_index), int(opt_index)
        correct = GK_QUIZZES[q_index]["answer"]
        selected = GK_QUIZZES[q_index]["options"][opt_index]
        if selected == correct:
            await query.message.reply_text("✅ Great!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Next Quiz", callback_data="gk_quiz")]]))
        else:
            await query.message.reply_text(f"❌ Wrong! Correct answer: {correct}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Next Quiz", callback_data="gk_quiz")]]))

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(quiz_answer_handler, pattern=r"^quiz_\d+_\d+$"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("QuickMate Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
