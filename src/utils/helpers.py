"""辅助函数模块"""

import re
import time
from typing import List, Iterator, Dict, Any
from datetime import datetime


def split_text_for_streaming(text: str, max_length: int = 300) -> List[str]:
    """
    将长文本分割成适合流式处理的段落，优化支持10万字长文本
    """
    if len(text) <= max_length:
        return [text]
    
    segments = []
    
    # 对于超长文本，先按章节分割
    if len(text) > 50000:  # 超过5万字时启用章节分割
        # 尝试按章节标记分割
        chapter_patterns = [
            r'第[一二三四五六七八九十\d]+章[^\n]*\n',  # 第X章
            r'第[一二三四五六七八九十\d]+节[^\n]*\n',  # 第X节
            r'Chapter\s+\d+[^\n]*\n',  # Chapter X
            r'=+[^=\n]*=+\n',  # ===标题===
            r'-+[^-\n]*-+\n',  # ---标题---
        ]
        
        for pattern in chapter_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                chapters = re.split(pattern, text, flags=re.IGNORECASE)
                if len(chapters) > 1:
                    # 找到章节分割点，递归处理每个章节
                    for i, chapter in enumerate(chapters):
                        if chapter.strip():
                            chapter_segments = split_text_for_streaming(chapter.strip(), max_length)
                            segments.extend(chapter_segments)
                    return segments
    
    # 智能分割，优先在自然断点处分割以保持连贯性
    segments = []
    current_segment = ""
    
    # 首先按段落分割
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # 如果当前段落加上新段落不超过限制，就合并
        if len(current_segment + paragraph) <= max_length:
            if current_segment:
                current_segment += "\n\n" + paragraph
            else:
                current_segment = paragraph
        else:
            # 保存当前段落
            if current_segment:
                segments.append(current_segment)
            
            # 如果单个段落太长，智能分割
            if len(paragraph) > max_length:
                segments.extend(_smart_split_paragraph(paragraph, max_length))
                current_segment = ""
            else:
                current_segment = paragraph
    
    # 添加最后一个段落
    if current_segment:
        segments.append(current_segment)
    
    # 确保没有空段落，并限制总段数
    segments = [seg.strip() for seg in segments if seg.strip()]
    
    # 对于超长文本，限制最大段数以避免内存问题
    if len(segments) > 1000:  # 最多1000段
        # 重新合并一些段落
        merged_segments = []
        current_merged = ""
        
        for segment in segments:
            if len(current_merged + segment) <= max_length * 2:  # 允许稍大的段落
                current_merged += segment + " "
            else:
                if current_merged:
                    merged_segments.append(current_merged.strip())
                current_merged = segment + " "
        
        if current_merged:
            merged_segments.append(current_merged.strip())
        
        segments = merged_segments[:1000]  # 最多保留1000段
    
    return segments


def _smart_split_paragraph(paragraph: str, max_length: int) -> List[str]:
    """
    智能分割段落，优先在自然断点处分割以保持语音连贯性
    
    Args:
        paragraph: 要分割的段落
        max_length: 最大长度
        
    Returns:
        List[str]: 分割后的段落列表
    """
    if len(paragraph) <= max_length:
        return [paragraph]
    
    segments = []
    
    # 定义分割优先级（从高到低）
    split_patterns = [
        (r'[。！？.!?]\s*', ''),           # 句号、感叹号、问号 - 最高优先级
        (r'[；;]\s*', '；'),               # 分号 - 高优先级  
        (r'[，,]\s*', '，'),               # 逗号 - 中等优先级
        (r'[：:]\s*', '：'),               # 冒号 - 中等优先级
        (r'[、]\s*', '、'),                # 顿号 - 低优先级
        (r'\s+', ' '),                     # 空格 - 最低优先级
    ]
    
    current_text = paragraph
    
    while len(current_text) > max_length:
        best_split_pos = -1
        best_suffix = ''
        
        # 按优先级尝试分割
        for pattern, suffix in split_patterns:
            # 在max_length范围内查找最后一个匹配点
            matches = list(re.finditer(pattern, current_text[:max_length]))
            if matches:
                last_match = matches[-1]
                split_pos = last_match.end()
                
                # 找到合适的分割点
                if split_pos > len(current_text) * 0.3:  # 确保不会分割得太短
                    best_split_pos = split_pos
                    best_suffix = suffix
                    break
        
        if best_split_pos > 0:
            # 在找到的位置分割
            segment = current_text[:best_split_pos].strip()
            if best_suffix and not segment.endswith(('。', '！', '？', '.', '!', '?')):
                segment += best_suffix
            
            segments.append(segment)
            current_text = current_text[best_split_pos:].strip()
        else:
            # 如果找不到合适的分割点，强制在max_length处分割
            segments.append(current_text[:max_length].strip())
            current_text = current_text[max_length:].strip()
    
    # 添加剩余部分
    if current_text:
        segments.append(current_text)
    
    return [seg for seg in segments if seg.strip()]


def parse_subtitle(content: str) -> str:
    """解析字幕文件，提取纯文本"""
    lines = content.split('\n')
    text_lines = []
    
    for line in lines:
        line = line.strip()
        # 跳过序号行
        if line.isdigit():
            continue
        # 跳过时间戳行
        if '-->' in line:
            continue
        # 跳过空行
        if not line:
            continue
        # 移除HTML标签
        line = re.sub(r'<[^>]+>', '', line)
        if line:
            text_lines.append(line)
    
    return '\n'.join(text_lines)


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def format_duration(seconds: float) -> str:
    """格式化时长"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m{secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h{minutes}m{secs:.1f}s"


def generate_filename(prefix: str = "speech", format: str = "mp3") -> str:
    """生成文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{format}"


def calculate_timeout(text_length: int) -> int:
    """根据文本长度计算超时时间，支持10万字长文本"""
    if text_length > 100000:
        return 1800  # 30分钟 - 10万字以上
    elif text_length > 50000:
        return 1200  # 20分钟 - 5-10万字
    elif text_length > 20000:
        return 900   # 15分钟 - 2-5万字
    elif text_length > 10000:
        return 600   # 10分钟 - 1-2万字
    elif text_length > 5000:
        return 300   # 5分钟 - 5千-1万字
    elif text_length > 1000:
        return 180   # 3分钟 - 1千-5千字
    else:
        return 60    # 1分钟 - 1千字以下


def get_language_from_voice(voice: str) -> str:
    """从语音名称推断语言"""
    language_map = {
        'zh-CN': 'zh-CN',
        'zh-TW': 'zh-TW', 
        'zh-HK': 'zh-HK',
        'en-US': 'en-US',
        'en-GB': 'en-GB',
        'ja-JP': 'ja-JP',
        'ko-KR': 'ko-KR',
        'de-DE': 'de-DE',
        'fr-FR': 'fr-FR',
        'es-ES': 'es-ES',
        'it-IT': 'it-IT',
        'pt-BR': 'pt-BR',
        'ru-RU': 'ru-RU',
        'ar-SA': 'ar-SA',
        'hi-IN': 'hi-IN',
    }
    
    for lang_code, lang in language_map.items():
        if voice.startswith(lang_code):
            return lang
    
    # OpenAI语音默认为英语
    openai_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
    if voice in openai_voices:
        return 'en-US'
    
    return 'en-US'  # 默认


def get_preview_text(language: str) -> str:
    """获取预览文本"""
    preview_texts = {
        "zh-CN": "你好，这是语音预览测试。欢迎使用文本转语音服务。",
        "zh-TW": "你好，這是語音預覽測試。歡迎使用文字轉語音服務。",
        "zh-HK": "你好，這是語音預覽測試。歡迎使用文字轉語音服務。",
        "en-US": "Hello, this is a voice preview test. Welcome to the text-to-speech service.",
        "en-GB": "Hello, this is a voice preview test. Welcome to the text-to-speech service.",
        "ja-JP": "こんにちは、これは音声プレビューテストです。テキスト読み上げサービスへようこそ。",
        "ko-KR": "안녕하세요, 음성 미리보기 테스트입니다. 텍스트 음성 변환 서비스에 오신 것을 환영합니다.",
        "de-DE": "Hallo, dies ist ein Sprachvorschau-Test. Willkommen beim Text-zu-Sprache-Dienst.",
        "fr-FR": "Bonjour, ceci est un test de prévisualisation vocale. Bienvenue dans le service de synthèse vocale.",
        "es-ES": "Hola, esta es una prueba de vista previa de voz. Bienvenido al servicio de texto a voz.",
        "it-IT": "Ciao, questo è un test di anteprima vocale. Benvenuto nel servizio di sintesi vocale.",
        "pt-BR": "Olá, este é um teste de pré-visualização de voz. Bem-vindo ao serviço de texto para fala.",
        "ru-RU": "Привет, это тест предварительного просмотра голоса. Добро пожаловать в службу преобразования текста в речь.",
    }
    
    return preview_texts.get(language, preview_texts["en-US"])


class Timer:
    """计时器工具类"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        return self
    
    def stop(self):
        """停止计时"""
        self.end_time = time.time()
        return self
    
    @property
    def elapsed(self) -> float:
        """获取耗时（秒）"""
        if self.start_time is None:
            return 0.0
        
        end = self.end_time or time.time()
        return end - self.start_time
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
