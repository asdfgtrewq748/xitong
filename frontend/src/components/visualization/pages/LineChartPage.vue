<template>
  <div class="chart-page">
    <div class="page-header modern">
      <div class="title-group">
        <h2><el-icon><DataLine /></el-icon> 折线图</h2>
        <p class="subtitle">用于展示数据随时间或类别的变化趋势 — 支持多系列对比、平滑曲线与趋势分析</p>
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

          <el-collapse v-model="leftCollapseActive">
            <el-collapse-item title="主映射" name="mapping">
              <el-form label-position="top" size="small" class="compact-form">
                <el-form-item label="X 轴">
                  <el-select v-model="config.xField" placeholder="选择 X 字段" @change="updateChart">
                    <el-option v-for="f in fields" :key="f.name" :label="`${f.name} (${f.type})`" :value="f.name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Y 轴">
                  <el-select v-model="config.yField" placeholder="选择 Y 字段" @change="updateChart">
                    <el-option v-for="f in numericFields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="分组 (多条线)">
                  <el-select v-model="config.groupField" placeholder="可选: 按类别分组" clearable @change="updateChart">
                    <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-collapse-item>

            <el-collapse-item title="高级选项" name="advanced">
              <el-form label-position="top" size="small" class="compact-form">
                <el-divider content-position="left">线条样式</el-divider>
                <el-form-item label="线宽">
                  <el-slider v-model="config.lineWidth" :min="1" :max="10" :step="0.5" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item label="线条类型">
                  <el-select v-model="config.lineType" @change="updateChart">
                    <el-option label="实线" value="solid" />
                    <el-option label="虚线" value="dashed" />
                    <el-option label="点线" value="dotted" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.smooth" active-text="平滑曲线" @change="updateChart" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.showSymbol" active-text="显示数据点" @change="updateChart" />
                </el-form-item>
                <el-form-item label="数据点大小" v-if="config.showSymbol">
                  <el-slider v-model="config.symbolSize" :min="2" :max="20" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.showArea" active-text="显示面积" @change="updateChart" />
                </el-form-item>
                <el-form-item label="面积透明度" v-if="config.showArea">
                  <el-slider v-model="config.areaOpacity" :min="0.1" :max="0.8" :step="0.1" show-input @change="updateChart" />
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
                
                <el-divider content-position="left">导出选项</el-divider>
                <el-form-item label="导出内容">
                  <el-radio-group v-model="exportOptions.content" size="small">
                    <el-radio value="full">完整图表</el-radio>
                    <el-radio value="linesOnly">仅曲线</el-radio>
                  </el-radio-group>
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
            <div class="num">{{ totalDataPoints }}</div>
            <div class="label">数据点</div>
          </div>
          <div class="summary-item">
            <div class="num">{{ seriesCount }}</div>
            <div class="label">系列数</div>
          </div>
          <div class="summary-item">
            <div class="num">{{ previewData.length }}</div>
            <div class="label">记录数</div>
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

            <line-chart v-else ref="chartRef" :data="chartData" :config="fullChartConfig" :height="560" />
          </div>
        </div>
      </main>
    </div>

    <help-dialog v-model="showHelp" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { DataLine, QuestionFilled, RefreshLeft, Download } from '@element-plus/icons-vue'
import ChartToolbar from '../ChartToolbar.vue'
import HelpDialog from '../HelpDialog.vue'
import LineChart from '../charts/LineChart.vue'
import { useVisualizationStore } from '../../../stores/visualizationStore'
import { adaptForChart } from '../../../utils/dataAdapter'

const store = useVisualizationStore()
const chartRef = ref(null)
const showHelp = ref(false)

const config = reactive({
  type: 'line',
  xField: null,
  yField: null,
  groupField: null,
  title: '折线图',
  xAxisLabel: 'X轴',
  yAxisLabel: 'Y轴',
  showGrid: false,
  backgroundColor: 'transparent',
  fontFamily: 'SimSun, "Times New Roman", serif',
  theme: 'light',
  
  // 线条样式
  lineWidth: 2,
  lineType: 'solid',
  smooth: false,
  showSymbol: true,
  symbolSize: 6,
  showArea: false,
  areaOpacity: 0.3,
  
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
  showLegend: true
})

const exportOptions = reactive({
  content: 'full' // 'full' | 'linesOnly'
})

const fields = ref([])
const chartData = ref({ data: [], type: 'simple' })
const previewData = ref([])
const leftCollapseActive = ref(['mapping', 'advanced'])

const hasData = computed(() => store.hasData)
const numericFields = computed(() => fields.value.filter(f => f.type === 'number'))
// 完整图表配置 - 根据导出选项动态调整
const fullChartConfig = computed(() => {
  if (exportOptions.content === 'linesOnly') {
    // 仅曲线模式：隐藏所有装饰元素
    return {
      ...config,
      title: '',
      showLegend: false,
      showGrid: false,
      xAxisLabel: '',
      yAxisLabel: '',
      showAxisLine: false,
      showAxisTick: false,
      showGridLines: false,
      backgroundColor: 'transparent'
    }
  }
  return config
})

const onImported = ({ rows, columns, datasetId }) => {
  try {
    store.setParsedData(datasetId, rows, columns)
    fields.value = columns
    previewData.value = rows
    
    const numFields = columns.filter(c => c.type === 'number')
    // 确保X轴和Y轴不使用相同字段
    if (columns.length >= 1) {
      config.xField = columns[0].name
      // Y轴优先选择与X轴不同的数值字段
      if (numFields.length >= 1) {
        const differentNumField = numFields.find(f => f.name !== config.xField)
        config.yField = differentNumField ? differentNumField.name : (numFields.length > 1 ? numFields[1].name : numFields[0].name)
      }
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

// 导出事件处理 - ChartToolbar 会直接使用当前图表状态进行导出
const onExport = () => {
  // ChartToolbar 会自动处理导出，此处只需确认
  const mode = exportOptions.content === 'linesOnly' ? '仅曲线' : '完整图表'
  console.log(`导出模式: ${mode}`)
}

// 监听导出选项变化，触发图表重新渲染
watch(() => exportOptions.content, () => {
  // fullChartConfig 是计算属性，会自动响应变化
  // 但需要触发图表更新以应用新配置
  nextTick(() => {
    if (chartRef.value?.resize) {
      chartRef.value.resize()
    }
  })
}, { immediate: false })

// 统计计算
const totalDataPoints = computed(() => {
  if (!chartData.value || !chartData.value.data) return 0
  if (Array.isArray(chartData.value.data)) return chartData.value.data.length
  if (typeof chartData.value.data === 'object') {
    return Object.values(chartData.value.data).reduce((s, arr) => s + (Array.isArray(arr) ? arr.length : 0), 0)
  }
  return 0
})

const seriesCount = computed(() => {
  if (!config.groupField || !previewData.value) return 1
  try {
    return new Set(previewData.value.map(r => r[config.groupField])).size
  } catch (e) {
    return 1
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

.sidebar.modern .el-collapse-item__header {
  cursor: pointer;
  user-select: none;
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
