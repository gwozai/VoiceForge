"""日志工具模块"""

import logging
import os
from typing import Optional

from ..config.settings import Config


def setup_logger(config: Config, name: Optional[str] = None) -> logging.Logger:
    """设置日志记录器"""
    
    logger_name = name or __name__
    logger = logging.getLogger(logger_name)
    
    # 避免重复设置
    if logger.handlers:
        return logger
    
    # 获取配置
    log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO').upper())
    log_file = config.get('LOG_FILE', 'tts_generation.log')
    log_format = config.get('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
    
    # 设置日志级别
    logger.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(log_format)
    
    # 文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


class LoggerMixin:
    """日志混入类"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取日志记录器"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
