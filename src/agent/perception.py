import xml.etree.ElementTree as ET
from loguru import logger
import re
def parse_ui_dump(xml_path="window_dump.xml"):
    """
    Parse dumped UI XML and return a list of elements with attributes.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    elements = []
    for node in root.iter():
        attrs = node.attrib
        if "text" in attrs or "resource-id" in attrs:
            elements.append({
                "text": attrs.get("text", ""),
                "resource_id": attrs.get("resource-id", ""),
                "bounds": attrs.get("bounds", "")
            })
    return elements

def find_element_by_text(elements, keyword):
    """
    Find element that contains the keyword in text.
    """
    for el in elements:
        if keyword.lower() in el["text"].lower():
            logger.info(f"Found element by text '{keyword}': {el}")
            return el
    return None

def parse_bounds(bounds_str):
    """
    Convert bounds string like '[206,91][779,236]' into (x, y) center.
    """
    nums = list(map(int, re.findall(r"\d+", bounds_str)))
    if len(nums) == 4:
        x1, y1, x2, y2 = nums
        return ( (x1+x2)//2, (y1+y2)//2 )
    return None