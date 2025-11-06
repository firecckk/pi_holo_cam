#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raspberry Pi 实时视频输出到 framebuffer (/dev/fb0)
使用 mmap 提高性能，支持文字叠加。
分辨率自动匹配 fbset (默认 800x480, BGRA, 32bpp)

依赖:
    sudo apt install python3-picamera2 fbset
    pip install pillow numpy
运行:
    sudo python3 pi_video_fb.py
"""

import os
import time
import mmap
import signal
import atexit
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2


# -----------------------------
# Disable TTY
# -----------------------------
def disable_fb_console():
    os.system("echo 0 | sudo tee /sys/class/vtconsole/vtcon1/bind > /dev/null 2>&1")

def enable_fb_console():
    os.system("echo 1 | sudo tee /sys/class/vtconsole/vtcon1/bind > /dev/null 2>&1")

# 注册退出恢复函数
atexit.register(enable_fb_console)
signal.signal(signal.SIGINT, lambda s, f: exit(0))

# 程序开始时禁用终端
disable_fb_console()

# -----------------------------
# framebuffer 检测函数
# -----------------------------
def get_fb_info():
    """使用 fbset -s 获取 framebuffer 分辨率和位深"""
    out = subprocess.check_output(["fbset", "-s"], text=True)
    for line in out.splitlines():
        if "geometry" in line:
            parts = line.split()
            w, h, _, _, bpp = parts[1:6]
            return int(w), int(h), int(bpp)
    raise RuntimeError("无法解析 framebuffer 几何信息")


# -----------------------------
# 图像转换函数
# -----------------------------
def pil_to_fb_bytes(img: Image.Image, width: int, height: int, bpp: int) -> bytes:
    """把 PIL 图像转换为 framebuffer 的原始像素字节流"""
    img = img.resize((width, height), Image.LANCZOS)

    if bpp == 32:
        # framebuffer 是 BGRA 排列
        return img.convert("RGBA").tobytes("raw", "BGRA")
    elif bpp == 16:
        # RGB565 模式（少见，但支持）
        arr = np.array(img.convert("RGB"), dtype=np.uint8)
        r = (arr[..., 0] >> 3).astype(np.uint16)
        g = (arr[..., 1] >> 2).astype(np.uint16)
        b = (arr[..., 2] >> 3).astype(np.uint16)
        rgb565 = (r << 11) | (g << 5) | b
        return rgb565.tobytes()
    else:
        raise ValueError(f"Unsupported framebuffer bpp: {bpp}")


# -----------------------------
# 主程序
# -----------------------------
def main():
    print("启动视频流显示...")
    fb_width, fb_height, fb_bpp = get_fb_info()
    print(f"Framebuffer: {fb_width}x{fb_height} @ {fb_bpp} bpp")

    # 初始化相机
    picam = Picamera2()
    config = picam.create_video_configuration(main={"size": (fb_width, fb_height)})
    picam.configure(config)
    picam.start()
    time.sleep(0.5)

    # 尝试加载字体
    try:
        FONT = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
        )
    except Exception:
        FONT = ImageFont.load_default()

    # 打开 framebuffer 并 mmap
    fb_path = "/dev/fb0"
    fb_size = fb_width * fb_height * (fb_bpp // 8)
    fb_fd = os.open(fb_path, os.O_RDWR)
    fb_map = mmap.mmap(fb_fd, fb_size, mmap.MAP_SHARED, mmap.PROT_WRITE)

    # 主循环
    frame_interval = 1 / 30  # 目标 30 FPS
    frames = 0
    t0 = time.time()
    print("开始视频输出 (Ctrl+C 退出)...")

    try:
        while True:
            # 采集帧
            frame = picam.capture_array()
            img = Image.fromarray(frame).convert("RGBA")

            # 叠加时间戳
            draw = ImageDraw.Draw(img)
            ts = time.strftime("%H:%M:%S")
            draw.text((10, 10), ts, font=FONT, fill=(255, 255, 255, 255))

            # 转换为 framebuffer 格式
            raw = pil_to_fb_bytes(img, fb_width, fb_height, fb_bpp)

            # 写入 framebuffer（使用 mmap）
            fb_map.seek(0)
            fb_map.write(raw)
            fb_map.flush()

            # 计算帧率
            frames += 1
            now = time.time()
            if now - t0 >= 1:
                print(f"{frames} FPS")
                frames = 0
                t0 = now

            time.sleep(frame_interval)
    except KeyboardInterrupt:
        print("\n退出视频流显示。")
    finally:
        fb_map.close()
        os.close(fb_fd)
        picam.stop()


if __name__ == "__main__":
    main()

