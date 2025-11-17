<template>
  <div class="descriptive-stats-panel">
    <div class="panel-header">
      <h3>描述性统计</h3>
      <el-button type="primary" size="small" @click="runAnalysis" :loading="loading" :disabled="!canAnalyze">
        <el-icon><DataAnalysis /></el-icon> 开始分析
      </el-button>
    </div>

    <div v-if="!statsResult" class="empty-hint">
      <el-empty description="选择变量后点击开始分析查看统计结果" :image-size="100" />
    </div>

    <div v-else class="stats-result">
      <!--统计摘要表 -->
      <el-card shadow="never" class="result-card">
        <template #header>
          <div class="card-header">
            <span>统计摘要</span>
            <el-button size="small" @click="exportTable">导出表格</el-button>
          </div>
        </template>

        <el-table
          :data="summaryTableData"
          border
          stripe
          size="small"
          max-height="400"
          style="width: 100%"
        >
          <el-table-column prop="variable" label="变量" fixed width="120" />
          <el-table-column prop="count" label="有效数" width="80" align="center" />
          <el-table-column prop="missing" label="缺失数" width="80" align="center" />
          <el-table-column prop="mean" label="均值" width="100" :formatter="formatNumber" />
          <el-table-column prop="std" label="标准差" width="100" :formatter="formatNumber" />
          <el-table-column prop="min" label="最小值" width="100" :formatter="formatNumber" />
          <el-table-column prop="q25" label="25%" width="100" :formatter="formatNumber" />
          <el-table-column prop="median" label="中位数" width="100" :formatter="formatNumber" />
          <el-table-column prop="q75" label="75%" width="100" :formatter="formatNumber" />
          <el-table-column prop="max" label="最大值" width="100" :formatter="formatNumber" />
          <el-table-column prop="skewness" label="偏度" width="100" :formatter="formatNumber" />
          <el-table-column prop="kurtosis" label="峰度" width="100" :formatter="formatNumber" />
        </el-table>
      </el-card>

      <!-- 详细统计指标 -->
      <el-card shadow="never" class="result-card" style="margin-top: 16px">
        <template #header>
          <span>详细指标</span>
        </template>

        <el-collapse>
          <el-collapse-item v-for="(varStats, varName) in detailedStats" :key="varName" :name="varName">
            <template #title>
              <strong>{{ varName }}</strong>
            </template>

            <el-descriptions :column="3" border size="small">
              <el-descriptions-item label="样本量">{{ varStats.count }}</el-descriptions-item>
              <el-descriptions-item label="缺失值">{{ varStats.missing }} ({{ varStats.missing_rate?.toFixed(2) }}%)</el-descriptions-item>
              <el-descriptions-item label="众数">{{ formatValue(varStats.mode) }}</el-descriptions-item>
              
              <el-descriptions-item label="均值">{{ formatValue(varStats.mean) }}</el-descriptions-item>
              <el-descriptions-item label="中位数">{{ formatValue(varStats.median) }}</el-descriptions-item>
              <el-descriptions-item label="标准差">{{ formatValue(varStats.std) }}</el-descriptions-item>
              
              <el-descriptions-item label="方差">{{ formatValue(varStats.variance) }}</el-descriptions-item>
              <el-descriptions-item label="极差">{{ formatValue(varStats.range) }}</el-descriptions-item>
              <el-descriptions-item label="四分位距">{{ formatValue(varStats.iqr) }}</el-descriptions-item>
              
              <el-descriptions-item label="变异系数">{{ formatValue(varStats.cv) }}%</el-descriptions-item>
              <el-descriptions-item label="标准误">{{ formatValue(varStats.sem) }}</el-descriptions-item>
              <el-descriptions-item label="95%置信区间">
                [{{ formatValue(varStats.ci_lower) }}, {{ formatValue(varStats.ci_upper) }}]
              </el-descriptions-item>
              
              <el-descriptions-item label="偏度">
                {{ formatValue(varStats.skewness) }}
                <el-tag size="small" style="margin-left: 8px">{{ getSkewnessType(varStats.skewness) }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="峰度">
                {{ formatValue(varStats.kurtosis) }}
                <el-tag size="small" style="margin-left: 8px">{{ getKurtosisType(varStats.kurtosis) }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis } from '@element-plus/icons-vue'
import { getApiBase } from '../../../utils/api'

const props = defineProps({
  data: Object,
  selectedVariables: Array
})

const emit = defineEmits(['update'])

const loading = ref(false)
const statsResult = ref(null)

const canAnalyze = computed(() => {
  return props.data && props.selectedVariables && props.selectedVariables.length > 0
})

const summaryTableData = computed(() => {
  if (!statsResult.value) return []
  return statsResult.value.summary_table || []
})

const detailedStats = computed(() => {
  if (!statsResult.value) return {}
  return statsResult.value.detailed_stats || {}
})

// 执行分析
const runAnalysis = async () => {
  if (!canAnalyze.value) {
    ElMessage.warning('请先选择要分析的变量')
    return
  }

  loading.value = true
  
  try {
    // 构建请求数据
    const requestData = {}
    props.selectedVariables.forEach(varName => {
      requestData[varName] = props.data[varName]
    })

    const response = await fetch(`${getApiBase()}/statistics/descriptive`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: requestData })
    })

    const result = await response.json()

    if (result.status === 'success') {
      statsResult.value = result.data
      emit('update', result.data)
      ElMessage.success('统计分析完成')
    }
  } catch (error) {
    ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 格式化数字
const formatNumber = (row, column, cellValue) => {
  return formatValue(cellValue)
}

const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value !== 'number') return value
  if (isNaN(value)) return 'NaN'
  return value.toFixed(4)
}

// 偏度类型判断
const getSkewnessType = (skewness) => {
  if (skewness === null || skewness === undefined) return '-'
  const abs = Math.abs(skewness)
  if (abs < 0.5) return '近似对称'
  if (skewness > 0) return '右偏'
  return '左偏'
}

// 峰度类型判断
const getKurtosisType = (kurtosis) => {
  if (kurtosis === null || kurtosis === undefined) return '-'
  if (kurtosis > 0) return '尖峰'
  if (kurtosis < 0) return '平峰'
  return '正态'
}

// 导出表格
const exportTable = () => {
  ElMessage.info('导出功能开发中...')
}

// 监听变量选择变化
watch(() => props.selectedVariables, () => {
  statsResult.value = null
}, { deep: true })
</script>

<style scoped>
.descriptive-stats-panel {
  padding: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.empty-hint {
  text-align: center;
  padding: 60px 20px;
}

.stats-result {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
}

:deep(.el-descriptions__content) {
  color: #303133;
}

:deep(.el-collapse-item__header) {
  padding-left: 12px;
  font-size: 14px;
}
</style>
