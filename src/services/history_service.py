"""历史记录服务"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from ..utils.logger import LoggerMixin


class HistoryService(LoggerMixin):
    """历史记录服务类"""
    
    def __init__(self, db_manager=None):
        from flask import current_app
        self.db_manager = db_manager or current_app.config.get('DB_MANAGER')
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """获取生成统计数据"""
        if not self.db_manager:
            return {"success": False, "error": "数据库管理器未配置"}
        
        try:
            return self.db_manager.get_generation_stats()
        except Exception as e:
            self.logger.error(f"获取统计数据失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def export_logs_csv(self) -> Dict[str, Any]:
        """导出日志为CSV格式"""
        if not self.db_manager:
            return {"success": False, "error": "数据库管理器未配置"}
        
        try:
            data = self.db_manager.export_logs_csv()
            return {"success": True, "data": data}
        except Exception as e:
            self.logger.error(f"导出日志失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def cleanup_old_logs(self, days: int = 30) -> Dict[str, Any]:
        """清理旧日志"""
        if not self.db_manager:
            return {"success": False, "error": "数据库管理器未配置"}
        
        try:
            deleted_count = self.db_manager.cleanup_old_logs(days)
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"已清理 {deleted_count} 条超过 {days} 天的日志"
            }
        except Exception as e:
            self.logger.error(f"清理日志失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_recent_generations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近的生成记录"""
        if not self.db_manager:
            return []
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT * FROM generation_logs
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                records = []
                for row in cursor.fetchall():
                    record = dict(row)
                    # 格式化时间戳
                    if record.get('timestamp'):
                        try:
                            dt = datetime.fromisoformat(record['timestamp'])
                            record['formatted_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            record['formatted_time'] = record['timestamp']
                    
                    records.append(record)
                
                return records
                
        except Exception as e:
            self.logger.error(f"获取最近记录失败: {str(e)}")
            return []
    
    def get_voice_usage_stats(self) -> Dict[str, Any]:
        """获取语音使用统计"""
        if not self.db_manager:
            return {}
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT 
                        voice,
                        COUNT(*) as usage_count,
                        SUM(text_length) as total_chars,
                        AVG(duration) as avg_duration,
                        SUM(audio_size) as total_size
                    FROM generation_logs
                    WHERE status = 'success'
                    GROUP BY voice
                    ORDER BY usage_count DESC
                ''')
                
                stats = {}
                for row in cursor.fetchall():
                    voice_data = dict(row)
                    voice_data['avg_duration'] = round(voice_data['avg_duration'] or 0, 2)
                    voice_data['total_size_mb'] = round((voice_data['total_size'] or 0) / 1024 / 1024, 2)
                    stats[voice_data['voice']] = voice_data
                
                return stats
                
        except Exception as e:
            self.logger.error(f"获取语音统计失败: {str(e)}")
            return {}
    
    def get_daily_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取每日统计"""
        if not self.db_manager:
            return []
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as total_count,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
                        SUM(text_length) as total_chars,
                        AVG(duration) as avg_duration,
                        SUM(audio_size) as total_size
                    FROM generation_logs
                    WHERE DATE(timestamp) >= DATE('now', '-{} days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                '''.format(days))
                
                stats = []
                for row in cursor.fetchall():
                    day_data = dict(row)
                    day_data['success_rate'] = round(
                        (day_data['success_count'] / day_data['total_count'] * 100) if day_data['total_count'] > 0 else 0, 
                        1
                    )
                    day_data['avg_duration'] = round(day_data['avg_duration'] or 0, 2)
                    day_data['total_size_mb'] = round((day_data['total_size'] or 0) / 1024 / 1024, 2)
                    stats.append(day_data)
                
                return stats
                
        except Exception as e:
            self.logger.error(f"获取每日统计失败: {str(e)}")
            return []
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """获取错误分析"""
        if not self.db_manager:
            return {}
        
        try:
            with self.db_manager.get_connection() as conn:
                # 错误类型统计
                cursor = conn.execute('''
                    SELECT 
                        error_message,
                        COUNT(*) as count,
                        MAX(timestamp) as last_occurrence
                    FROM generation_logs
                    WHERE status = 'error' AND error_message IS NOT NULL
                    GROUP BY error_message
                    ORDER BY count DESC
                    LIMIT 20
                ''')
                
                error_types = []
                for row in cursor.fetchall():
                    error_data = dict(row)
                    try:
                        dt = datetime.fromisoformat(error_data['last_occurrence'])
                        error_data['last_occurrence_formatted'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        error_data['last_occurrence_formatted'] = error_data['last_occurrence']
                    error_types.append(error_data)
                
                # 总体错误率
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count
                    FROM generation_logs
                ''')
                
                totals = cursor.fetchone()
                error_rate = round(
                    (totals['error_count'] / totals['total_requests'] * 100) if totals['total_requests'] > 0 else 0,
                    2
                )
                
                return {
                    "error_types": error_types,
                    "total_requests": totals['total_requests'],
                    "error_count": totals['error_count'],
                    "error_rate": error_rate
                }
                
        except Exception as e:
            self.logger.error(f"获取错误分析失败: {str(e)}")
            return {}
