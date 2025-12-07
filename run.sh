# 1. 设置平台为 EGLFS (您的加速驱动)
export QT_QPA_EGLFS_KMS=1
export QT_QPA_PLATFORM=eglfs

# 强制 Qt 隐藏光标
export QT_QPA_EGLFS_HIDECURSOR=1

# 3. 运行您的应用程序
export QT_QPA_EGLFS_KMS_CONFIG=./kms_config.json
export QT_QPA_EGLFS_ALWAYS_SET_MODE=1
#export QT_LOGGING_RULES="qt.qpa.*=true"
python3 rpi_main.py  -platform eglfs
