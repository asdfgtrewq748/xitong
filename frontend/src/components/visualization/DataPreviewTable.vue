<template>
  <div class="data-preview-table">
    <div class="header">
      <div class="title">
        <el-icon><Document /></el-icon>
        <span>数据预览</span>
        <el-tag v-if="tableData.length" size="small" style="margin-left: 8px;">
          {{ tableData.length }} 行 × {{ columns.length }} 列
        </el-tag>
      </div>
      <div class="actions">
        <el-button size="small" @click="showStats = !showStats">
          <el-icon><DataAnalysis /></el-icon>
          {{ showStats ? '隐藏' : '显示' }}统计信息
        </el-button>
      </div>
    </div>

    <!-- 统计信息 -->
    <el-collapse-transition>
      <div v-if="showStats && statistics" class="statistics">
        <el-descriptions :column="3" size="small" border>
          <el-descriptions-item 
            v-for="col in numericColumns" 
            :key="col"
            :label="col"
          >
            <div class="stat-item">
              <span>最小: {{ statistics[col]?.min?.toFixed(2) }}</span>
              <span>最大: {{ statistics[col]?.max?.toFixed(2) }}</span>
              <span>平均: {{ statistics[col]?.mean?.toFixed(2) }}</span>
              <span>标准差: {{ statistics[col]?.std?.toFixed(2) }}</span>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-collapse-transition>

    <!-- 数据表格 -->
    <el-table
      :data="paginatedData"
      :height="tableHeight"
      stripe
      border
      size="small"
      style="width: 100%"
      :empty-text="emptyText"
    >
      <el-table-column
        v-for="column in columns"
        :key="column"
        :prop="column"
        :label="column"
        :sortable="true"
        :width="columnWidth"
      >
        <template #default="{ row }">
          <span :class="{ 'numeric-cell': isNumeric(row[column]) }">
            {{ formatCellValue(row[column]) }}
          </span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-if="tableData.length > pageSize"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[50, 100, 200, 500]"
      :total="tableData.length"
      layout="total, sizes, prev, pager, next, jumper"
      style="margin-top: 12px; justify-content: center;"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, computed, watch } from 'vue'
import { Document, DataAnalysis } from '@element-plus/icons-vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  height: { type: Number, default: 400 }
})

const showStats = ref(true)
const currentPage = ref(1)
const pageSize = ref(100)

const tableData = computed(() => props.data || [])
const tableHeight = computed(() => props.height)
const columnWidth = computed(() => {
  const cols = props.columns.length
  return cols > 6 ? 150 : undefined
})

const emptyText = computed(() => 
  props.data.length === 0 ? '暂无数据，请先导入CSV或JSON文件' : '加载中...'
)

// 计算分页数据
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return tableData.value.slice(start, end)
})

// 提取数值列
const numericColumns = computed(() => {
  if (!tableData.value.length) return []
  return props.columns.filter(col => {
    const firstValue = tableData.value[0]?.[col]
    return typeof firstValue === 'number' || !isNaN(parseFloat(firstValue))
  })
})

// 计算统计信息
const statistics = computed(() => {
  if (!tableData.value.length) return null
  
  const stats = {}
  numericColumns.value.forEach(col => {
    const values = tableData.value
      .map(row => parseFloat(row[col]))
      .filter(v => !isNaN(v))
    
    if (values.length > 0) {
      const sum = values.reduce((a, b) => a + b, 0)
      const mean = sum / values.length
      const variance = values.reduce((acc, v) => acc + Math.pow(v - mean, 2), 0) / values.length
      
      stats[col] = {
        min: Math.min(...values),
        max: Math.max(...values),
        mean: mean,
        std: Math.sqrt(variance),
        count: values.length
      }
    }
  })
  
  return stats
})

function isNumeric(value) {
  return typeof value === 'number' || (typeof value === 'string' && !isNaN(parseFloat(value)))
}

function formatCellValue(value) {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') return value.toFixed(4)
  if (typeof value === 'string' && !isNaN(parseFloat(value))) {
    return parseFloat(value).toFixed(4)
  }
  return value
}

function handleSizeChange(newSize) {
  pageSize.value = newSize
  currentPage.value = 1
}

function handlePageChange(newPage) {
  currentPage.value = newPage
}

// 监听数据变化，重置分页
watch(() => props.data, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.data-preview-table {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 4px;
  padding: 12px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.statistics {
  margin-bottom: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
}

.stat-item span {
  color: #606266;
}

.numeric-cell {
  font-family: 'Courier New', monospace;
  color: #409EFF;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table__header th) {
  background-color: #f5f7fa;
  font-weight: 600;
}

:deep(.el-pagination) {
  display: flex;
  justify-content: center;
}
</style>
