from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence


class AdvancedKeyRecorder(QLineEdit):
    """高级按键录制控件 - 支持Ctrl/Alt(+Shift)+字母数字的组合，不允许重复"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("点击此处开始录制...")
        self.setReadOnly(True)
        self.recording = False
        self.recorded_keys = []
        self.recorded_modifiers = set()
        self.recorded_main_key = ""
        self.recorded_sequence = ""
        
    def mousePressEvent(self, event):
        """鼠标点击开始录制"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_recording()
        super().mousePressEvent(event)
        
    def start_recording(self):
        """开始录制快捷键"""
        self.recording = True
        self.recorded_keys.clear()
        self.recorded_modifiers.clear()
        self.recorded_main_key = ""
        self.recorded_sequence = ""
        self.setText("请按下快捷键组合...")
        self.grabKeyboard()  # 捕获所有键盘事件
        
    def keyPressEvent(self, event):
        """处理键盘按下事件"""
        if not self.recording:
            return super().keyPressEvent(event)
            
        key = event.key()
        modifiers = event.modifiers()
        
        # 如果已经录满3个按键，停止录制
        if len(self.recorded_keys) >= 3:
            return
            
        # 处理修饰键（Ctrl、Alt、Shift）
        if key in [Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift]:
            modifier_name = ""
            if key == Qt.Key.Key_Control:
                modifier_name = "Ctrl"
            elif key == Qt.Key.Key_Alt:
                modifier_name = "Alt"
            elif key == Qt.Key.Key_Shift:
                modifier_name = "Shift"
                
            # 不允许重复添加相同的修饰键
            if modifier_name not in self.recorded_modifiers:
                self.recorded_modifiers.add(modifier_name)
            return
            
        # 处理主键（字母、数字）
        if key != Qt.Key.Key_unknown:
            # 获取按键名称
            key_name = QKeySequence(key).toString()
            if key_name and len(key_name) == 1:  # 只接受单个字符（字母、数字）
                # 转换为大写
                key_name = key_name.upper()
                
                # 确保已经有Ctrl或Alt修饰键
                has_ctrl_or_alt = "Ctrl" in self.recorded_modifiers or "Alt" in self.recorded_modifiers
                if not has_ctrl_or_alt:
                    return  # 必须有Ctrl或Alt
                    
                # 不允许重复主键
                if self.recorded_main_key == key_name:
                    return
                    
                self.recorded_main_key = key_name
                
                # 构建完整的快捷键序列
                sequence_parts = []
                
                # 添加修饰键（按固定顺序：Ctrl, Alt, Shift）
                if "Ctrl" in self.recorded_modifiers:
                    sequence_parts.append("Ctrl")
                if "Alt" in self.recorded_modifiers:
                    sequence_parts.append("Alt")
                if "Shift" in self.recorded_modifiers:
                    sequence_parts.append("Shift")
                    
                # 添加主键
                sequence_parts.append(self.recorded_main_key)
                self.recorded_sequence = "+".join(sequence_parts)
                self.setText(self.recorded_sequence)
                
                # 自动停止录制（因为已经完成有效组合）
                QTimer.singleShot(100, self.stop_recording)
        
    def keyReleaseEvent(self, event):
        """处理键盘释放事件"""
        if not self.recording:
            return super().keyReleaseEvent(event)
            
    def stop_recording(self):
        """停止录制"""
        self.recording = False
        self.releaseKeyboard()
        
    def get_recorded_sequence(self):
        """获取录制的按键序列"""
        return self.recorded_sequence
        
    def clear_recording(self):
        """清空录制内容"""
        self.recorded_keys.clear()
        self.recorded_modifiers.clear()
        self.recorded_main_key = ""
        self.recorded_sequence = ""
        self.setText("")