"""Seed course content: "English for Hindi speakers".

Each skill is defined by a small vocabulary (english, hindi) and a few sentences
(hindi, english, word-to-blank[, alternative english answers]). seed.py expands
these into varied lessons, so the content stays easy to read and extend.
"""

COURSE = {"title": "English", "from_language": "Hindi", "to_language": "English"}

UNITS = [
    {
        "title": "Basics", "description": "नमस्ते कहना और अपना परिचय देना", "color": "#58cc02",
        "skills": [
            {
                "title": "Greetings", "icon": "👋",
                "words": [("hello", "नमस्ते"), ("goodbye", "अलविदा"), ("please", "कृपया"), ("thank you", "धन्यवाद"),
                          ("sorry", "माफ़ कीजिए"), ("yes", "हाँ"), ("no", "नहीं"), ("welcome", "स्वागत है")],
                "sentences": [
                    ("नमस्ते, आप कैसे हैं?", "Hello, how are you?", "how"),
                    ("मैं ठीक हूँ, धन्यवाद।", "I am fine, thank you.", "fine"),
                    ("सुप्रभात!", "Good morning!", "morning"),
                    ("आपका स्वागत है।", "You are welcome.", "welcome"),
                    ("कृपया बैठिए।", "Please sit down.", "sit"),
                    ("अलविदा, कल मिलते हैं।", "Goodbye, see you tomorrow.", "tomorrow"),
                ],
            },
            {
                "title": "Introductions", "icon": "🙋",
                "words": [("I", "मैं"), ("you", "आप"), ("name", "नाम"), ("my", "मेरा"), ("your", "आपका"),
                          ("friend", "दोस्त"), ("student", "छात्र"), ("teacher", "शिक्षक")],
                "sentences": [
                    ("मेरा नाम राम है।", "My name is Ram.", "name"),
                    ("आपका नाम क्या है?", "What is your name?", "your"),
                    ("मैं एक छात्र हूँ।", "I am a student.", "student"),
                    ("आप मेरे दोस्त हैं।", "You are my friend.", "friend"),
                    ("वह मेरी शिक्षक है।", "She is my teacher.", "teacher", ["He is my teacher."]),
                    ("मैं भारत से हूँ।", "I am from India.", "India"),
                ],
            },
            {
                "title": "Numbers", "icon": "🔢",
                "words": [("one", "एक"), ("two", "दो"), ("three", "तीन"), ("four", "चार"),
                          ("five", "पाँच"), ("six", "छह"), ("seven", "सात"), ("ten", "दस")],
                "sentences": [
                    ("मेरे पास दो किताबें हैं।", "I have two books.", "two"),
                    ("वह पाँच साल का है।", "He is five years old.", "five"),
                    ("हमारे घर में तीन कमरे हैं।", "Our house has three rooms.", "three",
                     ["There are three rooms in our house."]),
                    ("मुझे एक कप चाय चाहिए।", "I want one cup of tea.", "one",
                     ["I want a cup of tea.", "I need one cup of tea.", "I need a cup of tea."]),
                    ("एक सप्ताह में सात दिन होते हैं।", "A week has seven days.", "seven",
                     ["There are seven days in a week."]),
                    ("कक्षा में दस छात्र हैं।", "There are ten students in the class.", "ten"),
                ],
            },
            {
                "title": "Colors", "icon": "🎨",
                "words": [("red", "लाल"), ("blue", "नीला"), ("green", "हरा"), ("yellow", "पीला"),
                          ("black", "काला"), ("white", "सफ़ेद"), ("pink", "गुलाबी"), ("orange", "नारंगी")],
                "sentences": [
                    ("आसमान नीला है।", "The sky is blue.", "blue"),
                    ("पत्ते हरे हैं।", "The leaves are green.", "green"),
                    ("मेरी कार लाल है।", "My car is red.", "red"),
                    ("केला पीला होता है।", "A banana is yellow.", "yellow", ["The banana is yellow.", "Bananas are yellow."]),
                    ("उसकी बिल्ली काली है।", "Her cat is black.", "black", ["His cat is black."]),
                    ("दूध सफ़ेद होता है।", "Milk is white.", "white", ["The milk is white."]),
                ],
            },
        ],
    },
    {
        "title": "Food & Family", "description": "खाना-पीना और परिवार", "color": "#1cb0f6",
        "skills": [
            {
                "title": "Food", "icon": "🍎",
                "words": [("apple", "सेब"), ("bread", "रोटी"), ("rice", "चावल"), ("water", "पानी"),
                          ("milk", "दूध"), ("tea", "चाय"), ("egg", "अंडा"), ("banana", "केला")],
                "sentences": [
                    ("मुझे सेब पसंद है।", "I like apples.", "apples", ["I like apple.", "I like the apple."]),
                    ("मैं पानी पीता हूँ।", "I drink water.", "water"),
                    ("वह चाय पीती है।", "She drinks tea.", "tea", ["He drinks tea."]),
                    ("हम रोटी खाते हैं।", "We eat bread.", "bread"),
                    ("मुझे दूध चाहिए।", "I need milk.", "milk"),
                    ("क्या आपको चावल पसंद है?", "Do you like rice?", "rice"),
                ],
            },
            {
                "title": "Family", "icon": "👪",
                "words": [("mother", "माँ"), ("father", "पिता"), ("brother", "भाई"), ("sister", "बहन"),
                          ("son", "बेटा"), ("daughter", "बेटी"), ("grandmother", "दादी"), ("grandfather", "दादा")],
                "sentences": [
                    ("मेरी माँ घर पर है।", "My mother is at home.", "mother"),
                    ("मेरे पिता डॉक्टर हैं।", "My father is a doctor.", "doctor"),
                    ("मेरा एक भाई है।", "I have one brother.", "brother", ["I have a brother."]),
                    ("उसकी बहन स्कूल जाती है।", "His sister goes to school.", "sister", ["Her sister goes to school."]),
                    ("मेरी दादी कहानी सुनाती हैं।", "My grandmother tells stories.", "grandmother"),
                    ("यह मेरा परिवार है।", "This is my family.", "family"),
                ],
            },
            {
                "title": "Animals", "icon": "🐶",
                "words": [("dog", "कुत्ता"), ("cat", "बिल्ली"), ("cow", "गाय"), ("horse", "घोड़ा"),
                          ("bird", "चिड़िया"), ("fish", "मछली"), ("elephant", "हाथी"), ("monkey", "बंदर")],
                "sentences": [
                    ("कुत्ता भौंक रहा है।", "The dog is barking.", "barking", ["A dog is barking."]),
                    ("बिल्ली दूध पीती है।", "The cat drinks milk.", "cat", ["A cat drinks milk.", "Cats drink milk."]),
                    ("हाथी बहुत बड़ा है।", "The elephant is very big.", "elephant"),
                    ("चिड़िया उड़ रही है।", "The bird is flying.", "flying", ["A bird is flying."]),
                    ("गाय घास खाती है।", "The cow eats grass.", "grass", ["A cow eats grass.", "Cows eat grass."]),
                    ("मछली पानी में रहती है।", "The fish lives in water.", "lives", ["Fish live in water.", "A fish lives in water."]),
                ],
            },
            {
                "title": "Clothes", "icon": "👕",
                "words": [("shirt", "कमीज़"), ("shoes", "जूते"), ("hat", "टोपी"), ("dress", "पोशाक"),
                          ("socks", "मोज़े"), ("coat", "कोट"), ("pants", "पतलून"), ("bag", "थैला")],
                "sentences": [
                    ("मेरी कमीज़ नई है।", "My shirt is new.", "shirt"),
                    ("ये जूते बहुत महँगे हैं।", "These shoes are very expensive.", "shoes"),
                    ("वह टोपी पहनता है।", "He wears a hat.", "hat"),
                    ("आज ठंड है, कोट पहनो।", "It is cold today, wear a coat.", "coat", ["It's cold today, wear a coat."]),
                    ("उसकी पोशाक लाल है।", "Her dress is red.", "dress"),
                    ("मेरा थैला भारी है।", "My bag is heavy.", "heavy"),
                ],
            },
        ],
    },
    {
        "title": "Daily Life", "description": "घर, सफ़र और समय", "color": "#ce82ff",
        "skills": [
            {
                "title": "Home", "icon": "🏠",
                "words": [("house", "घर"), ("door", "दरवाज़ा"), ("window", "खिड़की"), ("table", "मेज़"),
                          ("chair", "कुर्सी"), ("bed", "बिस्तर"), ("kitchen", "रसोई"), ("room", "कमरा")],
                "sentences": [
                    ("यह मेरा घर है।", "This is my house.", "house", ["This is my home."]),
                    ("दरवाज़ा खोलिए।", "Open the door.", "door"),
                    ("मेज़ पर किताब है।", "There is a book on the table.", "table"),
                    ("कमरा बड़ा है।", "The room is big.", "big"),
                    ("रसोई में माँ हैं।", "Mother is in the kitchen.", "kitchen", ["My mother is in the kitchen."]),
                    ("खिड़की बंद है।", "The window is closed.", "closed"),
                ],
            },
            {
                "title": "Travel", "icon": "🚌",
                "words": [("bus", "बस"), ("train", "रेलगाड़ी"), ("road", "सड़क"), ("market", "बाज़ार"),
                          ("school", "स्कूल"), ("hospital", "अस्पताल"), ("station", "स्टेशन"), ("ticket", "टिकट")],
                "sentences": [
                    ("मैं बाज़ार जा रहा हूँ।", "I am going to the market.", "market"),
                    ("बस कहाँ है?", "Where is the bus?", "Where"),
                    ("मुझे एक टिकट चाहिए।", "I need a ticket.", "ticket"),
                    ("स्टेशन पास में है।", "The station is nearby.", "nearby"),
                    ("वह अस्पताल में है।", "He is in the hospital.", "hospital", ["She is in the hospital."]),
                    ("रेलगाड़ी देर से आई।", "The train came late.", "late"),
                ],
            },
            {
                "title": "Time", "icon": "⏰",
                "words": [("today", "आज"), ("morning", "सुबह"), ("evening", "शाम"), ("night", "रात"),
                          ("Monday", "सोमवार"), ("Sunday", "रविवार"), ("week", "सप्ताह"), ("time", "समय")],
                "sentences": [
                    ("आज सोमवार है।", "Today is Monday.", "Monday"),
                    ("मैं सुबह उठता हूँ।", "I wake up in the morning.", "morning", ["I get up in the morning."]),
                    ("शाम को हम चाय पीते हैं।", "We drink tea in the evening.", "evening"),
                    ("रात को मैं सोता हूँ।", "I sleep at night.", "night"),
                    ("रविवार को छुट्टी है।", "There is a holiday on Sunday.", "Sunday"),
                    ("अभी क्या समय हुआ है?", "What time is it now?", "time"),
                ],
            },
            {
                "title": "Weather", "icon": "🌦️",
                "words": [("rain", "बारिश"), ("sun", "सूरज"), ("cloud", "बादल"), ("wind", "हवा"),
                          ("hot", "गरम"), ("cold", "ठंडा"), ("snow", "बर्फ़"), ("weather", "मौसम")],
                "sentences": [
                    ("आज बारिश हो रही है।", "It is raining today.", "raining", ["It's raining today."]),
                    ("आज बहुत गरमी है।", "It is very hot today.", "hot", ["It's very hot today.", "Today it is very hot."]),
                    ("आसमान में बादल हैं।", "There are clouds in the sky.", "clouds"),
                    ("सूरज चमक रहा है।", "The sun is shining.", "sun"),
                    ("आज मौसम अच्छा है।", "The weather is nice today.", "weather",
                     ["The weather is good today.", "Today the weather is nice."]),
                    ("सर्दियों में बर्फ़ गिरती है।", "Snow falls in winter.", "winter", ["It snows in winter."]),
                ],
            },
        ],
    },
]

LESSONS_PER_SKILL = 3

ACHIEVEMENTS = [
    # code, title, description, icon, metric, threshold, gem reward
    ("first_steps", "First Steps", "Complete your first lesson", "🌱", "lessons_completed", 1, 10),
    ("on_fire", "On Fire", "Reach a 3 day streak", "🔥", "streak", 3, 15),
    ("week_warrior", "Week Warrior", "Reach a 7 day streak", "⚔️", "streak", 7, 30),
    ("xp_hunter", "XP Hunter", "Earn 100 XP", "⚡", "total_xp", 100, 15),
    ("xp_master", "XP Master", "Earn 500 XP", "🏅", "total_xp", 500, 40),
    ("perfectionist", "Perfectionist", "Finish a lesson with no mistakes", "💎", "perfect_lessons", 1, 15),
    ("skill_master", "Skill Master", "Complete every lesson of a skill", "🎓", "skills_completed", 1, 20),
    ("goal_getter", "Goal Getter", "Hit your daily XP goal", "🎯", "goal_days", 1, 10),
    ("speedster", "Speedster", "Answer 10 questions correctly in a timed practice", "⏱️", "best_timed_correct", 10, 25),
    ("legend", "Legend", "Complete a legendary challenge", "👑", "legendary_count", 1, 50),
]

# name, display name, avatar colour, weekly xp  (leaderboard rivals)
RIVALS = [
    ("aarav", "Aarav Sharma", "#ff9600", 410), ("diya", "Diya Patel", "#ce82ff", 380),
    ("rohan", "Rohan Mehta", "#1cb0f6", 355), ("ananya", "Ananya Iyer", "#ff4b4b", 320),
    ("kabir", "Kabir Singh", "#58cc02", 290), ("ishita", "Ishita Rao", "#ffc800", 265),
    ("vihaan", "Vihaan Gupta", "#1cb0f6", 240), ("meera", "Meera Nair", "#ce82ff", 215),
    ("arjun", "Arjun Verma", "#ff9600", 180), ("saanvi", "Saanvi Joshi", "#58cc02", 150),
    ("dev", "Dev Malhotra", "#ff4b4b", 85), ("tara", "Tara Khan", "#1cb0f6", 60),
    ("yash", "Yash Reddy", "#ffc800", 40), ("kiara", "Kiara Das", "#ce82ff", 25),
]

# tier, name, colour  (everyone starts in Bronze)
LEAGUES = [(1, "Bronze League", "#cd7f32"), (2, "Silver League", "#a8b4c0"), (3, "Gold League", "#ffc800"),
           (4, "Sapphire League", "#1cb0f6"), (5, "Ruby League", "#ff4b4b"), (6, "Diamond League", "#ce82ff")]
