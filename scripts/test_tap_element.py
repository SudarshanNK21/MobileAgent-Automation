from src.utils import adb_utils
from src.agent import perception

if __name__ == "__main__":
    device = adb_utils.connect_device()

    # Dump hierarchy
    adb_utils.dump_ui_hierarchy(device, "test_ui.xml")

    # Parse
    elements = perception.parse_ui_dump("test_ui.xml")
    target = perception.find_element_by_text(elements, "videos")

    if target:
        adb_utils.tap_element(device, target)
        print(f"Tapped: {target}")
    else:
        print("Search element not found")
