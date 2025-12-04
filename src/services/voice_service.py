"""语音管理服务"""

import requests
import base64
from typing import List, Dict, Any, Optional

from ..models.voice import Voice
from ..utils.logger import LoggerMixin
from ..utils.helpers import get_language_from_voice, get_preview_text
from ..config.constants import OPENAI_VOICE_MAPPING
import json
import os


class VoiceService(LoggerMixin):
    """语音管理服务类"""
    
    def __init__(self, config=None, tts_service=None):
        from flask import current_app
        self.config = config or current_app.config.get('VOICEFORGE_CONFIG')
        self.tts_service = tts_service
        
        # API配置
        self.api_base_url = self.config.get('API_BASE_URL')
        self.voices_endpoint = self.config.get('VOICES_ENDPOINT')
        self.api_endpoint = self.config.get('API_ENDPOINT')
    
    def get_all_voices(self) -> Dict[str, List[Voice]]:
        """获取所有语音列表"""
        voices_by_category = {}
        
        # 尝试从JSON文件加载语音列表
        voices_data = self._load_voices_from_json()
        
        if voices_data and "voices" in voices_data:
            # 使用JSON文件中的语音列表
            for category, voice_list in voices_data["voices"].items():
                voices = []
                for voice_info in voice_list:
                    if isinstance(voice_info, dict):
                        # 新格式：包含详细信息的字典
                        # 提取简短的语音名称（用于实际TTS调用）
                        short_name = voice_info.get("short_name", voice_info["name"])
                        if not short_name or short_name == voice_info["name"]:
                            # 从完整名称中提取简短名称
                            full_name = voice_info["name"]
                            if "(" in full_name and ")" in full_name:
                                # 格式: "Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural) (Female)"
                                parts = full_name.split("(")
                                if len(parts) >= 2:
                                    locale_voice = parts[1].split(")")[0]  # "zh-CN, XiaoxiaoNeural"
                                    if "," in locale_voice:
                                        locale, voice_name = locale_voice.split(", ", 1)
                                        short_name = f"{locale.strip()}-{voice_name.strip()}"
                                    else:
                                        short_name = locale_voice.strip()
                        
                        voice = Voice(
                            name=short_name,  # 使用简短名称
                            language=voice_info.get("locale", ""),
                            gender=voice_info.get("gender", "Unknown"),
                            region=voice_info.get("locale", "").split("-")[-1] if voice_info.get("locale") else "",
                            description=f"{voice_info.get('gender', 'Unknown')} voice"
                        )
                    else:
                        # 旧格式：只有语音名称的字符串
                        gender = self._infer_gender(voice_info)
                        voice = Voice.from_edge_tts_format(voice_info, gender)
                    voices.append(voice)
                
                voices_by_category[category] = voices
        else:
            # 回退到默认语音列表
            voices_by_category = self._get_default_voices()
        
        return voices_by_category
    
    def _load_voices_from_json(self) -> Optional[Dict[str, Any]]:
        """从JSON文件加载语音列表"""
        try:
            # 尝试加载完整的语音列表
            config_dir = os.path.dirname(os.path.dirname(__file__))  # src目录
            json_path = os.path.join(config_dir, "config", "complete_edge_voices.json")
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # 回退到基础语音列表
            json_path = os.path.join(config_dir, "config", "edge_tts_voices.json")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
        except Exception as e:
            self.logger.warning(f"加载语音JSON文件失败: {e}")
        
        return None
    
    def _get_default_voices(self) -> Dict[str, List[Voice]]:
        """获取默认语音列表（回退方案）"""
        default_voices = {
            "OpenAI Voices": [
                Voice(name="alloy", gender="Neutral", language="en-US"),
                Voice(name="echo", gender="Male", language="en-US"),
                Voice(name="fable", gender="Female", language="en-US"),
                Voice(name="onyx", gender="Male", language="en-US"),
                Voice(name="nova", gender="Female", language="en-US"),
                Voice(name="shimmer", gender="Female", language="en-US"),
            ],
            "中文(简体)": [
                Voice.from_edge_tts_format("zh-CN-XiaoxiaoNeural", "Female"),
                Voice.from_edge_tts_format("zh-CN-YunxiNeural", "Male"),
                Voice.from_edge_tts_format("zh-CN-XiaohanNeural", "Female"),
                Voice.from_edge_tts_format("zh-CN-XiaomoNeural", "Female"),
            ],
            "English (US)": [
                Voice.from_edge_tts_format("en-US-AriaNeural", "Female"),
                Voice.from_edge_tts_format("en-US-DavisNeural", "Male"),
                Voice.from_edge_tts_format("en-US-JennyNeural", "Female"),
                Voice.from_edge_tts_format("en-US-GuyNeural", "Male"),
            ]
        }
        return default_voices
    
    def get_voice_by_name(self, voice_name: str) -> Optional[Voice]:
        """根据名称获取语音"""
        # 检查是否是OpenAI语音
        if voice_name in OPENAI_VOICE_MAPPING:
            actual_voice = OPENAI_VOICE_MAPPING[voice_name]
            gender = self._infer_gender(actual_voice)
            return Voice.from_edge_tts_format(actual_voice, gender)
        
        # 检查是否在语音列表中
        all_voices = self.get_all_voices()
        for voice_list in all_voices.values():
            for voice in voice_list:
                if voice.name == voice_name:
                    return voice
        
        return None
    
    def get_voices_from_api(self, api_key: str) -> Dict[str, Any]:
        """从API获取语音列表"""
        try:
            url = self.api_base_url + self.voices_endpoint
            headers = {"Authorization": f"Bearer {api_key}"}
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"从API获取语音失败: {str(e)}")
            raise
    
    def preview_voice(self, voice_name: str, api_key: str, custom_text: str = None) -> Dict[str, Any]:
        """预览语音"""
        try:
            # 获取语音对象
            voice = self.get_voice_by_name(voice_name)
            if not voice:
                return {
                    "success": False,
                    "error": f"未找到语音: {voice_name}"
                }
            
            # 获取预览文本
            language = get_language_from_voice(voice_name)
            preview_text = custom_text or get_preview_text(language)
            
            # 如果有TTS服务，生成预览音频
            if self.tts_service:
                from ..models.tts_request import TTSRequest
                
                request = TTSRequest(
                    input=preview_text,
                    voice=voice_name,
                    model="tts-1",
                    response_format="mp3",
                    speed=1.0,
                    api_key=api_key
                )
                
                response = self.tts_service.generate_speech(request)
                
                if response.success:
                    # 转换为base64
                    audio_base64 = base64.b64encode(response.audio_data).decode('utf-8')
                    return {
                        "success": True,
                        "audio": audio_base64,
                        "format": "mp3",
                        "text": preview_text,
                        "voice": voice.to_dict()
                    }
                else:
                    return {
                        "success": False,
                        "error": response.error_message
                    }
            else:
                # 没有TTS服务时返回文本信息
                return {
                    "success": True,
                    "text": preview_text,
                    "voice": voice.to_dict(),
                    "message": "TTS服务未配置，无法生成音频预览"
                }
                
        except Exception as e:
            self.logger.error(f"语音预览失败: {str(e)}")
            return {
                "success": False,
                "error": f"预览失败: {str(e)}"
            }
    
    def search_voices(self, query: str, language: str = None, gender: str = None) -> List[Voice]:
        """搜索语音"""
        results = []
        
        for voices in VOICES_BY_LANGUAGE.values():
            for voice_name in voices:
                voice_gender = self._infer_gender(voice_name)
                voice = Voice.from_edge_tts_format(voice_name, voice_gender)
                
                # 检查查询条件
                match_query = not query or query.lower() in voice_name.lower()
                match_language = not language or voice.matches_language(language)
                match_gender = not gender or voice.matches_gender(gender)
                
                if match_query and match_language and match_gender:
                    results.append(voice)
        
        return results
    
    def get_voice_statistics(self) -> Dict[str, Any]:
        """获取语音统计信息"""
        stats = {
            "total_voices": 0,
            "by_language": {},
            "by_gender": {"Male": 0, "Female": 0, "Neutral": 0}
        }
        
        for category, voices in VOICES_BY_LANGUAGE.items():
            stats["by_language"][category] = len(voices)
            stats["total_voices"] += len(voices)
            
            # 统计性别分布
            for voice_name in voices:
                gender = self._infer_gender(voice_name)
                if gender in stats["by_gender"]:
                    stats["by_gender"][gender] += 1
        
        return stats
    
    def validate_voice(self, voice_name: str) -> Dict[str, Any]:
        """验证语音是否有效"""
        # 检查OpenAI语音
        if voice_name in OPENAI_VOICE_MAPPING:
            return {
                "valid": True,
                "type": "openai",
                "actual_voice": OPENAI_VOICE_MAPPING[voice_name],
                "message": f"OpenAI语音 '{voice_name}' 映射到 '{OPENAI_VOICE_MAPPING[voice_name]}'"
            }
        
        # 检查Edge-TTS语音
        for category, voices in VOICES_BY_LANGUAGE.items():
            if voice_name in voices:
                return {
                    "valid": True,
                    "type": "edge-tts",
                    "category": category,
                    "message": f"Edge-TTS语音 '{voice_name}' 来自 '{category}'"
                }
        
        return {
            "valid": False,
            "message": f"未知语音: '{voice_name}'"
        }
    
    def _infer_gender(self, voice_name: str) -> str:
        """推断语音性别"""
        voice_lower = voice_name.lower()
        
        # OpenAI语音性别映射
        openai_genders = {
            "alloy": "Neutral",
            "echo": "Male", 
            "fable": "Female",
            "onyx": "Male",
            "nova": "Female",
            "shimmer": "Female"
        }
        
        if voice_name in openai_genders:
            return openai_genders[voice_name]
        
        # 基于名称模式推断性别
        female_patterns = [
            'xiaoxiao', 'xiaohan', 'xiaomo', 'xiaorui', 'xiaoyi', 'xiaomeng', 
            'xiaoshuang', 'xiaoxuan', 'xiaoyan', 'xiaoyou', 'xiaozhen', 'xiaochen',
            'hsiaoche', 'hsiaoy', 'hiugaai', 'hiumaan', 'ava', 'emma', 'jenny', 
            'aria', 'jane', 'sara', 'nancy', 'amber', 'ana', 'ashley', 'cora',
            'elizabeth', 'michelle', 'monica', 'sonia', 'libby', 'abbi', 'bella',
            'hollie', 'maisie', 'olivia', 'nanami', 'aoi', 'mayu', 'shiori',
            'sunhi', 'seohy', 'yujin', 'katja', 'amala', 'elke', 'gisela',
            'klarissa', 'louisa', 'maja', 'tanja', 'denise', 'brigitte',
            'celeste', 'coralie', 'eloise', 'jacqueline', 'josephine', 'yvette'
        ]
        
        male_patterns = [
            'yunxi', 'yunfeng', 'yunhao', 'yunjian', 'yunxia', 'yunyang',
            'yunye', 'yunze', 'yunjhe', 'wanlung', 'andrew', 'brian', 'guy',
            'davis', 'jason', 'tony', 'eric', 'jacob', 'roger', 'steffan',
            'ryan', 'alfie', 'elliot', 'ethan', 'noah', 'oliver', 'thomas',
            'keita', 'daichi', 'naoki', 'injoon', 'bongjin', 'gookmin',
            'jimin', 'conrad', 'bernd', 'christoph', 'kasper', 'kilian',
            'klaus', 'ralf', 'henri', 'alain', 'claude', 'jerome', 'maurice',
            'yves', 'alvaro', 'arnau', 'dario', 'elias', 'nil', 'saul', 'teo'
        ]
        
        for pattern in female_patterns:
            if pattern in voice_lower:
                return "Female"
        
        for pattern in male_patterns:
            if pattern in voice_lower:
                return "Male"
        
        # 默认返回中性
        return "Neutral"
