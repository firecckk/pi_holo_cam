import numpy as np
import requests
import pyaudio
import threading
import openai
import queue
import time
import wave
import io
import re

from config import API_KEY

openai.api_key = API_KEY
TRANSCRIBE_URL = "https://api.openai.com/v1/audio/transcriptions"  # multipart POST

COMMAND_MAP = {
    "navigation": 1,
    "navigate": 1,
    "ai": 2,
    "video": 3,
    "hi" : 4
}

# 音频参数（PCM 16）
RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
FRAMES_PER_BUFFER = 1024
SEGMENT_SECONDS = 2.0  # 每个片段长度（秒） —— 可调，短一点延迟更低但请求频繁
RMS_THRESHOLD = 30

def calculate_rms(chunk_data):
    data = np.frombuffer(chunk_data, dtype=np.int16)
    return np.sqrt(np.maximum(0, np.mean(data**2)))

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

TRANSCRIBE_URL = "https://api.openai.com/v1/audio/transcriptions"  # multipart POST
def transcribe_audio_bytes(wav_bytes):
    """把 wav bytes 上传给 OpenAI transcription endpoint，返回文本"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {
        "file": ("clip.wav", wav_bytes, "audio/wav"),
    }
    data = {
        "model": "whisper-1", 
        "language": "en",  # english
    }
    resp = requests.post(TRANSCRIBE_URL, headers=headers, files=files, data=data, timeout=30)
    resp.raise_for_status()
    j = resp.json()
    return j.get("text", "")

class VoiceCommand:
    def _record_worker(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=FORMAT,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=FRAMES_PER_BUFFER)
        try:
            while True:
                frames = []
                frames_needed = int(RATE / FRAMES_PER_BUFFER * SEGMENT_SECONDS)
                rms_valid = False
                for _ in range(frames_needed):
                    data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                    rms = calculate_rms(data)
                    #print(rms)
                    if rms > RMS_THRESHOLD:
                        rms_valid = True
                    frames.append(data)
                if rms_valid:
                    # 把 PCM 片段合成 WAV bytes
                    wav_bytes = pcm_frames_to_wav_bytes(frames, RATE, CHANNELS)
                    self.audio_queue.put(wav_bytes)
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

    def _listener_worker(self):
        while True:
            wav_bytes = self.audio_queue.get()
            if wav_bytes is None:
                break
            #timestamp = time.strftime("%Y%m%d_%H%M%S")
            #filename = os.path.join("records", f"segment_{timestamp}_{start:.4f}.wav")
            #try:
            #    with open(filename, 'wb') as f:
            #        f.write(wav_bytes)
            #    print(f"[保存] 片段已保存至：{filename}")
            #except Exception as e:
            #    print(f"[保存错误] 无法保存片段：{e}")
            try:
                transcribed = transcribe_audio_bytes(wav_bytes)
                if not transcribed.strip():
                    print("Empty transcribe")
                    continue
                print(f"[transcribe] {transcribed}")
                self.input_listener.emit_speech(transcribed)
                text = transcribed.lower()
                cleaned_text = re.sub(r'[^a-z\s]', '', text)
                #print(f"[cleaned] {cleaned_text}")
                for keyword, command_code in COMMAND_MAP.items():
                    if keyword in cleaned_text:
                        self.input_listener.emit_cmd(command_code)
                        break

            except Exception as e:
                print("[错误]", e)
            finally:
                ...
    
    def __init__(self, input_listener):
        self.audio_queue = queue.Queue()
        self.input_listener = input_listener
        self.listening = False

    def start(self):
        self.recorder = threading.Thread(target=self._record_worker, daemon=True)
        self.listener = threading.Thread(target=self._listener_worker, daemon=True)
        self.recorder.start()
        self.listener.start()

    def stop(self):
        self.audio_queue.put(None)
        self.recorder.join(timeout=1)
        self.listener.join(timeout=1)