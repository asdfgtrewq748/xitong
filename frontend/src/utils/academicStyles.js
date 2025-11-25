/**
 * 学术图表样式配置
 * 符合 Nature/Science 等顶级期刊要求
 */

/**
 * 学术字体配置
 */
export const AcademicFonts = {
  // 推荐的学术字体
  serif: {
    primary: 'Times New Roman, Times, serif',
    fallback: 'Georgia, serif',
    chinese: 'SimSun, STSong, serif' // 宋体
  },
  sansSerif: {
    primary: 'Arial, Helvetica, sans-serif',
    fallback: 'Verdana, sans-serif',
    chinese: 'SimHei, STHeiti, sans-serif' // 黑体
  },
  monospace: {
    primary: 'Courier New, Courier, monospace',
    fallback: 'Monaco, monospace'
  }
}

/**
 * 字体大小标准（pt）
 */
export const FontSizes = {
  // SCI 期刊标准
  title: 24,        // 标题
  subtitle: 20,     // 副标题
  axisLabel: 18,    // 坐标轴标签
  axisTitle: 20,    // 坐标轴标题
  legend: 16,       // 图例
  annotation: 14,   // 注释
  caption: 12,      // 说明文字
  
  // 演示用（稍大）
  presentation: {
    title: 32,
    subtitle: 28,
    axisLabel: 24,
    axisTitle: 28,
    legend: 22,
    annotation: 20
  }
}

/**
 * 色盲友好配色方案
 * 参考：ColorBrewer, Wong 2011
 */
export const ColorBlindFriendlyPalettes = {
  // Wong (2011) 8色方案 - 最常用
  wong: [
    '#E69F00', // 橙色
    '#56B4E9', // 天蓝
    '#009E73', // 蓝绿
    '#F0E442', // 黄色
    '#0072B2', // 蓝色
    '#D55E00', // 朱红
    '#CC79A7', // 紫红
    '#999999'  // 灰色
  ],
  
  // Tol (2012) 亮色方案
  tolBright: [
    '#4477AA', // 蓝色
    '#EE6677', // 红色
    '#228833', // 绿色
    '#CCBB44', // 黄色
    '#66CCEE', // 青色
    '#AA3377', // 紫色
    '#BBBBBB'  // 灰色
  ],
  
  // Tol (2012) 柔和方案
  tolMuted: [
    '#332288', // 靛蓝
    '#88CCEE', // 青色
    '#44AA99', // 蓝绿
    '#117733', // 绿色
    '#999933', // 橄榄绿
    '#DDCC77', // 沙色
    '#CC6677', // 玫瑰
    '#882255', // 紫色
    '#AA4499'  // 紫红
  ],
  
  // 灰度方案（打印友好）
  grayscale: [
    '#000000', // 黑色
    '#404040', // 深灰
    '#808080', // 中灰
    '#BFBFBF', // 浅灰
    '#E0E0E0'  // 极浅灰
  ]
}

/**
 * 线条样式标准
 */
export const LineStyles = {
  // 线条粗细（px）
  width: {
    thin: 0.5,      // 最细（网格线）
    normal: 1,      // 普通（坐标轴）
    medium: 1.5,    // 中等（数据线）
    thick: 2,       // 粗（强调线）
    extraThick: 3   // 特粗
  },
  
  // 线型
  types: {
    solid: 'solid',
    dashed: [5, 5],
    dotted: [2, 2],
    dashDot: [10, 5, 2, 5],
    longDash: [10, 5]
  }
}

/**
 * 符号样式标准
 */
export const SymbolStyles = {
  // 符号大小
  sizes: {
    small: 4,
    normal: 6,
    medium: 8,
    large: 10,
    extraLarge: 12
  },
  
  // 符号类型
  types: [
    'circle',
    'rect',
    'triangle',
    'diamond',
    'pin',
    'arrow'
  ]
}

/**
 * 网格样式
 */
export const GridStyles = {
  show: true,
  lineStyle: {
    color: '#E0E0E0',
    width: 0.5,
    type: 'solid'
  }
}

/**
 * 创建学术风格配置
 * @param {string} style - 风格类型: 'journal' | 'presentation' | 'thesis'
 * @param {Object} options - 自定义选项
 * @returns {Object} ECharts 样式配置
 */
export function createAcademicStyle(style = 'journal', options = {}) {
  const isPresentation = style === 'presentation'
  const fontSizes = isPresentation ? FontSizes.presentation : FontSizes
  
  return {
    // 全局文本样式
    textStyle: {
      fontFamily: options.fontFamily || AcademicFonts.sansSerif.primary,
      fontSize: fontSizes.axisLabel,
      color: '#000000'
    },
    
    // 标题
    title: {
      textStyle: {
        fontFamily: options.titleFont || AcademicFonts.sansSerif.primary,
        fontSize: fontSizes.title,
        fontWeight: 'bold',
        color: '#000000'
      },
      subtextStyle: {
        fontSize: fontSizes.subtitle,
        color: '#333333'
      },
      left: 'center',
      top: 10
    },
    
    // 图例
    legend: {
      textStyle: {
        fontSize: fontSizes.legend,
        fontFamily: options.fontFamily || AcademicFonts.sansSerif.primary
      },
      itemWidth: 25,
      itemHeight: 14,
      icon: 'rect'
    },
    
    // 网格
    grid: {
      left: '12%',
      right: '8%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    
    // X轴
    xAxis: {
      nameTextStyle: {
        fontSize: fontSizes.axisTitle,
        fontWeight: 'bold',
        padding: [10, 0, 0, 0]
      },
      axisLabel: {
        fontSize: fontSizes.axisLabel,
        color: '#000000'
      },
      axisLine: {
        lineStyle: {
          color: '#000000',
          width: LineStyles.width.normal
        }
      },
      axisTick: {
        lineStyle: {
          color: '#000000',
          width: LineStyles.width.normal
        },
        length: 5
      },
      splitLine: {
        show: options.showGridLines !== false,
        lineStyle: {
          color: '#E0E0E0',
          width: LineStyles.width.thin,
          type: 'solid'
        }
      }
    },
    
    // Y轴
    yAxis: {
      nameTextStyle: {
        fontSize: fontSizes.axisTitle,
        fontWeight: 'bold',
        padding: [0, 10, 0, 0]
      },
      axisLabel: {
        fontSize: fontSizes.axisLabel,
        color: '#000000'
      },
      axisLine: {
        lineStyle: {
          color: '#000000',
          width: LineStyles.width.normal
        }
      },
      axisTick: {
        lineStyle: {
          color: '#000000',
          width: LineStyles.width.normal
        },
        length: 5
      },
      splitLine: {
        show: options.showGridLines !== false,
        lineStyle: {
          color: '#E0E0E0',
          width: LineStyles.width.thin,
          type: 'solid'
        }
      }
    },
    
    // 系列默认样式
    series: {
      lineStyle: {
        width: LineStyles.width.medium
      },
      symbolSize: SymbolStyles.sizes.normal,
      itemStyle: {
        borderWidth: 0
      }
    },
    
    // 工具提示
    tooltip: {
      textStyle: {
        fontSize: FontSizes.annotation
      },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#333',
      borderWidth: 1
    },
    
    // 背景色
    backgroundColor: options.backgroundColor || '#FFFFFF',
    
    // 动画（期刊模式关闭，演示模式开启）
    animation: style === 'presentation'
  }
}

/**
 * 应用色盲友好配色
 * @param {Array} series - 系列数组
 * @param {string} palette - 调色板名称
 * @returns {Array} 应用配色后的系列
 */
export function applyColorBlindPalette(series, palette = 'wong') {
  const colors = ColorBlindFriendlyPalettes[palette] || ColorBlindFriendlyPalettes.wong
  
  return series.map((s, index) => ({
    ...s,
    itemStyle: {
      ...s.itemStyle,
      color: colors[index % colors.length]
    },
    lineStyle: {
      ...s.lineStyle,
      color: colors[index % colors.length]
    }
  }))
}

/**
 * 优化坐标轴样式
 * @param {Object} axis - 坐标轴配置
 * @param {Object} options - 优化选项
 * @returns {Object} 优化后的坐标轴配置
 */
export function optimizeAxisStyle(axis, options = {}) {
  return {
    ...axis,
    nameTextStyle: {
      ...axis.nameTextStyle,
      fontSize: options.titleSize || FontSizes.axisTitle,
      fontWeight: 'bold',
      color: '#000000'
    },
    axisLabel: {
      ...axis.axisLabel,
      fontSize: options.labelSize || FontSizes.axisLabel,
      color: '#000000',
      fontFamily: options.fontFamily || AcademicFonts.sansSerif.primary
    },
    axisLine: {
      show: true,
      lineStyle: {
        color: '#000000',
        width: options.lineWidth || LineStyles.width.normal
      }
    },
    axisTick: {
      show: true,
      lineStyle: {
        color: '#000000',
        width: options.lineWidth || LineStyles.width.normal
      }
    },
    splitLine: {
      show: options.showGrid !== false,
      lineStyle: {
        color: '#E0E0E0',
        width: LineStyles.width.thin,
        type: 'solid'
      }
    }
  }
}

/**
 * 验证图表符合期刊标准
 * @param {Object} option - ECharts 配置
 * @returns {Object} 验证结果和建议
 */
export function validateJournalStandards(option) {
  const warnings = []
  const errors = []
  
  // 检查字体大小
  if (option.title?.textStyle?.fontSize < 18) {
    warnings.push('标题字体可能过小（建议 ≥18pt）')
  }
  
  // 检查线条粗细
  if (option.series) {
    option.series.forEach((s, i) => {
      if (s.type === 'line' && s.lineStyle?.width < 0.5) {
        warnings.push(`系列${i + 1}线条可能过细（建议 ≥0.5pt）`)
      }
    })
  }
  
  // 检查配色（是否色盲友好）
  if (option.color && option.color.length > 0) {
    const hasColorBlindIssues = !option.color.every(c => 
      Object.values(ColorBlindFriendlyPalettes).some(palette => palette.includes(c))
    )
    if (hasColorBlindIssues) {
      warnings.push('配色方案可能不够色盲友好，建议使用推荐调色板')
    }
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings,
    suggestions: [
      '使用 Arial 或 Times New Roman 字体',
      '确保所有文字 ≥12pt',
      '线条粗细 ≥0.5pt',
      '使用色盲友好配色',
      '背景使用白色或透明'
    ]
  }
}

/**
 * 快速应用学术样式
 * @param {Object} option - 原始 ECharts 配置
 * @param {string} style - 样式类型
 * @param {Object} customOptions - 自定义选项
 * @returns {Object} 应用样式后的配置
 */
export function applyAcademicStyle(option, style = 'journal', customOptions = {}) {
  const academicStyle = createAcademicStyle(style, customOptions)
  
  // 深度合并配置
  const mergedOption = {
    ...option,
    textStyle: { ...option.textStyle, ...academicStyle.textStyle },
    title: { ...option.title, ...academicStyle.title },
    legend: { ...option.legend, ...academicStyle.legend },
    grid: { ...option.grid, ...academicStyle.grid },
    tooltip: { ...option.tooltip, ...academicStyle.tooltip },
    backgroundColor: academicStyle.backgroundColor,
    animation: academicStyle.animation
  }
  
  // 优化坐标轴
  if (option.xAxis) {
    mergedOption.xAxis = Array.isArray(option.xAxis)
      ? option.xAxis.map(axis => ({ ...axis, ...academicStyle.xAxis }))
      : { ...option.xAxis, ...academicStyle.xAxis }
  }
  
  if (option.yAxis) {
    mergedOption.yAxis = Array.isArray(option.yAxis)
      ? option.yAxis.map(axis => ({ ...axis, ...academicStyle.yAxis }))
      : { ...option.yAxis, ...academicStyle.yAxis }
  }
  
  // 应用色盲友好配色
  if (customOptions.colorPalette && option.series) {
    mergedOption.series = applyColorBlindPalette(option.series, customOptions.colorPalette)
  }
  
  return mergedOption
}

export default {
  AcademicFonts,
  FontSizes,
  ColorBlindFriendlyPalettes,
  LineStyles,
  SymbolStyles,
  GridStyles,
  createAcademicStyle,
  applyColorBlindPalette,
  optimizeAxisStyle,
  validateJournalStandards,
  applyAcademicStyle
}
