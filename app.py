from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from datetime import datetime
from multi_agent_system import run_agents  # Use your real multi-agent handler

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Translation dictionary
translations = {
    'en': {
        'title': "Register",
        'name': "Name",
        'email': "Email",
        'password': "Password",
        'location': "Location",
        'land_size': "Farm Size (in acres)",
        'crop': "Preferred Crop",
        'register': "Register",
        'login_link': "Already have an account? Login",
        'login': "Login",
        'home_welcome': "Welcome",
        'logout': "Logout"
    },
    'ta': {
        'title': "பதிவு",
        'name': "பெயர்",
        'email': "மின்னஞ்சல்",
        'password': "கடவுச்சொல்",
        'location': "இடம்",
        'land_size': "பண்ணை அளவு (ஏக்கர்)",
        'crop': "விருப்பமான பயிர்",
        'register': "பதிவுசெய்யவும்",
        'login_link': "ஏற்கனவே கணக்கு உள்ளதா? உள்நுழைக",
        'login': "உள்நுழை",
        'home_welcome': "வரவேற்பு",
        'logout': "வெளியேறு"
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

    response = None
    if request.method == 'POST':
        query = request.form.get('query') or request.form.get('custom_query')
        query = query.strip() if query else ""
        
        if not query:
            response = "❌ Please enter a valid question." if session.get('language') == 'en' else "❌ தயவுசெய்து ஒரு சரியான கேள்வியை உள்ளிடவும்."
        else:
            response = run_agents(query, user_data=session['user'])

    return render_template('ask.html', user=session['user'], response=response, language=session.get('language', 'en'))


@app.route('/market')
def market():
    if 'user' not in session:
        return redirect(url_for('login'))

    month = datetime.now().month
    seasonals = []
    if month in [3, 4, 5]:
        seasonals = ['🥭 Mango', '🍉 Watermelon', '🥥 Tender Coconut']
    elif month in [6, 7, 8]:
        seasonals = ['🌽 Corn', '🍅 Tomato']
    elif month in [9, 10, 11]:
        seasonals = ['🥔 Potato', '🍠 Sweet Potato']
    else:
        seasonals = ['🥕 Carrot', '🍓 Strawberry']

    return render_template('market.html', seasonals=seasonals)

@app.route('/news')
def news():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('news.html')

@app.route("/eco")
def eco_friendly():
    user_name = session.get("user", {}).get("name", "Farmer")
    language = session.get("language", "en")

    suggestions = [
        {
            "name_en": "General Organic Fertilizer Pack",
            "desc_en": "Safe for all crops and environments.",
            "name_ta": "பொது ஜைவ உரப்பொதி",
            "desc_ta": "அனைத்து பயிர்களுக்கும் பாதுகாப்பானது.",
            "link": "https://www.amazon.in/s?k=general+Organic+Fertilizer+Pack"
        },
        {
            "name_en": "Neem Cake Powder",
            "desc_en": "Natural soil booster and pest repellent.",
            "name_ta": "வேப்பம்பிண்டி தூள்",
            "desc_ta": "மண்ணை மேம்படுத்தும் நச்சுநீக்கி.",
            "link": "https://www.amazon.in/s?k=Neem+Cake+Powder"
        },
        {
            "name_en": "Compost Maker Kit",
            "desc_en": "Speed up composting for organic farming.",
            "name_ta": "உரமாவது மெக்கர் கிட்",
            "desc_ta": "சுருக்கமாக உரமாக்கும் கருவி.",
            "link": "https://www.amazon.in/s?k=Compost+Maker+Kit"
        }
    ]

    return render_template("eco.html", user_name=user_name, language=language, suggestions=suggestions)

@app.route('/schemes')
def schemes():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('schemes.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
