from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QGraphicsView, QGraphicsScene, QSizePolicy  # 添加QSizePolicy导入
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt  # 添加Qt导入


class InputImagePanel(QWidget):  
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置输入图片面板"""
        # 设置与API配置相同的字体
        title_font = QFont("SimSun", 11)  # 添加标题字体
        content_font = QFont("SimSun", 9)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # 输入图片区域 - 恢复QGroupBox边框
        original_group = QGroupBox("输入图片")
        original_group.setFont(title_font)
        original_layout = QVBoxLayout()
        original_layout.setContentsMargins(5, 5, 5, 5)
        
        self.original_view = QGraphicsView()
        self.original_scene = QGraphicsScene()
        self.original_view.setScene(self.original_scene)
        self.original_view.setStyleSheet("background-color: white;")
        # 禁用滚动条，只显示等比例缩放的图片
        self.original_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.original_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 设置为Expanding策略，让内容决定高度，但设置最小高度避免为0
        self.original_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.original_view.setMinimumHeight(100)  # 设置最小高度
        original_layout.addWidget(self.original_view)
        
        # 确保将布局设置给QGroupBox
        original_group.setLayout(original_layout)

        layout.addWidget(original_group)

    def display_original_image(self, image_path):
        """显示原图"""
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtCore import Qt

        try:
            self.original_scene.clear()
            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                self.original_scene.addText("图片加载失败", QFont("SimSun", 11))
                return

            # 直接添加图片到场景
            self.original_scene.addPixmap(pixmap)
            
            # 自动适应视图大小
            self.original_view.fitInView(self.original_scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

        except Exception as e:
            self.original_scene.clear()
            self.original_scene.addText(f"图片加载失败: {str(e)}", QFont("SimSun", 11))