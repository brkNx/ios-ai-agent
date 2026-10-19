import time
from wda_driver import WDADriver
from brain import VisionBrain, ActionDecision

class IOSAgent:
    def __init__(self, wda_url: str = "http://localhost:8100", max_steps: int = 15):
        self.driver = WDADriver(wda_url)
        self.brain = VisionBrain()
        self.max_steps = max_steps
        self.history = []

    def run(self, goal: str):
        print(f"\n[🚀] Launching Goal: '{goal}'")
        
        if not self.driver.is_connected():
            print("[❌] ERROR: Cannot reach iPhone WDA server!")
            print("     Make sure WebDriverAgent is running on your iPhone and port 8100 is accessible.")
            return

        screen_size = self.driver.get_window_size()
        w, h = screen_size
        print(f"[📱] Connected to iPhone. Screen: {w}x{h} points.")

        for step in range(1, self.max_steps + 1):
            print(f"\n--- [Step {step}/{self.max_steps}] ---")
            
            # 1. Capture screen
            print("[📸] Capturing screenshot...")
            screenshot = self.driver.screenshot()
            
            # 2. Vision perception & decision
            print("[🧠] AI analyzing screen and deciding action...")
            try:
                decision: ActionDecision = self.brain.decide_next_action(
                    image=screenshot,
                    screen_size=screen_size,
                    goal=goal,
                    history=self.history
                )
            except Exception as e:
                print(f"[❌] AI perception error: {e}")
                break

            print(f"[💡 Reason]: {decision.reason}")
            print(f"[⚡ Action]: {decision.action.upper()}", end=" ")
            
            # 3. Execute action
            if decision.action == "tap":
                print(f"-> Coordinate: ({decision.x}, {decision.y})")
                self.driver.tap(decision.x, decision.y)
                self.history.append(f"Tapped: ({decision.x}, {decision.y}) - {decision.reason}")
                time.sleep(1.5)

            elif decision.action == "type":
                print(f"-> Text: '{decision.text}'")
                self.driver.type_text(decision.text)
                self.history.append(f"Typed: '{decision.text}'")
                time.sleep(1.0)

            elif decision.action == "swipe":
                print(f"-> Direction: {decision.direction}")
                self._handle_swipe(decision.direction, w, h)
                self.history.append(f"Swiped: {decision.direction}")
                time.sleep(1.5)

            elif decision.action == "home":
                print("-> Pressed Home Button")
                self.driver.press_home()
                self.history.append("Pressed Home button")
                time.sleep(1.5)

            elif decision.action == "wait":
                sec = decision.seconds or 2
                print(f"-> Waiting for {sec} seconds...")
                time.sleep(sec)
                self.history.append(f"Waited {sec}s")

            elif decision.action == "finish":
                print(f"\n[🎉 TASK COMPLETED!]: {decision.result}")
                return

        print("\n[⚠️] Max step limit reached.")

    def _handle_swipe(self, direction: str, w: int, h: int):
        cx, cy = w // 2, h // 2
        if direction == "up":
            self.driver.swipe(cx, cy + 200, cx, cy - 200)
        elif direction == "down":
            self.driver.swipe(cx, cy - 200, cx, cy + 200)
        elif direction == "left":
            self.driver.swipe(cx + 150, cy, cx - 150, cy)
        elif direction == "right":
            self.driver.swipe(cx - 150, cy, cx + 150, cy)
