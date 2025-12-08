import pyaudio
import time
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
        
        # 记录流式响应开始的时间
        start_time_total = time.time()
        
        chunk_count = 0 # 记录数据块编号
        
        for chunk in response.iter_bytes():
            
            chunk_count += 1
            # 记录接收数据块之前的时间
            start_time_chunk = time.time()
            
            buffer.extend(chunk)

            # 如果 buffer 太小，不播放（防止不完整 PCM 帧）
            if len(buffer) < 512:    # 约 10ms 音频
                # 计算并打印接收此块数据所花费的时间
                time_elapsed_chunk = time.time() - start_time_chunk
                print(f"Chunk {chunk_count}: Received {len(chunk)} bytes in {time_elapsed_chunk:.4f} seconds (Buffer too small to play)")
                continue

            # 保证 16-bit 对齐（偶数字节）
            playable_size = len(buffer) - (len(buffer) % 2)
            if playable_size > 0:
                # 记录写入音频流之前的时间
                start_time_write = time.time()
                
                stream.write(bytes(buffer[:playable_size]))
                
                # 计算并打印接收和写入此块数据所花费的总时间
                time_elapsed_chunk_total = time.time() - start_time_chunk
                time_elapsed_write = time.time() - start_time_write
                
                print(f"Chunk {chunk_count}: Received {len(chunk)} bytes, Wrote {playable_size} bytes. Total time: {time_elapsed_chunk_total:.4f}s (Write time: {time_elapsed_write:.4f}s)")
                
                del buffer[:playable_size]
        
        # 记录接收所有数据的时间
        end_time_receive = time.time()
        print("-" * 30)
        print(f"Total chunks received: {chunk_count}")
        print(f"Total reception time: {end_time_receive - start_time_total:.4f} seconds")


        # 播放剩余数据
        if len(buffer) > 0:
            stream.write(bytes(buffer))
            print(f"Played remaining {len(buffer)} bytes.")

        stream.stop_stream()
        stream.close()
        pa.terminate()
        
        # 记录音频播放结束后的时间
        end_time_total = time.time()
        print(f"Total function execution time (including cleanup): {end_time_total - start_time_total:.4f} seconds")

stream_tts_and_play("You are HoloCap vision assistance AI. The image provided is exactly what the user is seeing. Analyze the image and return a JSON object with two keys")