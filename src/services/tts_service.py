"""TTS核心服务"""

import requests
import time
import io
from typing import Iterator, Optional, Dict, Any
from flask import current_app

from ..models.tts_request import TTSRequest, TTSResponse, StreamingTTSResponse
from ..utils.logger import LoggerMixin
from ..utils.helpers import split_text_for_streaming, calculate_timeout, Timer
from ..utils.validators import RequestValidator


class TTSService(LoggerMixin):
    """TTS核心服务类"""
    
    def __init__(self, config=None, db_manager=None):
        self.config = config or current_app.config.get('VOICEFORGE_CONFIG')
        self.db_manager = db_manager or current_app.config.get('DB_MANAGER')
        self.validator = RequestValidator()
        
        # API配置
        self.api_base_url = self.config.get('API_BASE_URL')
        self.api_endpoint = self.config.get('API_ENDPOINT')
        self.models_endpoint = self.config.get('MODELS_ENDPOINT')
        
    def generate_speech(self, request: TTSRequest) -> TTSResponse:
        """生成语音"""
        try:
            # 验证请求
            validation_result = self.validator.validate_tts_request(request.to_dict())
            if not validation_result['valid']:
                return TTSResponse(
                    success=False,
                    error_message='; '.join(validation_result['errors'])
                )
            
            # 记录开始时间
            timer = Timer().start()
            
            # 构建API请求
            url = self.api_base_url + self.api_endpoint
            headers = request.get_headers()
            data = request.to_api_dict()
            
            # 计算超时时间
            timeout = calculate_timeout(request.text_length)
            
            self.logger.info(f"TTS生成开始 | 字符数: {request.text_length} | 语音: {request.voice} | 格式: {request.response_format}")
            
            # 发送请求，优化连接设置
            session = requests.Session()
            session.headers.update(headers)
            
            # 设置连接池和重试策略
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            retry_strategy = Retry(
                total=2,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["POST"]
            )
            
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=1,
                pool_maxsize=1
            )
            
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            response = session.post(url, json=data, timeout=(30, timeout), stream=False)
            response.raise_for_status()
            
            # 处理响应
            audio_data = response.content
            timer.stop()
            
            self.logger.info(f"TTS生成完成 | 耗时: {timer.elapsed:.2f}s | 音频大小: {len(audio_data)/1024:.1f}KB")
            
            # 记录到数据库
            if self.db_manager:
                self.db_manager.log_generation(
                    text_length=request.text_length,
                    voice=request.voice,
                    format=request.response_format,
                    speed=request.speed,
                    mode=request.mode,
                    duration=timer.elapsed,
                    audio_size=len(audio_data),
                    status='success'
                )
            
            return TTSResponse(
                success=True,
                audio_data=audio_data,
                audio_size=len(audio_data),
                duration=timer.elapsed
            )
            
        except requests.exceptions.Timeout:
            error_msg = "请求超时"
            self.logger.error(f"TTS生成超时: {error_msg}")
            self._log_error(request, error_msg)
            return TTSResponse(success=False, error_message=error_msg, status_code=504)
            
        except requests.exceptions.RequestException as e:
            error_msg = self._parse_request_error(e)
            self.logger.error(f"TTS生成失败: {error_msg}")
            self._log_error(request, error_msg)
            return TTSResponse(success=False, error_message=error_msg, status_code=getattr(e.response, 'status_code', 500))
            
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            self.logger.error(f"TTS生成异常: {error_msg}")
            self._log_error(request, error_msg)
            return TTSResponse(success=False, error_message=error_msg, status_code=500)
    
    def generate_streaming_speech(self, request: TTSRequest) -> Iterator[bytes]:
        """生成流式语音"""
        try:
            # 验证请求
            validation_result = self.validator.validate_tts_request(request.to_dict())
            if not validation_result['valid']:
                raise ValueError('; '.join(validation_result['errors']))
            
            # 分割文本，限制为300字符以符合语音服务器要求
            text_segments = split_text_for_streaming(request.input, max_length=300)
            total_segments = len(text_segments)
            
            # 对于超长文本，记录详细信息
            if request.text_length > 50000:
                self.logger.info(f"超长文本流式TTS开始 | 总字符: {request.text_length} | 分段数: {total_segments}")
            else:
                self.logger.info(f"流式TTS开始 | 分段数: {total_segments} | 总字符: {request.text_length}")
            
            streaming_response = StreamingTTSResponse(request)
            streaming_response.start_time = time.time()
            
            # 使用队列管理器确保同步处理
            from ..utils.queue_manager import get_queue_manager
            queue_manager = get_queue_manager()
            
            # 存储结果的字典
            segment_results = {}
            completed_segments = 0
            
            def segment_callback(task_id: str, result: Any, error: Exception):
                """段落处理完成回调"""
                nonlocal completed_segments
                segment_index = int(task_id.split('_')[1])
                
                if error:
                    self.logger.error(f"段落 {segment_index+1} 处理失败: {str(error)}")
                    segment_results[segment_index] = None
                else:
                    segment_results[segment_index] = result
                
                completed_segments += 1
            
            # 提交所有段落到队列
            for i, segment in enumerate(text_segments):
                progress = (i + 1) / total_segments * 100
                
                if request.text_length > 10000:  # 长文本显示详细进度
                    self.logger.info(f"提交段落 {i+1}/{total_segments} ({progress:.1f}%): {segment[:30]}...")
                else:
                    self.logger.debug(f"提交段落 {i+1}/{total_segments}: {segment[:50]}...")
                
                # 创建段落请求
                segment_request = TTSRequest(
                    input=segment,
                    voice=request.voice,
                    model=request.model,
                    response_format=request.response_format,
                    speed=request.speed,
                    api_key=request.api_key
                )
                
                # 提交到队列，使用优先级确保顺序
                task_id = f"segment_{i}"
                queue_manager.submit_task(
                    task_id=task_id,
                    func=self._generate_segment_sync,
                    args=(segment_request, i+1, total_segments),
                    callback=segment_callback,
                    priority=i  # 使用索引作为优先级确保顺序
                )
            
            # 等待所有段落完成并按顺序yield结果
            yielded_segments = set()
            
            while completed_segments < total_segments:
                time.sleep(0.1)  # 短暂等待
                
                # 按顺序检查是否有新完成的段落可以yield
                for i in range(total_segments):
                    if (i not in yielded_segments and 
                        i in segment_results and 
                        segment_results[i] is not None and 
                        segment_results[i] != "processed"):
                        
                        chunk_data = segment_results[i]
                        streaming_response.add_chunk(chunk_data)
                        yield chunk_data
                        
                        # 标记为已处理
                        segment_results[i] = "processed"
                        yielded_segments.add(i)
                        
                        self.logger.debug(f"已输出段落 {i+1}/{total_segments}")
            
            # 完成流式响应
            streaming_response.finalize(success=True)
            
            # 记录到数据库
            if self.db_manager:
                self.db_manager.log_generation(
                    text_length=request.text_length,
                    voice=request.voice,
                    format=request.response_format,
                    speed=request.speed,
                    mode='流式',
                    duration=streaming_response.duration,
                    audio_size=streaming_response.total_size,
                    status='success'
                )
            
            self.logger.info(f"流式TTS完成 | 耗时: {streaming_response.duration:.2f}s | 总大小: {streaming_response.total_size/1024:.1f}KB")
            
        except Exception as e:
            error_msg = f"流式生成失败: {str(e)}"
            self.logger.error(error_msg)
            self._log_error(request, error_msg)
            raise
    
    def _generate_segment_sync(self, segment_request: TTSRequest, segment_num: int, total_segments: int) -> bytes:
        """
        同步生成单个段落的音频
        
        Args:
            segment_request: 段落请求
            segment_num: 段落编号
            total_segments: 总段落数
            
        Returns:
            bytes: 音频数据
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.logger.info(f"处理段落 {segment_num}/{total_segments} (队列同步处理)")
                
                segment_response = self.generate_speech(segment_request)
                
                if segment_response.success and segment_response.audio_data:
                    if retry_count > 0:
                        self.logger.info(f"段落 {segment_num} 重试成功 (第{retry_count+1}次尝试)")
                    
                    return segment_response.audio_data
                else:
                    raise Exception(segment_response.error_message or "段落生成失败")
                    
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                
                if retry_count < max_retries:
                    wait_time = retry_count * 2  # 递增等待时间：2s, 4s, 6s
                    self.logger.warning(f"段落 {segment_num} 生成失败 (第{retry_count}次): {error_msg}，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"段落 {segment_num} 生成失败，已达最大重试次数: {error_msg}")
                    raise Exception(f"段落 {segment_num} 生成失败: {error_msg}")
    
    def test_connection(self, api_key: str) -> Dict[str, Any]:
        """测试API连接"""
        try:
            url = self.api_base_url + self.models_endpoint
            headers = {"Authorization": f"Bearer {api_key}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            models_data = response.json()
            return {
                "success": True,
                "message": "连接成功",
                "models": models_data
            }
            
        except requests.exceptions.Timeout:
            return {"success": False, "message": "连接超时"}
        except requests.exceptions.RequestException as e:
            error_msg = self._parse_request_error(e)
            return {"success": False, "message": f"连接失败: {error_msg}"}
        except Exception as e:
            return {"success": False, "message": f"未知错误: {str(e)}"}
    
    def get_models(self, api_key: str) -> Dict[str, Any]:
        """获取可用模型"""
        try:
            url = self.api_base_url + self.models_endpoint
            headers = {"Authorization": f"Bearer {api_key}"}
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"获取模型失败: {str(e)}")
            raise
    
    def _parse_request_error(self, error: requests.exceptions.RequestException) -> str:
        """解析请求错误"""
        if hasattr(error, 'response') and error.response is not None:
            status_code = error.response.status_code
            
            # 根据状态码返回友好的错误信息
            if status_code == 401:
                return "API密钥无效"
            elif status_code == 403:
                return "访问被拒绝，请检查API密钥"
            elif status_code == 404:
                return "API服务不可用"
            elif status_code == 429:
                return "请求过于频繁，请稍后重试"
            elif status_code == 500:
                return "服务器内部错误"
            else:
                try:
                    error_data = error.response.json()
                    return error_data.get('error', f"HTTP {status_code}")
                except:
                    return f"HTTP {status_code}: {error.response.text[:100]}"
        
        return str(error)
    
    def _log_error(self, request: TTSRequest, error_message: str):
        """记录错误到数据库"""
        if self.db_manager:
            self.db_manager.log_generation(
                text_length=request.text_length,
                voice=request.voice,
                format=request.response_format,
                speed=request.speed,
                mode=request.mode,
                status='error',
                error_message=error_message
            )
