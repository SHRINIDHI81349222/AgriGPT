from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_session import Session
from gtts import gTTS
import os
from datetime import datetime
from multi_agent_system import run_agents
from deep_translator import GoogleTranslator

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Translations
translations = {
    'en': {
        'title': "Register", 'name': "Name", 'email': "Email", 'password': "Password",
        'location': "Location", 'land_size': "Farm Size (in acres)", 'crop': "Preferred Crop",
        'register': "Register", 'login_link': "Already have an account? Login", 'login': "Login",
        'home_welcome': "Welcome", 'logout': "Logout",
        'ask_title': "Ask AgriGPT", 'back_home': "Back to Home",
        'ask_input_label': "Type your question:", 'ask_placeholder': "e.g., What crop should I grow in dry soil?",
        'btn_crop': "Best crop for me?", 'btn_irrigation': "Is irrigation needed?",
        'btn_market': "Market prices now?", 'btn_sustainability': "Am I eco-friendly?",
        'submit_btn': "Submit Question", 'thinking': "AgriGPT is analyzing your question...",
        'agrigpt_says': "AgriGPT Says:", 'waiting': "Waiting for your question..."
    },
    'ta': {
        'title': "பதிவு", 'name': "பெயர்", 'email': "மின்னஞ்சல்", 'password': "கடவுச்சொல்",
        'location': "இடம்", 'land_size': "பண்ணை அளவு (ஏக்கர்)", 'crop': "விருப்பமான பயிர்",
        'register': "பதிவுசெய்யவும்", 'login_link': "ஏற்கனவே கணக்கு உள்ளதா? உள்நுழைக", 'login': "உள்நுழை",
        'home_welcome': "வரவேற்பு", 'logout': "வெளியேறு",
        'ask_title': "அக்ரிGPT-யைக் கேளுங்கள்", 'back_home': "முகப்புக்கு திரும்பு",
        'ask_input_label': "உங்கள் கேள்வியை உள்ளிடவும்:",
        'ask_placeholder': "உதாரணம்: உலர்ந்த மண்ணில் என்ன பயிர் விதைக்கலாம்?",
        'btn_crop': "எனக்கு ஏற்ற பயிர்?", 'btn_irrigation': "நீர்ப்பாசனம் தேவைதானா?",
        'btn_market': "சந்தை விலை என்ன?", 'btn_sustainability': "நான் பசுமையாக இருக்கிறேனா?",
        'submit_btn': "கேள்வியை சமர்ப்பிக்கவும்",
        'thinking': "அக்ரிGPT உங்கள் கேள்வியை பகுப்பாய்வு செய்கிறது...",
        'agrigpt_says': "அக்ரிGPT சொல்கிறது:",
        'waiting': "தயவு செய்து உங்கள் கேள்வியை உள்ளிடவும்..."
    }
}

@app.context_processor
def inject_lang():
    lang = session.get('language', 'en')
    return dict(text=translations.get(lang, translations['en']), language=lang)

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/language', methods=['GET', 'POST'])
def language():
    if request.method == 'POST':
        session['language'] = request.form.get('language')
        return redirect(url_for('register'))
    return render_template('language.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['user'] = {
            'name': request.form['name'],
            'email': request.form['email'],
            'location': request.form['location'],
            'land_size': request.form['land_size'],
            'crop_type': request.form['crop']
        }
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = {
            'name': request.form['name'],
            'location': request.form.get('location', ''),
            'crop_type': request.form.get('crop_type', ''),
            'land_size': request.form.get('land_size', '')
        }
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', user=session['user'], language=session.get('language', 'en'))

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    language = session.get('language', 'en')
    response = None

    if request.method == 'POST':
        query = request.form.get('query') or request.form.get('custom_query', '').strip()

        if not query:
            response = "❌ Please enter a valid question." if language == 'en' else "❌ தயவுசெய்து ஒரு சரியான கேள்வியை உள்ளிடவும்."
        else:
            # Translate Tamil input to English
            if language == 'ta':
                query_translated = GoogleTranslator(source='ta', target='en').translate(query)
                prompt = f"Please answer this question clearly:\n{query_translated}"
            else:
                prompt = query

            # Run the agents
            ai_response = run_agents(prompt, user_data=user)

            # Translate back to Tamil
            if language == 'ta':
                try:
                    response = GoogleTranslator(source='en', target='ta').translate(ai_response)
                except Exception as e:
                    response = "⚠️ பதிலை தமிழில் மொழிபெயர்க்க முடியவில்லை."
            else:
                response = ai_response

    return render_template("ask.html", language=language, text=translations.get(language, {}), user=user, response=response)

@app.route('/market')
def market():
    if 'user' not in session:
        return redirect(url_for('login'))

    language = session.get('language', 'en')

    trends = [
        {
            "name_en": "Tomato",
            "name_ta": "தக்காளி",
            "price": "₹120/kg",
            "trend": "🔺 Rising (30% increase)",
            "region": "Tamil Nadu, Karnataka",
            "advice_en": "Tomato prices are soaring due to rainfall impact. Consider planning for next monsoon.",
            "advice_ta": "மழை காரணமாக விலை உயர்ந்துள்ளது. அடுத்த பருவத்திற்கு சாகுபடி திட்டமிடுங்கள்."
        },
        {
            "name_en": "Onion",
            "name_ta": "வெங்காயம்",
            "price": "₹95/kg",
            "trend": "🔺 High demand",
            "region": "Maharashtra, Tamil Nadu",
            "advice_en": "Shortage expected during festival season. High profit potential.",
            "advice_ta": "திருவிழா காலத்தில் பற்றாக்குறை. நல்ல லாப வாய்ப்பு."
        },
        {
            "name_en": "Banana",
            "name_ta": "வாழை",
            "price": "₹60–₹70/kg",
            "trend": "➡ Stable but in demand",
            "region": "Kerala, TN",
            "advice_en": "Steady export demand. Suitable for small-scale farmers too.",
            "advice_ta": "நிரந்தர ஏற்றுமதி தேவை. சிறு நிலத்திற்கும் ஏற்றது."
        },
        {
            "name_en": "Green Chili",
            "name_ta": "பச்சை மிளகாய்",
            "price": "₹140/kg",
            "trend": "🔺 Sharp increase",
            "region": "Andhra Pradesh, TN",
            "advice_en": "Consider intercrop options as price is rising sharply.",
            "advice_ta": "உருண்டு பயிராக சேர்த்து சாகுபடி செய்யலாம்."
        },
        {
            "name_en": "Coriander",
            "name_ta": "கொத்தமல்லி",
            "price": "₹80–₹100/kg",
            "trend": "🔼 Slightly Rising",
            "region": "All over South India",
            "advice_en": "Fast-growing leafy crop. Ideal during short rains.",
            "advice_ta": "வேகமாக வளரும். குறுகிய மழைக்காலத்திற்கு ஏற்றது."
        }
    ]

    return render_template("market.html", trends=trends, language=language)




@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    lang = session.get('language', 'en')

    if not text.strip():
        return "No text", 400

    try:
        filename = f"speech_{datetime.now().timestamp()}.mp3"
        filepath = os.path.join("static", filename)

        # Choose correct language
        tts_lang = 'ta' if lang == 'ta' else 'en'
        tts = gTTS(text=text, lang=tts_lang)
        tts.save(filepath)

        return {'url': url_for('static', filename=filename)}
    except Exception as e:
        return {'error': str(e)}, 500
@app.route('/news')
def news():
    if 'user' not in session:
        return redirect(url_for('login'))

    language = session.get('language', 'en')

    news_items = [
        {
            "title_en": "Tamil Nadu Government Launches e-Vaadagai Portal for Farmers",
            "title_ta": "தமிழ்நாடு அரசு விவசாயிகளுக்காக 'இ-வாடகை' தளத்தை அறிமுகம் செய்கிறது",
            "summary_en": "Now farmers can rent agri equipment online easily through a mobile portal.",
            "summary_ta": "இனி விவசாயிகள் விவசாய உபகரணங்களை ஆன்லைனில் எளிதாக வாடகைக்கு பெறலாம்.",
            "source": "https://www.tn.gov.in/",
            "date": "2025-06-12"
        },
        {
            "title_en": "Tomato Prices Surge in Chennai Wholesale Markets",
            "title_ta": "சென்னை மொத்த சந்தையில் தக்காளி விலை உயர்வு",
            "summary_en": "Tomato prices crossed ₹120/kg due to short rainfall this month.",
            "summary_ta": "மழையில்லாததால் தக்காளி விலை ₹120/கிலோ என உயர்ந்துள்ளது.",
            "source": "https://www.thehindu.com/",
            "date": "2025-06-10"
        },
        {
            "title_en": "AI in Agriculture: IIT Madras Launches Smart Farming Pilot",
            "title_ta": "விவசாயத்தில் செயற்கை நுண்ணறிவு: ஐஐடி மெட்ராஸ் 'ஸ்மார்ட்' திட்டம்",
            "summary_en": "Precision farming technology trialed in Kanchipuram district with drones and sensors.",
            "summary_ta": "காஞ்சிபுரம் மாவட்டத்தில் ட்ரோன் மற்றும் சென்சார் உதவியுடன் சோதனை செய்கிறது.",
            "source": "https://www.iitm.ac.in/",
            "date": "2025-06-09"
        },
        {
            "title_en": "New Solar Pump Subsidy Approved for TN Farmers",
            "title_ta": "தமிழ்நாட்டில் விவசாயிகளுக்காக புதிய சூரிய பம்ப் தள்ளுபடி",
            "summary_en": "Over 10,000 new solar pump sets to be distributed this financial year.",
            "summary_ta": "இந்த நிதியாண்டில் 10,000 சூரிய பம்ப்கள் வழங்க திட்டம்.",
            "source": "https://teda.in/",
            "date": "2025-06-08"
        },
        {
            "title_en": "Organic Farming Movement Gains Momentum Among Young Farmers",
            "title_ta": "இளைஞர் விவசாயிகளில் ஜৈவ விவசாயம் அதிகரிக்கிறது",
            "summary_en": "Awareness and training programs draw more youth into eco-farming.",
            "summary_ta": "விழிப்புணர்வு மற்றும் பயிற்சியால் இளைஞர்கள் பசுமை விவசாயத்தில் ஈடுபடுகின்றனர்.",
            "source": "https://vikatan.com/",
            "date": "2025-06-06"
        }
    ]

    return render_template("news.html", news_items=news_items, language=language)


@app.route("/eco")
def eco_friendly():
    language = session.get("language", "en")
    user_name = session.get("user", {}).get("name", "Farmer")

    suggestions = [
        {
            "name_en": "Organic Neem Oil Spray",
            "desc_en": "Natural pest control for vegetables and fruits.",
            "use_en": "Spray on leaves to repel insects and fungi.",
            "name_ta": "ஜைவ வேப்ப எண்ணெய் தெளிப்பு",
            "desc_ta": "பூச்சிகளை எதிர்க்க இயற்கை தீர்வு.",
            "use_ta": "இலைகளில் தெளித்து பூச்சிகளை விரட்டலாம்.",
            "link": "https://www.amazon.in/s?k=neem+oil+organic+spray"
        },
        {
            "name_en": "Vermicompost Fertilizer",
            "desc_en": "Improves soil structure and fertility using worm compost.",
            "use_en": "Mix with topsoil for healthy root growth.",
            "name_ta": "நண்டு உரம்",
            "desc_ta": "மண்ணை செறிவூட்டும் பசுமையான உரம்.",
            "use_ta": "மண்ணுடன் கலந்து பயிர்களுக்கு வேர்விருத்தி.",
            "link": "https://www.amazon.in/s?k=vermicompost"
        },
        {
            "name_en": "Bio Enzyme Cleaner (For Soil)",
            "desc_en": "Eco-alternative to chemical inputs, promotes soil microbes.",
            "use_en": "Dilute and spray weekly for enriched soil.",
            "name_ta": "பயோ என்சைம் உரம்",
            "desc_ta": "மண்ணுக்கான உயிரணு வளர்ப்பு ஊட்டச்சத்து.",
            "use_ta": "ஊற வைத்து வாரம் ஒருமுறை தெளிக்கவும்.",
            "link": "https://www.amazon.in/s?k=bio+enzyme+for+soil"
        },
        {
            "name_en": "Cocopeat Blocks",
            "desc_en": "Retains water and supports seed germination.",
            "use_en": "Ideal for nurseries and polyhouse farming.",
            "name_ta": "தென்னங்கொட்டைப் பூசி",
            "desc_ta": "நீரை பராமரிக்கும். விதை வளர்க்க உதவும்.",
            "use_ta": "நர்சரி மற்றும் ஹைட்ரோபோனிக்கில் பயன்படுத்தலாம்.",
            "link": "https://www.amazon.in/s?k=cocopeat+block"
        },
        {
            "name_en": "Cow Dung Cakes",
            "desc_en": "Traditional organic fertilizer rich in nutrients.",
            "use_en": "Dry and mix with field soil once a month.",
            "name_ta": "மாட்டுப்பாணை உரம்",
            "desc_ta": "மிகுந்த ஊட்டச்சத்து கொண்ட பாரம்பரிய உரம்.",
            "use_ta": "மணலில் கலந்து மாதம் ஒருமுறை பயன்படுத்தலாம்.",
            "link": "https://www.amazon.in/s?k=cow+dung+cakes"
        },
        {
            "name_en": "Mulching Film Sheet",
            "desc_en": "Reduces water loss and controls weeds.",
            "use_en": "Spread on field before sowing.",
            "name_ta": "மல்சிங் ஷீட்",
            "desc_ta": "நீர் இழப்பை குறைக்கும், களையை கட்டுப்படுத்தும்.",
            "use_ta": "விதை விதைக்குமுன் தரையில் விரிக்கவும்.",
            "link": "https://www.amazon.in/s?k=mulching+sheet"
        }
    ]

    return render_template("eco.html", suggestions=suggestions, user_name=user_name, language=language)

@app.route('/schemes')
def schemes():
    if 'user' not in session:
        return redirect(url_for('login'))

    language = session.get('language', 'en')

    schemes = [
        {
            "title_en": "PM-KISAN (Income Support)",
            "title_ta": "பிரதமர் கிசான் (வருமான உதவி)",
            "desc_en": "Provides ₹6,000 per year to small and marginal farmers in 3 installments.",
            "desc_ta": "சிறு விவசாயிகளுக்கு ஆண்டுக்கு ₹6,000 வரை மும்முறையாக வழங்கப்படுகிறது.",
            "scope": "National",
            "link": "https://pmkisan.gov.in/"
        },
        {
            "title_en": "Soil Health Card Scheme",
            "title_ta": "மண் ஆரோக்கிய அட்டை திட்டம்",
            "desc_en": "Farmers receive a card showing their soil condition and fertilizer recommendations.",
            "desc_ta": "மண்ணின் நிலை மற்றும் உர பரிந்துரைகளை விவசாயிகள் பெறுகின்றனர்.",
            "scope": "National",
            "link": "https://soilhealth.dac.gov.in/"
        },
        {
            "title_en": "Rainfed Area Development",
            "title_ta": "மழை சார்ந்த பகுதி மேம்பாடு",
            "desc_en": "Supports integrated farming in rainfed regions through crop-livestock integration.",
            "desc_ta": "மழை சார்ந்த இடங்களில் ஒருங்கிணைந்த விவசாயத்திற்கு ஆதரவு.",
            "scope": "National (specific states)",
            "link": "https://agriinfra.dac.gov.in/"
        },
        {
            "title_en": "Tamil Nadu Free Solar Pump Scheme",
            "title_ta": "தமிழ்நாடு சூரிய வெப்ப பம்ப் திட்டம்",
            "desc_en": "Subsidized solar-powered irrigation pumps for Tamil Nadu farmers.",
            "desc_ta": "தமிழ்நாட்டு விவசாயிகளுக்காக சூரிய பம்புகள் தள்ளுபடி விலையில் வழங்கப்படும்.",
            "scope": "Tamil Nadu",
            "link": "https://aed.tn.gov.in/en/schemes/renewal-energy-in-agriculture/chief-ministers-scheme-of-solar-powered-pumpsets/"
        },
        {
            "title_en": "Agriculture Infrastructure Fund (AIF)",
            "title_ta": "விவசாய உட்கட்டமைப்பு நிதி (AIF)",
            "desc_en": "Offers low-interest loans for setting up agri warehouses, cold chains, etc.",
            "desc_ta": "விவசாய குளிர் சேமிப்பு மற்றும் களஞ்சிய திட்டங்களுக்கு வட்டியில்லா கடன் வழங்கப்படும்.",
            "scope": "National",
            "link": "https://agriinfra.dac.gov.in/"
        }
    ]

    return render_template("schemes.html", schemes=schemes, language=language)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
