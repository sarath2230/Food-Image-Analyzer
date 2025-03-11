import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import google.generativeai as genai
from io import BytesIO
from flask import jsonify



# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Google Generative AI
os.environ["GOOGLE_API_KEY"] = "AIzaSyAV6sfg2mb64Jw3uiDObFaeDkIHbKIaY1w"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Define input prompts in English and Telugu
input_prompt1 = """
Embark on a culinary exploration as you uncover the secrets of the delectable dish in the uploaded image:
1. Discover the name of the dish.
2. Discover the ingredients required to prepare the dish only.
"""

input_prompt1_telugu = """
మీరు అప్‌లోడ్ చేసిన చిత్రంలో వంటకం యొక్క రహస్యాలను అన్వేషిస్తూ ఒక వంటక అన్వేషణలో పాల్గొనండి:
1. వంటకం యొక్క పేరు మరియు వంటకానికి సంబంధించిన ముఖ్యమైన వివరాలను కనుగొనండి.
2. వంటకంలోని ఆసక్తికరమైన మూలాలను అన్వేషించండి, దాని సాంస్కృతిక మరియు చారిత్రక ప్రాముఖ్యతను ఆవిష్కరించండి.
3. వంటకం యొక్క రుచికరమైన రుచిని తీసుకురావడంలో సహకరించే పదార్థాల గురించి పాయింట్ల రూపంలో వివరించండి.
"""

input_prompt2 = """
As a culinary maestro guiding eager chefs, lay out the meticulous steps for crafting the featured dish:
1."Can you provide a step-by-step guide for preparing this dish in simple English? Please include what needs to be done in each step, the ingredients to use, and how long or at what temperature to cook. 
Make sure the instructions are easy for beginners to follow."

"""


input_prompt2_telugu = """
ఆసక్తికరమైన వంటకాన్ని తయారు చేయడానికి కావాల్సిన వివరణాత్మక దశలను వివరించండి:
1. నాణ్యత మరియు తాజాదనంపై ప్రత్యేక దృష్టితో ఉత్తమ పదార్థాలను ఎంచుకోవడం ప్రారంభించండి.
2. ప్రతి పదార్థాన్ని శుభ్రపరచడం, తొక్క తొలగించడం మరియు ఖచ్చితంగా తరిగే ప్రక్రియను వివరించండి.
3. వంట ప్రక్రియలో ప్రతి దశను వివరించండి, వంటకాన్ని అద్భుతంగా మార్చడానికి నిపుణుల చిట్కాలు పంచుకోండి.
4. సాధారణ వంటకాన్ని అద్భుతంగా మార్చడానికి నైపుణ్యంతో ప్రదర్శించండి.

"""

input_prompt3 = """
In your role as a nutritional advisor, present a comprehensive overview of the dish's nutritional value:
1. Discover the ingredients required to prepare the dish.
2."Please provide the nutrition values in a table format.The table should have four columns: 'Nutrient', 'Amount' . Include calories, proteins, fats, and carbohydrates

"""
input_prompt3_telugu = """
పోషణ నిపుణుడిగా మీ పాత్రలో వంటకం యొక్క పూర్తి పోషక విలువలను సమర్పించండి:
1. కేలరీలు, ప్రోటీన్లు, కొవ్వులు మరియు కార్బోహైడ్రేట్లు వంటి పోషక విలువలను చూపించే పట్టికను డిసెండింగ్ క్రమంలో ప్రదర్శించండి.
2. ప్రతి పదార్థం యొక్క పోషక విలువలను వివరించే మరో పట్టికను తయారు చేయండి, వంటకంలోని ఆహార రహస్యాలను బయటపెట్టండి.
"""

# Helper functions
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text
