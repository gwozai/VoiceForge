"""语音模型"""

from typing import Dict, Any, Optional
from .base import BaseModel, ValidationMixin


class Voice(BaseModel, ValidationMixin):
    """语音模型"""
    
    def __init__(self,
                 name: str = "",
                 language: str = "",
                 gender: str = "",
                 region: str = "",
                 description: str = "",
                 **kwargs):
        super().__init__(**kwargs)
        
        self.name = name
        self.language = language
        self.gender = gender
        self.region = region
        self.description = description
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        if self.gender:
            return f"{self.name} ({self.gender})"
        return self.name
    
    @property
    def full_name(self) -> str:
        """完整名称"""
        parts = [self.name]
        if self.language:
            parts.append(self.language)
        if self.gender:
            parts.append(self.gender)
        return " - ".join(parts)
    
    def validate(self) -> Dict[str, Any]:
        """验证语音数据"""
        errors = []
        
        # 验证必填字段
        required_result = self._validate_required_fields(['name'])
        if not required_result['valid']:
            errors.extend(required_result['errors'])
        
        # 验证性别
        if self.gender and self.gender not in ['Male', 'Female', 'Neutral']:
            errors.append("性别必须是 Male、Female 或 Neutral")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def matches_language(self, language: str) -> bool:
        """检查是否匹配指定语言"""
        if not language:
            return True
        return self.language.lower() == language.lower()
    
    def matches_gender(self, gender: str) -> bool:
        """检查是否匹配指定性别"""
        if not gender:
            return True
        return self.gender.lower() == gender.lower()
    
    @classmethod
    def from_edge_tts_format(cls, name: str, gender: str = "") -> 'Voice':
        """从Edge TTS格式创建语音对象"""
        # 从名称推断语言
        language = ""
        region = ""
        
        if name.startswith('zh-CN'):
            language = "Chinese"
            region = "China"
        elif name.startswith('zh-TW'):
            language = "Chinese"
            region = "Taiwan"
        elif name.startswith('zh-HK'):
            language = "Chinese"
            region = "Hong Kong"
        elif name.startswith('en-US'):
            language = "English"
            region = "United States"
        elif name.startswith('en-GB'):
            language = "English"
            region = "United Kingdom"
        elif name.startswith('ja-JP'):
            language = "Japanese"
            region = "Japan"
        elif name.startswith('ko-KR'):
            language = "Korean"
            region = "Korea"
        # 可以继续添加更多语言...
        
        return cls(
            name=name,
            language=language,
            gender=gender,
            region=region,
            description=f"{language} voice from {region}" if language and region else ""
        )
