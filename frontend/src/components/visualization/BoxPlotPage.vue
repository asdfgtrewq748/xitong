<template>
  <div class="box-plot-page">
    <improved-visualization-home />
  </div>
</template>

<script setup name="BoxPlotPage">
/* eslint-disable no-undef */
import ImprovedVisualizationHome from './ImprovedVisualizationHome.vue'
import { onMounted } from 'vue'
import { useVisualizationStore } from '../../stores/visualizationStore'

const store = useVisualizationStore()

onMounted(() => {
  // 设置默认图表类型为箱线图
  store.updateChartConfig({ type: 'box' })
})
</script>

<style scoped>
.box-plot-page {
  height: 100vh;
  overflow: hidden;
}
</style>