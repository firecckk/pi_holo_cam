import os
import threading
import time
import mmap
import signal
import atexit
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2

import api
import render
import button

button_pressed = False 
async_task_lock = threading.Lock() 
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
msg = ""

def handle_frame(img):
    global button_pressed
    if(button_pressed):
        button_pressed = False
        save_img(img)
        if async_task_lock.acquire(blocking=False):
            threading.Thread(target=async_task, args=(), daemon=True).start()
    if render.scroller is not None:
        rendered_frame = render.scroller.render_frame(img)
    else:
        rendered_frame = img
    return rendered_frame 

def async_task():
    try:
        #msg = api.request()
        msg = "The CN Tower, standing at 553.33 meters (1,815 feet, 5 inches), is an iconic communications and observation tower in downtown Toronto, Canada. Completed in 1976, it was the world's tallest free-standing structure for over 30 years and remains the tallest in the Western Hemisphere"
        os.system(f"mpg321 audio.mp3") # play sound
        render.scroller = render.setup_scroller(msg, font_path)
    except Exception as e:
        print("thread error", e)
    finally:
        async_task_lock.release()

def save_img(img):
    #img = Image.fromarray(frame).convert("RGBA")
    img.save('frame.png')
    #img = Image.fromarray(frame).convert("RGB")
    #img.save('frame.jpg') # without A channel


def button_callback(channel):
    global button_pressed
    #button_pressed = True
    print("button pressed: ", channel)

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
    # init button
    button.gpio_button_init(button_callback)

    # init fb
    fb_width=800
    fb_height=480
    fb_bpp = 32
    
    fb_path = "/dev/fb0"
    fb_size = fb_width * fb_height * (fb_bpp // 8)
    fb_fd = os.open(fb_path, os.O_RDWR)
    fb_map = mmap.mmap(fb_fd, fb_size, mmap.MAP_SHARED, mmap.PROT_WRITE)

    # init cam
    camera_width = 1600
    camera_height = 960
    picam = Picamera2()
    config = picam.create_video_configuration(main={"size": (camera_width, camera_height)})
    picam.configure(config)
    picam.start()

    time.sleep(0.5)

    frames = 0
    t0 = time.time()

    try:
        while True:
            frame = picam.capture_array()

            img = Image.fromarray(frame).convert("RGBA")
            img = handle_frame(img)

            img = img.resize((800, 480), Image.LANCZOS)

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
