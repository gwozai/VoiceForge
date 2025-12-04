"""历史记录模型"""

from typing import Dict, Any, Optional
from datetime import datetime

from .base import BaseModel, ValidationMixin


class GenerationLog(BaseModel, ValidationMixin):
    """生成日志模型"""
    
    def __init__(self,
                 id: Optional[int] = None,
                 timestamp: str = "",
                 text_length: int = 0,
                 voice: str = "",
                 format: str = "",
                 speed: float = 1.0,
                 mode: str = "",
                 duration: Optional[float] = None,
                 audio_size: Optional[int] = None,
                 status: str = "success",
                 error_message: Optional[str] = None,
                 ip_address: Optional[str] = None,
                 user_agent: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        
        self.id = id
        self.timestamp = timestamp or datetime.now().isoformat()
        self.text_length = text_length
        self.voice = voice
        self.format = format
        self.speed = speed
        self.mode = mode
        self.duration = duration
        self.audio_size = audio_size
        self.status = status
        self.error_message = error_message
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    @property
    def formatted_timestamp(self) -> str:
        """格式化时间戳"""
        try:
            dt = datetime.fromisoformat(self.timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return self.timestamp
    
    @property
    def audio_size_mb(self) -> float:
        """音频大小（MB）"""
        if self.audio_size:
            return round(self.audio_size / 1024 / 1024, 2)
        return 0.0
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == 'success'
    
    @property
    def is_streaming(self) -> bool:
        """是否为流式"""
        return self.mode == '流式'
    
    def validate(self) -> Dict[str, Any]:
        """验证日志数据"""
        errors = []
        
        # 验证必填字段
        required_result = self._validate_required_fields(['timestamp', 'text_length', 'voice', 'format'])
        if not required_result['valid']:
            errors.extend(required_result['errors'])
        
        # 验证数值字段
        if self.text_length < 0:
            errors.append("文本长度不能为负数")
        
        if self.speed <= 0:
            errors.append("语速必须大于0")
        
        if self.duration is not None and self.duration < 0:
            errors.append("持续时间不能为负数")
        
        if self.audio_size is not None and self.audio_size < 0:
            errors.append("音频大小不能为负数")
        
        # 验证状态
        if self.status not in ['success', 'error']:
            errors.append("状态必须是 'success' 或 'error'")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'GenerationLog':
        """从数据库行创建实例"""
        return cls(**row)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            'formatted_timestamp': self.formatted_timestamp,
            'audio_size_mb': self.audio_size_mb,
            'is_success': self.is_success,
            'is_streaming': self.is_streaming
        })
        return data
