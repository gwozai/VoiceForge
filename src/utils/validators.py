"""验证工具模块"""

import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from ..config.constants import SUPPORTED_FORMATS, SUPPORTED_MODELS, VOICES, ALLOWED_FILE_TYPES


class TTSValidator:
    """TTS请求验证器"""
    
    @staticmethod
    def validate_text(text: str, max_length: int = 100000) -> Dict[str, Any]:
        """验证文本输入 - 支持10万字长文本"""
        if not text or not text.strip():
            return {"valid": False, "error": "文本不能为空"}
        
        text = text.strip()
        if len(text) > max_length:
            return {"valid": False, "error": f"文本长度不能超过 {max_length} 字符（{max_length//1000}万字）"}
        
        return {"valid": True, "text": text, "length": len(text)}
    
    @staticmethod
    def validate_voice(voice: str) -> Dict[str, Any]:
        """验证语音参数"""
        if not voice:
            return {"valid": False, "error": "语音参数不能为空"}
        
        if voice not in VOICES:
            return {"valid": False, "error": f"不支持的语音: {voice}"}
        
        return {"valid": True, "voice": voice}
    
    @staticmethod
    def validate_format(format: str) -> Dict[str, Any]:
        """验证音频格式"""
        if not format:
            return {"valid": False, "error": "音频格式不能为空"}
        
        if format not in SUPPORTED_FORMATS:
            return {"valid": False, "error": f"不支持的音频格式: {format}"}
        
        return {"valid": True, "format": format}
    
    @staticmethod
    def validate_model(model: str) -> Dict[str, Any]:
        """验证模型参数"""
        if not model:
            return {"valid": False, "error": "模型参数不能为空"}
        
        if model not in SUPPORTED_MODELS:
            return {"valid": False, "error": f"不支持的模型: {model}"}
        
        return {"valid": True, "model": model}
    
    @staticmethod
    def validate_speed(speed: float) -> Dict[str, Any]:
        """验证语速参数"""
        if speed is None:
            return {"valid": False, "error": "语速参数不能为空"}
        
        if not isinstance(speed, (int, float)):
            return {"valid": False, "error": "语速参数必须是数字"}
        
        if speed < 0.25 or speed > 4.0:
            return {"valid": False, "error": "语速范围必须在 0.25x - 4.0x 之间"}
        
        return {"valid": True, "speed": float(speed)}
    
    @staticmethod
    def validate_api_key(api_key: str) -> Dict[str, Any]:
        """验证API密钥"""
        if not api_key or not api_key.strip():
            return {"valid": False, "error": "API密钥不能为空"}
        
        # 这里可以添加更复杂的API密钥验证逻辑
        return {"valid": True, "api_key": api_key.strip()}
    
    @staticmethod
    def validate_url(url: str) -> Dict[str, Any]:
        """验证URL格式"""
        if not url:
            return {"valid": False, "error": "URL不能为空"}
        
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return {"valid": False, "error": "无效的URL格式"}
            
            if result.scheme not in ['http', 'https']:
                return {"valid": False, "error": "URL必须使用HTTP或HTTPS协议"}
            
            return {"valid": True, "url": url}
        except Exception as e:
            return {"valid": False, "error": f"URL解析失败: {str(e)}"}
    
    @staticmethod
    def validate_file_type(filename: str) -> Dict[str, Any]:
        """验证文件类型"""
        if not filename:
            return {"valid": False, "error": "文件名不能为空"}
        
        filename_lower = filename.lower()
        is_allowed = any(filename_lower.endswith(ext) for ext in ALLOWED_FILE_TYPES)
        
        if not is_allowed:
            allowed_types_str = ', '.join(ALLOWED_FILE_TYPES)
            return {"valid": False, "error": f"不支持的文件格式，支持的格式: {allowed_types_str}"}
        
        return {"valid": True, "filename": filename}


class RequestValidator:
    """请求验证器"""
    
    def __init__(self):
        self.tts_validator = TTSValidator()
    
    def validate_tts_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证TTS请求"""
        errors = []
        validated_data = {}
        
        # 验证文本
        text_result = self.tts_validator.validate_text(data.get('input', ''))
        if not text_result['valid']:
            errors.append(text_result['error'])
        else:
            validated_data['input'] = text_result['text']
            validated_data['text_length'] = text_result['length']
        
        # 验证语音
        voice_result = self.tts_validator.validate_voice(data.get('voice', ''))
        if not voice_result['valid']:
            errors.append(voice_result['error'])
        else:
            validated_data['voice'] = voice_result['voice']
        
        # 验证格式
        format_result = self.tts_validator.validate_format(data.get('response_format', 'mp3'))
        if not format_result['valid']:
            errors.append(format_result['error'])
        else:
            validated_data['response_format'] = format_result['format']
        
        # 验证模型
        model_result = self.tts_validator.validate_model(data.get('model', 'tts-1'))
        if not model_result['valid']:
            errors.append(model_result['error'])
        else:
            validated_data['model'] = model_result['model']
        
        # 验证语速
        speed_result = self.tts_validator.validate_speed(data.get('speed', 1.0))
        if not speed_result['valid']:
            errors.append(speed_result['error'])
        else:
            validated_data['speed'] = speed_result['speed']
        
        # 验证API密钥
        api_key_result = self.tts_validator.validate_api_key(data.get('api_key', ''))
        if not api_key_result['valid']:
            errors.append(api_key_result['error'])
        else:
            validated_data['api_key'] = api_key_result['api_key']
        
        if errors:
            return {"valid": False, "errors": errors}
        
        return {"valid": True, "data": validated_data}
