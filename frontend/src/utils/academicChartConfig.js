/**
 * 科研绘图配置工具
 * 提供期刊标准的图表配置和导出设置
 */

import { getJournalStyle, getColorScheme, FontSizes } from './chartWrapper'

/**
 * 期刊配置标准
 */
export const JournalStandards = {
  // Nature 期刊标准
  nature: {
    name: 'Nature',
    description: 'Nature系列期刊标准',
    width: {
      single: 89,  // mm (单栏)
      double: 183, // mm (双栏)
      full: 247    // mm (全宽)
    },
    height: {
      half: 120,   // mm (半高)
      full: 180    // mm (全高)
    },
    dpi: 300,
    fonts: {
      sans: 'Arial',
      serif: 'Times New Roman'
    },
    maxFigureSize: '30MB',
    formats: ['TIFF', 'JPEG', 'PNG'],
    requirements: {
      lineWeight: '最小0.5pt',
      fontSize: '最小6pt',
      resolution: '300 DPI',
      colorMode: 'RGB或CMYK'
    }
  },

  // Science 期刊标准
  science: {
    name: 'Science',
    description: 'Science系列期刊标准',
    width: {
      single: 90,   // mm
      double: 180,
      full: 240
    },
    height: {
      half: 120,
      full: 170
    },
    dpi: 300,
    fonts: {
      sans: 'Helvetica',
      serif: 'Times New Roman'
    },
    formats: ['TIFF', 'EPS', 'PDF'],
    requirements: {
      lineWeight: '最小1pt',
      fontSize: '6-12pt',
      resolution: '300 DPI',
      colorMode: 'RGB'
    }
  },

  // IEEE 期刊标准
  ieee: {
    name: 'IEEE',
    description: 'IEEE系列期刊标准',
    width: {
      single: 86,   // mm (3.5英寸)
      double: 178,  // mm (7英寸)
      full: 247    // mm (9.75英寸)
    },
    height: {
      half: 120,
      full: 160
    },
    dpi: 600,
    fonts: {
      sans: 'Helvetica',
      serif: 'Times New Roman'
    },
    formats: ['EPS', 'PDF', 'TIFF'],
    requirements: {
      lineWeight: '最小1pt',
      fontSize: '7-12pt',
      resolution: '600 DPI',
      colorMode: 'Grayscale preferred'
    }
  },

  // PLOS 期刊标准
  plos: {
    name: 'PLOS',
    description: 'PLOS系列期刊标准',
    width: {
      single: 170,  // mm
      double: 170,
      full: 240
    },
    height: {
      half: 130,
      full: 200
    },
    dpi: 300,
    fonts: {
      sans: 'Arial',
      serif: 'Times New Roman'
    },
    formats: ['TIFF', 'EPS', 'PNG', 'JPEG'],
    requirements: {
      lineWeight: '最小1pt',
      fontSize: '6-12pt',
      resolution: '300 DPI',
      colorMode: 'RGB preferred'
    }
  }
}

/**
 * 图表类型配置
 */
export const ChartTypeConfig = {
  scatter: {
    defaultPoint: 6,
    minPoint: 2,
    maxPoint: 10,
    lineWeight: 1,
    alpha: 0.8,
    errorBarWidth: 0.5,
    regressionLine: 'dashed',
    regressionWidth: 1.5
  },
  line: {
    lineWidth: 1.5,
    minLineWidth: 0.5,
    maxLineWidth: 3,
    symbolSize: 4,
    showSymbols: true,
    smooth: false,
    alpha: 1
  },
  bar: {
    barWidth: '80%',
    minBarWidth: '60%',
    maxBarWidth: '90%',
    lineWidth: 0.8,
    alpha: 0.9,
    gap: '10%'
  },
  heatmap: {
    cellSize: 20,
    minCellSize: 10,
    maxCellSize: 30,
    showGrid: true,
    gridWidth: 0.5,
    colorbarWidth: 10
  },
  violin: {
    width: 0.8,
    lineWidth: 1,
    showBox: true,
    showMean: true,
    showPoints: false,
    pointSize: 2
  }
}

/**
 * 创建期刊标准图表配置
 */
export function createJournalChartConfig(chartType, journalType, options = {}) {
  const journal = JournalStandards[journalType] || JournalStandards.nature
  const chartConfig = ChartTypeConfig[chartType] || ChartTypeConfig.scatter
  const style = getJournalStyle(journalType)

  return {
    // 基本配置
    journal: journalType,
    chartType,

    // 尺寸配置
    width: options.width || journal.width.single,
    height: options.height || journal.height.half,
    dpi: journal.dpi,

    // 字体配置
    font: {
      family: style.title.fontFamily,
      sizes: {
        title: style.title.fontSize,
        axis: style.axis.fontSize,
        legend: style.legend.fontSize,
        annotation: FontSizes.caption
      }
    },

    // 图表样式
    style: {
      lineWidth: chartConfig.lineWidth,
      symbolSize: chartConfig.defaultPoint || chartConfig.symbolSize,
      alpha: chartConfig.alpha,
      colors: getColorScheme(options.colorScheme || 'colorblind_friendly')
    },

    // 布局配置
    layout: {
      titleTop: '5%',
      legendBottom: '5%',
      axisMargin: 30,
      gridMargin: '15%'
    },

    // 导出配置
    export: {
      format: journal.formats[0], // 默认第一个格式
      quality: 'high',
      background: '#ffffff'
    },

    // 期刊特殊要求
    requirements: journal.requirements,

    // 用户自定义选项
    ...options
  }
}

/**
 * 获取图表最佳尺寸
 */
export function getOptimalChartSize(journalType, layoutType = 'single') {
  const journal = JournalStandards[journalType] || JournalStandards.nature

  switch (layoutType) {
    case 'single':
      return { width: journal.width.single, height: journal.height.half }
    case 'double':
      return { width: journal.width.double, height: journal.height.half }
    case 'full':
      return { width: journal.width.full, height: journal.height.full }
    case 'wide':
      return { width: journal.width.full, height: journal.height.half }
    default:
      return { width: journal.width.single, height: journal.height.half }
  }
}

/**
 * 生成图表文件名（学术规范）
 */
export function generateAcademicFilename(figureInfo) {
  const {
    journal,
    figureNumber,
    panelLetter,
    description,
    format = 'png',
    version = 'v1'
  } = figureInfo

  const timestamp = new Date().toISOString().slice(0, 10)
  const safeDescription = description ? `_${description.replace(/[^a-zA-Z0-9]/g, '_')}` : ''
  const panel = panelLetter ? panelLetter.toUpperCase() : ''

  let filename = ''

  if (journal && figureNumber) {
    // 期刊专用格式
    filename = `${journal}_Fig${figureNumber}${panel}${safeDescription}_${timestamp}_${version}.${format}`
  } else {
    // 通用学术格式
    filename = `Figure${figureNumber || ''}${panel}${safeDescription}_${timestamp}_${version}.${format}`
  }

  return filename
}

/**
 * 验证图表是否符合期刊要求
 */
export function validateJournalFigure(chartConfig, journalType) {
  const journal = JournalStandards[journalType]
  const errors = []
  const warnings = []

  if (!journal) {
    errors.push('未知的期刊类型')
    return { valid: false, errors, warnings }
  }

  // 检查分辨率
  if (chartConfig.dpi < journal.dpi) {
    errors.push(`分辨率不足：当前${chartConfig.dpi} DPI，要求${journal.dpi} DPI`)
  }

  // 检查字体大小
  if (chartConfig.font?.sizes?.axis < 6) {
    errors.push('字体大小过小：坐标轴字体应不小于6pt')
  } else if (chartConfig.font?.sizes?.axis < 7) {
    warnings.push('字体大小较小：建议坐标轴字体不小于7pt')
  }

  // 检查线宽
  const minLineWeight = parseFloat(journal.requirements.lineWeight.replace(/[^0-9.]/g, ''))
  if (chartConfig.style?.lineWidth < minLineWeight) {
    errors.push(`线条过细：当前${chartConfig.style.lineWidth}pt，要求${journal.requirements.lineWeight}`)
  }

  // 检查文件格式
  const supportedFormats = journal.formats.map(f => f.toLowerCase())
  const currentFormat = chartConfig.export?.format?.toLowerCase()
  if (currentFormat && !supportedFormats.includes(currentFormat)) {
    errors.push(`不支持的文件格式：${chartConfig.export.format}，支持格式：${supportedFormats.join(', ')}`)
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    requirements: journal.requirements
  }
}

/**
 * 获取图表优化建议
 */
export function getOptimizationSuggestions(chartConfig, journalType) {
  const suggestions = []
  const journal = JournalStandards[journalType]

  if (!journal) {
    return ['请选择有效的期刊类型']
  }

  // 色彩建议
  if (chartConfig.style?.colors?.length > 8) {
    suggestions.push('颜色过多：建议使用不超过8种颜色以提高可读性')
  }

  // 布局建议
  const aspectRatio = (chartConfig.height || 100) / (chartConfig.width || 100)
  if (aspectRatio > 1.5) {
    suggestions.push('图表过高：建议调整宽高比例以适应期刊版面')
  } else if (aspectRatio < 0.6) {
    suggestions.push('图表过宽：建议调整宽高比例以适应期刊版面')
  }

  // 标题建议
  if (!chartConfig.title || chartConfig.title.length < 10) {
    suggestions.push('标题过短：建议提供描述性的图表标题')
  } else if (chartConfig.title && chartConfig.title.length > 200) {
    suggestions.push('标题过长：建议精简标题，详情可在正文或图注中说明')
  }

  // 图例建议
  if (chartConfig.showLegend && chartConfig.legendItems?.length > 10) {
    suggestions.push('图例项过多：考虑简化图表或分多个子图展示')
  }

  return suggestions
}

/**
 * 创建图表元数据
 */
export function createFigureMetadata(chartConfig, dataInfo) {
  return {
    title: chartConfig.title,
    subtitle: chartConfig.subtitle,
    description: chartConfig.description,

    // 技术信息
    generated: new Date().toISOString(),
    software: 'Scientific Visualization System',
    version: '1.0.0',

    // 图表配置
    chartType: chartConfig.chartType,
    journal: chartConfig.journal,
    dimensions: {
      width: chartConfig.width,
      height: chartConfig.height,
      dpi: chartConfig.dpi
    },
    style: {
      colorScheme: chartConfig.style?.colors,
      fontFamily: chartConfig.font?.family,
      fontSize: chartConfig.font?.sizes
    },

    // 数据信息
    data: {
      source: dataInfo.source,
      size: dataInfo.size,
      variables: dataInfo.variables,
      preprocessing: dataInfo.preprocessing
    },

    // 统计信息
    statistics: dataInfo.statistics,

    // 版权信息
    copyright: chartConfig.copyright || {
      license: 'CC BY 4.0',
      author: chartConfig.author,
      institution: chartConfig.institution
    }
  }
}