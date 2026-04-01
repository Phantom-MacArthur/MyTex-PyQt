from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from input_image_panel import InputImagePanel
from result_visualization_panel import ResultVisualizationPanel


class ImageDisplayPanel(QWidget):  # 改回QWidget，无外侧边框
    def __init__(self, parent=None):
        super().__init__(parent)  # 移除标题参数
        self.setup_ui()

    def setup_ui(self):
        """设置左侧面板 - 高度与右部完全一致"""
        # 设置尺寸策略 - 改为Preferred与右部一致
        policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setSizePolicy(policy)
        
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)  # 与右侧面板一致
        # 移除顶部对齐，让拉伸比例正常工作
        self.setLayout(left_layout)
        
        # 输入图片面板 - 保持QGroupBox边框
        self.input_panel = InputImagePanel()
        left_layout.addWidget(self.input_panel)
        
        # 识别结果可视化面板 - 保持QGroupBox边框  
        self.result_panel = ResultVisualizationPanel()
        left_layout.addWidget(self.result_panel)
        
        # 恢复拉伸比例：两个面板各占一半高度
        left_layout.setStretch(0, 1)
        left_layout.setStretch(1, 1)

    def display_original_image(self, image_path):
        """在上方区域显示原图"""
        self.input_panel.display_original_image(image_path)

    def display_result_visualization(self, latex_formula):
        """在下方区域显示识别结果"""
        self.result_panel.display_result_visualization(latex_formula)