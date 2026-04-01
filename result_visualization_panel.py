from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QSizePolicy
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import re


class ResultVisualizationPanel(QWidget):  
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置识别结果可视化面板"""
        title_font = QFont("SimSun", 11)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # 识别结果区域
        result_vis_group = QGroupBox("识别结果")
        result_vis_group.setFont(title_font)
        result_vis_layout = QVBoxLayout()
        result_vis_layout.setContentsMargins(5, 5, 5, 5)
        
        # 使用 QLabel 显示结果
        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Microsoft YaHei", 12))
        self.result_label.setStyleSheet("background-color: white; color: black; padding: 10px;")
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(100)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        result_vis_layout.addWidget(self.result_label)
        
        result_vis_group.setLayout(result_vis_layout)
        layout.addWidget(result_vis_group)
        
    def display_result_visualization(self, latex_formula):
        """显示识别结果"""
        print(f"DEBUG: display_result_visualization called with: {latex_formula}")
        
        # 检测是否包含中文字符或 \text{} 命令
        def needs_text_mode(text):
            if re.search(r'[\u4e00-\u9fff]', text) or re.search(r'\\text\{', text):
                return True
            return False
        
        # 提取 \text{} 中的纯文本内容
        def extract_text_content(text):
            patterns = [
                r'\\text\{([^}]*)\}',
                r'\\mathrm\{([^}]*)\}',
                r'\\mathit\{([^}]*)\}',
                r'\\mathbf\{([^}]*)\}'
            ]
            result = text
            for pattern in patterns:
                result = re.sub(pattern, r'\1', result)
            
            # 处理 LaTeX 换行命令 \\ -> 换行符
            result = result.replace(r'\\', '\n')
            
            # 移除其他常见的 LaTeX 命令（保留基本文本）
            # 移除 \begin{...} 和 \end{...}
            result = re.sub(r'\\begin\{[^}]*\}', '', result)
            result = re.sub(r'\\end\{[^}]*\}', '', result)
            
            return result
        
        if needs_text_mode(latex_formula):
            # 文本显示模式
            display_text = extract_text_content(latex_formula)
            print(f"DEBUG: Text mode - displaying: {repr(display_text)}")
            self.result_label.setText(display_text)
        else:
            # 纯数学公式模式（显示原始 LaTeX）
            print(f"DEBUG: Math mode - displaying: {repr(latex_formula)}")
            self.result_label.setText(latex_formula)
            
        print("DEBUG: Result label updated successfully")