<template>
  <div class="empty-state" :class="sizeClass">
    <!-- 图标/图片 -->
    <div class="empty-icon" :class="typeClass">
      <!-- 内置SVG图标 -->
      <svg v-if="type === 'no-data'" viewBox="0 0 64 64" fill="none">
        <rect x="10" y="20" width="44" height="32" rx="2" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="28" x2="54" y2="28" stroke="currentColor" stroke-width="2"/>
        <circle cx="18" cy="24" r="1.5" fill="currentColor"/>
        <circle cx="24" cy="24" r="1.5" fill="currentColor"/>
        <circle cx="30" cy="24" r="1.5" fill="currentColor"/>
        <path d="M20 36 L32 44 L44 32" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.3"/>
      </svg>

      <svg v-else-if="type === 'no-search'" viewBox="0 0 64 64" fill="none">
        <circle cx="28" cy="28" r="14" stroke="currentColor" stroke-width="2"/>
        <line x1="38" y1="38" x2="50" y2="50" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="22" y1="28" x2="34" y2="28" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="28" y1="22" x2="28" y2="34" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>

      <svg v-else-if="type === 'error'" viewBox="0 0 64 64" fill="none">
        <circle cx="32" cy="32" r="20" stroke="currentColor" stroke-width="2"/>
        <line x1="26" y1="26" x2="38" y2="38" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="38" y1="26" x2="26" y2="38" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>

      <svg v-else-if="type === 'network'" viewBox="0 0 64 64" fill="none">
        <rect x="12" y="12" width="40" height="28" rx="2" stroke="currentColor" stroke-width="2"/>
        <line x1="16" y1="44" x2="48" y2="44" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="28" y1="40" x2="32" y2="44" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <line x1="18" y1="20" x2="46" y2="32" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.3"/>
        <circle cx="46" cy="20" r="3" fill="currentColor"/>
      </svg>

      <svg v-else-if="type === 'permission'" viewBox="0 0 64 64" fill="none">
        <rect x="20" y="28" width="24" height="20" rx="2" stroke="currentColor" stroke-width="2"/>
        <path d="M24 28 V22 A8 8 0 0 1 40 22 V28" stroke="currentColor" stroke-width="2"/>
        <circle cx="32" cy="38" r="2" fill="currentColor"/>
      </svg>

      <svg v-else viewBox="0 0 64 64" fill="none">
        <rect x="16" y="24" width="32" height="24" rx="2" stroke="currentColor" stroke-width="2"/>
        <path d="M16 32 L32 42 L48 32" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="32" y1="42" x2="32" y2="48" stroke="currentColor" stroke-width="2"/>
      </svg>

      <!-- 自定义图片 -->
      <img v-if="image" :src="image" :alt="title" class="custom-image" />
    </div>

    <!-- 标题 -->
    <h3 v-if="title" class="empty-title">{{ title }}</h3>

    <!-- 描述 -->
    <p v-if="description" class="empty-description">{{ description }}</p>

    <!-- 操作按钮 -->
    <div v-if="$slots.actions || actionText" class="empty-actions">
      <slot name="actions">
        <button v-if="actionText" class="btn-action" @click="handleAction">
          {{ actionText }}
        </button>
      </slot>
    </div>

    <!-- 额外内容 -->
    <div v-if="$slots.default" class="empty-extra">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    type: {
      type: String,
      default: 'no-data', // 'no-data', 'no-search', 'error', 'network', 'permission', 'custom'
      validator: (value) => ['no-data', 'no-search', 'error', 'network', 'permission', 'custom'].includes(value)
    },
    title: {
      type: String,
      default: ''
    },
    description: {
      type: String,
      default: ''
    },
    image: {
      type: String,
      default: ''
    },
    actionText: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: 'medium', // 'small', 'medium', 'large'
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    }
  },
  computed: {
    typeClass() {
      return `icon-${this.type}`
    },
    sizeClass() {
      return `size-${this.size}`
    }
  },
  methods: {
    handleAction() {
      this.$emit('action')
    },

    /**
     * 获取默认标题
     */
    getDefaultTitle() {
      const titles = {
        'no-data': '暂无数据',
        'no-search': '未找到匹配结果',
        'error': '加载失败',
        'network': '网络连接失败',
        'permission': '无访问权限'
      }
      return this.title || titles[this.type] || '暂无内容'
    },

    /**
     * 获取默认描述
     */
    getDefaultDescription() {
      const descriptions = {
        'no-data': '当前没有可显示的数据',
        'no-search': '请尝试使用其他关键词搜索',
        'error': '数据加载出现问题，请稍后重试',
        'network': '请检查网络连接后重试',
        'permission': '您没有权限查看此内容'
      }
      return this.description || descriptions[this.type] || ''
    }
  }
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

/* 尺寸变体 */
.size-small {
  padding: 24px 16px;
}

.size-small .empty-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
}

.size-small .empty-title {
  font-size: 15px;
  margin-bottom: 8px;
}

.size-small .empty-description {
  font-size: 13px;
}

.size-medium {
  padding: 40px 20px;
}

.size-medium .empty-icon {
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
}

.size-medium .empty-title {
  font-size: 18px;
  margin-bottom: 12px;
}

.size-medium .empty-description {
  font-size: 14px;
}

.size-large {
  padding: 60px 30px;
}

.size-large .empty-icon {
  width: 160px;
  height: 160px;
  margin-bottom: 24px;
}

.size-large .empty-title {
  font-size: 20px;
  margin-bottom: 16px;
}

.size-large .empty-description {
  font-size: 15px;
}

/* 图标 */
.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.empty-icon svg {
  width: 60%;
  height: 60%;
}

/* 图标颜色 */
.icon-no-data {
  background: #f5f7fa;
  color: #909399;
}

.icon-no-search {
  background: #e8f4fd;
  color: #409eff;
}

.icon-error {
  background: #fef0f0;
  color: #f56c6c;
}

.icon-network {
  background: #fdf6ec;
  color: #e6a23c;
}

.icon-permission {
  background: #fef0f0;
  color: #f56c6c;
}

.icon-custom {
  background: #f5f7fa;
  color: #909399;
}

.custom-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* 标题和描述 */
.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.empty-description {
  font-size: 14px;
  color: #909399;
  line-height: 1.6;
  margin: 0;
  max-width: 400px;
}

/* 操作按钮 */
.empty-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-action {
  padding: 10px 24px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action:hover {
  background: #66b1ff;
}

/* 额外内容 */
.empty-extra {
  margin-top: 16px;
  color: #909399;
  font-size: 13px;
}

/* 动画效果 */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.empty-icon:hover {
  animation: float 2s ease-in-out infinite;
}

/* 响应式 */
@media (max-width: 768px) {
  .empty-state {
    padding: 30px 16px;
  }

  .size-large {
    padding: 40px 20px;
  }

  .size-large .empty-icon {
    width: 120px;
    height: 120px;
  }
}
</style>
