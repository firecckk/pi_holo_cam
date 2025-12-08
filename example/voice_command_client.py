"""
realtime_assistant.py
简易“实时”语音助手（录 2s -> 转写 -> 聊天 -> 本地 TTS 播放）
依赖: pyaudio, requests, openai, pyttsx3
"""

import os
import io
import time
import wave
import queue
import threading
import requests
import pyaudio
import openai
#import pyttsx3
from client import API_KEY

# 配置
OPENAI_API_KEY = API_KEY

openai.api_key = API_KEY
TRANSCRIBE_URL = "https://api.openai.com/v1/audio/transcriptions"  # multipart POST

# 音频参数（PCM 16）
RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
FRAMES_PER_BUFFER = 1024
SEGMENT_SECONDS = 2.0  # 每个片段长度（秒） —— 可调，短一点延迟更低但请求频繁

# 用队列把录音和处理解耦
audio_queue = queue.Queue()

# TTS 引擎（本地）
#tts = pyttsx3.init()
# 可选：调整语速/音量/声音
#tts.setProperty("rate", 160)

def record_worker():
    """从麦克风录音，按 SEGMENT_SECONDS 切片放到队列里"""
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=FRAMES_PER_BUFFER)
    print(f"[录音] 开始（每 {SEGMENT_SECONDS}s 切片）—— 按 Ctrl+C 停止")
    try:
        while True:
            frames = []
            frames_needed = int(RATE / FRAMES_PER_BUFFER * SEGMENT_SECONDS)
            for _ in range(frames_needed):
                data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                frames.append(data)
            # 把 PCM 片段合成 WAV bytes
            wav_bytes = pcm_frames_to_wav_bytes(frames, RATE, CHANNELS)
            audio_queue.put(wav_bytes)
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        print("[录音] 结束")

def pcm_frames_to_wav_bytes(frames, rate, channels):
    """把原始 PCM 帧转换成 WAV 格式的 bytes（内存）"""
    buf = io.BytesIO()
    wf = wave.open(buf, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()
    buf.seek(0)
    return buf.read()

def transcribe_audio_bytes(wav_bytes):
    """把 wav bytes 上传给 OpenAI transcription endpoint，返回文本"""
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {
        "file": ("clip.wav", wav_bytes, "audio/wav"),
    }
    data = {
        "model": "whisper-1",  # 使用 Whisper 模型做转写（可替换）
        # "language": "zh",  # 若想强制中文，可加 language 参数（按需）
    }
    resp = requests.post(TRANSCRIBE_URL, headers=headers, files=files, data=data, timeout=30)
    resp.raise_for_status()
    j = resp.json()
    # OpenAI transcription 返回通常包含 "text" 字段
    return j.get("text", "")

def chat_with_openai(system_prompt, user_text):
    """把用户文字交给 Chat API（这里用 ChatCompletion）并返回助手回复文本"""
    # 你可以改成 openai.ChatCompletion.create(...) 或者 openai.Chat.create(...) 取决于 SDK 版本
    # 下面用常见的 ChatCompletion 接口（注意不同 SDK 版本名可能略不同）
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # 可替换为你有权限的模型
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        max_tokens=300,
        temperature=0.6,
    )
    # 提取文本
    text = ""
    if "choices" in resp and len(resp.choices) > 0:
        text = resp.choices[0].message.get("content", "")
    return text.strip()

def speaker_worker():
    """从 audio_queue 读取音频片段，转写 -> 聊天 -> TTS"""
    system_prompt = "你是一个帮助用户的中文语音助手，回答简洁、礼貌。"
    while True:
        wav_bytes = audio_queue.get()
        if wav_bytes is None:
            break
        start = time.time()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        #filename = os.path.join("records", f"segment_{timestamp}_{start:.4f}.wav")
        #try:
        #    with open(filename, 'wb') as f:
        #        f.write(wav_bytes)
        #    print(f"[保存] 片段已保存至：{filename}")
        #except Exception as e:
        #    print(f"[保存错误] 无法保存片段：{e}")
        try:
            # 1) 转写
            transcribed = transcribe_audio_bytes(wav_bytes)
            if not transcribed.strip():
                print("[转写] 空，跳过")
                continue
            print(f"[转写] {transcribed}")

            # 2) 发送给 ChatGPT/LLM
            #reply = chat_with_openai(system_prompt, transcribed)
            reply = ""
            print(f"[助手] {reply}")

            # 3) TTS 播放（本地）
            #tts.say(reply)
            #tts.runAndWait()
        except Exception as e:
            print("[错误]", e)
        finally:
            elapsed = time.time() - start
            print(f"[片段处理耗时] {elapsed:.2f}s")

def main():
    recorder = threading.Thread(target=record_worker, daemon=True)
    speaker = threading.Thread(target=speaker_worker, daemon=True)
    recorder.start()
    speaker.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("退出中...")
        audio_queue.put(None)
        recorder.join(timeout=1)
        speaker.join(timeout=1)

if __name__ == "__main__":
    main()
