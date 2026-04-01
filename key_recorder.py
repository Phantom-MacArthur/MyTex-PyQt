from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence


class StepByStepKeyRecorder(QLineEdit):
    """分步按键录制控件 - 支持先按Alt再按V的方式"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("点击此处开始录制...")
        self.setReadOnly(True)
        self.recording = False
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
        
        # 处理修饰键
        if key in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta]:
            # 记录修饰键
            if key == Qt.Key.Key_Control:
                self.recorded_modifiers.add("Ctrl")
            elif key == Qt.Key.Key_Alt:
                self.recorded_modifiers.add("Alt")
            elif key == Qt.Key.Key_Shift:
                self.recorded_modifiers.add("Shift")
            elif key == Qt.Key.Key_Meta:
                self.recorded_modifiers.add("Meta")
            return
            
        # 处理主键（字母、数字等）
        if key != Qt.Key.Key_unknown and key not in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta]:
            # 获取主键名称
            key_name = QKeySequence(key).toString().upper()
            if key_name and len(key_name) == 1:  # 只接受单个字符（字母、数字）
                self.recorded_main_key = key_name
                
                # 构建完整的快捷键序列
                sequence_parts = list(self.recorded_modifiers)
                if self.recorded_main_key:
                    sequence_parts.append(self.recorded_main_key)
                    
                if sequence_parts:
                    self.recorded_sequence = "+".join(sequence_parts)
                    self.setText(self.recorded_sequence)
                    
                    # 停止录制
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