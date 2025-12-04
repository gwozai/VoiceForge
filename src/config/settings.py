"""配置管理类"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('config/.env')


class Config:
    """基础配置类"""
    
    def __init__(self):
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        self._config.update({
            # Flask 配置
            'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key'),
            'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
            'HOST': os.getenv('FLASK_HOST', '0.0.0.0'),
            'PORT': int(os.getenv('FLASK_PORT', '8080')),
            
            # 数据库配置
            'DB_PATH': os.getenv('DB_PATH', 'tts_stats.db'),
            
            # API 配置
            'API_BASE_URL': os.getenv('API_BASE_URL', 'http://117.72.56.34:5050'),
            'API_ENDPOINT': os.getenv('API_ENDPOINT', '/v1/audio/speech'),
            'VOICES_ENDPOINT': os.getenv('VOICES_ENDPOINT', '/voices'),
            'MODELS_ENDPOINT': os.getenv('MODELS_ENDPOINT', '/models'),
            
            # 默认值配置
            'DEFAULT_API_KEY': os.getenv('DEFAULT_API_KEY', 'your_api_key_here'),
            'DEFAULT_MODEL': os.getenv('DEFAULT_MODEL', 'tts-1'),
            'DEFAULT_VOICE': os.getenv('DEFAULT_VOICE', 'zh-CN-XiaoxiaoNeural'),
            'DEFAULT_FORMAT': os.getenv('DEFAULT_FORMAT', 'mp3'),
            'DEFAULT_SPEED': float(os.getenv('DEFAULT_SPEED', '1.0')),
            'DEFAULT_LANGUAGE': os.getenv('DEFAULT_LANGUAGE', 'zh-CN'),
            
            # 日志配置
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE', 'tts_generation.log'),
            
            # 静态文件配置
            'STATIC_FOLDER': 'static',
            'TEMPLATE_FOLDER': 'templates',
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self._config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """批量更新配置"""
        self._config.update(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self._config.copy()
    
    @property
    def flask_config(self) -> Dict[str, Any]:
        """获取Flask相关配置"""
        return {
            'SECRET_KEY': self.get('SECRET_KEY'),
            'DEBUG': self.get('DEBUG'),
        }


class DevelopmentConfig(Config):
    """开发环境配置"""
    
    def _load_config(self):
        super()._load_config()
        self._config.update({
            'DEBUG': True,
            'LOG_LEVEL': 'DEBUG',
        })


class ProductionConfig(Config):
    """生产环境配置"""
    
    def _load_config(self):
        super()._load_config()
        self._config.update({
            'DEBUG': False,
            'LOG_LEVEL': 'INFO',
        })


class TestConfig(Config):
    """测试环境配置"""
    
    def _load_config(self):
        super()._load_config()
        self._config.update({
            'DEBUG': True,
            'TESTING': True,
            'DB_PATH': ':memory:',  # 内存数据库
            'LOG_LEVEL': 'DEBUG',
        })


# 配置工厂
def get_config(env: str = None) -> Config:
    """根据环境获取配置"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestConfig,
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()
