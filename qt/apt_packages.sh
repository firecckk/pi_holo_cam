# 1. 更新包列表
sudo apt update

# 2. 安装 PyQt6 Python 绑定
# 这个包会作为依赖项自动拉取大部分必要的 Qt 6 运行时库（如 libqt6widgets6, libqt6gui6 等）。
sudo apt install python3-pyqt6

# 3. （可选，但推荐）安装 Qt 6 核心库，确保 eglfs/platform 插件齐全
# 尤其是在嵌入式系统中，安装 qt6-base-dev 有助于确保所有依赖都被满足。
sudo apt install qt6-base-dev

# 4. （可选）如果你想使用 Qt Designer 或其他开发工具
# sudo apt install qt6-tools-dev
