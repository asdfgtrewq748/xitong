<template>
  <div class="chart-container" :style="{ height: height + 'px' }" ref="chartRef"></div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { ChartWrapper } from '../ChartWrapper'
import { generateSurfaceOption } from '../../../utils/chartWrapper'

const props = defineProps({ 
  data: { type: Object, required: true }, 
  config: { type: Object, required: true },
  height: { type: Number, default: 480 }
})
const chartRef = ref(null)
let wrapper = null

function updateChart() {
  if (!wrapper || !props.data || !props.config) return
  try {
    const option = generateSurfaceOption(props.data, props.config)
    wrapper.update(option, true)
  } catch (error) {
    console.error('更新三维曲面图失败:', error)
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
  const instance = wrapper.getInstance()
  if (!instance) {
    throw new Error('无法获取图表实例')
  }
  
  const { type = 'png', pixelRatio = 2 } = options
  
  return instance.getDataURL({
    type: type === 'svg' ? 'svg' : 'png',
    pixelRatio,
    backgroundColor: props.config?.backgroundColor || '#fff'
  })
}

// 暴露方法给父组件
defineExpose({
  getChartInstance,
  resize,
  exportChart
})

onMounted(() => {
  wrapper = new ChartWrapper(chartRef.value, { theme: props.config?.theme, initOptions: { renderer: 'webgl' } })
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
.chart-container { width: 100%; height: 480px; }
</style>
