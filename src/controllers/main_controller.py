"""主控制器"""

from flask import Blueprint, render_template, current_app
from ..config.constants import VOICES_BY_LANGUAGE, VOICES, SUPPORTED_FORMATS, SUPPORTED_MODELS

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    """主页面"""
    config = current_app.config.get('VOICEFORGE_CONFIG')
    
    return render_template(
        "index.html",
        voices_by_language=VOICES_BY_LANGUAGE,
        voices=VOICES,
        formats=SUPPORTED_FORMATS,
        models=SUPPORTED_MODELS,
        openai_voices=['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
        default_api_key=config.get('DEFAULT_API_KEY') if config else 'your_api_key_here',
        default_model=config.get('DEFAULT_MODEL') if config else 'tts-1',
        default_voice=config.get('DEFAULT_VOICE') if config else 'zh-CN-XiaoxiaoNeural',
        default_format=config.get('DEFAULT_FORMAT') if config else 'mp3',
        default_speed=config.get('DEFAULT_SPEED') if config else 1.0,
        default_language=config.get('DEFAULT_LANGUAGE') if config else 'zh-CN',
        api_base_url=config.get('API_BASE_URL') if config else 'http://117.72.56.34:5050',
    )
