/**
 * 通知管理器模块
 */

export class NotificationManager {
    constructor() {
        this.notifications = new Set();
    }
    
    show(message, type = 'info', duration = 3000) {
        const notification = this.createNotification(message, type);
        document.body.appendChild(notification);
        this.notifications.add(notification);
        
        // 自动消失
        setTimeout(() => {
            this.remove(notification);
        }, duration);
        
        return notification;
    }
    
    createNotification(message, type) {
        const notification = document.createElement('div');
        const alertClass = this.getAlertClass(type);
        
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // 绑定关闭事件
        const closeBtn = notification.querySelector('.btn-close');
        closeBtn.addEventListener('click', () => this.remove(notification));
        
        return notification;
    }
    
    getAlertClass(type) {
        const typeMap = {
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'success': 'alert-success',
            'info': 'alert-info'
        };
        return typeMap[type] || 'alert-info';
    }
    
    remove(notification) {
        if (notification && notification.parentNode) {
            notification.remove();
            this.notifications.delete(notification);
        }
    }
    
    clearAll() {
        this.notifications.forEach(notification => {
            this.remove(notification);
        });
    }
}
