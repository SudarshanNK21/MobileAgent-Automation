from src.utils import adb_utils
import time

if __name__ == "__main__":
    device = adb_utils.connect_device()

    # 1. Take screenshot
    adb_utils.take_screenshot(device, "test_screenshot.png")

    # 2. Dump UI hierarchy
    adb_utils.dump_ui_hierarchy(device, "test_ui.xml")

    # 3. Tap test (tap somewhere visible, e.g., center of the screen)
    screen_width, screen_height = device.window_size()
    center_x, center_y = screen_width // 2, screen_height // 2
    adb_utils.tap(device, center_x, center_y)
    time.sleep(2)

    # 4. Open Google search bar / input test (works if on home screen)
    adb_utils.input_text(device, "Hello from Python!")
    time.sleep(2)

    # 5. Press Back
    adb_utils.press_back(device)
    time.sleep(1)

    # 6. Press Home
    adb_utils.press_home(device)

    print("✅ Test completed. Check emulator for live interactions.")
