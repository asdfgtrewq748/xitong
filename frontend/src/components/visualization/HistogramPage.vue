<template>
  <div class="histogram-page">
    <improved-visualization-home />
  </div>
</template>

<script setup name="HistogramPage">
/* eslint-disable no-undef */
import ImprovedVisualizationHome from './ImprovedVisualizationHome.vue'
import { onMounted } from 'vue'
import { useVisualizationStore } from '../../stores/visualizationStore'

const store = useVisualizationStore()

onMounted(() => {
  // 设置默认图表类型为直方图
  store.updateChartConfig({ type: 'histogram' })
})
</script>

<style scoped>
.histogram-page {
  height: 100vh;
  overflow: hidden;
}
</style>