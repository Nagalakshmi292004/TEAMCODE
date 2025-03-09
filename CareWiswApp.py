import os
import streamlit as st
import google.generativeai as palm

# Get API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")

# Check if API key is available
if not api_key:
    st.error("❌ API Key is missing! Please set GOOGLE_API_KEY in your environment variables.")
    st.stop()  # Stop execution if API key is missing

# Configure Generative AI with API key
palm.configure(api_key=api_key)

def list_available_models():
    """List available models in the project and return them as a list."""
    try:
        models = list(palm.list_models())
        return models
    except Exception as e:
        st.error(f"❌ Error listing models: {str(e)}")
        return []

def get_symptom_advice(symptom_description, model_name):
    """Generate medical advice based on the given symptom description."""
    try:
        model = palm.GenerativeModel(model_name)
        response = model.generate_content(symptom_description)
        return response.text if response else "⚠️ No advice generated."
    except Exception as e:
        return f"❌ An error occurred: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="CareWise AI", page_icon="🏥", layout="wide")

# Header section
st.markdown('<h1 style="text-align: center; color: #4CAF50;">🏥 CareWise AI</h1>', unsafe_allow_html=True)

# Info section
st.markdown("""
    <p style="font-size: 18px; text-align: center; color: #555;">
        Describe your symptoms below, and get personalized medical advice from our AI system powered by Google's Generative AI.
    </p>
    <div style="text-align: center;">
        <span style="font-size: 48px;">🩺</span>
    </div>
""", unsafe_allow_html=True)

# User input
user_input = st.text_area(
    "💬 Describe your symptoms:",
    "",
    height=150,
    max_chars=500,
    help="Please provide as much detail as possible for accurate advice.",
    placeholder="Example: I have a fever, headache, and body aches..."
)

# Button to get medical advice
if st.button("Get Medical Advice", use_container_width=True):
    if user_input:
        with st.spinner("🔍 Generating advice... Please wait."):
            models = list_available_models()

            if models:
                preferred_model = next(
                    (m.name for m in models if 'gemini-1.5-pro-latest' in m.name), models[0].name
                )

                st.write(f"✨ Using model: {preferred_model}")

                # Get AI advice based on symptoms
                advice = get_symptom_advice(user_input, preferred_model)
                st.subheader("💡 AI's Suggestion:")
                st.success(advice)  # Styled output
            else:
                st.error("❌ No models available. Please check your credentials or GCP settings.")
    else:
        st.warning("⚠️ Please enter your symptoms for analysis.")

# Footer
st.markdown("""
    <hr>
    <p style="text-align: center; font-size: 14px; color: #777;">
        Powered by <a href="https://cloud.google.com/ai" target="_blank">Google Cloud AI</a> | Designed for quick medical assistance.
    </p>
""", unsafe_allow_html=True)
