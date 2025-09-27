import time
from src.utils import adb_utils
from src.agent import perception, vision, vlm_llava


# --- Updated MobileAgent with LLaVA LLM for dynamic tasks ---
import json, re


class MobileAgent:
    def __init__(self, ollama_url="http://localhost:11434/api/generate"):
        self.device = adb_utils.connect_device()
        self.ollama_url = ollama_url

    def open_app(self, app_name, activity=None):
        """
        Open an app by name using a package mapping. Add more mappings as needed.
        """
        app_package_map = {
            "amazon": "in.amazon.mShop.android.shopping",
            "clock": "com.android.deskclock",
            "youtube": "com.google.android.youtube",
            "chrome": "com.android.chrome",
            # Add more as needed
        }
        package = app_package_map.get(app_name.lower())
        if not package:
            print(f"[ERROR] No package mapping found for app: {app_name}")
            return False
        if activity:
            self.device.shell(["am", "start", "-n", f"{package}/{activity}"])
        else:
            self.device.shell(["monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"])
        print(f"[Agent] Opened app: {app_name} (package: {package})")
        time.sleep(2)
        return True

    def find_element(self, keyword, vision_query=None, score_threshold=0.2, screenshot_path="agent_screen.png"):
        # 1. Try UI hierarchy
        adb_utils.dump_ui_hierarchy(self.device, "agent_ui.xml")
        elements = perception.parse_ui_dump("agent_ui.xml")
        el = perception.find_element_by_text(elements, keyword)
        if el:
            print(f"[UI] Found element by text: {el}")
            return el
        # 2. Try vision (OWL-ViT)
        adb_utils.take_screenshot(self.device, screenshot_path)
        if not vision_query:
            vision_query = keyword
        el = vision.detect_element(screenshot_path, query=vision_query, score_threshold=score_threshold)
        if el:
            print(f"[Vision] Found element by vision: {el}")
            return el
        # 3. Try LLaVA
        print("[LLaVA] Trying LLaVA fallback...")
        prompt = (
            f"Look at this screenshot. Identify the '{keyword}' element. "
            "Reply ONLY with coordinates in this JSON format: {\"x1\": number, \"y1\": number, \"x2\": number, \"y2\": number}. "
            "Do not include any explanation or extra text."
        )
        answer = vlm_llava.query_llava(screenshot_path, prompt, ollama_url=self.ollama_url)
        try:
            cleaned = answer.strip()
            cleaned = re.sub(r"^```(?:json)?", "", cleaned)
            cleaned = re.sub(r"```$", "", cleaned)
            cleaned = cleaned.strip()
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                coords = json.loads(match.group(0))
                x1, y1, x2, y2 = coords["x1"], coords["y1"], coords["x2"], coords["y2"]
                if x1 > x2: x1, x2 = x2, x1
                if y1 > y2: y1, y2 = y2, y1
                bounds_str = f"[{x1},{y1}][{x2},{y2}]"
                return {"text": keyword, "resource_id": "", "bounds": bounds_str}
        except Exception as e:
            print("[LLaVA] Could not parse response:", answer)
            print("Error:", e)
        return None

    def tap_element(self, element):
        adb_utils.tap_element(self.device, element)

    def input_text(self, text):
        adb_utils.input_text(self.device, text)

    def parse_task_to_steps(self, task):
        """
        Use LLaVA as an LLM to break down the user task into step-by-step UI actions.
        Now uses a real screenshot instead of a blank image for better reliability.
        """
        prompt = (
            "You are a mobile automation agent. Given the following user task, break it down into step-by-step UI actions for an Android device.\n"
            f"Task: '{task}'\n"
            "Reply ONLY with a JSON array of steps, each as a string. Do not include any explanation."
        )
        # Take a real screenshot for LLaVA LLM context
        print("[DEBUG] Taking screenshot for LLaVA LLM step parsing...")
        screenshot_path = "llava_llm_task.png"
        adb_utils.take_screenshot(self.device, screenshot_path)
        print(f"[DEBUG] Screenshot saved to {screenshot_path}")
        print(f"[DEBUG] Sending prompt to LLaVA: {prompt}")
        answer = vlm_llava.query_llava(screenshot_path, prompt, ollama_url=self.ollama_url)
        print(f"[DEBUG] LLaVA raw response: {answer}")
        try:
            cleaned = answer.strip()
            cleaned = re.sub(r"^```(?:json)?", "", cleaned)
            cleaned = re.sub(r"```$", "", cleaned)
            cleaned = cleaned.strip()
            steps = json.loads(cleaned)
            print("[LLaVA LLM] Parsed steps:", steps)
            return steps
        except Exception as e:
            print("[LLaVA LLM] Could not parse steps:", answer)
            print("Error:", e)
            return []

    def run_task(self, task):
        print(f"[Agent] User task: {task}")
        print("[DEBUG] Parsing task to steps with LLaVA...")
        steps = self.parse_task_to_steps(task)
        if not steps:
            print("[ERROR] No steps parsed from LLaVA. Aborting task.")
            return
        for i, step in enumerate(steps):
            print(f"[Agent] Step {i+1}: {step}")
            try:
                # Try to open app if step says so
                if re.search(r"open (.+?) app", step, re.IGNORECASE):
                    app_match = re.search(r"open (.+?) app", step, re.IGNORECASE)
                    app_name = app_match.group(1).strip()
                    print(f"[DEBUG] Attempting to open app: {app_name}")
                    if not self.open_app(app_name):
                        print(f"[ERROR] Failed to open app: {app_name}")
                        break
                    continue
                # Try to find element and tap
                print(f"[DEBUG] Finding element for step: {step}")
                el = self.find_element(step)
                if el:
                    self.tap_element(el)
                    print(f"[Agent] Tapped element for step: {step}")
                    time.sleep(1)
                else:
                    print(f"[WARN] Could not find element for step: {step}")
                # If step contains input text
                if re.search(r'"([^"]+)"', step):
                    m = re.search(r'"([^"]+)"', step)
                    if m:
                        self.input_text(m.group(1))
                        print(f"[Agent] Input text: {m.group(1)}")
                        time.sleep(1)
            except Exception as e:
                print(f"[ERROR] Exception in step {i+1}: {step}")
                print("Error:", e)
                break

if __name__ == "__main__":
    ollama_url = "http://localhost:11434/api/generate"
    agent = MobileAgent(ollama_url=ollama_url)
    user_task = input("Enter your mobile task: set an alarm at 7:45 am\n")
    agent.run_task(user_task)
