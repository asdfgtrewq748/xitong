<template>
  <div v-if="visible" class="global-loading-overlay">
    <div class="loading-container">
      <!-- 加载动画 -->
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
      </div>

      <!-- 加载文本 -->
      <div class="loading-text">{{ message }}</div>

      <!-- 进度条（可选） -->
      <div v-if="showProgress" class="loading-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="progress-text">{{ progress }}%</div>
      </div>

      <!-- 提示信息 -->
      <div v-if="tip" class="loading-tip">{{ tip }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GlobalLoading',
  data() {
    return {
      visible: false,
      message: '加载中...',
      progress: 0,
      showProgress: false,
      tip: ''
    }
  },
  methods: {
    show(options = {}) {
      this.message = options.message || '加载中...'
      this.progress = options.progress || 0
      this.showProgress = options.showProgress || false
      this.tip = options.tip || ''
      this.visible = true
    },
    hide() {
      this.visible = false
      this.progress = 0
      this.showProgress = false
      this.tip = ''
    },
    updateProgress(progress, message) {
      this.progress = Math.min(100, Math.max(0, progress))
      if (message) this.message = message
    }
  }
}
</script>

<style scoped>
.global-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.loading-container {
  text-align: center;
  color: white;
  max-width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* 三环加载动画 */
.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 4px solid transparent;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.spinner-ring:nth-child(2) {
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
  border-top-color: #67c23a;
  animation-delay: 0.2s;
}

.spinner-ring:nth-child(3) {
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
  border-top-color: #e6a23c;
  animation-delay: 0.4s;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 16px;
  color: #fff;
}

.loading-progress {
  margin-top: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.loading-tip {
  margin-top: 12px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}
</style>
