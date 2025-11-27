import os
import base64
import io
import json
from typing import Optional
import time
from pathlib import Path
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


def analyze_frame(frame_rgb) -> dict:
    """Analyze a numpy RGB frame using OpenAI vision and return description text.

    - frame_rgb: numpy array in RGB shape (H, W, 3), dtype=uint8
    Returns a dict: {'ui_text': str, 'speech_text': str}
    """
    client = _get_client()
    # Convert numpy RGB to JPEG base64 (resize to 512x512 for cost/speed)
    img = Image.fromarray(frame_rgb).convert("RGB")
    img = img.resize((512, 512))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    system_prompt = (
        "You are HoloCap AI. Analyze the image and return a JSON object with two keys: "
        "'ui_text' (max 10 words, concise for HUD) and "
        "'speech_text' (natural, specific but simple, 1-2 sentences for audio)."
    )

    # Using chat.completions for vision per existing project style
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=150,
        )

        content = resp.choices[0].message.content
        print("Chat GPT responses: ", content)
        return json.loads(content)
    except Exception as e:
        print(f"AI Error: {e}")
        return {"ui_text": f"Error: {e}", "speech_text": ""}


def generate_speech(text_input, output_file="response.mp3"):
    """
    Converts text to speech using OpenAI's TTS API.
    """
    client = _get_client()
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text_input
        )
        
        # Save the audio to a file
        speech_file_path = Path(__file__).parent / output_file
        response.stream_to_file(speech_file_path)
        return str(speech_file_path)
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None
