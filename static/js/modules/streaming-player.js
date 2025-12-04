/**
 * 流式音频播放器模块
 */

export class StreamingAudioPlayer {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            bufferSize: options.bufferSize || 51200, // 50KB - 增大缓冲区
            updateInterval: options.updateInterval || 1500, // 1.5秒 - 更频繁更新
            format: options.format || 'mp3',
            maxChunks: options.maxChunks || 2000, // 最大块数，防止内存溢出
            refreshInterval: options.refreshInterval || 5, // 每N个段落刷新一次音频（增加间隔）
            smoothTransition: options.smoothTransition !== false, // 启用平滑过渡
            preloadBuffer: options.preloadBuffer !== false, // 启用预加载缓冲
            ...options
        };
        
        this.chunks = [];
        this.totalSize = 0;
        this.audioElement = null;
        this.currentUrl = null;
        this.isFinished = false;
        this.lastPlayedTime = 0;
        this.segmentCount = 0;
        this.processedSegments = 0;
        this.startTime = Date.now();
        
        this.init();
    }
    
    init() {
        // 创建播放器界面
        this.container.innerHTML = `
            <div class="streaming-player">
                <div class="d-flex align-items-center gap-2 mb-2">
                    <div class="loading-spinner"></div>
                    <small class="text-muted">
                        <span class="status-text">准备中...</span>
                    </small>
                </div>
                <audio controls style="width: 100%;"></audio>
                <div class="progress mt-2" style="height: 4px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 0%"></div>
                </div>
                <div class="d-flex justify-content-between mt-1">
                    <small class="text-muted">
                        <span class="received-size">0 KB</span>
                    </small>
                    <small class="text-muted">
                        <span class="chunk-count">0 段</span>
                    </small>
                </div>
            </div>
        `;
        
        this.audioElement = this.container.querySelector('audio');
        this.statusText = this.container.querySelector('.status-text');
        this.progressBar = this.container.querySelector('.progress-bar');
        this.receivedSizeEl = this.container.querySelector('.received-size');
        this.chunkCountEl = this.container.querySelector('.chunk-count');
        
        // 双缓冲播放器：实现无缝切换
        this.isRefreshing = false;
        this.pendingChunks = 0;
        this.lastChunkCount = 0; // 上次更新时的块数
        this.nextAudio = null;   // 预加载的下一个音频
        this.nextUrl = null;
        
        // 播放结束时自动切换到预加载的音频
        this.audioElement.addEventListener('ended', () => {
            if (this.nextAudio && this.nextUrl) {
                // 无缝切换到预加载的音频
                this.switchToNextAudio();
            } else if (!this.isFinished && this.pendingChunks > 0) {
                // 没有预加载但有新内容，强制刷新
                this.forceRefreshAndPlay();
            } else if (this.isFinished) {
                this.updateStatus('播放完成');
            }
        });
        
        // 播放接近结尾时预加载新内容
        this.audioElement.addEventListener('timeupdate', () => {
            if (this.isFinished) return;
            
            const remaining = (this.audioElement.duration || 0) - (this.audioElement.currentTime || 0);
            
            // 剩余8秒时开始预加载
            if (remaining < 8 && remaining > 0 && this.pendingChunks > 0 && !this.nextAudio) {
                this.preloadNextAudio();
            }
        });
    }
    
    addAudioData(audioData) {
        const uint8Array = new Uint8Array(audioData);
        this.chunks.push(uint8Array);
        this.totalSize += uint8Array.length;
        this.processedSegments++;
        this.pendingChunks++;
        
        // 防止内存溢出
        if (this.chunks.length > this.options.maxChunks) {
            const removedChunk = this.chunks.shift();
            this.totalSize -= removedChunk.length;
        }
        
        // 只更新UI，不刷新音频（避免断点）
        this.updateUI();
        
        // 首次有数据时创建音频并播放
        if (this.chunks.length === 1) {
            this.forceRefreshAndPlay();
        }
        // 后续数据只存储，等播放快结束时再预加载
    }
    
    preloadNextAudio() {
        // 预加载下一段音频（在后台准备好）
        if (this.nextAudio) return; // 已经在预加载了
        
        const combinedArray = new Uint8Array(this.totalSize);
        let offset = 0;
        for (const chunk of this.chunks) {
            combinedArray.set(chunk, offset);
            offset += chunk.length;
        }
        
        const blob = new Blob([combinedArray], { type: `audio/${this.options.format}` });
        this.nextUrl = URL.createObjectURL(blob);
        
        // 创建预加载的音频元素
        this.nextAudio = document.createElement('audio');
        this.nextAudio.src = this.nextUrl;
        this.nextAudio.preload = 'auto';
        this.nextAudio.load();
        
        this.lastChunkCount = this.chunks.length;
        console.log(`预加载音频完成，共 ${this.chunks.length} 段`);
    }
    
    switchToNextAudio() {
        // 无缝切换到预加载的音频
        if (!this.nextAudio || !this.nextUrl) return;
        
        const oldDuration = this.audioElement.duration || 0;
        const rate = this.audioElement.playbackRate || 1;
        
        // 清理旧的URL
        if (this.currentUrl) {
            URL.revokeObjectURL(this.currentUrl);
        }
        
        // 更新当前音频
        this.currentUrl = this.nextUrl;
        this.audioElement.src = this.nextUrl;
        this.audioElement.playbackRate = rate;
        
        // 从上次播放结束的位置继续
        this.audioElement.addEventListener('loadedmetadata', () => {
            if (oldDuration > 0 && oldDuration < this.audioElement.duration) {
                this.audioElement.currentTime = oldDuration;
            }
            this.audioElement.play().catch(() => {});
        }, { once: true });
        
        this.audioElement.load();
        
        // 清理预加载
        this.nextAudio = null;
        this.nextUrl = null;
        this.pendingChunks = 0;
        
        console.log(`无缝切换完成，从 ${oldDuration.toFixed(2)}s 继续播放`);
    }
    
    shouldRefreshAudio() {
        // 智能判断是否需要刷新音频
        if (!this.audioElement) return true;
        
        // 如果音频已经播放完毕，需要刷新
        if (this.audioElement.ended) return true;
        
        // 如果音频暂停且有新内容，需要刷新
        if (this.audioElement.paused && this.chunks.length > 1) return true;
        
        // 如果当前播放时间接近音频结尾，且有新内容，需要刷新
        const currentTime = this.audioElement.currentTime || 0;
        const duration = this.audioElement.duration || 0;
        const timeRemaining = duration - currentTime;
        
        if (timeRemaining < 2 && this.chunks.length % this.options.refreshInterval === 0) {
            return true;
        }
        
        // 如果累积了足够多的新段落，需要刷新
        if (this.chunks.length % (this.options.refreshInterval * 2) === 0) {
            return true;
        }
        
        return false;
    }
    
    forceRefreshAndPlay() {
        // 强制刷新并播放，用于播放结束后继续
        if (this.chunks.length === 0 || this.isRefreshing) return;
        
        this.isRefreshing = true;
        
        const currentTime = this.audioElement.currentTime || 0;
        const rate = this.audioElement.playbackRate || 1;
        
        // 创建新的音频blob
        const combinedArray = new Uint8Array(this.totalSize);
        let offset = 0;
        
        for (const chunk of this.chunks) {
            combinedArray.set(chunk, offset);
            offset += chunk.length;
        }
        
        const blob = new Blob([combinedArray], { type: `audio/${this.options.format}` });
        const newUrl = URL.createObjectURL(blob);
        
        // 清理旧的URL
        if (this.currentUrl) {
            URL.revokeObjectURL(this.currentUrl);
        }
        
        this.currentUrl = newUrl;
        this.audioElement.src = newUrl;
        this.audioElement.playbackRate = rate;
        
        // 设置播放位置并播放
        this.audioElement.addEventListener('loadedmetadata', () => {
            // 从之前的位置继续播放
            if (currentTime > 0 && currentTime < this.audioElement.duration) {
                this.audioElement.currentTime = currentTime;
            }
            this.audioElement.play().catch(e => console.warn('自动播放失败:', e));
        }, { once: true });
        
        this.audioElement.load();
        
        // 重置计数器
        this.pendingChunks = 0;
        this.lastRefreshTime = Date.now();
        
        setTimeout(() => {
            this.isRefreshing = false;
        }, 500);
        
        console.log(`刷新音频，从 ${currentTime.toFixed(2)}s 继续`);
    }
    
    refreshAudio() {
        if (this.chunks.length === 0) return;
        
        // 使用强制刷新播放
        this.forceRefreshAndPlay();
    }
    
    seamlessRefresh() {
        // 无缝刷新：创建新音频元素，在合适时机切换
        const currentTime = this.audioElement.currentTime || 0;
        const rate = this.audioElement.playbackRate || 1;
        
        // 创建新的音频blob
        const combinedArray = new Uint8Array(this.totalSize);
        let offset = 0;
        
        for (const chunk of this.chunks) {
            combinedArray.set(chunk, offset);
            offset += chunk.length;
        }
        
        const blob = new Blob([combinedArray], { type: `audio/${this.options.format}` });
        const newUrl = URL.createObjectURL(blob);
        
        // 创建新的音频元素
        const newAudio = document.createElement('audio');
        newAudio.src = newUrl;
        newAudio.controls = true;
        newAudio.style.width = '100%';
        newAudio.currentTime = currentTime;
        newAudio.playbackRate = rate;
        
        // 预加载新音频
        newAudio.addEventListener('canplaythrough', () => {
            // 在当前音频播放到接近结尾时切换
            const switchTime = Math.max(0, this.audioElement.duration - 0.1);
            
            if (currentTime >= switchTime - 0.5) {
                // 立即切换
                this.switchToNewAudio(newAudio, newUrl, currentTime);
            } else {
                // 等待合适时机切换
                const checkSwitch = () => {
                    if (this.audioElement.currentTime >= switchTime - 0.2) {
                        this.switchToNewAudio(newAudio, newUrl, this.audioElement.currentTime);
                    } else {
                        setTimeout(checkSwitch, 100);
                    }
                };
                setTimeout(checkSwitch, 100);
            }
        });
        
        newAudio.load();
    }
    
    normalRefresh() {
        // 正常刷新：直接替换音频源
        const currentTime = this.audioElement.currentTime || 0;
        const wasPlaying = !this.audioElement.paused;
        const rate = this.audioElement.playbackRate || 1;
        
        // 创建新的音频blob
        const combinedArray = new Uint8Array(this.totalSize);
        let offset = 0;
        
        for (const chunk of this.chunks) {
            combinedArray.set(chunk, offset);
            offset += chunk.length;
        }
        
        const blob = new Blob([combinedArray], { type: `audio/${this.options.format}` });
        const newUrl = URL.createObjectURL(blob);
        
        // 清理旧的URL
        if (this.currentUrl) {
            URL.revokeObjectURL(this.currentUrl);
        }
        
        this.currentUrl = newUrl;
        this.audioElement.src = newUrl;
        
        // 恢复播放状态
        if (wasPlaying) {
            this.audioElement.currentTime = currentTime;
            this.audioElement.playbackRate = rate;
            this.audioElement.play().catch(e => console.warn('播放失败:', e));
        }
    }
    
    switchToNewAudio(newAudio, newUrl, currentTime) {
        // 无缝切换到新音频
        const oldAudio = this.audioElement;
        const oldUrl = this.currentUrl;
        
        // 替换音频元素
        this.audioElement = newAudio;
        this.currentUrl = newUrl;
        
        // 替换DOM中的音频元素
        if (oldAudio.parentNode) {
            oldAudio.parentNode.replaceChild(newAudio, oldAudio);
        }
        
        // 从当前时间开始播放
        newAudio.currentTime = currentTime;
        newAudio.play().catch(e => console.warn('无缝切换播放失败:', e));
        
        // 清理旧资源
        setTimeout(() => {
            if (oldUrl) {
                URL.revokeObjectURL(oldUrl);
            }
        }, 1000);
        
        console.log(`无缝切换完成，从 ${currentTime.toFixed(2)}s 继续播放`);
    }
    
    updateUI() {
        // 更新接收大小
        const sizeKB = (this.totalSize / 1024).toFixed(1);
        this.receivedSizeEl.textContent = `${sizeKB} KB`;
        
        // 更新段数 - 显示处理进度
        if (this.segmentCount > 0) {
            this.chunkCountEl.textContent = `${this.processedSegments}/${this.segmentCount} 段`;
        } else {
            this.chunkCountEl.textContent = `${this.processedSegments} 段`;
        }
        
        // 更新进度条
        let progress = 0;
        if (this.segmentCount > 0) {
            // 基于段数的精确进度
            progress = Math.min((this.processedSegments / this.segmentCount) * 100, 100);
        } else {
            // 基于数据量的估算进度（长文本可能需要更大的估算值）
            const estimatedTotal = this.totalSize > 500000 ? 2000000 : 200000; // 2MB for very long texts
            progress = Math.min((this.totalSize / estimatedTotal) * 100, 90);
        }
        this.progressBar.style.width = `${progress.toFixed(1)}%`;
        
        // 显示处理时间（长文本很有用）
        const elapsed = (Date.now() - this.startTime) / 1000;
        if (elapsed > 10) { // 超过10秒显示时间
            const timeStr = elapsed > 60 ? `${Math.floor(elapsed/60)}m${Math.floor(elapsed%60)}s` : `${elapsed.toFixed(0)}s`;
            this.updateStatus(`正在处理... (${timeStr})`);
        }
    }
    
    play() {
        return this.audioElement ? this.audioElement.play() : Promise.reject();
    }
    
    pause() {
        if (this.audioElement) this.audioElement.pause();
    }
    
    updateStatus(message) {
        if (this.statusText) this.statusText.textContent = message;
    }
    
    setTotalSegments(count) {
        this.segmentCount = count;
        this.updateUI();
    }
    
    finalize() {
        this.isFinished = true;
        
        // 最终刷新确保完整，但保持当前播放状态
        if (this.pendingChunks > 0) {
            const wasPlaying = !this.audioElement.paused;
            const currentTime = this.audioElement.currentTime || 0;
            
            this.forceRefreshAndPlay();
            
            // 如果之前不是在播放，就暂停
            if (!wasPlaying && currentTime === 0) {
                setTimeout(() => {
                    this.audioElement.pause();
                }, 100);
            }
        }
        
        this.updateStatus('生成完成');
        
        // 完成时进度条到100%
        this.progressBar.style.width = '100%';
        this.progressBar.classList.remove('progress-bar-animated');
        this.progressBar.classList.add('bg-success');
        
        // 隐藏加载动画
        const spinner = this.container.querySelector('.loading-spinner');
        if (spinner) {
            spinner.style.display = 'none';
        }
        
        console.log('音频生成完成，总大小:', (this.totalSize / 1024).toFixed(1), 'KB');
    }
    
    getAudioElement() {
        return this.audioElement;
    }
    
    getAudioBlob() {
        if (this.chunks.length === 0) return null;
        
        const mimeType = this.getMimeType();
        return new Blob(this.chunks, { type: mimeType });
    }
    
    getMimeType() {
        const format = this.options.format || 'mp3';
        return format === 'mp3' ? 'audio/mpeg' : `audio/${format}`;
    }
    
    destroy() {
        if (this.currentUrl) {
            URL.revokeObjectURL(this.currentUrl);
        }
        this.chunks = [];
        
        if (this.audioElement) {
            this.audioElement.pause();
            this.audioElement.src = '';
        }
    }
}
