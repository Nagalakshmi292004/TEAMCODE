from dotenv import load_dotenv
load_dotenv()
import os
import streamlit as st
import google.generativeai as palm
import speech_recognition as sr
from PIL import Image
from fpdf import FPDF
import datetime

# ✅ Securely get API key from .env file
api_key = "" 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key is missing! Please set GOOGLE_API_KEY in your environment variables.")
    st.stop()

palm.configure(api_key=api_key)

# ========== AI Model List ==========
def list_available_models():
    try:
        models = list(palm.list_models())
        return models
    except Exception as e:
        st.error(f"Error listing models: {str(e)}")
        return []

# ========== AI Content Generation ==========
def get_symptom_advice(symptom_description, model_name):
    try:
        model = palm.GenerativeModel(model_name)
        response = model.generate_content(symptom_description)
        return response.text if response else "No advice generated."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# ========== Speech Recognition ==========
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak now.")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError:
            return "Speech recognition service unavailable."
        except Exception as e:
            return f"Error: {str(e)}"

# ========== Disease Detection ==========
def detect_possible_condition(symptom_text):
    text = symptom_text.lower()

    if all(k in text for k in ["fever", "body pain", "fatigue"]):
        return "🌡️ Possible condition detected: Dengue"
    elif all(k in text for k in ["cough", "sore throat", "chills"]):
        return "🌬️ Possible condition detected: Flu-like illness"
    elif all(k in text for k in ["vomiting", "diarrhea", "dehydration"]):
        return "🧪 Possible condition detected: Food Poisoning"
    elif all(k in text for k in ["headache", "nausea", "sensitivity to light"]):
        return "🧠 Possible condition detected: Migraine"
    return None

# ========== PDF Generator ==========
def generate_pdf(symptom, advice):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, "CareWise - Medical Advice Report", ln=True, align="C", fill=True)
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Symptom Description:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, symptom)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "AI Medical Advice:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, advice)

    filename = "HealthAdvice.pdf"
    pdf.output(filename)
    return filename

# ========== Streamlit UI Setup ==========
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

st.set_page_config(page_title="Health Advisor", page_icon="🏥", layout="wide")

image_path = "/mnt/data/download.jpg"
if os.path.exists(image_path):
    st.image(image_path, width=150)

st.markdown('<h1 style="text-align: center; color: #007BFF;">🏥 Health Advisor</h1>', unsafe_allow_html=True)
st.markdown("""
    <p style="font-size: 18px; text-align: center; color: #555;">
        Describe your symptoms below by typing or using voice input.
    </p>
""", unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size: 48px;">🩺</div>', unsafe_allow_html=True)

# ========== Voice Input ==========
if st.button("🎤 Speak Symptoms"):
    speech_text = recognize_speech()
    if speech_text and "could not" not in speech_text.lower():
        st.session_state.user_input = speech_text.strip()
        st.success(f"🗣️ You said: {speech_text}")
    else:
        st.warning("❌ Could not understand your speech. Please try again.")

# ========== Text Input ==========
user_input = st.text_area(
    "Enter your symptoms:",
    value=st.session_state.user_input,
    height=150,
    max_chars=500,
    help="Please provide as much detail as possible for accurate advice.",
    placeholder="Prompt be like I am suffering from fever, headache,..."
)
st.session_state.user_input = user_input

# ========== Medical Advice Button ==========
if st.button("Medical Advice", use_container_width=True):
    if st.session_state.user_input.strip():
        with st.spinner("Generating advice... Please wait."):
            models = list_available_models()
            if models:
                preferred_model = next((m.name for m in models if 'gemini-1.5-flash' in m.name), models[0].name)
                st.write(f"Using model: {preferred_model}")
                advice = get_symptom_advice(st.session_state.user_input, preferred_model)

                st.subheader("AI's Suggestion:")
                st.success(advice)

                # 🔍 Show possible condition
                possible_condition = detect_possible_condition(advice)
                if possible_condition:
                    st.info(possible_condition)

                # 📄 Show download button
                file_path = generate_pdf(st.session_state.user_input, advice)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Medical Advice (PDF)",
                        data=f,
                        file_name="HealthAdvice.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("No models available. Please check your credentials or GCP settings.")
    else:
        st.warning("Please enter or speak your symptoms for analysis.")
