from flask import Flask, render_template, request, send_file, jsonify, Response
import requests
import io
import json
import base64
import re
import logging
from datetime import datetime
import time
import os
import sqlite3
from threading import Lock

app = Flask(__name__)

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tts_generation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 数据库配置
DB_PATH = 'tts_stats.db'
db_lock = Lock()

def init_db():
    """初始化数据库"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS generation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                text_length INTEGER NOT NULL,
                voice TEXT NOT NULL,
                format TEXT NOT NULL,
                speed REAL DEFAULT 1.0,
                mode TEXT NOT NULL,
                duration REAL,
                audio_size INTEGER,
                status TEXT DEFAULT 'success',
                error_message TEXT,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        conn.commit()
    logger.info("数据库初始化完成")

# 启动时初始化数据库
init_db()

def log_generation(text_length, voice, format, speed, mode, duration=None, 
                   audio_size=None, status='success', error_message=None):
    """记录生成日志到数据库"""
    try:
        with db_lock:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('''
                    INSERT INTO generation_logs 
                    (timestamp, text_length, voice, format, speed, mode, duration, audio_size, status, error_message, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    text_length,
                    voice,
                    format,
                    speed,
                    mode,
                    duration,
                    audio_size,
                    status,
                    error_message,
                    request.remote_addr if request else None,
                    request.headers.get('User-Agent', '')[:200] if request else None
                ))
                conn.commit()
    except Exception as e:
        logger.error(f"记录日志失败: {e}")

# API 配置
API_BASE_URL = "http://117.72.56.34:5050"
API_ENDPOINT = "/v1/audio/speech"
VOICES_ENDPOINT = "/voices"
MODELS_ENDPOINT = "/models"

# 默认值
DEFAULT_API_KEY = "your_api_key_here"
DEFAULT_MODEL = "tts-1"
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
DEFAULT_FORMAT = "mp3"
DEFAULT_SPEED = 1.0
DEFAULT_LANGUAGE = "zh-CN"

# 支持的音频格式
FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]

# 支持的模型
MODELS = ["tts-1", "tts-1-hd"]

# OpenAI 语音映射（映射到 edge-tts 等效语音）
OPENAI_VOICE_MAPPING = {
    "alloy": "en-US-AvaNeural",      # 柔和中性
    "echo": "en-US-AndrewNeural",     # 回声风格
    "fable": "en-US-EmmaNeural",      # 故事讲述
    "onyx": "en-US-GuyNeural",        # 宝石般清晰
    "nova": "en-US-AriaNeural",       # 新星般明亮
    "shimmer": "en-US-JennyNeural",   # 闪烁效果
}

# 语音列表（按语言分组）
VOICES_BY_LANGUAGE = {
    "OpenAI Compatible": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
    "Chinese (zh-CN)": [
        "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-XiaohanNeural", "zh-CN-XiaomoNeural",
        "zh-CN-XiaoruiNeural", "zh-CN-XiaoyiNeural", "zh-CN-YunfengNeural", "zh-CN-YunhaoNeural",
        "zh-CN-YunjianNeural", "zh-CN-YunxiaNeural", "zh-CN-YunyangNeural", "zh-CN-YunyeNeural",
        "zh-CN-YunzeNeural", "zh-CN-XiaochenNeural", "zh-CN-XiaomengNeural", "zh-CN-XiaoshuangNeural",
        "zh-CN-XiaoxuanNeural", "zh-CN-XiaoyanNeural", "zh-CN-XiaoyouNeural", "zh-CN-XiaozhenNeural",
    ],
    "Chinese (zh-TW)": [
        "zh-TW-HsiaoChenNeural", "zh-TW-HsiaoYuNeural", "zh-TW-YunJheNeural",
    ],
    "Chinese (zh-HK)": [
        "zh-HK-HiuGaaiNeural", "zh-HK-HiuMaanNeural", "zh-HK-WanLungNeural",
    ],
    "English (en-US)": [
        "en-US-AvaNeural", "en-US-AndrewNeural", "en-US-EmmaNeural", "en-US-BrianNeural",
        "en-US-JennyNeural", "en-US-GuyNeural", "en-US-AriaNeural", "en-US-DavisNeural",
        "en-US-JaneNeural", "en-US-JasonNeural", "en-US-SaraNeural", "en-US-TonyNeural",
        "en-US-NancyNeural", "en-US-AmberNeural", "en-US-AnaNeural", "en-US-AshleyNeural",
        "en-US-BrandonNeural", "en-US-ChristopherNeural", "en-US-CoraNeural", "en-US-ElizabethNeural",
        "en-US-EricNeural", "en-US-JacobNeural", "en-US-MichelleNeural", "en-US-MonicaNeural",
        "en-US-RogerNeural", "en-US-SteffanNeural",
    ],
    "English (en-GB)": [
        "en-GB-SoniaNeural", "en-GB-RyanNeural", "en-GB-LibbyNeural", "en-GB-AbbiNeural",
        "en-GB-AlfieNeural", "en-GB-BellaNeural", "en-GB-ElliotNeural", "en-GB-EthanNeural",
        "en-GB-HollieNeural", "en-GB-MaisieNeural", "en-GB-NoahNeural", "en-GB-OliverNeural",
        "en-GB-OliviaNeural", "en-GB-ThomasNeural",
    ],
    "Japanese (ja-JP)": [
        "ja-JP-NanamiNeural", "ja-JP-KeitaNeural", "ja-JP-AoiNeural", "ja-JP-DaichiNeural",
        "ja-JP-MayuNeural", "ja-JP-NaokiNeural", "ja-JP-ShioriNeural",
    ],
    "Korean (ko-KR)": [
        "ko-KR-SunHiNeural", "ko-KR-InJoonNeural", "ko-KR-BongJinNeural", "ko-KR-GookMinNeural",
        "ko-KR-JiMinNeural", "ko-KR-SeoHyeonNeural", "ko-KR-SoonBokNeural", "ko-KR-YuJinNeural",
    ],
    "German (de-DE)": [
        "de-DE-KatjaNeural", "de-DE-ConradNeural", "de-DE-AmalaNeural", "de-DE-BerndNeural",
        "de-DE-ChristophNeural", "de-DE-ElkeNeural", "de-DE-GiselaNeural", "de-DE-KasperNeural",
        "de-DE-KillianNeural", "de-DE-KlarissaNeural", "de-DE-KlausNeural", "de-DE-LouisaNeural",
        "de-DE-MajaNeural", "de-DE-RalfNeural", "de-DE-TanjaNeural",
    ],
    "French (fr-FR)": [
        "fr-FR-DeniseNeural", "fr-FR-HenriNeural", "fr-FR-AlainNeural", "fr-FR-BrigitteNeural",
        "fr-FR-CelesteNeural", "fr-FR-ClaudeNeural", "fr-FR-CoralieNeural", "fr-FR-EloiseNeural",
        "fr-FR-JacquelineNeural", "fr-FR-JeromeNeural", "fr-FR-JosephineNeural", "fr-FR-MauriceNeural",
        "fr-FR-YvesNeural", "fr-FR-YvetteNeural",
    ],
    "Spanish (es-ES)": [
        "es-ES-ElviraNeural", "es-ES-AlvaroNeural", "es-ES-AbrilNeural", "es-ES-ArnauNeural",
        "es-ES-DarioNeural", "es-ES-EliasNeural", "es-ES-EstrellaNeural", "es-ES-IreneNeural",
        "es-ES-LaiaNeural", "es-ES-LiaNeural", "es-ES-NilNeural", "es-ES-SaulNeural",
        "es-ES-TeoNeural", "es-ES-TrianaNeural", "es-ES-VeraNeural",
    ],
    "Italian (it-IT)": [
        "it-IT-IsabellaNeural", "it-IT-DiegoNeural", "it-IT-BenignoNeural", "it-IT-CalimeroNeural",
        "it-IT-CataldoNeural", "it-IT-ElsaNeural", "it-IT-FabiolaNeural", "it-IT-FiammaNeural",
        "it-IT-GianniNeural", "it-IT-ImeldaNeural", "it-IT-IrmaNeural", "it-IT-LisandroNeural",
        "it-IT-PalmiraNeural", "it-IT-PierinaNeural", "it-IT-RinaldoNeural",
    ],
    "Portuguese (pt-BR)": [
        "pt-BR-FranciscaNeural", "pt-BR-AntonioNeural", "pt-BR-BrendaNeural", "pt-BR-DonatoNeural",
        "pt-BR-ElzaNeural", "pt-BR-FabioNeural", "pt-BR-GiovannaNeural", "pt-BR-HumbertoNeural",
        "pt-BR-JulioNeural", "pt-BR-LeilaNeural", "pt-BR-LeticiaNeural", "pt-BR-ManuelaNeural",
        "pt-BR-NicolauNeural", "pt-BR-ValerioNeural", "pt-BR-YaraNeural",
    ],
    "Russian (ru-RU)": [
        "ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural", "ru-RU-DariyaNeural",
    ],
    "Arabic (ar-SA)": [
        "ar-SA-ZariyahNeural", "ar-SA-HamedNeural",
    ],
    "Hindi (hi-IN)": [
        "hi-IN-SwaraNeural", "hi-IN-MadhurNeural",
    ],
    "Other Languages": [
        "af-ZA-AdriNeural", "am-ET-MekdesNeural", "ar-AE-FatimaNeural", "az-AZ-BanuNeural",
        "bg-BG-KalinaNeural", "ca-ES-JoanaNeural", "cs-CZ-VlastaNeural", "da-DK-ChristelNeural",
        "el-GR-AthinaNeural", "fi-FI-SelmaNeural", "he-IL-HilaNeural", "hu-HU-NoemiNeural",
        "id-ID-GadisNeural", "ms-MY-YasminNeural", "nl-NL-FennaNeural", "no-NO-PernilleNeural",
        "pl-PL-AgnieszkaNeural", "ro-RO-AlinaNeural", "sk-SK-ViktoriaNeural", "sl-SI-PetraNeural",
        "sv-SE-SofieNeural", "th-TH-PremwadeeNeural", "tr-TR-EmelNeural", "uk-UA-PolinaNeural",
        "vi-VN-HoaiMyNeural",
    ],
}

# 扁平化语音列表
VOICES = []
for voices in VOICES_BY_LANGUAGE.values():
    VOICES.extend(voices)


@app.route("/", methods=["GET"])
def index():
    """主页面"""
    return render_template(
        "index.html",
        voices_by_language=VOICES_BY_LANGUAGE,
        voices=VOICES,
        formats=FORMATS,
        models=MODELS,
        openai_voices=list(OPENAI_VOICE_MAPPING.keys()),
        default_api_key=DEFAULT_API_KEY,
        default_model=DEFAULT_MODEL,
        default_voice=DEFAULT_VOICE,
        default_format=DEFAULT_FORMAT,
        default_speed=DEFAULT_SPEED,
        default_language=DEFAULT_LANGUAGE,
        api_base_url=API_BASE_URL,
    )


@app.route("/api/generate", methods=["POST"])
def generate_speech():
    """生成语音 API"""
    try:
        # 获取请求数据
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        api_key = data.get("api_key", DEFAULT_API_KEY)
        model = data.get("model", DEFAULT_MODEL)
        input_text = data.get("input", "")
        voice = data.get("voice", DEFAULT_VOICE)
        response_format = data.get("response_format", DEFAULT_FORMAT)
        speed = float(data.get("speed", DEFAULT_SPEED))
        stream_format = data.get("stream_format", "")
        
        if not input_text:
            return jsonify({"error": "Input text is required"}), 400
        
        # 构建 API 请求
        api_data = {
            "model": model,
            "input": input_text,
            "voice": voice,
        }
        if response_format:
            api_data["response_format"] = response_format
        if speed:
            api_data["speed"] = speed
        if stream_format:
            api_data["stream_format"] = stream_format
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # 发送请求
        print(f"[DEBUG] Sending request to {API_BASE_URL + API_ENDPOINT}")
        print(f"[DEBUG] Data: {api_data}")
        
        # 根据文本长度调整超时时间
        text_length = len(input_text)
        if text_length > 10000:
            timeout = 300  # 5分钟
        elif text_length > 5000:
            timeout = 180  # 3分钟
        elif text_length > 1000:
            timeout = 120  # 2分钟
        else:
            timeout = 60   # 1分钟
        
        print(f"[DEBUG] Text length: {text_length}, Timeout: {timeout}s")
        
        # 记录生成开始
        generation_start = time.time()
        logger.info(f"TTS生成开始 | 字符数: {text_length} | 语音: {voice} | 格式: {response_format} | 模式: {'流式' if stream_format else '普通'}")
        
        if stream_format == "sse":
            # 真正的流式响应 - 分段生成
            def generate_streaming():
                try:
                    # 将长文本分段处理
                    text_segments = split_text_for_streaming(input_text)
                    print(f"[DEBUG] Split text into {len(text_segments)} segments")
                    
                    for i, segment in enumerate(text_segments):
                        print(f"[DEBUG] Processing segment {i+1}/{len(text_segments)}: {segment[:50]}...")
                        
                        # 为每个段落生成音频
                        segment_data = {
                            "model": model,
                            "input": segment,
                            "voice": voice,
                            "response_format": response_format,
                            "speed": speed
                        }
                        
                        try:
                            segment_response = requests.post(
                                API_BASE_URL + API_ENDPOINT,
                                headers=headers,
                                json=segment_data,
                                timeout=30  # 减少单段超时时间
                            )
                            
                            if segment_response.status_code == 200:
                                # 分块发送音频数据，使用更大的块以减少网络开销
                                audio_data = segment_response.content
                                chunk_size = 16384  # 16KB chunks，更大的块
                                
                                print(f"[DEBUG] Segment {i+1} generated: {len(audio_data)} bytes")
                                
                                for j in range(0, len(audio_data), chunk_size):
                                    chunk = audio_data[j:j + chunk_size]
                                    yield chunk
                                    
                                # 在段落之间添加小延迟，让前端有时间处理
                                import time
                                time.sleep(0.1)
                                
                            else:
                                print(f"[DEBUG] Segment {i+1} failed: {segment_response.status_code}")
                                # 如果某个段落失败，继续处理下一个
                                continue
                                
                        except requests.exceptions.Timeout:
                            print(f"[DEBUG] Segment {i+1} timeout, skipping...")
                            continue
                        except Exception as e:
                            print(f"[DEBUG] Segment {i+1} error: {e}")
                            continue
                            
                except Exception as e:
                    print(f"[DEBUG] Streaming error: {e}")
                    yield b""  # 发送空数据表示结束
            
            return Response(
                generate_streaming(),
                mimetype=f"audio/{response_format}",
                headers={
                    "Content-Type": f"audio/{response_format}",
                    "Transfer-Encoding": "chunked",
                    "Cache-Control": "no-cache",
                }
            )
        else:
            # 非流式响应 - 调用原始 API
            response = requests.post(
                API_BASE_URL + API_ENDPOINT,
                headers=headers,
                json=api_data,
                timeout=timeout
            )
            
            if response.status_code != 200:
                print(f"[DEBUG] Error response: {response.status_code} - {response.text[:500]}")
            
            response.raise_for_status()
            
            audio_data = response.content
            
            # 记录生成完成
            generation_duration = time.time() - generation_start
            audio_size = len(audio_data)
            logger.info(f"TTS生成完成 | 耗时: {generation_duration:.2f}s | 字符数: {text_length} | 音频大小: {audio_size/1024:.1f}KB | 语音: {voice}")
            
            # 持久化到数据库
            log_generation(
                text_length=text_length,
                voice=voice,
                format=response_format,
                speed=speed,
                mode='普通',
                duration=generation_duration,
                audio_size=audio_size,
                status='success'
            )
            
            return send_file(
                io.BytesIO(audio_data),
                mimetype=f"audio/{response_format}",
                as_attachment=data.get("download") == "true",
                download_name=f"speech.{response_format}"
            )
    
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_msg = e.response.json().get('error', str(e))
            except:
                error_msg = e.response.text or str(e)
        return jsonify({"error": error_msg}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/voices", methods=["GET", "POST"])
def get_voices():
    """获取所有可用语音"""
    try:
        # 获取 API Key
        if request.method == "POST":
            data = request.get_json() or {}
            api_key = data.get("api_key", DEFAULT_API_KEY)
        else:
            api_key = request.args.get("api_key", DEFAULT_API_KEY)
        
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(API_BASE_URL + VOICES_ENDPOINT, headers=headers, timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/models", methods=["GET", "POST"])
def get_models():
    """获取所有可用模型"""
    try:
        # 获取 API Key
        if request.method == "POST":
            data = request.get_json() or {}
            api_key = data.get("api_key", DEFAULT_API_KEY)
        else:
            api_key = request.args.get("api_key", DEFAULT_API_KEY)
        
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(API_BASE_URL + MODELS_ENDPOINT, headers=headers, timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/voice_mapping", methods=["GET"])
def get_voice_mapping():
    """获取 OpenAI 语音映射"""
    return jsonify(OPENAI_VOICE_MAPPING)


@app.route("/api/voices_by_language", methods=["GET"])
def get_voices_by_language():
    """获取按语言分组的语音列表"""
    return jsonify(VOICES_BY_LANGUAGE)


@app.route("/api/test_connection", methods=["POST"])
def test_connection():
    """测试 API 连接"""
    try:
        data = request.get_json() or {}
        api_key = data.get("api_key", DEFAULT_API_KEY)
        
        # 测试获取模型列表
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(API_BASE_URL + MODELS_ENDPOINT, headers=headers, timeout=10)
        response.raise_for_status()
        
        return jsonify({
            "success": True,
            "message": "Connection successful",
            "models": response.json()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/api/preview_voice", methods=["POST"])
def preview_voice():
    """预览语音样本"""
    try:
        data = request.get_json() or {}
        api_key = data.get("api_key", DEFAULT_API_KEY)
        voice = data.get("voice", DEFAULT_VOICE)
        language = data.get("language", "en-US")
        
        # 根据语言选择预览文本
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
        
        # 从语音名称推断语言
        if voice.startswith("zh-CN"):
            language = "zh-CN"
        elif voice.startswith("zh-TW"):
            language = "zh-TW"
        elif voice.startswith("zh-HK"):
            language = "zh-HK"
        elif voice.startswith("en-US"):
            language = "en-US"
        elif voice.startswith("en-GB"):
            language = "en-GB"
        elif voice.startswith("ja-JP"):
            language = "ja-JP"
        elif voice.startswith("ko-KR"):
            language = "ko-KR"
        elif voice.startswith("de-DE"):
            language = "de-DE"
        elif voice.startswith("fr-FR"):
            language = "fr-FR"
        elif voice.startswith("es-ES"):
            language = "es-ES"
        elif voice.startswith("it-IT"):
            language = "it-IT"
        elif voice.startswith("pt-BR"):
            language = "pt-BR"
        elif voice.startswith("ru-RU"):
            language = "ru-RU"
        elif voice in OPENAI_VOICE_MAPPING:
            language = "en-US"
        
        preview_text = preview_texts.get(language, preview_texts["en-US"])
        
        # 生成预览音频
        api_data = {
            "model": "tts-1",
            "input": preview_text,
            "voice": voice,
            "response_format": "mp3",
            "speed": 1.0,
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(
            API_BASE_URL + API_ENDPOINT,
            headers=headers,
            json=api_data,
            timeout=30
        )
        response.raise_for_status()
        
        # 返回 base64 编码的音频
        audio_base64 = base64.b64encode(response.content).decode('utf-8')
        return jsonify({
            "success": True,
            "audio": audio_base64,
            "format": "mp3",
            "text": preview_text,
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# 从URL加载文本内容
@app.route("/api/fetch_url", methods=["POST"])
def fetch_url_content():
    """代理获取远程URL的文本内容（避免CORS问题）"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({"success": False, "error": "URL不能为空"}), 400
        
        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            return jsonify({"success": False, "error": "无效的URL格式"}), 400
        
        # 发送请求获取内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 尝试检测编码
        content_type = response.headers.get('content-type', '')
        if 'charset=' in content_type:
            encoding = content_type.split('charset=')[-1].split(';')[0].strip()
        else:
            # 尝试自动检测
            encoding = response.apparent_encoding or 'utf-8'
        
        try:
            text = response.content.decode(encoding)
        except:
            text = response.content.decode('utf-8', errors='ignore')
        
        # 清理文本
        text = text.strip()
        
        return jsonify({
            "success": True,
            "text": text,
            "length": len(text),
            "url": url
        })
        
    except requests.exceptions.Timeout:
        return jsonify({"success": False, "error": "请求超时，请检查URL是否可访问"}), 408
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"请求失败: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# 兼容旧的路由
@app.route("/get_voices")
def get_voices_legacy():
    return get_voices()


@app.route("/get_models")
def get_models_legacy():
    return get_models()


def split_text_for_streaming(text, max_length=300):
    """
    将长文本分割成适合流式处理的段落
    """
    if len(text) <= max_length:
        return [text]
    
    segments = []
    
    # 首先按段落分割
    paragraphs = text.split('\n\n')
    current_segment = ""
    
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
            
            # 如果单个段落太长，需要进一步分割
            if len(paragraph) > max_length:
                # 按句子分割
                sentences = re.split(r'[。！？.!?]\s*', paragraph)
                temp_segment = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    # 添加标点符号
                    if not sentence.endswith(('。', '！', '？', '.', '!', '?')):
                        if any(char in sentence for char in '，,；;：:'):
                            sentence += '。'
                        else:
                            sentence += '。'
                    
                    if len(temp_segment + sentence) <= max_length:
                        temp_segment += sentence
                    else:
                        if temp_segment:
                            segments.append(temp_segment)
                        temp_segment = sentence
                
                if temp_segment:
                    current_segment = temp_segment
                else:
                    current_segment = ""
            else:
                current_segment = paragraph
    
    # 添加最后一个段落
    if current_segment:
        segments.append(current_segment)
    
    # 确保没有空段落
    segments = [seg.strip() for seg in segments if seg.strip()]
    
    print(f"[DEBUG] Text split into {len(segments)} segments:")
    for i, seg in enumerate(segments):
        print(f"[DEBUG] Segment {i+1}: {len(seg)} chars - {seg[:100]}...")
    
    return segments


# 记录生成统计（供前端调用，主要用于流式模式）
@app.route("/api/log_generation", methods=["POST"])
def api_log_generation():
    """前端调用来记录生成统计"""
    try:
        data = request.get_json()
        log_generation(
            text_length=data.get('text_length', 0),
            voice=data.get('voice', 'unknown'),
            format=data.get('format', 'mp3'),
            speed=data.get('speed', 1.0),
            mode=data.get('mode', 'unknown'),
            duration=data.get('duration'),
            audio_size=data.get('audio_size'),
            status=data.get('status', 'success'),
            error_message=data.get('error_message')
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# 获取生成统计
@app.route("/api/stats")
def get_stats():
    """获取生成统计数据"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            
            # 总体统计
            summary = conn.execute('''
                SELECT 
                    COUNT(*) as total_count,
                    SUM(text_length) as total_chars,
                    SUM(duration) as total_duration,
                    SUM(audio_size) as total_size,
                    AVG(duration) as avg_duration,
                    AVG(text_length) as avg_chars
                FROM generation_logs
                WHERE status = 'success'
            ''').fetchone()
            
            # 按语音统计
            voice_stats = conn.execute('''
                SELECT voice, COUNT(*) as count, SUM(text_length) as chars
                FROM generation_logs
                WHERE status = 'success'
                GROUP BY voice
                ORDER BY count DESC
                LIMIT 10
            ''').fetchall()
            
            # 按日期统计
            daily_stats = conn.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as count, SUM(text_length) as chars
                FROM generation_logs
                WHERE status = 'success'
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            ''').fetchall()
            
            # 最近记录
            recent_logs = conn.execute('''
                SELECT * FROM generation_logs
                ORDER BY timestamp DESC
                LIMIT 50
            ''').fetchall()
            
            return jsonify({
                "success": True,
                "summary": {
                    "total_count": summary['total_count'] or 0,
                    "total_chars": summary['total_chars'] or 0,
                    "total_duration": round(summary['total_duration'] or 0, 2),
                    "total_size_mb": round((summary['total_size'] or 0) / 1024 / 1024, 2),
                    "avg_duration": round(summary['avg_duration'] or 0, 2),
                    "avg_chars": round(summary['avg_chars'] or 0, 0)
                },
                "voice_stats": [dict(row) for row in voice_stats],
                "daily_stats": [dict(row) for row in daily_stats],
                "recent_logs": [dict(row) for row in recent_logs]
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# 导出统计数据
@app.route("/api/stats/export")
def export_stats():
    """导出统计数据为CSV"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute('SELECT * FROM generation_logs ORDER BY timestamp DESC')
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            # 生成CSV
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(columns)
            writer.writerows(rows)
            
            csv_data = output.getvalue()
            
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=tts_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
