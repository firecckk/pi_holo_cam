import signal
import qt.gui as gui
import qt.InputListener as InputListener
import KeyEvent.tcp_button as tcp_button

signal.signal(signal.SIGINT, lambda s, f: exit(0))

# -----------------------------
# Config Camera
# -----------------------------
import camera
camera.init_camera(False)

if __name__ == "__main__":
    input_listener = InputListener.InputListener()
    tcp_button.thread_run(input_listener)
    gui.run(input_listener, DEBUG_MODE=True) # set DEBUG_MODE=True for not flipping