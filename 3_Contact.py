import streamlit as st
page_bg = """
<style>
.stApp {
    background: linear-gradient(90deg, #bfd4bf, #ddd6e1);
    padding: 10px;
    transition: all 0.3s ease-in-out;
}
h1 {
    color: black;
    font-size: 3.5em;
    text-align: center;
    font-weight: bold;
    margin-bottom: 20px;
    font-family:  "Lucida Handwriting", cursive;
    animation: fadeIn 2s ease-in-out;
}
h2, h3, p {
    color: #333;
    text-align: center;
    font-family: 'Verdana', sans-serif;
    animation: slideIn 1.5s ease-in-out;
}

/* Center the button and add hover effect */
div.stButton > button {
    background-color: #00aaff;
    color: white;
    font-size: 1.3em;
    font-weight: bold;
    padding: 12px 25px;
    border-radius: 12px;
    border: 2px solid #0077cc;
    margin: 0 auto;
    display: block;
    box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.2);
    transition: background-color 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}

/* Button hover effect */
div.stButton > button:hover {
    background-color: #0077cc;
    color: #fff;
    box-shadow: 5px 5px 12px rgba(0, 0, 0, 0.3);
    cursor: pointer;
}


/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideIn {
    from { transform: translateY(30px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# Initialize session state variable if it doesn't exist
if 'started' not in st.session_state:
    st.session_state.started = False

# Main content display logic for the initial page
if not st.session_state.started:
    
    import streamlit as st
import smtplib
from email.mime.text import MIMEText

# Function to send the error report via email
def send_email(error_message, user_email):
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"
    receiver_email = "receiver_email@example.com"
    
    # Set up the email content
    subject = "Error Report"
    body = f"Error Message: {error_message}\nUser Email: {user_email}"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # Set up the SMTP server and send the email
    try:
        with smtplib.SMTP_SSL("smtp.example.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"

# Streamlit form for error submission
st.title("Submit an Error Report")

with st.form("error_form"):
    user_email = st.text_input("Your Email")
    error_message = st.text_area("Describe the error you encountered")
    submit_button = st.form_submit_button("Submit")

if submit_button:
    if user_email and error_message:
        result = send_email(error_message, user_email)
        st.success(result)
    else:
        st.warning("Please provide both your email and a description of the error.")
