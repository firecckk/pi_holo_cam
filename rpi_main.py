import os
import atexit
import signal
import qt.gui as gui
import qt.InputListener as InputListener
import KeyEvent.gpio_button as gpio_button
import KeyEvent.tcp_button as tcp_button

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
# Config Camera
# -----------------------------
import camera
camera.init_camera(real=True)

if __name__ == "__main__":
    input_listener = InputListener.InputListener()
    tcp_button.thread_run(input_listener)
    gpio_button.gpio_button_init(input_listener)
    gui.run(input_listener)