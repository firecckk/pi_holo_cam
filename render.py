from PIL import Image, ImageDraw, ImageFont
import textwrap

def wrap_text(text, font, max_width):
    """将长文本按最大宽度分割成多行[2,3](@ref)"""
    lines = []
    # 按字符分割以便更精确计算宽度
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append('')
            continue
            
        words = []
        for char in paragraph:
            words.append(char)
            test_line = ''.join(words)
            # 获取当前行宽度
            bbox = font.getbbox(test_line) if hasattr(font, 'getbbox') else font.getsize(test_line)
            line_width = bbox[2] - bbox[0] if hasattr(font, 'getbbox') else bbox[0]
            
            if line_width > max_width:
                if len(words) > 1:
                    lines.append(''.join(words[:-1]))
                    words = [words[-1]]
                else:
                    lines.append(''.join(words))
                    words = []
        
        if words:
            lines.append(''.join(words))
    
    return lines

class TextScroller:
    def __init__(self, background_image, text, font_path, font_size=30, 
                 text_color=(255, 255, 255), margin=50, scroll_speed=2):
        """
        初始化文本滚动器
        
        参数:
            background_image: 背景图片路径或PIL Image对象
            text: 要滚动的长文本
            font_path: 字体文件路径
            font_size: 字体大小
            text_color: 文字颜色
            margin: 边距
            scroll_speed: 滚动速度(像素/帧)
        """
        if isinstance(background_image, str):
            self.background = Image.open(background_image).convert('RGB')
        else:
            self.background = background_image.convert('RGB')
        
        self.text = text
        self.font = ImageFont.truetype(font_path, font_size)
        self.text_color = text_color
        self.margin = margin
        self.scroll_speed = scroll_speed
        
        # 计算可用的文本宽度
        self.max_width = self.background.width - 2 * margin
        
        # 文本换行处理
        self.lines = wrap_text(text, self.font, self.max_width)
        
        # 计算行高
        bbox = self.font.getbbox("Ay") if hasattr(self.font, 'getbbox') else self.font.getsize("Ay")
        self.line_height = bbox[3] - bbox[1] + 5 if hasattr(self.font, 'getbbox') else bbox[1] + 5
        
        # 计算总文本高度
        self.total_text_height = len(self.lines) * self.line_height
        
        # 初始化滚动位置（从屏幕底部开始）
        self.current_y = self.background.height
        
    def render_frame(self):
        """渲染当前帧"""
        # 创建背景副本
        frame = self.background.copy()
        draw = ImageDraw.Draw(frame)
        
        # 计算当前可见的行
        start_index = max(0, int((self.background.height - self.current_y) / self.line_height) - 1)
        end_index = min(len(self.lines), 
                       start_index + int(self.background.height / self.line_height) + 2)
        
        # 绘制可见行
        for i in range(start_index, end_index):
            if i < 0 or i >= len(self.lines):
                continue
                
            line = self.lines[i]
            if not line.strip():  # 跳过空行
                continue
                
            # 计算文本位置（水平居中）
            bbox = draw.textbbox((0, 0), line, font=self.font) if hasattr(draw, 'textbbox') else draw.textsize(line, font=self.font)
            text_width = bbox[2] - bbox[0] if hasattr(draw, 'textbbox') else bbox[0]
            x = (self.background.width - text_width) // 2
            
            # 垂直位置
            y = self.current_y + i * self.line_height
            
            # 只在可见区域内绘制
            if -self.line_height < y < self.background.height + self.line_height:
                # 添加文字阴影效果增强可读性
                shadow_color = (0, 0, 0)
                draw.text((x+1, y+1), line, font=self.font, fill=shadow_color)
                draw.text((x, y), line, font=self.font, fill=self.text_color)
        
        # 更新滚动位置
        self.current_y -= self.scroll_speed
        
        # 检查是否滚动完成，完成后重置位置
        if self.current_y + self.total_text_height < -self.background.height:
            self.current_y = self.background.height
        
        return frame

# 使用示例
def setup_scroller(background_path, text, font_path):
    """初始化滚动文本"""
    return TextScroller(
        background_image=background_path,
        text=text,
        font_path=font_path,
        font_size=24,
        text_color=(255, 255, 255),
        margin=40,
        scroll_speed=1
    )

# 全局滚动器实例
scroller = None

def handle_frame(frame):
    global scroller
    
    # 初始化滚动器（仅第一次调用时）
    if scroller is None:
        msg = "The CN Tower, standing at 553.33 meters (1,815 feet, 5 inches), is an iconic communications and observation tower in downtown Toronto, Canada. Completed in 1976, it was the world's tallest free-standing structure for over 30 years and remains the tallest in the Western Hemisphere"
        font_path = "arial.ttf"  # 替换为实际字体路径
        scroller = setup_scroller(frame, msg, font_path)
    
    # 渲染当前帧
    result_frame = scroller.render_frame()
    
    return result_frame
