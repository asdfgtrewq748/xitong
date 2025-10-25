<template>
  <div class="box-plot">
    <div
      ref="chartContainer"
      class="chart-container"
      :style="{ height: height + 'px' }"
    ></div>
  </div>
</template>

<script setup name="BoxPlot">
/* eslint-disable no-undef */
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { ChartWrapper, generateBoxPlotOption } from '../../../utils/chartWrapper'

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  config: {
    type: Object,
    required: true
  },
  height: {
    type: Number,
    default: 400
  },
  width: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['ready', 'click'])

const chartContainer = ref(null)
const chartWrapper = ref(null)

const initChart = async () => {
  if (!chartContainer.value) return

  await nextTick()

  chartWrapper.value = new ChartWrapper(chartContainer.value, {
    theme: props.config.theme || 'light',
    renderer: 'canvas'
  })

  chartWrapper.value.init()
  updateChart()

  chartWrapper.value.getInstance().on('click', (params) => {
    emit('click', params)
  })

  emit('ready', chartWrapper.value.getInstance())
}

const updateChart = () => {
  if (!chartWrapper.value || !props.data) return

  // 检查数据是否有效
  const hasValidData = props.data.data && 
    Array.isArray(props.data.data) && 
    props.data.data.length > 0

  if (!hasValidData) {
    // 如果没有有效数据，渲染空图表（使用notMerge清除旧配置）
    chartWrapper.value.update({
      title: { text: props.config.title || '箱线图', left: 'center' },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: []
    }, true)
    return
  }

  const option = generateBoxPlotOption(props.data, props.config)
  // 使用notMerge=true完全替换配置，避免旧配置残留
  chartWrapper.value.update(option, true)
}

const resize = () => {
  if (chartWrapper.value) {
    chartWrapper.value.resize()
  }
}

const exportChart = (options = {}) => {
  if (!chartWrapper.value) return null

  return chartWrapper.value.exportImage({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#ffffff',
    ...options
  })
}

// 监听数据变化
watch([() => props.data, () => props.config], () => {
  updateChart()
}, { deep: true })

// 监听主题变化
watch(() => props.config.theme, (newTheme) => {
  if (chartWrapper.value) {
    chartWrapper.value.setTheme(newTheme)
    updateChart()
  }
})

onMounted(() => {
  initChart()

  // 监听窗口大小变化
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  if (chartWrapper.value) {
    chartWrapper.value.dispose()
  }
})

// 暴露方法给父组件
/* eslint-disable no-undef */
defineExpose({
  exportChart,
  resize,
  getInstance: () => chartWrapper.value?.getInstance()
})
</script>

<style scoped>
.box-plot {
  width: 100%;
  position: relative;
}

.chart-container {
  width: 100%;
  min-height: 300px;
}
</style>