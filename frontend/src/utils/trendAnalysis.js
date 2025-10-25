/**
 * 趋势分析工具
 */

/**
 * 计算趋势信息
 * @param {Array} data - 数据数组
 * @returns {Object} 趋势信息
 */
export function calculateTrendInfo(data) {
  if (!data || data.length < 2) {
    return {}
  }

  const n = data.length
  const startValue = data[0]
  const endValue = data[n - 1]
  const change = endValue - startValue
  const changeRate = (change / startValue) * 100

  const values = [...data]
  const mean = values.reduce((a, b) => a + b, 0) / n
  const std = Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / n)

  const maxValue = Math.max(...values)
  const minValue = Math.min(...values)

  // 判断趋势
  let trend = 'stable'
  if (Math.abs(changeRate) > 5) {
    trend = changeRate > 0 ? 'upward' : 'downward'
  }

  // 计算波动性（变异系数）
  const volatility = std / mean

  return {
    trend,
    changeRate,
    volatility,
    startValue,
    endValue,
    maxValue,
    minValue,
    meanValue: mean,
    stdValue: std,
    dataPoints: n
  }
}

/**
 * 检测异常值
 * @param {Array} data - 数据数组
 * @param {number} threshold - Z分数阈值
 * @returns {Array} 异常值列表
 */
export function detectOutliers(data, threshold = 2) {
  if (!data || data.length < 3) return []

  const mean = data.reduce((a, b) => a + b, 0) / data.length
  const std = Math.sqrt(data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length)

  const outliers = []
  data.forEach((value, index) => {
    const zscore = Math.abs((value - mean) / std)
    if (zscore > threshold) {
      outliers.push({
        index,
        value,
        zscore
      })
    }
  })

  return outliers.sort((a, b) => Math.abs(b.zscore) - Math.abs(a.zscore))
}

/**
 * 检测周期性（简化版）
 * @param {Array} data - 数据数组
 * @returns {Object} 周期性信息
 */
export function detectPeriodicity(data) {
  if (!data || data.length < 20) return {}

  // 使用自相关函数检测周期
  const autocorr = calculateAutocorrelation(data)
  const n = autocorr.length

  // 寻找第一个显著的峰值（除了0延迟）
  let maxCorr = 0
  let bestPeriod = 1

  for (let lag = 1; lag < Math.min(n / 2, 50); lag++) {
    if (Math.abs(autocorr[lag]) > maxCorr && Math.abs(autocorr[lag]) > 0.3) {
      maxCorr = Math.abs(autocorr[lag])
      bestPeriod = lag
    }
  }

  // 评估周期强度
  let strength = 0
  if (bestPeriod > 1) {
    strength = maxCorr
  }

  // 计算置信度（简化版本）
  const confidence = Math.min(0.95, strength * 1.5)

  return {
    period: bestPeriod,
    strength,
    confidence,
    autocorrelation: autocorr
  }
}

/**
 * 计算自相关函数
 * @param {Array} data - 数据数组
 * @returns {Array} 自相关系数数组
 */
function calculateAutocorrelation(data) {
  const n = data.length
  const mean = data.reduce((a, b) => a + b, 0) / n
  const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / n

  const autocorr = []
  const normalizedData = data.map(val => val - mean)

  for (let lag = 0; lag < n; lag++) {
    let correlation = 0
    let count = 0

    for (let i = 0; i < n - lag; i++) {
      correlation += normalizedData[i] * normalizedData[i + lag]
      count++
    }

    if (count > 0 && variance > 0) {
      autocorr[lag] = correlation / (count * variance)
    } else {
      autocorr[lag] = 0
    }
  }

  return autocorr
}

/**
 * 趋势预测（简化版线性预测）
 * @param {Array} data - 历史数据
 * @param {Object} options - 预测选项
 * @returns {Object} 预测结果
 */
export function predictTrend(data, options = {}) {
  const { steps = 5, confidenceLevel = 0.95 } = options

  if (!data || data.length < 10) {
    throw new Error('数据点不足，无法进行预测')
  }

  // 简单线性外推
  const n = data.length
  const xValues = Array.from({ length: n }, (_, i) => i)
  const yValues = [...data]

  // 计算线性回归参数
  const meanX = xValues.reduce((a, b) => a + b, 0) / n
  const meanY = yValues.reduce((a, b) => a + b, 0) / n

  let numerator = 0
  let denominator = 0
  for (let i = 0; i < n; i++) {
    numerator += (xValues[i] - meanX) * (yValues[i] - meanY)
    denominator += Math.pow(xValues[i] - meanX, 2)
  }

  const slope = denominator === 0 ? 0 : numerator / denominator
  const intercept = meanY - slope * meanX

  // 计算预测值
  const predictions = []
  for (let i = 0; i < steps; i++) {
    const futureX = n + i
    predictions.push(intercept + slope * futureX)
  }

  // 计算置信区间（简化版本）
  const residuals = yValues.map((y, i) => y - (intercept + slope * i))
  const mse = residuals.reduce((sum, r) => sum + r * r, 0) / n
  const stdError = Math.sqrt(mse)

  const zScore = confidenceIntervalToZ(confidenceLevel)
  const margin = zScore * stdError * Math.sqrt(1 + 1/n)

  const lastValue = data[n - 1]
  const direction = slope > 0 ? 'upward' : slope < 0 ? 'downward' : 'stable'
  const lowerBound = lastValue + slope * steps * (1 - margin)
  const upperBound = lastValue + slope * steps * (1 + margin)

  // 评估模型准确度（基于历史拟合度）
  const ssTotal = yValues.reduce((sum, y) => sum + Math.pow(y - meanY, 2), 0)
  const ssResidual = residuals.reduce((sum, r) => sum + r * r, 0)
  const r2 = 1 - (ssResidual / ssTotal)

  return {
    predictions,
    direction,
    lowerBound,
    upperBound,
    margin,
    r2,
    accuracy: Math.max(0, r2),
    model: 'linear',
    steps,
    confidenceLevel
  }
}

/**
 * 置信区间转换为Z分数
 * @param {number} confidence - 置信水平
 * @returns {number} Z分数
 */
function confidenceIntervalToZ(confidence) {
  // 简化的正态分布分位数
  const zScores = {
    0.90: 1.645,
    0.95: 1.96,
    0.99: 2.576
  }
  return zScores[confidence] || 1.96
}

/**
 * 执行平稳性检验（简化版ADF检验）
 * @param {Array} data - 数据数组
 * @returns {Object} 检验结果
 */
export function performStationarityTest(data) {
  if (!data || data.length < 10) {
    return { pValue: 1, significant: false }
  }

  // 简化的ADF检验近似
  // 实际应用中应该使用专业的统计库
  const firstValue = data[0]
  const lastValue = data[data.length - 1]
  const change = lastValue - firstValue
  const mean = data.reduce((a, b) => a + b, 0) / data.length
  const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length

  // 简化的统计量
  const statistic = Math.abs(change) / Math.sqrt(variance)

  // 简化的p值计算
  let pValue = 1
  if (statistic > 2) {
    pValue = 0.05
  } else if (statistic > 1.5) {
    pValue = 0.1
  }

  // 判断是否平稳（p < 0.05认为显著）
  const significant = pValue < 0.05

  return {
    statistic,
    pValue,
    significant,
    test: 'ADF'
  }
}

/**
 * 执行正态性检验（简化版Shapiro-Wilk检验近似）
 * @param {Array} data - 数据数组
 * @returns {Object} 检验结果
 */
export function performNormalityTest(data) {
  if (!data || data.length < 3) {
    return { normal: false, pValue: 1 }
  }

  const n = data.length
  const mean = data.reduce((a, b) => a + b, 0) / n
  const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / n
  const std = Math.sqrt(variance)

  // 计算偏度和峰度
  let skewness = 0
  let kurtosis = 0

  data.forEach(val => {
    const standardized = (val - mean) / std
    skewness += Math.pow(standardized, 3)
    kurtosis += Math.pow(standardized, 4)
  })

  skewness /= n
  kurtosis = kurtosis / n - 3  // 超额峰度

  // 简化的正态性判断
  const skewnessThreshold = 2 / Math.sqrt(n / 6)
  const kurtosisThreshold = 4 / Math.sqrt(n / 24)

  const isSkewnessNormal = Math.abs(skewness) < skewnessThreshold
  const isKurtosisNormal = Math.abs(kurtosis) < kurtosisThreshold

  const normal = isSkewnessNormal && isKurtosisNormal

  // 简化的p值计算
  const testStatistic = Math.sqrt(n) * Math.max(
    Math.abs(skewness) / skewnessThreshold,
    Math.abs(kurtosis) / kurtosisThreshold
  )

  let pValue = 1
  if (testStatistic > 2) {
    pValue = 0.05
  } else if (testStatistic > 1) {
    pValue = 0.1
  }

  return {
    normal,
    pValue,
    skewness,
    kurtosis,
    test: 'Shapiro-Wilk'
  }
}

/**
 * 计算Durbin-Watson统计量
 * @param {Array} data - 残差数组
 * @returns {number} DW统计量
 */
export function calculateDurbinWatson(data) {
  if (!data || data.length < 2) return null

  let numerator = 0
  let denominator = 0

  for (let i = 1; i < data.length; i++) {
    const diff = data[i] - data[i - 1]
    numerator += diff * diff
  }

  for (let i = 0; i < data.length; i++) {
    denominator += data[i] * data[i]
  }

  if (denominator === 0) return null

  return numerator / denominator
}

/**
 * 计算移动平均
 * @param {Array} data - 数据数组
 * @param {number} window - 窗口大小
 * @returns {Array} 移动平均数组
 */
export function calculateMovingAverage(data, window = 5) {
  if (!data || data.length < window) return []

  const result = []
  for (let i = window - 1; i < data.length; i++) {
    const sum = data.slice(i - window + 1, i + 1).reduce((a, b) => a + b, 0)
    result.push(sum / window)
  }

  return result
}

/**
 * 计算指数平滑
 * @param {Array} data - 数据数组
 * @param {number} alpha - 平滑参数
 * @returns {Array} 指数平滑数组
 */
export function calculateExponentialSmoothing(data, alpha = 0.3) {
  if (!data || data.length === 0) return []

  const result = [data[0]]

  for (let i = 1; i < data.length; i++) {
    const smoothed = alpha * data[i] + (1 - alpha) * result[i - 1]
    result.push(smoothed)
  }

  return result
}