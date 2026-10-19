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
        print(f"\n[🚀] Hedef Başlatılıyor: '{goal}'")
        
        if not self.driver.is_connected():
            print("[❌] HATA: iPhone WDA sunucusuna bağlanılamadı!")
            print("     Lütfen telefonda WebDriverAgent'ın açık olduğundan emin olun.")
            return

        screen_size = self.driver.get_window_size()
        w, h = screen_size
        print(f"[📱] iPhone Bağlandı. Ekran: {w}x{h} points.")

        for step in range(1, self.max_steps + 1):
            print(f"\n--- [Adım {step}/{self.max_steps}] ---")
            
            # 1. Ekran görüntüsü al
            print("[📸] Ekran görüntüsü alınıyor...")
            screenshot = self.driver.screenshot()
            
            # 2. AI karar versin
            print("[🧠] AI ekrana bakıyor ve düşünüyor...")
            try:
                decision: ActionDecision = self.brain.decide_next_action(
                    image=screenshot,
                    screen_size=screen_size,
                    goal=goal,
                    history=self.history
                )
            except Exception as e:
                print(f"[❌] AI analiz hatası: {e}")
                break

            print(f"[💡 Neden]: {decision.reason}")
            print(f"[⚡ Eylem]: {decision.action.upper()}", end=" ")
            
            # 3. Eylemi uygula
            if decision.action == "tap":
                print(f"-> Koordinat: ({decision.x}, {decision.y})")
                self.driver.tap(decision.x, decision.y)
                self.history.append(f"Tıklandı: ({decision.x}, {decision.y}) - {decision.reason}")
                time.sleep(1.5)

            elif decision.action == "type":
                print(f"-> Metin: '{decision.text}'")
                self.driver.type_text(decision.text)
                self.history.append(f"Yazıldı: '{decision.text}'")
                time.sleep(1.0)

            elif decision.action == "swipe":
                print(f"-> Yön: {decision.direction}")
                self._handle_swipe(decision.direction, w, h)
                self.history.append(f"Kaydırıldı: {decision.direction}")
                time.sleep(1.5)

            elif decision.action == "home":
                print("-> Ana Ekrana Dönüldü")
                self.driver.press_home()
                self.history.append("Ana ekrana dönüldü")
                time.sleep(1.5)

            elif decision.action == "wait":
                sec = decision.seconds or 2
                print(f"-> {sec} saniye bekleniyor...")
                time.sleep(sec)
                self.history.append(f"{sec} sn beklendi")

            elif decision.action == "finish":
                print(f"\n[🎉 GÖREV TAMAMLANDI!]: {decision.result}")
                return

        print("\n[⚠️] Maksimum adım sınırına ulaşıldı.")

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
