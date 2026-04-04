from PyQt6.QtWidgets import (
    QGroupBox, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QSizePolicy, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from confidence_bar import ConfidenceBar


class RecognitionButtonsPanel(QGroupBox):
    # 定义信号
    select_image_requested = pyqtSignal()
    take_screenshot_requested = pyqtSignal()
    retry_recognition_requested = pyqtSignal()
    compact_mode_toggled = pyqtSignal(bool)
    always_on_top_toggled = pyqtSignal(bool)  # 新增置顶切换信号
    screenshot_settings_requested = pyqtSignal()  # 新增截图设置信号
    
    def __init__(self, parent=None):
        super().__init__("图片识别", parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置图片识别按钮面板"""
        title_font = QFont("SimSun", 11)
        content_font = QFont("SimSun", 9)
        self.setFont(title_font)
        
        # 主布局 - 垂直布局包含按钮行和记录行
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)  # 设置固定5px边距
        self.setLayout(main_layout)
        
        # 按钮行 - 4个功能按钮居中，左右边距相同
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加左侧弹性空间实现居中
        button_layout.addStretch(1)
        
        # 4个功能按钮统一为70x30固定大小
        self.select_btn = QPushButton("选择图片")
        self.select_btn.setFont(content_font)
        self.select_btn.setFixedSize(70, 30)
        self.select_btn.clicked.connect(self.select_image_requested.emit)
        button_layout.addWidget(self.select_btn)
        
        self.retry_btn = QPushButton("再次识别")
        self.retry_btn.setFont(content_font)
        self.retry_btn.setFixedSize(70, 30)
        self.retry_btn.clicked.connect(self.retry_recognition_requested.emit)
        button_layout.addWidget(self.retry_btn)
        
        self.screenshot_btn = QPushButton("截图识别")
        self.screenshot_btn.setFont(content_font)
        self.screenshot_btn.setFixedSize(70, 30)
        self.screenshot_btn.clicked.connect(self.take_screenshot_requested.emit)
        button_layout.addWidget(self.screenshot_btn)
        
        self.shortcut_btn = QPushButton("截图设置")
        self.shortcut_btn.setFont(content_font)
        self.shortcut_btn.setFixedSize(70, 30)
        self.shortcut_btn.clicked.connect(self.screenshot_settings_requested)  # 修复：直接连接到信号，而不是emit方法
        button_layout.addWidget(self.shortcut_btn)
        
        # 添加右侧弹性空间实现居中
        button_layout.addStretch(1)
        
        main_layout.addLayout(button_layout)
        
        # 状态行 - 包含精简模式按钮、置顶按钮、成功计数器和置信度
        record_layout = QHBoxLayout()
        record_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        record_layout.setSpacing(2)  # 改为2px，与上一行按钮间距相同
        record_layout.setContentsMargins(0, 0, 0, 0)
        
        # 精简模式按钮放在状态行最左侧
        self.compact_mode_btn = QPushButton("精简模式")
        self.compact_mode_btn.setFont(content_font)
        self.compact_mode_btn.setCheckable(True)
        self.compact_mode_btn.setFixedSize(70, 30)
        self.compact_mode_btn.clicked.connect(self.on_compact_mode_toggled)
        record_layout.addWidget(self.compact_mode_btn)
        
        # 置顶按钮 - 调整为与其他按钮相同的大小
        self.always_on_top_btn = QPushButton("置顶")
        self.always_on_top_btn.setFont(content_font)
        self.always_on_top_btn.setCheckable(True)
        self.always_on_top_btn.setFixedSize(70, 30)  # 改为70x30，与其他按钮一致
        self.always_on_top_btn.setChecked(True)  # 默认置顶
        self.always_on_top_btn.clicked.connect(self.on_always_on_top_toggled)
        record_layout.addWidget(self.always_on_top_btn)
        
        self.record_label = QLabel("成功: 0")  # 只显示成功计数，初始为0
        self.record_label.setFont(content_font)
        self.record_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)  # 自适应宽度
        record_layout.addWidget(self.record_label)
        
        confidence_label = QLabel("置信度:")
        confidence_label.setFont(content_font)
        record_layout.addWidget(confidence_label)
        
        # 置信度条占满剩余空间
        self.confidence_bar = ConfidenceBar()
        # 使用Fixed策略确保高度严格为25px，Expanding确保宽度占满
        self.confidence_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.confidence_bar.set_confidence(0.0)
        record_layout.addWidget(self.confidence_bar)
        
        # 不再添加额外的弹性空间，让置信度条自然占满
        
        main_layout.addLayout(record_layout)
        
    def on_compact_mode_toggled(self, checked):
        """精简模式切换处理"""
        self.compact_mode_toggled.emit(checked)
        
    def on_always_on_top_toggled(self, checked):
        """置顶切换处理"""
        self.always_on_top_toggled.emit(checked)
        
    def update_record_count(self, success_count, fail_count):
        """更新识别记录 - 只显示成功计数"""
        self.record_label.setText(f"成功: {success_count}")
        
    def set_confidence(self, confidence):
        """设置置信度"""
        self.confidence_bar.set_confidence(confidence)
        
    def show_screenshot_shortcut_dialog(self):
        """这个方法应该由父组件调用，而不是直接连接到按钮"""
        from screenshot_dialog import ScreenshotShortcutDialog
        dialog = ScreenshotShortcutDialog(self, self.current_screenshot_shortcut if hasattr(self, 'current_screenshot_shortcut') else "printscreen")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_shortcut = dialog.get_selected_shortcut()
            self.current_screenshot_shortcut = new_shortcut
            # 注意：这里可能需要发出信号，但当前没有连接