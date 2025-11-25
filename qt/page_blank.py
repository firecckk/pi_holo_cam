from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer
import threading

import camera
from . import ai_client


class BlankPage(QLabel):
    def __init__(self):
        super().__init__(alignment=Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #000000; color: #ECF0F1; font-size: 18px;")
        self.setWordWrap(True)
        self.busy = False
        self.setText("Blank Page\n\nPress Enter to capture and analyze the camera frame.")

    def capture_and_analyze(self):
        if self.busy:
            return
        self.busy = True
        self.setText("Capturing frame...\nPlease wait.")

        def _worker():
            try:
                frame_rgb = camera.get_camera().capture_Image()
                desc = ai_client.analyze_frame(frame_rgb)
                QTimer.singleShot(0, lambda: self._apply_result(desc))
            except Exception as e:
                QTimer.singleShot(0, lambda: self._apply_result(f"Error: {e}"))

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_result(self, text: str):
        self.setText(text)
        self.busy = False