import RPi.GPIO as GPIO
from PyQt6.QtCore import Qt

BUTTON_PINS = {
    16: Qt.Key.Key_Up,      # GPIO 16 -> 上键
    20: Qt.Key.Key_Down,    # GPIO 20 -> 下键
    21: Qt.Key.Key_Return   # GPIO 21 -> 确认键
}
PULLUP_PIN = 12

def gpio_button_init(input_listener):
    """初始化 GPIO 按钮，连接到 InputListener"""
    # init gpio
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(PULLUP_PIN, GPIO.OUT)
    GPIO.output(PULLUP_PIN, GPIO.HIGH)

    for pin, key_code in BUTTON_PINS.items():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
        
        # 创建回调函数，使用闭包捕获 key_code
        def button_callback(channel, kc=key_code, listener=input_listener):
            listener.emit_key(kc)
        
        GPIO.add_event_detect(pin, GPIO.FALLING, 
                         callback=button_callback, 
                         bouncetime=100)
        print(f"GPIO {pin} 已绑定到按键 {key_code}")
