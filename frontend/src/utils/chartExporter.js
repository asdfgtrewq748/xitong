/**
 * 高质量科研图表导出工具
 * 支持 PNG/SVG/PDF/EPS 格式，符合 Nature/Science 等顶级期刊要求
 */

/**
 * 期刊标准尺寸（单位：mm）
 */
export const JournalDimensions = {
  nature: {
    singleColumn: { width: 89, height: 89 },
    doubleColumn: { width: 183, height: 120 },
    fullPage: { width: 183, height: 247 }
  },
  science: {
    singleColumn: { width: 90, height: 90 },
    doubleColumn: { width: 180, height: 120 },
    fullPage: { width: 180, height: 240 }
  },
  pnas: {
    singleColumn: { width: 87, height: 87 },
    doubleColumn: { width: 178, height: 120 },
    fullPage: { width: 178, height: 234 }
  },
  custom: {
    singleColumn: { width: 89, height: 89 },
    doubleColumn: { width: 170, height: 120 },
    fullPage: { width: 170, height: 240 }
  }
}

/**
 * DPI 标准
 */
export const DPIStandards = {
  print: 300,      // 印刷标准
  highRes: 600,    // 高分辨率
  screen: 72,      // 屏幕显示
  presentation: 150 // 演示用
}

/**
 * mm转px转换（基于DPI）
 * @param {number} mm - 毫米数
 * @param {number} dpi - DPI值
 * @returns {number} 像素数
 */
function mmToPixels(mm, dpi = DPIStandards.print) {
  return Math.round((mm / 25.4) * dpi)
}

/**
 * 导出配置预设
 */
export const ExportPresets = {
  // 期刊标准
  natureSingleColumn: {
    width: mmToPixels(89, 300),
    height: mmToPixels(89, 300),
    dpi: 300,
    format: 'png',
    backgroundColor: '#ffffff'
  },
  natureDoubleColumn: {
    width: mmToPixels(183, 300),
    height: mmToPixels(120, 300),
    dpi: 300,
    format: 'png',
    backgroundColor: '#ffffff'
  },
  scienceSingleColumn: {
    width: mmToPixels(90, 300),
    height: mmToPixels(90, 300),
    dpi: 300,
    format: 'png',
    backgroundColor: '#ffffff'
  },
  scienceDoubleColumn: {
    width: mmToPixels(180, 300),
    height: mmToPixels(120, 300),
    dpi: 300,
    format: 'png',
    backgroundColor: '#ffffff'
  },
  // 通用预设
  printQuality: {
    dpi: 300,
    format: 'png',
    backgroundColor: '#ffffff'
  },
  webQuality: {
    dpi: 72,
    format: 'png',
    backgroundColor: '#ffffff'
  },
  presentation: {
    dpi: 150,
    format: 'png',
    backgroundColor: '#ffffff'
  }
}

/**
 * 图表导出器类
 */
export class ChartExporter {
  constructor(chartInstance) {
    this.chart = chartInstance
  }

  /**
   * 导出为PNG（高分辨率）
   * @param {Object} options - 导出选项
   * @returns {Promise<Blob>}
   */
  async exportPNG(options = {}) {
    const {
      width,
      height,
      dpi = DPIStandards.print,
      backgroundColor = '#ffffff',
      pixelRatio = dpi / 72 // 转换为像素比
    } = options

    if (!this.chart) {
      throw new Error('图表实例不存在')
    }

    // 临时调整图表大小（如果指定了尺寸）
    const originalSize = this.chart.getWidth && this.chart.getHeight ? 
      { width: this.chart.getWidth(), height: this.chart.getHeight() } : null

    if (width && height) {
      this.chart.resize({ width, height })
    }

    // 导出图像
    const dataURL = this.chart.getDataURL({
      type: 'png',
      pixelRatio,
      backgroundColor,
      excludeComponents: ['toolbox']
    })

    // 恢复原始尺寸
    if (originalSize) {
      this.chart.resize(originalSize)
    }

    // 转换为Blob
    const blob = await this.dataURLToBlob(dataURL)
    return blob
  }

  /**
   * 导出为SVG（矢量格式）
   * @param {Object} options - 导出选项
   * @returns {Promise<Blob>}
   */
  async exportSVG(options = {}) {
    if (!this.chart) {
      throw new Error('图表实例不存在')
    }

    try {
      // ECharts SVG导出
      const svgStr = this.chart.renderToSVGString()
      
      if (!svgStr) {
        throw new Error('SVG导出失败：图表未使用SVG渲染器')
      }

      // 添加元数据
      const enhancedSVG = this.enhanceSVG(svgStr, options)
      
      const blob = new Blob([enhancedSVG], { type: 'image/svg+xml;charset=utf-8' })
      return blob
    } catch (error) {
      console.error('SVG导出错误:', error)
      throw new Error('请确保图表使用SVG渲染器初始化')
    }
  }

  /**
   * 增强SVG（添加元数据和优化）
   * @param {string} svgStr - SVG字符串
   * @param {Object} options - 选项
   * @returns {string}
   */
  enhanceSVG(svgStr, options = {}) {
    const { title, description } = options
    
    // 添加标题和描述
    let enhanced = svgStr.replace(
      '<svg',
      `<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#"`
    )

    if (title || description) {
      const metadata = []
      if (title) metadata.push(`<title>${title}</title>`)
      if (description) metadata.push(`<desc>${description}</desc>`)
      enhanced = enhanced.replace('<svg', `<svg>\n${metadata.join('\n')}`)
    }

    return enhanced
  }

  /**
   * 导出为PDF（通过SVG转换）
   * @returns {Promise<Blob>}
   */
  async exportPDF() {
    // 注意：真正的PDF导出需要后端支持或使用jsPDF库
    // 这里提供基础实现，可以后续集成jsPDF
    throw new Error('PDF导出需要安装jsPDF库，请使用SVG格式替代')
  }

  /**
   * 导出为EPS（通过SVG转换）
   * @returns {Promise<Blob>}
   */
  async exportEPS() {
    // EPS导出通常需要后端转换
    // 建议导出SVG后使用Inkscape等工具转换
    throw new Error('EPS导出需要后端支持，请使用SVG格式替代')
  }

  /**
   * DataURL转Blob
   * @param {string} dataURL
   * @returns {Promise<Blob>}
   */
  dataURLToBlob(dataURL) {
    return new Promise((resolve) => {
      const arr = dataURL.split(',')
      const mime = arr[0].match(/:(.*?);/)[1]
      const bstr = atob(arr[1])
      let n = bstr.length
      const u8arr = new Uint8Array(n)
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n)
      }
      resolve(new Blob([u8arr], { type: mime }))
    })
  }

  /**
   * 下载文件
   * @param {Blob} blob - 文件Blob
   * @param {string} filename - 文件名
   */
  downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  /**
   * 一键导出（根据格式自动选择）
   * @param {Object} options - 导出选项
   */
  async export(options = {}) {
    const {
      format = 'png',
      filename = `chart_${Date.now()}`,
      preset = null,
      ...exportOptions
    } = options

    // 应用预设
    const finalOptions = preset ? { ...ExportPresets[preset], ...exportOptions } : exportOptions

    let blob
    let extension = format.toLowerCase()

    try {
      switch (extension) {
        case 'png':
          blob = await this.exportPNG(finalOptions)
          break
        case 'svg':
          blob = await this.exportSVG(finalOptions)
          break
        case 'pdf':
          blob = await this.exportPDF(finalOptions)
          break
        case 'eps':
          blob = await this.exportEPS(finalOptions)
          break
        default:
          throw new Error(`不支持的格式: ${format}`)
      }

      // 下载文件
      const fullFilename = `${filename}.${extension}`
      this.downloadBlob(blob, fullFilename)

      return { success: true, filename: fullFilename }
    } catch (error) {
      console.error('导出失败:', error)
      return { success: false, error: error.message }
    }
  }
}

/**
 * 批量导出多个图表
 * @param {Array} charts - 图表实例数组
 * @param {Object} options - 导出选项
 * @returns {Promise<Array>}
 */
export async function batchExportCharts(charts, options = {}) {
  const results = []
  
  for (let i = 0; i < charts.length; i++) {
    const chart = charts[i]
    const exporter = new ChartExporter(chart.instance)
    
    const filename = options.filename ? `${options.filename}_${i + 1}` : `chart_${i + 1}_${Date.now()}`
    
    const result = await exporter.export({
      ...options,
      filename
    })
    
    results.push(result)
  }
  
  return results
}

/**
 * 创建导出配置
 * @param {string} journal - 期刊类型
 * @param {string} size - 尺寸类型
 * @param {number} dpi - DPI
 * @returns {Object}
 */
export function createExportConfig(journal = 'nature', size = 'singleColumn', dpi = 300) {
  const dimensions = JournalDimensions[journal]?.[size] || JournalDimensions.nature.singleColumn
  
  return {
    width: mmToPixels(dimensions.width, dpi),
    height: mmToPixels(dimensions.height, dpi),
    dpi,
    backgroundColor: '#ffffff'
  }
}

/**
 * 快捷导出函数
 */
export function quickExport(chartInstance, format = 'png', quality = 'print') {
  const exporter = new ChartExporter(chartInstance)
  const preset = quality === 'print' ? 'printQuality' : 
                 quality === 'web' ? 'webQuality' : 
                 'presentation'
  
  return exporter.export({
    format,
    preset,
    filename: `chart_${Date.now()}`
  })
}

export default {
  ChartExporter,
  JournalDimensions,
  DPIStandards,
  ExportPresets,
  batchExportCharts,
  createExportConfig,
  quickExport
}
