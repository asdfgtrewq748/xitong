/**
 * ECharts 图表封装工具
 * 提供统一的初始化、更新、导出接口
 */
import * as echarts from 'echarts'
import 'echarts-gl' // 3D 支持

/**
 * 数据验证工具函数
 */

/**
 * 验证点数据有效性
 */
export function isValidPoint(point) {
  return point &&
    point !== null &&
    typeof point === 'object' &&
    (typeof point.x === 'number' || point.x !== undefined) &&
    typeof point.y === 'number' &&
    !isNaN(point.y) &&
    isFinite(point.y)
}

/**
 * 验证箱线图数据有效性
 */
export function isValidBoxPlotItem(item) {
  return item &&
    typeof item.min === 'number' &&
    typeof item.q1 === 'number' &&
    typeof item.median === 'number' &&
    typeof item.q3 === 'number' &&
    typeof item.max === 'number' &&
    !isNaN(item.min) && !isNaN(item.q1) && !isNaN(item.median) &&
    !isNaN(item.q3) && !isNaN(item.max) &&
    item.min <= item.q1 && item.q1 <= item.median &&
    item.median <= item.q3 && item.q3 <= item.max
}

/**
 * 验证热力图数据有效性
 */
export function isValidHeatmapData(data) {
  return Array.isArray(data) &&
    data.every(point =>
      Array.isArray(point) &&
      point.length >= 3 &&
      point.every(coord => typeof coord === 'number' && !isNaN(coord))
    )
}

/**
 * 验证3D曲面图数据有效性
 */
export function isValidSurfaceData(data) {
  return data &&
    Array.isArray(data.x) && Array.isArray(data.y) && Array.isArray(data.z) &&
    data.x.length > 0 && data.y.length > 0 && data.z.length > 0 &&
    data.z.every(row =>
      Array.isArray(row) &&
      row.length === data.x.length &&
      row.every(val => typeof val === 'number' && !isNaN(val))
    )
}

/**
 * 过滤和清理点数据
 */
export function cleanPointData(points) {
  if (!Array.isArray(points)) return []
  return points.filter(isValidPoint)
}

/**
 * 过滤和清理箱线图数据
 */
export function cleanBoxPlotData(items) {
  if (!Array.isArray(items)) return []
  return items.filter(isValidBoxPlotItem)
}

/**
 * 清理数值数组
 */
export function cleanNumericArray(arr) {
  if (!Array.isArray(arr)) return []
  return arr.filter(val => typeof val === 'number' && !isNaN(val) && isFinite(val))
}

/**
 * 计算数值范围
 */
export function calculateNumericRange(values) {
  const cleanValues = cleanNumericArray(values)
  if (cleanValues.length === 0) return { min: 0, max: 0, range: 0 }

  const min = Math.min(...cleanValues)
  const max = Math.max(...cleanValues)
  return { min, max, range: max - min }
}

/**
 * 安全的数值格式化
 */
export function safeFormatNumber(value, decimals = 2) {
  if (typeof value !== 'number' || isNaN(value) || !isFinite(value)) {
    return 'N/A'
  }
  return value.toFixed(decimals)
}

/**
 * 创建图表包装器
 */
export class ChartWrapper {
  constructor(container, options = {}) {
    this.container = container
    this.instance = null
    this.theme = options.theme || 'light'
    this.options = options
    this.resizeObserver = null
    this.resizeTimer = null
  }
  
  /**
   * 初始化图表
   * @param {Object} options - 可选参数，如 { renderer: 'svg' }
   */
  init(options = {}) {
    if (this.instance) {
      this.dispose()
    }
    
    // 合并初始化参数，允许动态指定 renderer
    const initOptions = {
      renderer: options.renderer || this.options.renderer || 'canvas',
      useDirtyRect: true, // 开启脏矩形优化
      ...this.options.initOptions,
      ...options
    }
    
    this.instance = echarts.init(this.container, this.theme, initOptions)
    
    // 设置自动 resize
    this.setupAutoResize()
    
    return this.instance
  }
  
  /**
   * 更新图表配置
   * @param {Object} option - ECharts 配置
   * @param {Boolean} notMerge - 是否不合并
   */
  update(option, notMerge = false) {
    if (!this.instance) {
      this.init()
    }
    
    this.instance.setOption(option, notMerge)
  }
  
  /**
   * 设置主题
   */
  setTheme(theme) {
    if (this.theme === theme) return
    
    this.theme = theme
    const currentOption = this.instance?.getOption()
    this.dispose()
    this.init()
    
    if (currentOption) {
      this.update(currentOption)
    }
  }
  
  /**
   * 导出为图像
   * @param {Object} options - 导出选项
   * @returns {String} DataURL
   */
  exportImage(options = {}) {
    if (!this.instance) return null
    
    const {
      type = 'png',
      pixelRatio = 2,
      backgroundColor = '#ffffff'
    } = options
    
    return this.instance.getDataURL({
      type,
      pixelRatio,
      backgroundColor
    })
  }
  
  /**
   * 导出为 SVG
   * @returns {String} SVG 字符串
   */
  exportSVG() {
    if (!this.instance) return null
    
    try {
      return this.instance.renderToSVGString()
    } catch (error) {
      console.error('SVG 导出不支持:', error)
      return null
    }
  }
  
  /**
   * 显示加载动画
   */
  showLoading(text = '加载中...') {
    if (this.instance) {
      this.instance.showLoading('default', {
        text,
        color: '#409EFF',
        textColor: '#000',
        maskColor: 'rgba(255, 255, 255, 0.8)',
        zlevel: 0
      })
    }
  }
  
  /**
   * 隐藏加载动画
   */
  hideLoading() {
    if (this.instance) {
      this.instance.hideLoading()
    }
  }
  
  /**
   * 设置自动调整大小
   */
  setupAutoResize() {
    // 使用 ResizeObserver 监听容器大小变化
    if (window.ResizeObserver) {
      this.resizeObserver = new ResizeObserver(() => {
        this.resizeDebounced()
      })
      this.resizeObserver.observe(this.container)
    } else {
      // 降级到 window resize
      window.addEventListener('resize', this.resizeDebounced.bind(this))
    }
  }
  
  /**
   * 防抖的 resize 方法
   */
  resizeDebounced() {
    if (this.resizeTimer) {
      clearTimeout(this.resizeTimer)
    }
    this.resizeTimer = setTimeout(() => {
      this.resize()
    }, 100)
  }
  
  /**
   * 手动调整大小
   */
  resize() {
    if (this.instance && !this.instance.isDisposed()) {
      // 使用 requestAnimationFrame 确保在渲染帧之外调用
      requestAnimationFrame(() => {
        if (this.instance && !this.instance.isDisposed()) {
          this.instance.resize()
        }
      })
    }
  }
  
  /**
   * 获取实例
   */
  getInstance() {
    return this.instance
  }
  
  /**
   * 清除图表
   */
  clear() {
    if (this.instance) {
      this.instance.clear()
    }
  }
  
  /**
   * 销毁图表
   */
  dispose() {
    if (this.resizeTimer) {
      clearTimeout(this.resizeTimer)
      this.resizeTimer = null
    }
    
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
      this.resizeObserver = null
    }
    
    if (this.instance) {
      this.instance.dispose()
      this.instance = null
    }
  }
}

/**
 * 科研级颜色方案配置
 */
export const ColorSchemes = {
  // 经典科学配色方案
  viridis: ['#440154', '#31688e', '#35b779', '#fde724'],
  plasma: ['#0d0887', '#7e03a8', '#cc4778', '#f89540', '#f0f921'],
  magma: ['#000004', '#180f3d', '#440f76', '#721f81', '#9d2d6f', '#cd4071', '#f1605d', '#fd9668', '#feca8d', '#fcffa4'],
  inferno: ['#000004', '#1b0c41', '#4a0c6b', '#781c6d', '#a52c60', '#ce4e7a', '#f1605d', '#fd9668', '#feca8d', '#fcffa4'],

  // 色盲友好配色方案
  colorblind_friendly: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
  okabe_ito: ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7'],
  wong: ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7'],

  // 科学期刊标准配色
  nature_palette: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
  science_palette: ['#0173b2', '#de8f05', '#029e73', '#cc78bc', '#ca9161', '#fbafe4', '#949494', '#ece133', '#56b4e9'],
  cell_palette: ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#F0E442', '#56B4E9', '#D55E00'],

  // 专业学术配色
  academic: ['#2c3e50', '#e74c3c', '#3498db', '#f39c12', '#27ae60', '#9b59b6', '#1abc9c', '#34495e'],
  publication: ['#08519c', '#a50f15', '#006d2c', '#d94801', '#7a0177', '#0868ac', '#fdae61', '#abdda4'],
  thesis: ['#2c3e50', '#34495e', '#7f8c8d', '#95a5a6', '#bdc3c7', '#ecf0f1', '#3498db', '#e74c3c'],

  // 连续色谱
  coolwarm: ['#3b4cc0', '#7396f5', '#b0cbf7', '#f6bfa6', '#f07e6e', '#dd4c43', '#b40426'],
  blue_red: ['#0571b0', '#92c5de', '#f7f7f7', '#f4a582', '#ca0020'],
  green_red: ['#008837', '#a6dba0', '#f7f7f7', '#e2c1a6', '#b2182b'],

  // 基础配色方案
  rainbow: ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00', '#FF7F00', '#FF0000'],
  hot: ['#000000', '#330000', '#660000', '#990000', '#CC0000', '#FF0000', '#FF3300', '#FF6600', '#FF9900', '#FFCC00', '#FFFF00', '#FFFFFF'],
  cool: ['#00FFFF', '#00EEFF', '#00DDFF', '#00CCFF', '#00BBFF', '#00AAFF', '#0099FF', '#0088FF', '#0077FF', '#0066FF', '#0055FF', '#FF00FF'],
  terrain: ['#333399', '#3366CC', '#0099CC', '#00CC99', '#33CC66', '#66CC33', '#99CC00', '#CCCC00', '#CC9900', '#CC6600', '#CC3300', '#FFFFFF'],

  // Matplotlib 经典配色方案（匹配 sanweiyuntu.py）
  jet: ['#00007F', '#0000FF', '#007FFF', '#00FFFF', '#7FFF7F', '#FFFF00', '#FF7F00', '#FF0000', '#7F0000'],
  seismic: ['#00004C', '#0000E6', '#4D4DFF', '#B3B3FF', '#FFFFFF', '#FFB3B3', '#FF4D4D', '#E60000', '#4C0000'],
  YlOrRd: ['#FFFFCC', '#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026'],
  RdYlBu: ['#A50026', '#D73027', '#F46D43', '#FDAE61', '#FEE090', '#E0F3F8', '#ABD9E9', '#74ADD1', '#4575B4', '#313695'],
  Spectral: ['#9E0142', '#D53E4F', '#F46D43', '#FDAE61', '#FEE08B', '#E6F598', '#ABDDA4', '#66C2A5', '#3288BD', '#5E4FA2'],

  // 灰度系列（黑白印刷友好）
  greys: ['#f7f7f7', '#cccccc', '#969696', '#636363', '#252525'],
  scientific_grey: ['#2b2b2b', '#525252', '#737373', '#969696', '#bdbdbd', '#d9d9d9', '#f7f7f7'],

  // 单色渐变
  blues: ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],
  reds: ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15', '#67000d'],
  greens: ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#41ab5d', '#238b45', '#006d2c', '#00441b'],
  purples: ['#fcfbfd', '#efedf5', '#dadaeb', '#bcbddc', '#9e9ac8', '#807dba', '#6a51a3', '#54278f', '#3f007d'],
  oranges: ['#fff5eb', '#fee6ce', '#fdd0a2', '#fdae6b', '#fd8d3c', '#f16913', '#d94801', '#a63603', '#7f2704']
}

/**
 * 获取颜色方案
 */
export function getColorScheme(name) {
  return ColorSchemes[name] || ColorSchemes.viridis
}

/**
 * 学术字体配置
 */
export const AcademicFonts = {
  // 西文字体
  times_new_roman: {
    family: 'Times New Roman, serif',
    description: '经典学术字体，多数期刊推荐'
  },
  arial: {
    family: 'Arial, sans-serif',
    description: '清晰易读，适合数据展示'
  },
  helvetica: {
    family: 'Helvetica, sans-serif',
    description: '现代无衬线字体，科学期刊常用'
  },
  calibri: {
    family: 'Calibri, sans-serif',
    description: 'Microsoft默认字体，学术友好'
  },
  georgia: {
    family: 'Georgia, serif',
    description: '优雅衬线字体，适合标题'
  },

  // 中文字体
  songti: {
    family: 'SimSun, serif',
    description: '宋体，中文学术标准'
  },
  heiti: {
    family: 'SimHei, sans-serif',
    description: '黑体，适合标题和重点'
  },
  kaiti: {
    family: 'KaiTi, serif',
    description: '楷体，优雅中文字体'
  },
  fangsong: {
    family: 'FangSong, serif',
    description: '仿宋，传统学术字体'
  },

  // 备用字体配置
  fallback: {
    family: '"Times New Roman", "SimSun", serif',
    description: '中英文备用字体组合'
  }
}

/**
 * 字体大小规范（像素）
 */
export const FontSizes = {
  caption: 10,      // 图例、标注
  axis: 12,         // 坐标轴标签
  subtitle: 14,     // 副标题
  title: 16,        // 主标题
  large: 18,        // 大标题
  small: 8          // 小字体
}

/**
 * 获取学术字体配置
 */
export function getAcademicFont(fontName = 'times_new_roman') {
  const font = AcademicFonts[fontName] || AcademicFonts.times_new_roman
  return {
    ...font,
    sizes: FontSizes
  }
}

/**
 * 图表样式配置（期刊标准）
 */
export const JournalStyles = {
  // Nature期刊风格
  nature: {
    title: {
      fontSize: 16,
      fontWeight: 'bold',
      fontFamily: 'Arial, sans-serif',
      color: '#000000'
    },
    axis: {
      fontSize: 12,
      fontFamily: 'Arial, sans-serif',
      color: '#000000'
    },
    legend: {
      fontSize: 10,
      fontFamily: 'Arial, sans-serif',
      color: '#000000'
    },
    grid: {
      show: true,
      lineStyle: {
        color: '#cccccc',
        width: 0.5,
        type: 'solid'
      }
    },
    backgroundColor: '#ffffff'
  },

  // Science期刊风格
  science: {
    title: {
      fontSize: 14,
      fontWeight: 'bold',
      fontFamily: 'Helvetica, Arial, sans-serif',
      color: '#000000'
    },
    axis: {
      fontSize: 11,
      fontFamily: 'Helvetica, Arial, sans-serif',
      color: '#000000'
    },
    legend: {
      fontSize: 9,
      fontFamily: 'Helvetica, Arial, sans-serif',
      color: '#000000'
    },
    grid: {
      show: false
    },
    backgroundColor: '#ffffff'
  },

  // IEEE期刊风格
  ieee: {
    title: {
      fontSize: 12,
      fontWeight: 'bold',
      fontFamily: 'Times New Roman, serif',
      color: '#000000'
    },
    axis: {
      fontSize: 10,
      fontFamily: 'Times New Roman, serif',
      color: '#000000'
    },
    legend: {
      fontSize: 9,
      fontFamily: 'Times New Roman, serif',
      color: '#000000'
    },
    grid: {
      show: true,
      lineStyle: {
        color: '#888888',
        width: 0.3,
        type: 'dashed'
      }
    },
    backgroundColor: '#ffffff'
  },

  // 默认学术风格 (用户要求的样式)
  academic: {
    title: {
      fontSize: FontSizes.title,
      fontWeight: 'bold',
      fontFamily: 'SimSun, "Times New Roman", serif', // 中文宋体,英文Times New Roman
      color: '#000000'
    },
    axis: {
      fontSize: FontSizes.axis,
      fontFamily: 'SimSun, "Times New Roman", serif',
      color: '#000000'
    },
    legend: {
      fontSize: FontSizes.caption,
      fontFamily: 'SimSun, "Times New Roman", serif',
      color: '#000000'
    },
    grid: {
      show: false, // 删除网格
      lineStyle: {
        color: '#e0e0e0',
        width: 0,
        type: 'solid'
      }
    },
    backgroundColor: 'transparent' // 透明背景
  }
}

/**
 * 获取期刊样式配置
 */
export function getJournalStyle(journal = 'academic') {
  return JournalStyles[journal] || JournalStyles.academic
}

/**
 * 应用通用样式配置 (用户自定义优先)
 * 统一处理网格、背景、字体等设置
 */
export function applyCommonStyle(option, config) {
  const {
    showGrid = false,
    backgroundColor = 'transparent',
    fontFamily = 'SimSun, "Times New Roman", serif'
  } = config

  // 应用背景色 (用户设置优先)
  option.backgroundColor = backgroundColor

  // 应用网格设置
  if (option.grid) {
    option.grid.show = showGrid
  }
  if (option.xAxis) {
    if (Array.isArray(option.xAxis)) {
      option.xAxis.forEach(axis => {
        axis.splitLine = axis.splitLine || {}
        axis.splitLine.show = showGrid
      })
    } else {
      option.xAxis.splitLine = option.xAxis.splitLine || {}
      option.xAxis.splitLine.show = showGrid
    }
  }
  if (option.yAxis) {
    if (Array.isArray(option.yAxis)) {
      option.yAxis.forEach(axis => {
        axis.splitLine = axis.splitLine || {}
        axis.splitLine.show = showGrid
      })
    } else {
      option.yAxis.splitLine = option.yAxis.splitLine || {}
      option.yAxis.splitLine.show = showGrid
    }
  }

  // 应用字体
  const applyFont = (obj) => {
    if (obj && obj.textStyle) {
      obj.textStyle.fontFamily = fontFamily
    }
  }

  applyFont(option.title)
  applyFont(option.legend)
  if (option.xAxis) {
    if (Array.isArray(option.xAxis)) {
      option.xAxis.forEach(axis => {
        if (axis.axisLabel) axis.axisLabel.fontFamily = fontFamily
        if (axis.nameTextStyle) axis.nameTextStyle.fontFamily = fontFamily
      })
    } else {
      if (option.xAxis.axisLabel) option.xAxis.axisLabel.fontFamily = fontFamily
      if (option.xAxis.nameTextStyle) option.xAxis.nameTextStyle.fontFamily = fontFamily
    }
  }
  if (option.yAxis) {
    if (Array.isArray(option.yAxis)) {
      option.yAxis.forEach(axis => {
        if (axis.axisLabel) axis.axisLabel.fontFamily = fontFamily
        if (axis.nameTextStyle) axis.nameTextStyle.fontFamily = fontFamily
      })
    } else {
      if (option.yAxis.axisLabel) option.yAxis.axisLabel.fontFamily = fontFamily
      if (option.yAxis.nameTextStyle) option.yAxis.nameTextStyle.fontFamily = fontFamily
    }
  }

  return option
}

/**
 * 生成散点图配置
 */
export function generateScatterOption(data, config) {
  const {
    title,
    subtitle,
    xAxisLabel,
    yAxisLabel,
    showLegend = true,
    showGrid = false,
    colorScheme = 'viridis',
    pointSize = 10,
    opacity = 0.8,
    journalStyle = 'academic',
    showRegression = false,
    showErrorBars = false,
    // 新增样式配置
    axisLineColor = '#333',
    axisLabelFontSize = 12,
    axisLineWidth = 1,
    showAxisLine = true,
    showAxisTick = true,
    showGridLines = false,
    gridLineColor = '#e0e0e0',
    gridLineWidth = 1,
    xAxisMin = null,
    xAxisMax = null,
    yAxisMin = null,
    yAxisMax = null,
    titleFontSize = 18,
    titleFontWeight = 'bold',
    legendFontSize = 12,
    pointShape = 'circle',
    pointBorderColor = '#fff',
    pointBorderWidth = 0,
    fontFamily = 'SimSun, "Times New Roman", serif'
  } = config

  const style = getJournalStyle(journalStyle)
  // const isDark = theme === 'dark'  // 未使用，已注释
  const textColor = style.title.color
  const bgColor = style.backgroundColor
  
  // 防御性检查：确保数据结构有效
  if (!data || !data.data) {
    return {
      title: { text: title || '散点图', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis: { type: 'value' },
      yAxis: { type: 'value' },
      series: [{ type: 'scatter', data: [] }]
    }
  }
  
  // 处理分组数据
  const series = []
  const colors = getColorScheme(colorScheme)
  
  console.log('[Scatter] Data type:', data.type, 'Point size:', pointSize, 'Opacity:', opacity)
  
  if (data.type === 'grouped') {
    if (data.data && typeof data.data === 'object') {
      let colorIndex = 0
      Object.entries(data.data).forEach(([group, points]) => {
        if (Array.isArray(points) && points.length > 0) {
          console.log(`[Scatter] Group "${group}" has ${points.length} points`)
          series.push({
            name: group,
            type: 'scatter',
            data: points.map(p => [p.x, p.y]),
            symbolSize: pointSize,
            symbol: pointShape,
            itemStyle: {
              opacity,
              color: colors[colorIndex % colors.length],
              borderColor: pointBorderColor,
              borderWidth: pointBorderWidth
            }
          })
          colorIndex++
        }
      })
    }
  } else {
    if (Array.isArray(data.data) && data.data.length > 0) {
      console.log(`[Scatter] Simple data with ${data.data.length} points`)
      series.push({
        name: '数据点',
        type: 'scatter',
        data: data.data.map(p => [p.x, p.y]),
        symbolSize: pointSize,
        symbol: pointShape,
        itemStyle: {
          opacity,
          color: colors[0],
          borderColor: pointBorderColor,
          borderWidth: pointBorderWidth
        }
      })
    }
  }
  
  console.log('[Scatter] Generated', series.length, 'series')
  
  // 学术级布局配置
  const option = {
    title: {
      text: title,
      subtext: subtitle,
      left: 'center',
      top: '5%',
      textStyle: {
        ...style.title,
        fontSize: titleFontSize,
        fontWeight: titleFontWeight,
        fontFamily
      },
      subtextStyle: {
        ...style.title,
        fontSize: axisLabelFontSize,
        fontWeight: 'normal',
        fontFamily
      }
    },
    backgroundColor: bgColor,
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (!params || !params.value || !Array.isArray(params.value)) {
          return params?.seriesName || '数据点'
        }
        let tooltip = `<strong>${params.seriesName || '数据点'}</strong><br/>`
        if (params.value[0] !== undefined) {
          tooltip += `X: ${Number(params.value[0]).toFixed(3)}<br/>`
        }
        if (params.value[1] !== undefined) {
          tooltip += `Y: ${Number(params.value[1]).toFixed(3)}`
        }
        if (params.value[2] !== undefined) {
          tooltip += `<br/>Value: ${Number(params.value[2]).toFixed(3)}`
        }
        return tooltip
      },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#cccccc',
      borderWidth: 1,
      textStyle: { fontSize: 11, fontFamily }
    },
    legend: {
      show: showLegend,
      bottom: '5%',
      left: 'center',
      textStyle: {
        ...style.legend,
        fontSize: legendFontSize,
        fontFamily
      },
      itemGap: 20,
      itemWidth: 12,
      itemHeight: 12
    },
    grid: {
      ...style.grid,
      show: showGrid,
      left: '15%',
      right: '10%',
      bottom: '20%',
      top: '20%',
      containLabel: true,
      tooltip: {
        show: true,
        trigger: 'axis'
      }
    },
    xAxis: {
      type: 'value',
      name: xAxisLabel,
      nameLocation: 'middle',
      nameGap: 30,
      min: xAxisMin,
      max: xAxisMax,
      nameTextStyle: {
        ...style.axis,
        fontSize: axisLabelFontSize,
        fontWeight: 'bold',
        fontFamily
      },
      axisLabel: {
        ...style.axis,
        fontSize: axisLabelFontSize,
        fontFamily,
        formatter: (value) => value.toPrecision(3),
        margin: 10
      },
      axisLine: {
        show: showAxisLine,
        lineStyle: {
          color: axisLineColor,
          width: axisLineWidth
        }
      },
      axisTick: {
        show: showAxisTick,
        length: 5
      },
      splitLine: {
        show: showGridLines,
        lineStyle: {
          color: gridLineColor,
          width: gridLineWidth,
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: yAxisLabel,
      nameLocation: 'middle',
      nameGap: 40,
      min: yAxisMin,
      max: yAxisMax,
      nameTextStyle: {
        ...style.axis,
        fontSize: axisLabelFontSize,
        fontWeight: 'bold',
        fontFamily
      },
      axisLabel: {
        ...style.axis,
        fontSize: axisLabelFontSize,
        fontFamily,
        formatter: (value) => value.toPrecision(3),
        margin: 10
      },
      axisLine: {
        show: showAxisLine,
        lineStyle: {
          color: axisLineColor,
          width: axisLineWidth
        }
      },
      axisTick: {
        show: showAxisTick,
        length: 5
      },
      splitLine: {
        show: showGridLines,
        lineStyle: {
          color: gridLineColor,
          width: gridLineWidth,
          type: 'dashed'
        }
      }
    },
    series,
    color: getColorScheme(colorScheme)
  }

  // 添加误差线
  if (showErrorBars && data.errorBars) {
    data.errorBars.forEach((errorBar, index) => {
      if (series[index]) {
        series[index].errorBar = errorBar
      }
    })
  }

  // 添加回归线
  if (showRegression && data.regression) {
    series.push({
      name: '回归线',
      type: 'line',
      data: data.regression,
      smooth: false,
      lineStyle: {
        color: '#ff0000',
        width: 2,
        type: 'dashed'
      },
      symbol: 'none',
      emphasis: { disabled: true }
    })

    // 添加回归方程
    if (data.regressionEquation) {
      option.graphic = [{
        type: 'text',
        left: '70%',
        top: '10%',
        style: {
          text: `R² = ${data.r2 ? data.r2.toFixed(3) : 'N/A'}`,
          fill: textColor,
          fontSize: style.legend.fontSize,
          fontFamily: style.axis.fontFamily
        }
      }]
    }
  }

  // 应用通用样式配置
  applyCommonStyle(option, config)

  return option
}

  /**
   * 双线性重采样（将原始 z 矩阵从原来的 x/y 网格插值到新的 xNew/yNew 网格）
   * z: 原始二维数组，z[row][col] 对应 y[row], x[col]
   */
  function bilinearResample(z, xOld, yOld, xNew, yNew) {
    // eslint-disable-next-line no-unused-vars
    const nx = xOld.length
    // eslint-disable-next-line no-unused-vars
    const ny = yOld.length
    const nxNew = xNew.length
    const nyNew = yNew.length
    const out = Array.from({ length: nyNew }, () => Array(nxNew).fill(null))

    // 辅助：查找 xOld 的索引区间
    const findIdx = (arr, v) => {
      if (v <= arr[0]) return 0
      if (v >= arr[arr.length - 1]) return arr.length - 2
      let lo = 0, hi = arr.length - 1
      while (lo <= hi) {
        const mid = Math.floor((lo + hi) / 2)
        if (arr[mid] <= v) lo = mid + 1
        else hi = mid - 1
      }
      return Math.max(0, lo - 1)
    }

    for (let i = 0; i < nyNew; i++) {
      for (let j = 0; j < nxNew; j++) {
        const xv = xNew[j]
        const yv = yNew[i]
        const ix = findIdx(xOld, xv)
        const iy = findIdx(yOld, yv)
        const x1 = xOld[ix], x2 = xOld[ix + 1]
        const y1 = yOld[iy], y2 = yOld[iy + 1]
        const q11 = (z[iy] && z[iy][ix] != null) ? z[iy][ix] : null
        const q12 = (z[iy + 1] && z[iy + 1][ix] != null) ? z[iy + 1][ix] : null
        const q21 = (z[iy] && z[iy][ix + 1] != null) ? z[iy][ix + 1] : null
        const q22 = (z[iy + 1] && z[iy + 1][ix + 1] != null) ? z[iy + 1][ix + 1] : null

        // 若部分值缺失，优先使用可用邻域值的平均
        const available = [q11, q12, q21, q22].filter(v => v != null)
        if (available.length === 0) {
          out[i][j] = null
          continue
        }

        // 标准双线性插值
        const dx = (x2 - x1) || 1
        const dy = (y2 - y1) || 1
        const tx = (xv - x1) / dx
        const ty = (yv - y1) / dy

        const interp = (a, b, t) => (a == null || b == null) ? (a != null ? a : b) : (a * (1 - t) + b * t)

        const r1 = interp(q11, q21, tx)
        const r2 = interp(q12, q22, tx)
        const value = interp(r1, r2, ty)
        out[i][j] = value == null ? (available.reduce((s, v) => s + v, 0) / available.length) : value
      }
    }
    return out
  }

  /**
   * 生成高斯核
   */
  function createGaussianKernel(sigma) {
    const radius = Math.ceil(sigma * 3)
    const size = radius * 2 + 1
    const kernel = Array.from({ length: size }, () => Array(size).fill(0))
    const twoSigma2 = 2 * sigma * sigma
    let sum = 0
    for (let y = -radius; y <= radius; y++) {
      for (let x = -radius; x <= radius; x++) {
        const v = Math.exp(-(x * x + y * y) / twoSigma2)
        kernel[y + radius][x + radius] = v
        sum += v
      }
    }
    // 归一化
    for (let i = 0; i < size; i++) for (let j = 0; j < size; j++) kernel[i][j] /= sum
    return { kernel, radius }
  }

  /**
   * 对二维矩阵进行高斯平滑卷积
   */
  function gaussianBlur2D(z, sigma) {
    if (!sigma || sigma <= 0) return z
    const { kernel, radius } = createGaussianKernel(sigma)
    const h = z.length
    const w = z[0] ? z[0].length : 0
    const out = Array.from({ length: h }, () => Array(w).fill(null))

    for (let i = 0; i < h; i++) {
      for (let j = 0; j < w; j++) {
        let sum = 0, weight = 0
        for (let ky = -radius; ky <= radius; ky++) {
          for (let kx = -radius; kx <= radius; kx++) {
            const iy = i + ky
            const jx = j + kx
            if (iy < 0 || iy >= h || jx < 0 || jx >= w) continue
            const val = z[iy][jx]
            if (val == null || isNaN(val)) continue
            const wgt = kernel[ky + radius][kx + radius]
            sum += val * wgt
            weight += wgt
          }
        }
        out[i][j] = weight > 0 ? sum / weight : null
      }
    }
    return out
  }


/**
 * 生成折线图配置
 */
export function generateLineOption(data, config) {
  const {
    title = '折线图',
    xAxisLabel = 'X轴',
    yAxisLabel = 'Y轴',
    showLegend = true,
    showGrid = false,
    colorScheme = 'default',
    backgroundColor = 'transparent',
    fontFamily = 'SimSun, "Times New Roman", serif',
    
    // 线条样式
    lineWidth = 2,
    lineType = 'solid',
    smooth = false,
    showSymbol = true,
    symbolSize = 6,
    showArea = false,
    areaOpacity = 0.3,
    
    // 坐标轴样式
    axisLineColor = '#333',
    axisLabelFontSize = 12,
    axisLineWidth = 1,
    showAxisLine = true,
    showAxisTick = true,
    showGridLines = false,
    gridLineColor = '#e0e0e0',
    gridLineWidth = 1,
    
    // 字体样式
    titleFontSize = 18,
    titleFontWeight = 'bold',
    legendFontSize = 12
  } = config

  const textColor = '#333333'
  
  // 防御性检查：确保数据结构有效
  if (!data || !data.data) {
    return {
      title: { text: title, left: 'center', textStyle: { color: textColor, fontFamily } },
      backgroundColor,
      xAxis: { type: 'value' },
      yAxis: { type: 'value' },
      series: [{ type: 'line', data: [] }]
    }
  }
  
  // 生成系列数据
  const series = []
  if (data.type === 'grouped') {
    if (data.data && typeof data.data === 'object') {
      Object.entries(data.data).forEach(([group, points]) => {
        if (Array.isArray(points) && points.length > 0) {
          const seriesItem = {
            name: group,
            type: 'line',
            data: points.map(p => [p.x, p.y]),
            smooth,
            showSymbol,
            symbolSize,
            lineStyle: {
              width: lineWidth,
              type: lineType
            }
          }
          
          // 添加面积图配置
          if (showArea) {
            seriesItem.areaStyle = {
              opacity: areaOpacity
            }
          }
          
          series.push(seriesItem)
        }
      })
    }
  } else {
    if (Array.isArray(data.data) && data.data.length > 0) {
      const seriesItem = {
        name: '数据',
        type: 'line',
        data: data.data.map(p => [p.x, p.y]),
        smooth,
        showSymbol,
        symbolSize,
        lineStyle: {
          width: lineWidth,
          type: lineType
        }
      }
      
      // 添加面积图配置
      if (showArea) {
        seriesItem.areaStyle = {
          opacity: areaOpacity
        }
      }
      
      series.push(seriesItem)
    }
  }
  
  const option = {
    title: {
      text: title,
      left: 'center',
      textStyle: {
        color: textColor,
        fontSize: titleFontSize,
        fontWeight: titleFontWeight,
        fontFamily
      }
    },
    backgroundColor,
    tooltip: {
      trigger: 'axis',
      textStyle: {
        fontFamily
      }
    },
    legend: {
      show: showLegend,
      bottom: 10,
      textStyle: {
        color: textColor,
        fontSize: legendFontSize,
        fontFamily
      }
    },
    grid: {
      show: showGrid,
      left: '10%',
      right: '10%',
      bottom: showLegend ? '15%' : '10%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: xAxisLabel,
      nameTextStyle: {
        color: textColor,
        fontSize: axisLabelFontSize,
        fontFamily
      },
      axisLabel: {
        color: textColor,
        fontSize: axisLabelFontSize,
        fontFamily
      },
      axisLine: {
        show: showAxisLine,
        lineStyle: {
          color: axisLineColor,
          width: axisLineWidth
        }
      },
      axisTick: {
        show: showAxisTick
      },
      splitLine: {
        show: showGridLines,
        lineStyle: {
          color: gridLineColor,
          width: gridLineWidth
        }
      }
    },
    yAxis: {
      type: 'value',
      name: yAxisLabel,
      nameTextStyle: {
        color: textColor,
        fontSize: axisLabelFontSize,
        fontFamily
      },
      axisLabel: {
        color: textColor,
        fontSize: axisLabelFontSize,
        fontFamily
      },
      axisLine: {
        show: showAxisLine,
        lineStyle: {
          color: axisLineColor,
          width: axisLineWidth
        }
      },
      axisTick: {
        show: showAxisTick
      },
      splitLine: {
        show: showGridLines,
        lineStyle: {
          color: gridLineColor,
          width: gridLineWidth
        }
      }
    },
    series,
    color: getColorScheme(colorScheme)
  }

  return option
}

/**
 * 生成热力图配置
 */
export function generateHeatmapOption(data, config) {
  const { 
    title, 
    xAxisLabel, 
    yAxisLabel, 
    colorScheme,
    showValues = true,
    showGrid = false,
    showColorBar = true,
    valueFontSize = 12,
    titleFontSize = 18,
    colorRange = 'auto',
    fontFamily = 'SimSun, "Times New Roman", serif'
  } = config

  const textColor = '#333333'
  const bgColor = '#ffffff'
  
  // 防御性检查：确保数据结构有效
  if (!data || !Array.isArray(data.data) || data.data.length === 0 || 
      !Array.isArray(data.xValues) || !Array.isArray(data.yValues)) {
    return {
      title: { text: title || '热力图', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'category', data: [] },
      series: [{ type: 'heatmap', data: [] }]
    }
  }
  
  const option = {
    title: {
      text: title,
      left: 'center',
      textStyle: { 
        color: textColor,
        fontSize: titleFontSize,
        fontFamily
      }
    },
    backgroundColor: bgColor,
    tooltip: {
      position: 'top',
      formatter: function(params) {
        return `${data.xValues[params.value[0]]}<br/>${data.yValues[params.value[1]]}<br/>值: ${params.value[2].toFixed(2)}`
      }
    },
    grid: {
      left: '10%',
      right: showColorBar ? '15%' : '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.xValues,
      name: xAxisLabel,
      nameTextStyle: { color: textColor, fontFamily },
      axisLabel: { color: textColor, fontFamily },
      splitLine: { show: showGrid, lineStyle: { color: '#e0e0e0' } }
    },
    yAxis: {
      type: 'category',
      data: data.yValues,
      name: yAxisLabel,
      nameTextStyle: { color: textColor, fontFamily },
      axisLabel: { color: textColor, fontFamily },
      splitLine: { show: showGrid, lineStyle: { color: '#e0e0e0' } }
    },
    visualMap: {
      show: showColorBar,
      min: colorRange === 'auto' ? Math.min(...data.data.map(d => d[2])) : config.colorMin,
      max: colorRange === 'auto' ? Math.max(...data.data.map(d => d[2])) : config.colorMax,
      calculable: true,
      orient: 'vertical',
      right: '5%',
      top: 'center',
      inRange: {
        color: getColorScheme(colorScheme)
      },
      textStyle: { color: textColor, fontFamily }
    },
    series: [{
      name: '热力值',
      type: 'heatmap',
      data: data.data,
      label: {
        show: showValues,
        fontSize: valueFontSize,
        fontFamily,
        formatter: function(params) {
          return params.value[2].toFixed(1)
        }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  // 应用通用样式配置
  applyCommonStyle(option, config)

  return option
}

/**
 * 生成三维曲面图配置
 */
export function generateSurfaceOption(data, config) {
  const { 
    title, 
    xAxisLabel, 
    yAxisLabel, 
    zAxisLabel, 
    colorScheme,
    viewAngle = 45,
    pitchAngle = 30,
    showWireframe = false,
    grid3D = true,
    // 渲染与采样
    smoothingSigma = 0,
    resolution = null,
    // 色条设置
    showColorBar = true,
    colorBarPosition = 'right',
    colorBarShrink = 0.8,
    colorBarLabel = '数值',
    // 导出设置（pixelRatio在 exportChart 调用时传递，这里仅记录）
    // eslint-disable-next-line no-unused-vars
    exportPixelRatio = 2,
    titleFontSize = 18,
    fontFamily = 'SimSun, "Times New Roman", serif'
  } = config

  const textColor = '#333333'
  const bgColor = '#ffffff'

  // 防御性检查：确保数据结构有效
  if (!data || !Array.isArray(data.x) || !Array.isArray(data.y) || !Array.isArray(data.z) ||
      data.x.length === 0 || data.y.length === 0 || data.z.length === 0) {
    return {
      title: { text: title || '3D曲面', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis3D: { type: 'value' },
      yAxis3D: { type: 'value' },
      zAxis3D: { type: 'value' },
      grid3D: {},
      series: [{ type: 'surface', data: [] }]
    }
  }

  const option = {
    title: {
      text: title,
      left: 'center',
      textStyle: { 
        color: textColor,
        fontSize: titleFontSize,
        fontFamily
      }
    },
    backgroundColor: bgColor,
    tooltip: {
      formatter: function(params) {
        if (params.value) {
          return `X: ${params.value[0].toFixed(2)}<br/>Y: ${params.value[1].toFixed(2)}<br/>Z: ${params.value[2].toFixed(2)}`
        }
        return ''
      }
    },
    visualMap: {
      show: showColorBar,
      dimension: 2,
      min: Math.min(...data.z.flat().filter(v => v != null)),
      max: Math.max(...data.z.flat().filter(v => v != null)),
      inRange: {
        color: getColorScheme(colorScheme)
      },
      // 色条位置与样式（模拟 matplotlib colorbar 的 pad, shrink, aspect）
      orient: colorBarPosition === 'bottom' ? 'horizontal' : 'vertical',
      left: colorBarPosition === 'left' ? '5%' : (colorBarPosition === 'bottom' ? 'center' : undefined),
      right: colorBarPosition === 'right' ? '5%' : undefined,
      bottom: colorBarPosition === 'bottom' ? '5%' : undefined,
      top: colorBarPosition === 'bottom' ? undefined : 'center',
      // shrink 映射为 visualMap 的 itemHeight/itemWidth
      itemHeight: colorBarPosition === 'bottom' ? undefined : `${Math.floor(colorBarShrink * 200)}`,
      itemWidth: colorBarPosition === 'bottom' ? `${Math.floor(colorBarShrink * 200)}` : undefined,
      text: [colorBarLabel || '高', '低'],
      textStyle: { color: textColor, fontFamily, fontSize: 11 },
      calculable: true
    },
    xAxis3D: {
      name: xAxisLabel,
      type: 'value',
      nameTextStyle: { color: textColor, fontFamily },
      axisLabel: { color: textColor, fontFamily }
    },
    yAxis3D: {
      name: yAxisLabel,
      type: 'value',
      nameTextStyle: { color: textColor, fontFamily },
      axisLabel: { color: textColor, fontFamily }
    },
    zAxis3D: {
      name: zAxisLabel,
      type: 'value',
      nameTextStyle: { color: textColor, fontFamily },
      axisLabel: { color: textColor, fontFamily }
    },
    grid3D: {
      show: grid3D,
      boxWidth: 100,
      boxHeight: 100,
      boxDepth: 100,
      viewControl: {
        projection: 'perspective',
        alpha: pitchAngle,
        beta: viewAngle,
        distance: 200,
        autoRotate: false,
        rotateSensitivity: 1,
        zoomSensitivity: 1
      },
      light: {
        main: {
          shadow: true,
          intensity: 1.2
        },
        ambient: {
          intensity: 0.4
        }
      }
    },
    series: [{
      type: 'surface',
      data: (() => {
        // 处理重采样与平滑：如果 resolution 指定，则对 x/y 进行均匀重采样并双线性插值
        let x = data.x.slice()
        let y = data.y.slice()
        let z = data.z.map(r => r.slice())

        // 保证 z 为二维数值矩阵
        const toNumber = v => (v == null || isNaN(v) ? null : Number(v))
        z = z.map(row => row.map(toNumber))

        // 重采样
        if (resolution && Number.isInteger(resolution) && resolution > 2) {
          const xMin = Math.min(...x)
          const xMax = Math.max(...x)
          const yMin = Math.min(...y)
          const yMax = Math.max(...y)
          const nx = resolution
          const ny = resolution
          const xNew = Array.from({ length: nx }, (_, i) => xMin + (xMax - xMin) * i / (nx - 1))
          const yNew = Array.from({ length: ny }, (_, i) => yMin + (yMax - yMin) * i / (ny - 1))
          z = bilinearResample(z, x, y, xNew, yNew)
          x = xNew
          y = yNew
        }

        // 平滑（高斯卷积）
        if (smoothingSigma && smoothingSigma > 0) {
          z = gaussianBlur2D(z, smoothingSigma)
        }

        // 将矩阵转换为 [x,y,z] 三元组数组
        const triples = []
        for (let i = 0; i < y.length; i++) {
          for (let j = 0; j < x.length; j++) {
            const val = z[i] && z[i][j]
            if (val == null || isNaN(val)) continue
            triples.push([x[j], y[i], val])
          }
        }
        return triples
      })(),
      shading: 'color',
      wireframe: {
        show: showWireframe,
        lineStyle: {
          color: 'rgba(0,0,0,0.3)',
          width: 1
        }
      }
    }]
  }

  // 应用通用样式配置
  applyCommonStyle(option, config)

  return option
}

/**
 * 生成柱状图配置（修复版本）
 */
export function generateBarOption(data, config) {
  const {
    title,
    subtitle,
    xAxisLabel,
    yAxisLabel,
    showLegend,
    showGrid,
    colorScheme,
    opacity,
    journalStyle = 'academic',
    barWidth = 40,
    showLabel = true,
    titleFontSize = 18,
    fontFamily = 'SimSun, "Times New Roman", serif'
  } = config

  const style = getJournalStyle(journalStyle)
  const textColor = style.title.color
  const bgColor = style.backgroundColor

  // 防御性检查：确保数据结构有效
  if (!data || !data.data) {
    return {
      title: { text: title || '柱状图', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [] }]
    }
  }

  const series = []
  let xAxisData = []

  if (data.type === 'grouped') {
    if (data.data && typeof data.data === 'object') {
      Object.entries(data.data).forEach(([group, points]) => {
        if (Array.isArray(points) && points.length > 0) {
          // 验证数据有效性
          const validPoints = points.filter(p =>
            p && (p.x !== undefined && p.x !== null) && typeof p.y === 'number'
          )
          if (validPoints.length > 0) {
            series.push({
              name: group,
              type: 'bar',
              data: validPoints.map(p => ({
                name: p.x,
                value: p.y
              })),
              itemStyle: {
                opacity: opacity || 0.8
              },
              emphasis: {
                itemStyle: {
                  opacity: 1
                }
              }
            })
            xAxisData.push(...validPoints.map(p => p.x))
          }
        }
      })
    }
  } else {
    if (Array.isArray(data.data) && data.data.length > 0) {
      // 验证数据有效性
      const validPoints = data.data.filter(p =>
        p && (p.x !== undefined && p.x !== null) && typeof p.y === 'number'
      )
      if (validPoints.length > 0) {
        series.push({
          name: '数据',
          type: 'bar',
          barWidth: `${barWidth}%`,
          label: {
            show: showLabel,
            position: 'top',
            fontSize: 10,
            fontFamily
          },
          data: validPoints.map(p => ({
            name: p.x,
            value: p.y
          })),
          itemStyle: {
            opacity: opacity || 0.8,
            color: getColorScheme(colorScheme)[0],
            borderColor: getColorScheme(colorScheme)[1],
            borderWidth: 0.5
          },
          emphasis: {
            itemStyle: {
              opacity: 1,
              borderWidth: 1
            }
          }
        })
        xAxisData = validPoints.map(p => p.x)
      }
    }
  }

  // 去重并排序x轴数据
  xAxisData = [...new Set(xAxisData)].sort()

  if (series.length === 0) {
    console.warn('柱状图数据无效，返回空图表')
    return {
      title: { text: title || '柱状图', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [] }]
    }
  }

  const option = {
    title: {
      text: title,
      subtext: subtitle,
      left: 'center',
      top: '5%',
      textStyle: {
        ...style.title,
        fontSize: titleFontSize,
        fontFamily
      },
      subtextStyle: {
        ...style.title,
        fontSize: style.axis.fontSize,
        fontWeight: 'normal',
        fontFamily
      }
    },
    backgroundColor: bgColor,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        if (!params || params.length === 0) return '无数据'
        return params.map(p => {
          const value = p.data?.value || p.value || 'N/A'
          return `${p.seriesName}: ${value}`
        }).join('<br/>')
      },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#cccccc',
      borderWidth: 1,
      textStyle: { fontSize: 11 }
    },
    legend: {
      show: showLegend && series.length > 1,
      bottom: '5%',
      left: 'center',
      textStyle: style.legend,
      itemGap: 20,
      itemWidth: 12,
      itemHeight: 12
    },
    grid: {
      ...style.grid,
      show: showGrid,
      left: '15%',
      right: '10%',
      bottom: '20%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      name: xAxisLabel,
      nameLocation: 'middle',
      nameGap: 30,
      nameTextStyle: {
        ...style.axis,
        fontWeight: 'bold'
      },
      axisLabel: {
        ...style.axis,
        interval: xAxisData.length > 20 ? Math.floor(xAxisData.length / 10) : 0,
        rotate: xAxisData.length > 8 ? 45 : 0,
        margin: 10
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: textColor,
          width: 1
        }
      },
      tickLine: {
        show: true,
        length: 5
      }
    },
    yAxis: {
      type: 'value',
      name: yAxisLabel,
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {
        ...style.axis,
        fontWeight: 'bold'
      },
      axisLabel: {
        ...style.axis,
        formatter: (value) => value.toFixed(1),
        margin: 10
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: textColor,
          width: 1
        }
      },
      tickLine: {
        show: true,
        length: 5
      },
      splitLine: style.grid.show ? {
        show: true,
        lineStyle: style.grid.lineStyle
      } : { show: false }
    },
    series,
    color: getColorScheme(colorScheme)
  }

  // 应用通用样式配置
  applyCommonStyle(option, config)

  return option
}

/**
 * 生成箱线图配置（修复版本）
 */
export function generateBoxPlotOption(data, config) {
  const {
    title,
    subtitle,
    xAxisLabel,
    yAxisLabel,
    showGrid,
    colorScheme,
    journalStyle = 'academic',
    showLegend = true,
    titleFontSize = 18,
    fontFamily = 'SimSun, "Times New Roman", serif'
  } = config

  const style = getJournalStyle(journalStyle)
  const textColor = style.title.color
  const bgColor = style.backgroundColor

  // 防御性检查：确保数据结构有效
  if (!data || !Array.isArray(data.data) || data.data.length === 0) {
    return {
      title: { text: title || '箱线图', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [{ type: 'boxplot', data: [] }]
    }
  }

  // 验证数据完整性
  const validData = data.data.filter(item =>
    item &&
    typeof item.min === 'number' &&
    typeof item.q1 === 'number' &&
    typeof item.median === 'number' &&
    typeof item.q3 === 'number' &&
    typeof item.max === 'number'
  )

  if (validData.length === 0) {
    console.warn('箱线图数据无效，返回空图表')
    return {
      title: { text: title || '箱线图', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [{ type: 'boxplot', data: [] }]
    }
  }

  // 准备箱线图数据
  const boxPlotData = validData.map(item => [item.min, item.q1, item.median, item.q3, item.max])
  const categories = validData.map(item => item.group || item.name || '数据组')

  const option = {
    title: {
      text: title,
      subtext: subtitle,
      left: 'center',
      top: '5%',
      textStyle: {
        ...style.title,
        fontSize: titleFontSize,
        fontFamily
      },
      subtextStyle: {
        ...style.title,
        fontSize: style.axis.fontSize,
        fontWeight: 'normal',
        fontFamily
      }
    },
    backgroundColor: bgColor,
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        if (!params.data || params.data.length < 5) {
          return `${params.name}<br/>数据不完整`
        }
        const [min, q1, median, q3, max] = params.data
        return [
          `<strong>${params.name}</strong>`,
          `最小值: ${min?.toFixed(2) || 'N/A'}`,
          `Q1: ${q1?.toFixed(2) || 'N/A'}`,
          `中位数: ${median?.toFixed(2) || 'N/A'}`,
          `Q3: ${q3?.toFixed(2) || 'N/A'}`,
          `最大值: ${max?.toFixed(2) || 'N/A'}`,
          `IQR: ${((q3 || 0) - (q1 || 0)).toFixed(2)}`
        ].join('<br/>')
      },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#cccccc',
      borderWidth: 1,
      textStyle: { fontSize: 11 }
    },
    legend: {
      show: showLegend && validData.length > 1,
      bottom: '5%',
      left: 'center',
      textStyle: { ...style.legend, fontFamily },
      itemGap: 20,
      itemWidth: 12,
      itemHeight: 12,
      data: validData.map(item => item.name || item.group)
    },
    grid: {
      ...style.grid,
      show: showGrid,
      left: '15%',
      right: '10%',
      bottom: '20%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      name: xAxisLabel,
      nameLocation: 'middle',
      nameGap: 30,
      nameTextStyle: {
        ...style.axis,
        fontWeight: 'bold'
      },
      axisLabel: {
        ...style.axis,
        interval: 0,
        rotate: categories.some(cat => cat.length > 8) ? 45 : 0,
        margin: 10
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: textColor,
          width: 1
        }
      },
      tickLine: {
        show: true,
        length: 5
      }
    },
    yAxis: {
      type: 'value',
      name: yAxisLabel,
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {
        ...style.axis,
        fontWeight: 'bold'
      },
      axisLabel: {
        ...style.axis,
        formatter: (value) => value.toFixed(2),
        margin: 10
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: textColor,
          width: 1
        }
      },
      tickLine: {
        show: true,
        length: 5
      },
      splitLine: style.grid.show ? {
        show: true,
        lineStyle: style.grid.lineStyle
      } : { show: false }
    },
    series: [{
      name: '箱线图',
      type: 'boxplot',
      data: boxPlotData,
      itemStyle: {
        color: getColorScheme(colorScheme)[0],
        borderColor: getColorScheme(colorScheme)[1],
        borderWidth: 1
      },
      emphasis: {
        itemStyle: {
          borderColor: getColorScheme(colorScheme)[2],
          borderWidth: 2
        }
      }
    }],
    color: getColorScheme(colorScheme)
  }

  // 应用通用样式配置
  applyCommonStyle(option, config)

  return option
}

/**
 * 生成直方图配置（修复版本）
 */
export function generateHistogramOption(data, config) {
  const {
    title,
    subtitle,
    xAxisLabel,
    yAxisLabel,
    showGrid,
    colorScheme,
    opacity,
    journalStyle = 'academic',
    showLabel = true,
    titleFontSize = 18,
    fontFamily = 'SimSun, "Times New Roman", serif'
  } = config

  const style = getJournalStyle(journalStyle)
  const textColor = style.title.color
  const bgColor = style.backgroundColor

  // 防御性检查：确保数据结构有效
  if (!data || !Array.isArray(data.data) || data.data.length === 0) {
    return {
      title: { text: title || '直方图', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [] }]
    }
  }

  // 验证数据完整性
  const validBins = data.data.filter(bin =>
    bin && typeof bin.count === 'number' && bin.range
  )

  if (validBins.length === 0) {
    console.warn('直方图数据无效，返回空图表')
    return {
      title: { text: title || '直方图', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [] }]
    }
  }

  const total = data.total || validBins.reduce((sum, bin) => sum + bin.count, 0)

  const option = {
    title: {
      text: title,
      subtext: subtitle,
      left: 'center',
      top: '5%',
      textStyle: {
        ...style.title,
        fontSize: titleFontSize,
        fontFamily
      },
      subtextStyle: {
        ...style.title,
        fontSize: style.axis.fontSize,
        fontWeight: 'normal',
        fontFamily
      }
    },
    backgroundColor: bgColor,
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        if (!params || params.length === 0) return '无数据'
        const data = params[0]
        if (!data || typeof data.value !== 'number') return '数据无效'

        const percentage = ((data.value / total) * 100).toFixed(2)
        const cumulative = validBins
          .slice(0, data.dataIndex + 1)
          .reduce((sum, bin) => sum + bin.count, 0)
        const cumulativePercentage = ((cumulative / total) * 100).toFixed(2)

        return [
          `<strong>${data.axisValueLabel}</strong>`,
          `频数: ${data.value}`,
          `频率: ${percentage}%`,
          `累积频数: ${cumulative}`,
          `累积频率: ${cumulativePercentage}%`
        ].join('<br/>')
      },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#cccccc',
      borderWidth: 1,
      textStyle: { fontSize: 11 }
    },
    grid: {
      ...style.grid,
      show: showGrid,
      left: '15%',
      right: '10%',
      bottom: '20%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: validBins.map(bin => bin.range),
      name: xAxisLabel,
      nameLocation: 'middle',
      nameGap: 30,
      nameTextStyle: {
        ...style.axis,
        fontWeight: 'bold'
      },
      axisLabel: {
        ...style.axis,
        interval: validBins.length > 20 ? Math.floor(validBins.length / 10) : 0,
        rotate: validBins.length > 15 ? 45 : 0,
        margin: 10
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: textColor,
          width: 1
        }
      },
      tickLine: {
        show: true,
        length: 5
      }
    },
    yAxis: {
      type: 'value',
      name: yAxisLabel,
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {
        ...style.axis,
        fontWeight: 'bold'
      },
      axisLabel: {
        ...style.axis,
        formatter: (value) => value.toFixed(0),
        margin: 10
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: textColor,
          width: 1
        }
      },
      tickLine: {
        show: true,
        length: 5
      },
      splitLine: style.grid.show ? {
        show: true,
        lineStyle: style.grid.lineStyle
      } : { show: false }
    },
    series: [{
      name: '频数',
      type: 'bar',
      label: {
        show: showLabel,
        position: 'top',
        fontSize: 10,
        fontFamily,
        formatter: '{c}'
      },
      data: validBins.map(bin => ({
        value: bin.count,
        total: total,
        itemStyle: {
          opacity: opacity || 0.8
        }
      })),
      barWidth: '85%',
      itemStyle: {
        color: getColorScheme(colorScheme)[0],
        opacity: opacity || 0.8,
        borderColor: getColorScheme(colorScheme)[1],
        borderWidth: 0.5
      },
      emphasis: {
        itemStyle: {
          opacity: 1,
          borderWidth: 1
        }
      }
    }],
    color: getColorScheme(colorScheme)
  }

  // 应用通用样式配置
  applyCommonStyle(option, config)

  return option
}
