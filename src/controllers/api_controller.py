"""API控制器"""

import io
import json
from flask import Blueprint, request, jsonify, current_app, Response, send_file

from ..services.tts_service import TTSService
from ..services.voice_service import VoiceService
from ..services.file_service import FileService
from ..services.history_service import HistoryService
from ..models.tts_request import TTSRequest
from ..utils.helpers import generate_filename

api_bp = Blueprint('api', __name__)


def get_services():
    """获取服务实例"""
    config = current_app.config.get('VOICEFORGE_CONFIG')
    db_manager = current_app.config.get('DB_MANAGER')
    
    tts_service = TTSService(config, db_manager)
    voice_service = VoiceService(config, tts_service)
    file_service = FileService()
    history_service = HistoryService(db_manager)
    
    return tts_service, voice_service, file_service, history_service


@api_bp.route("/test_connection", methods=["POST"])
def test_connection():
    """测试API连接"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({
                "success": False,
                "message": "API Key不能为空"
            }), 400
        
        tts_service, _, _, _ = get_services()
        result = tts_service.test_connection(api_key)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"测试连接失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"连接测试失败: {str(e)}"
        }), 500


@api_bp.route("/models", methods=["POST"])
def get_models():
    """获取可用模型"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({"error": "API Key不能为空"}), 400
        
        tts_service, _, _, _ = get_services()
        models_data = tts_service.get_models(api_key)
        
        return jsonify(models_data)
        
    except Exception as e:
        current_app.logger.error(f"获取模型失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/voices", methods=["GET"])
def get_voices():
    """获取语音列表"""
    try:
        _, voice_service, _, _ = get_services()
        voices = voice_service.get_all_voices()
        
        return jsonify({
            "success": True,
            "voices": {category: [voice.to_dict() for voice in voice_list] 
                      for category, voice_list in voices.items()}
        })
        
    except Exception as e:
        current_app.logger.error(f"获取语音列表失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/preview_voice", methods=["POST"])
def preview_voice():
    """预览语音"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        voice = data.get('voice', '')
        api_key = data.get('api_key', '')
        custom_text = data.get('text', '')
        
        if not voice:
            return jsonify({"error": "语音参数不能为空"}), 400
        
        if not api_key:
            return jsonify({"error": "API Key不能为空"}), 400
        
        _, voice_service, _, _ = get_services()
        result = voice_service.preview_voice(voice, api_key, custom_text)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"语音预览失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/generate", methods=["POST"])
def generate_speech():
    """生成语音API"""
    try:
        # 获取请求数据
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # 创建TTS请求对象
        tts_request = TTSRequest(
            input=data.get('input', ''),
            voice=data.get('voice', ''),
            model=data.get('model', 'tts-1'),
            response_format=data.get('response_format', 'mp3'),
            speed=float(data.get('speed', 1.0)),
            api_key=data.get('api_key', ''),
            stream_format=data.get('stream_format', '')
        )
        
        tts_service, _, _, _ = get_services()
        
        # 检查是否是流式请求
        if tts_request.is_streaming:
            return generate_streaming_speech_response(tts_service, tts_request)
        else:
            return generate_normal_speech_response(tts_service, tts_request)
        
    except Exception as e:
        current_app.logger.error(f"生成语音失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


def generate_normal_speech_response(tts_service: TTSService, tts_request: TTSRequest):
    """生成普通语音响应"""
    response = tts_service.generate_speech(tts_request)
    
    if response.success:
        # 返回音频文件
        audio_io = io.BytesIO(response.audio_data)
        filename = generate_filename("speech", tts_request.response_format)
        
        return send_file(
            audio_io,
            mimetype=f'audio/{tts_request.response_format}',
            as_attachment=True,
            download_name=filename
        )
    else:
        return jsonify({
            "error": response.error_message
        }), response.status_code or 500


def generate_streaming_speech_response(tts_service: TTSService, tts_request: TTSRequest):
    """生成流式语音响应"""
    def generate():
        try:
            for chunk in tts_service.generate_streaming_speech(tts_request):
                yield chunk
        except Exception as e:
            current_app.logger.error(f"流式生成失败: {str(e)}")
            # 在流式响应中，我们无法返回JSON错误，只能记录日志
    
    return Response(
        generate(),
        mimetype=f'audio/{tts_request.response_format}',
        headers={
            'Content-Disposition': f'attachment; filename="{generate_filename("speech", tts_request.response_format)}"'
        }
    )


@api_bp.route("/fetch_url", methods=["POST"])
def fetch_url():
    """获取URL内容"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        url = data.get('url', '')
        
        if not url:
            return jsonify({"error": "URL不能为空"}), 400
        
        _, _, file_service, _ = get_services()
        result = file_service.fetch_url_content(url)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"获取URL内容失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/queue_status", methods=["GET"])
def queue_status():
    """获取队列状态"""
    try:
        from ..utils.queue_manager import get_queue_manager
        queue_manager = get_queue_manager()
        status = queue_manager.get_status()
        
        return jsonify({
            "success": True,
            "status": status
        })
        
    except Exception as e:
        current_app.logger.error(f"获取队列状态失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/log_generation", methods=["POST"])
def log_generation():
    """记录生成日志"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        db_manager = current_app.config.get('DB_MANAGER')
        if not db_manager:
            return jsonify({"error": "数据库管理器未配置"}), 500
        
        log_id = db_manager.log_generation(
            text_length=int(data.get('text_length', 0)),
            voice=data.get('voice', ''),
            format=data.get('format', ''),
            speed=float(data.get('speed', 1.0)),
            mode=data.get('mode', ''),
            duration=float(data.get('duration', 0)) if data.get('duration') else None,
            audio_size=int(data.get('audio_size', 0)) if data.get('audio_size') else None,
            status=data.get('status', 'success'),
            error_message=data.get('error_message'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            "success": True,
            "log_id": log_id
        })
        
    except Exception as e:
        current_app.logger.error(f"记录日志失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/stats", methods=["GET"])
def get_stats():
    """获取统计数据"""
    try:
        _, _, _, history_service = get_services()
        stats = history_service.get_generation_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        current_app.logger.error(f"获取统计数据失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/stats/export", methods=["GET"])
def export_stats():
    """导出统计数据"""
    try:
        _, _, _, history_service = get_services()
        result = history_service.export_logs_csv()
        
        if result["success"]:
            # 创建CSV内容
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=result["data"]["columns"])
            writer.writeheader()
            writer.writerows(result["data"]["rows"])
            
            # 转换为字节流
            csv_data = output.getvalue().encode('utf-8-sig')  # 使用BOM以支持Excel
            csv_io = io.BytesIO(csv_data)
            
            return send_file(
                csv_io,
                mimetype='text/csv',
                as_attachment=True,
                download_name='tts_generation_logs.csv'
            )
        else:
            return jsonify(result), 500
        
    except Exception as e:
        current_app.logger.error(f"导出统计数据失败: {str(e)}")
        return jsonify({"error": str(e)}), 500
