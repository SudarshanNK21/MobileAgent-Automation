from src.agent import vision
from src.utils import adb_utils

if __name__ == "__main__":
    device = adb_utils.connect_device()

    # Take screenshot
    adb_utils.take_screenshot(device, "vision_test.png")

    # Find element by vision
    target = vision.detect_element("vision_test.png", query="playstore icon", score_threshold=0.2)

    if target:
        adb_utils.tap_element(device, target)
        print(f"Tapped: {target}")
    else:
        print("Element not found by vision")

    print("Debug image saved as vision_debug.png")
