from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import threading
import pygame

import camera
import ai_client


class AIPage(QLabel):
    # Signal to deliver analysis result back to UI thread
    result_ready = pyqtSignal(str)
    def __init__(self):
        super().__init__(alignment=Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #000000; color: #ECF0F1; font-size: 18px;")
        self.setWordWrap(True)
        self.busy = False
        self._timeout_timer = None
        # Connect signal to UI slot
        self.result_ready.connect(self._apply_result)
        self.setText("Blank Page\n\nPress Enter to capture and analyze the camera frame.")

        # Initialize pygame mixer for audio
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Warning: Could not initialize audio: {e}")

    def capture_and_analyze(self):
        if self.busy:
            return
        self.busy = True
        self.setText("Capturing frame...\nPlease wait.")
        
        # Start watchdog timeout
        if self._timeout_timer is None:
            self._timeout_timer = QTimer(self)
            self._timeout_timer.setSingleShot(True)
            self._timeout_timer.timeout.connect(lambda: self._apply_result("Error: analysis timed out"))
        self._timeout_timer.start(20000)  # 20s timeout

        def _worker():
            try:
                # Use fast path: no extra color conversions
                cam = camera.get_camera()
                frame_rgb = cam.capture_raw()
                desc = ai_client.analyze_frame(frame_rgb)

                # Generate and play audio
                if desc and not desc.startswith("Error"):
                    audio_path = ai_client.generate_speech(desc)
                    if audio_path:
                        try:
                            pygame.mixer.music.load(audio_path)
                            pygame.mixer.music.play()
                        except Exception as e:
                            print(f"Audio playback error: {e}")

                # Emit signal to update UI on the main thread
                self.result_ready.emit(desc)
            except Exception as e:
                # Emit error via signal
                self.result_ready.emit(f"Error: {e}")

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_result(self, text: str):
        # Stop timeout if still active
        if self._timeout_timer and self._timeout_timer.isActive():
            self._timeout_timer.stop()
        self.setText(text)
        self.busy = False