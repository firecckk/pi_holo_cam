from PyQt6.QtCore import (QObject, pyqtSignal)

class InputListener(QObject):
    cmd_event = pyqtSignal(int)
    key_pressed = pyqtSignal(int)
    speech_recognized = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def emit_cmd(self, cmd_code):
        self.cmd_event.emit(cmd_code)
    
    def emit_key(self, key_code):
        """发送按键事件"""
        self.key_pressed.emit(key_code)

    def emit_speech(self, recognized_text):
        """发送语音识别文本事件"""
        self.speech_recognized.emit(recognized_text)