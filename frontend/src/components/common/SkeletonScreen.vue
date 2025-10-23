<template>
  <div class="skeleton-container">
    <!-- 表格骨架屏 -->
    <div v-if="type === 'table'" class="skeleton-table">
      <div class="skeleton-table-header">
        <div v-for="col in columns" :key="col" class="skeleton-table-col skeleton-shimmer"></div>
      </div>
      <div v-for="row in rows" :key="row" class="skeleton-table-row">
        <div v-for="col in columns" :key="col" class="skeleton-table-cell skeleton-shimmer"></div>
      </div>
    </div>

    <!-- 卡片骨架屏 -->
    <div v-else-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-card-header">
        <div class="skeleton-avatar skeleton-shimmer"></div>
        <div class="skeleton-card-title">
          <div class="skeleton-line skeleton-shimmer" style="width: 60%"></div>
          <div class="skeleton-line skeleton-shimmer" style="width: 40%; margin-top: 8px"></div>
        </div>
      </div>
      <div class="skeleton-card-body">
        <div v-for="line in 3" :key="line" class="skeleton-line skeleton-shimmer" :style="getLineStyle(line)"></div>
      </div>
      <div class="skeleton-card-footer">
        <div class="skeleton-button skeleton-shimmer"></div>
        <div class="skeleton-button skeleton-shimmer"></div>
      </div>
    </div>

    <!-- 图表骨架屏 -->
    <div v-else-if="type === 'chart'" class="skeleton-chart">
      <div class="skeleton-chart-title skeleton-shimmer"></div>
      <div class="skeleton-chart-body">
        <div class="skeleton-chart-bars">
          <div v-for="bar in 5" :key="bar" class="skeleton-chart-bar" :style="{ height: getRandomHeight() }">
            <div class="skeleton-shimmer"></div>
          </div>
        </div>
        <div class="skeleton-chart-axis skeleton-shimmer"></div>
      </div>
    </div>

    <!-- 列表骨架屏 -->
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div v-for="item in rows" :key="item" class="skeleton-list-item">
        <div class="skeleton-list-icon skeleton-shimmer"></div>
        <div class="skeleton-list-content">
          <div class="skeleton-line skeleton-shimmer" style="width: 70%"></div>
          <div class="skeleton-line skeleton-shimmer" style="width: 50%; margin-top: 8px"></div>
        </div>
      </div>
    </div>

    <!-- 表单骨架屏 -->
    <div v-else-if="type === 'form'" class="skeleton-form">
      <div v-for="field in rows" :key="field" class="skeleton-form-field">
        <div class="skeleton-label skeleton-shimmer"></div>
        <div class="skeleton-input skeleton-shimmer"></div>
      </div>
      <div class="skeleton-form-actions">
        <div class="skeleton-button skeleton-shimmer"></div>
        <div class="skeleton-button skeleton-shimmer"></div>
      </div>
    </div>

    <!-- 文本骨架屏 -->
    <div v-else-if="type === 'text'" class="skeleton-text">
      <div v-for="line in rows" :key="line" class="skeleton-line skeleton-shimmer" :style="getLineStyle(line)"></div>
    </div>

    <!-- 自定义骨架屏 -->
    <div v-else class="skeleton-custom">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SkeletonScreen',
  props: {
    type: {
      type: String,
      default: 'text', // 'table', 'card', 'chart', 'list', 'form', 'text', 'custom'
      validator: (value) => ['table', 'card', 'chart', 'list', 'form', 'text', 'custom'].includes(value)
    },
    rows: {
      type: Number,
      default: 3
    },
    columns: {
      type: Number,
      default: 4
    },
    animated: {
      type: Boolean,
      default: true
    }
  },
  methods: {
    getLineStyle(index) {
      const widths = ['100%', '95%', '85%', '90%', '80%']
      return {
        width: widths[index % widths.length]
      }
    },
    getRandomHeight() {
      const heights = ['40%', '60%', '80%', '100%', '70%']
      return heights[Math.floor(Math.random() * heights.length)]
    }
  }
}
</script>

<style scoped>
/* 基础骨架容器 */
.skeleton-container {
  width: 100%;
}

/* 闪烁动画 */
.skeleton-shimmer {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 表格骨架 */
.skeleton-table {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.skeleton-table-header {
  display: flex;
  gap: 1px;
  background: #f5f7fa;
  padding: 12px;
}

.skeleton-table-col {
  flex: 1;
  height: 20px;
  border-radius: 4px;
}

.skeleton-table-row {
  display: flex;
  gap: 1px;
  padding: 12px;
  border-top: 1px solid #e4e7ed;
}

.skeleton-table-cell {
  flex: 1;
  height: 16px;
  border-radius: 4px;
}

/* 卡片骨架 */
.skeleton-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.skeleton-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 16px;
  flex-shrink: 0;
}

.skeleton-card-title {
  flex: 1;
}

.skeleton-card-body {
  margin-bottom: 16px;
}

.skeleton-card-footer {
  display: flex;
  gap: 12px;
}

/* 图表骨架 */
.skeleton-chart {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.skeleton-chart-title {
  height: 24px;
  width: 40%;
  border-radius: 4px;
  margin-bottom: 20px;
}

.skeleton-chart-body {
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.skeleton-chart-bars {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 20px;
  margin-bottom: 12px;
}

.skeleton-chart-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.skeleton-chart-bar > div {
  width: 100%;
  height: 100%;
  border-radius: 4px 4px 0 0;
}

.skeleton-chart-axis {
  height: 2px;
  width: 100%;
  border-radius: 1px;
}

/* 列表骨架 */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: white;
}

.skeleton-list-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  margin-right: 16px;
  flex-shrink: 0;
}

.skeleton-list-content {
  flex: 1;
}

/* 表单骨架 */
.skeleton-form {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 24px;
  background: white;
}

.skeleton-form-field {
  margin-bottom: 20px;
}

.skeleton-label {
  height: 16px;
  width: 100px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-input {
  height: 40px;
  width: 100%;
  border-radius: 4px;
}

.skeleton-form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

/* 文本骨架 */
.skeleton-text {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-line {
  height: 16px;
  border-radius: 4px;
}

/* 按钮骨架 */
.skeleton-button {
  height: 36px;
  width: 80px;
  border-radius: 6px;
}

/* 响应式 */
@media (max-width: 768px) {
  .skeleton-card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .skeleton-avatar {
    margin-bottom: 12px;
  }

  .skeleton-chart-body {
    height: 200px;
  }

  .skeleton-table-row,
  .skeleton-table-header {
    padding: 8px;
  }
}
</style>
