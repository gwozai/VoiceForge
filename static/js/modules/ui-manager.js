/**
 * UI管理器模块
 */

export class UIManager {
    constructor() {
        this.generateBtn = null;
        this.originalBtnText = '';
    }
    
    init() {
        this.generateBtn = document.getElementById('generateBtn');
        if (this.generateBtn) {
            this.originalBtnText = this.generateBtn.innerHTML;
        }
        console.log('UIManager 初始化完成');
    }
    
    getCurrentText() {
        const textInput = document.getElementById('input_text');
        return textInput ? textInput.value : '';
    }
    
    setGenerateButtonLoading(loading) {
        if (!this.generateBtn) return;
        
        if (loading) {
            this.generateBtn.disabled = true;
            this.generateBtn.innerHTML = '<div class="loading-spinner d-inline-block me-2"></div> 生成中...';
        } else {
            this.generateBtn.disabled = false;
            this.generateBtn.innerHTML = this.originalBtnText;
        }
    }
    
    updateCharCount() {
        const textInput = document.getElementById('input_text');
        const charCountEl = document.querySelector('.char-count');
        
        if (textInput && charCountEl) {
            const count = textInput.value.length;
            charCountEl.textContent = `字符: ${count}`;
        }
    }
    
    showAudioOutput(audioUrl) {
        const audioOutput = document.getElementById('audioOutput');
        const audioActions = document.getElementById('audioActions');
        
        if (audioOutput) {
            audioOutput.innerHTML = `
                <audio controls autoplay src="${audioUrl}" style="width: 100%;"></audio>
                <div class="mt-2 text-center">
                    <small class="text-muted">
                        <i class="bi bi-check-circle text-success"></i> 
                        语音生成成功
                    </small>
                </div>
            `;
            
            // 添加播放事件监听
            const audio = audioOutput.querySelector('audio');
            if (audio) {
                audio.addEventListener('play', () => {
                    console.log('🎵 音频开始自动播放');
                });
                
                audio.addEventListener('ended', () => {
                    console.log('🎵 音频播放完成');
                });
                
                // 如果浏览器阻止了自动播放，显示提示
                audio.addEventListener('pause', () => {
                    if (audio.currentTime === 0) {
                        console.log('⚠️ 浏览器可能阻止了自动播放，请手动点击播放按钮');
                    }
                });
            }
        }
        
        if (audioActions) {
            audioActions.style.cssText = 'display: flex !important;';
        }
        
        // 存储当前音频URL供下载使用
        window.currentAudioUrl = audioUrl;
    }
    
    showError(message) {
        const audioOutput = document.getElementById('audioOutput');
        if (audioOutput) {
            audioOutput.innerHTML = `
                <div class="text-center p-4">
                    <i class="bi bi-exclamation-triangle text-warning" style="font-size: 2rem;"></i>
                    <h5 class="mt-2 text-danger">生成失败</h5>
                    <p class="text-muted">${message}</p>
                </div>
            `;
        }
    }
}
