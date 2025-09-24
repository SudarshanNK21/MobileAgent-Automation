from src.agent import vision
from src.utils import adb_utils

if __name__ == "__main__":
    device = adb_utils.connect_device()

    # Take screenshot
    adb_utils.take_screenshot(device, "vision_test.png")

    # Try to find element by vision
    box = vision.detect_element("vision_test.png", query="youtube")
    if box:
        x1, y1, x2, y2 = box
        x, y = (x1 + x2)//2, (y1 + y2)//2
        device.click(x, y)
        print(f"Tapped element at {x},{y}")
    else:
        print("Element not found by vision")
