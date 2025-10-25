<template>
  <div class="chart-container" ref="chartRef"></div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { ChartWrapper } from '../ChartWrapper'
import { generateHeatmapOption } from '../../../utils/chartWrapper'

const props = defineProps({ data: { type: Object, required: true }, config: { type: Object, required: true } })
const chartRef = ref(null)
let wrapper = null

function updateChart() {
  if (!wrapper || !props.data || !props.config) return
  try {
    const option = generateHeatmapOption(props.data, props.config)
    wrapper.update(option, true)
  } catch (error) {
    console.error('更新热力图失败:', error)
  }
}

function getChartInstance() {
  return wrapper ? wrapper.getInstance() : null
}

// 暴露方法给父组件
defineExpose({
  getChartInstance
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
