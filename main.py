import os
import time
import mmap
import signal
import atexit
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2
import RPi.GPIO as GPIO

button_pressed = False

def handle_frame(frame):
    if(button_pressed):
        save_img()
    return frame

def save_img():
    img = Image.fromarray(frame).convert("RGBA")
    img.save('frame.png')
    #img.save('frame.jpg') # without A channel


def button_callback(channel):
    button_pressed = True


# -----------------------------
# Disable TTY
# -----------------------------
def disable_fb_console():
    os.system("echo 0 | sudo tee /sys/class/vtconsole/vtcon1/bind > /dev/null 2>&1")

def enable_fb_console():
    os.system("echo 1 | sudo tee /sys/class/vtconsole/vtcon1/bind > /dev/null 2>&1")

atexit.register(enable_fb_console)
signal.signal(signal.SIGINT, lambda s, f: exit(0))

disable_fb_console()


# -----------------------------
# Graphics
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
# MAIN
# -----------------------------

def main():
    # init gpio
    GPIO.setmode(GPIO.BCM)
    BUTTON_PIN = 29
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                         callback=button_callback, 
                         bouncetime=300)

    # init fb
    fb_width=800
    fb_height=480
    fb_bpp = 32
    
    fb_path = "/dev/fb0"
    fb_size = fb_width * fb_height * (fb_bpp // 8)
    fb_fd = os.open(fb_path, os.O_RDWR)
    fb_map = mmap.mmap(fb_fd, fb_size, mmap.MAP_SHARED, mmap.PROT_WRITE)

    # init cam
    picam = Picamera2()
    config = picam.create_video_configuration(main={"size": (fb_width, fb_height)})
    picam.configure(config)
    picam.start()

    time.sleep(0.5)

    frames = 0
    t0 = time.time()

    try:
        while True:
            frame = picam.capture_array()

            frame = handle_frame(frame)

            img = Image.fromarray(frame).convert("RGBA")
            raw = pil_to_fb_bytes(img, fb_width, fb_height, fb_bpp)

            fb_map.seek(0)
            fb_map.write(raw)
            fb_map.flush()

            frames += 1
            now = time.time()
            if now - t0 >= 1:
                print(f"{frames} FPS")
                frames = 0
                t0 = now

    except KeyboardInterrupt:
        print("\nexiting...")
    finally:
        fb_map.close()
        os.close(fb_fd)
        picam.stop()

if __name__ == "__main__":
    main()
