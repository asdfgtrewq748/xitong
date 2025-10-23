<template>
  <div v-if="visible" class="error-overlay" @click="handleOverlayClick">
    <div class="error-container" @click.stop>
      <!-- 错误图标 -->
      <div class="error-icon" :class="errorTypeClass">
        <svg v-if="errorType === 'network'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <polyline points="9 22 9 12 15 12 15 22" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="1" y1="1" x2="23" y2="23" stroke-linecap="round" stroke-width="2"/>
        </svg>
        <svg v-else-if="errorType === 'validation'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="12" y1="8" x2="12" y2="12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="12" y1="16" x2="12.01" y2="16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        <svg v-else-if="errorType === 'server'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <rect x="2" y="2" width="20" height="8" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <rect x="2" y="14" width="20" height="8" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="6" y1="6" x2="6.01" y2="6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="6" y1="18" x2="6.01" y2="18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="15" y1="9" x2="9" y2="15" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="9" y1="9" x2="15" y2="15" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
      </div>

      <!-- 错误标题 -->
      <h3 class="error-title">{{ title }}</h3>

      <!-- 错误消息 -->
      <p class="error-message">{{ message }}</p>

      <!-- 解决方案 -->
      <div v-if="solutions.length > 0" class="solutions-section">
        <h4 class="solutions-title">建议的解决方法：</h4>
        <ul class="solutions-list">
          <li v-for="(solution, index) in solutions" :key="index">
            {{ solution }}
          </li>
        </ul>
      </div>

      <!-- 技术详情（可展开） -->
      <div v-if="technicalDetails" class="technical-details">
        <button class="toggle-details" @click="showDetails = !showDetails">
          <span>{{ showDetails ? '隐藏' : '查看' }}技术详情</span>
          <svg :class="{ rotated: showDetails }" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="6 9 12 15 18 9" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
        </button>
        <div v-show="showDetails" class="details-content">
          <pre>{{ technicalDetails }}</pre>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="error-actions">
        <button v-if="showRetry" class="btn-retry" @click="handleRetry">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="23 4 23 10 17 10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
          重试
        </button>
        <button v-if="showHelp" class="btn-help" @click="handleHelp">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <line x1="12" y1="17" x2="12.01" y2="17" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
          帮助
        </button>
        <button class="btn-close" @click="handleClose">关闭</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ErrorHandler',
  data() {
    return {
      visible: false,
      errorType: 'general', // 'network', 'validation', 'server', 'general'
      title: '',
      message: '',
      solutions: [],
      technicalDetails: '',
      showDetails: false,
      showRetry: false,
      showHelp: false,
      onRetry: null,
      onHelp: null
    }
  },
  computed: {
    errorTypeClass() {
      return `icon-${this.errorType}`
    }
  },
  methods: {
    /**
     * 显示错误
     * @param {Object} options - 错误配置
     * @param {String} options.type - 错误类型 network/validation/server/general
     * @param {String} options.title - 错误标题
     * @param {String} options.message - 错误消息
     * @param {Array} options.solutions - 解决方案列表
     * @param {String} options.technicalDetails - 技术详情
     * @param {Boolean} options.showRetry - 是否显示重试按钮
     * @param {Boolean} options.showHelp - 是否显示帮助按钮
     * @param {Function} options.onRetry - 重试回调
     * @param {Function} options.onHelp - 帮助回调
     */
    show(options = {}) {
      this.errorType = options.type || 'general'
      this.title = options.title || this.getDefaultTitle(this.errorType)
      this.message = options.message || '发生了一个错误'
      this.solutions = options.solutions || this.getDefaultSolutions(this.errorType)
      this.technicalDetails = options.technicalDetails || ''
      this.showRetry = options.showRetry !== undefined ? options.showRetry : this.shouldShowRetry(this.errorType)
      this.showHelp = options.showHelp !== undefined ? options.showHelp : true
      this.onRetry = options.onRetry || null
      this.onHelp = options.onHelp || null
      this.showDetails = false
      this.visible = true
    },

    hide() {
      this.visible = false
      this.showDetails = false
    },

    handleOverlayClick() {
      this.hide()
    },

    handleRetry() {
      if (this.onRetry) {
        this.onRetry()
      }
      this.hide()
    },

    handleHelp() {
      if (this.onHelp) {
        this.onHelp()
      } else {
        // 默认帮助行为：打开帮助文档或联系支持
        window.open('/help', '_blank')
      }
    },

    handleClose() {
      this.hide()
    },

    getDefaultTitle(type) {
      const titles = {
        network: '网络连接失败',
        validation: '数据验证失败',
        server: '服务器错误',
        general: '操作失败'
      }
      return titles[type] || titles.general
    },

    getDefaultSolutions(type) {
      const solutions = {
        network: [
          '检查您的网络连接是否正常',
          '尝试刷新页面重新加载',
          '如果使用VPN，请尝试关闭后重试',
          '检查防火墙是否阻止了连接'
        ],
        validation: [
          '检查输入的数据格式是否正确',
          '确保所有必填字段都已填写',
          '验证数据范围是否符合要求',
          '参考示例数据进行填写'
        ],
        server: [
          '服务器可能正在维护，请稍后重试',
          '刷新页面后重新尝试',
          '如果问题持续存在，请联系技术支持',
          '检查服务器状态页面了解更多信息'
        ],
        general: [
          '尝试刷新页面',
          '清除浏览器缓存后重试',
          '使用其他浏览器尝试',
          '如果问题持续，请联系技术支持'
        ]
      }
      return solutions[type] || solutions.general
    },

    shouldShowRetry(type) {
      // 网络错误和服务器错误默认显示重试按钮
      return type === 'network' || type === 'server'
    },

    /**
     * 从 Error 对象或 API 响应自动解析错误
     */
    showFromError(error) {
      let type = 'general'
      let title = ''
      let message = ''
      let technicalDetails = ''

      if (error.response) {
        // HTTP 错误响应
        const status = error.response.status
        if (status >= 500) {
          type = 'server'
          title = '服务器错误'
          message = '服务器遇到了问题，请稍后重试'
        } else if (status === 404) {
          type = 'general'
          title = '资源不存在'
          message = '请求的资源未找到'
        } else if (status === 403) {
          type = 'validation'
          title = '访问被拒绝'
          message = '您没有权限执行此操作'
        } else if (status === 400) {
          type = 'validation'
          title = '请求参数错误'
          message = error.response.data?.detail || '请检查输入的数据是否正确'
        }
        technicalDetails = JSON.stringify(error.response.data, null, 2)
      } else if (error.request) {
        // 网络错误（请求发出但没有响应）
        type = 'network'
        title = '网络连接失败'
        message = '无法连接到服务器，请检查网络连接'
        technicalDetails = error.message
      } else {
        // 其他错误
        type = 'general'
        title = '操作失败'
        message = error.message || '发生了未知错误'
        technicalDetails = error.stack || error.toString()
      }

      this.show({ type, title, message, technicalDetails })
    }
  }
}
</script>

<style scoped>
.error-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 0.2s ease-out;
  padding: 20px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.error-container {
  background: white;
  border-radius: 12px;
  padding: 32px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 错误图标 */
.error-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-icon svg {
  width: 36px;
  height: 36px;
}

.icon-network {
  background: #e8f4fd;
  color: #409eff;
}

.icon-validation {
  background: #fef0f0;
  color: #f56c6c;
}

.icon-server {
  background: #fdf6ec;
  color: #e6a23c;
}

.icon-general {
  background: #f4f4f5;
  color: #909399;
}

/* 标题和消息 */
.error-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  text-align: center;
}

.error-message {
  font-size: 15px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 20px 0;
  text-align: center;
}

/* 解决方案 */
.solutions-section {
  background: #f5f7fa;
  border-left: 4px solid #409eff;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.solutions-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.solutions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.solutions-list li {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  padding-left: 20px;
  position: relative;
  margin-bottom: 8px;
}

.solutions-list li:last-child {
  margin-bottom: 0;
}

.solutions-list li::before {
  content: '•';
  position: absolute;
  left: 8px;
  color: #409eff;
  font-weight: bold;
}

/* 技术详情 */
.technical-details {
  margin-bottom: 20px;
}

.toggle-details {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 8px;
  background: transparent;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-details:hover {
  border-color: #409eff;
  color: #409eff;
}

.toggle-details svg {
  width: 16px;
  height: 16px;
  margin-left: 6px;
  transition: transform 0.3s;
}

.toggle-details svg.rotated {
  transform: rotate(180deg);
}

.details-content {
  margin-top: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
}

.details-content pre {
  margin: 0;
  font-size: 12px;
  color: #606266;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', Courier, monospace;
}

/* 操作按钮 */
.error-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.error-actions button {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: flex;
  align-items: center;
  gap: 6px;
}

.error-actions button svg {
  width: 16px;
  height: 16px;
}

.btn-retry {
  background: #409eff;
  color: white;
}

.btn-retry:hover {
  background: #66b1ff;
}

.btn-help {
  background: #e8f4fd;
  color: #409eff;
}

.btn-help:hover {
  background: #d3e9fc;
}

.btn-close {
  background: #f4f4f5;
  color: #606266;
}

.btn-close:hover {
  background: #e9e9eb;
}

/* 滚动条样式 */
.error-container::-webkit-scrollbar {
  width: 8px;
}

.error-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.error-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

.error-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>
