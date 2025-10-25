/**
 * 采样工具 - 用于大数据集性能优化
 */

/**
 * 简单随机采样
 * @param {Array} data - 原始数据
 * @param {Number} maxPoints - 最大点数
 * @returns {Array} 采样后的数据
 */
export function randomSample(data, maxPoints = 10000) {
  if (!data || data.length <= maxPoints) return data
  
  const step = Math.ceil(data.length / maxPoints)
  return data.filter((_, index) => index % step === 0)
}

/**
 * 系统采样（等间隔）
 * @param {Array} data - 原始数据
 * @param {Number} maxPoints - 最大点数
 * @returns {Array} 采样后的数据
 */
export function systematicSample(data, maxPoints = 10000) {
  if (!data || data.length <= maxPoints) return data
  
  const step = data.length / maxPoints
  const sampled = []
  
  for (let i = 0; i < maxPoints; i++) {
    const index = Math.floor(i * step)
    if (index < data.length) {
      sampled.push(data[index])
    }
  }
  
  return sampled
}

/**
 * 最大最小值保留采样
 * @param {Array} data - 原始数据
 * @param {String} field - 用于判断最大最小值的字段
 * @param {Number} maxPoints - 最大点数
 * @returns {Array} 采样后的数据
 */
export function minMaxSample(data, field, maxPoints = 10000) {
  if (!data || data.length <= maxPoints) return data
  
  // 按字段值排序
  const sorted = [...data].sort((a, b) => {
    const aVal = typeof a === 'object' ? a[field] : a
    const bVal = typeof b === 'object' ? b[field] : b
    return aVal - bVal
  })
  
  // 保留最小和最大值
  const sampled = [sorted[0]]
  const step = Math.floor((sorted.length - 2) / (maxPoints - 2))
  
  for (let i = step; i < sorted.length - 1; i += step) {
    sampled.push(sorted[i])
    if (sampled.length >= maxPoints - 1) break
  }
  
  sampled.push(sorted[sorted.length - 1])
  return sampled
}

/**
 * 检测是否需要采样
 * @param {Array} data - 数据
 * @param {Number} threshold - 阈值
 * @returns {Boolean}
 */
export function needsSampling(data, threshold = 10000) {
  return data && data.length > threshold
}

/**
 * 智能采样（根据数据量自动选择策略）
 * @param {Array} data - 原始数据
 * @param {Object} options - 采样选项
 * @returns {Object} { sampled, info }
 */
export function smartSample(data, options = {}) {
  const {
    maxPoints = 10000,
    field = null,
    method = 'auto' // auto, random, systematic, minmax
  } = options
  
  if (!data || data.length <= maxPoints) {
    return {
      sampled: data,
      info: {
        original: data.length,
        sampled: data.length,
        ratio: 1,
        method: 'none'
      }
    }
  }
  
  let sampled
  let selectedMethod = method
  
  if (method === 'auto') {
    // 自动选择最佳采样方法
    if (field) {
      selectedMethod = 'minmax'
      sampled = minMaxSample(data, field, maxPoints)
    } else if (data.length > 100000) {
      selectedMethod = 'systematic'
      sampled = systematicSample(data, maxPoints)
    } else {
      selectedMethod = 'random'
      sampled = randomSample(data, maxPoints)
    }
  } else if (method === 'random') {
    sampled = randomSample(data, maxPoints)
  } else if (method === 'systematic') {
    sampled = systematicSample(data, maxPoints)
  } else if (method === 'minmax' && field) {
    sampled = minMaxSample(data, field, maxPoints)
  } else {
    sampled = systematicSample(data, maxPoints)
    selectedMethod = 'systematic'
  }
  
  return {
    sampled,
    info: {
      original: data.length,
      sampled: sampled.length,
      ratio: (sampled.length / data.length).toFixed(3),
      method: selectedMethod
    }
  }
}

/**
 * LTTB降采样算法（Largest Triangle Three Buckets）
 * 用于时间序列数据，保留视觉上最重要的点
 * @param {Array} data - 原始数据，格式: [{x, y}]
 * @param {Number} threshold - 目标点数
 * @returns {Array} 采样后的数据
 */
export function lttbDownsample(data, threshold = 10000) {
  if (!data || data.length <= threshold) return data
  
  const sampled = []
  const dataLength = data.length
  const bucketSize = (dataLength - 2) / (threshold - 2)
  
  // 始终保留第一个点
  sampled.push(data[0])
  
  let a = 0 // 上一个选择的点的索引
  
  for (let i = 0; i < threshold - 2; i++) {
    // 计算当前bucket的平均点作为下一个bucket的代表
    let avgX = 0
    let avgY = 0
    let avgRangeStart = Math.floor((i + 1) * bucketSize) + 1
    let avgRangeEnd = Math.floor((i + 2) * bucketSize) + 1
    avgRangeEnd = avgRangeEnd < dataLength ? avgRangeEnd : dataLength
    
    const avgRangeLength = avgRangeEnd - avgRangeStart
    
    for (; avgRangeStart < avgRangeEnd; avgRangeStart++) {
      avgX += data[avgRangeStart].x
      avgY += data[avgRangeStart].y
    }
    avgX /= avgRangeLength
    avgY /= avgRangeLength
    
    // 在当前bucket中找到形成最大三角形面积的点
    const rangeOffs = Math.floor(i * bucketSize) + 1
    const rangeTo = Math.floor((i + 1) * bucketSize) + 1
    
    const pointAX = data[a].x
    const pointAY = data[a].y
    
    let maxArea = -1
    let maxAreaPoint
    let nextA
    
    for (let idx = rangeOffs; idx < rangeTo; idx++) {
      // 计算三角形面积
      const area = Math.abs(
        (pointAX - avgX) * (data[idx].y - pointAY) -
        (pointAX - data[idx].x) * (avgY - pointAY)
      ) * 0.5
      
      if (area > maxArea) {
        maxArea = area
        maxAreaPoint = data[idx]
        nextA = idx
      }
    }
    
    sampled.push(maxAreaPoint)
    a = nextA
  }
  
  // 始终保留最后一个点
  sampled.push(data[dataLength - 1])
  
  return sampled
}

/**
 * 聚合降采样 - 将数据分桶并计算统计量
 * @param {Array} data - 原始数据
 * @param {Number} bucketSize - 桶大小
 * @param {String} aggregation - 聚合方法 (mean, max, min)
 * @returns {Array} 采样后的数据
 */
export function aggregateDownsample(data, bucketSize, aggregation = 'mean') {
  if (!data || data.length <= bucketSize) return data

  const result = []
  for (let i = 0; i < data.length; i += bucketSize) {
    const bucket = data.slice(i, i + bucketSize)
    
    if (aggregation === 'mean') {
      const avg = bucket.reduce((sum, point) => ({
        x: sum.x + point.x / bucket.length,
        y: sum.y + point.y / bucket.length,
        ...(point.z !== undefined && { z: sum.z + point.z / bucket.length })
      }), { x: 0, y: 0, z: 0 })
      result.push(avg)
    } else if (aggregation === 'max') {
      result.push(bucket.reduce((max, point) => point.y > max.y ? point : max))
    } else if (aggregation === 'min') {
      result.push(bucket.reduce((min, point) => point.y < min.y ? point : min))
    }
  }
  
  return result
}

/**
 * 分箱统计 - 用于直方图和热力图
 * @param {Array} data - 原始数据
 * @param {String} field - 字段名
 * @param {Number} bins - 分箱数量
 * @returns {Array} 分箱结果
 */
export function binData(data, field, bins = 10) {
  if (!data || data.length === 0) return []

  const values = data.map(d => d[field]).filter(v => v !== null && v !== undefined && !isNaN(v))
  if (values.length === 0) return []
  
  const min = Math.min(...values)
  const max = Math.max(...values)
  const binWidth = (max - min) / bins

  const histogram = Array(bins).fill(0).map((_, i) => ({
    min: min + i * binWidth,
    max: min + (i + 1) * binWidth,
    center: min + (i + 0.5) * binWidth,
    count: 0
  }))

  values.forEach(value => {
    let binIndex = Math.floor((value - min) / binWidth)
    if (binIndex === bins) binIndex = bins - 1 // 处理最大值边界情况
    if (binIndex >= 0 && binIndex < bins) {
      histogram[binIndex].count++
    }
  })

  return histogram
}

/**
 * 获取采样建议
 * @param {Array} data - 数据
 * @returns {Object} 采样建议
 */
export function getSamplingRecommendation(data) {
  if (!data || data.length === 0) {
    return { needsSampling: false, strategy: null, reason: '无数据' }
  }

  const count = data.length

  if (count <= 5000) {
    return { 
      needsSampling: false, 
      strategy: null, 
      reason: '数据量较小，无需采样',
      targetPoints: count
    }
  }

  if (count <= 20000) {
    return { 
      needsSampling: true, 
      strategy: 'systematic', 
      reason: '中等数据量，建议系统采样',
      targetPoints: 10000
    }
  }

  if (count <= 100000) {
    return { 
      needsSampling: true, 
      strategy: 'lttb', 
      reason: '大数据量，建议LTTB降采样（保留视觉特征）',
      targetPoints: 15000
    }
  }

  return { 
    needsSampling: true, 
    strategy: 'systematic', 
    reason: '超大数据量，建议系统采样',
    targetPoints: 20000
  }
}
