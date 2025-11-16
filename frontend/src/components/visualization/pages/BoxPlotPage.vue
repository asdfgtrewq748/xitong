<template>
  <div class="chart-page">
    <div class="page-header">
      <h2><el-icon><DataBoard /></el-icon>箱线图</h2>
      <div class="header-actions">
        <el-button @click="showHelp = true" circle><el-icon><QuestionFilled /></el-icon></el-button>
      </div>
    </div>

    <div class="page-content">
      <aside class="sidebar">
        <el-card shadow="never">
          <template #header>数据导入</template>
          <chart-toolbar @imported="onImported" @export="onExport" :has-data="hasData" :chart-ref="chartRef" compact />
        </el-card>

        <el-card shadow="never" style="margin-top: 16px;">
          <template #header>字段映射</template>
          <el-form label-position="top" size="small">
            <el-form-item label="数值字段">
              <el-select v-model="config.yField" @change="updateChart">
                <el-option v-for="field in numericFields" :key="field.name" :label="field.name" :value="field.name" />
              </el-select>
            </el-form-item>
            <el-form-item label="分组字段 (可选)">
              <el-select v-model="config.groupField" clearable @change="updateChart">
                <el-option v-for="field in fields" :key="field.name" :label="field.name" :value="field.name" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" style="margin-top: 16px;">
          <template #header>样式设置</template>
          <chart-settings-panel :config="config" chart-type="box" @apply="onSettingsApply" compact />
        </el-card>
      </aside>

      <main class="chart-area">
        <div class="chart-toolbar">
          <el-button-group>
            <el-button @click="resetView"><el-icon><RefreshLeft /></el-icon>重置</el-button>
            <el-button @click="exportChart('png')"><el-icon><Download /></el-icon>PNG</el-button>
            <el-button @click="exportChart('svg')"><el-icon><Download /></el-icon>SVG</el-button>
          </el-button-group>
        </div>
        <div class="chart-container">
          <el-empty v-if="!hasData" description="请导入数据" />
          <box-plot v-else ref="chartRef" :data="chartData" :config="chartConfig" :height="500" />
        </div>
      </main>

      <aside class="data-panel">
        <el-card shadow="never">
          <template #header>数据预览</template>
          <data-preview-table v-if="hasData" :data="previewData" :columns="fields.map(f => f.name)" :height="300" />
          <el-empty v-else description="暂无数据" :image-size="60" />
        </el-card>
      </aside>
    </div>

    <help-dialog v-model="showHelp" />
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { DataBoard, QuestionFilled, RefreshLeft, Download } from '@element-plus/icons-vue'
import ChartToolbar from '../ChartToolbar.vue'
import ChartSettingsPanel from '../ChartSettingsPanel.vue'
import DataPreviewTable from '../DataPreviewTable.vue'
import HelpDialog from '../HelpDialog.vue'
import BoxPlot from '../charts/BoxPlot.vue'
import { useVisualizationStore } from '../../../stores/visualizationStore'
import { adaptForChart } from '../../../utils/dataAdapter'

const store = useVisualizationStore()
const chartRef = ref(null)
const showHelp = ref(false)

const config = reactive({
  type: 'box',
  yField: null,
  groupField: null,
  title: '箱线图',
  showGrid: false,
  backgroundColor: 'transparent',
  fontFamily: 'SimSun, "Times New Roman", serif',
  theme: 'light'
})

const fields = ref([])
const chartData = ref({ data: [], type: 'simple' })
const previewData = ref([])
const hasData = computed(() => store.hasData)
const numericFields = computed(() => fields.value.filter(f => f.type === 'number'))
const chartConfig = computed(() => config)

const onImported = ({ rows, columns, datasetId }) => {
  store.setParsedData(datasetId, rows, columns)
  fields.value = columns
  previewData.value = rows
  const numFields = columns.filter(c => c.type === 'number')
  if (numFields.length >= 1) config.yField = numFields[0].name
  updateChart()
  ElMessage.success(`成功导入 ${rows.length} 条数据`)
}

const updateChart = () => {
  if (!store.currentDataset || !config.yField) return
  const { parsedData, columns } = store.currentDataset
  chartData.value = adaptForChart(parsedData, columns, config)
  store.updateChartConfig(config)
}

const onSettingsApply = ({ config: newConfig }) => {
  Object.assign(config, newConfig)
  updateChart()
}

const resetView = () => chartRef.value?.resize?.() && ElMessage.info('视图已重置')
const exportChart = (format) => {
  chartRef.value?.exportChart?.({ type: format, filename: `boxplot_${Date.now()}` })
  ElMessage.success(`正在导出${format.toUpperCase()}`)
}
const onExport = (payload) => exportChart(typeof payload === 'string' ? payload : payload?.format)
</script>

<style scoped>
.chart-page { height: 100%; display: flex; flex-direction: column; background: #f5f7fa; }
.page-header { background: white; padding: 16px 24px; border-bottom: 1px solid #e4e7ed; display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { margin: 0; display: flex; align-items: center; gap: 8px; }
.page-content { flex: 1; display: grid; grid-template-columns: 280px 1fr 320px; gap: 16px; padding: 16px; overflow: hidden; }
.sidebar, .data-panel { overflow-y: auto; }
.chart-area { display: flex; flex-direction: column; background: white; border-radius: 8px; padding: 16px; }
.chart-toolbar { margin-bottom: 12px; }
.chart-container { flex: 1; min-height: 0; }
</style>
