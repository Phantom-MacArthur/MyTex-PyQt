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
        
        # 设置尺寸策略：左部Expanding（填充可用空间），右部主导高度
        left_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        right_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        self.left_panel.setSizePolicy(left_policy)
        self.right_panel.setSizePolicy(right_policy)
        
        # 添加左侧面板
        main_layout.addWidget(self.left_panel)
        
        # 添加右侧面板
        main_layout.addWidget(self.right_panel)
        
        # 设置拉伸比例
        main_layout.setStretch(0, 8)
        main_layout.setStretch(1, 10)
        
        # 主窗口高度由内容决定
        main_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setSizePolicy(main_policy)