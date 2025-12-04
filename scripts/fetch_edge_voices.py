#!/usr/bin/env python3
"""
Edge-TTS语音获取脚本
动态获取所有可用的Edge-TTS语音并生成JSON配置文件
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

try:
    import edge_tts
except ImportError:
    print("错误: 需要安装 edge-tts 库")
    print("请运行: pip install edge-tts")
    sys.exit(1)


class EdgeVoiceFetcher:
    """Edge-TTS语音获取器"""
    
    def __init__(self):
        self.voices = []
        self.grouped_voices = {}
        
    async def fetch_voices(self) -> List[Dict[str, Any]]:
        """获取所有Edge-TTS语音"""
        try:
            print("正在获取Edge-TTS语音列表...")
            voices = await edge_tts.list_voices()
            
            processed_voices = []
            for voice in voices:
                processed_voice = {
                    "name": voice["Name"],
                    "short_name": voice["ShortName"],
                    "gender": voice["Gender"],
                    "locale": voice["Locale"],
                    "language": voice.get("LocaleName", voice["Locale"]),
                    "country": voice.get("LocaleName", "").split(" ")[-1] if voice.get("LocaleName") else "",
                    "sample_rate": voice.get("SampleRateHertz", "24000"),
                    "voice_type": voice.get("VoiceType", "Neural")
                }
                processed_voices.append(processed_voice)
            
            self.voices = processed_voices
            print(f"成功获取 {len(processed_voices)} 个语音")
            return processed_voices
            
        except Exception as e:
            print(f"获取语音失败: {e}")
            return []
    
    def group_voices_by_language(self) -> Dict[str, List[Dict[str, Any]]]:
        """按语言分组语音"""
        grouped = {}
        
        # 语言映射
        language_map = {
            "zh-CN": "中文(简体)",
            "zh-TW": "中文(繁体-台湾)",
            "zh-HK": "中文(繁体-香港)",
            "en-US": "English (US)",
            "en-GB": "English (UK)",
            "en-AU": "English (Australia)",
            "en-CA": "English (Canada)",
            "en-IN": "English (India)",
            "ja-JP": "日本語 (Japanese)",
            "ko-KR": "한국어 (Korean)",
            "de-DE": "Deutsch (German)",
            "fr-FR": "Français (French)",
            "es-ES": "Español (Spanish)",
            "es-MX": "Español (Mexico)",
            "it-IT": "Italiano (Italian)",
            "pt-BR": "Português (Brazil)",
            "pt-PT": "Português (Portugal)",
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
            "fi-FI": "Suomi (Finnish)",
            "cs-CZ": "Čeština (Czech)",
            "hu-HU": "Magyar (Hungarian)",
            "ro-RO": "Română (Romanian)",
            "sk-SK": "Slovenčina (Slovak)",
            "bg-BG": "Български (Bulgarian)",
            "hr-HR": "Hrvatski (Croatian)",
            "sl-SI": "Slovenščina (Slovenian)",
            "et-EE": "Eesti (Estonian)",
            "lv-LV": "Latviešu (Latvian)",
            "lt-LT": "Lietuvių (Lithuanian)",
            "mt-MT": "Malti (Maltese)",
            "ga-IE": "Gaeilge (Irish)",
            "cy-GB": "Cymraeg (Welsh)",
            "is-IS": "Íslenska (Icelandic)",
            "mk-MK": "Македонски (Macedonian)",
            "sr-RS": "Српски (Serbian)",
            "bs-BA": "Bosanski (Bosnian)",
            "sq-AL": "Shqip (Albanian)",
            "eu-ES": "Euskera (Basque)",
            "ca-ES": "Català (Catalan)",
            "gl-ES": "Galego (Galician)",
            "af-ZA": "Afrikaans",
            "am-ET": "አማርኛ (Amharic)",
            "az-AZ": "Azərbaycan (Azerbaijani)",
            "bn-BD": "বাংলা (Bengali)",
            "my-MM": "မြန်မာ (Burmese)",
            "km-KH": "ខ្មែរ (Khmer)",
            "ka-GE": "ქართული (Georgian)",
            "gu-IN": "ગુજરાતી (Gujarati)",
            "he-IL": "עברית (Hebrew)",
            "id-ID": "Bahasa Indonesia",
            "jv-ID": "Basa Jawa (Javanese)",
            "kn-IN": "ಕನ್ನಡ (Kannada)",
            "kk-KZ": "Қазақ (Kazakh)",
            "ky-KG": "Кыргыз (Kyrgyz)",
            "lo-LA": "ລາວ (Lao)",
            "ml-IN": "മലയാളം (Malayalam)",
            "mr-IN": "मराठी (Marathi)",
            "mn-MN": "Монгол (Mongolian)",
            "ne-NP": "नेपाली (Nepali)",
            "ps-AF": "پښتو (Pashto)",
            "fa-IR": "فارسی (Persian)",
            "pa-IN": "ਪੰਜਾਬੀ (Punjabi)",
            "si-LK": "සිංහල (Sinhala)",
            "so-SO": "Soomaali (Somali)",
            "sw-KE": "Kiswahili (Swahili)",
            "ta-IN": "தமிழ் (Tamil)",
            "te-IN": "తెలుగు (Telugu)",
            "ur-PK": "اردو (Urdu)",
            "uz-UZ": "O'zbek (Uzbek)",
            "zu-ZA": "isiZulu (Zulu)"
        }
        
        for voice in self.voices:
            locale = voice["locale"]
            language_name = language_map.get(locale, f"{voice['language']} ({locale})")
            
            if language_name not in grouped:
                grouped[language_name] = []
            
            grouped[language_name].append(voice)
        
        # 按语音名称排序
        for language in grouped:
            grouped[language].sort(key=lambda x: x["name"])
        
        self.grouped_voices = grouped
        return grouped
    
    def save_to_json(self, output_path: str) -> bool:
        """保存到JSON文件"""
        try:
            # 创建输出目录
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 准备输出数据
            output_data = {
                "metadata": {
                    "total_voices": len(self.voices),
                    "total_languages": len(self.grouped_voices),
                    "generated_at": asyncio.get_event_loop().time(),
                    "description": "Complete Edge-TTS voices list generated automatically"
                },
                "voices_by_language": self.grouped_voices,
                "all_voices": self.voices
            }
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"语音列表已保存到: {output_path}")
            print(f"总计: {len(self.voices)} 个语音，{len(self.grouped_voices)} 种语言")
            return True
            
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False
    
    def generate_constants_file(self, output_path: str) -> bool:
        """生成Python常量文件"""
        try:
            # 创建输出目录
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 生成Python代码
            python_code = '''"""
Edge-TTS语音常量 - 自动生成
此文件由 scripts/fetch_edge_voices.py 自动生成，请勿手动修改
"""

# 所有语音列表
ALL_EDGE_TTS_VOICES = [
'''
            
            for voice in self.voices:
                python_code += f'    "{voice["name"]}",\n'
            
            python_code += ']\n\n# 按语言分组的语音\nVOICES_BY_LANGUAGE = {\n'
            
            for language, voices in self.grouped_voices.items():
                python_code += f'    "{language}": [\n'
                for voice in voices:
                    python_code += f'        "{voice["name"]}",\n'
                python_code += '    ],\n'
            
            python_code += '}\n\n# 语音详细信息\nVOICE_DETAILS = {\n'
            
            for voice in self.voices:
                python_code += f'    "{voice["name"]}": {{\n'
                python_code += f'        "short_name": "{voice["short_name"]}",\n'
                python_code += f'        "gender": "{voice["gender"]}",\n'
                python_code += f'        "locale": "{voice["locale"]}",\n'
                python_code += f'        "language": "{voice["language"]}",\n'
                python_code += f'        "voice_type": "{voice["voice_type"]}"\n'
                python_code += '    },\n'
            
            python_code += '}\n'
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            print(f"Python常量文件已生成: {output_path}")
            return True
            
        except Exception as e:
            print(f"生成Python文件失败: {e}")
            return False


async def main():
    """主函数"""
    print("Edge-TTS语音获取脚本")
    print("=" * 50)
    
    # 获取脚本目录
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    
    # 输出路径
    json_output = project_dir / "src" / "config" / "complete_edge_voices.json"
    python_output = project_dir / "src" / "config" / "edge_voices_constants.py"
    
    # 创建获取器
    fetcher = EdgeVoiceFetcher()
    
    # 获取语音
    voices = await fetcher.fetch_voices()
    if not voices:
        print("未能获取到语音列表")
        return
    
    # 分组
    grouped = fetcher.group_voices_by_language()
    print(f"语音已按 {len(grouped)} 种语言分组")
    
    # 保存JSON文件
    if fetcher.save_to_json(str(json_output)):
        print("✅ JSON文件生成成功")
    else:
        print("❌ JSON文件生成失败")
    
    # 生成Python常量文件
    if fetcher.generate_constants_file(str(python_output)):
        print("✅ Python常量文件生成成功")
    else:
        print("❌ Python常量文件生成失败")
    
    print("\n语言统计:")
    for language, voices in grouped.items():
        print(f"  {language}: {len(voices)} 个语音")


if __name__ == "__main__":
    asyncio.run(main())
