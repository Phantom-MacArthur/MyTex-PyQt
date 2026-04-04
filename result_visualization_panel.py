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
        content_font = QFont("SimSun", 9)  # 使用与LaTeX文本框相同的小字号
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # 识别结果区域
        result_vis_group = QGroupBox("LaTeX公式")  # 修改标题为"LaTeX公式"
        result_vis_group.setFont(title_font)
        result_vis_layout = QVBoxLayout()
        result_vis_layout.setContentsMargins(5, 5, 5, 5)
        
        # 使用 QLabel 显示结果（靠左上角对齐）
        self.result_label = QLabel("")
        self.result_label.setFont(content_font)  # 小字号9pt
        self.result_label.setStyleSheet("background-color: white; color: black; padding: 10px;")
        self.result_label.setWordWrap(True)  # 自动换行
        self.result_label.setMinimumHeight(100)
        # 靠左上角对齐（不是居中）
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        # 设置尺寸策略，允许垂直扩展以适应内容，但不会产生滚动条
        self.result_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        result_vis_layout.addWidget(self.result_label)
        
        result_vis_group.setLayout(result_vis_layout)
        layout.addWidget(result_vis_group)
        
    def display_result_visualization(self, latex_formula):
        """显示识别结果"""
        
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
            self.result_label.setText(display_text)
        else:
            # 纯数学公式模式（显示原始 LaTeX）
            self.result_label.setText(latex_formula)
