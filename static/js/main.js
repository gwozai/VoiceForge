/**
 * VoiceForge 主JavaScript模块 - 面向对象版本
 */

import { AudioManager } from './modules/audio-manager.js';
import { TTSClient } from './modules/tts-client.js';
import { UIManager } from './modules/ui-manager.js';
import { NotificationManager } from './modules/notification.js';
import { StreamingAudioPlayer } from './modules/streaming-player.js';

class VoiceForgeApp {
    constructor() {
        this.audioManager = new AudioManager();
        this.ttsClient = new TTSClient();
        this.uiManager = new UIManager();
        this.notificationManager = new NotificationManager();
        
        this.init();
    }
    
    init() {
        console.log('VoiceForge 2.0 - 面向对象版本初始化中...');
        
        // 初始化各个模块
        this.audioManager.init();
        this.uiManager.init();
        
        // 绑定事件
        this.bindEvents();
        
        console.log('VoiceForge 2.0 初始化完成');
    }
    
    bindEvents() {
        // 生成语音按钮
        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.handleGenerateSpeech());
        }
        
        // 测试连接按钮
        const testConnectionBtn = document.getElementById('testConnectionBtn');
        if (testConnectionBtn) {
            testConnectionBtn.addEventListener('click', () => this.handleTestConnection());
        }
        
        // 加载模型按钮
        const loadModelsBtn = document.getElementById('loadModelsBtn');
        if (loadModelsBtn) {
            loadModelsBtn.addEventListener('click', () => this.handleLoadModels());
        }
        
        // 加载语音按钮
        const loadVoicesBtn = document.getElementById('loadVoicesBtn');
        if (loadVoicesBtn) {
            loadVoicesBtn.addEventListener('click', () => this.handleLoadVoices());
        }
        
        // 语音试听按钮
        const previewVoiceBtn = document.getElementById('previewVoiceBtn');
        if (previewVoiceBtn) {
            previewVoiceBtn.addEventListener('click', () => this.handlePreviewVoice());
        }
        
        // 文件上传
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        }
        
        // URL获取按钮
        const fetchUrlBtn = document.getElementById('fetchUrlBtn');
        if (fetchUrlBtn) {
            fetchUrlBtn.addEventListener('click', () => this.handleFetchUrl());
        }
        
        // 字符计数更新
        const inputText = document.getElementById('input_text');
        if (inputText) {
            inputText.addEventListener('input', () => this.updateCharCount());
        }
    }
    
    async handleGenerateSpeech() {
        try {
            const inputText = this.ttsClient.getCurrentText().trim();
            if (!inputText) {
                this.notificationManager.show('请输入要转换的文本或上传文件', 'warning');
                return;
            }
            
            // 长文本处理提示
            const textLength = inputText.length;
            if (textLength > 100000) {
                this.notificationManager.show(`检测到超长文本(${Math.floor(textLength/1000)}k字符)，建议开启流式传输模式，预计需要20-30分钟`, 'info');
            } else if (textLength > 50000) {
                this.notificationManager.show(`检测到长文本(${Math.floor(textLength/1000)}k字符)，建议开启流式传输模式，预计需要10-15分钟`, 'info');
            } else if (textLength > 20000) {
                this.notificationManager.show(`检测到较长文本(${Math.floor(textLength/1000)}k字符)，建议开启流式传输模式`, 'info');
            }
            
            // 清理之前的音频播放器
            this.audioManager.cleanupAllAudio();
            
            // 显示加载状态
            this.uiManager.setGenerateButtonLoading(true);
            
            // 获取当前设置
            const settings = this.ttsClient.getCurrentSettings();
            settings.input = inputText;
            
            // 检查是否启用流式传输
            let isStreaming = settings.stream_format === 'stream';
            
            // 超过1000字符必须开启流式传输
            if (textLength > 1000 && !isStreaming) {
                const confirmed = confirm(`文本长度为 ${textLength} 字符，超过1000字符必须开启流式传输模式。\n\n点击"确定"开启流式传输并继续生成。`);
                
                if (confirmed) {
                    isStreaming = true;
                    // 自动勾选流式传输选项
                    const streamingCheckbox = document.getElementById('stream_mode');
                    if (streamingCheckbox) {
                        streamingCheckbox.checked = true;
                    }
                } else {
                    // 用户取消，停止生成
                    this.uiManager.setGenerateButtonLoading(false);
                    return;
                }
            }
            
            if (isStreaming) {
                await this.handleStreamingGeneration(settings);
            } else {
                await this.handleNormalGeneration(settings);
            }
            
        } catch (error) {
            console.error('生成语音失败:', error);
            this.notificationManager.show('生成语音失败: ' + error.message, 'error');
            this.uiManager.showError(error.message);
        } finally {
            this.uiManager.setGenerateButtonLoading(false);
        }
    }
    
    async handleNormalGeneration(settings) {
        // 普通生成模式
        const audioBlob = await this.ttsClient.generateSpeech(settings);
        
        // 创建音频URL
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // 显示音频播放器
        this.uiManager.showAudioOutput(audioUrl);
        
        // 注册音频元素
        const audioElement = document.querySelector('#audioOutput audio');
        if (audioElement) {
            this.audioManager.registerAudio(audioElement);
        }
        
        this.notificationManager.show('语音生成成功！', 'success');
        
        // 检查是否自动下载
        if (document.getElementById('auto_download')?.checked) {
            setTimeout(() => {
                if (typeof downloadAudio === 'function') {
                    downloadAudio();
                }
            }, 1000);
        }
    }
    
    async handleStreamingGeneration(settings) {
        // 流式生成模式
        const audioOutput = document.getElementById('audioOutput');
        if (!audioOutput) return;
        
        // 创建流式播放器容器
        const playerContainer = document.createElement('div');
        audioOutput.innerHTML = '';
        audioOutput.appendChild(playerContainer);
        
        // 创建流式播放器，优化长文本处理
        const textLength = settings.input.length;
        const bufferSize = textLength > 50000 ? 102400 : textLength > 10000 ? 51200 : 20480; // 动态缓冲区
        
        const streamingPlayer = new StreamingAudioPlayer(playerContainer, {
            format: settings.response_format,
            bufferSize: bufferSize,
            maxChunks: textLength > 50000 ? 3000 : 2000, // 长文本允许更多块
            refreshInterval: textLength > 10000 ? 8 : 5, // 长文本大幅减少刷新频率
            smoothTransition: true // 启用平滑过渡
        });
        
        // 注册到音频管理器
        this.audioManager.setStreamingPlayer(streamingPlayer);
        
        // 根据文本长度显示不同状态
        if (textLength > 50000) {
            streamingPlayer.updateStatus('正在处理超长文本，请耐心等待...');
        } else if (textLength > 10000) {
            streamingPlayer.updateStatus('正在处理长文本...');
        } else {
            streamingPlayer.updateStatus('正在分段生成音频...');
        }
        
        let totalReceived = 0;
        let chunkCount = 0;
        
        // 开始流式生成
        const audioBlob = await this.ttsClient.generateStreamingSpeech(
            settings,
            // onChunk 回调
            (chunk, receivedBytes, chunkIndex) => {
                totalReceived = receivedBytes;
                chunkCount = chunkIndex;
                
                // 添加音频数据到播放器
                streamingPlayer.addAudioData(chunk);
                
                // 更新状态
                const sizeKB = (totalReceived / 1024).toFixed(1);
                streamingPlayer.updateStatus(`正在接收... ${sizeKB}KB (${chunkCount}段)`);
            },
            // onComplete 回调
            (blob, totalSize) => {
                streamingPlayer.finalize();
                
                const sizeKB = (totalSize / 1024).toFixed(1);
                this.notificationManager.show(`流式语音生成完成！总大小: ${sizeKB}KB`, 'success');
                
                // 存储最终的音频URL
                const finalUrl = URL.createObjectURL(blob);
                window.currentAudioUrl = finalUrl;
                
                // 显示下载按钮
                const audioActions = document.getElementById('audioActions');
                if (audioActions) {
                    audioActions.style.cssText = 'display: flex !important;';
                }
                
                // 检查是否自动下载
                if (document.getElementById('auto_download')?.checked) {
                    setTimeout(() => {
                        if (typeof downloadAudio === 'function') {
                            downloadAudio();
                        }
                    }, 1000);
                }
            },
            // onError 回调
            (error) => {
                streamingPlayer.updateStatus('生成失败');
                this.notificationManager.show(`流式生成失败: ${error.message}`, 'error');
            }
        );
    }
    
    async handleTestConnection() {
        try {
            this.notificationManager.show('正在测试连接...', 'info');
            const result = await this.ttsClient.testConnection();
            
            if (result.success) {
                this.notificationManager.show('连接成功！', 'success');
            } else {
                this.notificationManager.show('连接失败: ' + result.message, 'error');
            }
        } catch (error) {
            this.notificationManager.show('连接测试失败: ' + error.message, 'error');
        }
    }
    
    async handleLoadModels() {
        try {
            this.notificationManager.show('正在加载模型...', 'info');
            const result = await this.ttsClient.loadModels();
            
            // 更新模型选择器
            const modelSelect = document.getElementById('model');
            if (modelSelect && result.models) {
                const currentValue = modelSelect.value;
                modelSelect.innerHTML = '';
                
                const models = result.models.data || result.models;
                models.forEach(model => {
                    const option = document.createElement('option');
                    const modelId = model.id || model;
                    option.value = modelId;
                    option.textContent = modelId;
                    modelSelect.appendChild(option);
                });
                
                // 恢复选择
                if (Array.from(modelSelect.options).some(opt => opt.value === currentValue)) {
                    modelSelect.value = currentValue;
                }
            }
            
            this.notificationManager.show(`已成功加载 ${result.models?.data?.length || result.models?.length || 0} 个模型`, 'success');
        } catch (error) {
            this.notificationManager.show('加载模型失败: ' + error.message, 'error');
        }
    }
    
    async handleLoadVoices() {
        try {
            this.notificationManager.show('正在加载语音...', 'info');
            const result = await this.ttsClient.loadVoices();
            
            // 更新语音选择器
            const voiceSelect = document.getElementById('voice');
            let totalCount = 0;
            
            if (voiceSelect && result.voices) {
                const currentValue = voiceSelect.value;
                voiceSelect.innerHTML = '';
                
                Object.keys(result.voices).forEach(category => {
                    const group = document.createElement('optgroup');
                    group.label = category;
                    
                    result.voices[category].forEach(voice => {
                        const option = document.createElement('option');
                        option.value = voice.name;
                        option.textContent = `${voice.name} (${voice.gender || 'Unknown'})`;
                        group.appendChild(option);
                        totalCount++;
                    });
                    
                    voiceSelect.appendChild(group);
                });
                
                // 恢复选择
                if (Array.from(voiceSelect.options).some(opt => opt.value === currentValue)) {
                    voiceSelect.value = currentValue;
                }
            }
            
            this.notificationManager.show(`已成功加载 ${totalCount} 个语音`, 'success');
        } catch (error) {
            this.notificationManager.show('加载语音失败: ' + error.message, 'error');
        }
    }
    
    async handlePreviewVoice() {
        try {
            const voice = document.getElementById('custom_voice')?.value || document.getElementById('voice')?.value;
            if (!voice) {
                this.notificationManager.show('请先选择一个语音', 'warning');
                return;
            }
            
            this.notificationManager.show('正在生成语音预览...', 'info');
            
            const result = await this.ttsClient.previewVoice(voice);
            
            if (result.success) {
                if (result.audio) {
                    // 如果返回了base64音频数据
                    const audioData = atob(result.audio);
                    const audioArray = new Uint8Array(audioData.length);
                    for (let i = 0; i < audioData.length; i++) {
                        audioArray[i] = audioData.charCodeAt(i);
                    }
                    const audioBlob = new Blob([audioArray], { type: `audio/${result.format}` });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    
                    // 播放预览音频
                    const audio = new Audio(audioUrl);
                    audio.play();
                    
                    this.notificationManager.show(`语音预览: "${result.text}"`, 'success');
                } else {
                    this.notificationManager.show(result.message || '预览功能暂不可用', 'info');
                }
            } else {
                this.notificationManager.show('预览失败: ' + result.error, 'error');
            }
        } catch (error) {
            this.notificationManager.show('语音预览失败: ' + error.message, 'error');
        }
    }
    
    // 处理文件上传
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        try {
            const text = await this.readFileAsText(file);
            const processedText = this.processFileContent(text, file.name);
            
            // 显示文件预览
            const filePreview = document.getElementById('filePreview');
            const fileContent = document.getElementById('fileContent');
            
            if (filePreview && fileContent) {
                fileContent.value = processedText;
                filePreview.style.display = 'block';
                
                // 更新主文本框
                const inputText = document.getElementById('input_text');
                if (inputText) {
                    inputText.value = processedText;
                    this.updateCharCount();
                }
                
                this.notificationManager.show(`文件 "${file.name}" 上传成功，共 ${processedText.length} 个字符`, 'success');
            }
        } catch (error) {
            this.notificationManager.show('文件读取失败: ' + error.message, 'error');
        }
    }
    
    // 处理URL获取
    async handleFetchUrl() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput?.value?.trim();
        
        if (!url) {
            this.notificationManager.show('请输入有效的URL地址', 'warning');
            return;
        }
        
        try {
            const fetchUrlBtn = document.getElementById('fetchUrlBtn');
            if (fetchUrlBtn) {
                fetchUrlBtn.disabled = true;
                fetchUrlBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 获取中...';
            }
            
            const response = await this.ttsClient.fetchUrlContent(url);
            
            if (response.success) {
                const processedText = this.processFileContent(response.content, url);
                
                // 显示URL预览
                const urlPreview = document.getElementById('urlPreview');
                const urlContent = document.getElementById('urlContent');
                
                if (urlPreview && urlContent) {
                    urlContent.value = processedText;
                    urlPreview.style.display = 'block';
                    
                    // 更新主文本框
                    const inputText = document.getElementById('input_text');
                    if (inputText) {
                        inputText.value = processedText;
                        this.updateCharCount();
                    }
                    
                    this.notificationManager.show(`网络文本获取成功，共 ${processedText.length} 个字符`, 'success');
                }
            } else {
                this.notificationManager.show('获取失败: ' + response.error, 'error');
            }
        } catch (error) {
            this.notificationManager.show('网络请求失败: ' + error.message, 'error');
        } finally {
            const fetchUrlBtn = document.getElementById('fetchUrlBtn');
            if (fetchUrlBtn) {
                fetchUrlBtn.disabled = false;
                fetchUrlBtn.innerHTML = '<i class="bi bi-download"></i> 获取';
            }
        }
    }
    
    // 读取文件内容
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('文件读取失败'));
            reader.readAsText(file, 'UTF-8');
        });
    }
    
    // 处理文件内容（支持不同格式）
    processFileContent(content, filename) {
        const extension = filename.toLowerCase().split('.').pop();
        
        switch (extension) {
            case 'srt':
                // 处理字幕文件
                return this.parseSrtContent(content);
            case 'md':
                // 处理Markdown文件
                return this.parseMarkdownContent(content);
            case 'txt':
            default:
                // 普通文本文件
                return content.trim();
        }
    }
    
    // 解析SRT字幕文件
    parseSrtContent(content) {
        const lines = content.split('\n');
        const textLines = [];
        
        for (const line of lines) {
            const trimmed = line.trim();
            // 跳过序号行和时间戳行
            if (trimmed && !trimmed.match(/^\d+$/) && !trimmed.includes('-->')) {
                // 移除HTML标签
                const cleanText = trimmed.replace(/<[^>]+>/g, '');
                if (cleanText) {
                    textLines.push(cleanText);
                }
            }
        }
        
        return textLines.join('\n');
    }
    
    // 解析Markdown文件
    parseMarkdownContent(content) {
        // 移除Markdown标记，保留纯文本
        return content
            .replace(/^#{1,6}\s+/gm, '') // 移除标题标记
            .replace(/\*\*(.*?)\*\*/g, '$1') // 移除粗体标记
            .replace(/\*(.*?)\*/g, '$1') // 移除斜体标记
            .replace(/`(.*?)`/g, '$1') // 移除代码标记
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // 移除链接，保留文本
            .replace(/^[-*+]\s+/gm, '') // 移除列表标记
            .trim();
    }
    
    // 更新字符计数
    updateCharCount() {
        const inputText = document.getElementById('input_text');
        const charCount = document.getElementById('charCount');
        
        if (inputText && charCount) {
            const count = inputText.value.length;
            charCount.textContent = `字符: ${count}`;
        }
    }
}

// 当DOM加载完成时初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.voiceForgeApp = new VoiceForgeApp();
});
