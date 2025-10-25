<template>
  <el-drawer
    v-model="drawerVisible"
    title="快速操作"
    direction="rtl"
    size="400px"
    :before-close="handleClose"
  >
    <div class="quick-actions-content">
      <!-- 常用操作 -->
      <div class="action-section">
        <h4 class="section-title">
          <el-icon><Operation /></el-icon>
          常用操作
        </h4>
        <div class="action-grid">
          <div
            v-for="action in commonActions"
            :key="action.key"
            class="action-item"
            @click="executeAction(action)"
          >
            <div class="action-icon" :style="{ background: action.color }">
              <el-icon>
                <component :is="action.icon" />
              </el-icon>
            </div>
            <div class="action-info">
              <div class="action-name">{{ action.name }}</div>
              <div class="action-description">{{ action.description }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 图表模板 -->
      <div class="action-section">
        <h4 class="section-title">
          <el-icon><Document /></el-icon>
          图表模板
        </h4>
        <div class="template-list">
          <div
            v-for="template in chartTemplates"
            :key="template.id"
            class="template-item"
            @click="applyTemplate(template)"
          >
            <div class="template-preview">
              <img
                :src="template.preview"
                :alt="template.name"
                class="template-image"
              />
            </div>
            <div class="template-info">
              <div class="template-name">{{ template.name }}</div>
              <div class="template-description">{{ template.description }}</div>
              <div class="template-tags">
                <el-tag
                  v-for="tag in template.tags"
                  :key="tag"
                  size="small"
                  type="info"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷键 -->
      <div class="action-section">
        <h4 class="section-title">
          <el-icon><Keyboard /></el-icon>
          快捷键
        </h4>
        <div class="shortcut-list">
          <div
            v-for="shortcut in shortcuts"
            :key="shortcut.key"
            class="shortcut-item"
          >
            <div class="shortcut-info">
              <div class="shortcut-name">{{ shortcut.name }}</div>
              <div class="shortcut-description">{{ shortcut.description }}</div>
            </div>
            <div class="shortcut-keys">
              <kbd
                v-for="key in shortcut.keys"
                :key="key"
                class="shortcut-key"
              >
                {{ key }}
              </kbd>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近操作 -->
      <div class="action-section" v-if="recentActions.length > 0">
        <h4 class="section-title">
          <el-icon><Clock /></el-icon>
          最近操作
        </h4>
        <div class="recent-list">
          <div
            v-for="action in recentActions"
            :key="action.id"
            class="recent-item"
            @click="executeRecentAction(action)"
          >
            <el-icon class="recent-icon">
              <component :is="action.icon" />
            </el-icon>
            <div class="recent-info">
              <div class="recent-name">{{ action.name }}</div>
              <div class="recent-time">{{ formatTime(action.timestamp) }}</div>
            </div>
            <el-button
              text
              type="primary"
              size="small"
              @click.stop="executeRecentAction(action)"
            >
              重复
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Operation, Document, Keyboard, Clock
} from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'action'])

// 抽屉可见性
const drawerVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 常用操作
const commonActions = ref([
  {
    key: 'import-data',
    name: '导入数据',
    description: '导入CSV或JSON数据文件',
    icon: 'Upload',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    action: 'import'
  },
  {
    key: 'auto-config',
    name: '智能配置',
    description: '自动配置图表参数',
    icon: 'Setting',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    action: 'auto-config'
  },
  {
    key: 'export-chart',
    name: '导出图表',
    description: '导出为PNG或SVG格式',
    icon: 'Download',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    action: 'export'
  },
  {
    key: 'reset-view',
    name: '重置视图',
    description: '恢复图表默认视图',
    icon: 'RefreshLeft',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    action: 'reset'
  },
  {
    key: 'share-chart',
    name: '分享图表',
    description: '生成分享链接',
    icon: 'Share',
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    action: 'share'
  },
  {
    key: 'data-analysis',
    name: '数据分析',
    description: '查看数据统计信息',
    icon: 'DataAnalysis',
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    action: 'analysis'
  }
])

// 图表模板
const chartTemplates = ref([
  {
    id: 'correlation-analysis',
    name: '相关性分析',
    description: '用于分析两个变量之间的相关关系',
    preview: '/api/placeholder/60/40',
    tags: ['散点图', '相关性', '回归分析'],
    config: {
      type: 'scatter',
      title: '相关性分析',
      showLegend: true,
      showGrid: true,
      colorScheme: 'viridis'
    }
  },
  {
    id: 'time-series',
    name: '时间序列分析',
    description: '展示数据随时间的变化趋势',
    preview: '/api/placeholder/60/40',
    tags: ['折线图', '趋势', '时间'],
    config: {
      type: 'line',
      title: '时间序列分析',
      showLegend: true,
      showGrid: true,
      smooth: true,
      colorScheme: 'plasma'
    }
  },
  {
    id: 'distribution-analysis',
    name: '分布分析',
    description: '分析数据的分布特征和统计信息',
    preview: '/api/placeholder/60/40',
    tags: ['直方图', '分布', '统计'],
    config: {
      type: 'histogram',
      title: '数据分布分析',
      colorScheme: 'coolwarm',
      binCount: 20
    }
  },
  {
    id: 'comparison-analysis',
    name: '对比分析',
    description: '比较多组数据之间的差异',
    preview: '/api/placeholder/60/40',
    tags: ['柱状图', '对比', '分组'],
    config: {
      type: 'bar',
      title: '数据对比分析',
      showLegend: true,
      colorScheme: 'jet'
    }
  }
])

// 快捷键
const shortcuts = ref([
  {
    key: 'import',
    name: '导入数据',
    description: '快速导入数据文件',
    keys: ['Ctrl', 'O']
  },
  {
    key: 'export',
    name: '导出图表',
    description: '导出当前图表',
    keys: ['Ctrl', 'S']
  },
  {
    key: 'auto-config',
    name: '智能配置',
    description: '自动配置图表参数',
    keys: ['Ctrl', 'A']
  },
  {
    key: 'reset',
    name: '重置视图',
    description: '恢复默认视图',
    keys: ['Ctrl', 'R']
  },
  {
    key: 'fullscreen',
    name: '全屏模式',
    description: '切换全屏显示',
    keys: ['F11']
  }
])

// 最近操作
const recentActions = ref([
  {
    id: '1',
    name: '导入数据集',
    timestamp: Date.now() - 300000, // 5分钟前
    icon: 'Upload',
    action: 'import'
  },
  {
    id: '2',
    name: '应用散点图模板',
    timestamp: Date.now() - 600000, // 10分钟前
    icon: 'TrendCharts',
    action: 'apply-template',
    templateId: 'correlation-analysis'
  },
  {
    id: '3',
    name: '导出PNG图表',
    timestamp: Date.now() - 900000, // 15分钟前
    icon: 'Download',
    action: 'export',
    format: 'png'
  }
])

// 方法
const handleClose = (done) => {
  done()
}

const executeAction = (action) => {
  emit('action', action.action)
  addToRecentActions(action)
  drawerVisible.value = false
}

const applyTemplate = (template) => {
  emit('action', {
    type: 'apply-template',
    template: template
  })
  addToRecentActions({
    name: `应用${template.name}模板`,
    icon: 'Document',
    action: 'apply-template',
    templateId: template.id
  })
  drawerVisible.value = false
  ElMessage.success(`已应用模板: ${template.name}`)
}

const executeRecentAction = (action) => {
  if (action.action === 'apply-template') {
    const template = chartTemplates.value.find(t => t.id === action.templateId)
    if (template) {
      applyTemplate(template)
      return
    }
  }

  emit('action', action.action)
  ElMessage.success(`已执行操作: ${action.name}`)
}

const addToRecentActions = (action) => {
  const newAction = {
    id: Date.now().toString(),
    name: action.name,
    timestamp: Date.now(),
    icon: action.icon,
    action: action.action
  }

  recentActions.value.unshift(newAction)

  // 只保留最近10条操作
  if (recentActions.value.length > 10) {
    recentActions.value = recentActions.value.slice(0, 10)
  }
}

const formatTime = (timestamp) => {
  const now = Date.now()
  const diff = now - timestamp

  if (diff < 60000) { // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) { // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 1天内
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return `${Math.floor(diff / 86400000)}天前`
  }
}

// 键盘事件监听
const handleKeyDown = (event) => {
  const key = event.key.toUpperCase()
  const ctrl = event.ctrlKey || event.metaKey

  // Ctrl+O: 导入数据
  if (ctrl && key === 'O') {
    event.preventDefault()
    executeAction(commonActions.value.find(a => a.key === 'import-data'))
  }

  // Ctrl+S: 导出图表
  if (ctrl && key === 'S') {
    event.preventDefault()
    executeAction(commonActions.value.find(a => a.key === 'export-chart'))
  }

  // Ctrl+A: 智能配置
  if (ctrl && key === 'A') {
    event.preventDefault()
    executeAction(commonActions.value.find(a => a.key === 'auto-config'))
  }

  // Ctrl+R: 重置视图
  if (ctrl && key === 'R') {
    event.preventDefault()
    executeAction(commonActions.value.find(a => a.key === 'reset-view'))
  }

  // F11: 全屏
  if (key === 'F11') {
    event.preventDefault()
    emit('action', 'fullscreen')
  }
}

// 监听键盘事件
watch(drawerVisible, (visible) => {
  if (visible) {
    document.addEventListener('keydown', handleKeyDown)
  } else {
    document.removeEventListener('keydown', handleKeyDown)
  }
})
</script>

<style scoped>
.quick-actions-content {
  padding: 16px;
}

.action-section {
  margin-bottom: 24px;
}

.action-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 常用操作网��� */
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fafbfc;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-item:hover {
  background: #f0f9ff;
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.action-info {
  flex: 1;
  min-width: 0;
}

.action-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.action-description {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

/* 图表模板 */
.template-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.template-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fafbfc;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.template-item:hover {
  background: #f0f9ff;
  border-color: #409eff;
}

.template-preview {
  width: 60px;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.template-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.template-description {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
  line-height: 1.4;
}

.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 快捷键列表 */
.shortcut-list {
  background: #fafbfc;
  border-radius: 8px;
  overflow: hidden;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.shortcut-item:last-child {
  border-bottom: none;
}

.shortcut-info {
  flex: 1;
}

.shortcut-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.shortcut-description {
  font-size: 12px;
  color: #909399;
}

.shortcut-keys {
  display: flex;
  gap: 4px;
}

.shortcut-key {
  display: inline-block;
  padding: 4px 8px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 11px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  color: #606266;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 最近操作 */
.recent-list {
  background: #fafbfc;
  border-radius: 8px;
  overflow: hidden;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-item:hover {
  background: #f0f9ff;
}

.recent-icon {
  color: #409eff;
  font-size: 16px;
}

.recent-info {
  flex: 1;
}

.recent-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.recent-time {
  font-size: 12px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .action-grid {
    grid-template-columns: 1fr;
  }

  .template-item {
    flex-direction: column;
    text-align: center;
  }

  .shortcut-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .recent-item {
    flex-wrap: wrap;
  }
}

/* 抽屉样式调整 */
:deep(.el-drawer__header) {
  margin-bottom: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-drawer__body) {
  padding: 0;
}

:deep(.el-drawer__title) {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
</style>
