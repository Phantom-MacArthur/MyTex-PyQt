from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QDialog, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal
from api_config_panel import APIConfigPanel
from recognition_buttons_panel import RecognitionButtonsPanel
from latex_result_panel import LatexResultPanel
from screenshot_dialog import ScreenshotShortcutDialog
from api_config import APIService, APIConfigManager


class APIAndRecognitionPanel(QWidget):
    # 定义信号
    select_image_requested = pyqtSignal()
    take_screenshot_requested = pyqtSignal()
    retry_recognition_requested = pyqtSignal()
    screenshot_shortcut_changed = pyqtSignal(str)  # 添加这个信号
    compact_mode_toggled = pyqtSignal(bool)
    always_on_top_toggled = pyqtSignal(bool)  # 新增置顶切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_config_manager = APIConfigManager()
        self.current_screenshot_shortcut = "printscreen"  # 默认使用PrintScreen
        self.setup_ui()

    def setup_ui(self):
        """设置右侧面板布局 - 高度由内容主导"""
        policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setSizePolicy(policy)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 顶部对齐
        self.setLayout(right_layout)

        # 设置右侧固定宽度为300px
        self.setFixedWidth(300)

        # 统一字体大小 - 标题11pt，内容9pt
        title_font = QFont("SimSun", 11)
        content_font = QFont("SimSun", 9)

        # API配置面板
        self.config_panel = APIConfigPanel()
        right_layout.addWidget(self.config_panel)

        # 图片识别按钮面板
        self.buttons_panel = RecognitionButtonsPanel()
        right_layout.addWidget(self.buttons_panel)

        # LaTeX公式结果面板
        self.latex_panel = LatexResultPanel()
        right_layout.addWidget(self.latex_panel)

        # 连接信号
        self.buttons_panel.select_image_requested.connect(
            self.select_image_requested.emit
        )
        self.buttons_panel.take_screenshot_requested.connect(
            self.take_screenshot_requested.emit
        )
        self.buttons_panel.retry_recognition_requested.connect(
            self.retry_recognition_requested.emit
        )
        self.buttons_panel.compact_mode_toggled.connect(self.compact_mode_toggled.emit)
        self.buttons_panel.always_on_top_toggled.connect(
            self.always_on_top_toggled.emit
        )  # 连接新信号
        self.buttons_panel.screenshot_settings_requested.connect(
            self.show_screenshot_shortcut_dialog
        )  # 连接截图设置信号

        # 启动时显示使用说明
        self.latex_panel.show_startup_instructions()

    def set_app_config(self, app_id, app_secret):
        """设置App配置"""
        self.config_panel.set_app_config(app_id, app_secret)

    def get_app_id(self):
        """获取App ID"""
        return self.config_panel.get_app_id()

    def get_app_secret(self):
        """获取App Secret"""
        return self.config_panel.get_app_secret()

    def get_endpoint_choice(self):
        """获取API端口选择"""
        return self.config_panel.get_endpoint_choice()

    @property
    def compact_mode_btn(self):
        """提供对精简模式按钮的访问"""
        return self.buttons_panel.compact_mode_btn

    @property
    def config_group(self):
        """提供对API配置组的访问"""
        return self.config_panel

    @property
    def result_group(self):
        """提供对LaTeX结果组的访问"""
        return self.latex_panel

    def get_api_config_manager(self):
        """获取API配置管理器"""
        return self.api_config_manager

    def show_screenshot_shortcut_dialog(self):
        """显示截图快捷键设置对话框"""
        dialog = ScreenshotShortcutDialog(self, self.current_screenshot_shortcut)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_shortcut = dialog.get_selected_shortcut()
            self.current_screenshot_shortcut = new_shortcut
            self.screenshot_shortcut_changed.emit(new_shortcut)

    def update_record_count(self, success_count, fail_count):
        """更新识别记录"""
        self.buttons_panel.update_record_count(success_count, fail_count)

    def set_confidence(self, confidence):
        """设置置信度"""
        self.buttons_panel.set_confidence(confidence)

    def clear_result_text(self):
        """清空结果文本"""
        self.latex_panel.clear_result_text()

    def show_processing_message(self):
        """显示处理中消息"""
        self.latex_panel.show_processing_message()

    def show_config_prompt(self):
        """显示配置提示"""
        self.latex_panel.show_config_prompt()

    def show_error(self, error_msg, details=""):
        """显示错误信息"""
        self.latex_panel.show_error(error_msg, details)

    def show_success_result(self, result):
        """显示成功结果"""
        self.latex_panel.show_success_result(result)

    def get_current_screenshot_shortcut(self):
        """获取当前截图快捷键设置"""
        return self.current_screenshot_shortcut
