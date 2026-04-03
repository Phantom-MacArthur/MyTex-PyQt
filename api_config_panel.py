from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QRadioButton, QButtonGroup, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from api_config import APIService, APIConfigManager


class APIConfigPanel(QGroupBox):
    # 定义信号
    config_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("API配置", parent)
        self.api_config_manager = APIConfigManager()
        self.setup_ui()
        
    def setup_ui(self):
        """设置API配置面板"""
        title_font = QFont("SimSun", 11)
        content_font = QFont("SimSun", 9)
        self.setFont(title_font)
        
        # 显式设置QGroupBox的边距，上边距为10像素
        self.setContentsMargins(0, 10, 0, 0)
        
        config_layout = QVBoxLayout()
        self.setLayout(config_layout)
        
        # API服务选择 - 下拉框占满剩余空间
        api_service_layout = QHBoxLayout()
        api_service_layout.setContentsMargins(0, 0, 0, 0)
        api_service_layout.setSpacing(5)
        api_service_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 添加左对齐，与其他行一致
        api_service_label = QLabel("API服务:")
        api_service_label.setFont(content_font)
        self.api_service_combo = QComboBox()
        self.api_service_combo.setFont(content_font)
        self.api_service_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.api_service_combo.setMinimumWidth(200)  # 调整为与AppID相同的最小宽度
        # 添加 SimpleTex 标准版和轻量版选项
        self.api_service_combo.addItem("SimpleTex（标准版）", "simples_std")
        self.api_service_combo.addItem("SimpleTex（轻量版）", "simples_turbo")
        api_service_layout.addWidget(api_service_label)
        api_service_layout.addWidget(self.api_service_combo)
        config_layout.addLayout(api_service_layout)
        
        # App ID - 调整宽度适应300px总宽度
        app_id_layout = QHBoxLayout()
        app_id_layout.setContentsMargins(0, 0, 0, 0)
        app_id_layout.setSpacing(5)
        app_id_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        app_id_label = QLabel("App ID:")
        app_id_label.setFont(content_font)
        self.app_id_entry = QLineEdit()
        self.app_id_entry.setFont(content_font)
        self.app_id_entry.setMinimumWidth(200)  # 保持200px最小宽度
        app_id_layout.addWidget(app_id_label)
        app_id_layout.addWidget(self.app_id_entry)
        config_layout.addLayout(app_id_layout)
        
        # App Secret - 调整宽度适应300px总宽度  
        app_secret_layout = QHBoxLayout()
        app_secret_layout.setContentsMargins(0, 0, 0, 0)
        app_secret_layout.setSpacing(5)
        app_secret_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        app_secret_label = QLabel("App Secret:")
        app_secret_label.setFont(content_font)
        self.app_secret_entry = QLineEdit()
        self.app_secret_entry.setFont(content_font)
        self.app_secret_entry.setEchoMode(QLineEdit.EchoMode.Normal)  # 显示明文
        self.app_secret_entry.setMinimumWidth(180)  # 保持180px最小宽度
        app_secret_layout.addWidget(app_secret_label)
        app_secret_layout.addWidget(self.app_secret_entry)
        config_layout.addLayout(app_secret_layout)
        
        # 连接信号 - 移除端口相关的信号连接
        self.app_id_entry.textChanged.connect(self._on_config_changed)
        self.app_secret_entry.textChanged.connect(self._on_config_changed)
        
    def _on_config_changed(self):
        """配置发生变化时更新配置管理器"""
        app_id = self.get_app_id()
        app_secret = self.get_app_secret()
        endpoint_choice = self.get_endpoint_choice()
        self.api_config_manager.set_simpletex_config(app_id, app_secret, endpoint_choice)
        self.config_changed.emit()
            
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
        """获取API端口选择 - 从服务选择中解析"""
        current_data = self.api_service_combo.currentData()
        if current_data == "simples_turbo":
            return "turbo"
        else:
            return "standard"
            
    def set_service_selection(self, is_turbo):
        """设置服务选择"""
        if is_turbo:
            self.api_service_combo.setCurrentIndex(1)  # 轻量版
        else:
            self.api_service_combo.setCurrentIndex(0)  # 标准版

    def get_api_config_manager(self):
        """获取API配置管理器"""
        return self.api_config_manager