"""语音控制器"""

from flask import Blueprint, jsonify
from ..config.constants import VOICES_BY_LANGUAGE

voice_bp = Blueprint('voice', __name__)


@voice_bp.route("/list")
def list_voices():
    """获取语音列表"""
    return jsonify({
        "success": True,
        "voices": VOICES_BY_LANGUAGE
    })


@voice_bp.route("/preview", methods=["POST"])
def preview_voice():
    """语音预览 - 简化版本"""
    return jsonify({
        "success": True,
        "message": "Voice preview not yet implemented in OOP version"
    })
