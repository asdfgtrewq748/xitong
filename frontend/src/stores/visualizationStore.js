/**
 * 科研绘图数据与配置管理 Store
 * 管理数据集、图表配置、导出状态和历史记录
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useVisualizationStore = defineStore('visualization', () => {
  // ========== 状态 ==========
  
  // 数据集管理
  const datasets = ref({})
  const currentDatasetId = ref(null)
  
  // 图表配置
  const chartConfig = ref({
    type: 'scatter', // scatter, heatmap, surface, line, bar, box, histogram
    xField: null,
    yField: null,
    zField: null, // 用于 3D 图表
    colorField: null,
    sizeField: null,
    groupField: null, // 分组字段
    title: '科研图表',
    xAxisLabel: 'X轴',
    yAxisLabel: 'Y轴',
    zAxisLabel: 'Z轴',
    showLegend: true,
    showGrid: true,
    colorScheme: 'viridis', // viridis, plasma, coolwarm, jet
    pointSize: 8,
    lineWidth: 2,
    opacity: 0.8,
    theme: 'light', // light, dark
    binCount: 10, // 直方图分箱数
    smooth: true // 折线图平滑
  })
  
  // 导出状态
  const exportStatus = ref({
    busy: false,
    progress: 0,
    lastExportUrl: null,
    lastExportFilename: null,
    error: null
  })
  
  // 预设配置
  const presets = ref([
    {
      id: 'scatter-basic',
      name: '基础散点图',
      type: 'scatter',
      description: '简单的 X-Y 散点图',
      icon: 'ScatterChart'
    },
    {
      id: 'heatmap-basic',
      name: '热力图',
      type: 'heatmap',
      description: '数据密度热力图',
      icon: 'Grid'
    },
    {
      id: 'surface-3d',
      name: '三维曲面',
      type: 'surface',
      description: '三维曲面图',
      icon: 'Histogram'
    },
    {
      id: 'line-time',
      name: '时序折线图',
      type: 'line',
      description: '时间序列趋势图',
      icon: 'TrendCharts'
    },
    {
      id: 'bar-comparison',
      name: '对比柱状图',
      type: 'bar',
      description: '多组数据对比分析',
      icon: 'Histogram'
    },
    {
      id: 'box-distribution',
      name: '箱线图',
      type: 'box',
      description: '数据分布与异常值分析',
      icon: 'DataBoard'
    },
    {
      id: 'histogram-distribution',
      name: '直方图',
      type: 'histogram',
      description: '数据频数分布分析',
      icon: 'DataAnalysis'
    }
  ])
  
  // 历史记录（最多保存 20 条）
  const history = ref([])
  const maxHistorySize = 20
  
  // ========== 计算属性 ==========
  
  const currentDataset = computed(() => {
    return currentDatasetId.value ? datasets.value[currentDatasetId.value] : null
  })
  
  const datasetList = computed(() => {
    return Object.values(datasets.value).sort((a, b) => b.createdAt - a.createdAt)
  })
  
  const hasData = computed(() => {
    return currentDataset.value && currentDataset.value.parsedData.length > 0
  })
  
  const availableFields = computed(() => {
    if (!currentDataset.value) return []
    return currentDataset.value.columns.map(col => ({
      name: col.name,
      type: col.type,
      stats: col.stats
    }))
  })
  
  const numericFields = computed(() => {
    return availableFields.value.filter(f => f.type === 'number')
  })
  
  const categoricalFields = computed(() => {
    return availableFields.value.filter(f => f.type === 'string')
  })
  
  // ========== 数据集操作 ==========
  
  /**
   * 导入数据集
   * @param {Object} options - { name, rawData, source, fileType }
   * @returns {string} datasetId
   */
  function importDataset({ name, rawData, source = 'upload', fileType = 'csv' }) {
    const id = `dataset_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    datasets.value[id] = {
      id,
      name,
      rawData, // 原始数据（字符串或对象数组）
      parsedData: [], // 解析后的数据
      columns: [], // 列信息
      source,
      fileType,
      createdAt: Date.now(),
      meta: {
        rowCount: 0,
        columnCount: 0,
        fileSize: rawData.length || 0
      }
    }
    
    currentDatasetId.value = id
    return id
  }
  
  /**
   * 设置解析后的数据
   * @param {string} id - 数据集 ID
   * @param {Array} data - 解析后的数据
   * @param {Array} columns - 列信息
   */
  function setParsedData(id, data, columns) {
    if (!datasets.value[id]) return
    
    datasets.value[id].parsedData = data
    datasets.value[id].columns = columns
    datasets.value[id].meta.rowCount = data.length
    datasets.value[id].meta.columnCount = columns.length
  }
  
  /**
   * 删除数据集
   */
  function deleteDataset(id) {
    if (datasets.value[id]) {
      delete datasets.value[id]
      
      // 如果删除的是当前数据集，切换到其他数据集
      if (currentDatasetId.value === id) {
        const remaining = Object.keys(datasets.value)
        currentDatasetId.value = remaining.length > 0 ? remaining[0] : null
      }
    }
  }
  
  /**
   * 切换当前数据集
   */
  function setCurrentDataset(id) {
    if (datasets.value[id]) {
      currentDatasetId.value = id
    }
  }
  
  /**
   * 清空所有数据集
   */
  function clearAllDatasets() {
    datasets.value = {}
    currentDatasetId.value = null
  }
  
  // ========== 图表配置操作 ==========
  
  /**
   * 更新图表配置
   */
  function updateChartConfig(updates) {
    chartConfig.value = {
      ...chartConfig.value,
      ...updates
    }
  }
  
  /**
   * 重置图表配置为默认值
   */
  function resetChartConfig() {
    chartConfig.value = {
      type: 'scatter',
      xField: null,
      yField: null,
      zField: null,
      colorField: null,
      sizeField: null,
      groupField: null,
      title: '科研图表',
      xAxisLabel: 'X轴',
      yAxisLabel: 'Y轴',
      zAxisLabel: 'Z轴',
      showLegend: true,
      showGrid: true,
      colorScheme: 'viridis',
      pointSize: 8,
      lineWidth: 2,
      opacity: 0.8,
      theme: 'light',
      binCount: 10,
      smooth: true
    }
  }
  
  /**
   * 自动配置图表（根据数据类型智能选择字段）
   */
  function autoConfigureChart() {
    if (!hasData.value) return
    
    const numeric = numericFields.value
    const categorical = categoricalFields.value
    
    // 根据图表类型自动选择字段
    if (chartConfig.value.type === 'scatter' || chartConfig.value.type === 'line') {
      if (numeric.length >= 2) {
        chartConfig.value.xField = numeric[0].name
        chartConfig.value.yField = numeric[1].name
        if (categorical.length > 0) {
          chartConfig.value.groupField = categorical[0].name
        }
      }
    } else if (chartConfig.value.type === 'surface') {
      if (numeric.length >= 3) {
        chartConfig.value.xField = numeric[0].name
        chartConfig.value.yField = numeric[1].name
        chartConfig.value.zField = numeric[2].name
      }
    } else if (chartConfig.value.type === 'heatmap') {
      if (numeric.length >= 1) {
        chartConfig.value.colorField = numeric[0].name
        if (categorical.length >= 2) {
          chartConfig.value.xField = categorical[0].name
          chartConfig.value.yField = categorical[1].name
        } else if (numeric.length >= 2) {
          chartConfig.value.xField = numeric[0].name
          chartConfig.value.yField = numeric[1].name
        }
      }
    }
  }
  
  // ========== 导出操作 ==========
  
  /**
   * 开始导出
   */
  function startExport() {
    exportStatus.value.busy = true
    exportStatus.value.progress = 0
    exportStatus.value.error = null
  }
  
  /**
   * 更新导出进度
   */
  function updateExportProgress(progress) {
    exportStatus.value.progress = progress
  }
  
  /**
   * 完成导出
   */
  function completeExport(url, filename) {
    exportStatus.value.busy = false
    exportStatus.value.progress = 100
    exportStatus.value.lastExportUrl = url
    exportStatus.value.lastExportFilename = filename
  }
  
  /**
   * 导出失败
   */
  function failExport(error) {
    exportStatus.value.busy = false
    exportStatus.value.error = error
  }
  
  /**
   * 重置导出状态
   */
  function resetExportStatus() {
    exportStatus.value = {
      busy: false,
      progress: 0,
      lastExportUrl: null,
      lastExportFilename: null,
      error: null
    }
  }
  
  // ========== 预设与历史 ==========
  
  /**
   * 保存当前配置到历史
   */
  function saveToHistory(label = '') {
    const snapshot = {
      id: `history_${Date.now()}`,
      label: label || `配置 - ${new Date().toLocaleString()}`,
      timestamp: Date.now(),
      datasetId: currentDatasetId.value,
      config: JSON.parse(JSON.stringify(chartConfig.value))
    }
    
    history.value.unshift(snapshot)
    
    // 限制历史记录数量
    if (history.value.length > maxHistorySize) {
      history.value = history.value.slice(0, maxHistorySize)
    }
  }
  
  /**
   * 从历史恢复配置
   */
  function restoreFromHistory(historyId) {
    const snapshot = history.value.find(h => h.id === historyId)
    if (!snapshot) return false
    
    // 恢复数据集
    if (snapshot.datasetId && datasets.value[snapshot.datasetId]) {
      currentDatasetId.value = snapshot.datasetId
    }
    
    // 恢复配置
    chartConfig.value = JSON.parse(JSON.stringify(snapshot.config))
    
    return true
  }
  
  /**
   * 删除历史记录
   */
  function deleteHistory(historyId) {
    const index = history.value.findIndex(h => h.id === historyId)
    if (index !== -1) {
      history.value.splice(index, 1)
    }
  }
  
  /**
   * 清空历史
   */
  function clearHistory() {
    history.value = []
  }
  
  /**
   * 加载预设配置
   */
  function loadPreset(presetId) {
    const preset = presets.value.find(p => p.id === presetId)
    if (!preset) return false
    
    chartConfig.value.type = preset.type
    autoConfigureChart()
    
    return true
  }
  
  return {
    // 状态
    datasets,
    currentDatasetId,
    chartConfig,
    exportStatus,
    presets,
    history,
    
    // 计算属性
    currentDataset,
    datasetList,
    hasData,
    availableFields,
    numericFields,
    categoricalFields,
    
    // 数据集操作
    importDataset,
    setParsedData,
    deleteDataset,
    setCurrentDataset,
    clearAllDatasets,
    
    // 图表配置
    updateChartConfig,
    resetChartConfig,
    autoConfigureChart,
    
    // 导出操作
    startExport,
    updateExportProgress,
    completeExport,
    failExport,
    resetExportStatus,
    
    // 历史与预设
    saveToHistory,
    restoreFromHistory,
    deleteHistory,
    removeHistoryItem: deleteHistory, // 别名
    clearHistory,
    loadPreset
  }
})
