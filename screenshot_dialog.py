from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from advanced_key_recorder import AdvancedKeyRecorder


class ScreenshotShortcutDialog(QDialog):
    """截图快捷键设置对话框"""
    
    def __init__(self, parent=None, current_shortcut="alt+c"):  # 默认改为alt+c
        super().__init__(parent)
        self.setWindowTitle("设置截图快捷键")
        self.current_shortcut = current_shortcut
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout()
        
        # 快捷键选择 - 更新选项
        self.shortcut_combo = QComboBox()
        self.shortcut_combo.addItems(["PrintScreen", "Alt+C", "自定义"])
        if self.current_shortcut == "printscreen":
            self.shortcut_combo.setCurrentText("PrintScreen")
        elif self.current_shortcut == "alt+c":
            self.shortcut_combo.setCurrentText("Alt+C")
        else:
            self.shortcut_combo.setCurrentText("自定义")
            
        layout.addRow("快捷键方式:", self.shortcut_combo)
        
        # 自定义快捷键输入（仅在选择自定义时显示）
        self.custom_shortcut_input = AdvancedKeyRecorder()
        if self.current_shortcut not in ["printscreen", "alt+v"]:
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
        elif shortcut_type == "Alt+C":
            return "alt+c"
        else:
            custom_text = self.custom_shortcut_input.get_recorded_sequence()
            return custom_text if custom_text else "printscreen"