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
  }
  
  /**
   * 初始化图表
   */
  init() {
    if (this.instance) {
      this.dispose()
    }
    
    this.instance = echarts.init(this.container, this.theme, {
      renderer: this.options.renderer || 'canvas',
      useDirtyRect: true, // 开启脏矩形优化
      ...this.options.initOptions
    })
    
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
        this.resize()
      })
      this.resizeObserver.observe(this.container)
    } else {
      // 降级到 window resize
      window.addEventListener('resize', this.resize.bind(this))
    }
  }
  
  /**
   * 手动调整大小
   */
  resize() {
    if (this.instance) {
      this.instance.resize()
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

  // 默认学术风格
  academic: {
    title: {
      fontSize: FontSizes.title,
      fontWeight: 'bold',
      fontFamily: getAcademicFont().family,
      color: '#000000'
    },
    axis: {
      fontSize: FontSizes.axis,
      fontFamily: getAcademicFont().family,
      color: '#000000'
    },
    legend: {
      fontSize: FontSizes.caption,
      fontFamily: getAcademicFont().family,
      color: '#000000'
    },
    grid: {
      show: true,
      lineStyle: {
        color: '#e0e0e0',
        width: 0.5,
        type: 'solid'
      }
    },
    backgroundColor: '#ffffff'
  }
}

/**
 * 获取期刊样式配置
 */
export function getJournalStyle(journal = 'academic') {
  return JournalStyles[journal] || JournalStyles.academic
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
    showLegend,
    showGrid,
    colorScheme,
    pointSize,
    opacity,
    journalStyle = 'academic',
    showRegression = false,
    showErrorBars = false
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
      series: []
    }
  }
  
  // 处理分组数据
  const series = []
  if (data.type === 'grouped') {
    if (data.data && typeof data.data === 'object') {
      Object.entries(data.data).forEach(([group, points]) => {
        if (Array.isArray(points) && points.length > 0) {
          series.push({
            name: group,
            type: 'scatter',
            data: points.map(p => [p.x, p.y]),
            symbolSize: pointSize,
            itemStyle: {
              opacity
            }
          })
        }
      })
    }
  } else {
    if (Array.isArray(data.data) && data.data.length > 0) {
      series.push({
        name: '数据点',
        type: 'scatter',
        data: data.data.map(p => [p.x, p.y]),
        symbolSize: pointSize,
        itemStyle: {
          opacity,
          color: getColorScheme(colorScheme)[0]
        }
      })
    }
  }
  
  // 学术级布局配置
  const option = {
    title: {
      text: title,
      subtext: subtitle,
      left: 'center',
      top: '5%',
      textStyle: {
        ...style.title,
        fontSize: style.title.fontSize
      },
      subtextStyle: {
        ...style.title,
        fontSize: style.axis.fontSize,
        fontWeight: 'normal'
      }
    },
    backgroundColor: bgColor,
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        let tooltip = `<strong>${params.seriesName}</strong><br/>`
        tooltip += `X: ${params.value[0].toFixed(3)}<br/>`
        tooltip += `Y: ${params.value[1].toFixed(3)}`
        if (params.value[2] !== undefined) {
          tooltip += `<br/>Value: ${params.value[2].toFixed(3)}`
        }
        return tooltip
      },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#cccccc',
      borderWidth: 1,
      textStyle: { fontSize: 11 }
    },
    legend: {
      show: showLegend,
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
      nameTextStyle: {
        ...style.axis,
        fontWeight: 'bold'
      },
      axisLabel: {
        ...style.axis,
        formatter: (value) => value.toPrecision(3),
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
        formatter: (value) => value.toPrecision(3),
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

  return option
}

/**
 * 生成折线图配置
 */
export function generateLineOption(data, config) {
  const {
    title,
    xAxisLabel,
    yAxisLabel,
    showLegend,
    showGrid,
    colorScheme,
    lineWidth,
    opacity
  } = config

  const textColor = '#333333'
  const bgColor = '#ffffff'
  
  // 防御性检查：确保数据结构有效
  if (!data || !data.data) {
    return {
      title: { text: title || '折线图', left: 'center', textStyle: { color: textColor } },
      backgroundColor: bgColor,
      xAxis: { type: 'value' },
      yAxis: { type: 'value' },
      series: []
    }
  }
  
  const series = []
  if (data.type === 'grouped') {
    if (data.data && typeof data.data === 'object') {
      Object.entries(data.data).forEach(([group, points]) => {
        if (Array.isArray(points) && points.length > 0) {
          series.push({
            name: group,
            type: 'line',
            data: points.map(p => [p.x, p.y]),
            smooth: true,
            lineStyle: { width: lineWidth },
            itemStyle: { opacity }
          })
        }
      })
    }
  } else {
    if (Array.isArray(data.data) && data.data.length > 0) {
      series.push({
        name: '数据',
        type: 'line',
        data: data.data.map(p => [p.x, p.y]),
        smooth: true,
        lineStyle: { width: lineWidth },
        itemStyle: { opacity }
      })
    }
  }
  
  return {
    title: {
      text: title,
      left: 'center',
      textStyle: { color: textColor }
    },
    backgroundColor: bgColor,
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      show: showLegend,
      bottom: 10,
      textStyle: { color: textColor }
    },
    grid: {
      show: showGrid,
      left: '10%',
      right: '10%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: xAxisLabel,
      nameTextStyle: { color: textColor },
      axisLabel: { color: textColor }
    },
    yAxis: {
      type: 'value',
      name: yAxisLabel,
      nameTextStyle: { color: textColor },
      axisLabel: { color: textColor }
    },
    series,
    color: getColorScheme(colorScheme)
  }
}

/**
 * 生成热力图配置
 */
export function generateHeatmapOption(data, config) {
  const { title, xAxisLabel, yAxisLabel, colorScheme } = config

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
      series: []
    }
  }
  
  return {
    title: {
      text: title,
      left: 'center',
      textStyle: { color: textColor }
    },
    backgroundColor: bgColor,
    tooltip: {
      position: 'top'
    },
    grid: {
      left: '10%',
      right: '15%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.xValues,
      name: xAxisLabel,
      nameTextStyle: { color: textColor },
      axisLabel: { color: textColor }
    },
    yAxis: {
      type: 'category',
      data: data.yValues,
      name: yAxisLabel,
      nameTextStyle: { color: textColor },
      axisLabel: { color: textColor }
    },
    visualMap: {
      min: Math.min(...data.data.map(d => d[2])),
      max: Math.max(...data.data.map(d => d[2])),
      calculable: true,
      orient: 'vertical',
      right: '5%',
      top: 'center',
      inRange: {
        color: getColorScheme(colorScheme)
      },
      textStyle: { color: textColor }
    },
    series: [{
      name: '热力值',
      type: 'heatmap',
      data: data.data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
}

/**
 * 生成三维曲面图配置
 */
export function generateSurfaceOption(data, config) {
  const { title, xAxisLabel, yAxisLabel, zAxisLabel, colorScheme } = config

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
      series: []
    }
  }

  return {
    title: {
      text: title,
      left: 'center',
      textStyle: { color: textColor }
    },
    backgroundColor: bgColor,
    tooltip: {},
    visualMap: {
      show: true,
      dimension: 2,
      min: Math.min(...data.z.flat().filter(v => v != null)),
      max: Math.max(...data.z.flat().filter(v => v != null)),
      inRange: {
        color: getColorScheme(colorScheme)
      },
      textStyle: { color: textColor }
    },
    xAxis3D: {
      name: xAxisLabel,
      type: 'value',
      nameTextStyle: { color: textColor },
      axisLabel: { color: textColor }
    },
    yAxis3D: {
      name: yAxisLabel,
      type: 'value',
      nameTextStyle: { color: textColor },
      axisLabel: { color: textColor }
    },
    zAxis3D: {
      name: zAxisLabel,
      type: 'value',
      nameTextStyle: { color: textColor },
      axisLabel: { color: textColor }
    },
    grid3D: {
      viewControl: {
        projection: 'perspective'
      },
      light: {
        main: {
          shadow: true
        },
        ambient: {
          intensity: 0.4
        }
      }
    },
    series: [{
      type: 'surface',
      data: data.z.map((row, i) =>
        row.map((z, j) => [data.x[j], data.y[i], z])
      ).flat(),
      shading: 'color'
    }]
  }
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
    journalStyle = 'academic'
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
      series: []
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
      series: []
    }
  }

  return {
    title: {
      text: title,
      subtext: subtitle,
      left: 'center',
      top: '5%',
      textStyle: {
        ...style.title,
        fontSize: style.title.fontSize
      },
      subtextStyle: {
        ...style.title,
        fontSize: style.axis.fontSize,
        fontWeight: 'normal'
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
    journalStyle = 'academic'
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
      series: []
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
      series: []
    }
  }

  // 准备箱线图数据
  const boxPlotData = validData.map(item => [item.min, item.q1, item.median, item.q3, item.max])
  const categories = validData.map(item => item.group || item.name || '数据组')

  return {
    title: {
      text: title,
      subtext: subtitle,
      left: 'center',
      top: '5%',
      textStyle: {
        ...style.title,
        fontSize: style.title.fontSize
      },
      subtextStyle: {
        ...style.title,
        fontSize: style.axis.fontSize,
        fontWeight: 'normal'
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
      show: validData.length > 1,
      bottom: '5%',
      left: 'center',
      textStyle: style.legend,
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
    journalStyle = 'academic'
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
      series: []
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
      series: []
    }
  }

  const total = data.total || validBins.reduce((sum, bin) => sum + bin.count, 0)

  return {
    title: {
      text: title,
      subtext: subtitle,
      left: 'center',
      top: '5%',
      textStyle: {
        ...style.title,
        fontSize: style.title.fontSize
      },
      subtextStyle: {
        ...style.title,
        fontSize: style.axis.fontSize,
        fontWeight: 'normal'
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
}
