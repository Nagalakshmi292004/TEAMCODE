import os
import streamlit as st
import google.generativeai as palm
import speech_recognition as sr

# Get API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")

# Check if API key is available
if not api_key:
    st.error(" API Key is missing! Please set GOOGLE_API_KEY in your environment variables.")
    st.stop()

# Configure Generative AI with API key
palm.configure(api_key=api_key)

def list_available_models():
    """List available models."""
    try:
        models = list(palm.list_models())
        return models
    except Exception as e:
        st.error(f" Error listing models: {str(e)}")
        return []

def get_symptom_advice(symptom_description, model_name):
    """Generate medical advice using AI."""
    try:
        model = palm.GenerativeModel(model_name)
        response = model.generate_content(symptom_description)
        return response.text if response else " No advice generated."
    except Exception as e:
        return f" An error occurred: {str(e)}"

def recognize_speech():
    """Capture voice input."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info(" Listening... Please speak now.")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return " Could not understand audio."
        except sr.RequestError:
            return " Speech recognition service unavailable."
        except Exception as e:
            return f" Error: {str(e)}"

# Load background image from the correct path
bg_image_path = "back.jpg"  # Ensure this file is in the same directory as your script

# Apply custom background styling
st.markdown(
    f"""
    <style>
        .stApp {{
            background: url("data:image/jpg;base64,{open(bg_image_path, "rb").read().encode("base64").decode()}");
            background-size: cover;
            background-position: center;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit UI
st.set_page_config(page_title="CareWise AI", page_icon="🏥", layout="wide")

st.markdown('<h1 style="text-align: center; color: #4CAF50;">🏥 CareWise AI</h1>', unsafe_allow_html=True)

st.markdown("""
    <p style="font-size: 18px; text-align: center; color: #555;">
        Describe your symptoms below by typing or using voice input
    </p>
    <div style="text-align: center;">
        <span style="font-size: 48px;">🩺</span>
    </div>
""", unsafe_allow_html=True)

if st.button("🎙️ Speak Symptoms"):
    speech_text = recognize_speech()
    if "" not in speech_text and "" not in speech_text:
        st.success(f"📝 Transcribed Text: {speech_text}")
        st.session_state.user_input = speech_text
        st.rerun()
    else:
        st.warning(speech_text)

user_input = st.text_area(
    "💬 Describe your symptoms:",
    value=st.session_state.get("user_input", ""),
    height=150,
    max_chars=500,
    help="Please provide as much detail as possible for accurate advice.",
    placeholder="Example: I have a fever, headache, and body aches..."
)

st.session_state.user_input = user_input

if st.button("Get Medical Advice", use_container_width=True):
    if st.session_state.user_input.strip():
        with st.spinner("🔍 Generating advice... Please wait."):
            models = list_available_models()

            if models:
                preferred_model = next(
                    (m.name for m in models if 'gemini-1.5-pro-latest' in m.name), models[0].name
                )

                st.write(f"✨ Using model: {preferred_model}")

                advice = get_symptom_advice(st.session_state.user_input, preferred_model)
                st.subheader("💡 AI's Suggestion:")
                st.success(advice)
            else:
                st.error("No models available. Please check your credentials or GCP settings.")
    else:
        st.warning("Please enter or speak your symptoms for analysis.")

st.markdown("""
    <hr>
    <p style="text-align: center; font-size: 14px; color: #777;">
        Powered by <a href="https://cloud.google.com/ai" target="_blank">Google Cloud AI</a> | Designed for quick medical assistance.
    </p>
""", unsafe_allow_html=True)
