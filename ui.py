from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QGraphicsView,
    QGraphicsScene,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QPainter, QFont, QColor
import os
from api_config import APIService, APIConfigManager


class ConfidenceBar(QWidget):
    """置信度显示控件 - 填色长方形内部显示百分比，靠左对齐，使用柔和颜色"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.confidence = 0.0
        self.setMinimumHeight(25)
        self.setMinimumWidth(150)

    def set_confidence(self, confidence):
        """设置置信度值 (0.0 - 1.0)"""
        self.confidence = max(0.0, min(1.0, confidence))
        self.update()  # 触发重绘

    def paintEvent(self, event):
        """绘制置信度条"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取控件尺寸
        width = self.width()
        height = self.height()

        # 绘制背景（浅灰色）
        painter.setBrush(QColor(245, 245, 245))  # 更浅的背景
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, width, height)

        # 绘制置信度填充（柔和的蓝色渐变，避免刺眼的绿色）
        fill_width = int(width * self.confidence)
        if fill_width > 0:
            # 使用柔和的蓝色系，低置信度偏浅蓝，高置信度偏深蓝
            base_blue = 200  # 基础蓝色值
            if self.confidence < 0.3:
                # 很低置信度：浅蓝色
                red = 230
                green = 240
                blue = 250
            elif self.confidence < 0.7:
                # 中等置信度：中等蓝色
                red = 180
                green = 210
                blue = 240
            else:
                # 高置信度：深蓝色
                red = 120
                green = 180
                blue = 230

            painter.setBrush(QColor(red, green, blue))
            painter.drawRect(0, 0, fill_width, height)

        # 绘制边框（更细的边框）
        painter.setPen(QColor(220, 220, 220))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(0, 0, width - 1, height - 1)

        # 绘制百分比文本（居中显示在填充区域内，如果填充区域足够宽）
        percentage_text = f"{self.confidence:.1%}"
        painter.setPen(QColor(60, 60, 60))  # 深灰色文字
        painter.setFont(QFont("SimSun", 11))

        if fill_width > 40:  # 如果填充区域足够宽，文字显示在填充区域内
            painter.drawText(
                0, 0, fill_width, height, Qt.AlignmentFlag.AlignCenter, percentage_text
            )
        else:  # 否则显示在整个控件内
            painter.drawText(
                0, 0, width, height, Qt.AlignmentFlag.AlignCenter, percentage_text
            )


class ScreenshotShortcutDialog(QDialog):
    """截图快捷键设置对话框"""

    def __init__(self, parent=None, current_shortcut="ctrl+c"):
        super().__init__(parent)
        self.setWindowTitle("设置截图快捷键")
        self.current_shortcut = current_shortcut
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        # 快捷键选择
        self.shortcut_combo = QComboBox()
        self.shortcut_combo.addItems(["PrintScreen", "Ctrl+C", "自定义"])
        if self.current_shortcut == "printscreen":
            self.shortcut_combo.setCurrentText("PrintScreen")
        elif self.current_shortcut == "ctrl+c":
            self.shortcut_combo.setCurrentText("Ctrl+C")
        else:
            self.shortcut_combo.setCurrentText("自定义")

        layout.addRow("快捷键方式:", self.shortcut_combo)

        # 自定义快捷键输入（仅在选择自定义时显示）
        self.custom_shortcut_input = QLineEdit()
        self.custom_shortcut_input.setPlaceholderText("例如：Ctrl+Shift+A")
        if self.current_shortcut not in ["printscreen", "ctrl+c"]:
            self.custom_shortcut_input.setText(self.current_shortcut)
        layout.addRow("自定义快捷键:", self.custom_shortcut_input)

        # 确定取消按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # 连接信号
        self.shortcut_combo.currentTextChanged.connect(self.on_shortcut_type_changed)
        self.on_shortcut_type_changed(self.shortcut_combo.currentText())

    def on_shortcut_type_changed(self, text):
        """快捷键类型变化时更新自定义输入框状态"""
        if text == "自定义":
            self.custom_shortcut_input.setEnabled(True)
        else:
            self.custom_shortcut_input.setEnabled(False)
            self.custom_shortcut_input.clear()

    def get_selected_shortcut(self):
        """获取选中的快捷键"""
        shortcut_type = self.shortcut_combo.currentText()
        if shortcut_type == "PrintScreen":
            return "printscreen"
        elif shortcut_type == "Ctrl+C":
            return "ctrl+c"
        else:
            custom_text = self.custom_shortcut_input.text().strip()
            return custom_text if custom_text else "printscreen"


class FormulaRecognizerUI(QWidget):
    # 定义信号
    select_image_requested = pyqtSignal()
    take_screenshot_requested = pyqtSignal()
    retry_recognition_requested = pyqtSignal()  # 新增重试信号
    screenshot_shortcut_changed = pyqtSignal(str)  # 截图快捷键变化信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_config_manager = APIConfigManager()
        self.current_screenshot_shortcut = "ctrl+c"
        self.setup_ui()

    def setup_ui(self):
        """设置 PyQt6 用户界面"""
        # 主窗口布局
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # 左侧：图片显示区域（分为上下两部分）
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # 上部：原图显示 - 高度减半（原来是250，现在是125）
        original_group = QGroupBox("输入图片")
        original_layout = QVBoxLayout()
        original_group.setLayout(original_layout)

        self.original_view = QGraphicsView()
        self.original_scene = QGraphicsScene()
        self.original_view.setScene(self.original_scene)
        self.original_view.setStyleSheet("background-color: white;")
        self.original_view.setMinimumHeight(125)  # 减半
        self.original_view.setMaximumHeight(125)  # 限制最大高度
        original_layout.addWidget(self.original_view)

        left_layout.addWidget(original_group)

        # 下部：识别结果可视化 - 高度减半（原来是250，现在是125）
        result_vis_group = QGroupBox("识别结果")
        result_vis_layout = QVBoxLayout()
        result_vis_group.setLayout(result_vis_layout)

        self.result_vis_view = QGraphicsView()
        self.result_vis_scene = QGraphicsScene()
        self.result_vis_view.setScene(self.result_vis_scene)
        self.result_vis_view.setStyleSheet("background-color: white;")
        self.result_vis_view.setMinimumHeight(125)  # 减半
        self.result_vis_view.setMaximumHeight(125)  # 限制最大高度
        result_vis_layout.addWidget(self.result_vis_view)

        left_layout.addWidget(result_vis_group)

        # 右侧：配置和结果区域
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # API配置区域
        config_group = QGroupBox("API配置")
        config_layout = QVBoxLayout()
        config_group.setLayout(config_layout)

        # API服务选择 - 修复灰色问题
        api_service_layout = QHBoxLayout()
        api_service_label = QLabel("API服务:")
        api_service_label.setFont(QFont("SimSun", 13))
        self.api_service_combo = QComboBox()
        self.api_service_combo.setFont(QFont("SimSun", 13))
        # 目前只支持 SimpleTex
        self.api_service_combo.addItem("SimpleTex", APIService.SIMPLETEX.value)
        # 不再禁用，保持可用状态
        api_service_layout.addWidget(api_service_label)
        api_service_layout.addWidget(self.api_service_combo)
        config_layout.addLayout(api_service_layout)

        # App ID - 长度加一倍
        app_id_layout = QHBoxLayout()
        app_id_label = QLabel("App ID:")
        app_id_label.setFont(QFont("SimSun", 13))
        self.app_id_entry = QLineEdit()
        self.app_id_entry.setFont(QFont("SimSun", 13))
        self.app_id_entry.setMinimumWidth(200)  # 增加宽度
        app_id_layout.addWidget(app_id_label)
        app_id_layout.addWidget(self.app_id_entry)
        config_layout.addLayout(app_id_layout)

        # App Secret - 长度加一倍，明文显示
        app_secret_layout = QHBoxLayout()
        app_secret_label = QLabel("App Secret:")
        app_secret_label.setFont(QFont("SimSun", 13))
        self.app_secret_entry = QLineEdit()
        self.app_secret_entry.setFont(QFont("SimSun", 13))
        self.app_secret_entry.setMinimumWidth(200)  # 增加宽度
        # 明文显示（不使用密码模式）
        self.app_secret_entry.setEchoMode(QLineEdit.EchoMode.Normal)
        app_secret_layout.addWidget(app_secret_label)
        app_secret_layout.addWidget(self.app_secret_entry)
        config_layout.addLayout(app_secret_layout)

        # API端口选择
        endpoint_layout = QHBoxLayout()
        endpoint_label = QLabel("API端口:")
        endpoint_label.setFont(QFont("SimSun", 13))
        endpoint_layout.addWidget(endpoint_label)

        self.endpoint_group = QButtonGroup()
        self.standard_radio = QRadioButton("标准版")
        self.turbo_radio = QRadioButton("轻量版")
        self.standard_radio.setFont(QFont("SimSun", 13))
        self.turbo_radio.setFont(QFont("SimSun", 13))
        self.standard_radio.setChecked(True)

        self.endpoint_group.addButton(self.standard_radio)
        self.endpoint_group.addButton(self.turbo_radio)

        endpoint_layout.addWidget(self.standard_radio)
        endpoint_layout.addWidget(self.turbo_radio)
        endpoint_layout.addStretch()
        config_layout.addLayout(endpoint_layout)

        right_layout.addWidget(config_group)

        # 按钮区域 - 重构为两行
        # 第一行：选择图片
        first_button_layout = QHBoxLayout()
        first_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.select_btn = QPushButton("选择图片")
        self.select_btn.setFont(QFont("SimSun", 13))
        self.select_btn.clicked.connect(self.select_image_requested.emit)
        first_button_layout.addWidget(self.select_btn)
        right_layout.addLayout(first_button_layout)

        # 第二行：截图识别 + 截图快捷键
        second_button_layout = QHBoxLayout()
        second_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.screenshot_btn = QPushButton("截图识别")
        self.screenshot_btn.setFont(QFont("SimSun", 13))
        self.screenshot_btn.clicked.connect(self.take_screenshot_requested.emit)
        second_button_layout.addWidget(self.screenshot_btn)

        self.shortcut_btn = QPushButton("截图快捷键")
        self.shortcut_btn.setFont(QFont("SimSun", 13))
        self.shortcut_btn.clicked.connect(self.show_screenshot_shortcut_dialog)
        second_button_layout.addWidget(self.shortcut_btn)
        right_layout.addLayout(second_button_layout)

        # 重试按钮（单独一行）
        retry_button_layout = QHBoxLayout()
        retry_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.retry_btn = QPushButton("再次识别")
        self.retry_btn.setFont(QFont("SimSun", 13))
        self.retry_btn.clicked.connect(self.retry_recognition_requested.emit)
        self.retry_btn.setEnabled(False)  # 初始禁用，有图片后再启用
        retry_button_layout.addWidget(self.retry_btn)
        right_layout.addLayout(retry_button_layout)

        # 结果显示区域
        result_group = QGroupBox("LaTeX 公式")
        result_layout = QVBoxLayout()
        result_group.setLayout(result_layout)

        self.result_text = QTextEdit()
        self.result_text.setFont(QFont("SimSun", 13))
        self.result_text.setReadOnly(True)
        self.result_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        result_layout.addWidget(self.result_text)

        # 置信度显示区域 - 靠左对齐
        confidence_layout = QHBoxLayout()
        confidence_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        confidence_label = QLabel("置信度:")
        confidence_label.setFont(QFont("SimSun", 13))
        self.confidence_bar = ConfidenceBar()
        confidence_layout.addWidget(confidence_label)
        confidence_layout.addWidget(self.confidence_bar)
        result_layout.addLayout(confidence_layout)

        right_layout.addWidget(result_group)

        # 添加到主布局
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        # 设置比例
        main_layout.setStretch(0, 1)  # 左侧可扩展
        main_layout.setStretch(1, 0)  # 右侧固定宽度

        # 启动时显示使用说明
        self.show_startup_instructions()

        # 连接配置变化信号
        self.app_id_entry.textChanged.connect(self._on_config_changed)
        self.app_secret_entry.textChanged.connect(self._on_config_changed)
        self.standard_radio.toggled.connect(self._on_endpoint_changed)
        self.turbo_radio.toggled.connect(self._on_endpoint_changed)

    def show_screenshot_shortcut_dialog(self):
        """显示截图快捷键设置对话框"""
        dialog = ScreenshotShortcutDialog(self, self.current_screenshot_shortcut)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_shortcut = dialog.get_selected_shortcut()
            self.current_screenshot_shortcut = new_shortcut
            self.screenshot_shortcut_changed.emit(new_shortcut)

    def _on_config_changed(self):
        """配置发生变化时更新配置管理器"""
        app_id = self.get_app_id()
        app_secret = self.get_app_secret()
        endpoint_choice = self.get_endpoint_choice()
        self.api_config_manager.set_simpletex_config(
            app_id, app_secret, endpoint_choice
        )

    def _on_endpoint_changed(self):
        """端点选择发生变化时更新配置管理器"""
        if self.sender().isChecked():
            self._on_config_changed()

    def enable_retry_button(self):
        """启用重试按钮"""
        self.retry_btn.setEnabled(True)

    def disable_retry_button(self):
        """禁用重试按钮"""
        self.retry_btn.setEnabled(False)

    def show_startup_instructions(self):
        """显示启动使用说明"""
        instructions = """💡 使用说明:
1. 前往 https://simpletex.cn/user/center 开通开放平台功能
2. 在应用列表中创建应用，获取App ID和App Secret  
3. 在软件界面中填入App ID和App Secret
4. 选择包含公式的截图图片
5. 软件会自动识别并自动复制LaTeX结果，无需手动操作
"""
        self.result_text.setPlainText(instructions)

    def set_app_config(self, app_id, app_secret):
        """设置App配置"""
        self.app_id_entry.setText(app_id)
        self.app_secret_entry.setText(app_secret)
        self._on_config_changed()

    def get_app_id(self):
        """获取App ID"""
        return self.app_id_entry.text().strip()

    def get_app_secret(self):
        """获取App Secret"""
        return self.app_secret_entry.text().strip()

    def get_endpoint_choice(self):
        """获取API端口选择"""
        if self.turbo_radio.isChecked():
            return "turbo"
        else:
            return "standard"

    def get_api_config_manager(self):
        """获取API配置管理器"""
        return self.api_config_manager

    def get_current_screenshot_shortcut(self):
        """获取当前截图快捷键"""
        return self.current_screenshot_shortcut

    def clear_result_text(self):
        """清空结果文本"""
        self.result_text.clear()
        self.confidence_bar.set_confidence(0.0)  # 重置置信度

    def show_processing_message(self):
        """显示处理中消息"""
        current_text = self.result_text.toPlainText()
        self.result_text.setPlainText(current_text + "正在识别公式，请稍候...\n")
        self.confidence_bar.set_confidence(0.0)  # 重置置信度

    def show_config_prompt(self):
        """显示配置提示"""
        current_text = self.result_text.toPlainText()
        self.result_text.setPlainText(current_text + "请在右侧填写App ID和App Secret\n")
        self.confidence_bar.set_confidence(0.0)  # 重置置信度

    def show_error(self, error_msg, details=""):
        """显示错误信息"""
        current_text = self.result_text.toPlainText()
        error_text = f"识别失败:\n{error_msg}\n"
        if details:
            error_text += f"详细信息:\n{details}\n"
        self.result_text.setPlainText(current_text + error_text)
        self.confidence_bar.set_confidence(0.0)  # 重置置信度

    def show_success_result(self, result):
        """显示成功结果"""
        current_text = self.result_text.toPlainText()
        if "res" in result and "latex" in result["res"]:
            latex_formula = result["res"]["latex"]
            confidence = result["res"].get("conf", 0)

            success_text = f"{latex_formula}\n\n"
            # 置信度由专门的控件显示，这里不再显示文本
            success_text += "\n✅ 已成功识别并自动复制"
            self.result_text.setPlainText(current_text + success_text)

            # 显示置信度
            self.confidence_bar.set_confidence(confidence)
        else:
            import json

            formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
            result_text = f"完整结果:\n{formatted_result}\n"
            self.result_text.setPlainText(current_text + result_text)
            self.confidence_bar.set_confidence(0.0)  # 重置置信度

    def display_original_image(self, image_path):
        """在上方区域显示原图"""
        try:
            self.original_scene.clear()
            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                self.original_scene.addText("图片加载失败", QFont("SimSun", 13))
                return

            # 获取视图大小
            view_width = self.original_view.width() - 20  # 减去边框
            view_height = self.original_view.height() - 20

            if view_width <= 0 or view_height <= 0:
                view_width = 400  # 加倍
                view_height = 250  # 加倍

            # 计算缩放比例
            ratio = min(view_width / pixmap.width(), view_height / pixmap.height())
            new_width = int(pixmap.width() * ratio)
            new_height = int(pixmap.height() * ratio)
            new_width = max(new_width, 1)
            new_height = max(new_height, 1)

            scaled_pixmap = pixmap.scaled(
                new_width,
                new_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            # 居中显示
            x = (view_width - new_width) // 2
            y = (view_height - new_height) // 2

            self.original_scene.setSceneRect(0, 0, view_width, view_height)
            self.original_scene.addPixmap(scaled_pixmap).setPos(x, y)

        except Exception as e:
            self.original_scene.clear()
            self.original_scene.addText(f"图片加载失败: {str(e)}", QFont("SimSun", 13))

    def display_result_visualization(self, latex_formula):
        """在下方区域显示识别结果"""
        try:
            self.result_vis_scene.clear()
            text_item = self.result_vis_scene.addText(
                latex_formula, QFont("SimSun", 13)
            )
            # 居中显示文本
            text_rect = text_item.boundingRect()
            scene_rect = self.result_vis_scene.sceneRect()
            text_item.setPos(
                (scene_rect.width() - text_rect.width()) / 2,
                (scene_rect.height() - text_rect.height()) / 2,
            )
        except Exception as e:
            self.result_vis_scene.clear()
            self.result_vis_scene.addText(f"显示失败: {str(e)}", QFont("SimSun", 13))
