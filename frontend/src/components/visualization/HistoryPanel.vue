<template>
  <div class="history-panel">
    <div class="header">
      <h4>
        <el-icon><Clock /></el-icon>
        配置历史
      </h4>
      <el-button size="small" text @click="clearHistory" :disabled="!historyList.length">
        <el-icon><Delete /></el-icon>
        清空
      </el-button>
    </div>

    <el-empty 
      v-if="!historyList.length" 
      description="暂无历史记录"
      :image-size="60"
    />

    <el-timeline v-else style="padding: 12px 0; max-height: 400px; overflow-y: auto;">
      <el-timeline-item
        v-for="(item, index) in historyList"
        :key="item.id"
        :timestamp="formatTime(item.timestamp)"
        placement="top"
        :color="index === currentIndex ? '#409EFF' : '#909399'"
      >
        <el-card shadow="hover" :class="{ 'active-history': index === currentIndex }">
          <div class="history-item">
            <div class="history-title">
              <el-tag size="small" :type="getChartTypeTag(item.config.type)">
                {{ getChartTypeName(item.config.type) }}
              </el-tag>
              <span style="margin-left: 8px; font-size: 12px; color: #606266;">
                {{ item.config.title || '未命名图表' }}
              </span>
            </div>
            
            <div class="history-details">
              <el-descriptions :column="1" size="small">
                <el-descriptions-item label="X">{{ item.config.xField || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Y">{{ item.config.yField || '-' }}</el-descriptions-item>
                <el-descriptions-item v-if="item.config.zField" label="Z">{{ item.config.zField }}</el-descriptions-item>
              </el-descriptions>
            </div>
            
            <div class="history-actions">
              <el-button size="small" @click="restoreConfig(item)" :disabled="index === currentIndex">
                <el-icon><RefreshLeft /></el-icon>
                恢复
              </el-button>
              <el-button size="small" text type="danger" @click="deleteHistoryItem(item.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { computed } from 'vue'
import { Clock, Delete, RefreshLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useVisualizationStore } from '../../stores/visualizationStore'

const store = useVisualizationStore()
const emit = defineEmits(['restore'])

const historyList = computed(() => store.history || [])
const currentIndex = computed(() => store.currentHistoryIndex || 0)

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

function getChartTypeName(type) {
  const names = {
    scatter: '散点图',
    line: '折线图',
    heatmap: '热力图',
    surface: '三维曲面'
  }
  return names[type] || type
}

function getChartTypeTag(type) {
  const tags = {
    scatter: '',
    line: 'success',
    heatmap: 'warning',
    surface: 'danger'
  }
  return tags[type] || ''
}

function restoreConfig(item) {
  emit('restore', item.config)
  ElMessage.success('配置已恢复')
}

function deleteHistoryItem(id) {
  store.removeHistoryItem(id)
  ElMessage.success('历史记录已删除')
}

function clearHistory() {
  ElMessageBox.confirm('确定要清空所有历史记录吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    store.clearHistory()
    ElMessage.success('历史记录已清空')
  }).catch(() => {
    // 用户取消
  })
}
</script>

<style scoped>
.history-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
}

.history-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-title {
  display: flex;
  align-items: center;
}

.history-details {
  font-size: 12px;
}

.history-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.active-history {
  border: 2px solid #409EFF;
}

:deep(.el-timeline-item__timestamp) {
  font-size: 11px;
  color: #909399;
}

:deep(.el-card__body) {
  padding: 12px;
}

:deep(.el-descriptions__label) {
  width: 30px;
  font-weight: 500;
}

:deep(.el-descriptions__content) {
  font-size: 12px;
  color: #606266;
}
</style>
