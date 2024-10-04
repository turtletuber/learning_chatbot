import streamlit as st
from openai import OpenAI
import google.auth
from google.cloud import aiplatform  # Assuming this is the client for Gemini API (adjust if needed)

# Show title and description
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that allows you to choose between using OpenAI's GPT-3.5 or Google's Gemini model to generate responses. "
    "You need to provide the corresponding API key or credentials to use either service."
)

# Allow the user to choose between OpenAI and Gemini
api_choice = st.selectbox("Choose the API:", ["OpenAI GPT-3.5", "Google Gemini"])

# Input fields for OpenAI and Gemini credentials based on the user's choice
if api_choice == "OpenAI GPT-3.5":
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Assuming Google Gemini API uses service account key for authentication
    service_account_key_path = st.text_input("Google Service Account Key Path", type="password")
    if not service_account_key_path:
        st.info("Please provide the path to your Google Service Account key file.", icon="🗝️")

# Initialize the client based on the selected API
if api_choice == "OpenAI GPT-3.5" and openai_api_key:
    # Create an OpenAI client
    client = OpenAI(api_key=openai_api_key)
elif api_choice == "Google Gemini" and service_account_key_path:
    # Initialize Google Gemini (or AI Platform) client
    credentials, project = google.auth.load_credentials_from_file(service_account_key_path)
    aiplatform.init(credentials=credentials, project=project)

# Chat interaction logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response based on the selected API
    if api_choice == "OpenAI GPT-3.5" and openai_api_key:
        # Generate a response using OpenAI API
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        # Stream the response to the chat
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    elif api_choice == "Google Gemini" and service_account_key_path:
        # Generate a response using Google Gemini API (adjust method as per actual API)
        # Here, we assume a Gemini-like model completion process, adjust for your specific API
        gemini_model = aiplatform.gapic.PredictionServiceClient(credentials=credentials)
        # Example model invocation (this is just placeholder logic, adjust to match Gemini's API)
        prediction_response = gemini_model.predict(
            endpoint="projects/{project}/locations/{location}/endpoints/{endpoint_id}",
            instances=[{"prompt": prompt}],
        )
        response = prediction_response.predictions[0]['content']
        # Display response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
