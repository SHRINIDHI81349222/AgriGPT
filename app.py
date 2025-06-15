from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_session import Session
from gtts import gTTS
import os
from datetime import datetime
from multi_agent_system import rule_based_response  # ✅ new function, no OpenAI
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
            user['language'] = language  # Send language to rule-based logic

            if language == 'ta':
                try:
                    query = GoogleTranslator(source='ta', target='en').translate(query)
                except:
                    response = "⚠️ மொழிபெயர்ப்பு தோல்வியடைந்தது."

            if not response:
                ai_response = rule_based_response(query, user)

                if language == 'ta':
                    try:
                        response = GoogleTranslator(source='en', target='ta').translate(ai_response)
                    except:
                        response = "⚠️ பதிலை தமிழில் மொழிபெயர்க்க முடியவில்லை."
                else:
                    response = ai_response

    return render_template("ask.html", language=language, text=translations.get(language, {}), user=user, response=response)

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    lang = session.get('language', 'en')

    if not text.strip():
        return "No text", 400

    try:
        filename = f"speech_{datetime.now().timestamp()}.mp3"
        filepath = os.path.join("static", filename)

        tts_lang = 'ta' if lang == 'ta' else 'en'
        tts = gTTS(text=text, lang=tts_lang)
        tts.save(filepath)

        return {'url': url_for('static', filename=filename)}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == "__main__":
    print("✅ AgriGPT is running at http://127.0.0.1:5000")
    app.run(debug=True)
