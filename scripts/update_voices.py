#!/usr/bin/env python3
"""
简化的语音更新脚本
快速更新Edge-TTS语音列表
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import edge_tts
except ImportError:
    print("❌ 错误: 需要安装 edge-tts 库")
    print("请运行: pip install edge-tts")
    sys.exit(1)


async def update_voices():
    """更新语音列表"""
    print("🎤 正在更新Edge-TTS语音列表...")
    
    try:
        # 获取所有语音
        voices = await edge_tts.list_voices()
        
        # 按语言分组
        grouped_voices = {}
        language_map = {
            "zh-CN": "中文(简体)",
            "zh-TW": "中文(繁体-台湾)", 
            "zh-HK": "中文(繁体-香港)",
            "en-US": "English (US)",
            "en-GB": "English (UK)",
            "en-AU": "English (Australia)",
            "ja-JP": "日本語 (Japanese)",
            "ko-KR": "한국어 (Korean)",
            "de-DE": "Deutsch (German)",
            "fr-FR": "Français (French)",
            "es-ES": "Español (Spanish)",
            "it-IT": "Italiano (Italian)",
            "pt-BR": "Português (Brazil)",
            "ru-RU": "Русский (Russian)",
            "ar-SA": "العربية (Arabic)",
            "hi-IN": "हिन्दी (Hindi)",
            "th-TH": "ไทย (Thai)",
            "vi-VN": "Tiếng Việt (Vietnamese)",
            "tr-TR": "Türkçe (Turkish)",
            "pl-PL": "Polski (Polish)",
            "nl-NL": "Nederlands (Dutch)",
            "sv-SE": "Svenska (Swedish)",
            "da-DK": "Dansk (Danish)",
            "no-NO": "Norsk (Norwegian)",
            "fi-FI": "Suomi (Finnish)"
        }
        
        for voice in voices:
            locale = voice["Locale"]
            language_name = language_map.get(locale, f"{voice.get('LocaleName', locale)} ({locale})")
            
            if language_name not in grouped_voices:
                grouped_voices[language_name] = []
            
            voice_info = {
                "name": voice["Name"],
                "short_name": voice["ShortName"],
                "gender": voice["Gender"],
                "locale": voice["Locale"]
            }
            grouped_voices[language_name].append(voice_info)
        
        # 排序
        for language in grouped_voices:
            grouped_voices[language].sort(key=lambda x: x["name"])
        
        # 保存到配置文件
        config_dir = project_root / "src" / "config"
        config_dir.mkdir(exist_ok=True)
        
        output_file = config_dir / "complete_edge_voices.json"
        
        output_data = {
            "total_voices": len(voices),
            "total_languages": len(grouped_voices),
            "voices": grouped_voices
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功更新语音列表!")
        print(f"📊 总计: {len(voices)} 个语音，{len(grouped_voices)} 种语言")
        print(f"📁 保存位置: {output_file}")
        
        # 显示语言统计
        print("\n📈 语言统计:")
        for language, voice_list in sorted(grouped_voices.items()):
            print(f"  {language}: {len(voice_list)} 个语音")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(update_voices())
    sys.exit(0 if success else 1)
