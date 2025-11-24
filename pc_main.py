import signal
import qt.gui as gui
import qt.InputListener as InputListener
import KeyEvent.tcp_button as tcp_button

signal.signal(signal.SIGINT, lambda s, f: exit(0))

if __name__ == "__main__":
    input_listener = InputListener.InputListener()
    tcp_button.thread_run(input_listener)
    gui.run(input_listener)