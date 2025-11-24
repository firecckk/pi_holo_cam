from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os

class MapPage(QLabel):
    def __init__(self):
        super(MapPage, self).__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #000000;")
        # 获取图片路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, "resources", "icons", "uoft.png")
        if not os.path.exists(img_path):
            # 兼容直接从qt目录运行
            img_path = os.path.join(base_dir, "..", "qt", "resources", "icons", "uoft.png")
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(320, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(pixmap)
        else:
            self.setText("图片未找到: uoft.png")