<template>
  <div class="data-statistics-panel">
    <!-- 数据概览 -->
    <div class="stats-overview">
      <h4>数据概览</h4>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ data.length }}</div>
          <div class="stat-label">总行数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ fields.length }}</div>
          <div class="stat-label">字段数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ numericFields.length }}</div>
          <div class="stat-label">数值字段</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ categoricalFields.length }}</div>
          <div class="stat-label">分类字段</div>
        </div>
      </div>
    </div>

    <!-- 字段统计 -->
    <div class="field-statistics">
      <h4>字段统计</h4>
      <div class="field-tabs">
        <el-tabs v-model="activeFieldTab" type="border-card">
          <el-tab-pane
            v-for="field in numericFields"
            :key="field.name"
            :label="field.name"
            :name="field.name"
          >
            <div class="field-stats">
              <div class="stats-row">
                <div class="stat-box">
                  <div class="stat-title">基本统计</div>
                  <div class="stat-values">
                    <div class="stat-value-item">
                      <span class="label">最小值:</span>
                      <span class="value">{{ formatNumber(field.stats.min) }}</span>
                    </div>
                    <div class="stat-value-item">
                      <span class="label">最大值:</span>
                      <span class="value">{{ formatNumber(field.stats.max) }}</span>
                    </div>
                    <div class="stat-value-item">
                      <span class="label">平均值:</span>
                      <span class="value">{{ formatNumber(field.stats.mean) }}</span>
                    </div>
                    <div class="stat-value-item">
                      <span class="label">中位数:</span>
                      <span class="value">{{ formatNumber(field.stats.median) }}</span>
                    </div>
                    <div class="stat-value-item">
                      <span class="label">标准差:</span>
                      <span class="value">{{ formatNumber(field.stats.std) }}</span>
                    </div>
                  </div>
                </div>

                <div class="stat-box">
                  <div class="stat-title">分布信息</div>
                  <div class="stat-values">
                    <div class="stat-value-item">
                      <span class="label">有效值:</span>
                      <span class="value">{{ field.stats.count }}</span>
                    </div>
                    <div class="stat-value-item">
                      <span class="label">唯一值:</span>
                      <span class="value">{{ field.stats.unique }}</span>
                    </div>
                    <div class="stat-value-item">
                      <span class="label">缺失值:</span>
                      <span class="value">{{ field.hasNull ? '有' : '无' }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 分布预览 -->
              <div class="distribution-preview">
                <div class="stat-title">分布预览</div>
                <div class="mini-histogram">
                  <canvas
                    :ref="`histogram-${field.name}`"
                    class="histogram-canvas"
                    width="280"
                    height="80"
                  ></canvas>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane
            v-for="field in categoricalFields"
            :key="field.name"
            :label="field.name"
            :name="field.name"
          >
            <div class="field-stats">
              <div class="stats-row">
                <div class="stat-box">
                  <div class="stat-title">基本统计</div>
                  <div class="stat-values">
                    <div class="stat-value-item">
                      <span class="label">有效值:</span>
                      <span class="value">{{ field.stats.count }}</span>
                    </div>
                    <div class="stat-value-item">
                      <span class="label">唯一值:</span>
                      <span class="value">{{ field.stats.unique }}</span>
                    </div>
                    <div class="stat-value-item">
                      <span class="label">缺失值:</span>
                      <span class="value">{{ field.hasNull ? '有' : '无' }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 分类值分布 -->
              <div class="categorical-distribution">
                <div class="stat-title">分类值分布</div>
                <div class="category-list">
                  <div
                    v-for="(category, index) in getTopCategories(field.name, 5)"
                    :key="index"
                    class="category-item"
                  >
                    <span class="category-name">{{ category.value }}</span>
                    <div class="category-bar">
                      <div
                        class="category-fill"
                        :style="{ width: (category.count / field.stats.count * 100) + '%' }"
                      ></div>
                    </div>
                    <span class="category-count">{{ category.count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 数据质量 -->
    <div class="data-quality">
      <h4>数据质量</h4>
      <div class="quality-metrics">
        <div class="quality-item">
          <div class="quality-label">完整性</div>
          <div class="quality-bar">
            <el-progress
              :percentage="completeness"
              :color="getQualityColor(completeness)"
              :show-text="false"
            />
          </div>
          <div class="quality-value">{{ completeness.toFixed(1) }}%</div>
        </div>
        <div class="quality-item">
          <div class="quality-label">唯一性</div>
          <div class="quality-bar">
            <el-progress
              :percentage="uniqueness"
              :color="getQualityColor(uniqueness)"
              :show-text="false"
            />
          </div>
          <div class="quality-value">{{ uniqueness.toFixed(1) }}%</div>
        </div>
      </div>
    </div>

    <!-- 建议操作 -->
    <div class="suggestions">
      <h4>智能建议</h4>
      <div class="suggestion-list">
        <div
          v-for="(suggestion, index) in suggestions"
          :key="index"
          class="suggestion-item"
          @click="applySuggestion(suggestion)"
        >
          <el-icon class="suggestion-icon">
            <InfoFilled />
          </el-icon>
          <div class="suggestion-content">
            <div class="suggestion-title">{{ suggestion.title }}</div>
            <div class="suggestion-description">{{ suggestion.description }}</div>
          </div>
          <el-button type="primary" text size="small">
            应用
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  fields: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['suggestion-applied'])

const activeFieldTab = ref('')

// 计算属性
const numericFields = computed(() =>
  props.fields.filter(f => f.type === 'number')
)

const categoricalFields = computed(() =>
  props.fields.filter(f => f.type === 'string')
)

const completeness = computed(() => {
  if (props.data.length === 0) return 100

  let totalCells = props.data.length * props.fields.length
  let validCells = 0

  props.data.forEach(row => {
    props.fields.forEach(field => {
      if (row[field.name] != null && row[field.name] !== '') {
        validCells++
      }
    })
  })

  return (validCells / totalCells) * 100
})

const uniqueness = computed(() => {
  if (props.data.length === 0) return 100

  const uniqueRows = new Set(
    props.data.map(row => JSON.stringify(row))
  ).size

  return (uniqueRows / props.data.length) * 100
})

const suggestions = computed(() => {
  const suggestions = []

  // 数据采样建议
  if (props.data.length > 10000) {
    suggestions.push({
      title: '数据量较大',
      description: '建议启用数据采样以提高性能',
      type: 'sampling',
      action: () => {
        emit('suggestion-applied', { type: 'sampling', maxPoints: 5000 })
      }
    })
  }

  // 缺失值处理建议
  const hasMissingData = props.fields.some(f => f.hasNull)
  if (hasMissingData) {
    suggestions.push({
      title: '存在缺失值',
      description: '建议处理缺失数据或过滤无效记录',
      type: 'missing-data',
      action: () => {
        emit('suggestion-applied', { type: 'filter-missing' })
      }
    })
  }

  // 图表类型建议
  if (numericFields.value.length >= 2) {
    suggestions.push({
      title: '适合散点图',
      description: '有多个数值字段，可分析变量相关性',
      type: 'chart-suggestion',
      action: () => {
        emit('suggestion-applied', {
          type: 'chart-change',
          chartType: 'scatter',
          xField: numericFields.value[0].name,
          yField: numericFields.value[1].name
        })
      }
    })
  }

  if (categoricalFields.value.length > 0 && numericFields.value.length > 0) {
    suggestions.push({
      title: '适合分组分析',
      description: '可按分类字段进行分组对比',
      type: 'group-analysis',
      action: () => {
        emit('suggestion-applied', {
          type: 'enable-grouping',
          groupField: categoricalFields.value[0].name
        })
      }
    })
  }

  return suggestions
})

// 方法
const formatNumber = (value) => {
  if (value == null) return 'N/A'
  if (typeof value !== 'number') return value
  return value.toLocaleString('zh-CN', {
    maximumFractionDigits: 4,
    minimumFractionDigits: 0
  })
}

const getTopCategories = (fieldName, limit = 5) => {
  const counts = {}

  props.data.forEach(row => {
    const value = row[fieldName]
    if (value != null && value !== '') {
      counts[value] = (counts[value] || 0) + 1
    }
  })

  return Object.entries(counts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, limit)
    .map(([value, count]) => ({ value, count }))
}

const getQualityColor = (percentage) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 70) return '#e6a23c'
  return '#f56c6c'
}

const drawMiniHistogram = (fieldName, canvas) => {
  if (!canvas || !props.data.length) return

  const ctx = canvas.getContext('2d')
  const field = props.fields.find(f => f.name === fieldName)
  if (!field || field.type !== 'number') return

  // 获取数值数据
  const values = props.data
    .map(row => row[fieldName])
    .filter(v => v != null && typeof v === 'number')
    .sort((a, b) => a - b)

  if (values.length === 0) return

  // 创建分箱
  const binCount = Math.min(20, Math.ceil(Math.sqrt(values.length)))
  const min = values[0]
  const max = values[values.length - 1]
  const binWidth = (max - min) / binCount

  const bins = Array.from({ length: binCount }, () => 0)
  values.forEach(value => {
    const binIndex = Math.min(
      Math.floor((value - min) / binWidth),
      binCount - 1
    )
    bins[binIndex]++
  })

  const maxBinHeight = Math.max(...bins)
  const width = canvas.width
  const height = canvas.height
  const barWidth = width / binCount

  // 清除画布
  ctx.clearRect(0, 0, width, height)

  // 绘制柱状图
  ctx.fillStyle = '#409eff'
  bins.forEach((count, i) => {
    const barHeight = (count / maxBinHeight) * (height - 10)
    const x = i * barWidth
    const y = height - barHeight

    ctx.fillRect(x + 1, y, barWidth - 2, barHeight)
  })
}

const applySuggestion = (suggestion) => {
  if (suggestion.action) {
    suggestion.action()
    ElMessage.success(`已应用建议: ${suggestion.title}`)
  }
}

// 生命周期
onMounted(async () => {
  await nextTick()

  // 设置默认选中的字段标签
  if (numericFields.value.length > 0) {
    activeFieldTab.value = numericFields.value[0].name
  } else if (categoricalFields.value.length > 0) {
    activeFieldTab.value = categoricalFields.value[0].name
  }

  // 绘制小直方图
  setTimeout(() => {
    numericFields.value.forEach(field => {
      const canvas = document.querySelector(`[ref="histogram-${field.name}"]`)
      if (canvas) {
        drawMiniHistogram(field.name, canvas)
      }
    })
  }, 100)
})
</script>

<style scoped>
.data-statistics-panel {
  max-height: 600px;
  overflow-y: auto;
}

.data-statistics-panel h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* 数据概览 */
.stats-overview {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 字段统计 */
.field-statistics {
  margin-bottom: 20px;
}

.field-stats {
  padding: 12px 0;
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.stat-box {
  flex: 1;
}

.stat-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.stat-values {
  background: #fafbfc;
  padding: 8px;
  border-radius: 4px;
}

.stat-value-item {
  display: flex;
  justify-content: space-between;
  padding: 2px 0;
  font-size: 12px;
}

.stat-value-item .label {
  color: #909399;
}

.stat-value-item .value {
  color: #303133;
  font-weight: 500;
}

/* 分布预览 */
.distribution-preview {
  margin-top: 12px;
}

.mini-histogram {
  background: #fafbfc;
  padding: 8px;
  border-radius: 4px;
  text-align: center;
}

.histogram-canvas {
  border: 1px solid #e4e7ed;
  border-radius: 2px;
}

/* 分类分布 */
.categorical-distribution {
  margin-top: 12px;
}

.category-list {
  background: #fafbfc;
  padding: 8px;
  border-radius: 4px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 12px;
}

.category-name {
  min-width: 60px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-bar {
  flex: 1;
  height: 16px;
  background: #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.category-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #66b1ff);
  transition: width 0.3s ease;
}

.category-count {
  min-width: 30px;
  text-align: right;
  color: #909399;
  font-weight: 500;
}

/* 数据质量 */
.data-quality {
  margin-bottom: 20px;
}

.quality-metrics {
  background: #fafbfc;
  padding: 12px;
  border-radius: 6px;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.quality-item:last-child {
  margin-bottom: 0;
}

.quality-label {
  min-width: 60px;
  font-size: 12px;
  color: #303133;
  font-weight: 500;
}

.quality-bar {
  flex: 1;
}

.quality-value {
  min-width: 40px;
  text-align: right;
  font-size: 12px;
  color: #303133;
  font-weight: 600;
}

/* 建议操作 */
.suggestions h4 {
  margin-bottom: 12px;
}

.suggestion-list {
  background: #fafbfc;
  border-radius: 6px;
  overflow: hidden;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #e4e7ed;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: #f0f9ff;
}

.suggestion-icon {
  color: #e6a23c;
  font-size: 16px;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.suggestion-description {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

/* 标签页样式调整 */
:deep(.el-tabs--border-card) {
  border: 1px solid #e4e7ed;
  box-shadow: none;
}

:deep(.el-tabs__header) {
  background: #fafbfc;
  margin: 0;
}

:deep(.el-tabs__nav) {
  border: none;
}

:deep(.el-tabs__item) {
  border: none;
  padding: 0 16px;
  height: 36px;
  line-height: 36px;
  font-size: 12px;
}

:deep(.el-tabs__content) {
  padding: 12px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stats-row {
    flex-direction: column;
    gap: 8px;
  }

  .quality-item {
    flex-wrap: wrap;
  }

  .quality-label {
    min-width: auto;
    flex-basis: 100%;
  }
}
</style>