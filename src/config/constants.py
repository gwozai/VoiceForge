"""常量定义"""

# 支持的音频格式
SUPPORTED_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]

# 支持的模型
SUPPORTED_MODELS = ["tts-1", "tts-1-hd"]

# OpenAI 语音映射
OPENAI_VOICE_MAPPING = {
    "alloy": "en-US-AvaNeural",
    "echo": "en-US-AndrewNeural", 
    "fable": "en-US-EmmaNeural",
    "onyx": "en-US-GuyNeural",
    "nova": "en-US-AriaNeural",
    "shimmer": "en-US-JennyNeural",
}

# 语音列表（按语言分组）
VOICES_BY_LANGUAGE = {
    "OpenAI Compatible": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
    "Chinese (zh-CN)": [
        "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-XiaohanNeural", 
        "zh-CN-XiaomoNeural", "zh-CN-XiaoruiNeural", "zh-CN-XiaoyiNeural",
        "zh-CN-YunfengNeural", "zh-CN-YunhaoNeural", "zh-CN-YunjianNeural",
        "zh-CN-YunxiaNeural", "zh-CN-YunyangNeural", "zh-CN-YunyeNeural",
        "zh-CN-YunzeNeural", "zh-CN-XiaochenNeural", "zh-CN-XiaomengNeural",
        "zh-CN-XiaoshuangNeural", "zh-CN-XiaoxuanNeural", "zh-CN-XiaoyanNeural",
        "zh-CN-XiaoyouNeural", "zh-CN-XiaozhenNeural",
    ],
    "Chinese (zh-TW)": [
        "zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural",
    ],
    "Chinese (zh-HK)": [
        "zh-HK-HiuGaaiNeural", "zh-HK-HiuMaanNeural", "zh-HK-WanLungNeural",
    ],
    "English (en-US)": [
        "en-US-AvaNeural", "en-US-AndrewNeural", "en-US-EmmaNeural", 
        "en-US-BrianNeural", "en-US-JennyNeural", "en-US-GuyNeural",
        "en-US-AriaNeural", "en-US-DavisNeural", "en-US-JaneNeural",
        "en-US-JasonNeural", "en-US-SaraNeural", "en-US-TonyNeural",
        "en-US-NancyNeural", "en-US-AmberNeural", "en-US-AnaNeural",
        "en-US-AshleyNeural", "en-US-BrandonNeural", "en-US-ChristopherNeural",
        "en-US-CoraNeural", "en-US-ElizabethNeural", "en-US-EricNeural",
        "en-US-JacobNeural", "en-US-MichelleNeural", "en-US-MonicaNeural",
        "en-US-RogerNeural", "en-US-SteffanNeural",
    ],
    "English (en-GB)": [
        "en-GB-SoniaNeural", "en-GB-RyanNeural", "en-GB-LibbyNeural",
        "en-GB-AbbiNeural", "en-GB-AlfieNeural", "en-GB-BellaNeural",
        "en-GB-ElliotNeural", "en-GB-EthanNeural", "en-GB-HollieNeural",
        "en-GB-MaisieNeural", "en-GB-NoahNeural", "en-GB-OliverNeural",
        "en-GB-OliviaNeural", "en-GB-ThomasNeural",
    ],
    # 可以继续添加更多语言...
}

# 扁平化语音列表
VOICES = []
for voices in VOICES_BY_LANGUAGE.values():
    VOICES.extend(voices)

# 默认值
DEFAULT_VALUES = {
    'API_KEY': 'your_api_key_here',
    'MODEL': 'tts-1',
    'VOICE': 'zh-CN-XiaoxiaoNeural',
    'FORMAT': 'mp3',
    'SPEED': 1.0,
    'LANGUAGE': 'zh-CN',
}

# API 端点
API_ENDPOINTS = {
    'SPEECH': '/v1/audio/speech',
    'VOICES': '/voices',
    'MODELS': '/models',
}

# 文件类型限制
ALLOWED_FILE_TYPES = ['.txt', '.md', '.text', '.srt', '.vtt', '.json']

# 流式传输配置
STREAMING_CONFIG = {
    'BUFFER_THRESHOLD': 20480,  # 20KB
    'CHUNK_SIZE': 16384,        # 16KB
    'MAX_SEGMENT_LENGTH': 300,  # 字符
}

# 日志配置
LOG_CONFIG = {
    'FORMAT': '%(asctime)s - %(levelname)s - %(message)s',
    'DEFAULT_LEVEL': 'INFO',
    'DEFAULT_FILE': 'tts_generation.log',
}
