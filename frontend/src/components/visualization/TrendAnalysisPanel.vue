<template>
  <div class="trend-analysis-panel">
    <!-- 趋势概览 -->
    <div class="trend-overview">
      <h4>趋势概览</h4>
      <div class="trend-cards">
        <div class="trend-card" :class="trendInfo.trend">
          <div class="trend-icon">
            <el-icon>
              <component :is="trendIcon" />
            </el-icon>
          </div>
          <div class="trend-info">
            <div class="trend-label">整体趋势</div>
            <div class="trend-value">{{ trendText }}</div>
          </div>
        </div>
        <div class="trend-card">
          <div class="trend-stat">
            <div class="stat-number">{{ trendInfo.changeRate?.toFixed(2) }}%</div>
            <div class="stat-label">变化率</div>
          </div>
        </div>
        <div class="trend-card">
          <div class="trend-stat">
            <div class="stat-number">{{ trendInfo.volatility?.toFixed(2) }}</div>
            <div class="stat-label">波动性</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 关键指标 -->
    <div class="key-metrics">
      <h4>关键指标</h4>
      <div class="metrics-grid">
        <div class="metric-item">
          <span class="metric-label">起始值:</span>
          <span class="metric-value">{{ trendInfo.startValue?.toFixed(3) }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">结束值:</span>
          <span class="metric-value">{{ trendInfo.endValue?.toFixed(3) }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">最大值:</span>
          <span class="metric-value">{{ trendInfo.maxValue?.toFixed(3) }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">最小值:</span>
          <span class="metric-value">{{ trendInfo.minValue?.toFixed(3) }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">平均值:</span>
          <span class="metric-value">{{ trendInfo.meanValue?.toFixed(3) }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">标准差:</span>
          <span class="metric-value">{{ trendInfo.stdValue?.toFixed(3) }}</span>
        </div>
      </div>
    </div>

    <!-- 周期性分析 -->
    <div class="periodicity-analysis" v-if="hasPeriodicity">
      <h4>周期性分析</h4>
      <div class="periodicity-info">
        <div class="period-item">
          <span class="period-label">检测到周期:</span>
          <span class="period-value">{{ periodicityInfo.period }}</span>
        </div>
        <div class="period-item">
          <span class="period-label">周期强度:</span>
          <span class="period-value">{{ periodicityInfo.strength?.toFixed(2) }}</span>
        </div>
        <div class="period-item">
          <span class="period-label">置信度:</span>
          <span class="period-value">{{ (periodicityInfo.confidence * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>

    <!-- 异常点检测 -->
    <div class="outlier-detection" v-if="outliers.length > 0">
      <h4>异常点检测</h4>
      <div class="outlier-summary">
        <el-alert
          :title="`检测到 ${outliers.length} 个异常点`"
          type="warning"
          :closable="false"
          show-icon
        />
        <div class="outlier-list">
          <div
            v-for="(outlier, index) in outliers.slice(0, 5)"
            :key="index"
            class="outlier-item"
          >
            <span class="outlier-index">#{{ outlier.index + 1 }}</span>
            <span class="outlier-value">{{ outlier.value?.toFixed(3) }}</span>
            <span class="outlier-zscore">(z={{ outlier.zscore?.toFixed(2) }})</span>
          </div>
          <div v-if="outliers.length > 5" class="outlier-more">
            还有 {{ outliers.length - 5 }} 个异常点...
          </div>
        </div>
      </div>
    </div>

    <!-- 预测模型 -->
    <div class="prediction-model" v-if="predictionAvailable">
      <h4>趋势预测</h4>
      <div class="prediction-controls">
        <el-form :model="predictionConfig" size="small">
          <el-form-item label="预测步数">
            <el-input-number
              v-model="predictionConfig.steps"
              :min="1"
              :max="50"
              @change="updatePrediction"
            />
          </el-form-item>
          <el-form-item label="置信区间">
            <el-select v-model="predictionConfig.confidenceLevel" @change="updatePrediction">
              <el-option label="90%" value="0.9" />
              <el-option label="95%" value="0.95" />
              <el-option label="99%" value="0.99" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <div class="prediction-summary">
        <div class="prediction-item">
          <span class="prediction-label">预测趋势:</span>
          <span class="prediction-value">{{ predictionResult.direction }}</span>
        </div>
        <div class="prediction-item">
          <span class="prediction-label">预测范围:</span>
          <span class="prediction-value">
            {{ predictionResult.lowerBound?.toFixed(3) }} - {{ predictionResult.upperBound?.toFixed(3) }}
          </span>
        </div>
        <div class="prediction-item">
          <span class="prediction-label">模型准确度:</span>
          <span class="prediction-value">{{ (predictionResult.accuracy * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>

    <!-- 统计检验 -->
    <div class="statistical-tests">
      <h4>统计检验</h4>
      <div class="test-results">
        <div class="test-item">
          <span class="test-name">平稳性检验 (ADF):</span>
          <span class="test-result" :class="stationarityTest.significant ? 'significant' : 'not-significant'">
            p = {{ stationarityTest.pValue?.toExponential(2) }}
            {{ stationarityTest.significant ? '(平稳)' : '(非平稳)' }}
          </span>
        </div>
        <div class="test-item">
          <span class="test-name">自相关检验:</span>
          <span class="test-result">
            Durbin-Watson: {{ durbinWatson?.toFixed(3) }}
            {{ getDurbinWatsonInterpretation(durbinWatson) }}
          </span>
        </div>
        <div class="test-item">
          <span class="test-name">正态性检验:</span>
          <span class="test-result" :class="normalityTest.normal ? 'normal' : 'not-normal'">
            {{ normalityTest.normal ? '符合' : '不符合' }}正态分布
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, computed, watch, onMounted } from 'vue'
import { ArrowUp, ArrowDown, Minus } from '@element-plus/icons-vue'
import {
  calculateTrendInfo,
  detectOutliers,
  detectPeriodicity,
  predictTrend,
  performStationarityTest,
  performNormalityTest,
  calculateDurbinWatson
} from '../../utils/trendAnalysis'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  xField: {
    type: String,
    required: true
  },
  yField: {
    type: String,
    required: true
  },
  groupField: {
    type: String,
    default: null
  }
})

// 计算趋势信息
const trendInfo = ref({})
const outliers = ref([])
const periodicityInfo = ref({})
const predictionConfig = ref({
  steps: 5,
  confidenceLevel: 0.95
})
const predictionResult = ref({})
const stationarityTest = ref({})
const normalityTest = ref({})
const durbinWatson = ref(null)

// 预测配置
const predictionAvailable = computed(() => props.data && props.data.length > 10)
const hasPeriodicity = computed(() => periodicityInfo.value.period && periodicityInfo.value.period > 1)

// 计算属性
const trendIcon = computed(() => {
  switch (trendInfo.value.trend) {
    case 'upward': return ArrowUp
    case 'downward': return ArrowDown
    default: return Minus
  }
})

const trendText = computed(() => {
  switch (trendInfo.value.trend) {
    case 'upward': return '上升趋势'
    case 'downward': return '下降趋势'
    default: return '平稳'
  }
})

// 方法
function analyzeTrends() {
  if (!props.data || !props.xField || !props.yField) return

  const yData = props.data.map(d => d[props.yField]).filter(v => v != null)

  if (yData.length < 3) return

  // 计算基本趋势信息
  trendInfo.value = calculateTrendInfo(yData)

  // 检测异常值
  outliers.value = detectOutliers(yData)

  // 检测周期性
  if (yData.length >= 20) {
    periodicityInfo.value = detectPeriodicity(yData)
  }

  // 统计检验
  stationarityTest.value = performStationarityTest(yData)
  normalityTest.value = performNormalityTest(yData)
  durbinWatson.value = calculateDurbinWatson(yData)
}

function updatePrediction() {
  if (!props.data || !props.yField) return

  const yData = props.data.map(d => d[props.yField]).filter(v => v != null)

  if (yData.length < 10) return

  try {
    predictionResult.value = predictTrend(yData, predictionConfig.value)
  } catch (error) {
    console.error('预测失败:', error)
  }
}

function getDurbinWatsonInterpretation(dw) {
  if (dw === null) return ''

  if (dw < 1.5) return '(正自相关)'
  if (dw > 2.5) return '(负自相关)'
  return '(无自相关)'
}

// 监听数据变化
watch([() => props.data, () => props.xField, () => props.yField], () => {
  analyzeTrends()
  if (predictionAvailable.value) {
    updatePrediction()
  }
}, { immediate: true })

// 监听预测配置变化
watch(() => predictionConfig.value, () => {
  updatePrediction()
}, { deep: true })

onMounted(() => {
  analyzeTrends()
})
</script>

<style scoped>
.trend-analysis-panel {
  padding: 16px;
  background: #fafbfc;
  border-radius: 8px;
}

.trend-analysis-panel h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 8px;
}

.trend-overview {
  margin-bottom: 20px;
}

.trend-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.trend-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.trend-card.upward {
  border-left: 4px solid #67c23a;
}

.trend-card.downward {
  border-left: 4px solid #f56c6c;
}

.trend-card.stable {
  border-left: 4px solid #909399;
}

.trend-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.trend-card.upward .trend-icon {
  background: #67c23a;
}

.trend-card.downward .trend-icon {
  background: #f56c6c;
}

.trend-card.stable .trend-icon {
  background: #909399;
}

.trend-info {
  flex: 1;
}

.trend-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.trend-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.trend-stat {
  text-align: center;
}

.stat-number {
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

.key-metrics {
  margin-bottom: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.metric-label {
  font-size: 12px;
  color: #606266;
}

.metric-value {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.periodicity-analysis,
.outlier-detection,
.prediction-model,
.statistical-tests {
  margin-bottom: 20px;
}

.periodicity-info,
.prediction-summary {
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.period-item,
.prediction-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}

.period-label,
.prediction-label {
  font-size: 12px;
  color: #606266;
}

.period-value,
.prediction-value {
  font-size: 12px;
  font-weight: 500;
  color: #303133;
}

.outlier-summary {
  margin-top: 12px;
}

.outlier-list {
  margin-top: 12px;
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.outlier-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 12px;
}

.outlier-index {
  color: #909399;
  min-width: 40px;
}

.outlier-value {
  font-weight: 500;
  color: #303133;
  flex: 1;
}

.outlier-zscore {
  color: #f56c6c;
  min-width: 60px;
}

.outlier-more {
  color: #909399;
  font-size: 11px;
  text-align: center;
  margin-top: 4px;
}

.prediction-controls {
  margin-bottom: 12px;
}

.test-results {
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.test-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 12px;
}

.test-name {
  color: #606266;
  flex: 1;
}

.test-result {
  font-weight: 500;
  color: #303133;
  text-align: right;
  min-width: 120px;
}

.test-result.significant,
.test-result.normal {
  color: #67c23a;
}

.test-result.not-significant,
.test-result.not-normal {
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .trend-cards {
    grid-template-columns: 1fr;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>