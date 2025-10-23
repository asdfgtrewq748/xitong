// frontend/src/utils/echartsOptimizer.js
// ECharts 性能优化工具

import { downSampleData, PerformanceConfig } from './performance'

/**
 * 获取优化的ECharts配置
 * @param {Object} originalOption - 原始配置
 * @returns {Object} 优化后的配置
 */
export function getOptimizedEChartsOption(originalOption) {
  const optimized = JSON.parse(JSON.stringify(originalOption))

  // 基础性能优化
  optimized.animation = PerformanceConfig.echarts.animationDuration > 0
  optimized.animationDuration = PerformanceConfig.echarts.animationDuration
  optimized.animationEasing = 'cubicOut'

  // 禁用不必要的特性
  optimized.useUTC = true
  optimized.progressive = 1000  // 渐进式渲染
  optimized.progressiveThreshold = 3000

  return optimized
}

/**
 * 优化系列数据
 * @param {Array} series - 系列数据
 * @param {Number} maxPoints - 最大点数
 * @returns {Array} 优化后的系列数据
 */
export function optimizeSeriesData(series, maxPoints = PerformanceConfig.echarts.maxDataPoints) {
  if (!Array.isArray(series)) return series

  return series.map(s => {
    if (!s.data || s.data.length <= maxPoints) {
      return s
    }

    console.log(`[ECharts优化] ${s.name || '系列'} 数据降采样: ${s.data.length} → ${maxPoints}`)

    return {
      ...s,
      data: downSampleData(s.data, maxPoints),
      sampling: 'lttb'  // 使用LTTB算法采样
    }
  })
}

/**
 * 3D图表优化配置
 */
export function get3DOptimizedOption(baseOption, devicePerformance = 'medium') {
  const optimized = { ...baseOption }

  // 根据设备性能调整
  if (devicePerformance === 'low') {
    optimized.grid3D = {
      ...optimized.grid3D,
      viewControl: {
        ...optimized.grid3D?.viewControl,
        autoRotate: false,
        damping: 0.8
      },
      light: {
        main: {
          intensity: 1.0,
          shadow: false  // 禁用阴影
        },
        ambient: {
          intensity: 0.3
        }
      },
      postEffect: {
        enable: false  // 禁用后处理效果
      }
    }
  } else if (devicePerformance === 'medium') {
    optimized.grid3D = {
      ...optimized.grid3D,
      light: {
        main: {
          intensity: 1.2,
          shadow: true,
          shadowQuality: 'low'
        }
      },
      postEffect: {
        enable: true,
        SSAO: {
          enable: false  // 禁用环境光遮蔽
        }
      }
    }
  }

  return optimized
}

/**
 * 创建响应式图表实例
 */
export class ResponsiveChart {
  constructor(echarts, dom) {
    this.echarts = echarts
    this.dom = dom
    this.chart = null
    this.resizeHandler = null
  }

  init(option) {
    if (this.chart) {
      this.chart.dispose()
    }

    this.chart = this.echarts.init(this.dom)
    this.chart.setOption(getOptimizedEChartsOption(option))

    // 添加响应式
    this.enableResponsive()
  }

  enableResponsive() {
    // 使用节流避免频繁resize
    let resizeTimer
    this.resizeHandler = () => {
      clearTimeout(resizeTimer)
      resizeTimer = setTimeout(() => {
        if (this.chart && !this.chart.isDisposed()) {
          this.chart.resize()
        }
      }, 100)
    }

    window.addEventListener('resize', this.resizeHandler)
  }

  dispose() {
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler)
    }
    if (this.chart && !this.chart.isDisposed()) {
      this.chart.dispose()
    }
  }

  updateOption(option, notMerge = false) {
    if (this.chart && !this.chart.isDisposed()) {
      this.chart.setOption(getOptimizedEChartsOption(option), notMerge)
    }
  }
}

/**
 * 延迟加载ECharts组件
 */
export async function lazyLoadECharts() {
  if (!PerformanceConfig.echarts.lazyLoad) {
    return import('echarts')
  }

  // 按需加载ECharts核心和组件
  const echarts = await import('echarts/core')
  const { CanvasRenderer } = await import('echarts/renderers')
  const { GridComponent, TooltipComponent, LegendComponent } = await import('echarts/components')
  const { LineChart, BarChart, PieChart, ScatterChart } = await import('echarts/charts')

  echarts.use([
    CanvasRenderer,
    GridComponent,
    TooltipComponent,
    LegendComponent,
    LineChart,
    BarChart,
    PieChart,
    ScatterChart
  ])

  return echarts
}

/**
 * 延迟加载ECharts GL
 */
export async function lazyLoadEChartsGL() {
  const echarts = await lazyLoadECharts()
  await import('echarts-gl')
  return echarts
}

export default {
  getOptimizedEChartsOption,
  optimizeSeriesData,
  get3DOptimizedOption,
  ResponsiveChart,
  lazyLoadECharts,
  lazyLoadEChartsGL
}
