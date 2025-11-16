<template>
  <div class="chart-page">
    <div class="page-header modern">
      <div class="title-group">
        <h2><el-icon><TrendCharts /></el-icon> 散点图</h2>
        <p class="subtitle">用于展示变量间关系与分布 — 支持分组着色、尺寸映射、回归拟合与导出</p>
      </div>

      <div class="header-actions">
        <chart-toolbar @imported="onImported" @export="onExport" :has-data="hasData" :chart-ref="chartRef" />
        <el-button type="text" @click="showHelp = true"><el-icon><QuestionFilled /></el-icon></el-button>
      </div>
    </div>

    <div class="page-content modern">
      <!-- 左侧：可收缩配置面板 -->
      <aside class="sidebar modern">
        <el-card shadow="hover" class="panel">
          <template #header>
            <div class="panel-title">字段映射</div>
          </template>

          <el-collapse v-model:active-name="leftCollapseActive">
            <el-collapse-item title="主映射" name="mapping">
              <el-form label-position="top" size="small" class="compact-form">
                <el-form-item label="X 轴">
                  <el-select v-model="config.xField" placeholder="选择 X 字段" @change="updateChart">
                    <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Y 轴">
                  <el-select v-model="config.yField" placeholder="选择 Y 字段" @change="updateChart">
                    <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="颜色 (分组)">
                  <el-select v-model="config.colorField" placeholder="可选: 分类/分组字段" clearable @change="updateChart">
                    <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="点大小 (可选)">
                  <el-select v-model="config.sizeField" placeholder="可选: 数值字段" clearable @change="updateChart">
                    <el-option v-for="f in numericFields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-collapse-item>

            <el-collapse-item title="高级选项" name="advanced">
              <el-form label-position="top" size="small" class="compact-form">
                <el-divider content-position="left">点样式</el-divider>
                <el-form-item label="点大小">
                  <el-slider v-model="config.pointSize" :min="2" :max="30" :step="1" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item label="透明度">
                  <el-slider v-model="config.opacity" :min="0.1" :max="1" :step="0.1" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item label="点形状">
                  <el-select v-model="config.pointShape" @change="updateChart">
                    <el-option label="圆形" value="circle" />
                    <el-option label="方形" value="rect" />
                    <el-option label="三角形" value="triangle" />
                    <el-option label="菱形" value="diamond" />
                  </el-select>
                </el-form-item>
                <el-form-item label="点边框宽度">
                  <el-slider v-model="config.pointBorderWidth" :min="0" :max="5" :step="0.5" show-input @change="updateChart" />
                </el-form-item>
                
                <el-divider content-position="left">坐标轴样式</el-divider>
                <el-form-item label="X轴标签">
                  <el-input v-model="config.xAxisLabel" @change="updateChart" />
                </el-form-item>
                <el-form-item label="Y轴标签">
                  <el-input v-model="config.yAxisLabel" @change="updateChart" />
                </el-form-item>
                <el-form-item label="轴标签字体大小">
                  <el-slider v-model="config.axisLabelFontSize" :min="8" :max="24" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item label="轴线宽度">
                  <el-slider v-model="config.axisLineWidth" :min="0" :max="5" :step="0.5" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.showAxisLine" active-text="显示轴线" @change="updateChart" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.showAxisTick" active-text="显示刻度" @change="updateChart" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.showGridLines" active-text="显示网格线" @change="updateChart" />
                </el-form-item>
                
                <el-divider content-position="left">字体设置</el-divider>
                <el-form-item label="标题字体大小">
                  <el-slider v-model="config.titleFontSize" :min="12" :max="32" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item label="标题字体粗细">
                  <el-select v-model="config.titleFontWeight" @change="updateChart">
                    <el-option label="正常" value="normal" />
                    <el-option label="加粗" value="bold" />
                    <el-option label="细" value="lighter" />
                  </el-select>
                </el-form-item>
                <el-form-item label="字体族">
                  <el-select v-model="config.fontFamily" @change="updateChart">
                    <el-option label="宋体 (SimSun)" value="SimSun, 'Times New Roman', serif" />
                    <el-option label="Arial" value="Arial, sans-serif" />
                    <el-option label="Times New Roman" value="'Times New Roman', serif" />
                    <el-option label="Helvetica" value="Helvetica, Arial, sans-serif" />
                  </el-select>
                </el-form-item>
                
                <el-divider content-position="left">其他</el-divider>
                <el-form-item>
                  <el-switch v-model="extras.showRegression" active-text="回归线" @change="updateChart" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="extras.showLabels" active-text="点标签" @change="updateChart" />
                </el-form-item>
                <el-form-item label="采样">
                  <el-select v-model="extras.sampling" placeholder="自动采样" @change="updateChart">
                    <el-option label="关闭" value="none" />
                    <el-option label="快速 (低分辨率)" value="fast" />
                    <el-option label="平衡" value="balanced" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-collapse-item>
          </el-collapse>
        </el-card>


      </aside>

      <!-- 中间：图表区域 -->
      <main class="chart-area modern">
        <div class="top-summary">
          <div class="summary-item">
            <div class="num">{{ totalPoints }}</div>
            <div class="label">点数</div>
          </div>
          <div class="summary-item">
            <div class="num">{{ groupsCount }}</div>
            <div class="label">分组数</div>
          </div>
          <div class="summary-item">
            <div class="num">{{ previewData.length }}</div>
            <div class="label">预览行</div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-actions">
            <el-button size="small" type="text" @click="resetView"><el-icon><RefreshLeft /></el-icon></el-button>
            <el-dropdown @command="exportChart">
              <el-button size="small"><el-icon><Download /></el-icon> 导出 <i class="el-icon-arrow-down el-icon--right"></i></el-button>
              <el-dropdown-menu>
                <el-dropdown-item command="png">PNG</el-dropdown-item>
                <el-dropdown-item command="svg">SVG</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>

          <div class="chart-container modern">
            <el-empty v-if="!hasData" description="暂无数据，使用右上角导入或左侧面板导入">
              <el-button type="primary" @click="$emit('open-import')">导入数据</el-button>
            </el-empty>

            <scatter-plot v-else ref="chartRef" :data="chartData" :config="fullChartConfig" :height="560" />
          </div>
        </div>
      </main>


    </div>

    <help-dialog v-model="showHelp" />
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts, QuestionFilled, RefreshLeft, Download } from '@element-plus/icons-vue'
import ChartToolbar from '../ChartToolbar.vue'
import HelpDialog from '../HelpDialog.vue'
import ScatterPlot from '../charts/ScatterPlot.vue'
import { useVisualizationStore } from '../../../stores/visualizationStore'
import { adaptForChart } from '../../../utils/dataAdapter'

const store = useVisualizationStore()
const chartRef = ref(null)
const showHelp = ref(false)

const config = reactive({
  type: 'scatter',
  xField: null,
  yField: null,
  colorField: null,
  sizeField: null,
  title: '散点图',
  xAxisLabel: 'X轴',
  yAxisLabel: 'Y轴',
  showGrid: false,
  backgroundColor: 'transparent',
  fontFamily: 'SimSun, "Times New Roman", serif',
  theme: 'light',
  pointSize: 10,
  opacity: 0.8,
  colorScheme: 'viridis',
  showLegend: true,
  
  // 坐标轴样式
  axisLineColor: '#333',
  axisLabelFontSize: 12,
  axisLineWidth: 1,
  showAxisLine: true,
  showAxisTick: true,
  showGridLines: false,
  gridLineColor: '#e0e0e0',
  gridLineWidth: 1,
  
  // 坐标轴范围
  xAxisMin: null,
  xAxisMax: null,
  yAxisMin: null,
  yAxisMax: null,
  
  // 字体样式
  titleFontSize: 18,
  titleFontWeight: 'bold',
  legendFontSize: 12,
  
  // 点样式
  pointShape: 'circle',
  pointBorderColor: '#fff',
  pointBorderWidth: 0,
  customColors: []
})

const fields = ref([])
const chartData = ref({ data: [], type: 'simple' })
const previewData = ref([])

const hasData = computed(() => store.hasData)
const numericFields = computed(() => fields.value.filter(f => f.type === 'number'))

// UI extras and controls
const extras = reactive({ showRegression: false, showLabels: false, sampling: 'none' })
const leftCollapseActive = ref(['mapping', 'advanced'])

const fullChartConfig = computed(() => ({
  ...config,
  extras: { ...extras }
}))

const onImported = ({ rows, columns, datasetId }) => {
  try {
    store.setParsedData(datasetId, rows, columns)
    fields.value = columns
    previewData.value = rows

    // 自动映射第一个和第二个数值字段，确保不同
    const numFields = columns.filter(c => c.type === 'number')
    if (numFields.length >= 2) {
      config.xField = numFields[0].name
      config.yField = numFields[1].name
    } else if (numFields.length === 1) {
      config.xField = columns[0]?.name
      config.yField = numFields[0].name
    }

    updateChart()
    ElMessage.success(`成功导入 ${rows.length} 条数据`)
  } catch (error) {
    ElMessage.error('数据导入失败: ' + error.message)
  }
}

const updateChart = () => {
  if (!store.currentDataset || !config.xField || !config.yField) return

  try {
    const { parsedData, columns } = store.currentDataset
    const adapted = adaptForChart(parsedData, columns, config)
    chartData.value = adapted
    store.updateChartConfig(config)
  } catch (error) {
    ElMessage.error('更新图表失败: ' + error.message)
  }
}

const resetView = () => {
  if (chartRef.value?.resize) {
    chartRef.value.resize()
  }
  ElMessage.info('视图已重置')
}

const exportChart = (format) => {
  // allow command from dropdown (png/svg) or event payload object
  const fmt = typeof format === 'string' ? format : (format?.command || format?.format)
  if (!fmt) return
  if (!chartRef.value) {
    ElMessage.warning('图表未准备好')
    return
  }
  try {
    chartRef.value.exportChart?.({ type: fmt, filename: `scatter_${Date.now()}` })
    ElMessage.success(`正在导出 ${fmt.toUpperCase()} 格式`)
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

const onExport = (payload) => {
  const format = typeof payload === 'string' ? payload : payload?.format
  if (format) exportChart(format)
}

// summary counts
const totalPoints = computed(() => {
  if (!chartData.value || !chartData.value.data) return 0
  if (Array.isArray(chartData.value.data)) return chartData.value.data.length
  // grouped data: object with arrays
  if (typeof chartData.value.data === 'object') return Object.values(chartData.value.data).reduce((s, arr) => s + (Array.isArray(arr) ? arr.length : 0), 0)
  return 0
})

const groupsCount = computed(() => {
  if (!config.colorField || !previewData.value) return 0
  try {
    return new Set(previewData.value.map(r => r[config.colorField])).size
  } catch (e) {
    return 0
  }
})
</script>

<style scoped>
.chart-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.page-header {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-header.modern {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 20px 8px 20px;
  border-bottom: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-group h2 {
  font-size: 20px;
  margin: 0;
  color: white;
}

.title-group .subtitle {
  margin: 4px 0 0 0;
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
}

.panel {
  border-radius: 8px;
}

.compact-form .el-form-item {
  margin-bottom: 8px;
}

.page-content.modern {
  flex: 1;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 18px;
  padding: 8px 16px 16px 16px;
  overflow: hidden;
}

.top-summary {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.summary-item {
  background: white;
  padding: 10px 14px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(16,24,40,0.03);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.summary-item .num {
  font-weight: 600;
  font-size: 18px;
}

.summary-item .label {
  color: #6b7280;
  font-size: 12px;
}

.chart-card {
  background: transparent;
}

.chart-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  margin-bottom: 8px;
}

.page-content {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 16px;
  padding: 16px;
  overflow: hidden;
}

.sidebar.modern {
  overflow-y: auto;
  max-height: calc(100vh - 180px);
}

.sidebar.modern .el-collapse {
  border: none;
}

.sidebar.modern .el-card {
  overflow: visible;
}

.chart-area {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  padding: 16px;
}

.chart-toolbar {
  margin-bottom: 12px;
}

.chart-container {
  flex: 1;
  min-height: 0;
}

@media (max-width: 1400px) {
  .page-content {
    grid-template-columns: 260px 1fr 280px;
  }
}
</style>
