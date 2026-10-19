import io
import json
import base64
from PIL import Image
from pydantic import BaseModel, Field
from typing import Optional, Literal
import config

class ActionDecision(BaseModel):
    action: Literal["tap", "type", "swipe", "home", "wait", "finish"]
    x: Optional[int] = Field(None, description="Tıklanacak X koordinatı (point)")
    y: Optional[int] = Field(None, description="Tıklanacak Y koordinatı (point)")
    text: Optional[str] = Field(None, description="Yazılacak metin (type aksiyonu için)")
    direction: Optional[Literal["up", "down", "left", "right"]] = Field(None, description="Kaydırma yönü")
    seconds: Optional[int] = Field(1, description="Bekleme süresi")
    reason: str = Field(..., description="Bu eylemi neden seçtiğinin kısa açıklaması")
    result: Optional[str] = Field(None, description="Görev bittiğinde kullanıcıya iletilecek sonuç")

SYSTEM_PROMPT = """Sen bir iPhone'u bizzat kullanan otonom bir AI ajansın.
Sana verilen ekran görüntüsünü, ekran çözünürlüğünü ve kullanıcının nihai hedefini inceleyerek BİR SONRAKİ tekil fiziksel adımı seç.

Kurallar:
1. Ekrandaki buton veya metinlerin koordinatlarını (X, Y) dikkatle hesapla.
2. Koordinatlar piksel değil, iOS ekran boyutu (points) cinsindendir.
3. Uygulama açmak için ana ekrandaki ikona tıkla veya Spotlight araması yap.
4. Yazı yazmadan önce arama kutusuna veya mesaj alanına tıkla ('tap'), ardından 'type' eylemini kullan.
5. Görev tamamlandığında 'finish' eylemini seç.
"""

class VisionBrain:
    def __init__(self):
        self.provider = config.AI_PROVIDER

    def decide_next_action(
        self,
        image: Image.Image,
        screen_size: tuple[int, int],
        goal: str,
        history: list[str]
    ) -> ActionDecision:
        width, height = screen_size
        user_prompt = f"""
Kullanıcı Hedefi: "{goal}"
Ekran Boyutu: {width} x {height} points.
Önceki Yapılan Eylemler:
{chr(10).join(f"- {h}" for h in history) if history else "- Henüz bir işlem yapılmadı."}

Ekrandaki görüntüyü incele ve şimdi atılması gereken TEK adımı JSON olarak üret.
"""
        if self.provider == "gemini":
            return self._call_gemini(image, user_prompt)
        else:
            return self._call_openai(image, user_prompt)

    def _call_gemini(self, image: Image.Image, prompt: str) -> ActionDecision:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=config.GEMINI_API_KEY)
            
            # Resmi buffer'a al
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            img_bytes = buf.getvalue()
            
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ActionDecision,
                    temperature=0.1
                )
            )
            return ActionDecision.model_validate_json(response.text)
        except Exception as e:
            # Fallback parsing
            print(f"[!] Gemini çağrı hatası: {e}")
            raise e

    def _call_openai(self, image: Image.Image, prompt: str) -> ActionDecision:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
        
        response = client.beta.chat.completions.parse(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64_img}"}
                        }
                    ]
                }
            ],
            response_format=ActionDecision,
            temperature=0.1
        )
        return response.choices[0].message.parsed
