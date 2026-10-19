import base64
import io
import time
import requests
from PIL import Image

class WDADriver:
    """WebDriverAgent (WDA) REST API client using modern W3C Actions."""
    def __init__(self, base_url: str = "http://localhost:8100"):
        self.base_url = base_url.rstrip("/")
        self.session_id = None
        self._window_size = None

    def is_connected(self) -> bool:
        """Check if the WDA server is reachable."""
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
        """Get the current session or start a new one."""
        if self.session_id:
            return self.session_id
        try:
            r = requests.post(
                f"{self.base_url}/session",
                json={"capabilities": {}},
                timeout=10
            )
            data = r.json()
            self.session_id = data.get("sessionId") or data.get("value", {}).get("sessionId")
            return self.session_id
        except Exception as e:
            print(f"[!] Session acquisition error: {e}")
            return ""

    def get_window_size(self) -> tuple[int, int]:
        """Return screen resolution in points: (width, height)."""
        if self._window_size:
            return self._window_size
        session_id = self.get_session()
        try:
            url = f"{self.base_url}/session/{session_id}/window/size" if session_id else f"{self.base_url}/window/size"
            r = requests.get(url, timeout=5)
            res = r.json().get("value", {})
            w = int(res.get("width", 390))
            h = int(res.get("height", 844))
            self._window_size = (w, h)
            return self._window_size
        except Exception:
            return (390, 844)

    def screenshot(self) -> Image.Image:
        """Capture screenshot and return a PIL Image object."""
        r = requests.get(f"{self.base_url}/screenshot", timeout=10)
        res = r.json()
        b64_data = res.get("value", "")
        img_bytes = base64.b64decode(b64_data)
        return Image.open(io.BytesIO(img_bytes))

    def tap(self, x: int, y: int):
        """Tap at screen coordinates (x, y) using W3C pointer actions."""
        session_id = self.get_session()
        url = f"{self.base_url}/session/{session_id}/actions"
        payload = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "finger1",
                    "parameters": {"pointerType": "touch"},
                    "actions": [
                        {"type": "pointerMove", "duration": 0, "x": int(x), "y": int(y)},
                        {"type": "pointerDown", "button": 0},
                        {"type": "pause", "duration": 100},
                        {"type": "pointerUp", "button": 0}
                    ]
                }
            ]
        }
        r = requests.post(url, json=payload, timeout=8)
        return r.status_code == 200

    def swipe(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.4):
        """Perform a swipe gesture from (from_x, from_y) to (to_x, to_y)."""
        session_id = self.get_session()
        url = f"{self.base_url}/session/{session_id}/actions"
        duration_ms = int(duration * 1000)
        payload = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "finger1",
                    "parameters": {"pointerType": "touch"},
                    "actions": [
                        {"type": "pointerMove", "duration": 0, "x": int(from_x), "y": int(from_y)},
                        {"type": "pointerDown", "button": 0},
                        {"type": "pause", "duration": 50},
                        {"type": "pointerMove", "duration": duration_ms, "x": int(to_x), "y": int(to_y)},
                        {"type": "pointerUp", "button": 0}
                    ]
                }
            ]
        }
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200

    def type_text(self, text: str):
        """Type text into currently focused input element."""
        session_id = self.get_session()
        url = f"{self.base_url}/session/{session_id}/wda/keys"
        payload = {"value": list(text)}
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200

    def press_home(self):
        """Press the home button / navigate to SpringBoard."""
        url = f"{self.base_url}/wda/homescreen"
        r = requests.post(url, timeout=5)
        return r.status_code == 200

    def launch_app(self, bundle_id: str):
        """Launch an application by its bundleId."""
        r = requests.post(
            f"{self.base_url}/session",
            json={"capabilities": {"bundleId": bundle_id}},
            timeout=10
        )
        data = r.json()
        self.session_id = data.get("sessionId") or data.get("value", {}).get("sessionId")
        return bool(self.session_id)
