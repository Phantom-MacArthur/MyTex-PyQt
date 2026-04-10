from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 尝试导入 latex2mathml 库用于 LaTeX 到 MathML 转换
try:
    import latex2mathml.converter
    LATEX2MATHML_AVAILABLE = True
except ImportError:
    LATEX2MATHML_AVAILABLE = False


class LatexResultPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("MathML公式", parent)  # 修改标题为"MathML公式"
        self.setup_ui()

    def setup_ui(self):
        """设置LaTeX公式结果面板"""
        title_font = QFont("SimSun", 11)
        content_font = QFont("SimSun", 9)
        self.setFont(title_font)

        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(10, 5, 10, 5)  # LaTeX文本框到父容器下边距为5
        result_layout.setSpacing(0)
        result_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(result_layout)

        # 设置LaTeX面板尺寸策略 - 允许垂直扩展
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.result_text = QTextEdit()
        self.result_text.setFont(content_font)
        self.result_text.setReadOnly(True)
        self.result_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        # 文本区域垂直策略设为Expanding，允许随窗口高度增加而扩展
        self.result_text.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        result_layout.addWidget(self.result_text)

    def clear_result_text(self):
        """清空结果文本"""
        self.result_text.clear()

    def show_processing_message(self):
        """显示处理中消息"""
        current_text = self.result_text.toPlainText()
        self.result_text.setPlainText(current_text + "正在识别公式，请稍候...\n")

    def show_config_prompt(self):
        """显示配置提示"""
        current_text = self.result_text.toPlainText()
        self.result_text.setPlainText(current_text + "请在右侧填写App ID和App Secret\n")

    def show_error(self, error_msg, details=""):
        """显示错误信息"""
        current_text = self.result_text.toPlainText()
        error_text = f"识别失败:\n{error_msg}\n"
        if details:
            error_text += f"详细信息:\n{details}\n"
        self.result_text.setPlainText(current_text + error_text)

    def show_success_result(self, result):
        """显示成功结果（不显示成功提示，只增加计数）"""
        current_text = self.result_text.toPlainText()
        if "res" in result and "latex" in result["res"]:
            latex_formula = result["res"]["latex"]
            
            # 默认转换为MathML格式显示
            if LATEX2MATHML_AVAILABLE:
                try:
                    mathml_formula = latex2mathml.converter.convert(latex_formula)
                    success_text = f"{mathml_formula}\n\n"
                except Exception as e:
                    # 如果转换失败，显示错误信息和原始LaTeX
                    success_text = f"⚠️ MathML转换失败: {str(e)}\n\n原始LaTeX公式:\n{latex_formula}\n\n"
            else:
                # 如果没有latex2mathml库，显示提示信息和LaTeX
                success_text = f"⚠️ 未安装latex2mathml库，无法转换为MathML\n\nLaTeX公式:\n{latex_formula}\n\n"
            self.result_text.setPlainText(current_text + success_text)
        else:
            import json

            formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
            result_text = f"完整结果:\n{formatted_result}\n"
            self.result_text.setPlainText(current_text + result_text)

    def update_record_count(self, success_count, fail_count):
        """更新识别记录"""
        self.record_label.setText(f"成功: {success_count}  失败: {fail_count}")

    def show_startup_instructions(self):
        """显示启动使用说明"""
        instructions = """💡 使用说明:
1. 前往 https://simpletex.cn/user/center 开通开放平台功能
2. 在应用列表中创建应用，获取App ID和App Secret  
3. 在软件界面中填入App ID和App Secret
4. 选择包含公式的截图图片(或截图粘贴)
5. 软件会自动识别并复制公式，无需手动操作
"""
        self.result_text.setPlainText(instructions)