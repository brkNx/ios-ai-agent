import base64
import io
import time
import requests
from PIL import Image

class WDADriver:
    """WebDriverAgent (WDA) REST API istemcisi."""
    def __init__(self, base_url: str = "http://localhost:8100"):
        self.base_url = base_url.rstrip("/")
        self.session_id = None
        self._window_size = None

    def is_connected(self) -> bool:
        """WDA sunucusunun ayakta olup olmadığını kontrol eder."""
        try:
            r = requests.get(f"{self.base_url}/status", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.session_id = data.get("sessionId")
                return True
            return False
        except Exception:
            return False

    def get_session(self) -> str:
        """Mevcut oturumu alır veya yeni oturum başlatır."""
        if self.session_id:
            return self.session_id
        try:
            r = requests.post(
                f"{self.base_url}/session",
                json={"capabilities": {}},
                timeout=10
            )
            data = r.json()
            self.session_id = data.get("sessionId")
            return self.session_id
        except Exception as e:
            print(f"[!] Session alma hatası: {e}")
            return ""

    def get_window_size(self) -> tuple[int, int]:
        """Ekran çözünürlüğünü (point bazında) döndürür (width, height)."""
        if self._window_size:
            return self._window_size
        try:
            r = requests.get(f"{self.base_url}/window/size", timeout=5)
            res = r.json().get("value", {})
            w = int(res.get("width", 393))
            h = int(res.get("height", 852))
            self._window_size = (w, h)
            return self._window_size
        except Exception:
            return (393, 852)

    def screenshot(self) -> Image.Image:
        """Ekran görüntüsü alır ve PIL Image nesnesi döner."""
        r = requests.get(f"{self.base_url}/screenshot", timeout=10)
        res = r.json()
        b64_data = res.get("value", "")
        img_bytes = base64.b64decode(b64_data)
        return Image.open(io.BytesIO(img_bytes))

    def tap(self, x: int, y: int):
        """Ekranda (x, y) koordinatına tıklar."""
        url = f"{self.base_url}/wda/tap/nil"
        payload = {"x": x, "y": y}
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200

    def swipe(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.4):
        """Ekranda kaydırma hareketi yapar."""
        url = f"{self.base_url}/wda/dragfromtoforduration"
        payload = {
            "fromX": from_x,
            "fromY": from_y,
            "toX": to_x,
            "toY": to_y,
            "duration": duration
        }
        r = requests.post(url, json=payload, timeout=8)
        return r.status_code == 200

    def type_text(self, text: str):
        """Aktif odaklanmış alana metin yazar."""
        url = f"{self.base_url}/wda/keys"
        payload = {"value": list(text)}
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200

    def press_home(self):
        """Ana ekrana döner."""
        url = f"{self.base_url}/wda/homescreen"
        r = requests.post(url, timeout=5)
        return r.status_code == 200

    def launch_app(self, bundle_id: str):
        """Belirtilen bundle_id'ye sahip uygulamayı başlatır."""
        session_id = self.get_session()
        url = f"{self.base_url}/session/{session_id}/wda/apps/launch" if session_id else f"{self.base_url}/wda/apps/launch"
        payload = {"bundleId": bundle_id}
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
