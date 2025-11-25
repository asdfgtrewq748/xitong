<template>
  <div class="regression-panel">
    <div class="panel-header">
      <h3>回归分析</h3>
      <el-button type="primary" size="small" @click="runAnalysis" :loading="loading" :disabled="!canAnalyze">
        <el-icon><DataAnalysis /></el-icon> 开始分析
      </el-button>
    </div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="8">
        <el-card shadow="hover" class="config-card">
          <template #header><span class="config-title">变量选择</span></template>
          <el-form label-position="top" size="small">
            <el-form-item label="自变量 (X)">
              <el-select v-model="xVariable" placeholder="选择自变量" style="width: 100%">
                <el-option v-for="col in numericColumns" :key="col" :label="col" :value="col" />
              </el-select>
            </el-form-item>
            <el-form-item label="因变量 (Y)">
              <el-select v-model="yVariable" placeholder="选择因变量" style="width: 100%">
                <el-option v-for="col in numericColumns" :key="col" :label="col" :value="col" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="config-card">
          <template #header><span class="config-title">回归类型</span></template>
          <el-form label-position="top" size="small">
            <el-form-item label="模型类型">
              <el-radio-group v-model="regressionType" style="width: 100%">
                <el-radio label="linear">线性回归</el-radio>
                <el-radio label="polynomial">多项式回归</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item v-if="regressionType === 'polynomial'" label="多项式阶数">
              <el-slider v-model="polynomialDegree" :min="2" :max="5" show-input />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="config-card" v-if="regressionResult">
          <template #header><span class="config-title">模型评估</span></template>
          <div class="metrics">
            <div class="metric-item">
              <span class="metric-label">R²:</span>
              <span class="metric-value">{{ regressionResult.r_squared?.toFixed(4) }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Adj R²:</span>
              <span class="metric-value">{{ regressionResult.adj_r_squared?.toFixed(4) }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">RMSE:</span>
              <span class="metric-value">{{ regressionResult.rmse?.toFixed(4) }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">p值:</span>
              <span class="metric-value">
                {{ regressionResult.p_value < 0.001 ? '< 0.001' : regressionResult.p_value?.toFixed(4) }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="!regressionResult" class="empty-hint">
      <el-empty description="选择变量后点击开始分析" :image-size="100" />
    </div>

    <div v-else class="regression-result">
      <!-- 回归方程 -->
      <el-alert
        :title="'回归方程: ' + regressionResult.equation"
        type="success"
        :closable="false"
        style="margin-bottom: 16px"
      />

      <!-- 散点图 + 回归线 -->
      <el-card shadow="never" class="result-card">
        <template #header>
          <div class="card-header">
            <span>散点图与回归线</span>
            <el-button size="small" @click="exportScatterChart">导出</el-button>
          </div>
        </template>
        <div ref="scatterChartRef" style="width: 100%; height: 500px;"></div>
      </el-card>

      <!-- 残差图 -->
      <el-row :gutter="16" style="margin-top: 16px">
        <el-col :span="12">
          <el-card shadow="never" class="result-card">
            <template #header><span>残差图</span></template>
            <div ref="residualChartRef" style="width: 100%; height: 350px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never" class="result-card">
            <template #header><span>残差分布</span></template>
            <div ref="residualHistRef" style="width: 100%; height: 350px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 详细统计 -->
      <el-card shadow="never" class="result-card" style="margin-top: 16px">
        <template #header><span>详细统计信息</span></template>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="样本量">{{ regressionResult.n_observations }}</el-descriptions-item>
          <el-descriptions-item label="R²">{{ regressionResult.r_squared?.toFixed(6) }}</el-descriptions-item>
          <el-descriptions-item label="调整后R²">{{ regressionResult.adj_r_squared?.toFixed(6) }}</el-descriptions-item>
          
          <el-descriptions-item label="RMSE">{{ regressionResult.rmse?.toFixed(6) }}</el-descriptions-item>
          <el-descriptions-item label="MSE">{{ regressionResult.mse?.toFixed(6) }}</el-descriptions-item>
          <el-descriptions-item label="F统计量">{{ regressionResult.f_statistic?.toFixed(4) }}</el-descriptions-item>
          
          <el-descriptions-item label="p值">
            {{ regressionResult.p_value < 0.001 ? '< 0.001' : regressionResult.p_value?.toFixed(6) }}
          </el-descriptions-item>
          <el-descriptions-item label="显著性" :span="2">
            <el-tag :type="regressionResult.p_value < 0.05 ? 'success' : 'danger'">
              {{ regressionResult.p_value < 0.05 ? '显著 (p < 0.05)' : '不显著 (p ≥ 0.05)' }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item v-if="regressionType === 'linear'" label="斜率" :span="3">
            {{ regressionResult.slope?.toFixed(6) }} 
            (95% CI: [{{ regressionResult.slope_ci?.[0]?.toFixed(4) }}, {{ regressionResult.slope_ci?.[1]?.toFixed(4) }}])
          </el-descriptions-item>
          
          <el-descriptions-item v-if="regressionType === 'linear'" label="截距" :span="3">
            {{ regressionResult.intercept?.toFixed(6) }}
          </el-descriptions-item>

          <el-descriptions-item v-if="regressionType === 'polynomial'" label="多项式阶数" :span="3">
            {{ regressionResult.degree }}
          </el-descriptions-item>
        </el-descriptions>
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
  numericColumns: Array
})

const emit = defineEmits(['update'])

const xVariable = ref(null)
const yVariable = ref(null)
const regressionType = ref('linear')
const polynomialDegree = ref(2)
const loading = ref(false)
const regressionResult = ref(null)

const scatterChartRef = ref(null)
const residualChartRef = ref(null)
const residualHistRef = ref(null)

let scatterChart = null
let residualChart = null
let residualHist = null

const canAnalyze = computed(() => {
  return props.data && xVariable.value && yVariable.value && xVariable.value !== yVariable.value
})

// 执行分析
const runAnalysis = async () => {
  if (!canAnalyze.value) {
    ElMessage.warning('请选择不同的X和Y变量')
    return
  }

  loading.value = true
  
  try {
    const response = await fetch(`${getApiBase()}/statistics/regression`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        x: props.data[xVariable.value],
        y: props.data[yVariable.value],
        x_label: xVariable.value,
        y_label: yVariable.value,
        regression_type: regressionType.value,
        polynomial_degree: polynomialDegree.value
      })
    })

    const result = await response.json()

    if (result.status === 'success') {
      regressionResult.value = result.data
      emit('update', result.data)
      
      await nextTick()
      renderCharts()
      
      ElMessage.success('回归分析完成')
    }
  } catch (error) {
    ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 渲染所有图表
const renderCharts = () => {
  renderScatterChart()
  renderResidualChart()
  renderResidualHistogram()
}

// 渲染散点图和回归线
const renderScatterChart = () => {
  if (!scatterChartRef.value || !regressionResult.value) return

  if (scatterChart) scatterChart.dispose()
  scatterChart = echarts.init(scatterChartRef.value)

  const xData = props.data[xVariable.value]
  const yData = props.data[yVariable.value]
  const scatterData = xData.map((x, i) => [x, yData[i]])
  
  const predRange = regressionResult.value.prediction_range
  const regressionLine = predRange.x.map((x, i) => [x, predRange.y[i]])

  const series = [
    {
      name: '观测值',
      type: 'scatter',
      data: scatterData,
      symbolSize: 6,
      itemStyle: { color: '#5470c6', opacity: 0.7 }
    },
    {
      name: '回归线',
      type: 'line',
      data: regressionLine,
      smooth: false,
      showSymbol: false,
      lineStyle: { color: '#ee6666', width: 2 }
    }
  ]

  // 如果是线性回归，添加预测区间
  if (regressionType.value === 'linear' && predRange.lower) {
    const upperBand = predRange.x.map((x, i) => [x, predRange.upper[i]])
    const lowerBand = predRange.x.map((x, i) => [x, predRange.lower[i]])
    
    series.push({
      name: '95%预测区间',
      type: 'line',
      data: upperBand,
      lineStyle: { color: '#91cc75', width: 1, type: 'dashed' },
      showSymbol: false
    })
    
    series.push({
      name: '95%预测区间',
      type: 'line',
      data: lowerBand,
      lineStyle: { color: '#91cc75', width: 1, type: 'dashed' },
      showSymbol: false
    })
  }

  const option = {
    title: {
      text: `${yVariable.value} vs ${xVariable.value}`,
      left: 'center',
      textStyle: { fontSize: 14, fontFamily: 'SimSun, "Times New Roman", serif' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['观测值', '回归线', '95%预测区间'],
      bottom: 10
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: xVariable.value,
      nameTextStyle: { fontFamily: 'SimSun, "Times New Roman", serif' }
    },
    yAxis: {
      type: 'value',
      name: yVariable.value,
      nameTextStyle: { fontFamily: 'SimSun, "Times New Roman", serif' }
    },
    series
  }

  scatterChart.setOption(option)
}

// 渲染残差图
const renderResidualChart = () => {
  if (!residualChartRef.value || !regressionResult.value) return

  if (residualChart) residualChart.dispose()
  residualChart = echarts.init(residualChartRef.value)

  const fitted = regressionResult.value.fitted_values
  const residuals = regressionResult.value.residuals
  const residualData = fitted.map((fit, i) => [fit, residuals[i]])

  const option = {
    title: {
      text: '残差图',
      left: 'center',
      textStyle: { fontSize: 14, fontFamily: 'SimSun, "Times New Roman", serif' }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => `拟合值: ${params.data[0].toFixed(3)}<br/>残差: ${params.data[1].toFixed(3)}`
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '拟合值',
      nameTextStyle: { fontFamily: 'SimSun, "Times New Roman", serif' }
    },
    yAxis: {
      type: 'value',
      name: '残差',
      nameTextStyle: { fontFamily: 'SimSun, "Times New Roman", serif' }
    },
    series: [
      {
        type: 'scatter',
        data: residualData,
        symbolSize: 5,
        itemStyle: { color: '#5470c6', opacity: 0.6 }
      },
      {
        type: 'line',
        data: [[Math.min(...fitted), 0], [Math.max(...fitted), 0]],
        lineStyle: { color: '#ee6666', width: 2, type: 'dashed' },
        showSymbol: false
      }
    ]
  }

  residualChart.setOption(option)
}

// 渲染残差直方图
const renderResidualHistogram = () => {
  if (!residualHistRef.value || !regressionResult.value) return

  if (residualHist) residualHist.dispose()
  residualHist = echarts.init(residualHistRef.value)

  const residuals = regressionResult.value.residuals
  const bins = 20
  const min = Math.min(...residuals)
  const max = Math.max(...residuals)
  const binWidth = (max - min) / bins
  
  const histogram = new Array(bins).fill(0)
  residuals.forEach(r => {
    const binIndex = Math.min(Math.floor((r - min) / binWidth), bins - 1)
    histogram[binIndex]++
  })

  const binCenters = histogram.map((_, i) => (min + binWidth * (i + 0.5)).toFixed(2))

  const option = {
    title: {
      text: '残差分布',
      left: 'center',
      textStyle: { fontSize: 14, fontFamily: 'SimSun, "Times New Roman", serif' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        if (!params || params.length === 0) return ''
        const p = params[0]
        return `残差: ${p.name}<br/>频数: ${p.value}`
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: binCenters,
      name: '残差',
      nameTextStyle: { fontFamily: 'SimSun, "Times New Roman", serif' },
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '频数',
      nameTextStyle: { fontFamily: 'SimSun, "Times New Roman", serif' }
    },
    series: [{
      type: 'bar',
      data: histogram,
      itemStyle: { color: '#91cc75' },
      barWidth: '80%'
    }]
  }

  residualHist.setOption(option)
}

// 导出散点图
const exportScatterChart = () => {
  if (!scatterChart) return
  const url = scatterChart.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#fff' })
  const a = document.createElement('a')
  a.href = url
  a.download = `回归分析_${xVariable.value}_${yVariable.value}_${Date.now()}.png`
  a.click()
  ElMessage.success('图表已导出')
}

// 监听变量变化
watch([xVariable, yVariable, regressionType, polynomialDegree], () => {
  regressionResult.value = null
  if (scatterChart) scatterChart.dispose()
  if (residualChart) residualChart.dispose()
  if (residualHist) residualHist.dispose()
})

// 组件卸载时清理
onBeforeUnmount(() => {
  if (scatterChart) scatterChart.dispose()
  if (residualChart) residualChart.dispose()
  if (residualHist) residualHist.dispose()
})
</script>

<style scoped>
.regression-panel {
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

.config-card {
  height: 100%;
}

.config-title {
  font-size: 14px;
  font-weight: 600;
}

.metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.metric-label {
  font-size: 13px;
  color: #606266;
  font-weight: 600;
}

.metric-value {
  font-size: 16px;
  color: #409EFF;
  font-weight: bold;
}

.empty-hint {
  text-align: center;
  padding: 60px 20px;
}

.regression-result {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
