"""数据库管理模块"""

import sqlite3
import logging
from threading import Lock
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

from ..config.settings import Config


class DatabaseManager:
    """数据库管理器 - 单例模式"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, config: Config = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Config = None):
        if hasattr(self, '_initialized'):
            return
        
        self.config = config
        self.db_path = config.get('DB_PATH') if config else 'tts_stats.db'
        self.logger = logging.getLogger(__name__)
        self._initialized = True
        
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS generation_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        text_length INTEGER NOT NULL,
                        voice TEXT NOT NULL,
                        format TEXT NOT NULL,
                        speed REAL DEFAULT 1.0,
                        mode TEXT NOT NULL,
                        duration REAL,
                        audio_size INTEGER,
                        status TEXT DEFAULT 'success',
                        error_message TEXT,
                        ip_address TEXT,
                        user_agent TEXT
                    )
                ''')
                conn.commit()
            self.logger.info("数据库初始化完成")
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def log_generation(self, 
                      text_length: int,
                      voice: str,
                      format: str,
                      speed: float,
                      mode: str,
                      duration: Optional[float] = None,
                      audio_size: Optional[int] = None,
                      status: str = 'success',
                      error_message: Optional[str] = None,
                      ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None) -> int:
        """记录生成日志"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO generation_logs 
                    (timestamp, text_length, voice, format, speed, mode, 
                     duration, audio_size, status, error_message, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    text_length, voice, format, speed, mode,
                    duration, audio_size, status, error_message,
                    ip_address, user_agent[:200] if user_agent else None
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"记录生成日志失败: {e}")
            return -1
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """获取生成统计数据"""
        try:
            with self.get_connection() as conn:
                # 总体统计
                summary = conn.execute('''
                    SELECT 
                        COUNT(*) as total_count,
                        SUM(text_length) as total_chars,
                        SUM(duration) as total_duration,
                        SUM(audio_size) as total_size,
                        AVG(duration) as avg_duration,
                        AVG(text_length) as avg_chars
                    FROM generation_logs
                    WHERE status = 'success'
                ''').fetchone()
                
                # 按语音统计
                voice_stats = conn.execute('''
                    SELECT voice, COUNT(*) as count, SUM(text_length) as chars
                    FROM generation_logs
                    WHERE status = 'success'
                    GROUP BY voice
                    ORDER BY count DESC
                    LIMIT 10
                ''').fetchall()
                
                # 按日期统计
                daily_stats = conn.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) as count, SUM(text_length) as chars
                    FROM generation_logs
                    WHERE status = 'success'
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                    LIMIT 30
                ''').fetchall()
                
                # 最近记录
                recent_logs = conn.execute('''
                    SELECT * FROM generation_logs
                    ORDER BY timestamp DESC
                    LIMIT 50
                ''').fetchall()
                
                return {
                    "success": True,
                    "summary": {
                        "total_count": summary['total_count'] or 0,
                        "total_chars": summary['total_chars'] or 0,
                        "total_duration": round(summary['total_duration'] or 0, 2),
                        "total_size_mb": round((summary['total_size'] or 0) / 1024 / 1024, 2),
                        "avg_duration": round(summary['avg_duration'] or 0, 2),
                        "avg_chars": round(summary['avg_chars'] or 0, 0)
                    },
                    "voice_stats": [dict(row) for row in voice_stats],
                    "daily_stats": [dict(row) for row in daily_stats],
                    "recent_logs": [dict(row) for row in recent_logs]
                }
        except Exception as e:
            self.logger.error(f"获取统计数据失败: {e}")
            return {"success": False, "error": str(e)}
    
    def export_logs_csv(self) -> List[Dict[str, Any]]:
        """导出日志为CSV格式数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT * FROM generation_logs ORDER BY timestamp DESC')
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                return {
                    "columns": columns,
                    "rows": [dict(row) for row in rows]
                }
        except Exception as e:
            self.logger.error(f"导出日志失败: {e}")
            return {"columns": [], "rows": []}
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """清理旧日志"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    DELETE FROM generation_logs 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                conn.commit()
                deleted_count = cursor.rowcount
                self.logger.info(f"清理了 {deleted_count} 条旧日志")
                return deleted_count
        except Exception as e:
            self.logger.error(f"清理旧日志失败: {e}")
            return 0
