import pyaudio
from openai import OpenAI

from client import client

def stream_tts_and_play(text):
    # streaming TTS
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
        response_format="pcm",
    ) as response:

        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True,
        )

        # 缓冲区：避免首包不完整导致的杂音
        buffer = bytearray()

        for chunk in response.iter_bytes():

            buffer.extend(chunk)

            # 如果 buffer 太小，不播放（防止不完整 PCM 帧）
            if len(buffer) < 512:    # 约 10ms 音频
                continue

            # 保证 16-bit 对齐（偶数字节）
            playable_size = len(buffer) - (len(buffer) % 2)
            if playable_size > 0:
                stream.write(bytes(buffer[:playable_size]))
                del buffer[:playable_size]

        # 播放剩余数据
        if len(buffer) > 0:
            stream.write(bytes(buffer))

        stream.stop_stream()
        stream.close()
        pa.terminate()

stream_tts_and_play("You are HoloCap vision assistance AI. The image provided is exactly what the user is seeing. Analyze the image and return a JSON object with two keys")