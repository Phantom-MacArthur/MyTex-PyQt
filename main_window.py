from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt

from image_display_panel import ImageDisplayPanel
from api_and_recognition_panel import APIAndRecognitionPanel


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置主窗口布局"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # 左、上、右、下边距都为10px
        main_layout.setSpacing(10)
        self.setLayout(main_layout)
        
        # 创建左右面板
        self.left_panel = APIAndRecognitionPanel()  # 左侧：API配置面板（控制区）
        self.right_panel = ImageDisplayPanel()      # 右侧：图片显示面板（展示区）
        
        # 固定左侧宽度为300px（API配置区域）
        left_width = 300
        self.left_panel.setFixedWidth(left_width)
        
        # 计算右侧最小宽度：总宽600 - 左侧300 - 左右边距20 - 中间间距10 = 270px
        right_min_width = 270
        self.right_panel.setMinimumWidth(right_min_width)
        
        # 设置尺寸策略 - 左侧固定宽度，右侧占满剩余空间；高度由左侧主导
        left_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        right_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        
        self.left_panel.setSizePolicy(left_policy)
        self.right_panel.setSizePolicy(right_policy)
        
        # 添加左侧面板（API配置区域）
        main_layout.addWidget(self.left_panel)
        
        # 添加右侧面板（图片显示区域）
        main_layout.addWidget(self.right_panel)
        
        # 设置拉伸因子：左侧不扩展（固定宽度），右侧可扩展
        main_layout.setStretch(0, 0)  # 左侧拉伸因子为0（不拉伸）
        main_layout.setStretch(1, 1)  # 右侧拉伸因子为1
        
        # 主窗口尺寸策略 - 水平可扩展，垂直由内容决定
        main_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setSizePolicy(main_policy)
        
        # 设置主窗口最小高度为500
        self.setMinimumHeight(500)
