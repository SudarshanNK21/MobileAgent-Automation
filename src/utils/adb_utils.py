import adbutils
import uiautomator2 as u2
from loguru import logger
from src.agent.perception import parse_bounds


def connect_device():
    """
    Connect to the first available device/emulator.
    Returns a uiautomator2 device object.
    """
    devices = adbutils.adb.device_list()
    if not devices:
        raise RuntimeError("No devices/emulators connected. Run `adb devices` to check.")
    serial = devices[0].serial
    d = u2.connect(serial)
    logger.info(f"Connected to device: {serial}")
    return d


def take_screenshot(device, output_path="screenshot.png"):
    """
    Take a screenshot from the device and save it.
    """
    device.screenshot(output_path)
    logger.info(f"Screenshot saved to {output_path}")


def dump_ui_hierarchy(device, output_path="window_dump.xml"):
    """
    Dump the UI hierarchy (XML) from the device.
    """
    xml = device.dump_hierarchy()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml)
    logger.info(f"UI hierarchy dumped to {output_path}")


def tap(device, x, y):
    """
    Tap on the screen at given coordinates.
    """
    device.click(x, y)
    logger.info(f"Tapped at ({x}, {y})")


def input_text(device, text):
    """
    Input text into the currently focused field.
    """
    device.set_fastinput_ime(True)  # Enables fast input method
    device.send_keys(text)
    logger.info(f"Input text: {text}")


def press_back(device):
    """
    Press back button.
    """
    device.press("back")
    logger.info("Pressed Back")


def press_home(device):
    """
    Press home button.
    """
    device.press("home")
    logger.info("Pressed Home")
    
def tap_element(device, element):
    """
    Tap UI element given its bounds using uiautomator2 device object.
    """
    
    center = parse_bounds(element["bounds"])
    if center:
        x, y = center
        device.click(x, y)
        logger.info(f"Tapped element at {center} -> {element['text']}")
    else:
        logger.warning(f"Could not parse bounds for element: {element}")
