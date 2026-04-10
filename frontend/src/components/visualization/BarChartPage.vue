<template>
  <div class="bar-chart-page">
    <improved-visualization-home />
  </div>
</template>

<script setup name="BarChartPage">
/* eslint-disable no-undef */
import ImprovedVisualizationHome from './ImprovedVisualizationHome.vue'
import { onMounted } from 'vue'
import { useVisualizationStore } from '../../stores/visualizationStore'

const store = useVisualizationStore()

onMounted(() => {
  // 设置默认图表类型为柱状图
  store.updateChartConfig({ type: 'bar' })
})
</script>

<style scoped>
.bar-chart-page {
  height: 100vh;
  overflow: hidden;
}

@media (max-width: 768px) {
  .chart-page { padding: 12px !important; }
  .chart-container { height: 320px !important; }
  .chart-controls { flex-wrap: wrap !important; gap: 6px !important; }
  .chart-controls > * { min-width: 100px !important; }
}
</style>