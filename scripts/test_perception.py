from  src.utils import adb_utils
from src.agent import perception

if __name__ == "__main__":
    serial = adb_utils.connect_device()

    # Dump UI hierarchy
    adb_utils.dump_ui_hierarchy(serial, "test_ui.xml")

    # Parse it
    elements = perception.parse_ui_dump("test_ui.xml")
    print(f"Found {len(elements)} elements")

    # Try to find a search bar or settings text
    result = perception.find_element_by_text(elements, "Search")
    print("Search element:", result)
