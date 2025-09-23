from src.utils import adb_utils

if __name__ == "__main__":
    device = adb_utils.connect_device()

    # Take screenshot
    adb_utils.take_screenshot(device, "test_screenshot.png")

    # Dump UI hierarchy
    adb_utils.dump_ui_hierarchy(device, "test_ui.xml")

    print("Test completed. Check test_screenshot.png and test_ui.xml")
