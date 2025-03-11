import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import google.generativeai as genai
from io import BytesIO
from flask import jsonify
import re


# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/contact')
def contacts():
    return render_template('contact.html')

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

input_prompt4 = """
Act as a nutritionist:
1. Discover the name of the dish.
2. Provide two vegetarian dish alternatives to the uploaded dish images that have similar nutritional values.
3. Provide two non-vegetarian dish alternatives to the uploaded dish  images that have similar nutritional values.
"""



# Helper functions
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text


def input_image_setup(uploaded_file):
    try:
        # Open the image using Pillow
        image = Image.open(uploaded_file)

        # Check the image format and set the MIME type accordingly
        img_format = image.format.lower()  # Detect the format of the image

        if img_format == 'jpeg' or img_format == 'jpg':
            mime_type = 'image/jpeg'
            format_to_save = 'JPEG'
        elif img_format == 'png':
            mime_type = 'image/png'
            format_to_save = 'PNG'
        else:
            raise ValueError(f"Unsupported image format: {img_format}")

        # Convert the image to RGB mode if it's not already in RGB (applies for PNG with transparency)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Create a BytesIO buffer to hold the image data
        image_buffer = BytesIO()
        
        # Save the image in its appropriate format to the buffer
        image.save(image_buffer, format=format_to_save)

        # Get the byte data from the buffer
        image_bytes = image_buffer.getvalue()

        # Prepare the image data to send to the API
        image_parts = [
            {
                "mime_type": mime_type,  # Set the MIME type dynamically based on the image format
                "data": image_bytes  # Use the byte data of the image
            }
        ]
        
        return image_parts

    except Exception as e:
        raise ValueError(f"Error processing image: {e}")








@app.route('/dish', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_language = request.form.get('language')
        uploaded_file = request.files.get('image')
        input_text = request.form.get('input_text')

        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(image_path)

            # Handle form actions
            action = request.form.get('action')
            
            # Pass the FileStorage object directly
            pdf_content = input_image_setup(uploaded_file)

            if action == "get_dish":
                input_prompt = input_prompt1 if selected_language == 'English' else input_prompt1_telugu
                response = get_gemini_response(input_prompt, pdf_content, input_text)
            elif action == "how_to_cook":
                input_prompt = input_prompt2 if selected_language == 'English' else input_prompt2_telugu
                response = get_gemini_response(input_prompt, pdf_content, input_text)
            elif action == "nutrition_value":
                input_prompt = input_prompt3 if selected_language == 'English' else input_prompt3_telugu
                response = get_gemini_response(input_prompt, pdf_content, input_text)
            
            
            # Format the response
            formatted_response = format_response(response)
            
            return render_template('index.html', response=formatted_response, image_url=url_for('uploaded_file', filename=filename))

    return render_template('index.html', response=None)




import re

def format_response(response):
    """
    Function to format the AI response into HTML with special handling for text enclosed in triple asterisks.
    """
    # First, handle bold text enclosed in triple asterisks (e.g., ***text***)
    response = re.sub(r'\*\*(.*?.)\*\*', r'<strong>\1</strong>', response)
    
    # Convert single asterisks for italic (e.g., *text*) to HTML <em> tags
    # response = re.sub(r'\*(.*?)\*', r'</em>\1</em>', response)
    
    # Replace new lines with <br> tags for better readability
    response = response.replace('\n', '<br>')

    # Optionally, if there are lists (e.g., * item1\n* item2), convert them to HTML lists
    # response = re.sub(r'\* (.+?)<br>', r'<li>\1</li>', response)
    response = re.sub(r'(<li>.+?</li>)<br>', r'\1', response)  # Remove unnecessary <br> tags after list items
    response = re.sub(r'(<li>.*?</li>)+', r'<ul>\1</ul>', response)  # Wrap list items in <ul>
    ingredients_list = response.split('\n')

    # Create HTML structure for each ingredient with a box (div)
    formatted_response = ""
    for ingredient in ingredients_list:
        if ingredient.strip():  # Check for non-empty ingredient text
            formatted_response += f"<div class='ingredient-box'>{ingredient.strip()}</div>\n"

    return formatted_response

    


@app.route('/dish/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)










input_prompts = {
    "get_ingredients": {
        "English": "List  ingredients only for the dish named '{}'.",
        "Telugu": "వంటకం యొక్క పేరు '{}' కోసం పదార్థాలను జాబితా చేయండి."
    },
    "get_preparation": {
        "English": "Provide step-by-step preparation instructions for the dish named '{}'.",
        "Telugu": "వంటకం యొక్క పేరు '{}' కోసం దశల వారీగా తయారీ దశలను ఇవ్వండి."
    },
    "get_nutrition": {
        "English": "What are the nutritional values for the dish named '{}' ? Provide in a table format.",
        "Telugu": "వంటకం యొక్క పేరు '{}' కు సంబంధించిన పోషక విలువలు ఏమిటి? పట్టికలో ఇవ్వండి."
    }
}



# Helper function to get response from Gemini AI
def get_gemini_response_for_dishname(input_prompt, context=""):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt + context])
    return response.text

# Function to format AI response into HTML
def format_response_for_dishname(response):
    response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)
    response = response.replace('\n', '<br>')
    return response

@app.route('/cusine', methods=['GET', 'POST'])
def indexes():
    if request.method == 'POST':
        selected_language = request.form.get('language')
        dish_name = request.form.get('dish_name')
        action = request.form.get('action')

        if dish_name and action in ['get_ingredients', 'get_preparation', 'get_nutrition']:
           
            # Use dish name input to get specific information (ingredients, preparation, nutrition)
            input_prompt = input_prompts[action][selected_language].format(dish_name)
            response = get_gemini_response_for_dishname(input_prompt)
            formatted_response = format_response_for_dishname(response)
            return render_template('index2.html', response=formatted_response, dish_name=dish_name)

    return render_template('index2.html', response=None)

if __name__ == "__main__":
    app.run(debug=True)






