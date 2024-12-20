import requests
import os
from dotenv import load_dotenv
# Load environment variables from .env file located two directories above the current file
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)
MODEL = os.getenv("openai_model")

def get_ephemeral_key():
    """
    Function to get an ephemeral API key for WebRTC connection to OpenAI's Realtime API.
    """
    url = "https://api.openai.com/v1/realtime/sessions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "voice": "verse"  # Optional customization
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()
