import io
import json
import base64
from PIL import Image
from pydantic import BaseModel, Field
from typing import Optional, Literal
import config

class ActionDecision(BaseModel):
    action: Literal["tap", "type", "swipe", "home", "wait", "finish"]
    x: Optional[int] = Field(None, description="Target X coordinate to tap in screen points")
    y: Optional[int] = Field(None, description="Target Y coordinate to tap in screen points")
    text: Optional[str] = Field(None, description="Text to type (for type action)")
    direction: Optional[Literal["up", "down", "left", "right"]] = Field(None, description="Swipe direction")
    seconds: Optional[int] = Field(1, description="Wait duration in seconds")
    reason: str = Field(..., description="Short explanation of why this action was chosen")
    result: Optional[str] = Field(None, description="Final outcome message when task is finished")

SYSTEM_PROMPT = """You are an autonomous AI agent operating an iPhone.
Inspect the provided screenshot, screen dimensions, and user objective to decide the NEXT single physical action.

Guidelines:
1. Accurately estimate target button or input field coordinates (X, Y).
2. Coordinates must be in screen points, not physical raw pixels.
3. To open an app, tap its home screen icon or trigger Spotlight search.
4. Always tap an input field before sending a 'type' action.
5. Once the objective is completed, return the 'finish' action.
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
User Goal: "{goal}"
Screen Dimensions: {width} x {height} points.
Action History:
{chr(10).join(f"- {h}" for h in history) if history else "- No actions performed yet."}

Examine the screenshot and return the single next atomic action as structured JSON.
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
            
            # Downscale and compress to JPEG for lightning-fast network transfer & vision token inference
            max_dim = 1024
            w, h = image.size
            if max(w, h) > max_dim:
                scale = max_dim / max(w, h)
                resized = image.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)
            else:
                resized = image

            buf = io.BytesIO()
            resized.convert("RGB").save(buf, format="JPEG", quality=75, optimize=True)
            img_bytes = buf.getvalue()
            
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
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
            print(f"[!] Gemini call error: {e}")
            raise e

    def _call_openai(self, image: Image.Image, prompt: str) -> ActionDecision:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Downscale and compress to JPEG for fast transfer
        max_dim = 1024
        w, h = image.size
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            resized = image.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)
        else:
            resized = image

        buf = io.BytesIO()
        resized.convert("RGB").save(buf, format="JPEG", quality=75, optimize=True)
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
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                        }
                    ]
                }
            ],
            response_format=ActionDecision,
            temperature=0.1
        )
        return response.choices[0].message.parsed
