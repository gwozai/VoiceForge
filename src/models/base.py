"""基础模型类"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json


class BaseModel(ABC):
    """基础模型类"""
    
    def __init__(self, **kwargs):
        self._data = {}
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        
        # 设置属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self._data[key] = value
    
    @property
    def created_at(self) -> datetime:
        """创建时间"""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """更新时间"""
        return self._updated_at
    
    def update(self, **kwargs) -> None:
        """更新模型数据"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self._data[key] = value
        self._updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = self._data.copy()
        
        # 添加类属性
        for key in dir(self):
            if not key.startswith('_') and not callable(getattr(self, key)):
                value = getattr(self, key)
                if not isinstance(value, (type, type(None))):
                    result[key] = value
        
        # 处理时间字段
        if hasattr(self, '_created_at'):
            result['created_at'] = self._created_at.isoformat()
        if hasattr(self, '_updated_at'):
            result['updated_at'] = self._updated_at.isoformat()
        
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """从字典创建实例"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseModel':
        """从JSON字符串创建实例"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @abstractmethod
    def validate(self) -> Dict[str, Any]:
        """验证模型数据"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data})"
    
    def __str__(self) -> str:
        return self.to_json()


class ValidationMixin:
    """验证混入类"""
    
    def _validate_required_fields(self, required_fields: list) -> Dict[str, Any]:
        """验证必填字段"""
        errors = []
        
        for field in required_fields:
            value = getattr(self, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"字段 '{field}' 是必填的")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _validate_field_type(self, field: str, expected_type: type) -> Dict[str, Any]:
        """验证字段类型"""
        value = getattr(self, field, None)
        
        if value is not None and not isinstance(value, expected_type):
            return {
                "valid": False, 
                "errors": [f"字段 '{field}' 应该是 {expected_type.__name__} 类型"]
            }
        
        return {"valid": True, "errors": []}
    
    def _validate_field_range(self, field: str, min_val: Any = None, max_val: Any = None) -> Dict[str, Any]:
        """验证字段范围"""
        value = getattr(self, field, None)
        errors = []
        
        if value is not None:
            if min_val is not None and value < min_val:
                errors.append(f"字段 '{field}' 不能小于 {min_val}")
            
            if max_val is not None and value > max_val:
                errors.append(f"字段 '{field}' 不能大于 {max_val}")
        
        return {"valid": len(errors) == 0, "errors": errors}
