import os
import streamlit as st
import google.generativeai as palm
import speech_recognition as sr

# Get API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")

# Check if API key is available
if not api_key:
    st.error("API Key is missing! Please set GOOGLE_API_KEY in your environment variables.")
    st.stop()

# Configure Generative AI with API key
palm.configure(api_key=api_key)

def list_available_models():
    """List available models in the project and return them as a list."""
    try:
        models = list(palm.list_models())
        return models
    except Exception as e:
        st.error(f" Error listing models: {str(e)}")
        return []

def get_symptom_advice(symptom_description, model_name):
    """Generate medical advice based on the given symptom description."""
    try:
        model = palm.GenerativeModel(model_name)
        response = model.generate_content(symptom_description)
        return response.text if response else "No advice generated."
    except Exception as e:
        return f" An error occurred: {str(e)}"

def recognize_speech():
    """Capture voice input and return transcribed text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak now.")
        try:
            recognizer.adjust_for_ambient_noise(source)  # Helps with background noise
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)  # Convert speech to text
            return text
        except sr.UnknownValueError:
            return " Could not understand audio."
        except sr.RequestError:
            return " Speech recognition service unavailable."
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize session state for user input if not already present
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Streamlit UI
st.set_page_config(page_title="Health Advisor", page_icon="🏥", layout="wide")

# Load and display the provided image as page icon
from PIL import Image
image_path = "/mnt/data/download.jpg"  # Ensure correct path to uploaded image
if os.path.exists(image_path):
    st.image(image_path, width=150)

# Header section (with blue color)
st.markdown('<h1 style="text-align: center; color: #007BFF;">🏥 Health Advisor</h1>', unsafe_allow_html=True)

# Info section
st.markdown("""
    <p style="font-size: 18px; text-align: center; color: #555;">
        Describe your symptoms below by typing or using voice input.
    </p>
""", unsafe_allow_html=True)

# Fixing the emoji rendering issue
st.markdown('<div style="text-align: center; font-size: 48px;">🩺</div>', unsafe_allow_html=True)

# Voice Input Button
if st.button(" Speak Symptoms"):
    speech_text = recognize_speech()
    if "" not in speech_text and "" not in speech_text:
        st.success(f" Transcribed Text: {speech_text}")
        st.session_state.user_input = speech_text  # Store speech input
        st.rerun()  # Force UI update
    else:
        st.warning(speech_text)

# Text area for user input (Now updates dynamically)
user_input = st.text_area(
    
    "Enter your symptoms:",
    value=st.session_state.user_input,
    height=150,
    max_chars=500,
    help="Please provide as much detail as possible for accurate advice.",
    placeholder="Prompt be like I amsuffering from fever, headache,..."
)

# Update session state with any manual changes to the text area
st.session_state.user_input = user_input

# Button to get medical advice
if st.button("Medical Advice", use_container_width=True):
    if st.session_state.user_input.strip():
        with st.spinner(" Generating advice... Please wait."):
            models = list_available_models()

            if models:
                preferred_model = next(
                    (m.name for m in models if 'gemini-1.5-pro-latest' in m.name), models[0].name
                )

                st.write(f" Using model: {preferred_model}")

                # Get AI advice based on symptoms
                advice = get_symptom_advice(st.session_state.user_input, preferred_model)
                st.subheader(" AI's Suggestion:")
                st.success(advice)
            else:
                st.error(" No models available. Please check your credentials or GCP settings.")
    else:
        st.warning(" Please enter or speak your symptoms for analysis.")
