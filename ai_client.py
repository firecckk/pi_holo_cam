import os
import base64
import io
from typing import Optional
import time
from PIL import Image

# OpenAI Python SDK
try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # Will be checked at runtime

# Prefer API key from config.py if present, else env var
API_KEY: Optional[str] = None
try:
    import config  # type: ignore
    API_KEY = getattr(config, "API_KEY", None)
except Exception:
    API_KEY = os.environ.get("OPENAI_API_KEY")

_client = None  # lazily initialized OpenAI client instance

def _get_client():
    global _client
    if _client is not None:
        print("_client is none")
        time.sleep(0.7)
        return _client
    if OpenAI is None:
        print("OpenAI package not available")
        time.sleep(0.7)
        raise RuntimeError("openai package not installed. Please `pip install openai`. ")
    if not API_KEY:
        print("API_KEY is missing")
        time.sleep(0.7)
        raise RuntimeError("Missing OpenAI API key. Set in config.API_KEY or env OPENAI_API_KEY.")
    # Add a network/request timeout to avoid indefinite hangs
    _client = OpenAI(api_key=API_KEY, timeout=10)
    return _client


def analyze_frame(frame_rgb) -> str:
    """Analyze a numpy RGB frame using OpenAI vision and return description text.

    - frame_rgb: numpy array in RGB shape (H, W, 3), dtype=uint8
    """
    client = _get_client()
    # Convert numpy RGB to JPEG base64 (resize to 512x512 for cost/speed)
    img = Image.fromarray(frame_rgb).convert("RGB")
    img = img.resize((512, 512))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    prompt = "Describe what I'm seeing right now."

    # Using chat.completions for vision per existing project style
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                ],
            }
        ],
    )

    response = resp.choices[0].message.content
    print("Chat GPT responses: ", response)
    return  response or "(No description returned)"
