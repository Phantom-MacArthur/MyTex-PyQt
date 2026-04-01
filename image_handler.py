from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
import io


class ImageHandler:
    """PyQt6 图像处理类"""
    
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
    def display_original_image(self, image_path, left_panel):
        """在上方区域显示原图"""
        left_panel.display_original_image(image_path)
            
    def display_result_visualization(self, latex_formula, left_panel):
        """在下方区域显示识别结果"""
        left_panel.display_result_visualization(latex_formula)