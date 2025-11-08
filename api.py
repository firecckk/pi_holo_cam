from openai import OpenAI
from PIL import Image
import base64
import io

import config 

client = OpenAI(api_key=config.API_KEY)

def request():
    img = Image.open("frame.jpg").convert("RGB")
    img = img.resize((512, 512))

    # To base64
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    prompt = "描述一下这张图片的内容。"

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # 或者 "gpt-4.1"
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}"
                        }
                    }
                ]
            }
        ]
    )
    return(response.choices[0].message.content)


