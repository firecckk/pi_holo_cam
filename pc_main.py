import signal
import qt.gui as gui
import qt.InputListener as InputListener
import KeyEvent.tcp_button as tcp_button
from VoiceCommand import VoiceCommand


# -----------------------------
# Config Camera
# -----------------------------
import camera
camera.init_camera(use_real_cam=False)

voice_command_service = None

if __name__ == "__main__":
    input_listener = InputListener.InputListener()
    tcp_button.thread_run(input_listener)
    voice_command_service = VoiceCommand(input_listener)
    voice_command_service.start()
    gui.run(input_listener)

def my_exit(num):
    if voice_command_service:
        voice_command_service.stop()
    exit(num)

signal.signal(signal.SIGINT, lambda s, f: my_exit(0))