# quickmate_bot_fixed_complete.py
import logging
import asyncio
from datetime import datetime
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator
import requests
import random

# -------------------------
# Config
# -------------------------
BOT_TOKEN = "8059468951:AAG2woZiKh05JK10tOtLac0tylsJFie5dMw"
WEATHER_API_KEY = "40222fb44bb4fffeafa1acae2a7bb798"

# -------------------------
# Logging
# -------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------------
# Sample Data
# -------------------------
GK_QUIZZES = [
    {"q":"❓ Earth ka sabse bada continent kaunsa hai?","options":["Asia","Africa","Europe","America"],"answer":"Asia"},
    {"q":"❓ Solar system ka sabse bada planet kaunsa hai?","options":["Jupiter","Saturn","Neptune","Earth"],"answer":"Jupiter"},
    {"q":"❓ World ka tallest mountain kaunsa hai?","options":["Everest","K2","Kangchenjunga","Lhotse"],"answer":"Everest"},
    {"q":"❓ USA ki rajdhani kaunsi hai?","options":["Washington D.C.","New York","Los Angeles","Chicago"],"answer":"Washington D.C."},
    {"q":"❓ Bharat ka rashtriya phool kya hai?","options":["Lotus","Rose","Sunflower","Tulip"],"answer":"Lotus"},
    {"q":"❓ India ki sabse badi nadi kaunsi hai?","options":["Ganga","Yamuna","Godavari","Krishna"],"answer":"Ganga"},
    {"q":"❓ Water ka chemical formula kya hai?","options":["H2O","CO2","O2","NaCl"],"answer":"H2O"},
    {"q":"❓ Light ki speed approximately kitni hai?","options":["3x10^8 m/s","3x10^6 m/s","1x10^8 m/s","1x10^6 m/s"],"answer":"3x10^8 m/s"},
    {"q":"❓ World ka largest ocean kaunsa hai?","options":["Pacific Ocean","Atlantic Ocean","Indian Ocean","Arctic Ocean"],"answer":"Pacific Ocean"},
    {"q":"❓ Bharat ka rashtriya pashu kya hai?","options":["Tiger","Lion","Elephant","Cow"],"answer":"Tiger"},
    {"q":"❓ Moon par pehla human kaun gaya tha?","options":["Neil Armstrong","Buzz Aldrin","Yuri Gagarin","Michael Collins"],"answer":"Neil Armstrong"},
    {"q":"❓ Earth ka largest desert kaunsa hai?","options":["Sahara","Gobi","Kalahari","Thar"],"answer":"Sahara"},
    {"q":"❓ Human body me kitne bones hote hain?","options":["206","205","210","201"],"answer":"206"},
    {"q":"❓ Computer ka father kaun hai?","options":["Charles Babbage","Alan Turing","Bill Gates","Steve Jobs"],"answer":"Charles Babbage"},
    {"q":"❓ Bharat ka rashtriya pakshi kya hai?","options":["Peacock","Sparrow","Eagle","Parrot"],"answer":"Peacock"},
    {"q":"❓ World ka longest river kaunsa hai?","options":["Nile","Amazon","Yangtze","Mississippi"],"answer":"Nile"},
    {"q":"❓ USA ka Independence Day kab hai?","options":["4th July","1st July","15th August","14th July"],"answer":"4th July"},
    {"q":"❓ Bharat ki rajdhani kaunsi hai?","options":["New Delhi","Mumbai","Kolkata","Chennai"],"answer":"New Delhi"},
    {"q":"❓ World ka largest country area wise kaunsa hai?","options":["Russia","Canada","China","USA"],"answer":"Russia"},
    {"q":"❓ Bharat ka rashtriya phal kya hai?","options":["Mango","Apple","Banana","Orange"],"answer":"Mango"},
    {"q":"❓ Light ka unit kya hai?","options":["Candela","Watt","Lumen","Lux"],"answer":"Candela"},
    {"q":"❓ Earth ka center primarily kis cheez se bana hai?","options":["Iron & Nickel","Copper","Gold","Aluminum"],"answer":"Iron & Nickel"},
    {"q":"❓ World ka highest waterfall kaunsa hai?","options":["Angel Falls","Niagara","Victoria Falls","Iguazu Falls"],"answer":"Angel Falls"},
    {"q":"❓ Bharat ka rashtriya khel kya hai?","options":["Hockey","Cricket","Football","Kabaddi"],"answer":"Hockey"},
    {"q":"❓ Human blood ka major component kya hai?","options":["Plasma","Platelets","Red Cells","White Cells"],"answer":"Plasma"},
    {"q":"❓ World ka fastest land animal kaunsa hai?","options":["Cheetah","Lion","Tiger","Leopard"],"answer":"Cheetah"},
    {"q":"❓ Bharat ki sabse unchi choti kaunsi hai?","options":["Kanchenjunga","Nanda Devi","Himalaya","Everest"],"answer":"Kanchenjunga"},
    {"q":"❓ Computer ki memory ka smallest unit kya hai?","options":["Bit","Byte","Nibble","Word"],"answer":"Bit"},
    {"q":"❓ World ka largest island kaunsa hai?","options":["Greenland","New Guinea","Borneo","Madagascar"],"answer":"Greenland"},
    {"q":"❓ India ki sabse badi jheel kaunsi hai?","options":["Vembanad","Chilika","Dal","Sambhar"],"answer":"Vembanad"},
    {"q":"❓ Speed of sound approx kitna hai?","options":["343 m/s","300 m/s","3400 m/s","34.3 m/s"],"answer":"343 m/s"},
    {"q":"❓ World ka oldest university kaunsa hai?","options":["Al-Qarawiyyin","Oxford","Harvard","Cambridge"],"answer":"Al-Qarawiyyin"},
    {"q":"❓ Bharat ka rashtriya nagar kya hai?","options":["New Delhi","Mumbai","Kolkata","Chennai"],"answer":"New Delhi"},
    {"q":"❓ World ka largest desert kaunsa hai?","options":["Sahara","Arctic","Gobi","Kalahari"],"answer":"Sahara"},
    {"q":"❓ Human heart kitne chambers ka hota hai?","options":["4","2","3","5"],"answer":"4"},
    {"q":"❓ Bharat ka rashtriya jaljeev kya hai?","options":["Gangetic Dolphin","Crocodile","Turtle","Shark"],"answer":"Gangetic Dolphin"},
    {"q":"❓ World ka smallest country kaunsa hai?","options":["Vatican City","Monaco","Nauru","Malta"],"answer":"Vatican City"},
    {"q":"❓ Bharat ka rashtriya vanaspati kya hai?","options":["Banyan","Neem","Peepal","Mango"],"answer":"Banyan"},
    {"q":"❓ Olympics ka founder kaun tha?","options":["Pierre de Coubertin","Baron de Coubertin","William Penny","None"],"answer":"Pierre de Coubertin"},
    {"q":"❓ World ka longest railway kaunsa hai?","options":["Trans-Siberian","Indian Railways","Canada","USA"],"answer":"Trans-Siberian"},
    {"q":"❓ Human brain ka approx weight kitna hota hai?","options":["1.4 kg","1 kg","2 kg","1.6 kg"],"answer":"1.4 kg"},
    {"q":"❓ World ka largest volcano kaunsa hai?","options":["Mauna Loa","Mount Fuji","Etna","Vesuvius"],"answer":"Mauna Loa"},
    {"q":"❓ World ka most populated country kaunsa hai?","options":["China","India","USA","Indonesia"],"answer":"China"},
    {"q":"❓ Speed of light approx kitni hai?","options":["3x10^8 m/s","3x10^6 m/s","1x10^8 m/s","1x10^6 m/s"],"answer":"3x10^8 m/s"},
    {"q":"❓ World ka deepest ocean kaunsa hai?","options":["Pacific","Atlantic","Indian","Arctic"],"answer":"Pacific"},
    {"q":"❓ Bharat ka rashtriya dhol kaunsa hai?","options":["Dhol","Mridangam","Tabla","Pakhawaj"],"answer":"Dhol"},
    {"q":"❓ World ka largest lake kaunsa hai?","options":["Caspian Sea","Lake Superior","Lake Victoria","Aral Sea"],"answer":"Caspian Sea"},
    {"q":"❓ Bharat ka national emblem kaun sa hai?","options":["Lion Capital of Ashoka","Tiger","Elephant","Peacock"],"answer":"Lion Capital of Ashoka"},
    {"q":"❓ First man in space kaun tha?","options":["Yuri Gagarin","Neil Armstrong","Buzz Aldrin","John Glenn"],"answer":"Yuri Gagarin"},
    {"q":"❓ Bharat ki sabse lambi nadi kaunsi hai?","options":["Ganga","Godavari","Yamuna","Krishna"],"answer":"Ganga"},
    {"q":"❓ World ka first country jahan Internet aya?","options":["USA","UK","Russia","China"],"answer":"USA"},
    {"q":"❓ Bharat ka rashtriya shabd kya hai?","options":["Satyamev Jayate","Vande Mataram","Jai Hind","None"],"answer":"Satyamev Jayate"},
    {"q":"❓ World ka largest rainforest kaunsa hai?","options":["Amazon","Congo","Southeast Asia","Daintree"],"answer":"Amazon"},
    {"q": "❓ World ka sabse chhota desh kaunsa hai?", "options": ["Vatican City", "Monaco", "San Marino", "Malta"], "answer": "Vatican City"},
    {"q": "❓ Chand par pehla kadam rakhne wale vyakti ka naam kya hai?", "options": ["Neil Armstrong", "Buzz Aldrin", "Yuri Gagarin", "Michael Collins"], "answer": "Neil Armstrong"},
    {"q": "❓ Taj Mahal kis shaher mein hai?", "options": ["Agra", "Delhi", "Jaipur", "Lucknow"], "answer": "Agra"},
    {"q": "❓ Facebook ka founder kaun hai?", "options": ["Mark Zuckerberg", "Elon Musk", "Bill Gates", "Larry Page"], "answer": "Mark Zuckerberg"},
    {"q": "❓ Bharat ka sabse bada rajya area ke hisaab se kaunsa hai?", "options": ["Rajasthan", "Madhya Pradesh", "Maharashtra", "Uttar Pradesh"], "answer": "Rajasthan"},
    {"q": "❓ Google ka parent company ka naam kya hai?", "options": ["Alphabet", "Meta", "Microsoft", "Amazon"], "answer": "Alphabet"},
    {"q": "❓ Sachin Tendulkar ko kis naam se jana jata hai?", "options": ["God of Cricket", "Master Blaster", "Little Master", "Sabhi"], "answer": "Sabhi"},
    {"q": "❓ Eiffel Tower kis desh mein hai?", "options": ["France", "Italy", "Germany", "Spain"], "answer": "France"},
    {"q": "❓ Amazon ka founder kaun hai?", "options": ["Jeff Bezos", "Elon Musk", "Bill Gates", "Steve Jobs"], "answer": "Jeff Bezos"},
    {"q": "❓ Bharat ka rashtriya phool kaunsa hai?", "options": ["Kamal", "Gulab", "Surajmukhi", "Rajnigandha"], "answer": "Kamal"},
    {"q": "❓ WhatsApp kis company ka hissa hai?", "options": ["Meta", "Google", "Microsoft", "Apple"], "answer": "Meta"},
    {"q": "❓ World ka sabse bada ocean kaunsa hai?", "options": ["Pacific", "Atlantic", "Indian", "Arctic"], "answer": "Pacific"},
    {"q": "❓ NASA ka full form kya hai?", "options": ["National Aeronautics and Space Administration", "North American Space Agency", "National Air Space Agency", "None"], "answer": "National Aeronautics and Space Administration"},
    {"q": "❓ Red Planet kis grah ko kaha jata hai?", "options": ["Mars", "Venus", "Jupiter", "Saturn"], "answer": "Mars"},
    {"q": "❓ Microsoft ke founder kaun hai?", "options": ["Bill Gates", "Steve Jobs", "Larry Page", "Mark Zuckerberg"], "answer": "Bill Gates"},
    {"q": "❓ Statue of Liberty kis desh mein hai?", "options": ["USA", "UK", "France", "Canada"], "answer": "USA"},
    {"q": "❓ Water ka chemical formula kya hai?", "options": ["H2O", "CO2", "O2", "NaCl"], "answer": "H2O"},
    {"q": "❓ Twitter ka bird logo ka rang kya hai?", "options": ["Blue", "Green", "Yellow", "Black"], "answer": "Blue"},
    {"q": "❓ World ka sabse tez jaanwar kaunsa hai?", "options": ["Cheetah", "Tiger", "Horse", "Leopard"], "answer": "Cheetah"},
    {"q": "❓ IPL ka pehla season kisne jeeta?", "options": ["Rajasthan Royals", "Chennai Super Kings", "Mumbai Indians", "Kolkata Knight Riders"], "answer": "Rajasthan Royals"},
    {"q": "❓ FIFA World Cup 2022 kisne jeeta?", "options": ["Argentina", "France", "Germany", "Brazil"], "answer": "Argentina"},
    {"q": "❓ World ka tallest building ka naam kya hai?", "options": ["Burj Khalifa", "Shanghai Tower", "Abraj Al-Bait", "One World Trade Center"], "answer": "Burj Khalifa"},
    {"q": "❓ Bharat ka rashtriya panchi kaunsa hai?", "options": ["Mor", "Koyal", "Kabootar", "Bulbul"], "answer": "Mor"},
    {"q": "❓ WhatsApp kis saal launch hua tha?", "options": ["2009", "2007", "2010", "2012"], "answer": "2009"},
    {"q": "❓ Mona Lisa painting kisne banayi?", "options": ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Michelangelo"], "answer": "Leonardo da Vinci"},
    {"q": "❓ YouTube ka founder kaun hai?", "options": ["Steve Chen, Chad Hurley, Jawed Karim", "Larry Page", "Mark Zuckerberg", "Bill Gates"], "answer": "Steve Chen, Chad Hurley, Jawed Karim"},
    {"q": "❓ Bharat ka pehla Prime Minister kaun tha?", "options": ["Jawaharlal Nehru", "Mahatma Gandhi", "Sardar Patel", "Lal Bahadur Shastri"], "answer": "Jawaharlal Nehru"},
    {"q": "❓ Human body mein kitni haddi hoti hai?", "options": ["206", "208", "210", "212"], "answer": "206"},
    {"q": "❓ World ka sabse bada desert kaunsa hai?", "options": ["Sahara", "Gobi", "Kalahari", "Arabian"], "answer": "Sahara"},
    {"q": "❓ Google ka launch year kaunsa hai?", "options": ["1998", "1995", "2000", "1996"], "answer": "1998"},
    {"q": "❓ World ka fastest train kaunsi hai?", "options": ["Shanghai Maglev", "Bullet Train", "TGV", "Eurostar"], "answer": "Shanghai Maglev"},
    {"q": "❓ Indian Railways ka headquarter kahan hai?", "options": ["New Delhi", "Mumbai", "Kolkata", "Chennai"], "answer": "New Delhi"},
    {"q": "❓ Bharat ka rashtriya khel kaunsa hai?", "options": ["Hockey", "Cricket", "Kabaddi", "Football"], "answer": "Hockey"},
    {"q": "❓ Bitcoin kisne banaya?", "options": ["Satoshi Nakamoto", "Elon Musk", "Vitalik Buterin", "Bill Gates"], "answer": "Satoshi Nakamoto"},
    {"q": "❓ Instagram kis saal launch hua tha?", "options": ["2010", "2008", "2012", "2014"], "answer": "2010"},
    {"q": "❓ Penicillin kisne discover kiya?", "options": ["Alexander Fleming", "Marie Curie", "Louis Pasteur", "Isaac Newton"], "answer": "Alexander Fleming"},
    {"q": "❓ Bharat ka rashtriya jaanwar kaunsa hai?", "options": ["Bagh", "Hathi", "Sher", "Singh"], "answer": "Bagh"},
    {"q": "❓ Apple company ka current CEO kaun hai? (2025)", "options": ["Tim Cook", "Steve Jobs", "Sundar Pichai", "Satya Nadella"], "answer": "Tim Cook"},
    {"q": "❓ WhatsApp ke logo ka rang kya hai?", "options": ["Green", "Blue", "Yellow", "Red"], "answer": "Green"},
    {"q": "❓ World ka sabse bada island kaunsa hai?", "options": ["Greenland", "New Guinea", "Borneo", "Madagascar"], "answer": "Greenland"},
    {"q": "❓ Bharat ka pehla satellite kaunsa tha?", "options": ["Aryabhata", "Rohini", "INSAT-1A", "Bhaskara"], "answer": "Aryabhata"},
    {"q": "❓ Mount Everest ki unchai kitni hai?", "options": ["8848 m", "8880 m", "8840 m", "8820 m"], "answer": "8848 m"},
    {"q": "❓ Cricket World Cup 2011 kisne jeeta?", "options": ["India", "Sri Lanka", "Australia", "Pakistan"], "answer": "India"},
    {"q": "❓ Bharat ka rashtriya geet ka naam kya hai?", "options": ["Vande Mataram", "Jana Gana Mana", "Saare Jahan Se Achha", "None"], "answer": "Vande Mataram"},
    {"q": "❓ Oxygen ka chemical symbol kya hai?", "options": ["O", "O2", "Ox", "Oy"], "answer": "O"},
    {"q": "❓ World ka sabse zyada population wala desh kaunsa hai? (2025)", "options": ["India", "China", "USA", "Indonesia"], "answer": "India"},
    {"q": "❓ Chand ka rashtriya upagrah kis grah ka hai?", "options": ["Prithvi", "Mars", "Jupiter", "Venus"], "answer": "Prithvi"},
    {"q": "❓ Solar System ka sabse bada planet kaunsa hai?", "options": ["Jupiter", "Saturn", "Neptune", "Uranus"], "answer": "Jupiter"},
    {"q": "❓ Bharat ka pehla Rashtrapati kaun tha?", "options": ["Dr. Rajendra Prasad", "Sarvepalli Radhakrishnan", "Zakir Husain", "V. V. Giri"], "answer": "Dr. Rajendra Prasad"},
    {"q": "❓ Human body mein kitni haddi hoti hai?", "options": ["206", "208", "210", "212"], "answer": "206"},
    {"q": "❓ Bharat ka rashtriya phool kaunsa hai?", "options": ["Gulab", "Kamal", "Sunflower", "Tulip"], "answer": "Kamal"},
    {"q": "❓ World War II ka ant kis saal hua?", "options": ["1942", "1943", "1945", "1947"], "answer": "1945"},
    {"q": "❓ Taj Mahal kisne banwaya tha?", "options": ["Akbar", "Shah Jahan", "Aurangzeb", "Babur"], "answer": "Shah Jahan"},
    {"q": "❓ Cricket World Cup 2011 kisne jeeta?", "options": ["India", "Australia", "Sri Lanka", "Pakistan"], "answer": "India"},
    {"q": "❓ Bharat ka rashtriya pashu kaunsa hai?", "options": ["Lion", "Tiger", "Elephant", "Leopard"], "answer": "Tiger"},
    {"q": "❓ Duniya ka sabse lamba nadi kaunsa hai?", "options": ["Nile", "Amazon", "Yangtze", "Mississippi"], "answer": "Nile"},
    {"q": "❓ Light ka speed vacuum me kitna hota hai?", "options": ["3×10^8 m/s", "1×10^6 m/s", "5×10^8 m/s", "2×10^7 m/s"], "answer": "3×10^8 m/s"},
    {"q": "❓ Mahatma Gandhi ka janm kab hua tha?", "options": ["2 October 1869", "15 August 1947", "26 January 1950", "10 April 1890"], "answer": "2 October 1869"},
    {"q": "❓ Mount Everest kis do desh ke beech hai?", "options": ["India-China", "Nepal-China", "India-Nepal", "China-Bhutan"], "answer": "Nepal-China"},
    {"q": "❓ Oxygen ka chemical symbol kya hai?", "options": ["Ox", "O", "O2", "Oy"], "answer": "O"},
    {"q": "❓ Bharat ka pehla upagrah kaunsa tha?", "options": ["Aryabhata", "Rohini", "INSAT-1A", "Bhaskara"], "answer": "Aryabhata"},
    {"q": "❓ Asia ka sabse chhota desh kaunsa hai?", "options": ["Maldives", "Sri Lanka", "Bhutan", "Nepal"], "answer": "Maldives"},
    {"q": "❓ IPL 2020 ka winner kaun tha?", "options": ["Mumbai Indians", "Chennai Super Kings", "Delhi Capitals", "Kolkata Knight Riders"], "answer": "Mumbai Indians"},
    {"q": "❓ Computer ka father kisko kaha jata hai?", "options": ["Alan Turing", "Charles Babbage", "Bill Gates", "Steve Jobs"], "answer": "Charles Babbage"},
    {"q": "❓ Bharat me rail seva kis saal shuru hui thi?", "options": ["1853", "1860", "1845", "1870"], "answer": "1853"},
    {"q": "❓ World’s largest desert kaunsa hai?", "options": ["Sahara", "Gobi", "Kalahari", "Arctic"], "answer": "Sahara"},
    {"q": "❓ Bharat ka rashtriya geet kaun sa hai?", "options": ["Jana Gana Mana", "Vande Mataram", "Saare Jahan Se Achha", "Ae Mere Watan Ke Logon"], "answer": "Vande Mataram"},
    {"q": "❓ Facebook ka founder kaun hai?", "options": ["Elon Musk", "Bill Gates", "Mark Zuckerberg", "Larry Page"], "answer": "Mark Zuckerberg"},
    {"q": "❓ Sunflower oil kis plant se banta hai?", "options": ["Sunflower", "Olive", "Soybean", "Coconut"], "answer": "Sunflower"},
    {"q": "❓ Telephone ka avishkar kisne kiya?", "options": ["Alexander Graham Bell", "Thomas Edison", "Nikola Tesla", "Michael Faraday"], "answer": "Alexander Graham Bell"},
    {"q": "❓ Bharat ka sabse bada rajya area ke hisaab se kaunsa hai?", "options": ["Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "Maharashtra"], "answer": "Rajasthan"},
    {"q": "❓ World’s highest waterfall kaunsa hai?", "options": ["Niagara Falls", "Angel Falls", "Iguazu Falls", "Victoria Falls"], "answer": "Angel Falls"},
    {"q": "❓ Penicillin ka discovery kisne kiya?", "options": ["Louis Pasteur", "Alexander Fleming", "Marie Curie", "Joseph Lister"], "answer": "Alexander Fleming"},
    {"q": "❓ India ka pehla Prime Minister kaun tha?", "options": ["Mahatma Gandhi", "Jawaharlal Nehru", "Sardar Patel", "Rajendra Prasad"], "answer": "Jawaharlal Nehru"},
    {"q": "❓ Hindi Diwas kab manaya jata hai?", "options": ["26 January", "14 September", "15 August", "2 October"], "answer": "14 September"},
    {"q": "❓ Duniya ka sabse tez janwar kaunsa hai?", "options": ["Cheetah", "Leopard", "Horse", "Lion"], "answer": "Cheetah"},
    {"q": "❓ Bharat me kitne rashtriya chinh hote hain?", "options": ["4", "5", "3", "6"], "answer": "4"},
    {"q": "❓ Which planet is known as the Red Planet?", "options": ["Venus", "Mars", "Jupiter", "Mercury"], "answer": "Mars"},
    {"q": "❓ Google ka co-founder kaun hai?", "options": ["Larry Page", "Elon Musk", "Bill Gates", "Mark Zuckerberg"], "answer": "Larry Page"},
    {"q": "❓ World’s smallest bird kaunsa hai?", "options": ["Sparrow", "Hummingbird", "Parrot", "Kingfisher"], "answer": "Hummingbird"},
    {"q": "❓ Statue of Unity kis rajya me hai?", "options": ["Gujarat", "Maharashtra", "Rajasthan", "Punjab"], "answer": "Gujarat"},
    {"q": "❓ Apple company ka founder kaun tha?", "options": ["Steve Jobs", "Bill Gates", "Elon Musk", "Jeff Bezos"], "answer": "Steve Jobs"},
    {"q": "❓ Asia ka sabse bada railway station kaunsa hai?", "options": ["Howrah", "Gorakhpur", "Chhatrapati Shivaji", "New Delhi"], "answer": "Gorakhpur"},
    {"q": "❓ Which gas is most abundant in Earth’s atmosphere?", "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Helium"], "answer": "Nitrogen"},
    {"q": "❓ Bharat ka rashtriya khel kaunsa hai?", "options": ["Cricket", "Hockey", "Kabaddi", "Football"], "answer": "Hockey"},
    {"q": "❓ Titanic ship kis saal dooba tha?", "options": ["1910", "1912", "1914", "1920"], "answer": "1912"},
    {"q": "❓ First man to walk on moon kaun tha?", "options": ["Yuri Gagarin", "Neil Armstrong", "Buzz Aldrin", "Michael Collins"], "answer": "Neil Armstrong"},
    {"q": "❓ Which organ purifies blood in human body?", "options": ["Heart", "Kidney", "Liver", "Lungs"], "answer": "Kidney"},
    {"q": "❓ India ka sabse uncha dam kaunsa hai?", "options": ["Tehri Dam", "Bhakra Nangal", "Sardar Sarovar", "Hirakud"], "answer": "Tehri Dam"},
    {"q": "❓ Bharat ka rashtriya vriksh kaunsa hai?", "options": ["Peepal", "Banyan", "Neem", "Mango"], "answer": "Banyan"}  
]

JOKES = [
    "😂 Ek banda doctor ke paas gaya: 'Doctor sahab, mujhe neend nahi aati.' Doctor: 'Aap din bhar kya karte ho?' Banda: 'Sota hoon.'",
    "😂 Teacher: 'Tum late kyu aaye?' Student: 'Sir, sapne me class chal rahi thi, attendance mark karne me time lag gaya.'",
    "😂 Girlfriend: 'Tum mujhe miss karte ho?' Boyfriend: 'Haan, jab tum call nahi uthati… tab main doosri ko call karta hoon.'",
    "😂 Ek ladka library me jaake bola: 'Mujhe ek burger dena.' Librarian: 'Yeh library hai!' Ladka: 'Oh sorry… mujhe ek burger dena.' (slowly)",
    "😂 Wife: 'Mere birthday pe kya gift doge?' Husband: 'Tumhe divorce ka gift card dunga, tum free ho jaogi!'",
    "😂 Ek dost: 'Mere ghar ka internet bohot slow hai.' Doosra: 'Kyun, patang se data kheench rahe ho?'",
    "😂 Padosi: 'Kal tumhare ghar se cheekhne ki awaaz aa rahi thi.' Main: 'Haan, phone gira tha… screen toot gayi.'",
    "😂 Girlfriend: 'Mujhe space chahiye.' Boyfriend: 'Chalo NASA chalte hain.'",
    "😂 Student: 'Sir, exam easy tha.' Teacher: 'Toh pass kyu nahi hue?' Student: 'Sir, mujhe lagta hai question paper ka mujhe trust nahi tha.'",
    "😂 Ek ladka gym me: 'Bhai, kaunsa exercise karun ki ladkiyan impress ho jayein?' Trainer: 'ATM pe kaam kar.'",
    "😂 Wife: 'Tum mujhe shopping le chalo.' Husband: 'Main busy hoon.' Wife: 'Main tumhare saath selfie nahi loongi.' Husband: 'Chalo chal rahe hain!'",
    "😂 Teacher: 'Tumhara future bright hai.' Student: 'Sir, phir toh main sunglasses pehen ke aaunga.'",
    "😂 Ek dost: 'Tu itna chhup kyu rehta hai?' Main: 'Kya karun, meri life me hide and seek chal rahi hai.'",
    "😂 Padosan: 'Aapke husband ghar me hain?' Wife: 'Nahi, main bhi free trial pe chal rahi hoon.'",
    "😂 Ek ladka road pe gira, log bole: 'Arey, chot lagi?' Ladka: 'Nahi re, earth ko hug kar raha tha.'",
    "😂 Girlfriend: 'Main tumse naraz hoon.' Boyfriend: 'Toh main tumhe maaf karta hoon.'",
    "😂 Teacher: 'Tum exam me likh ke aaye the ki oxygen colourless hai, phir red kyun likha?' Student: 'Sir, blood me milte hi sharma gayi.'",
    "😂 Dost: 'Mujhe neend nahi aati.' Main: 'Apna syllabus padh, 2 page me hi aa jayegi.'",
    "😂 Ek uncle: 'Beta, bada hoke kya banoge?' Bachcha: 'Bada.'",
    "😂 Wife: 'Main maa banne wali hoon!' Husband: 'Main papa banne wala hoon!' Padosi: 'Main chhup ho jaaun?'",
    "😂 Boss: 'Tum late kyu aaye?' Employee: 'Sir, road me board laga tha – “School ahead, go slow.”'",
    "😂 Doctor: 'Aapko rest ki zarurat hai.' Patient: 'Rest ka loan milta hai kya?'",
    "😂 Student: 'Sir, result kab aayega?' Teacher: 'Beta, tumhara result humara surprise hai.'",
    "😂 Girlfriend: 'Tum mujhe kab propose karoge?' Boyfriend: 'Jab tumhara recharge khatam hoga.'",
    "😂 Ek ladka: 'Main apne sapno ka ghar bana raha hoon.' Dost: 'Nice! Kaunsa cement use kar raha hai?' Ladka: 'Google SketchUp.'",
    "😂 Teacher: 'Homework kyu nahi kiya?' Student: 'Sir, electricity nahi thi… pen charge nahi ho raha tha.'",
    "😂 Boss: 'Tum kaam me serious kyu nahi hote?' Employee: 'Sir, maine doctor se commitment kar rakha hai – stress free rahunga.'",
    "😂 Wife: 'Tum mujhe pyaar karte ho?' Husband: 'Haan, lekin wifi zyada important hai.'",
    "😂 Padosi: 'Aapke ghar ka AC kaam nahi kar raha?' Main: 'Nahi, main free sauna service le raha hoon.'",
    "😂 Dost: 'Mera pet dard kar raha hai.' Main: 'Pet se bol de kaam band kare, chhutti le le.'",
    "😂 Teacher: 'Tere paper me sab blank kyu hai?' Student: 'Sir, white space bhi toh art hota hai.'",
    "😂 Girlfriend: 'Main tumhe block kar rahi hoon.' Boyfriend: 'Theek hai, lekin pehle recharge karwa de.'",
    "😂 Patient: 'Mujhe lagta hai main invisible hoon.' Doctor: 'Kaun bol raha hai?'",
    "😂 Dost: 'Mujhe lagta hai main handsome hoon.' Main: 'Haan, mirror ka glass tootta hua hoga.'",
    "😂 Wife: 'Mujhe gold chain chahiye.' Husband: 'Chain to main de dunga, gold khud bhar lena.'",
    "😂 Teacher: 'Tumne test me cheating ki?' Student: 'Nahi sir, main toh research kar raha tha.'",
    "😂 Dost: 'Mere phone me virus aa gaya.' Main: 'Shayad tumne usse mask nahi pehnaya.'",
    "😂 Girlfriend: 'Mujhe coffee pe le chalo.' Boyfriend: 'Thik hai, lekin apni cup laana.'",
    "😂 Patient: 'Mujhe bhoolne ki bimari ho gayi hai.' Doctor: 'Kab se?' Patient: 'Kab se kya?'",
    "😂 Wife: 'Main maa ban gayi!' Husband: 'Good, main cricket dekh raha hoon.'",
    "😂 Teacher: 'Homework kahan hai?' Student: 'Sir, homework bhi corona positive ho gaya.'",
    "😂 Boss: 'Tumhara promotion cancel.' Employee: 'Thank you sir, workload kam ho gaya.'",
    "😂 Dost: 'Mera weight badh gaya.' Main: 'Scale ko guilt trip de raha hai kya?'",
    "😂 Girlfriend: 'Tum mujhe miss karte ho?' Boyfriend: 'Nahi, mujhe tumhare jokes miss hote hain… kam funny the.'",
    "😂 Doctor: 'Tumhe diabetes hai.' Patient: 'Thank you, ab free me mithai milegi?'",
    "😂 Dost: 'Main millionaire ban gaya.' Main: 'Kaise?' Dost: 'Game me coins collect kiye.'",
    "😂 Wife: 'Tum khud se pyaar karte ho?' Husband: 'Haan, tum se zyada.'",
    "😂 Teacher: 'Tumne exam me fail kaise kiya?' Student: 'Sir, paper me questions kam the.'",
    "😂 Dost: 'Main diet pe hoon.' Main: 'Instagram pe ya food pe?'",
    "😂 Girlfriend: 'Main tumse naraz hoon.' Boyfriend: 'Kya main recharge karke manaa loon?'",
    "😂 Patient: 'Mere pet me chuhe daud rahe hain.' Doctor: 'Unhe billy bhej du?'",
    "😂 Dost: 'Mere ghar me network nahi aata.' Main: 'Shayad tumhara ghar offline hai.'",
    "😂 Teacher: 'Tum itne chup kyu ho?' Student: 'Sir, main silent mode me hoon.'",
    "😂 Boss: 'Tum meeting me so rahe the?' Employee: 'Sir, main dream me kaam kar raha tha.'",
    "😂 Dost: 'Mujhe girlfriend chahiye.' Main: 'App download kar le.'",
    "😂 Wife: 'Main tumhare liye dress laayi hoon.' Husband: 'Main tumhare liye patience laaya hoon.'",
    "😂 Teacher: 'Homework pura hua?' Student: 'Sir, homework bhi lockdown me phas gaya.'",
    "😂 Patient: 'Mujhe khushi ki dawai do.' Doctor: 'Recharge plan le le, unlimited call milega.'",
    "😂 Dost: 'Mere ghar ka fan slow chal raha hai.' Main: 'Shayad uska motivation kam hai.'",
    "😂 Girlfriend: 'Main tumse break up kar rahi hoon.' Boyfriend: 'Chalo, free me upgrade mil gaya.'",
    "😂 Wife: 'Main shopping pe jaa rahi hoon.' Husband: 'Main bank chhupane jaa raha hoon.'",
    "😂 Teacher: 'Tum class me kyu nahi aaye?' Student: 'Sir, sapne me extra class le li thi.'",
    "😂 Dost: 'Main ro raha hoon.' Main: 'Kya hua?' Dost: 'Mera phone slip hoke bed ke neeche gir gaya.'",
    "😂 Wife: 'Tumne mujhe pehli baar kahan dekha?' Husband: 'Zoom meeting me.'",
    "😂 Girlfriend: 'Mujhe gifts pasand hai.' Boyfriend: 'Mujhe free gifts pasand hai.'",
    "😂 Teacher: 'Tumhara handwriting kaisa hai?' Student: 'Sir, cryptography me use hota hai.'",
    "😂 Dost: 'Mujhe break chahiye.' Main: 'Biscuit ka ya relationship ka?'",
    "😂 Patient: 'Mujhe lagta hai main singer ban gaya.' Doctor: 'Chalo gala check karte hain.'",
    "😂 Wife: 'Mere liye pizza le aao.' Husband: 'Main pizza ban ke aata hoon.'",
    "😂 Teacher: 'Tumne copy kyu ki?' Student: 'Sir, sharing is caring.'",
    "😂 Dost: 'Main sad hoon.' Main: 'Toh khush lagne ka filter laga le.'",
    "😂 Boss: 'Tumhara kaam pending hai.' Employee: 'Sir, kaam ka patience test le raha hoon.'",
    "😂 Wife: 'Main tumse bahut pyaar karti hoon.' Husband: 'Main bhi, lekin sale se zyada nahi.'",
    "😂 Girlfriend: 'Tum mujhe gift kyu nahi dete?' Boyfriend: 'Main surprise ka wait kar raha hoon.'",
    "😂 Teacher: 'Tumne class me kya seekha?' Student: 'Sir, seat ka number.'",
    "😂 Dost: 'Mujhe neend aa rahi hai.' Main: 'Toh sleep mode on kar le.'",
    "😂 Wife: 'Mujhe new phone chahiye.' Husband: 'Apna purana phone donate kar de.'",
    "😂 Patient: 'Main bhool gaya hoon main kaun hoon.' Doctor: 'Toh fees kaun dega?'",
    "😂 Dost: 'Mere ghar ka wifi slow hai.' Main: 'Uska mood change kar de.'",
    "😂 Teacher: 'Tumne answer kyu nahi likha?' Student: 'Sir, pen ka internet khatam ho gaya.'",
    "😂 Girlfriend: 'Main tumse dur jaa rahi hoon.' Boyfriend: 'Google Map share kar do.'",
    "😂 Wife: 'Mere liye surprise hai?' Husband: 'Haan, khali wallet.'",
    "😂 Dost: 'Mujhe job chahiye.' Main: 'Job portal download kar.'",
    "😂 Patient: 'Mujhe lagta hai main hero hoon.' Doctor: 'Film ka naam batao.'",
    "😂 Teacher: 'Tumhare marks kam aaye.' Student: 'Sir, main minimalism follow karta hoon.'",
    "😂 Wife: 'Tum mujhe ignore karte ho.' Husband: 'Nahi, main focus mode me hoon.'",
    "😂 Dost: 'Mera phone toot gaya.' Main: 'Uske liye condolence message bhej du?'",
    "😂 Teacher: 'Tum mobile use kar rahe ho?' Student: 'Nahi sir, mobile mujhe use kar raha hai.'",
    "😂 Wife: 'Mujhe trip pe le chalo.' Husband: 'Sapne me chalenge.'",
    "😂 Girlfriend: 'Main tumse shaadi karungi.' Boyfriend: 'Aaj Friday 13 hai, lucky day hai.'",
    "😂 Teacher: 'Padhai kyun nahi karte?' Student: 'Aapne hi toh kaha tha knowledge share karo!'",
    "😂 Doctor: 'Aapko neend aati hai?' Patient: 'Nahi, main sone ke baad sota hoon.'",
    "😂 Boy: 'Tum itni sundar kaise ho?' Girl: 'Filter ka kamaal hai.'",
    "😂 Girlfriend: 'Main gussa hoon!' Boyfriend: 'Discount milega kya?'",
    "😂 Teacher: 'Homework kahan hai?' Student: 'Lockdown mein phas gaya sir!'",
    "😂 Wife: 'Mere liye kya lae ho?' Husband: 'Main toh tumhare liye hi ghar laut aaya.'",
    "😂 Boy: 'Mujhe tumse ek baat kahni hai.' Girl: 'Haan bolo.' Boy: 'Recharge kara do.'",
    "😂 Girlfriend: 'Tum mujhe kitna pyar karte ho?' Boyfriend: 'Google se zyada search karta hoon.'",
    "😂 Teacher: 'Batao electricity kisne discover ki?' Student: 'Jis din light gayi thi, us din pata chala.'",
    "😂 Wife: 'Tum mujhe kab shopping le jaoge?' Husband: 'Sapno mein roz le jata hoon.'",
    "😂 Boy: 'Meri life boring hai.' Friend: 'Toh comedy channel khol le!'",
    "😂 Girlfriend: 'Tum mujhe yaad karte ho?' Boyfriend: 'WiFi jaise… signal mila toh instantly connect hota hoon.'",
    "😂 Teacher: 'Yeh kaunsa tense hai?' Student: 'Present sir… gift wala.'",
    "😂 Boy: 'Mujhe tumse shaadi karni hai.' Girl: 'Main toh already busy hoon Netflix ke saath.'",
    "😂 Wife: 'Main tumhare liye kya hoon?' Husband: 'Monthly subscription… bina tumhare life incomplete hai.'",
    "😂 Teacher: 'Yeh homework incomplete kyun hai?' Student: 'Battery low ho gayi thi sir.'",
    "😂 Boy: 'Tum meri zindagi ho.' Girl: 'Phir toh main tumhe block kar rahi hoon.'",
    "😂 Girlfriend: 'Tum mujhe surprise doge?' Boyfriend: 'Haan… ek din bina call kiye aa jaunga.'",
    "😂 Teacher: 'Tum late kyun aaye?' Student: 'Sir, time ko respect nahi karta.'",
    "😂 Boy: 'Meri girlfriend kho gayi.' Friend: 'Toh nayi le le, purani model ki warranty khatam hogayi.'",
    "😂 Wife: 'Main thak gayi hoon.' Husband: 'Main toh tumse pehle hi thak chuka hoon.'",
    "😂 Girlfriend: 'Mujhe tum pe trust hai.' Boyfriend: 'Mujhe bhi… apne acting pe.'",
    "😂 Teacher: 'Yeh exam easy tha na?' Student: 'Haan sir, paper dekh ke so gaya.'",
    "😂 Boy: 'Mujhe tumse ek kaam hai.' Girl: 'Kya?' Boy: 'Meri crush se milwa do.'",
    "😂 Wife: 'Main tumse divorce lungi!' Husband: 'Shopping se sasti option hai.'",
    "😂 Teacher: 'Homework kahan hai?' Student: 'Dog kha gaya sir… magar dog vegan hai.'",
    "😂 Boy: 'Tum meri jaan ho.' Girl: 'Mujhe battery low ka icon mat samjho.'",
    "😂 Girlfriend: 'Tum mujhe ignore kyun karte ho?' Boyfriend: 'Tum WhatsApp status pe busy ho.'",
    "😂 Teacher: 'Tumhara future bright hai.' Student: 'Sir, bijli ka bill kaun bharega?'",
    "😂 Boy: 'Mujhe tumse ek promise chahiye.' Girl: 'Kya?' Boy: 'Mere memes pe hamesha laugh karna.'",
    "😂 Wife: 'Tum mujhe samajhte hi nahi!' Husband: 'Manual book ke saath nahi aayi thi tum.'",
    "😂 Boy: 'Mujhe tumse ek gift chahiye.' Girl: 'Kya?' Boy: 'Apna WiFi password.'",
    "😂 Girlfriend: 'Tum bahut smart ho.' Boyfriend: 'Acha toh Google se milwa du?'",
    "😂 Teacher: 'Yeh kaunsa subject hai?' Student: 'Sir, WhatsApp University ka.'",
    "😂 Boy: 'Tum meri duniya ho.' Girl: 'Phir toh main tumhara internet bandh kar rahi hoon.'",
    "😂 Wife: 'Main tumhare bina mar jaungi.' Husband: 'Insurance ka naam likhwa du?'",
    "😂 Boy: 'Mujhe tumse ek secret kahna hai.' Girl: 'Bolo.' Boy: 'Main fast charger hoon.'",
    "😂 Teacher: 'Tum itne chup kyun ho?' Student: 'Mute button on ho gaya sir.'",
    "😂 Boy: 'Meri ek wish poori karo.' Girl: 'Kya?' Boy: 'Tumhare phone ka gallery dekhna hai.'",
    "😂 Wife: 'Tum mujhe kab shopping karane le jaoge?' Husband: 'Jab mall free delivery dene lage.'",
    "😂 Girlfriend: 'Tum mujhse kitna pyar karte ho?' Boyfriend: 'Jitna data bachta hai recharge ke baad.'",
    "😂 Teacher: 'Tum itne late kyun aaye?' Student: 'Time se jaldi aane ki aadat khatam ho gayi.'",
    "😂 Boy: 'Main tumse break up kar raha hoon.' Girl: 'Main toh pehle hi single thi.'",
    "😂 Wife: 'Mujhe ek gift chahiye.' Husband: 'Budget-friendly ya heart-attack wala?'",
    "😂 Boy: 'Tum meri life ka goal ho.' Girl: 'Toh Google Calendar pe dal do.'",
    "😂 Teacher: 'Tumne exam mein blank paper kyun diya?' Student: 'Silence is the best answer.'",
    "😂 Boy: 'Mujhe tumse ek sawal hai.' Girl: 'Bolo.' Boy: 'Tum real ho ya filter?'",
    "😂 Wife: 'Main tumse gussa hoon!' Husband: 'Main bhi apne phone se gussa hoon.'",
    "😂 Girlfriend: 'Tum mujhe miss karte ho?' Boyfriend: 'Jab recharge khatam hota hai tab.'",
    "😂 Teacher: 'Yeh homework kahan hai?' Student: 'Sir, PDF banaya tha par phone hang ho gaya.'",
    "😂 Boy: 'Tum meri jaan ho.' Girl: 'Battery saver mode on ho gaya hai.'",
    "😂 Wife: 'Main tumhare liye kya hoon?' Husband: 'Google map… bina tumhare main kho jaata hoon.'",
    "😂 Teacher: 'Tum itne marks kaise laaye?' Student: 'Sir, calculator ka magic.'",
    "😂 Boy: 'Tum meri dream girl ho.' Girl: 'Dream se uth jao, reality check lo.'",
    "😂 Girlfriend: 'Tum mujhe ignore kyun karte ho?' Boyfriend: 'Tum offline ho toh hi online aata hoon.'",
    "😂 Teacher: 'Tumhara result kaisa hai?' Student: 'Sir, suspense movie jaisa… end tak pata nahi.'",
    "😂 Boy: 'Tum meri life ki WiFi ho.' Girl: 'Signal weak hai.'",
    "😂 Wife: 'Mujhe ek surprise chahiye.' Husband: 'Main tumhe light bill ka amount bata deta hoon.'",
    "😂 Boy: 'Tum meri battery ho.' Girl: 'Toh tumhara charger kaun?'",
    "😂 Teacher: 'Yeh kaunsa tense hai?' Student: 'Sir, suspense tense.'",
    "😂 Boy: 'Mujhe tumse ek help chahiye.' Girl: 'Bolo.' Boy: 'Mera password yaad rakhna.'",
    "😂 Wife: 'Main tumhare bina nahi reh sakti.' Husband: 'Toh EMI tum bhar do.'",
    "😂 Girlfriend: 'Tum bahut handsome lagte ho.' Boyfriend: 'Aaj mirror ka mood acha tha.'",
    "😂 Teacher: 'Homework complete kyun nahi?' Student: 'Sir, pen ka WiFi khatam ho gaya.'",
    "😂 Boy: 'Tum meri zindagi ki movie ho.' Girl: 'Flop ya hit?'",
    "😂 Wife: 'Tum mujhe kab khush karoge?' Husband: 'Jab sale lagegi.'",
    "😂 Boy: 'Mujhe tumse ek wish hai.' Girl: 'Kya?' Boy: 'Mujhe block mat karo.'",
    "😂 Teacher: 'Tumhara handwriting kaisa hai?' Student: 'Sir, barcode jaisa.'",
    "😂 Boy: 'Tum meri life ki light ho.' Girl: 'Bijli ka bill bharo phir.'",
    "😂 Wife: 'Main tumhare bina adhuri hoon.' Husband: 'Aur main salary ke bina.'",
    "😂 Boy: 'Mujhe tumse ek baat kahni hai.' Girl: 'Bolo.' Boy: 'Recharge kar do.'",
    "😂 Teacher: 'Tumhara future bright hai.' Student: 'Sir, sunglasses le aao phir.'",
    "😂 Boy: 'Tum meri WhatsApp status ho.' Girl: '24 ghante ke liye?'",
    "😂 Wife: 'Main tumse pyar karti hoon.' Husband: 'Main bhi free WiFi se.'",
    "😂 Boy: 'Tum meri life ka shortcut ho.' Girl: 'Direct uninstall kar do.'",
    "😂 Teacher: 'Tum class mein kyun so rahe the?' Student: 'Dream mein padhai kar raha tha sir.'",
    "😂 Boy: 'Tum meri motivation ho.' Girl: 'Toh gym join kar lo.'",
    "😂 Wife: 'Main tumse naraz hoon.' Husband: 'Main toh pehle se hi apne phone se naraz hoon.'",
    "😂 Boy: 'Tum meri duniya ho.' Girl: 'GPS ka kaam kaun karega phir?'",
    "😂 Teacher: 'Tum itne chup kyun ho?' Student: 'Mute mode pe hoon sir.'",
    "😂 Boy: 'Tum meri heartbeat ho.' Girl: 'Pacemaker lagwa lo phir.'",
    "😂 Wife: 'Main tumhare liye kya hoon?' Husband: 'Recharge plan… bina tumhare life slow hai.'",
    "😂 Boy: 'Tum meri app ho.' Girl: 'Main toh tumhe uninstall kar rahi hoon.'",
    "😂 Teacher: 'Tumhara attendance kam kyun hai?' Student: 'Sir, network issue.'",
    "😂 Boy: 'Tum meri dictionary ho.' Girl: 'Mujhe khol ke dekho mat.'",
    "😂 Wife: 'Mujhe ek gift chahiye.' Husband: 'EMI ka gift pack le aao?'",
    "😂 Boy: 'Tum meri alarm ho.' Girl: 'Phir toh snooze pe daal do.'",
    "😂 Teacher: 'Tumhara result kaisa hai?' Student: 'Sir, suspense movie jaisa.'"
]

QUOTES = [
    "🗨️ Kamyabi ka raaz: 'Consistency'.",
    "🗨️ Sapne wahi sach hote hain jo aap jagte hue dekhte ho.",
    "🗨️ Mehnat ka rang hamesha chamakta hai.",
    "🗨️ Har din ek nayi shuruaat ka mauka hai.",
    "🗨️ Asli shakti aapke soch mein hoti hai.",
    "🗨️ Seekhna kabhi band mat karo.",
    "🗨️ Patience is the key to success.",
    "🗨️ Positive soch, positive zindagi.",
    "🗨️ Har problem ka solution hota hai.",
    "🗨️ Apne goals pe focus rakho.",
    "🗨️ Hard work beats talent jab talent hard work nahi karta.",
    "🗨️ Chhote steps bade results laate hain.",
    "🗨️ Apne upar bharosa rakho.",
    "🗨️ Har girne ke baad uthna zaroori hai.",
    "🗨️ Discipline se hi dreams pure hote hain.",
    "🗨️ Har din apne aap ko better banao.",
    "🗨️ Jeetne ka maza tab aata hai jab mushkil ho.",
    "🗨️ Zindagi ek challenge hai, usse accept karo.",
    "🗨️ Sapne chhodo mat, unke liye lodo.",
    "🗨️ Mehnat ka phal hamesha meetha hota hai.",
    "🗨️ Khud par vishwas sabse badi taqat hai.",
    "🗨️ Har din kuch naya seekho.",
    "🗨️ Problems ko excuse mat banao.",
    "🗨️ Fear ke aage jeet hai.",
    "🗨️ Har kaam ka ek sahi samay hota hai.",
    "🗨️ Jo apne sapno ke liye ladta hai, wahi jeetta hai.",
    "🗨️ Zindagi me risk lena zaroori hai.",
    "🗨️ Aaj ka effort kal ka result banata hai.",
    "🗨️ Har struggle ek nayi kahani likhta hai.",
    "🗨️ Stop doubting yourself, start believing.",
    "🗨️ Motivation ke liye apne progress ko dekho.",
    "🗨️ Har din ek nayi opportunity hai.",
    "🗨️ Consistency > Motivation.",
    "🗨️ Apne goals likho, unke peeche bhago.",
    "🗨️ Har chhoti jeet celebrate karo.",
    "🗨️ Apna time aayega, bas lage raho.",
    "🗨️ Bina mehnat ke kuch nahi milta.",
    "🗨️ Life me excuses nahi, efforts do.",
    "🗨️ Har din ek kadam aage badho.",
    "🗨️ Kam bolna, zyada karna.",
    "🗨️ Self-discipline is self-love.",
    "🗨️ Har din gratitude feel karo.",
    "🗨️ Apne comfort zone se bahar niklo.",
    "🗨️ Hard work kabhi waste nahi hota.",
    "🗨️ Focus on process, not only results.",
    "🗨️ Har failure ek lesson hai.",
    "🗨️ Apne aap ko underestimate mat karo.",
    "🗨️ Progress slow ho sakti hai, par hoti zaroor hai.",
    "🗨️ Har din kuch productive karo.",
    "🗨️ Mindset hi sab kuch hai.",
    "🗨️ Stop complaining, start doing.",
    "🗨️ Har kaam ka pehla step sabse mushkil hota hai.",
    "🗨️ Energy un cheezon pe lagao jo matter karti hain.",
    "🗨️ Zindagi me self-control zaroori hai.",
    "🗨️ Sapne dekhna easy hai, unhe poora karna hard.",
    "🗨️ Jo tum soch sakte ho, wo tum kar sakte ho.",
    "🗨️ Kaam se darr mat, kaam se pyaar karo.",
    "🗨️ Har naya din ek gift hai.",
    "🗨️ Jeetne ke liye pehle haarna padta hai.",
    "🗨️ Self-improvement me invest karo.",
    "🗨️ Apne goals ke liye daily kaam karo.",
    "🗨️ Jo seekhta hai, wahi jeetta hai.",
    "🗨️ Aaj ka kaam kal pe mat chhodo.",
    "🗨️ Har din thoda better banne ki koshish karo.",
    "🗨️ Growth me time lagta hai.",
    "🗨️ Har mushkil ek naya skill sikhati hai.",
    "🗨️ Zindagi me positive log rakho.",
    "🗨️ Khud ki comparison sirf apne aaj se karo.",
    "🗨️ Apne goals ko visualize karo.",
    "🗨️ Har jeet ek sochi-samjhi strategy ka result hoti hai.",
    "🗨️ Zindagi ka maza challenges me hai.",
    "🗨️ Stop wishing, start doing.",
    "🗨️ Har din apne sapno ke kareeb jao.",
    "🗨️ Fail hone se daro mat.",
    "🗨️ Har setback ek comeback ka chance hai.",
    "🗨️ Khud ko motivate karna seekho.",
    "🗨️ Life me progress hi success hai.",
    "🗨️ Apni priorities set karo.",
    "🗨️ Har kaam patience se karo.",
    "🗨️ Negativity ko apne aas paas se hatao.",
    "🗨️ Success ke liye sacrifice zaroori hai.",
    "🗨️ Har din ek new chapter hai.",
    "🗨️ Khud ke liye khud ka hero bano.",
    "🗨️ Self-respect kabhi compromise mat karo.",
    "🗨️ Har decision ka ek impact hota hai.",
    "🗨️ Jo tum karte ho, wahi tum ban jaate ho.",
    "🗨️ Zindagi me learning kabhi khatam nahi hoti.",
    "🗨️ Apna focus sirf growth pe rakho.",
    "🗨️ Time sabse bada asset hai.",
    "🗨️ Apne goals ke liye apni habits badlo.",
    "🗨️ Har din gratitude feel karo.",
    "🗨️ Life ek marathon hai, sprint nahi.",
    "🗨️ Jo aaj karoge, kal wahi bologe.",
    "🗨️ Khud ke liye standards high rakho.",
    "🗨️ Har kaam dedication se karo.",
    "🗨️ Mehnat + patience = success.",
    "🗨️ Mehnat + patience = success.",
    "🗨️ Hard work beats talent when talent doesn't work hard.",
    "🗨️ Sapne wahi sach hote hain jo jagte hue dekhe jate hain.",
    "🗨️ Zindagi mein comfort zone se bahar niklo.",
    "🗨️ Every day is a new opportunity.",
    "🗨️ Waqt ka sahi use hi kaamyabi hai.",
    "🗨️ Small steps lead to big results.",
    "🗨️ Apni soch positive rakho.",
    "🗨️ Har din ek nayi shuruaat hai.",
    "🗨️ Success is a journey, not a destination.",
    "🗨️ Himmat kabhi mat haaro.",
    "🗨️ Discipline is the bridge between goals and success.",
    "🗨️ Jeetne wale kabhi give up nahi karte.",
    "🗨️ Khud par bharosa rakho.",
    "🗨️ Har failure ek lesson hota hai.",
    "🗨️ Badalte raho, seekhte raho.",
    "🗨️ Zindagi mein risk lena zaroori hai.",
    "🗨️ Mehnat ka phal hamesha meetha hota hai.",
    "🗨️ Kaam chhota ya bada nahi hota.",
    "🗨️ Har mushkil ek mauka hoti hai.",
    "🗨️ Focus on progress, not perfection.",
    "🗨️ Waqt aur mehnat kabhi waste nahi hoti.",
    "🗨️ Apni journey pe trust karo.",
    "🗨️ Great things take time.",
    "🗨️ Khud ki competition khud se karo.",
    "🗨️ Sapne chhote ya bade nahi hote.",
    "🗨️ Har din kuch naya seekho.",
    "🗨️ Kam bol, zyada kaam kar.",
    "🗨️ Positive soch, positive zindagi.",
    "🗨️ Khud ko behtar banane ka try karo.",
    "🗨️ Discipline bina success nahi.",
    "🗨️ Hard work ka koi shortcut nahi.",
    "🗨️ Har din apne goal ke kareeb jao.",
    "🗨️ Chhote steps, bade results.",
    "🗨️ Plan banao, action lo.",
    "🗨️ Khud ki value samjho.",
    "🗨️ Apni soch badlo, zindagi badal jayegi.",
    "🗨️ Patience ek superpower hai.",
    "🗨️ Har problem ka solution hota hai.",
    "🗨️ Effort hamesha count hota hai.",
    "🗨️ Kabhi seekhna band mat karo.",
    "🗨️ Apne comfort zone se bahar niklo.",
    "🗨️ Kaamyabi ke liye struggle zaroori hai.",
    "🗨️ Focus + Consistency = Success.",
    "🗨️ Har din mehnat ka ek naya mauka hota hai.",
    "🗨️ Apni energy sahi jagah lagao.",
    "🗨️ Dreams ka plan banao.",
    "🗨️ Time sabse bada resource hai.",
    "🗨️ Self-belief hi key hai.",
    "🗨️ Learning ka process kabhi khatam nahi hota.",
    "🗨️ Har cheez possible hai.",
    "🗨️ Zindagi ek race nahi, ek journey hai.",
    "🗨️ Jeetne ke liye lagatar koshish karo.",
    "🗨️ Apne sapno ke peeche bhaago.",
    "🗨️ Har din kuch naya try karo.",
    "🗨️ Success ka taste struggle ke baad hi milta hai.",
    "🗨️ Focused raho, distracted mat ho.",
    "🗨️ Apne dreams ke liye sacrifice karo.",
    "🗨️ Har waqt ready raho seekhne ke liye.",
    "🗨️ Self-improvement hi best investment hai.",
    "🗨️ Kaam pe focus karo, results apne aap aayenge.",
    "🗨️ Bada socho, bada karo.",
    "🗨️ Har chhoti achievement celebrate karo.",
    "🗨️ Apni journey enjoy karo.",
    "🗨️ Jeet ki value tab samajh aati hai jab haar ho.",
    "🗨️ Har din apna best do.",
    "🗨️ Apne goals likho.",
    "🗨️ Smart work + hard work = magic.",
    "🗨️ Apni priorities set karo.",
    "🗨️ Effort lagao, baaki chhod do.",
    "🗨️ Har din ek opportunity hai improve karne ki.",
    "🗨️ Apna best banne ka try karo.",
    "🗨️ Consistency is the secret.",
    "🗨️ Har setback ek comeback ka chance hai.",
    "🗨️ Zindagi mein excuses kam do.",
    "🗨️ Apni soch positive rakho, cheezein positive hongi.",
    "🗨️ Seekhne ka attitude rakho.",
    "🗨️ Apne time ka respect karo.",
    "🗨️ Mehnat ka fal hamesha milta hai.",
    "🗨️ Dreams ko reality mein badlo.",
    "🗨️ Zindagi mein kabhi rukna mat.",
    "🗨️ Patience se kaam lo.",
    "🗨️ Jeetne ka maza tab aata hai jab mushkil ho.",
    "🗨️ Apna focus sharp rakho.",
    "🗨️ Risk lo, warna regret hoga.",
    "🗨️ Har din apne future pe kaam karo.",
    "🗨️ Har problem ek chance hai grow hone ka.",
    "🗨️ Goals set karo aur unke peeche lag jao.",
    "🗨️ Khud ki life ka control lo.",
    "🗨️ Har din ek chhota step lo apne goal ki taraf.",
    "🗨️ Self-discipline hi real freedom hai.",
    "🗨️ Focus karo jo tum control kar sakte ho.",
    "🗨️ Har din seekhne ki aadat banao.",
    "🗨️ Apne sapno ke liye lagan rakho.",
    "🗨️ Never underestimate yourself.",
    "🗨️ Zindagi ka best investment khud pe hota hai.",
    "🗨️ Har din ek nayi shuruaat hoti hai.",
    "🗨️ Apni thinking positive rakho.",
    "🗨️ Struggle ke bina success ka maza nahi."
]

FACTS = [
    "💡 Aadmi ke body mein lagbhag 60% paani hota hai.",
    "💡 Dil ek din mein 1 lakh se zyada baar dhadakta hai.",
    "💡 Human brain mein 86 billion neurons hote hain.",
    "💡 Aankh blink karne ka average time 0.3 seconds hota hai.",
    "💡 Insaan ka skeleton 206 haddi se bana hota hai.",
    "💡 Ek chammach shahad banane ke liye 12 bees kaam karti hain.",
    "💡 Insaan ke bal har din 0.35 mm badhte hain.",
    "💡 Human tongue mein 8000 taste buds hote hain.",
    "💡 Nails summer mein zyada fast badhte hain.",
    "💡 Human lungs mein 600 million air sacs hote hain.",
    "💡 Aankh ki muscles sabse zyada active hoti hain.",
    "💡 Brain 20% oxygen consume karta hai.",
    "💡 Human heart apne aap bijli produce kar sakta hai.",
    "💡 Zyada hasne se immunity strong hoti hai.",
    "💡 Insaan ke fingerprint life-time change nahi hote.",
    "💡 Babies ke bones adults se zyada hote hain.",
    "💡 Pet ke andar ka acid blade ko bhi dissolve kar sakta hai.",
    "💡 Blue whale ka heart car ke size ka hota hai.",
    "💡 Aankh ka cornea blood supply nahi leta, oxygen hawa se leta hai.",
    "💡 Human nose 50,000 alag smells yaad rakh sakta hai.",
    "💡 Giraffe ka dil 2 feet lamba hota hai.",
    "💡 Octopus ke 3 dil hote hain.",
    "💡 Shark kabhi cancer nahi hota.",
    "💡 Sloth ek hafte mein sirf ek baar potty karta hai.",
    "💡 Owl apni aankh ghumaa nahi sakta.",
    "💡 Crocodile apni zubaan bahar nahi nikal sakta.",
    "💡 Tortoise 150 saal se zyada jee sakta hai.",
    "💡 Penguin upar se girke bhi bach jata hai kyunki uska body fat high hota hai.",
    "💡 Honey kabhi kharab nahi hota.",
    "💡 Banana technically ek berry hai.",
    "💡 Tomato ek fruit hai, vegetable nahi.",
    "💡 Apple paani mein float karta hai kyunki usmein 25% hawa hoti hai.",
    "💡 Watermelon 92% paani hota hai.",
    "💡 Mango world ka sabse popular fruit hai.",
    "💡 Strawberry berry nahi hoti.",
    "💡 Coffee peene se memory improve hoti hai.",
    "💡 Chocolate dogs ke liye poison hoti hai.",
    "💡 Ice garam paani mein thoda jaldi pighalta hai.",
    "💡 Water ko 100°C pe boil hone mein altitude ka effect hota hai.",
    "💡 Coconut pani natural blood plasma hota hai.",
    "💡 Garlic ek natural antibiotic hai.",
    "💡 Tulsi ke patte mein Vitamin C hota hai.",
    "💡 Turmeric ek powerful antioxidant hai.",
    "💡 Doodh calcium ka best source hai.",
    "💡 Carrot khane se eyesight improve hoti hai.",
    "💡 Broccoli mein Vitamin C orange se zyada hota hai.",
    "💡 Water fasting detox ke liye use hota hai.",
    "💡 Neem ke patte blood ko saaf karte hain.",
    "💡 Aloe vera skin ke liye best natural moisturizer hai.",
    "💡 Meditation stress kam karta hai.",
    "💡 Exercise se endorphin release hota hai jo mood improve karta hai.",
    "💡 Walking se heart health improve hoti hai.",
    "💡 Laughter therapy immunity boost karti hai.",
    "💡 Yoga body aur mind balance karta hai.",
    "💡 Sleeping 7-8 hours immunity ke liye zaroori hai.",
    "💡 Zyada paani peena skin ke liye achha hai.",
    "💡 Music sunne se stress kam hota hai.",
    "💡 Dancing se calories burn hoti hain.",
    "💡 Reading brain ko active rakhta hai.",
    "💡 New skill seekhne se brain cells grow hote hain.",
    "💡 Typing fast karna ek useful skill hai.",
    "💡 Positive thinking se life quality improve hoti hai.",
    "💡 Early morning sun light Vitamin D ka source hai.",
    "💡 Birds ke hollow bones unko udne mein help karte hain.",
    "💡 Butterfly apne pairon se taste karti hai.",
    "💡 Bees ek trip mein 50 flowers visit karti hain.",
    "💡 Ant apne weight ka 50 guna utha sakti hai.",
    "💡 Cheetah 0 se 100 km/h 3 seconds mein pahunchta hai.",
    "💡 Elephant kabhi jump nahi kar sakta.",
    "💡 Dolphins apne naam pehchante hain.",
    "💡 Whale songs underwater miles tak ja sakte hain.",
    "💡 Camel apne hump mein fat store karta hai.",
    "💡 Kangaroo peeche nahi chal sakta.",
    "💡 Ostrich ka egg 1.5 kg ka hota hai.",
    "💡 Starfish ke paas brain nahi hota.",
    "💡 Jellyfish ka body 95% paani hota hai.",
    "💡 Koala 20 ghante tak so sakta hai.",
    "💡 Snake apni aankh band nahi kar sakta.",
    "💡 Polar bear ka fur white hai lekin skin black hoti hai.",
    "💡 Panda ka diet 99% bamboo hota hai.",
    "💡 Crab ka blood blue hota hai.",
    "💡 Peacock ka feather waterproof hota hai.",
    "💡 Fireflies light produce karte hain chemical reaction se.",
    "💡 Chameleon apni aankh alag alag direction mein ghumata hai.",
    "💡 Spider silk steel se zyada strong hota hai.",
    "💡 Earth pe sabse zyada population insects ki hai.",
    "💡 Antarctica mein koi reptile nahi milta.",
    "💡 Moon pe koi hawa nahi hai.",
    "💡 Sun ek medium size star hai.",
    "💡 Venus sabse garam planet hai.",
    "💡 Saturn ke rings ice aur dust se bane hain.",
    "💡 Earth ka 71% paani hai.",
    "💡 Pani garam karne par uska rang change nahi hota.",
    "💡 Cheenti apne wajan ka 50 guna samaan utha sakti hai.",
    "💡 Aankh khuli rakhe hue chheenkna impossible hai.",
    "💡 Machhli paani ke bina zyada der zinda nahi reh sakti.",
    "💡 Python duniya ki sabse tez badhne wali programming language hai.",
    "💡 Moon par hawa nahi hoti.",
    "💡 Insaan ka dimaag 75% paani se bana hai.",
    "💡 Owl apni gardan 270 degree ghumaa sakta hai.",
    "💡 Insaan ka heart ek din mein 100,000 baar dhadakta hai.",
    "💡 Earth ek din mein 1600 km/hr ki speed se ghoomti hai.",
    "💡 Chandan ka tel 100 saal tak khushbu deta hai.",
    "💡 Giraffe ki jeebh ka rang kala hota hai.",
    "💡 Apple paani mein tairta hai kyunki usme hawa hoti hai.",
    "💡 Hathi kood nahi sakta.",
    "💡 Dolphin ek aankh khuli rakhkar soti hai.",
    "💡 Sabse tez daudnewala prani cheetah hai.",
    "💡 Machhar khoon ke smell ko 50 meter door se mehsoos karta hai.",
    "💡 Anda ubalte waqt halka sa ghoomne lagta hai.",
    "💡 Diamond sabse hard natural substance hai.",
    "💡 Camera ka sabse pehla photo 8 ghante mein capture hua tha.",
    "💡 Coca-Cola ka original rang green tha.",
    "💡 Murgi ka record egg laying 371 eggs ek saal mein hai.",
    "💡 Banana technically ek berry hai.",
    "💡 Aankh ka cornea body ka only part hai jisme blood supply nahi hoti.",
    "💡 Octopus ke 3 dil hote hain.",
    "💡 Insaan ke body mein 206 haddi hoti hain.",
    "💡 Plastic ko degrade hone mein 450 saal lagte hain.",
    "💡 Coffee duniya ka second most traded commodity hai.",
    "💡 Penguin bird hote hue bhi ud nahi sakta.",
    "💡 Pani freeze hote waqt phailta hai.",
    "💡 Ghoonghat pehne wali dulhan ka trend Victorian era se aaya.",
    "💡 Chocolate dogs ke liye poison hoti hai.",
    "💡 Kangaroo ulta chal nahi sakta.",
    "💡 Tomato ek fruit hai.",
    "💡 Shark ko cancer nahi hota.",
    "💡 Murgi T-Rex dinosaur ki close relative hai.",
    "💡 Pehli mobile call 1973 mein hui thi.",
    "💡 Ek din mein sabse zyada saans lene wala organ lungs hai.",
    "💡 Ek insan apni zindagi mein average 25 saal sone mein bitata hai.",
    "💡 Neem ke patte antibacterial hote hain.",
    "💡 Billi 100 se zyada awaaze nikal sakti hai.",
    "💡 Insaan ka liver apne aap ko regenerate kar sakta hai.",
    "💡 Ajgar apne shikar ko pure ka pura nigal leta hai.",
    "💡 Sea otter sote waqt haath pakad ke sote hain.",
    "💡 Machhli ki smell power bahut strong hoti hai.",
    "💡 Sun light ko earth tak aane mein 8 minute lagte hain.",
    "💡 Ek insan ke DNA ka 60% banana ke DNA se match karta hai.",
    "💡 Snail teen saal tak so sakta hai.",
    "💡 Aankh ka blink average 4 second mein hota hai.",
    "💡 Sloth ek hafte mein sirf ek baar potty karta hai.",
    "💡 Ek insan ki heartbeat ka sound valve ke close hone se aata hai.",
    "💡 Spider silk steel se zyada strong hoti hai.",
    "💡 Machhar ko pasina attract karta hai.",
    "💡 Ocean ka 80% hissa abhi tak explore nahi hua.",
    "💡 Sugar ek natural preservative hai.",
    "💡 Ek saal mein earth suraj ke chakkar lagati hai.",
    "💡 Billi apna khud ka naam pehchan sakti hai.",
    "💡 Butterfly apne pairon se taste karti hai.",
    "💡 Insaan ki bones steel se zyada strong hoti hain.",
    "💡 Watermelon 92% water hota hai.",
    "💡 Honeybee apni zindagi mein sirf 1/12 teaspoon honey banati hai.",
    "💡 Insaan ka heart football se bada nahi hota.",
    "💡 Ek insan ke body mein lagbhag 5.5 liter khoon hota hai.",
    "💡 Ek octopus ke 9 brain hote hain.",
    "💡 Polar bear ka fur white hota hai lekin skin black hoti hai.",
    "💡 Ek insan apni zindagi mein 1 lakh km chal leta hai.",
    "💡 Snake bina kaan ke bhi sun sakta hai.",
    "💡 Ek insan ka brain 20 watt energy consume karta hai.",
    "💡 Owl ki eyes move nahi karti.",
    "💡 Machhar ke wings 1000 baar per second beat karte hain.",
    "💡 Ek elephant ki pregnancy 22 months hoti hai.",
    "💡 Insaan ka fingerprint kabhi change nahi hota.",
    "💡 Dog ka nose fingerprint unique hota hai.",
    "💡 Ek insan bina pani ke sirf 3-5 din survive kar sakta hai.",
    "💡 Fire bina oxygen ke nahi jalti.",
    "💡 Water ka chemical formula H2O hai.",
    "💡 Ek normal insan 70-100 heartbeat per minute leta hai.",
    "💡 Banana seedless hota hai.",
    "💡 Cloud ka weight lakhon kilo hota hai.",
    "💡 Earth ka 71% surface water se covered hai.",
    "💡 Ek insan ka brain soते waqt zyada active hota hai.",
    "💡 Coconut ek fruit, seed aur nut teenon hota hai.",
    "💡 Antarctica sabse dry continent hai.",
    "💡 Ek glass water mein million bacteria hote hain.",
    "💡 Ek insan ke andar trillion cells hote hain.",
    "💡 Lightning sun ke surface se 5 guna zyada hoti hai.",
    "💡 Ek insan ek saal mein 4 crore baar saans leta hai.",
    "💡 Pigeon apna ghar 1300 km door se bhi dhund sakta hai.",
    "💡 Jellyfish ka body 95% water hota hai.",
    "💡 Ek insan ki aankh 1 crore colors dekh sakti hai.",
    "💡 Chameleon apni eyes alag direction mein move kar sakta hai.",
    "💡 Bamboo ek din mein 91 cm tak grow kar sakta hai.",
    "💡 Whale ka heart ek car jitna bada hota hai.",
    "💡 Insaan ka dant enamel sabse hard substance hai.",
    "💡 Ek insan ke pet mein 35 crore bacteria hote hain.",
    "💡 Ek frog apni skin se breathe kar sakta hai.",
    "💡 Ek insan ki bones lagbhag 14% body weight hoti hain.",
    "💡 Milky Way mein 100 billion se zyada stars hain.",
    "💡 Light ko sun se earth aane mein 8 min 20 sec lagte hain.",
    "💡 Black hole light ko bhi kheench leta hai.",
    "💡 Human-made objects space mein 8000+ hain.",
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
         InlineKeyboardButton("Weather Info", callback_data="weather")]
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

async def handle_pin_code(update: Update, context: ContextTypes.DEFAULT_TYPE, waiting_msg=None):
    user = update.effective_user

    if user.id not in user_state:
        user_state[user.id] = {}

    # Agar waiting_msg pass nahi hua, to yahan create karo
    if waiting_msg is None:
        waiting_msg = await update.message.reply_text("⌛ Please Wait A Moment ...")

    pin_code = update.message.text.strip()
    if not pin_code.isdigit() or len(pin_code) != 6:
        await waiting_msg.edit_text("❌ Please enter a valid 6-digit pin code.")
        return

    url = f"https://api.postalpincode.in/pincode/{pin_code}"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

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
# Send Next Functions
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

async def send_next_joke(user_id, query):
    index = user_state[user_id].get("joke_index", -1) + 1
    joke_list = user_state[user_id]["joke_list"]
    if index >= len(joke_list):
        await query.message.reply_text("🎉 Seen all jokes!", reply_markup=main_buttons())
        user_state[user_id]["joke_index"] = -1
        return
    user_state[user_id]["joke_index"] = index
    joke = joke_list[index]
    keyboard = [[InlineKeyboardButton("Next Joke", callback_data="jokes")]]
    await query.message.reply_text(joke, reply_markup=InlineKeyboardMarkup(keyboard))

async def send_next_quote(user_id, query):
    index = user_state[user_id].get("quote_index", -1) + 1
    quote_list = user_state[user_id]["quote_list"]
    if index >= len(quote_list):
        await query.message.reply_text("🎉 Seen all quotes!", reply_markup=main_buttons())
        user_state[user_id]["quote_index"] = -1
        return
    user_state[user_id]["quote_index"] = index
    quote = quote_list[index]
    keyboard = [[InlineKeyboardButton("Next Quote", callback_data="quotes")]]
    await query.message.reply_text(quote, reply_markup=InlineKeyboardMarkup(keyboard))

async def send_next_fact(user_id, query):
    index = user_state[user_id].get("fact_index", -1) + 1
    fact_list = user_state[user_id]["fact_list"]
    if index >= len(fact_list):
        await query.message.reply_text("🎉 Seen all facts!", reply_markup=main_buttons())
        user_state[user_id]["fact_index"] = -1
        return
    user_state[user_id]["fact_index"] = index
    fact = fact_list[index]
    keyboard = [[InlineKeyboardButton("Next Fact", callback_data="facts")]]
    await query.message.reply_text(fact, reply_markup=InlineKeyboardMarkup(keyboard))

# -------------------------
# Bot Handlers
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

    if data == "pin_code":
        user_state[user_id]["mode"] = "PIN_CODE_WAIT"
        await query.message.reply_text("📌 Please Enter 6-Digit PIN Code:")

    elif data == "translator":
        user_state[user_id]["mode"] = "TRANSLATOR_WAIT"
        await query.message.reply_text("📝 Send Text To Translate Any Language to English.")

    elif data == "gk_quiz":
        user_state[user_id]["mode"] = "GK_QUIZ"
        user_state[user_id]["quiz_list"] = get_randomized_list(GK_QUIZZES)
        user_state[user_id]["quiz_index"] = -1
        await send_next_quiz(user_id, query)

    elif data == "jokes":
        user_state[user_id]["mode"] = "JOKES"
        user_state[user_id]["joke_list"] = get_randomized_list(JOKES)
        user_state[user_id]["joke_index"] = -1
        await send_next_joke(user_id, query)

    elif data == "quotes":
        user_state[user_id]["mode"] = "QUOTES"
        user_state[user_id]["quote_list"] = get_randomized_list(QUOTES)
        user_state[user_id]["quote_index"] = -1
        await send_next_quote(user_id, query)

    elif data == "facts":
        user_state[user_id]["mode"] = "FACTS"
        user_state[user_id]["fact_list"] = get_randomized_list(FACTS)
        user_state[user_id]["fact_index"] = -1
        await send_next_fact(user_id, query)

    elif data == "time_date":
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        await query.message.reply_text(
            f"⏰ Time: {now.strftime('%I:%M %p')}\n📅 Date: {now.strftime('%d %B %Y')}",
            reply_markup=main_buttons()
        )

    elif data == "weather":
        user_state[user_id]["mode"] = "WEATHER_WAIT"
        await query.message.reply_text("🌤 Please Enter City Name:")

# -------------------------
# Message Handler
# -------------------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    # Pehle ek waiting message bhej do
    waiting_msg = await update.message.reply_text("⌛ Please Wait A Moment ...")

    if user_id not in user_state:
        await waiting_msg.edit_text("❌ Use /start first.")
        return

    mode = user_state[user_id].get("mode", "")

# -------------------------
# PIN Code
# -------------------------
    if mode == "PIN_CODE_WAIT":
        await handle_pin_code(update, context, waiting_msg)
        return

# -------------------------
# Translator
# -------------------------
    elif mode == "TRANSLATOR_WAIT":
        try:
            # 1 second delay
            await asyncio.sleep(1)
            translation = await asyncio.to_thread(
                GoogleTranslator(source='auto', target='en').translate, text
            )
            await waiting_msg.edit_text(f"🔤 {translation}")
        except Exception:
            await waiting_msg.edit_text("❌ Translation Failed. Please Try Again.")

# -------------------------
# Weather
# -------------------------
    elif mode == "WEATHER_WAIT":
        if not text:
            await waiting_msg.edit_text("❌ Enter valid city.")
            return

        weather = await asyncio.to_thread(fetch_weather, text)
        if weather:
            resp = (
                f"🌤 Weather in {weather['city']}:\n"
                f"🌡 Temperature: {weather['temp']}°C\n"
                f"💧 Humidity: {weather['humidity']}%\n"
                f"🌦 Rain (Today): {int(weather.get('pop',0))}%\n"
                f"📝 About: {weather['desc']}"
            )
            await waiting_msg.edit_text(resp)
        else:
            await waiting_msg.edit_text("❌ City Not Found, Please Try Again.")


# -------------------------
# Quiz Answer Handler
# -------------------------
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
# Imports
# -------------------------
from keep_alive import keep_alive
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# -------------------------
# Main
# -------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(quiz_answer_handler, pattern=r"^quiz_\d+_\d+$"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("QuickMate Bot is running...")
    app.run_polling()

if __name__ == "__main__":  
    # Start Flask heartbeat first
    keep_alive()
    
    # Then run the bot
    main()       