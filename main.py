"""
VoiceForge 主应用入口
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import create_app
from src.config.settings import get_config


def main():
    """主函数"""
    # 获取环境配置
    env = os.getenv('FLASK_ENV', 'development')
    config = get_config(env)
    
    # 创建应用
    app = create_app(config)
    
    # 运行应用
    app.run(
        debug=config.get('DEBUG'),
        host=config.get('HOST'),
        port=config.get('PORT')
    )


if __name__ == "__main__":
    main()
