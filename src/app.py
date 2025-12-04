"""
Flask应用工厂
"""

from flask import Flask
from typing import Optional

from .config.settings import Config
from .utils.database import DatabaseManager
from .utils.logger import setup_logger


def create_app(config: Optional[Config] = None) -> Flask:
    """创建Flask应用实例"""
    
    # 创建Flask应用
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # 加载配置
    if config:
        app.config.update(config.flask_config)
        app.config['VOICEFORGE_CONFIG'] = config
    
    # 设置日志
    if config:
        logger = setup_logger(config, 'voiceforge')
        app.logger = logger
    
    # 初始化数据库
    if config:
        db_manager = DatabaseManager(config)
        app.config['DB_MANAGER'] = db_manager
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册上下文处理器
    register_context_processors(app)
    
    return app


def register_blueprints(app: Flask) -> None:
    """注册蓝图"""
    from .controllers.main_controller import main_bp
    from .controllers.api_controller import api_bp
    from .controllers.voice_controller import voice_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(voice_bp, url_prefix='/voice')


def register_error_handlers(app: Flask) -> None:
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not Found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal Server Error"}, 500


def register_context_processors(app: Flask) -> None:
    """注册上下文处理器"""
    
    @app.context_processor
    def inject_config():
        """注入配置到模板上下文"""
        config = app.config.get('VOICEFORGE_CONFIG')
        if config:
            return {
                'config': config,
                'app_version': '2.0.0'
            }
        return {}
