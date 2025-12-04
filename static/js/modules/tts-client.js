/**
 * TTS客户端模块
 */

export class TTSClient {
    constructor() {
        this.baseUrl = '/api';
    }
    
    async testConnection() {
        try {
            const response = await fetch(`${this.baseUrl}/test_connection`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    api_key: this.getApiKey()
                })
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            throw new Error(`连接测试失败: ${error.message}`);
        }
    }
    
    async loadModels() {
        try {
            const response = await fetch(`${this.baseUrl}/models`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    api_key: this.getApiKey()
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`加载模型失败: ${error.message}`);
        }
    }
    
    async loadVoices() {
        try {
            const response = await fetch(`${this.baseUrl}/voices`, {
                method: 'GET'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`加载语音失败: ${error.message}`);
        }
    }
    
    async previewVoice(voice, customText = '') {
        try {
            const response = await fetch(`${this.baseUrl}/preview_voice`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    voice: voice,
                    api_key: this.getApiKey(),
                    text: customText
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`语音预览失败: ${error.message}`);
        }
    }
    
    async generateSpeech(requestData) {
        try {
            const response = await fetch(`${this.baseUrl}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.blob();
        } catch (error) {
            throw new Error(`语音生成失败: ${error.message}`);
        }
    }
    
    async generateStreamingSpeech(requestData, onChunk, onComplete, onError) {
        try {
            const response = await fetch(`${this.baseUrl}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const reader = response.body.getReader();
            const chunks = [];
            let receivedBytes = 0;
            
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                chunks.push(value);
                receivedBytes += value.length;
                
                // 调用chunk回调
                if (onChunk) {
                    onChunk(value, receivedBytes, chunks.length);
                }
            }
            
            // 合并所有chunks，优化长文本内存使用
            const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
            
            // 对于超大文件，分批处理以避免内存问题
            let result;
            if (totalLength > 50 * 1024 * 1024) { // 超过50MB
                console.log(`处理超大音频文件: ${(totalLength / 1024 / 1024).toFixed(1)}MB`);
                // 使用流式方式创建Blob，避免创建大型Uint8Array
                const blob = new Blob(chunks, { type: `audio/${requestData.response_format}` });
                
                if (onComplete) {
                    onComplete(blob, receivedBytes);
                }
                
                return blob;
            } else {
                // 正常处理
                result = new Uint8Array(totalLength);
                let offset = 0;
                
                for (const chunk of chunks) {
                    result.set(chunk, offset);
                    offset += chunk.length;
                }
                
                const blob = new Blob([result], { type: `audio/${requestData.response_format}` });
                
                if (onComplete) {
                    onComplete(blob, receivedBytes);
                }
                
                return blob;
            }
            
        } catch (error) {
            if (onError) {
                onError(error);
            }
            throw new Error(`流式语音生成失败: ${error.message}`);
        }
    }
    
    async fetchUrlContent(url) {
        try {
            const response = await fetch(`${this.baseUrl}/fetch_url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`获取URL内容失败: ${error.message}`);
        }
    }
    
    async getStats() {
        try {
            const response = await fetch(`${this.baseUrl}/stats`, {
                method: 'GET'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`获取统计数据失败: ${error.message}`);
        }
    }
    
    getApiKey() {
        const apiKeyInput = document.getElementById('api_key');
        return apiKeyInput ? apiKeyInput.value : '';
    }
    
    getCurrentSettings() {
        return {
            api_key: this.getApiKey(),
            model: document.getElementById('model')?.value || 'tts-1',
            voice: document.getElementById('custom_voice')?.value || document.getElementById('voice')?.value || 'zh-CN-XiaoxiaoNeural',
            response_format: document.querySelector('input[name="response_format"]:checked')?.value || 'mp3',
            speed: parseFloat(document.getElementById('speed')?.value || '1.0'),
            stream_format: document.getElementById('stream_mode')?.checked ? 'stream' : ''
        };
    }
    
    getCurrentText() {
        const textInput = document.getElementById('input_text');
        return textInput ? textInput.value : '';
    }
}
