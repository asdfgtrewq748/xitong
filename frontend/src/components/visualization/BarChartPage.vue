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
</style>