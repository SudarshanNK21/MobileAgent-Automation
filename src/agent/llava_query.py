def load_image(image_path):
    """Load an image from disk and return bytes."""
    with open(image_path, "rb") as f:
        return f.read()


import requests
import base64

# ADB imports
from src.utils import adb_utils
import time

def test_llava_inference(image_path, query="What is in the image?", ollama_url="http://localhost:11434/api/generate", model_name="llava"):
    """
    Send an image and prompt to Ollama's Llava model and return the response.
    """
    image_bytes = load_image(image_path)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": model_name,
        "prompt": query,
        "images": [image_b64],
        "stream": False
    }

    response = requests.post(ollama_url, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result.get("response", result)
    else:
        print(f"Ollama API error: {response.status_code} {response.text}")
        return None
