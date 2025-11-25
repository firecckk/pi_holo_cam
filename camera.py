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
        import cv2
        
        class Camera:

            def __init__(self):
                self.camera = Picamera2()
                config = self.camera.create_video_configuration(main={"size": (width, height)})
                self.camera.configure(config)
                self.camera.start()

            def capture_Image(self):
                frame = self.camera.capture_array()  # 获取numpy数组 (RGB)
                # 使用OpenCV转换色彩空间并确保内存连续
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.UMat(frame_rgb).get()  # 确保内存连续
                return frame_rgb
        __camera = Camera()
    else:
        class MockCamera:
            def __init__(self, width=480, height=320):
                self.width = width
                self.height = height
                # 生成一个固定的随机数组（作为"固定"的模拟图像）
                numpy.random.seed(42)
                self.mock_frame = numpy.random.randint(0, 256, (height, width, 3), dtype=numpy.uint8)

            def capture_Image(self):
                """返回固定的随机RGB数组"""
                return self.mock_frame.copy()
        __camera = MockCamera()
    __camera_inited = True