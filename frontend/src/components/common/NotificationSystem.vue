<template>
  <div class="notification-container" :class="positionClass">
    <transition-group name="notification-slide">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification-item"
        :class="getNotificationClass(notification)"
        @mouseenter="handleMouseEnter(notification)"
        @mouseleave="handleMouseLeave(notification)"
        @click="handleClick(notification)"
      >
        <!-- 图标 -->
        <div class="notification-icon">
          <svg v-if="notification.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
          <svg v-else-if="notification.type === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <line x1="12" y1="9" x2="12" y2="13" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <line x1="12" y1="17" x2="12.01" y2="17" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
          <svg v-else-if="notification.type === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <line x1="15" y1="9" x2="9" y2="15" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <line x1="9" y1="9" x2="15" y2="15" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <line x1="12" y1="16" x2="12" y2="12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <line x1="12" y1="8" x2="12.01" y2="8" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
        </div>

        <!-- 内容 -->
        <div class="notification-content">
          <div v-if="notification.title" class="notification-title">
            {{ notification.title }}
          </div>
          <div class="notification-message">
            {{ notification.message }}
          </div>
        </div>

        <!-- 关闭按钮 -->
        <button
          v-if="notification.closable"
          class="notification-close"
          @click.stop="close(notification.id)"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <line x1="6" y1="6" x2="18" y2="18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
        </button>

        <!-- 进度条 -->
        <div
          v-if="notification.showProgress"
          class="notification-progress"
          :style="{ animationDuration: notification.duration + 'ms' }"
        ></div>
      </div>
    </transition-group>
  </div>
</template>

<script>
export default {
  name: 'NotificationSystem',
  data() {
    return {
      notifications: [],
      nextId: 1,
      position: 'top-right', // 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'top-center', 'bottom-center'
      maxNotifications: 5
    }
  },
  computed: {
    positionClass() {
      return `position-${this.position}`
    }
  },
  methods: {
    /**
     * 显示通知
     * @param {Object} options - 通知配置
     */
    notify(options = {}) {
      const notification = {
        id: this.nextId++,
        type: options.type || 'info', // 'success', 'warning', 'error', 'info'
        title: options.title || '',
        message: options.message || '',
        duration: options.duration !== undefined ? options.duration : 4500,
        closable: options.closable !== false,
        showProgress: options.showProgress !== false,
        onClick: options.onClick || null,
        onClose: options.onClose || null,
        timer: null,
        pauseOnHover: options.pauseOnHover !== false
      }

      // 限制通知数量
      if (this.notifications.length >= this.maxNotifications) {
        this.notifications.shift()
      }

      this.notifications.push(notification)

      // 自动关闭
      if (notification.duration > 0) {
        this.startTimer(notification)
      }

      return notification.id
    },

    /**
     * 便捷方法
     */
    success(message, title = '') {
      return this.notify({ type: 'success', message, title })
    },

    warning(message, title = '') {
      return this.notify({ type: 'warning', message, title })
    },

    error(message, title = '') {
      return this.notify({ type: 'error', message, title })
    },

    info(message, title = '') {
      return this.notify({ type: 'info', message, title })
    },

    /**
     * 关闭通知
     */
    close(id) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index !== -1) {
        const notification = this.notifications[index]
        if (notification.timer) {
          clearTimeout(notification.timer)
        }
        if (notification.onClose) {
          notification.onClose()
        }
        this.notifications.splice(index, 1)
      }
    },

    /**
     * 关闭所有通知
     */
    closeAll() {
      this.notifications.forEach(n => {
        if (n.timer) clearTimeout(n.timer)
        if (n.onClose) n.onClose()
      })
      this.notifications = []
    },

    /**
     * 启动定时器
     */
    startTimer(notification) {
      notification.timer = setTimeout(() => {
        this.close(notification.id)
      }, notification.duration)
    },

    /**
     * 鼠标悬停暂停
     */
    handleMouseEnter(notification) {
      if (notification.pauseOnHover && notification.timer) {
        clearTimeout(notification.timer)
      }
    },

    handleMouseLeave(notification) {
      if (notification.pauseOnHover && notification.duration > 0) {
        this.startTimer(notification)
      }
    },

    /**
     * 点击事件
     */
    handleClick(notification) {
      if (notification.onClick) {
        notification.onClick()
      }
    },

    /**
     * 获取通知类名
     */
    getNotificationClass(notification) {
      return [
        `notification-${notification.type}`,
        { 'notification-clickable': notification.onClick }
      ]
    },

    /**
     * 设置通知位置
     */
    setPosition(position) {
      this.position = position
    }
  }
}
</script>

<style scoped>
.notification-container {
  position: fixed;
  z-index: 10000;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 位置变体 */
.position-top-right {
  top: 20px;
  right: 20px;
}

.position-top-left {
  top: 20px;
  left: 20px;
}

.position-bottom-right {
  bottom: 20px;
  right: 20px;
  flex-direction: column-reverse;
}

.position-bottom-left {
  bottom: 20px;
  left: 20px;
  flex-direction: column-reverse;
}

.position-top-center {
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.position-bottom-center {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  flex-direction: column-reverse;
}

/* 通知项 */
.notification-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 320px;
  max-width: 420px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.15);
  pointer-events: auto;
  overflow: hidden;
  cursor: default;
}

.notification-clickable {
  cursor: pointer;
}

.notification-clickable:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

/* 图标 */
.notification-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-icon svg {
  width: 20px;
  height: 20px;
}

/* 内容 */
.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.notification-message {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  word-wrap: break-word;
}

/* 关闭按钮 */
.notification-close {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: #909399;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.notification-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #606266;
}

.notification-close svg {
  width: 14px;
  height: 14px;
}

/* 进度条 */
.notification-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 100%;
  transform-origin: left;
  animation: progress linear forwards;
}

@keyframes progress {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

/* 类型样式 */
.notification-success {
  border-left: 4px solid #67c23a;
}

.notification-success .notification-icon {
  color: #67c23a;
}

.notification-success .notification-progress {
  background: #67c23a;
}

.notification-warning {
  border-left: 4px solid #e6a23c;
}

.notification-warning .notification-icon {
  color: #e6a23c;
}

.notification-warning .notification-progress {
  background: #e6a23c;
}

.notification-error {
  border-left: 4px solid #f56c6c;
}

.notification-error .notification-icon {
  color: #f56c6c;
}

.notification-error .notification-progress {
  background: #f56c6c;
}

.notification-info {
  border-left: 4px solid #409eff;
}

.notification-info .notification-icon {
  color: #409eff;
}

.notification-info .notification-progress {
  background: #409eff;
}

/* 过渡动画 */
.notification-slide-enter-active,
.notification-slide-leave-active {
  transition: all 0.3s ease;
}

.notification-slide-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-slide-leave-to {
  opacity: 0;
  transform: translateX(-100%);
  margin-bottom: -100px;
}

/* 从左侧进入的动画 */
.position-top-left .notification-slide-enter-from,
.position-bottom-left .notification-slide-enter-from {
  transform: translateX(-100%);
}

.position-top-left .notification-slide-leave-to,
.position-bottom-left .notification-slide-leave-to {
  transform: translateX(100%);
}

/* 居中的动画 */
.position-top-center .notification-slide-enter-from,
.position-bottom-center .notification-slide-enter-from {
  transform: translateY(-100%);
}

.position-top-center .notification-slide-leave-to {
  transform: translateY(-100%);
}

.position-bottom-center .notification-slide-leave-to {
  transform: translateY(100%);
}

/* 响应式 */
@media (max-width: 768px) {
  .notification-container {
    left: 10px !important;
    right: 10px !important;
    transform: none !important;
  }

  .notification-item {
    min-width: auto;
    max-width: none;
  }
}
</style>
