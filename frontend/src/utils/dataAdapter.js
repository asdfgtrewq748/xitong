/**
 * 数据适配器 - 将 CSV/JSON 数据转换为图表格式
 */
import Papa from 'papaparse'

/**
 * 解析 CSV 文件
 * @param {File|String} input - CSV 文件或字符串
 * @param {Object} options - 解析选项
 * @returns {Promise<Object>} { rows, columns, errors }
 */
export async function parseCSV(input, options = {}) {
  return new Promise((resolve, reject) => {
    const config = {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      encoding: options.encoding || 'UTF-8',
      delimiter: options.delimiter || '',
      complete: (results) => {
        const rows = results.data
        const columns = analyzeColumns(rows)
        
        resolve({
          rows,
          columns,
          errors: results.errors,
          meta: results.meta
        })
      },
      error: (error) => {
        reject(error)
      }
    }
    
    if (typeof input === 'string') {
      Papa.parse(input, config)
    } else {
      Papa.parse(input, config)
    }
  })
}

/**
 * 解析 JSON 数据
 * @param {String|Array} input - JSON 字符串或数组
 * @returns {Object} { rows, columns }
 */
export function parseJSON(input) {
  try {
    const data = typeof input === 'string' ? JSON.parse(input) : input
    
    if (!Array.isArray(data)) {
      throw new Error('JSON 数据必须是数组格式')
    }
    
    const rows = data
    const columns = analyzeColumns(rows)
    
    return { rows, columns, errors: [] }
  } catch (error) {
    throw new Error(`JSON 解析失败: ${error.message}`)
  }
}

/**
 * 分析列信息（类型、统计信息）
 * @param {Array} rows - 数据行
 * @returns {Array} 列信息数组
 */
export function analyzeColumns(rows) {
  if (!rows || rows.length === 0) return []
  
  const firstRow = rows[0]
  const columnNames = Object.keys(firstRow)
  
  return columnNames.map(name => {
    const values = rows.map(row => row[name]).filter(v => v != null)
    const type = inferColumnType(values)
    const stats = calculateStats(values, type)
    
    return {
      name,
      type,
      stats,
      hasNull: values.length < rows.length
    }
  })
}

/**
 * 推断列类型
 * @param {Array} values - 列值数组
 * @returns {String} 'number' | 'string' | 'date' | 'boolean'
 */
function inferColumnType(values) {
  if (values.length === 0) return 'string'
  
  // 检查是否全部为数字
  const numericCount = values.filter(v => typeof v === 'number' || !isNaN(Number(v))).length
  if (numericCount / values.length > 0.8) return 'number'
  
  // 检查是否为日期
  const dateCount = values.filter(v => !isNaN(Date.parse(v))).length
  if (dateCount / values.length > 0.8) return 'date'
  
  // 检查是否为布尔值
  const booleanCount = values.filter(v => v === true || v === false || v === 'true' || v === 'false').length
  if (booleanCount / values.length > 0.8) return 'boolean'
  
  return 'string'
}

/**
 * 计算列统计信息
 * @param {Array} values - 列值
 * @param {String} type - 列类型
 * @returns {Object} 统计信息
 */
function calculateStats(values, type) {
  const stats = {
    count: values.length,
    unique: new Set(values).size
  }
  
  if (type === 'number') {
    const numbers = values.map(v => Number(v)).filter(n => !isNaN(n))
    if (numbers.length > 0) {
      stats.min = Math.min(...numbers)
      stats.max = Math.max(...numbers)
      stats.mean = numbers.reduce((a, b) => a + b, 0) / numbers.length
      stats.median = calculateMedian(numbers)
      stats.std = calculateStd(numbers, stats.mean)
    }
  }
  
  return stats
}

/**
 * 计算中位数
 */
function calculateMedian(numbers) {
  const sorted = [...numbers].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0
    ? (sorted[mid - 1] + sorted[mid]) / 2
    : sorted[mid]
}

/**
 * 计算标准差
 */
function calculateStd(numbers, mean) {
  const variance = numbers.reduce((sum, num) => sum + Math.pow(num - mean, 2), 0) / numbers.length
  return Math.sqrt(variance)
}

/**
 * 将数据转换为图表格式
 * @param {Array} rows - 原始数据行
 * @param {Object} config - 图表配置
 * @returns {Object} 图表数据
 */
export function adaptForChart(rows, columns, config) {
  const { type, xField, yField, zField, colorField, sizeField, groupField } = config

  switch (type) {
    case 'scatter':
      return adaptForScatter(rows, { xField, yField, colorField, sizeField, groupField })
    case 'line':
      return adaptForLine(rows, { xField, yField, groupField })
    case 'heatmap':
      return adaptForHeatmap(rows, { xField, yField, colorField })
    case 'surface':
      return adaptForSurface(rows, { xField, yField, zField })
    case 'bar':
      return adaptForBar(rows, { xField, yField, groupField })
    case 'box':
      return adaptForBox(rows, { groupField, yField })
    case 'histogram':
      return adaptForHistogram(rows, { xField, groupField })
    default:
      return { data: [], config: {} }
  }
}

/**
 * 散点图数据适配
 */
function adaptForScatter(rows, { xField, yField, colorField, sizeField, groupField }) {
  const data = rows.map(row => {
    const point = {
      x: row[xField],
      y: row[yField]
    }
    
    if (colorField) point.color = row[colorField]
    if (sizeField) point.size = row[sizeField]
    if (groupField) point.group = row[groupField]
    
    return point
  }).filter(p => p.x != null && p.y != null)
  
  // 如果有分组，按组分离数据
  if (groupField) {
    const groups = {}
    data.forEach(point => {
      const group = point.group || 'default'
      if (!groups[group]) groups[group] = []
      groups[group].push(point)
    })
    return { data: groups, type: 'grouped' }
  }
  
  return { data, type: 'simple' }
}

/**
 * 折线图数据适配
 */
function adaptForLine(rows, { xField, yField, groupField }) {
  // 按 x 字段排序
  const sorted = [...rows].sort((a, b) => {
    const aVal = a[xField]
    const bVal = b[xField]
    if (typeof aVal === 'number') return aVal - bVal
    return String(aVal).localeCompare(String(bVal))
  })
  
  const data = sorted.map(row => ({
    x: row[xField],
    y: row[yField],
    group: groupField ? row[groupField] : 'default'
  })).filter(p => p.x != null && p.y != null)
  
  // 如果有分组，按组分离数据
  if (groupField) {
    const groups = {}
    data.forEach(point => {
      const group = point.group || 'default'
      if (!groups[group]) groups[group] = []
      groups[group].push({ x: point.x, y: point.y })
    })
    return { data: groups, type: 'grouped' }
  }
  
  return { data, type: 'simple' }
}

/**
 * 热力图数据适配
 */
function adaptForHeatmap(rows, { xField, yField, colorField }) {
  // 验证必需字段
  if (!xField || !yField || !colorField) {
    throw new Error('热力图需要指定X字段、Y字段和颜色字段')
  }
  
  const data = rows.map(row => [
    row[xField],
    row[yField],
    Number(row[colorField])
  ]).filter(p => p[0] != null && p[1] != null && p[2] != null && !isNaN(p[2]))
  
  if (data.length === 0) {
    throw new Error('没有有效的数据用于热力图')
  }
  
  // 获取唯一的 x 和 y 值
  const xValues = [...new Set(data.map(d => d[0]))].sort()
  const yValues = [...new Set(data.map(d => d[1]))].sort()
  
  return {
    data,
    xValues,
    yValues,
    type: 'matrix'
  }
}

/**
 * 三维曲面数据适配
 */
function adaptForSurface(rows, { xField, yField, zField, normalizeCoordinates = false }) {
  // 验证必需字段
  if (!xField || !yField || !zField) {
    throw new Error('3D曲面需要指定X字段、Y字段和Z字段')
  }
  
  const data = rows.map(row => ({
    x: Number(row[xField]),
    y: Number(row[yField]),
    z: Number(row[zField])
  })).filter(p => p.x != null && p.y != null && p.z != null && 
               !isNaN(p.x) && !isNaN(p.y) && !isNaN(p.z))
  
  if (data.length === 0) {
    throw new Error('没有有效的数据用于3D曲面')
  }
  
  // 构建网格数据
  const xValues = [...new Set(data.map(d => d.x))].sort((a, b) => a - b)
  const yValues = [...new Set(data.map(d => d.y))].sort((a, b) => a - b)
  
  // 创建 Z 值矩阵
  const zMatrix = []
  for (let i = 0; i < yValues.length; i++) {
    zMatrix[i] = []
    for (let j = 0; j < xValues.length; j++) {
      const point = data.find(p => p.x === xValues[j] && p.y === yValues[i])
      zMatrix[i][j] = point ? point.z : null
    }
  }

  // 如果需要归一化坐标（例如导出时的规范），将 X/Y 轴从模型边界开始并映射到 [0,1]
  if (normalizeCoordinates) {
    const xMin = Math.min(...xValues)
    const xMax = Math.max(...xValues)
    const yMin = Math.min(...yValues)
    const yMax = Math.max(...yValues)

    const xRange = (xMax - xMin) === 0 ? 1 : (xMax - xMin)
    const yRange = (yMax - yMin) === 0 ? 1 : (yMax - yMin)

    const xNorm = xValues.map(v => (v - xMin) / xRange)
    const yNorm = yValues.map(v => (v - yMin) / yRange)

    // 返回归一化后的坐标，同时保留原始边界信息以便需要时映射回原始坐标
    return {
      x: xNorm,
      y: yNorm,
      z: zMatrix,
      originalBounds: {
        xMin, xMax, yMin, yMax
      },
      type: 'surface',
      normalized: true
    }
  }

  return {
    x: xValues,
    y: yValues,
    z: zMatrix,
    type: 'surface'
  }
}

/**
 * 柱状图数据适配
 */
function adaptForBar(rows, { xField, yField, groupField }) {
  // 验证必需字段
  if (!xField || !yField) {
    throw new Error('柱状图需要指定X字段和Y字段')
  }
  
  const data = rows.map(row => ({
    x: row[xField],
    y: Number(row[yField]),
    group: groupField ? row[groupField] : 'default'
  })).filter(p => p.x != null && p.y != null && !isNaN(p.y))
  
  if (data.length === 0) {
    throw new Error('没有有效的数据用于柱状图')
  }
  
  if (groupField) {
    const groups = {}
    data.forEach(point => {
      const group = point.group || 'default'
      if (!groups[group]) groups[group] = []
      groups[group].push({ x: point.x, y: point.y })
    })
    return { data: groups, type: 'grouped' }
  }
  
  return { data, type: 'simple' }
}

/**
 * 箱线图数据适配
 */
function adaptForBox(rows, { groupField, yField }) {
  // 如果没有yField，抛出错误
  if (!yField) {
    throw new Error('箱线图需要指定Y字段（数值字段）')
  }
  
  const groups = {}
  
  rows.forEach(row => {
    const group = groupField ? (row[groupField] || 'default') : 'default'
    const value = row[yField]
    
    if (value != null && !isNaN(value)) {
      if (!groups[group]) groups[group] = []
      groups[group].push(Number(value))
    }
  })
  
  // 检查是否有有效数据
  if (Object.keys(groups).length === 0) {
    throw new Error('没有有效的数值数据用于箱线图')
  }
  
  // 计算每组的统计信息
  const boxData = Object.entries(groups).map(([group, values]) => {
    const sorted = values.sort((a, b) => a - b)
    const q1Index = Math.floor(sorted.length * 0.25)
    const q2Index = Math.floor(sorted.length * 0.5)
    const q3Index = Math.floor(sorted.length * 0.75)
    
    return {
      group,
      min: sorted[0],
      q1: sorted[q1Index],
      median: sorted[q2Index],
      q3: sorted[q3Index],
      max: sorted[sorted.length - 1]
    }
  })
  
  return { data: boxData, type: 'box' }
}

/**
 * 数据采样（用于大数据集）
 * @param {Array} data - 原始数据
 * @param {Number} maxPoints - 最大点数
 * @returns {Array} 采样后的数据
 */
export function sampleData(data, maxPoints = 10000) {
  if (data.length <= maxPoints) return data
  
  const step = Math.ceil(data.length / maxPoints)
  return data.filter((_, index) => index % step === 0)
}

/**
 * 数据聚合（用于热力图等）
 * @param {Array} data - 原始数据
 * @param {Object} options - 聚合选项
 * @returns {Array} 聚合后的数据
 */
export function aggregateData(data, options = {}) {
  const { xField, yField, valueField, method = 'mean', bins = 20 } = options
  
  // 创建网格
  const xValues = data.map(d => d[xField])
  const yValues = data.map(d => d[yField])
  
  const xMin = Math.min(...xValues)
  const xMax = Math.max(...xValues)
  const yMin = Math.min(...yValues)
  const yMax = Math.max(...yValues)
  
  const xBinSize = (xMax - xMin) / bins
  const yBinSize = (yMax - yMin) / bins
  
  // 分组到网格
  const grid = {}
  data.forEach(point => {
    const xBin = Math.floor((point[xField] - xMin) / xBinSize)
    const yBin = Math.floor((point[yField] - yMin) / yBinSize)
    const key = `${xBin},${yBin}`
    
    if (!grid[key]) {
      grid[key] = {
        x: xMin + (xBin + 0.5) * xBinSize,
        y: yMin + (yBin + 0.5) * yBinSize,
        values: []
      }
    }
    grid[key].values.push(point[valueField])
  })
  
  // 聚合每个网格
  return Object.values(grid).map(cell => ({
    x: cell.x,
    y: cell.y,
    value: aggregateValues(cell.values, method)
  }))
}

/**
 * 直方图数据适配
 */
function adaptForHistogram(rows, { xField, groupField }) {
  // 如果没有xField，抛出错误
  if (!xField) {
    throw new Error('直方图需要指定X字段（数值字段）')
  }
  
  const data = rows.map(row => ({
    value: Number(row[xField]),
    group: groupField ? row[groupField] : 'default'
  })).filter(d => d.value != null && !isNaN(d.value))

  // 检查是否有有效数据
  if (data.length === 0) {
    throw new Error('没有有效的数值数据用于直方图')
  }

  if (groupField) {
    // 分组直方图
    const groups = {}
    data.forEach(item => {
      const group = item.group || 'default'
      if (!groups[group]) groups[group] = []
      groups[group].push(item.value)
    })

    const histogramData = {}
    Object.entries(groups).forEach(([group, values]) => {
      histogramData[group] = createHistogramBins(values)
    })

    return { data: histogramData, type: 'grouped-histogram' }
  } else {
    // 单一直方图
    const values = data.map(d => d.value)
    const bins = createHistogramBins(values)
    return { data: bins, total: values.length, type: 'histogram' }
  }
}

/**
 * 创建直方图分箱
 * @param {Array} values - 数值数组
 * @param {Number} binCount - 分箱数量
 * @returns {Array} 分箱数据
 */
function createHistogramBins(values, binCount = 10) {
  if (values.length === 0) return []

  const sorted = [...values].sort((a, b) => a - b)
  const min = sorted[0]
  const max = sorted[sorted.length - 1]
  const binWidth = (max - min) / binCount

  const bins = Array.from({ length: binCount }, (_, i) => {
    const binMin = min + i * binWidth
    const binMax = binMin + binWidth
    const count = sorted.filter(v => v >= binMin && (i === binCount - 1 ? v <= binMax : v < binMax)).length

    return {
      range: `[${binMin.toFixed(2)}, ${binMax.toFixed(2)})`,
      min: binMin,
      max: binMax,
      count,
      frequency: count / values.length
    }
  })

  return bins.filter(bin => bin.count > 0)
}

/**
 * 聚合值
 */
function aggregateValues(values, method) {
  switch (method) {
    case 'mean':
      return values.reduce((a, b) => a + b, 0) / values.length
    case 'sum':
      return values.reduce((a, b) => a + b, 0)
    case 'max':
      return Math.max(...values)
    case 'min':
      return Math.min(...values)
    case 'count':
      return values.length
    default:
      return values.reduce((a, b) => a + b, 0) / values.length
  }
}
