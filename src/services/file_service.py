"""文件处理服务"""

import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from ..utils.logger import LoggerMixin
from ..utils.helpers import parse_subtitle
from ..utils.validators import TTSValidator
from ..config.constants import ALLOWED_FILE_TYPES


class FileService(LoggerMixin):
    """文件处理服务类"""
    
    def __init__(self):
        self.validator = TTSValidator()
    
    def process_uploaded_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """处理上传的文件"""
        try:
            # 验证文件类型
            validation_result = self.validator.validate_file_type(filename)
            if not validation_result['valid']:
                return {
                    "success": False,
                    "error": validation_result['error']
                }
            
            # 解码文件内容
            try:
                content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = file_content.decode('gbk')
                except UnicodeDecodeError:
                    return {
                        "success": False,
                        "error": "文件编码不支持，请使用UTF-8或GBK编码"
                    }
            
            # 根据文件类型处理内容
            processed_content = self._process_file_content(content, filename)
            
            return {
                "success": True,
                "content": processed_content,
                "filename": filename,
                "size": len(file_content),
                "length": len(processed_content)
            }
            
        except Exception as e:
            self.logger.error(f"文件处理失败: {str(e)}")
            return {
                "success": False,
                "error": f"文件处理失败: {str(e)}"
            }
    
    def fetch_url_content(self, url: str) -> Dict[str, Any]:
        """从URL获取内容"""
        try:
            # 验证URL
            validation_result = self.validator.validate_url(url)
            if not validation_result['valid']:
                return {
                    "success": False,
                    "error": validation_result['error']
                }
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # 发送请求
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # 检测编码
            encoding = response.encoding or 'utf-8'
            if encoding.lower() in ['iso-8859-1', 'windows-1252']:
                encoding = 'utf-8'
            
            # 获取内容
            try:
                content = response.content.decode(encoding)
            except UnicodeDecodeError:
                content = response.content.decode('utf-8', errors='ignore')
            
            # 简单的文本提取（去除HTML标签）
            processed_content = self._extract_text_from_html(content)
            
            return {
                "success": True,
                "content": processed_content,
                "url": url,
                "size": len(response.content),
                "length": len(processed_content),
                "encoding": encoding,
                "content_type": response.headers.get('content-type', 'unknown')
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "请求超时，请检查网络连接或稍后重试"
            }
        except requests.exceptions.RequestException as e:
            error_msg = self._parse_request_error(e)
            return {
                "success": False,
                "error": f"网络请求失败: {error_msg}"
            }
        except Exception as e:
            self.logger.error(f"URL内容获取失败: {str(e)}")
            return {
                "success": False,
                "error": f"获取内容失败: {str(e)}"
            }
    
    def validate_text_length(self, text: str, max_length: int = 100000) -> Dict[str, Any]:
        """验证文本长度 - 支持10万字长文本"""
        return self.validator.validate_text(text, max_length)
    
    def _process_file_content(self, content: str, filename: str) -> str:
        """根据文件类型处理内容"""
        filename_lower = filename.lower()
        
        # 字幕文件处理
        if filename_lower.endswith(('.srt', '.vtt')):
            return parse_subtitle(content)
        
        # JSON文件处理
        elif filename_lower.endswith('.json'):
            try:
                import json
                data = json.loads(content)
                # 如果是对象，尝试提取文本字段
                if isinstance(data, dict):
                    text_fields = ['text', 'content', 'message', 'description', 'body']
                    for field in text_fields:
                        if field in data and isinstance(data[field], str):
                            return data[field]
                    # 如果没有找到文本字段，返回JSON字符串
                    return json.dumps(data, ensure_ascii=False, indent=2)
                elif isinstance(data, list):
                    # 如果是数组，尝试连接所有字符串元素
                    texts = []
                    for item in data:
                        if isinstance(item, str):
                            texts.append(item)
                        elif isinstance(item, dict):
                            for field in text_fields:
                                if field in item and isinstance(item[field], str):
                                    texts.append(item[field])
                                    break
                    return '\n'.join(texts) if texts else content
                else:
                    return str(data)
            except json.JSONDecodeError:
                # JSON解析失败，返回原始内容
                return content
        
        # Markdown文件处理
        elif filename_lower.endswith('.md'):
            return self._extract_text_from_markdown(content)
        
        # 普通文本文件
        else:
            return content.strip()
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """从HTML中提取文本"""
        try:
            # 简单的HTML标签移除
            import re
            
            # 移除script和style标签及其内容
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            
            # 移除HTML标签
            text = re.sub(r'<[^>]+>', '', html_content)
            
            # 解码HTML实体
            import html
            text = html.unescape(text)
            
            # 清理空白字符
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)
            
        except Exception as e:
            self.logger.warning(f"HTML文本提取失败: {str(e)}")
            return html_content
    
    def _extract_text_from_markdown(self, markdown_content: str) -> str:
        """从Markdown中提取文本"""
        try:
            import re
            
            # 移除代码块
            markdown_content = re.sub(r'```.*?```', '', markdown_content, flags=re.DOTALL)
            markdown_content = re.sub(r'`[^`]+`', '', markdown_content)
            
            # 移除链接，保留文本
            markdown_content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown_content)
            
            # 移除图片
            markdown_content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', markdown_content)
            
            # 移除标题标记
            markdown_content = re.sub(r'^#+\s*', '', markdown_content, flags=re.MULTILINE)
            
            # 移除其他Markdown标记
            markdown_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', markdown_content)  # 粗体
            markdown_content = re.sub(r'\*([^*]+)\*', r'\1', markdown_content)      # 斜体
            markdown_content = re.sub(r'~~([^~]+)~~', r'\1', markdown_content)      # 删除线
            
            # 移除列表标记
            markdown_content = re.sub(r'^\s*[-*+]\s+', '', markdown_content, flags=re.MULTILINE)
            markdown_content = re.sub(r'^\s*\d+\.\s+', '', markdown_content, flags=re.MULTILINE)
            
            # 清理空白字符
            lines = [line.strip() for line in markdown_content.split('\n') if line.strip()]
            return '\n'.join(lines)
            
        except Exception as e:
            self.logger.warning(f"Markdown文本提取失败: {str(e)}")
            return markdown_content
    
    def _parse_request_error(self, error: requests.exceptions.RequestException) -> str:
        """解析请求错误"""
        if hasattr(error, 'response') and error.response is not None:
            status_code = error.response.status_code
            
            if status_code == 403:
                return "访问被拒绝，可能需要登录或权限"
            elif status_code == 404:
                return "页面不存在"
            elif status_code == 500:
                return "服务器内部错误"
            else:
                return f"HTTP {status_code}"
        
        return str(error)
