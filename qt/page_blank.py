from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

class BlankPage(QLabel):
    def __init__(self):
        super().__init__(alignment=Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #000000; color: #34495E; font-size: 24px;")
        self.setText("这是 Blank 页面")