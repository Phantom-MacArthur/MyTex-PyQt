from enum import Enum
from dataclasses import dataclass
from typing import Optional


class APIService(Enum):
    """支持的API服务类型"""
    SIMPLETEX = "simpletex"
    # 未来可以添加其他API服务
    # OTHER_API = "other_api"


@dataclass
class APIConfig:
    """API配置数据类"""
    service: APIService
    app_id: str = ""
    app_secret: str = ""
    endpoint_choice: str = "standard"  # "standard" or "turbo"
    
    def is_valid(self) -> bool:
        """检查配置是否有效"""
        return bool(self.app_id.strip()) and bool(self.app_secret.strip())
    
    @classmethod
    def create_simpletex_config(cls, app_id: str = "", app_secret: str = "", endpoint_choice: str = "standard") -> 'APIConfig':
        """创建 SimpleTex API 配置"""
        return cls(
            service=APIService.SIMPLETEX,
            app_id=app_id,
            app_secret=app_secret,
            endpoint_choice=endpoint_choice
        )


class APIConfigManager:
    """API配置管理器"""
    
    def __init__(self):
        self.current_config: Optional[APIConfig] = None
        self._initialize_default_config()
    
    def _initialize_default_config(self):
        """初始化默认配置"""
        self.current_config = APIConfig.create_simpletex_config()
    
    def set_simpletex_config(self, app_id: str, app_secret: str, endpoint_choice: str = "standard"):
        """设置 SimpleTex 配置"""
        self.current_config = APIConfig.create_simpletex_config(app_id, app_secret, endpoint_choice)
    
    def get_current_config(self) -> Optional[APIConfig]:
        """获取当前配置"""
        return self.current_config
    
    def is_config_valid(self) -> bool:
        """检查当前配置是否有效"""
        return self.current_config is not None and self.current_config.is_valid()
    
    def get_service_name(self) -> str:
        """获取当前服务名称"""
        if self.current_config:
            return self.current_config.service.value
        return ""
    
    def get_app_id(self) -> str:
        """获取 App ID"""
        if self.current_config:
            return self.current_config.app_id
        return ""
    
    def get_app_secret(self) -> str:
        """获取 App Secret"""
        if self.current_config:
            return self.current_config.app_secret
        return ""
    
    def get_endpoint_choice(self) -> str:
        """获取端点选择"""
        if self.current_config:
            return self.current_config.endpoint_choice
        return "standard"


# ========== 测试配置 - 用于开发调试 ========== #
TEST_CONFIG = APIConfig.create_simpletex_config(
    app_id="XvEdRCIKdRFlkSEdp28q3Ep4",
    app_secret="TtssQ12JCv6IrkUTqGYwuYFJkszCAAFk",
    endpoint_choice="standard"
)
# ============================================ #
