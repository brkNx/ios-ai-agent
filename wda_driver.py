import base64
import io
import time
import requests
from PIL import Image

class WDADriver:
    """High-performance WebDriverAgent (WDA) REST API client using W3C Actions and Keep-Alive."""
    def __init__(self, base_url: str = "http://localhost:8100"):
        self.base_url = base_url.rstrip("/")
        self.session_id = None
        self._window_size = None
        self.http = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=1)
        self.http.mount("http://", adapter)
        self.http.mount("https://", adapter)

    def is_connected(self) -> bool:
        """Check if WDA server is reachable and cache session ID."""
        try:
            r = self.http.get(f"{self.base_url}/status", timeout=2)
            if r.status_code == 200:
                data = r.json()
                self.session_id = data.get("sessionId")
                if self.session_id:
                    self._apply_speed_settings()
                return True
            return False
        except Exception:
            return False

    def get_session(self) -> str:
        """Get the current session or start a new one."""
        if self.session_id:
            return self.session_id
        try:
            r = self.http.post(
                f"{self.base_url}/session",
                json={"capabilities": {}},
                timeout=5
            )
            data = r.json()
            self.session_id = data.get("sessionId") or data.get("value", {}).get("sessionId")
            if self.session_id:
                self._apply_speed_settings()
            return self.session_id or ""
        except Exception as e:
            print(f"[!] Session acquisition error: {e}")
            return ""

    def _apply_speed_settings(self):
        """Configure WDA for maximum speed and reduced payload latency."""
        try:
            url = f"{self.base_url}/session/{self.session_id}/appium/settings"
            payload = {
                "settings": {
                    "mjpegServerScreenshotQuality": 40,
                    "mjpegServerFramerate": 30,
                    "screenshotQuality": 2,
                    "shouldUseCompactResponses": True,
                    "waitForIdleTimeout": 0.05
                }
            }
            self.http.post(url, json=payload, timeout=2)
        except Exception:
            pass

    def get_window_size(self) -> tuple[int, int]:
        """Return screen resolution in points: (width, height)."""
        if self._window_size:
            return self._window_size
        session_id = self.get_session()
        try:
            url = f"{self.base_url}/session/{session_id}/window/size" if session_id else f"{self.base_url}/window/size"
            r = self.http.get(url, timeout=3)
            res = r.json().get("value", {})
            w = int(res.get("width", 390))
            h = int(res.get("height", 844))
            self._window_size = (w, h)
            return self._window_size
        except Exception:
            return (390, 844)

    def screenshot(self) -> Image.Image:
        """Capture screenshot and return a PIL Image object."""
        r = self.http.get(f"{self.base_url}/screenshot", timeout=5)
        res = r.json()
        b64_data = res.get("value", "")
        img_bytes = base64.b64decode(b64_data)
        return Image.open(io.BytesIO(img_bytes))

    def tap(self, x: int, y: int):
        """Tap at screen coordinates (x, y) with minimal latency."""
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
                        {"type": "pause", "duration": 15},
                        {"type": "pointerUp", "button": 0}
                    ]
                }
            ]
        }
        r = self.http.post(url, json=payload, timeout=4)
        return r.status_code == 200

    def swipe(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.2):
        """Perform a fast swipe gesture from (from_x, from_y) to (to_x, to_y)."""
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
                        {"type": "pause", "duration": 10},
                        {"type": "pointerMove", "duration": duration_ms, "x": int(to_x), "y": int(to_y)},
                        {"type": "pointerUp", "button": 0}
                    ]
                }
            ]
        }
        r = self.http.post(url, json=payload, timeout=5)
        return r.status_code == 200

    def type_text(self, text: str):
        """Type text into currently focused input element."""
        session_id = self.get_session()
        url = f"{self.base_url}/session/{session_id}/wda/keys"
        payload = {"value": list(text)}
        r = self.http.post(url, json=payload, timeout=5)
        return r.status_code == 200

    def press_home(self):
        """Press the home button / navigate to SpringBoard."""
        url = f"{self.base_url}/wda/homescreen"
        r = self.http.post(url, timeout=3)
        return r.status_code == 200

    def activate_app(self, bundle_id: str):
        """Activate an app by bundleId directly."""
        session_id = self.get_session()
        url = f"{self.base_url}/session/{session_id}/wda/apps/activate"
        r = self.http.post(url, json={"bundleId": bundle_id}, timeout=5)
        return r.status_code == 200

    def launch_app(self, bundle_id: str):
        """Launch or create a session with the given bundleId."""
        r = self.http.post(
            f"{self.base_url}/session",
            json={"capabilities": {"bundleId": bundle_id}},
            timeout=8
        )
        data = r.json()
        self.session_id = data.get("sessionId") or data.get("value", {}).get("sessionId")
        return bool(self.session_id)

    def find_elements_by_label(self, label: str):
        """Fast predicate search for elements matching label."""
        session_id = self.get_session()
        url = f"{self.base_url}/session/{session_id}/elements"
        payload = {"using": "predicate string", "value": f'label CONTAINS "{label}"'}
        try:
            r = self.http.post(url, json=payload, timeout=3)
            return r.json().get("value", [])
        except Exception:
            return []

    def tap_element(self, element_id: str):
        """Directly click an element by its ID."""
        session_id = self.get_session()
        url = f"{self.base_url}/session/{session_id}/element/{element_id}/click"
        try:
            r = self.http.post(url, timeout=3)
            return r.status_code == 200
        except Exception:
            return False
