from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QGraphicsView, QGraphicsScene, QSizePolicy  # 添加QSizePolicy导入
)
from PyQt6.QtGui import QFont


class ResultVisualizationPanel(QWidget):  
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置识别结果可视化面板"""
        # 设置与API配置相同的字体
        title_font = QFont("SimSun", 11)  # 添加标题字体
        content_font = QFont("SimSun", 9)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # 识别结果区域 - 恢复QGroupBox边框
        result_vis_group = QGroupBox("识别结果")
        result_vis_group.setFont(title_font)
        result_vis_layout = QVBoxLayout()
        result_vis_layout.setContentsMargins(5, 5, 5, 5)
        
        self.result_vis_view = QGraphicsView()
        self.result_vis_scene = QGraphicsScene()
        self.result_vis_view.setScene(self.result_vis_scene)
        self.result_vis_view.setStyleSheet("background-color: white;")
        # 设置为Preferred策略，让内容决定高度，但设置最小高度避免为0
        self.result_vis_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.result_vis_view.setMinimumHeight(100)  # 设置最小高度
        result_vis_layout.addWidget(self.result_vis_view)
        
        # 确保将布局设置给QGroupBox
        result_vis_group.setLayout(result_vis_layout)
        
        layout.addWidget(result_vis_group)
        
    def display_result_visualization(self, latex_formula):
        """显示识别结果"""
        from PyQt6.QtGui import QFont
        from PyQt6.QtCore import Qt
        
        try:
            self.result_vis_scene.clear()
            
            # 直接添加文本到场景
            text_item = self.result_vis_scene.addText(latex_formula, QFont("SimSun", 11))
            
            # 自动适应视图大小
            self.result_vis_view.fitInView(self.result_vis_scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
        except Exception as e:
            self.result_vis_scene.clear()
            self.result_vis_scene.addText(f"显示失败: {str(e)}", QFont("SimSun", 11))