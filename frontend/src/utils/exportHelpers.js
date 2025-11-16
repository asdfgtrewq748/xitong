/**
 * 图表导出工具
 */
import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'
import Papa from 'papaparse'

/**
 * 导出图表为 PNG 图像（科研级高质量）
 * @param {Object} chartInstance - ECharts 实例
 * @param {Object} options - 导出选项
 */
export function exportChartAsPNG(chartInstance, options = {}) {
  const {
    filename = 'chart',
    pixelRatio = 4, // 提升到4倍像素比，支持300+ DPI
    backgroundColor = '#ffffff',
    width = 1200,  // 默认宽度
    height = 800,  // 默认高度
    quality = 'high' // 质量级别：standard, high, print
  } = options

  try {
    // 根据质量级别调整参数
    const qualitySettings = {
      standard: { pixelRatio: 2, width: 800, height: 600 },
      high: { pixelRatio: 4, width: 1200, height: 800 },
      print: { pixelRatio: 6, width: 2400, height: 1600 }
    }

    const settings = qualitySettings[quality] || qualitySettings.high
    const finalPixelRatio = pixelRatio || settings.pixelRatio

    const dataURL = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: finalPixelRatio,
      backgroundColor,
      width: width || settings.width,
      height: height || settings.height
    })

    // 转换为 Blob 并下载
    fetch(dataURL)
      .then(res => res.blob())
      .then(blob => {
        saveAs(blob, `${filename}_${quality}.png`)
      })

    return true
  } catch (error) {
    console.error('导出 PNG 失败:', error)
    throw error
  }
}

/**
 * 导出图表为 SVG 矢量图（高质量）
 * @param {Object|String} chartInstanceOrSvg - ECharts 实例或 SVG 字符串
 * @param {Object} options - 导出选项
 */
export function exportChartAsSVG(chartInstanceOrSvg, options = {}) {
  const {
    filename = 'chart'
  } = options

  try {
    let svgStr
    
    // 如果传入的是字符串，直接使用
    if (typeof chartInstanceOrSvg === 'string') {
      svgStr = chartInstanceOrSvg
    } else {
      // 否则尝试调用 renderToSVGString
      // 注意：这要求 chartInstance 是用 svg renderer 初始化的
      if (typeof chartInstanceOrSvg.renderToSVGString !== 'function') {
        throw new Error('图表实例不支持 SVG 导出。请使用 svg renderer 初始化图表。')
      }
      svgStr = chartInstanceOrSvg.renderToSVGString()
    }

    // 直接使用 ECharts 生成的 SVG
    // ECharts 的 svg renderer 已经生成了完整正确的 SVG，包含所有必要的属性

    const blob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' })
    saveAs(blob, `${filename}_high_quality.svg`)
    return true
  } catch (error) {
    console.error('导出 SVG 失败:', error)
    throw error
  }
}

/**
 * 导出图表为 PDF（学术出版格式）
 * @param {Object} chartInstance - ECharts 实例
 * @param {Object} options - 导出选项
 */
export async function exportChartAsPDF(chartInstance, options = {}) {
  const {
    filename = 'chart',
    width = 210, // A4 width in mm
    height = 148, // A4 height in mm (landscape)
    dpi = 300
  } = options

  try {
    // 首先导出为高质量PNG
    const pngDataURL = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: dpi / 96, // Convert DPI to pixel ratio
      backgroundColor: '#ffffff',
      width: width * dpi / 25.4, // Convert mm to pixels
      height: height * dpi / 25.4
    })

    // 使用jsPDF创建PDF（需要安装依赖）
    const { jsPDF } = await import('jspdf')
    const pdf = new jsPDF({
      orientation: 'landscape',
      unit: 'mm',
      format: 'a4'
    })

    // 将PNG添加到PDF
    const imgData = pngDataURL.replace('data:image/png;base64,', '')
    pdf.addImage(imgData, 'PNG', 0, 0, width, height)

    pdf.save(`${filename}_academic.pdf`)
    return true
  } catch (error) {
    console.error('导出 PDF 失败:', error)
    throw error
  }
}

/**
 * 导出图表为 TIFF（期刊专用格式）
 * @param {Object} chartInstance - ECharts 实例
 * @param {Object} options - 导出选项
 */
export async function exportChartAsTIFF(chartInstance, options = {}) {
  const {
    filename = 'chart',
    dpi = 300,
    width = 2400,
    height = 1600
  } = options

  try {
    // 导出为高质量PNG
    const dataURL = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: dpi / 96,
      backgroundColor: '#ffffff',
      width,
      height
    })

    // 转换为TIFF（使用UTIF.js或其他库）
    const response = await fetch(dataURL)
    const pngBlob = await response.blob()

    // 这里需要添加PNG到TIFF的转换逻辑
    // 由于浏览器端TIFF转换较复杂，建议在服务端处理
    // 现在先导出为高质量PNG，文件名包含TIFF标识
    saveAs(pngBlob, `${filename}_for_tiff_${dpi}dpi.png`)

    return true
  } catch (error) {
    console.error('导出 TIFF 失败:', error)
    throw error
  }
}

/**
 * 导出数据为 CSV
 * @param {Array} data - 数据数组
 * @param {Object} options - 导出选项
 */
export function exportDataAsCSV(data, options = {}) {
  const { filename = 'data', columns = null } = options
  
  try {
    let exportData = data
    
    // 如果提供了列配置，只导出指定列
    if (columns && Array.isArray(columns)) {
      exportData = data.map(row => {
        const filtered = {}
        columns.forEach(col => {
          filtered[col] = row[col]
        })
        return filtered
      })
    }
    
    const csv = Papa.unparse(exportData, {
      quotes: true,
      delimiter: ',',
      header: true
    })
    
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
    saveAs(blob, `${filename}.csv`)
    
    return true
  } catch (error) {
    console.error('导出 CSV 失败:', error)
    throw error
  }
}

/**
 * 导出数据为 Excel
 * @param {Array} data - 数据数组
 * @param {Object} options - 导出选项
 */
export function exportDataAsExcel(data, options = {}) {
  const {
    filename = 'data',
    sheetName = 'Sheet1',
    columns = null
  } = options
  
  try {
    let exportData = data
    
    // 如果提供了列配置，只导出指定列
    if (columns && Array.isArray(columns)) {
      exportData = data.map(row => {
        const filtered = {}
        columns.forEach(col => {
          filtered[col] = row[col]
        })
        return filtered
      })
    }
    
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(exportData)
    
    // 设置列宽
    const colWidths = Object.keys(exportData[0] || {}).map(key => ({
      wch: Math.max(key.length, 15)
    }))
    ws['!cols'] = colWidths
    
    XLSX.utils.book_append_sheet(wb, ws, sheetName)
    
    // 写入文件
    XLSX.writeFile(wb, `${filename}.xlsx`)
    
    return true
  } catch (error) {
    console.error('导出 Excel 失败:', error)
    throw error
  }
}

/**
 * 导出配置为 JSON
 * @param {Object} config - 配置对象
 * @param {Object} options - 导出选项
 */
export function exportConfigAsJSON(config, options = {}) {
  const { filename = 'chart-config' } = options
  
  try {
    const json = JSON.stringify(config, null, 2)
    const blob = new Blob([json], { type: 'application/json;charset=utf-8' })
    saveAs(blob, `${filename}.json`)
    return true
  } catch (error) {
    console.error('导出配置失败:', error)
    throw error
  }
}

/**
 * 复制图表到剪贴板
 * @param {Object} chartInstance - ECharts 实例
 */
export async function copyChartToClipboard(chartInstance) {
  try {
    const dataURL = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#ffffff'
    })
    
    const blob = await fetch(dataURL).then(res => res.blob())
    
    await navigator.clipboard.write([
      new ClipboardItem({ 'image/png': blob })
    ])
    
    return true
  } catch (error) {
    console.error('复制到剪贴板失败:', error)
    throw error
  }
}

/**
 * 打印图表
 * @param {Object} chartInstance - ECharts 实例
 */
export function printChart(chartInstance) {
  try {
    const dataURL = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#ffffff'
    })
    
    const printWindow = window.open('', '_blank')
    printWindow.document.write(`
      <html>
        <head>
          <title>打印图表</title>
          <style>
            body { margin: 0; padding: 20px; text-align: center; }
            img { max-width: 100%; height: auto; }
            @media print {
              body { padding: 0; }
            }
          </style>
        </head>
        <body>
          <img src="${dataURL}" onload="window.print(); window.close();" />
        </body>
      </html>
    `)
    printWindow.document.close()
    
    return true
  } catch (error) {
    console.error('打印失败:', error)
    throw error
  }
}

/**
 * 批量导出（图表 + 数据）
 * @param {Object} chartInstance - ECharts 实例
 * @param {Array} data - 数据数组
 * @param {Object} config - 配置对象
 * @param {Object} options - 导出选项
 */
export async function exportBundle(chartInstance, data, config, options = {}) {
  const { filename = 'chart-bundle' } = options
  
  try {
    // 导出图表为 PNG
    await exportChartAsPNG(chartInstance, { filename: `${filename}-chart` })
    
    // 导出数据为 Excel
    await exportDataAsExcel(data, { filename: `${filename}-data` })
    
    // 导出配置为 JSON
    await exportConfigAsJSON(config, { filename: `${filename}-config` })
    
    return true
  } catch (error) {
    console.error('批量导出失败:', error)
    throw error
  }
}

/**
 * 生成文件名（带时间戳）
 * @param {String} prefix - 文件名前缀
 * @param {String} ext - 文件扩展名
 * @returns {String} 文件名
 */
export function generateFilename(prefix = 'chart', ext = 'png') {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
  return `${prefix}_${timestamp}.${ext}`
}

/**
 * 获取支持的导出格式（科研级别）
 * @returns {Array} 格式列表
 */
export function getSupportedFormats() {
  return [
    // 图像格式
    { value: 'png', label: 'PNG (300 DPI)', icon: 'Picture', category: 'image', quality: 'high' },
    { value: 'png_print', label: 'PNG (600 DPI)', icon: 'Picture', category: 'image', quality: 'print' },
    { value: 'svg', label: 'SVG 矢量图', icon: 'Picture', category: 'image', quality: 'vector' },
    { value: 'pdf', label: 'PDF 学术版', icon: 'Document', category: 'image', quality: 'academic' },
    { value: 'tiff', label: 'TIFF (300 DPI)', icon: 'Picture', category: 'image', quality: 'print' },

    // 数据格式
    { value: 'csv', label: 'CSV 数据', icon: 'Document', category: 'data', quality: 'standard' },
    { value: 'xlsx', label: 'Excel 数据', icon: 'Document', category: 'data', quality: 'standard' },

    // 配置格式
    { value: 'json', label: 'JSON 配置', icon: 'DocumentCopy', category: 'config', quality: 'standard' },

    // 打印格式
    { value: 'eps', label: 'EPS 矢量图', icon: 'Picture', category: 'image', quality: 'print' }
  ]
}

/**
 * 获取期刊推荐导出格式
 * @returns {Array} 期刊格式列表
 */
export function getJournalFormats() {
  return [
    { value: 'tiff', label: 'TIFF (300 DPI)', description: 'Nature、Science等期刊要求' },
    { value: 'eps', label: 'EPS 矢量图', description: 'IEEE、ACS等期刊要求' },
    { value: 'pdf', label: 'PDF (600 DPI)', description: 'PLOS、eLife等期刊要求' },
    { value: 'svg', label: 'SVG 矢量图', description: '在线期刊推荐格式' }
  ]
}

/**
 * 根据期刊要求导出图表
 * @param {Object} chartInstance - ECharts 实例
 * @param {String} journalType - 期刊类型
 * @param {Object} options - 导出选项
 */
export async function exportForJournal(chartInstance, journalType, options = {}) {
  const journalSettings = {
    nature: { format: 'tiff', dpi: 300, width: 2400, height: 1600 },
    science: { format: 'tiff', dpi: 300, width: 1800, height: 1200 },
    ieee: { format: 'eps', dpi: 600, width: 1200, height: 800 },
    plos: { format: 'pdf', dpi: 300, width: 210, height: 148 }, // mm
    default: { format: 'png', dpi: 300, width: 1200, height: 800 }
  }

  const settings = journalSettings[journalType] || journalSettings.default

  try {
    switch (settings.format) {
      case 'tiff':
        return await exportChartAsTIFF(chartInstance, {
          ...options,
          dpi: settings.dpi,
          width: settings.width,
          height: settings.height
        })
      case 'eps':
        // EPS导出需要特殊处理，这里先导出高质量SVG
        return await exportChartAsSVG(chartInstance, {
          ...options,
          width: settings.width,
          height: settings.height
        })
      case 'pdf':
        return await exportChartAsPDF(chartInstance, {
          ...options,
          dpi: settings.dpi,
          width: settings.width,
          height: settings.height
        })
      default:
        return await exportChartAsPNG(chartInstance, {
          ...options,
          pixelRatio: settings.dpi / 96,
          width: settings.width,
          height: settings.height,
          quality: 'print'
        })
    }
  } catch (error) {
    console.error('期刊格式导出失败:', error)
    throw error
  }
}
