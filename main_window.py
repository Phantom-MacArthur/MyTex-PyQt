from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QSizePolicy
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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)
        
        # 创建左右面板
        self.left_panel = ImageDisplayPanel()
        self.right_panel = APIAndRecognitionPanel()
        
        # 固定右侧宽度，左侧设置相同宽度
        right_width = 300
        self.right_panel.setFixedWidth(right_width)
        self.left_panel.setFixedWidth(right_width)
        self.left_panel.setMinimumWidth(right_width)
        
        # 设置尺寸策略
        left_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        right_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        
        self.left_panel.setSizePolicy(left_policy)
        self.right_panel.setSizePolicy(right_policy)
        
        # 添加左侧面板
        main_layout.addWidget(self.left_panel)
        
        # 添加右侧面板
        main_layout.addWidget(self.right_panel)
        
        # 移除拉伸比例（因为右侧固定宽度）
        
        # 主窗口高度由内容决定
        main_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setSizePolicy(main_policy)