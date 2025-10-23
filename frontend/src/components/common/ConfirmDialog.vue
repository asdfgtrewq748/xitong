<template>
  <div v-if="visible" class="confirm-overlay" @click="handleOverlayClick">
    <div class="confirm-container" @click.stop>
      <!-- 确认图标 -->
      <div class="confirm-icon" :class="iconTypeClass">
        <svg v-if="type === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="12" y1="9" x2="12" y2="13" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="12" y1="17" x2="12.01" y2="17" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        <svg v-else-if="type === 'danger'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="15" y1="9" x2="9" y2="15" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="9" y1="9" x2="15" y2="15" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        <svg v-else-if="type === 'info'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="12" y1="16" x2="12" y2="12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <line x1="12" y1="8" x2="12.01" y2="8" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>
      </div>

      <!-- 标题 -->
      <h3 class="confirm-title">{{ title }}</h3>

      <!-- 消息内容 -->
      <p class="confirm-message">{{ message }}</p>

      <!-- 详细信息 -->
      <div v-if="details" class="confirm-details">
        <div class="details-label">详细信息：</div>
        <div class="details-content">{{ details }}</div>
      </div>

      <!-- 复选框选项（用于"不再提示"等） -->
      <div v-if="showCheckbox" class="confirm-checkbox">
        <label>
          <input type="checkbox" v-model="checkboxValue" />
          <span>{{ checkboxLabel }}</span>
        </label>
      </div>

      <!-- 操作按钮 -->
      <div class="confirm-actions">
        <button
          v-if="showCancel"
          class="btn-cancel"
          @click="handleCancel"
          :disabled="loading"
        >
          {{ cancelText }}
        </button>
        <button
          class="btn-confirm"
          :class="confirmButtonClass"
          @click="handleConfirm"
          :disabled="loading"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span>{{ loading ? loadingText : confirmText }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmDialog',
  data() {
    return {
      visible: false,
      type: 'warning', // 'warning', 'danger', 'info', 'success'
      title: '',
      message: '',
      details: '',
      confirmText: '确定',
      cancelText: '取消',
      showCancel: true,
      showCheckbox: false,
      checkboxLabel: '不再提示',
      checkboxValue: false,
      loading: false,
      loadingText: '处理中...',
      onConfirm: null,
      onCancel: null,
      closeOnConfirm: true
    }
  },
  computed: {
    iconTypeClass() {
      return `icon-${this.type}`
    },
    confirmButtonClass() {
      return {
        'btn-warning': this.type === 'warning',
        'btn-danger': this.type === 'danger',
        'btn-info': this.type === 'info',
        'btn-success': this.type === 'success',
        'btn-loading': this.loading
      }
    }
  },
  methods: {
    /**
     * 显示确认对话框
     * @param {Object} options - 配置选项
     */
    show(options = {}) {
      this.type = options.type || 'warning'
      this.title = options.title || '确认操作'
      this.message = options.message || '确定要执行此操作吗？'
      this.details = options.details || ''
      this.confirmText = options.confirmText || '确定'
      this.cancelText = options.cancelText || '取消'
      this.showCancel = options.showCancel !== false
      this.showCheckbox = options.showCheckbox || false
      this.checkboxLabel = options.checkboxLabel || '不再提示'
      this.checkboxValue = false
      this.loadingText = options.loadingText || '处理中...'
      this.onConfirm = options.onConfirm || null
      this.onCancel = options.onCancel || null
      this.closeOnConfirm = options.closeOnConfirm !== false
      this.loading = false
      this.visible = true

      return new Promise((resolve, reject) => {
        this._resolve = resolve
        this._reject = reject
      })
    },

    hide() {
      this.visible = false
      this.loading = false
    },

    handleOverlayClick() {
      if (!this.loading) {
        this.handleCancel()
      }
    },

    async handleConfirm() {
      if (this.loading) return

      try {
        if (this.onConfirm) {
          this.loading = true
          const result = await this.onConfirm(this.checkboxValue)
          this.loading = false

          if (this.closeOnConfirm) {
            this.hide()
          }

          if (this._resolve) {
            this._resolve({ confirmed: true, checkboxValue: this.checkboxValue, result })
          }
        } else {
          this.hide()
          if (this._resolve) {
            this._resolve({ confirmed: true, checkboxValue: this.checkboxValue })
          }
        }
      } catch (error) {
        this.loading = false
        console.error('[ConfirmDialog] 确认操作失败:', error)

        // 如果有错误，不自动关闭对话框
        if (this._reject) {
          this._reject(error)
        }
      }
    },

    handleCancel() {
      if (this.loading) return

      if (this.onCancel) {
        this.onCancel()
      }

      this.hide()

      if (this._resolve) {
        this._resolve({ confirmed: false, checkboxValue: this.checkboxValue })
      }
    },

    /**
     * 便捷方法：显示删除确认对话框
     */
    confirmDelete(itemName = '此项', options = {}) {
      return this.show({
        type: 'danger',
        title: '确认删除',
        message: `确定要删除${itemName}吗？`,
        details: '此操作无法撤销',
        confirmText: '删除',
        cancelText: '取消',
        ...options
      })
    },

    /**
     * 便捷方法：显示保存确认对话框
     */
    confirmSave(message = '确定要保存更改吗？', options = {}) {
      return this.show({
        type: 'info',
        title: '保存更改',
        message,
        confirmText: '保存',
        cancelText: '取消',
        ...options
      })
    },

    /**
     * 便捷方法：显示离开确认对话框
     */
    confirmLeave(message = '当前有未保存的更改，确定要离开吗？', options = {}) {
      return this.show({
        type: 'warning',
        title: '离开提醒',
        message,
        details: '未保存的更改将会丢失',
        confirmText: '离开',
        cancelText: '继续编辑',
        ...options
      })
    }
  }
}
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.confirm-container {
  background: white;
  border-radius: 12px;
  padding: 32px;
  max-width: 480px;
  width: 90%;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 图标样式 */
.confirm-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-icon svg {
  width: 32px;
  height: 32px;
}

.icon-warning {
  background: #fef0f0;
  color: #e6a23c;
}

.icon-danger {
  background: #fef0f0;
  color: #f56c6c;
}

.icon-info {
  background: #e8f4fd;
  color: #409eff;
}

.icon-success {
  background: #f0f9ff;
  color: #67c23a;
}

/* 标题和消息 */
.confirm-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  text-align: center;
}

.confirm-message {
  font-size: 15px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 16px 0;
  text-align: center;
}

/* 详细信息 */
.confirm-details {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
}

.details-label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 6px;
}

.details-content {
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
}

/* 复选框 */
.confirm-checkbox {
  margin-bottom: 20px;
  text-align: center;
}

.confirm-checkbox label {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.confirm-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  cursor: pointer;
}

.confirm-checkbox span {
  font-size: 14px;
  color: #606266;
}

/* 操作按钮 */
.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.confirm-actions button {
  flex: 1;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.confirm-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-cancel {
  background: #f4f4f5;
  color: #606266;
}

.btn-cancel:not(:disabled):hover {
  background: #e9e9eb;
}

.btn-confirm {
  color: white;
}

.btn-warning {
  background: #e6a23c;
}

.btn-warning:not(:disabled):hover {
  background: #ebb563;
}

.btn-danger {
  background: #f56c6c;
}

.btn-danger:not(:disabled):hover {
  background: #f78989;
}

.btn-info {
  background: #409eff;
}

.btn-info:not(:disabled):hover {
  background: #66b1ff;
}

.btn-success {
  background: #67c23a;
}

.btn-success:not(:disabled):hover {
  background: #85ce61;
}

/* 加载动画 */
.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .confirm-container {
    padding: 24px;
  }

  .confirm-actions {
    flex-direction: column-reverse;
  }

  .confirm-actions button {
    width: 100%;
  }
}
</style>
