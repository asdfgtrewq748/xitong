<template>
  <div class="correlation-panel">
    <div class="panel-header">
      <h3>相关性分析</h3>
      <div class="header-controls">
        <el-radio-group v-model="method" size="small">
          <el-radio-button label="pearson">Pearson</el-radio-button>
          <el-radio-button label="spearman">Spearman</el-radio-button>
        </el-radio-group>
        <el-button type="primary" size="small" @click="runAnalysis" :loading="loading" :disabled="!canAnalyze">
          <el-icon><DataAnalysis /></el-icon> 开始分析
        </el-button>
      </div>
    </div>

    <div v-if="!correlationResult" class="empty-hint">
      <el-empty description="选择至少2个变量后点击开始分析" :image-size="100" />
    </div>

    <div v-else class="correlation-result">
      <!-- 相关系数矩阵热力图 -->
      <el-card shadow="never" class="result-card">
        <template #header>
          <div class="card-header">
            <span>相关系数矩阵（{{ method === 'pearson' ? 'Pearson' : 'Spearman' }}）</span>
            <el-button size="small" @click="exportChart">导出图表</el-button>
          </div>
        </template>

        <div ref="chartRef" style="width: 100%; height: 500px;"></div>
      </el-card>

      <!-- 显著相关对 -->
      <el-card shadow="never" class="result-card" style="margin-top: 16px">
        <template #header>
          <div class="card-header">
            <span>显著相关变量对（p &lt; 0.05）</span>
            <el-tag size="small" type="info">共 {{ significantPairs.length }} 对</el-tag>
          </div>
        </template>

        <el-table
          :data="significantPairs"
          border
          stripe
          size="small"
          max-height="400"
        >
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="var1" label="变量1" min-width="120" />
          <el-table-column prop="var2" label="变量2" min-width="120" />
          <el-table-column prop="correlation" label="相关系数" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getCorrelationTagType(row.correlation)" size="small">
                {{ row.correlation.toFixed(4) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="p_value" label="p值" width="120" align="center">
            <template #default="{ row }">
              {{ row.p_value < 0.001 ? '< 0.001' : row.p_value.toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column prop="strength" label="相关强度" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStrengthTagType(row.strength)" size="small">
                {{ row.strength }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getApiBase } from '../../../utils/api'

const props = defineProps({
  data: Object,
  selectedVariables: Array
})

const emit = defineEmits(['update'])

const method = ref('pearson')
const loading = ref(false)
const correlationResult = ref(null)
const chartRef = ref(null)
let chartInstance = null

const canAnalyze = computed(() => {
  return props.data && props.selectedVariables && props.selectedVariables.length >= 2
})

const significantPairs = computed(() => {
  if (!correlationResult.value) return []
  return correlationResult.value.significant_pairs || []
})

// 执行分析
const runAnalysis = async () => {
  if (!canAnalyze.value) {
    ElMessage.warning('请选择至少2个变量进行相关性分析')
    return
  }

  loading.value = true
  
  try {
    const requestData = {}
    props.selectedVariables.forEach(varName => {
      requestData[varName] = props.data[varName]
    })

    const response = await fetch(`${getApiBase()}/statistics/correlation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: requestData, method: method.value })
    })

    const result = await response.json()

    if (result.status === 'success') {
      correlationResult.value = result.data
      emit('update', result.data)
      
      await nextTick()
      renderHeatmap()
      
      ElMessage.success('相关性分析完成')
    }
  } catch (error) {
    ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 渲染热力图
const renderHeatmap = () => {
  if (!chartRef.value || !correlationResult.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)

  const corrMatrix = correlationResult.value.correlation_matrix
  const variables = Object.keys(corrMatrix)
  
  // 转换为热力图数据格式
  const data = []
  variables.forEach((var1, i) => {
    variables.forEach((var2, j) => {
      const value = corrMatrix[var1][var2]
      data.push([j, i, value])
    })
  })

  const option = {
    tooltip: {
      position: 'top',
      formatter: (params) => {
        const var1 = variables[params.data[1]]
        const var2 = variables[params.data[0]]
        const corr = params.data[2]
        return `<strong>${var1}</strong> vs <strong>${var2}</strong><br/>相关系数: ${corr.toFixed(4)}`
      }
    },
    grid: {
      left: '15%',
      right: '10%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: variables,
      axisLabel: {
        rotate: 45,
        fontSize: 11,
        fontFamily: 'SimSun, "Times New Roman", serif'
      },
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: variables,
      axisLabel: {
        fontSize: 11,
        fontFamily: 'SimSun, "Times New Roman", serif'
      },
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', 
                '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      },
      text: ['强正相关', '强负相关'],
      textStyle: {
        fontSize: 11,
        fontFamily: 'SimSun, "Times New Roman", serif'
      }
    },
    series: [{
      name: '相关系数',
      type: 'heatmap',
      data: data,
      label: {
        show: true,
        fontSize: 10,
        formatter: (params) => params.data[2].toFixed(2)
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  chartInstance.setOption(option)
}

// 获取相关系数标签类型
const getCorrelationTagType = (corr) => {
  const abs = Math.abs(corr)
  if (abs >= 0.8) return 'danger'
  if (abs >= 0.6) return 'warning'
  if (abs >= 0.4) return 'success'
  return 'info'
}

// 获取强度标签类型
const getStrengthTagType = (strength) => {
  const map = {
    '极强': 'danger',
    '强': 'warning',
    '中等': 'success',
    '弱': 'info',
    '极弱': 'info'
  }
  return map[strength] || 'info'
}

// 导出图表
const exportChart = () => {
  if (!chartInstance) return
  const url = chartInstance.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  })
  
  const a = document.createElement('a')
  a.href = url
  a.download = `相关性矩阵_${method.value}_${Date.now()}.png`
  a.click()
  
  ElMessage.success('图表已导出')
}

// 监听变量选择变化
watch(() => props.selectedVariables, () => {
  correlationResult.value = null
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}, { deep: true })

// 监听方法变化，重新分析
watch(method, () => {
  if (correlationResult.value) {
    runAnalysis()
  }
})

// 组件卸载时清理
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.correlation-panel {
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

.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.empty-hint {
  text-align: center;
  padding: 60px 20px;
}

.correlation-result {
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
</style>
