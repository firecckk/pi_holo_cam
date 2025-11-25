# 1. 设置平台为 EGLFS (您的加速驱动)
export QT_QPA_PLATFORM="linuxfb:fb=/dev/fb0"
#export QT_QPA_PLATFORM=eglfs
#export QT_QPA_PLATFORM="eglfs:size=800x480"

# 强制 Qt 隐藏光标
export QT_QPA_EGLFS_HIDECURSOR=1

# 3. 运行您的应用程序
python3 rpi_main.py 
