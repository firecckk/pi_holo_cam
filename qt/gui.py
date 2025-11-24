import sys
import os
from PyQt6.QtCore import (Qt, QPropertyAnimation, QRect, QEasingCurve, QSize)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QListWidget, QListWidgetItem, QStackedWidget, 
                             QLabel)
from PyQt6.QtGui import QIcon, QKeyEvent, QCursor

# ----------------- 动画 Stacked Widget 类 (保持不变) -----------------

class AnimatedStackedWidget(QStackedWidget):
    """
    重写 QStackedWidget，实现垂直平移动画 (Vertical Slide Animation)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_duration = 300 # 动画时长 300ms
        self.current_index = 0
        self.is_animating = False

    def setCurrentIndex(self, index):
        if self.is_animating or index == self.current_index:
            return

        old_index = self.current_index
        
        # 确定滑动方向：
        # 如果新索引 > 旧索引 (按下键)，则新页面从下方滑入 (direction = 1)
        # 如果新索引 < 旧索引 (按上键)，则新页面从上方滑入 (direction = -1)
        direction = -1 if index > old_index else 1 

        old_widget = self.widget(old_index)
        new_widget = self.widget(index)

        # 1. 禁用输入
        self.is_animating = True
        
        # 2. 将新窗口放置在屏幕外侧 (垂直偏移)
        # 注意：此处使用 self.height() 进行垂直偏移
        offset_y = self.height() * direction * -1 
        new_widget.setGeometry(self.rect().translated(0, offset_y)) # x=0, y=offset_y
        
        # 3. 显示新窗口并将其置于顶部
        new_widget.show()
        new_widget.raise_()

        # --- 设置动画 ---
        
        # 旧窗口动画：向相反方向垂直移出
        self.anim_old = QPropertyAnimation(old_widget, b"geometry")
        self.anim_old.setDuration(self.animation_duration)
        self.anim_old.setStartValue(old_widget.geometry())
        # 移出屏幕 (y 坐标变化)
        self.anim_old.setEndValue(old_widget.geometry().translated(0, self.height() * direction))
        self.anim_old.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 新窗口动画：从屏幕外垂直移入
        self.anim_new = QPropertyAnimation(new_widget, b"geometry")
        self.anim_new.setDuration(self.animation_duration)
        self.anim_new.setStartValue(new_widget.geometry())
        self.anim_new.setEndValue(self.rect()) # 移到正常位置 (0, 0)
        self.anim_new.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 动画完成后的处理
        self.anim_new.finished.connect(lambda: self._animation_finished(old_widget, index))

        # 4. 开始并行播放动画
        self.anim_old.start()
        self.anim_new.start()
        
        self.current_index = index


    def _animation_finished(self, old_widget, final_index):
        # 动画完成后，将旧窗口隐藏并确保位置复位
        self.is_animating = False
        old_widget.hide()
        super().setCurrentIndex(final_index)
        old_widget.setGeometry(self.rect())

# ----------------- 主应用窗口类 (路径处理、美化和按键切换) -----------------

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raspberry Pi Embedded UI (PyQt6/Qt6)")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 图标路径处理
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ICON_PATH = os.path.join(base_dir, "resources", "icons")

        # --- 左侧菜单 (QListWidget) ---
        self.menu_list = QListWidget()
        self.menu_list.setMaximumWidth(115) 
        self.menu_list.setMinimumWidth(115)
        
        self.menu_list.setStyleSheet("""
        QListWidget {
            background-color: #0C1E30;
            color: #ECF0F1;
            border: none;
            font-size: 10px;
            padding: 0px;
            outline: none;
        }
        QListWidget::item {
            min-height: 100px;
            height: 100px;
            padding: 2px 2px 2px 2px;
        }
        QListWidget::item:selected {
            background-color: #45606F;
            color: #FFFFFF;
            border-left: 5px solid #E67E22;
        }
        """)
    
        # 单独设置图标尺寸（不要在样式表中设置）
        self.menu_list.setIconSize(QSize(96, 96))

        items_data = [
            ("Map", "map.png"), 
            ("状态", "ai.png"),
            ("维护", "set.png")
            #("关于", "about.png")
        ]
        
        for name, icon_file in items_data:
            item = QListWidgetItem(name)
            item.setText("")
            
            full_icon_path = os.path.join(self.ICON_PATH, icon_file)
            
            if os.path.exists(full_icon_path):
                icon = QIcon(full_icon_path)
                item.setIcon(icon) 
            else:
                print(f"警告：找不到图标文件：{full_icon_path}")

            self.menu_list.addItem(item)

        # --- 右侧内容区 (AnimatedStackedWidget) ---
        self.stacked_widget = AnimatedStackedWidget()
        
        # 添加内容页面
        for i, (name, _) in enumerate(items_data):
            page = QLabel(f"这是 {name} 页面", alignment=Qt.AlignmentFlag.AlignCenter)
            page.setStyleSheet(f"background-color: {'#000000'}; color: #34495E; font-size: 24px;")
            self.stacked_widget.addWidget(page)
            
        # 关联菜单点击事件和页面切换
        self.menu_list.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        self.menu_list.setCurrentRow(0) 

        # --- 组合布局 ---
        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(self.stacked_widget)
        
        # 确保 QMainWindow 接收按键事件，而不是 QListWidget
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _handle_input_key(self, key_code):
        """将 GPIO/TCP 指令转换为 Qt 按键事件"""
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress, 
            key_code, 
            Qt.KeyboardModifier.NoModifier
        )
        self.keyPressEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """
        处理按键事件，用于菜单切换
        """
        current_row = self.menu_list.currentRow()
        total_rows = self.menu_list.count()
        new_row = current_row

        if event.key() == Qt.Key.Key_Up:
            # 向上切换，使用 % 实现循环 (0-1 = -1, -1 % 4 = 3)
            new_row = (current_row - 1) % total_rows
            
        elif event.key() == Qt.Key.Key_Down:
            # 向下切换，使用 % 实现循环
            new_row = (current_row + 1) % total_rows
            
        elif event.key() == Qt.Key.Key_Q:
            # 添加 Q 键作为退出应用的快捷键，方便调试
            QApplication.instance().quit()

        # 如果新的行索引有变化，则更新 QListWidget
        if new_row != current_row:
            # 设置新行，这会自动触发 currentRowChanged 信号，从而执行页面动画切换
            self.menu_list.setCurrentRow(new_row)
        
        # 调用父类的 keyPressEvent 以处理其他默认按键行为
        super().keyPressEvent(event)

def run(input_listener):
    app = QApplication(sys.argv)
    app.setOverrideCursor(QCursor(Qt.CursorShape.BlankCursor))
    window = MainApplication()
    input_listener.key_pressed.connect(window._handle_input_key)
    window.show()
    window.resize(480, 320)
    print("window: ", window.width(), " ", window.height())
    sys.exit(app.exec())

if __name__ == "__main__":
    run()