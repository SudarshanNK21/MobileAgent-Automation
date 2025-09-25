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


def open_youtube_with_llava(device=None, ollama_url="http://localhost:11434/api/generate", model_name="llava"):
    """
    Take a screenshot, ask Llava if the user wants to open YouTube, and open it if so.
    """
    if device is None:
        device = adb_utils.connect_device()

    # Take screenshot
    screenshot_path = "vision_test.png"
    adb_utils.take_screenshot(device, screenshot_path)

    # Ask Llava what to do
    user_command = "open youtube"
    print(f"Sending screenshot and command '{user_command}' to Llava...")
    llava_response = test_llava_inference(screenshot_path, user_command, ollama_url, model_name)
    print("Llava response:", llava_response)

    # Simple logic: if 'youtube' in the command, open YouTube app
    if "youtube" in user_command.lower():
        print("Opening YouTube app on device...")
        # Try to launch YouTube via adb shell command
        try:
            # This uses uiautomator2's shell method
            device.shell(["am", "start", "-n", "com.google.android.youtube/com.google.android.youtube.HomeActivity"])
            print("YouTube app launched.")
        except Exception as e:
            print(f"Failed to launch YouTube: {e}")
        time.sleep(2)
    else:
        print("No YouTube command detected.")

    return llava_response
