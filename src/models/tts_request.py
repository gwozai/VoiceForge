"""TTS请求和响应模型"""

from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import io

from .base import BaseModel, ValidationMixin
from ..config.constants import SUPPORTED_FORMATS, SUPPORTED_MODELS, VOICES


class TTSRequest(BaseModel, ValidationMixin):
    """TTS请求模型"""
    
    def __init__(self, 
                 input: str = "",
                 voice: str = "zh-CN-XiaoxiaoNeural",
                 model: str = "tts-1",
                 response_format: str = "mp3",
                 speed: float = 1.0,
                 api_key: str = "",
                 stream_format: str = "",
                 **kwargs):
        super().__init__(**kwargs)
        
        self.input = input
        self.voice = voice
        self.model = model
        self.response_format = response_format
        self.speed = speed
        self.api_key = api_key
        self.stream_format = stream_format
    
    @property
    def text_length(self) -> int:
        """文本长度"""
        return len(self.input) if self.input else 0
    
    @property
    def is_streaming(self) -> bool:
        """是否为流式请求"""
        return bool(self.stream_format)
    
    @property
    def mode(self) -> str:
        """请求模式"""
        return "流式" if self.is_streaming else "普通"
    
    def validate(self) -> Dict[str, Any]:
        """验证请求数据"""
        errors = []
        
        # 验证必填字段
        required_result = self._validate_required_fields(['input', 'voice', 'model', 'api_key'])
        if not required_result['valid']:
            errors.extend(required_result['errors'])
        
        # 验证文本长度 - 支持10万字长文本
        if self.input and len(self.input) > 100000:
            errors.append("文本长度不能超过100000字符（10万字）")
        
        # 验证语音
        if self.voice and self.voice not in VOICES:
            errors.append(f"不支持的语音: {self.voice}")
        
        # 验证模型
        if self.model and self.model not in SUPPORTED_MODELS:
            errors.append(f"不支持的模型: {self.model}")
        
        # 验证格式
        if self.response_format and self.response_format not in SUPPORTED_FORMATS:
            errors.append(f"不支持的音频格式: {self.response_format}")
        
        # 验证语速
        speed_result = self._validate_field_range('speed', 0.25, 4.0)
        if not speed_result['valid']:
            errors.extend(speed_result['errors'])
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def to_api_dict(self) -> Dict[str, Any]:
        """转换为API请求格式"""
        data = {
            "model": self.model,
            "input": self.input,
            "voice": self.voice,
        }
        
        if self.response_format:
            data["response_format"] = self.response_format
        
        if self.speed:
            data["speed"] = self.speed
        
        if self.stream_format:
            data["stream_format"] = self.stream_format
        
        return data
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


@dataclass
class TTSResponse:
    """TTS响应模型"""
    
    success: bool
    audio_data: Optional[Union[bytes, io.BytesIO]] = None
    audio_url: Optional[str] = None
    audio_size: Optional[int] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    
    @property
    def has_audio(self) -> bool:
        """是否包含音频数据"""
        return self.audio_data is not None or self.audio_url is not None
    
    @property
    def audio_size_mb(self) -> float:
        """音频大小（MB）"""
        if self.audio_size:
            return round(self.audio_size / 1024 / 1024, 2)
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "audio_url": self.audio_url,
            "audio_size": self.audio_size,
            "audio_size_mb": self.audio_size_mb,
            "duration": self.duration,
            "error_message": self.error_message,
            "status_code": self.status_code,
            "has_audio": self.has_audio,
        }


class StreamingTTSResponse:
    """流式TTS响应模型"""
    
    def __init__(self, request: TTSRequest):
        self.request = request
        self.chunks = []
        self.total_size = 0
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.success = False
    
    def add_chunk(self, chunk: bytes) -> None:
        """添加音频块"""
        self.chunks.append(chunk)
        self.total_size += len(chunk)
    
    def finalize(self, success: bool = True, error_message: str = None) -> None:
        """完成响应"""
        self.success = success
        self.error_message = error_message
        if self.end_time is None:
            import time
            self.end_time = time.time()
    
    @property
    def audio_data(self) -> bytes:
        """获取完整音频数据"""
        return b''.join(self.chunks)
    
    @property
    def duration(self) -> Optional[float]:
        """获取生成耗时"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def to_response(self) -> TTSResponse:
        """转换为标准响应"""
        return TTSResponse(
            success=self.success,
            audio_data=self.audio_data,
            audio_size=self.total_size,
            duration=self.duration,
            error_message=self.error_message
        )
