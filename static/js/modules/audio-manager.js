/**
 * 音频管理器模块
 */

export class AudioManager {
    constructor() {
        this.activeAudioElements = new Set();
        this.currentStreamingPlayer = null;
    }
    
    init() {
        console.log('AudioManager 初始化完成');
    }
    
    // 清理所有音频播放器
    cleanupAllAudio() {
        // 清理普通音频元素
        this.activeAudioElements.forEach(audio => {
            if (audio && !audio.paused) {
                audio.pause();
            }
            if (audio && audio.src && audio.src.startsWith('blob:')) {
                URL.revokeObjectURL(audio.src);
            }
        });
        this.activeAudioElements.clear();
        
        // 清理流式播放器
        if (this.currentStreamingPlayer) {
            this.currentStreamingPlayer.destroy();
            this.currentStreamingPlayer = null;
        }
        
        console.log('所有音频播放器已清理');
    }
    
    // 注册新的音频元素
    registerAudio(audioElement) {
        this.activeAudioElements.add(audioElement);
        
        // 当音频结束时自动清理
        audioElement.addEventListener('ended', () => {
            this.activeAudioElements.delete(audioElement);
        });
    }
    
    // 设置当前流式播放器
    setStreamingPlayer(player) {
        if (this.currentStreamingPlayer) {
            this.currentStreamingPlayer.destroy();
        }
        this.currentStreamingPlayer = player;
    }
    
    // 创建音频播放器
    createAudioPlayer(container, audioUrl, options = {}) {
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = audioUrl;
        audio.style.width = '100%';
        
        if (options.autoplay) {
            audio.autoplay = true;
        }
        
        container.innerHTML = '';
        container.appendChild(audio);
        
        this.registerAudio(audio);
        
        return audio;
    }
}
