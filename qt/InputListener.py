from PyQt6.QtCore import (QObject, pyqtSignal)

class InputListener(QObject):
    key_pressed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def emit_key(self, key_code):
        """发送按键事件"""
        self.key_pressed.emit(key_code)