import os
import numpy

width = 320
height = 320

__camera = None
__camera_inited = False

def get_camera():
    global __camera, __camera_inited
    if not __camera_inited:
        print("Warning! camera accessed before inited")
        init_camera(False)
    return __camera

def init_camera(real = False):
    global __camera, __camera_inited
    if real:
        from picamera2 import Picamera2
        from libcamera import Transform
        import cv2
        import numpy as np
        
        class Camera:

            def __init__(self):
                self.camera = Picamera2()
                config = self.camera.create_video_configuration(
                        main={"size": (width, height)},
                        transform=Transform(hflip=True, vflip=True))
                self.camera.configure(config)
                self.camera.start()

            def capture_Image(self):
                frame = self.camera.capture_array()  # 获取numpy数组 (RGB)
                # 使用OpenCV转换色彩空间并确保内存连续
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.UMat(frame_rgb).get()  # 确保内存连续
                return frame_rgb

            def capture_raw(self):
                """快速获取原始RGB帧（不进行额外颜色空间转换）。"""
                frame = self.camera.capture_array()  # RGB
                if not frame.flags['C_CONTIGUOUS']:
                    frame = np.ascontiguousarray(frame)
                return frame
        __camera = Camera()
    else:
        from PIL import Image
        # Hardcoded mock image path
        mock_path = "./MockCam/test1.png"
        
        class MockCamera:
            def __init__(self, width=320, height=320):
                self.width = width
                self.height = height
                # Try to load hardcoded mock image, fallback to random
                if Image is not None and os.path.isfile(mock_path):
                    try:
                        img = Image.open(mock_path).convert("RGB")
                        img = img.resize((self.width, self.height))
                        self.mock_frame = numpy.array(img, dtype=numpy.uint8)
                        print(f"MockCamera: loaded mock image from {mock_path}")
                    except Exception as e:
                        print(f"MockCamera: failed to load, using random: {e}")
                        numpy.random.seed(42)
                        self.mock_frame = numpy.random.randint(0, 256, (height, width, 3), dtype=numpy.uint8)
                else:
                    # Fallback to random noise
                    numpy.random.seed(42)
                    self.mock_frame = numpy.random.randint(0, 256, (height, width, 3), dtype=numpy.uint8)

            def capture_Image(self):
                """返回固定的随机RGB数组"""
                return self.mock_frame.copy()

            def capture_raw(self):
                """返回固定的随机RGB数组（快速路径）。"""
                return self.mock_frame.copy()
        __camera = MockCamera()
    __camera_inited = True

def set_mock_image(path: str):
    """Set a file path to use as the mock camera image in PC simulation.

    - Call before first access to `get_camera()` or `init_camera(False)`.
    - Alternatively, set environment `CAMERA_MOCK_IMAGE`.
    """
    global __mock_image_path
    __mock_image_path = path
