"""控制器模块"""

from .main_controller import main_bp
from .api_controller import api_bp
from .voice_controller import voice_bp

__all__ = ['main_bp', 'api_bp', 'voice_bp']
