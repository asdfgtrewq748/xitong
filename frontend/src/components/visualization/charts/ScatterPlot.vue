<template>
  <div class="chart-container" :style="{ height: height + 'px' }" ref="chartRef"></div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import { ChartWrapper } from '../ChartWrapper'
import { generateScatterOption } from '../../../utils/chartWrapper'

const props = defineProps({ 
  data: { type: Object, required: true }, 
  config: { type: Object, required: true },
  height: { type: Number, default: 420 }
})
const chartRef = ref(null)
let wrapper = null

function updateChart() {
  if (!wrapper || !props.data || !props.config) return
  try {
    const option = generateScatterOption(props.data, props.config)
    wrapper.update(option, true)
  } catch (error) {
    console.error('更新散点图失败:', error)
  }
}

function getChartInstance() {
  return wrapper ? wrapper.getInstance() : null
}

function resize() {
  if (wrapper) {
    wrapper.resize()
  }
}

function exportChart(options = {}) {
  if (!wrapper) {
    throw new Error('图表未初始化')
  }
  
  const { type = 'png', pixelRatio = 2 } = options
  
  // SVG 导出需要使用 svg renderer
  if (type === 'svg') {
    // 使用原始数据和配置重新生成图表选项
    const chartOption = generateScatterOption(props.data, props.config)
    if (!chartOption) throw new Error('无法生成图表配置')
    
    console.log('[SVG Export] Chart option:', chartOption)
    console.log('[SVG Export] Series count:', chartOption.series?.length)
    
    // 检查系列数据
    if (chartOption.series && chartOption.series.length > 0) {
      chartOption.series.forEach((series, idx) => {
        console.log(`[SVG Export] Series ${idx}:`, {
          name: series.name,
          type: series.type,
          dataCount: series.data?.length,
          symbolSize: series.symbolSize,
          symbol: series.symbol,
          itemStyle: series.itemStyle,
          sampleData: series.data?.slice(0, 3) // 显示前3个数据点
        })
      })
    }
    
    // 临时创建使用 svg renderer 的实例
    const tempContainer = document.createElement('div')
    // 使用固定尺寸以确保SVG正确生成
    const exportWidth = 1200
    const exportHeight = 800
    tempContainer.style.width = exportWidth + 'px'
    tempContainer.style.height = exportHeight + 'px'
    tempContainer.style.position = 'absolute'
    tempContainer.style.left = '-9999px'
    document.body.appendChild(tempContainer)
    
    try {
      const tempInstance = echarts.init(tempContainer, null, { renderer: 'svg', width: exportWidth, height: exportHeight })
      
      // 修复字体族中的引号问题，避免 SVG 属性解析错误
      const fixFontFamily = (fontFamily) => {
        if (!fontFamily) return 'Arial, sans-serif'
        // 移除字体名称中的引号，使用单引号或去掉引号
        return fontFamily.replace(/"/g, "'")
      }
      
      // 修复所有可能包含字体的配置项
      if (chartOption.title && chartOption.title.textStyle) {
        chartOption.title.textStyle.fontFamily = fixFontFamily(chartOption.title.textStyle.fontFamily)
      }
      if (chartOption.legend && chartOption.legend.textStyle) {
        chartOption.legend.textStyle.fontFamily = fixFontFamily(chartOption.legend.textStyle.fontFamily)
      }
      if (chartOption.xAxis) {
        if (chartOption.xAxis.axisLabel) {
          chartOption.xAxis.axisLabel.fontFamily = fixFontFamily(chartOption.xAxis.axisLabel.fontFamily)
        }
        if (chartOption.xAxis.nameTextStyle) {
          chartOption.xAxis.nameTextStyle.fontFamily = fixFontFamily(chartOption.xAxis.nameTextStyle.fontFamily)
        }
      }
      if (chartOption.yAxis) {
        if (chartOption.yAxis.axisLabel) {
          chartOption.yAxis.axisLabel.fontFamily = fixFontFamily(chartOption.yAxis.axisLabel.fontFamily)
        }
        if (chartOption.yAxis.nameTextStyle) {
          chartOption.yAxis.nameTextStyle.fontFamily = fixFontFamily(chartOption.yAxis.nameTextStyle.fontFamily)
        }
      }
      if (chartOption.tooltip && chartOption.tooltip.textStyle) {
        chartOption.tooltip.textStyle.fontFamily = fixFontFamily(chartOption.tooltip.textStyle.fontFamily)
      }
      
      // 确保配置中的点样式正确，并强制设置较大的点以便可见
      if (chartOption.series) {
        chartOption.series.forEach(series => {
          if (series.type === 'scatter') {
            // 强制设置较大的点大小以确保可见
            series.symbolSize = 15
            series.symbol = series.symbol || 'circle'
            
            // 确保有明确的颜色和不透明度
            if (!series.itemStyle) {
              series.itemStyle = {}
            }
            series.itemStyle.opacity = 1.0
            
            // 如果没有颜色，设置一个默认颜色
            if (!series.itemStyle.color) {
              series.itemStyle.color = '#5470c6' // ECharts 默认蓝色
            }
            
            console.log(`[SVG Export] Adjusted series ${series.name}:`, {
              symbolSize: series.symbolSize,
              symbol: series.symbol,
              itemStyle: series.itemStyle
            })
          }
        })
      }
      
      // SVG 导出时使用白色背景
      if (chartOption.backgroundColor === 'transparent') {
        chartOption.backgroundColor = '#ffffff'
      }
      
      tempInstance.setOption(chartOption, true) // notMerge=true 确保配置完全替换
      
      let svgStr = tempInstance.renderToSVGString()
      console.log('[SVG Export] Original SVG length:', svgStr.length)
      console.log('[SVG Export] First 500 chars:', svgStr.substring(0, 500))
      
      // 检查并修复 SVG 开始标签的属性
      const svgTagMatch = svgStr.match(/<svg[^>]*>/i)
      if (svgTagMatch) {
        console.log('[SVG Export] Original SVG tag:', svgTagMatch[0])
        
        // 提取并清理 SVG 标签
        let svgTag = svgTagMatch[0]
        
        // 移除可能重复或格式错误的属性
        svgTag = svgTag
          .replace(/\s+/g, ' ') // 合并多个空格
          .replace(/\s*=\s*/g, '=') // 移除等号周围的空格
          .replace(/"\s+"/g, '" "') // 确保属性值之间有空格
        
        console.log('[SVG Export] Cleaned SVG tag:', svgTag)
        
        // 替换原始 SVG 标签
        svgStr = svgStr.replace(/<svg[^>]*>/i, svgTag)
      }
      
      console.log('[SVG Export] Final SVG first 500 chars:', svgStr.substring(0, 500))
      
      tempInstance.dispose()
      document.body.removeChild(tempContainer)
      return svgStr
    } catch (error) {
      console.error('[SVG Export] Error:', error)
      if (document.body.contains(tempContainer)) {
        document.body.removeChild(tempContainer)
      }
      throw error
    }
  }
  
  // PNG 导出：创建临时实例以实现透明背景
  // 使用原始数据和配置重新生成，并设置透明背景
  const exportConfig = { ...props.config, backgroundColor: 'transparent' }
  const chartOption = generateScatterOption(props.data, exportConfig)
  
  // 创建临时容器用于导出
  const tempContainer = document.createElement('div')
  const exportWidth = 1200
  const exportHeight = 800
  tempContainer.style.width = exportWidth + 'px'
  tempContainer.style.height = exportHeight + 'px'
  tempContainer.style.position = 'absolute'
  tempContainer.style.left = '-9999px'
  document.body.appendChild(tempContainer)
  
  try {
    const tempInstance = echarts.init(tempContainer, null, { renderer: 'canvas', width: exportWidth, height: exportHeight })
    tempInstance.setOption(chartOption)
    
    const dataURL = tempInstance.getDataURL({
      type: 'png',
      pixelRatio,
      backgroundColor: 'transparent',
      excludeComponents: ['toolbox']
    })
    
    tempInstance.dispose()
    document.body.removeChild(tempContainer)
    return dataURL
  } catch (error) {
    if (document.body.contains(tempContainer)) {
      document.body.removeChild(tempContainer)
    }
    throw error
  }
}

// 暴露方法给父组件
defineExpose({
  getChartInstance,
  resize,
  exportChart
})

onMounted(() => {
  wrapper = new ChartWrapper(chartRef.value, { theme: props.config?.theme })
  wrapper.init()
  updateChart()
})

watch(() => [props.data, props.config], () => {
  updateChart()
}, { deep: true })

onBeforeUnmount(() => {
  wrapper && wrapper.dispose()
})
</script>

<style scoped>
.chart-container { width: 100%; height: 420px; }
</style>
