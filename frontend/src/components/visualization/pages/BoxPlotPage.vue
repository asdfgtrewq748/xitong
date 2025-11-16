<template>
  <div class="chart-page modern-layout">
    <div class="page-header modern">
      <div class="title-group">
        <h2><el-icon><DataBoard /></el-icon> 箱线图</h2>
        <p class="subtitle">数据分布与离群值分析</p>
      </div>
      <div class="header-actions">
        <chart-toolbar @imported="onImported" :has-data="hasData" :chart-ref="chartRef" />
        <el-button type="text" @click="showHelp = true"><el-icon><QuestionFilled /></el-icon></el-button>
      </div>
    </div>

    <div class="page-content modern">
      <aside class="sidebar modern">
        <el-card shadow="hover" class="panel">
          <template #header><div class="panel-title">配置面板</div></template>
          <el-collapse v-model="leftCollapseActive">
            <el-collapse-item title="字段映射" name="mapping">
              <el-form label-position="top" size="small" class="compact-form">
                <el-form-item label="数值字段">
                  <el-select v-model="config.yField" @change="updateChart">
                    <el-option v-for="f in numericFields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="分组字段 (可选)">
                  <el-select v-model="config.groupField" clearable @change="updateChart">
                    <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-collapse-item>

            <el-collapse-item title="高级选项" name="advanced">
              <el-form label-position="top" size="small" class="compact-form">
                <el-divider content-position="left">基础设置</el-divider>
                <el-form-item label="图表标题">
                  <el-input v-model="config.title" @change="updateChart" />
                </el-form-item>
                <el-form-item label="Y轴标签">
                  <el-input v-model="config.yAxisLabel" @change="updateChart" />
                </el-form-item>

                <el-divider content-position="left">显示选项</el-divider>
                <el-form-item>
                  <el-switch v-model="config.showLegend" active-text="显示图例" @change="updateChart" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.showGrid" active-text="显示网格" @change="updateChart" />
                </el-form-item>

                <el-divider content-position="left">配色方案</el-divider>
                <el-form-item label="配色">
                  <el-select v-model="config.colorScheme" @change="updateChart">
                    <el-option label="默认" value="default" />
                    <el-option label="学术蓝" value="academic" />
                    <el-option label="自然绿" value="nature" />
                  </el-select>
                </el-form-item>

                <el-divider content-position="left">字体设置</el-divider>
                <el-form-item label="标题字号">
                  <el-slider v-model="config.titleFontSize" :min="12" :max="32" show-input @change="updateChart" />
                </el-form-item>
              </el-form>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </aside>

      <main class="chart-display modern">
        <div class="summary-cards">
          <el-card shadow="hover" class="summary-card">
            <div class="card-content">
              <el-icon class="card-icon"><DataLine /></el-icon>
              <div class="card-info">
                <div class="card-value">{{ groupCount }}</div>
                <div class="card-label">分组数</div>
              </div>
            </div>
          </el-card>
          <el-card shadow="hover" class="summary-card">
            <div class="card-content">
              <el-icon class="card-icon"><Document /></el-icon>
              <div class="card-info">
                <div class="card-value">{{ totalRecords }}</div>
                <div class="card-label">数据点</div>
              </div>
            </div>
          </el-card>
        </div>

        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>箱线图视图</span>
              <el-button-group size="small">
                <el-button @click="resetView"><el-icon><RefreshLeft /></el-icon></el-button>
              </el-button-group>
            </div>
          </template>
          <div class="chart-wrapper">
            <el-empty v-if="!hasData" description="请导入数据开始分析" :image-size="120" />
            <box-plot v-else ref="chartRef" :data="chartData" :config="fullChartConfig" :height="560" />
          </div>
        </el-card>
      </main>
    </div>

    <help-dialog v-model="showHelp" />
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { DataBoard, QuestionFilled, RefreshLeft, DataLine, Document } from '@element-plus/icons-vue'
import ChartToolbar from '../ChartToolbar.vue'
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
  yAxisLabel: '数值',
  showLegend: true,
  showGrid: false,
  colorScheme: 'default',
  backgroundColor: 'transparent',
  fontFamily: 'SimSun, "Times New Roman", serif',
  titleFontSize: 18
})

const fields = ref([])
const chartData = ref({ data: [], type: 'simple' })
const previewData = ref([])
const leftCollapseActive = ref(['mapping', 'advanced'])

const hasData = computed(() => store.hasData)
const numericFields = computed(() => fields.value.filter(f => f.type === 'number'))
const fullChartConfig = computed(() => config)

const onImported = ({ rows, columns, datasetId }) => {
  try {
    store.setParsedData(datasetId, rows, columns)
    fields.value = columns
    previewData.value = rows
    const numFields = columns.filter(c => c.type === 'number')
    if (numFields.length >= 1) config.yField = numFields[0].name
    updateChart()
    ElMessage.success(`成功导入 ${rows.length} 条数据`)
  } catch (error) {
    ElMessage.error('数据导入失败: ' + error.message)
  }
}

const updateChart = () => {
  if (!store.currentDataset || !config.yField) return
  try {
    const { parsedData, columns } = store.currentDataset
    chartData.value = adaptForChart(parsedData, columns, config)
    store.updateChartConfig(config)
  } catch (error) {
    ElMessage.error('更新图表失败: ' + error.message)
  }
}

const resetView = () => {
  if (chartRef.value?.resize) chartRef.value.resize()
  ElMessage.info('视图已重置')
}

const groupCount = computed(() => {
  if (!config.groupField || !previewData.value.length) return 1
  try {
    return new Set(previewData.value.map(r => r[config.groupField])).size
  } catch (e) {
    return 1
  }
})

const totalRecords = computed(() => previewData.value.length)
</script>

<style scoped>
.chart-page.modern-layout { height: 100%; display: flex; flex-direction: column; background: #f5f7fa; }
.page-header.modern { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; justify-content: space-between; align-items: center; padding: 20px 20px 8px 20px; border-bottom: none; }
.title-group h2 { font-size: 20px; margin: 0; color: white; }
.title-group .subtitle { margin: 4px 0 0 0; color: rgba(255, 255, 255, 0.85); font-size: 13px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.page-content.modern { flex: 1; display: grid; grid-template-columns: 320px 1fr; gap: 18px; padding: 8px 16px 16px 16px; overflow: hidden; }
.sidebar.modern { overflow-y: auto; padding-right: 4px; }
.chart-display.modern { display: flex; flex-direction: column; gap: 12px; overflow-y: auto; }
.summary-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.summary-card { border-radius: 8px; }
.card-content { display: flex; align-items: center; gap: 16px; }
.card-icon { font-size: 32px; color: #667eea; }
.card-info { flex: 1; }
.card-value { font-size: 24px; font-weight: bold; color: #303133; }
.card-label { font-size: 13px; color: #909399; margin-top: 4px; }
.chart-card { flex: 1; border-radius: 8px; display: flex; flex-direction: column; min-height: 0; }
.chart-header { display: flex; justify-content: space-between; align-items: center; }
.chart-wrapper { height: 100%; min-height: 500px; }
.panel { border-radius: 8px; }
.panel-title { font-weight: 600; font-size: 14px; }
.compact-form .el-form-item { margin-bottom: 12px; }
:deep(.el-collapse-item__header) { font-weight: 500; padding-left: 8px; cursor: pointer; }
:deep(.el-collapse-item__content) { padding: 12px 8px; }
:deep(.el-divider__text) { font-size: 12px; color: #909399; }
</style>
