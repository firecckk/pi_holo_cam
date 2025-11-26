from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage

import camera

class CameraPage(QLabel):
    def __init__(self):
        super().__init__(alignment=Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #000000;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 约30fps

    def update_frame(self):
        #h, w = frame_rgb.shape[:2]
        #bytes_per_line = 3 * w
        
        frame_rgb = camera.get_camera().capture_Image()
        img = QImage(frame_rgb.data, camera.width, camera.height, camera.height*3, QImage.Format.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(img).scaled(
            320, 320, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))