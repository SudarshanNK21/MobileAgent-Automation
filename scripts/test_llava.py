# from src.agent.vlm_llava import test_llava_inference,open_youtube_with_llava

# if __name__ == "__main__":
#     # Path to the image you want to test
#     image_path = "vision_test.png"  # Change if needed
#     query = "Describe the main object."
    
#     # print(f"Sending image '{image_path}' to Llava with query: '{query}'...")
#     # result = test_llava_inference(image_path, query)
#     # print("Llava result:", result)

#     print("Testing Llava + ADB integration for 'open youtube' command...")
#     response = open_youtube_with_llava()
#     print("Llava response:", response)

from src.utils import adb_utils
from src.agent.vlm_llava import query_llava
import json
import re
from PIL import Image, ImageDraw

if __name__ == "__main__":
    device = adb_utils.connect_device()

    # Take screenshot
    adb_utils.take_screenshot(device, "llava_test.png")

    # Ask LLaVA
    prompt = (
        "Look at this screenshot. Identify the YouTube app icon. "
        "Reply ONLY with coordinates in this JSON format: "
        "{\"x1\": number, \"y1\": number, \"x2\": number, \"y2\": number}. "
        "If possible, output normalized values (0–1). Do not add text."
    )
    answer = query_llava("llava_test.png", prompt)
    print("Raw LLaVA response:", repr(answer))

    try:
        # Clean markdown code fences
        cleaned = answer.strip()
        cleaned = re.sub(r"^```(?:json)?", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)
        cleaned = cleaned.strip()

        # Extract JSON
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in response")
        coords = json.loads(match.group(0))

        x1, y1, x2, y2 = coords["x1"], coords["y1"], coords["x2"], coords["y2"]

        # Get device screen size
        width, height = device.window_size()
        print(f"Device screen size: {width}x{height}")
        print(f"Raw coordinates: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

        # --- 🔹 Auto detect normalized vs absolute ---
        if all(0 <= v <= 1 for v in [x1, y1, x2, y2]):
            # Normalize
            x1, x2 = int(x1 * width), int(x2 * width)
            y1, y2 = int(y1 * height), int(y2 * height)
            print("Detected normalized coords → scaled to pixels")
        else:
            # Assume already pixel values
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            print("Detected absolute coords")

        # Ensure proper ordering
        if x1 > x2: x1, x2 = x2, x1
        if y1 > y2: y1, y2 = y2, y1

        # Clamp to screen
        x1, x2 = max(0, x1), min(width, x2)
        y1, y2 = max(0, y1), min(height, y2)

        # Center
        x, y = (x1 + x2) // 2, (y1 + y2) // 2
        print(f"Tap center: ({x},{y})")

        # Draw debug image
        img = Image.open("llava_test.png").convert("RGB")
        draw = ImageDraw.Draw(img)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        r = 10
        draw.ellipse([x - r, y - r, x + r, y + r], outline="blue", width=3)
        img.save("llava_test_marked.png")
        print("Saved marked screenshot as llava_test_marked.png")

        # Tap
        adb_utils.tap(device, x, y)
        print(f"Tapped YouTube at ({x},{y})")

    except Exception as e:
        print("Could not parse or use JSON from LLaVA response:", answer)
        print("Error:", e)


