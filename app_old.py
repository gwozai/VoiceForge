from flask import Flask, render_template, request, send_file, jsonify, Response
import requests
import io
import json

app = Flask(__name__)

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

# 支持的音频格式
FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]

# 从工具结果中提取的部分语音列表（简化，选择常见和多样化的）
VOICES = [
    # English
    "en-US-AvaNeural", "en-US-GuyNeural", "en-US-AnaNeural", "en-US-AndrewNeural",
    "en-US-AriaNeural", "en-US-BrianNeural", "en-US-ChristopherNeural", "en-US-EmmaNeural",
    "en-US-EricNeural", "en-US-JennyNeural", "en-US-MichelleNeural", "en-US-RogerNeural",
    # Chinese
    "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-XiaohanNeural", "zh-CN-XiaomoNeural",
    "zh-CN-XiaoruiNeural", "zh-CN-XiaoyiNeural", "zh-CN-YunfengNeural", "zh-CN-YunhaoNeural",
    "zh-CN-YunjianNeural", "zh-CN-YunxiaNeural", "zh-CN-YunyangNeural", "zh-CN-YunyeNeural",
    "zh-CN-YunzeNeural",
    # Other languages (from the list)
    "af-ZA-AdriNeural", "am-ET-MekdesNeural", "ar-AE-FatimaNeural", "az-AZ-BanuNeural",
    "bg-BG-KalinaNeural", "ca-ES-JoanaNeural", "cs-CZ-VlastaNeural", "da-DK-ChristelNeural",
    "de-DE-KatjaNeural", "el-GR-AthinaNeural", "es-ES-ElviraNeural", "fi-FI-SelmaNeural",
    "fr-FR-DeniseNeural", "he-IL-HilaNeural", "hi-IN-SwaraNeural", "hu-HU-NoemiNeural",
    "it-IT-IsabellaNeural", "ja-JP-NanamiNeural", "ko-KR-SunHiNeural", "nl-NL-FennaNeural",
    "pl-PL-AgnieszkaNeural", "pt-BR-FranciscaNeural", "ru-RU-SvetlanaNeural", "sv-SE-SofieNeural",
    "tr-TR-EmelNeural", "vi-VN-HoaiMyNeural",
    # OpenAI mappings
    "alloy", "echo", "fable", "onyx", "nova", "shimmer"
    # 可以添加更多，但保持合理长度；实际中通过 /voices 获取动态列表
]

@app.route("/", methods=["GET", "POST"])
def index():
    action = request.form.get("action", "generate")
    api_key = request.form.get("api_key", DEFAULT_API_KEY)
    model = request.form.get("model", DEFAULT_MODEL)
    input_text = request.form.get("input", "")
    voice = request.form.get("voice", DEFAULT_VOICE)
    response_format = request.form.get("response_format", DEFAULT_FORMAT)
    speed = float(request.form.get("speed", DEFAULT_SPEED))
    stream_format = request.form.get("stream_format", "")  # e.g., "sse"

    if request.method == "POST" and action == "generate":
        data = {
            "model": model,
            "input": input_text,
            "voice": voice,
        }
        if response_format:
            data["response_format"] = response_format
        if speed:
            data["speed"] = speed
        if stream_format:
            data["stream_format"] = stream_format

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(API_BASE_URL + API_ENDPOINT, headers=headers, json=data, stream=bool(stream_format))
            response.raise_for_status()

            if stream_format == "sse":
                def generate():
                    audio_data = b""
                    for line in response.iter_lines():
                        if line.startswith(b"data: "):
                            chunk = line[6:]
                            audio_data += chunk
                            yield chunk  # 流式发送块
                    # 完成后，可以做些什么，但这里只是流

                return Response(generate(), mimetype=f"audio/{response_format}")
            else:
                audio_data = response.content
                return send_file(
                    io.BytesIO(audio_data),
                    mimetype=f"audio/{response_format}",
                    as_attachment=request.form.get("download", "off") == "on",
                    download_name=f"speech.{response_format}"
                )
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    return render_template("index.html", voices=VOICES, formats=FORMATS, default_api_key=DEFAULT_API_KEY,
                           default_model=DEFAULT_MODEL, default_voice=DEFAULT_VOICE, default_format=DEFAULT_FORMAT,
                           default_speed=DEFAULT_SPEED)

@app.route("/get_voices")
def get_voices():
    try:
        response = requests.get(API_BASE_URL + VOICES_ENDPOINT)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_models")
def get_models():
    try:
        response = requests.get(API_BASE_URL + MODELS_ENDPOINT)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
