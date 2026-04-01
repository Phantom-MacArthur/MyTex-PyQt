from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QFont, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSizePolicy


class ConfidenceBar(QWidget):
    """置信度显示控件 - 填色长方形内部显示百分比，靠左对齐，使用柔和颜色"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.confidence = 0.0
        # 设置精确的25px高度
        self.setFixedHeight(25)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # 占满宽度
        
    def set_confidence(self, confidence):
        """设置置信度值 (0.0 - 1.0)"""
        self.confidence = max(0.0, min(1.0, confidence))
        self.update()  # 触发重绘
        
    def paintEvent(self, event):
        """绘制置信度条 - 使用圆角矩形，精细黑色描边，绿色填充，深灰色背景"""
        painter = QPainter(self)
        # 启用高质量渲染
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        # 获取控件尺寸
        width = self.width()
        height = self.height()
        radius = 4  # 圆角半径适配25px高度
        
        # 强制确保高度为25px
        if height != 25:
            height = 25
            
        # 绘制背景（深灰色）- 圆角矩形
        painter.setBrush(QColor(220, 220, 220))  # 更深的灰色背景
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, width, height, radius, radius)
        
        # 绘制置信度填充（绿色系）- 圆角矩形，占满整个宽度
        fill_width = int(width * self.confidence)
        if fill_width > 0:
            # 使用绿色系，低置信度偏浅绿，高置信度偏深绿
            if self.confidence < 0.3:
                # 很低置信度：浅绿色
                red = 230
                green = 250
                blue = 230
            elif self.confidence < 0.7:
                # 中等置信度：中等绿色
                red = 180
                green = 230
                blue = 180
            else:
                # 高置信度：深绿色
                red = 120
                green = 200
                blue = 120
            
            painter.setBrush(QColor(red, green, blue))
            painter.drawRoundedRect(0, 0, fill_width, height, radius, radius)
        else:
            # 当置信度为0时，显示白灰色背景（无填充）
            pass
        
        # 绘制精细黑色描边 - 使用1px宽度的圆角矩形边框
        pen = painter.pen()
        pen.setColor(QColor(0, 0, 0))
        pen.setWidth(1)  # 1px精细描边
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)  # 圆角连接
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(0, 0, width - 1, height - 1, radius, radius)  # 使用整数坐标
        
        # 绘制百分比文本 - 靠左对齐
        percentage_text = f"{self.confidence:.1%}"
        painter.setFont(QFont("SimSun", 9))
        
        # 始终靠左对齐显示百分比
        text_width = painter.fontMetrics().horizontalAdvance(percentage_text)
        text_x = 5  # 左边距5px
        text_y = (height + painter.fontMetrics().height()) // 2 - 2
        
        if fill_width > text_width + 10:  # 如果填充区域足够宽，文字显示在填充区域内（白色文字）
            painter.setPen(QColor(255, 255, 255))  # 白色文字
            painter.drawText(text_x, text_y, percentage_text)
        else:  # 否则显示在整个控件内（黑色文字）
            painter.setPen(QColor(0, 0, 0))  # 黑色文字
            painter.drawText(text_x, text_y, percentage_text)
