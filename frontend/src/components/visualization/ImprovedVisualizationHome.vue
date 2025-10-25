<template>
  <div class="improved-visualization-home">
    <!-- 顶部导航栏 -->
    <div class="top-navigation">
      <div class="nav-left">
        <h1 class="app-title">
          <el-icon class="title-icon"><TrendCharts /></el-icon>
          科研绘图工作台
        </h1>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>科研绘图</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentChartTypeLabel }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </div>
      <div class="nav-right">
        <theme-selector @change="onThemeChange" />
        <el-button type="primary" @click="showQuickActions = true" circle>
          <el-icon><Operation /></el-icon>
        </el-button>
        <el-button @click="showHelp = true" circle>
          <el-icon><QuestionFilled /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧面板 - 数据管理 -->
      <div class="left-panel" :class="{ collapsed: leftPanelCollapsed }">
        <div class="panel-header">
          <h3>数据管理</h3>
          <el-button
            text
            @click="leftPanelCollapsed = !leftPanelCollapsed"
            class="collapse-btn"
          >
            <el-icon>
              <ArrowLeft v-if="!leftPanelCollapsed" />
              <ArrowRight v-else />
            </el-icon>
          </el-button>
        </div>
        <div class="panel-content" v-show="!leftPanelCollapsed">
          <!-- 数据导入区域 -->
          <el-card shadow="never" class="data-import-card">
            <template #header>
              <div class="card-header">
                <el-icon><Upload /></el-icon>
                <span>数据导入</span>
              </div>
            </template>
            <chart-toolbar
              @imported="onImported"
              @export="onExport"
              :has-data="hasData"
              :chart-ref="chartComponentRef"
              compact
            />
          </el-card>

          <!-- 数据集列表 -->
          <el-card shadow="never" class="dataset-list-card">
            <template #header>
              <div class="card-header">
                <el-icon><FolderOpened /></el-icon>
                <span>数据集</span>
                <el-button
                  type="primary"
                  text
                  size="small"
                  @click="showDatasetManager = true"
                  style="margin-left: auto;"
                >
                  管理
                </el-button>
              </div>
            </template>
            <div class="dataset-list">
              <div
                v-for="dataset in datasetList"
                :key="dataset.id"
                class="dataset-item"
                :class="{ active: currentDatasetId === dataset.id }"
                @click="setCurrentDataset(dataset.id)"
              >
                <div class="dataset-info">
                  <div class="dataset-name">{{ dataset.name }}</div>
                  <div class="dataset-meta">{{ dataset.meta.rowCount }} 行 × {{ dataset.meta.columnCount }} 列</div>
                </div>
                <el-button
                  text
                  type="danger"
                  size="small"
                  @click.stop="deleteDataset(dataset.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </el-card>

          <!-- 图表类型选择 -->
          <el-card shadow="never" class="chart-type-card">
            <template #header>
              <div class="card-header">
                <el-icon><PieChart /></el-icon>
                <span>图表类型</span>
              </div>
            </template>
            <div class="chart-type-grid">
              <div
                v-for="chart in chartTypes"
                :key="chart.type"
                class="chart-type-item"
                :class="{ active: localConfig.type === chart.type }"
                @click="changeChartType(chart.type)"
              >
                <el-icon :size="24" :color="chart.color">
                  <component :is="chart.icon" />
                </el-icon>
                <span>{{ chart.name }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 中间图表区域 -->
      <div class="center-panel">
        <!-- 快速操作栏 -->
        <div class="quick-toolbar">
          <div class="toolbar-left">
            <el-button-group>
              <el-button
                :icon="RefreshLeft"
                @click="resetView"
                title="重置视图"
              />
              <el-button
                :icon="FullScreen"
                @click="toggleFullscreen"
                title="全屏"
              />
            </el-button-group>
          </div>
          <div class="toolbar-center">
            <h2 class="chart-title">{{ localConfig.title || '科研图表' }}</h2>
          </div>
          <div class="toolbar-right">
            <el-button-group>
              <el-dropdown @command="exportChart">
                <el-button :icon="Download">
                  导出<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="png">PNG 图像</el-dropdown-item>
                    <el-dropdown-item command="svg">SVG 矢量图</el-dropdown-item>
                    <el-dropdown-item command="pdf">PDF 文档</el-dropdown-item>
                    <el-dropdown-item divided command="bundle">打包导出</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button :icon="Share" title="分享" />
            </el-button-group>
          </div>
        </div>

        <!-- 图表容器 -->
        <div class="chart-container" :class="{ fullscreen: isFullscreen }">
          <div
            v-if="!hasData"
            class="empty-state"
          >
            <el-empty description="请导入数据开始创建图表">
              <el-button type="primary" @click="triggerDataImport">
                <el-icon><Upload /></el-icon>
                导入数据
              </el-button>
            </el-empty>
          </div>
          <component
            v-else
            :is="currentChartComponent"
            :data="chartData"
            :config="chartConfig"
            :height="isFullscreen ? window.innerHeight - 100 : 500"
            ref="chartComponentRef"
            @ready="onChartReady"
            @click="onChartClick"
          />
        </div>

        <!-- 数据预览切换 -->
        <div class="data-preview-toggle">
          <el-switch
            v-model="showDataPreview"
            active-text="数据预览"
            inactive-text=""
            @change="toggleDataPreview"
          />
        </div>

        <!-- 数据预览面板 -->
        <div v-if="showDataPreview && hasData" class="data-preview-panel">
          <data-preview-table
            :data="previewData"
            :columns="fields.map(f => f.name)"
            :height="200"
          />
        </div>

        <!-- 示例画廊 -->
        <div v-if="!hasData" class="sample-gallery">
          <chart-gallery @load-sample="onLoadSample" compact />
        </div>
      </div>

      <!-- 右侧面板 - 配置与统计 -->
      <div class="right-panel" :class="{ collapsed: rightPanelCollapsed }">
        <div class="panel-header">
          <h3>配置与分析</h3>
          <el-button
            text
            @click="rightPanelCollapsed = !rightPanelCollapsed"
            class="collapse-btn"
          >
            <el-icon>
              <ArrowRight v-if="!rightPanelCollapsed" />
              <ArrowLeft v-else />
            </el-icon>
          </el-button>
        </div>
        <div class="panel-content" v-show="!rightPanelCollapsed">
          <!-- 快速配置 -->
          <el-card shadow="never" class="quick-config-card">
            <template #header>
              <div class="card-header">
                <el-icon><Setting /></el-icon>
                <span>快速配置</span>
                <el-button
                  type="primary"
                  text
                  size="small"
                  @click="autoConfigure"
                  style="margin-left: auto;"
                >
                  智能配置
                </el-button>
              </div>
            </template>
            <el-form label-position="top" :model="localConfig" size="small">
              <el-form-item label="X 字段">
                <el-select v-model="localConfig.xField" placeholder="选择 X 字段" @change="applyConfig">
                  <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name"/>
                </el-select>
              </el-form-item>
              <el-form-item label="Y 字段">
                <el-select v-model="localConfig.yField" placeholder="选择 Y 字段" @change="applyConfig">
                  <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name"/>
                </el-select>
              </el-form-item>
              <el-form-item v-if="needsZField" label="Z 字段">
                <el-select v-model="localConfig.zField" placeholder="选择 Z 字段" @change="applyConfig">
                  <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name"/>
                </el-select>
              </el-form-item>
              <el-form-item v-if="needsGroupField" label="分组字段（可选）">
                <el-select v-model="localConfig.groupField" placeholder="选择分组字段" clearable @change="applyConfig">
                  <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name"/>
                </el-select>
              </el-form-item>
              <el-form-item v-if="needsColorField" label="颜色字段">
                <el-select v-model="localConfig.colorField" placeholder="选择颜色字段" @change="applyConfig">
                  <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name"/>
                </el-select>
              </el-form-item>
              <el-form-item label="颜色方案">
                <el-select v-model="localConfig.colorScheme" @change="applyConfig">
                  <el-option label="Viridis" value="viridis" />
                  <el-option label="Plasma" value="plasma" />
                  <el-option label="Coolwarm" value="coolwarm" />
                  <el-option label="Jet" value="jet" />
                  <el-option label="Rainbow" value="rainbow" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 数据统计 -->
          <el-card shadow="never" class="data-stats-card" v-if="hasData">
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>数据统计</span>
              </div>
            </template>
            <data-statistics-panel :data="previewData" :fields="fields" />
          </el-card>

          <!-- 高级设置 -->
          <el-card shadow="never" class="advanced-settings-card">
            <template #header>
              <div class="card-header">
                <el-icon><Tools /></el-icon>
                <span>高级设置</span>
              </div>
            </template>
            <chart-settings-panel
              :config="localConfig"
              :chart-type="localConfig.type"
              @apply="onSettingsApply"
              compact
            />
          </el-card>

          <!-- 采样信息 -->
          <el-alert
            v-if="samplingInfo.enabled"
            :title="`数据采样已启用: ${samplingInfo.method}`"
            :description="`原始 ${samplingInfo.original} 点 → 采样后 ${samplingInfo.sampled} 点 (${(samplingInfo.ratio * 100).toFixed(1)}%)`"
            type="info"
            :closable="false"
            show-icon
            class="sampling-alert"
          />
        </div>
      </div>
    </div>

    <!-- 快速操作弹窗 -->
    <quick-actions v-model="showQuickActions" @action="handleQuickAction" />

    <!-- 数据集管理弹窗 -->
    <dataset-manager
      v-model="showDatasetManager"
      :datasets="datasets"
      @select="setCurrentDataset"
      @delete="deleteDataset"
    />

    <!-- 帮助弹窗 -->
    <help-dialog v-model="showHelp" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts, Operation, QuestionFilled, Upload, FolderOpened,
  PieChart, RefreshLeft, FullScreen, Download, Share, Setting,
  DataAnalysis, Tools, ArrowLeft, ArrowRight, Delete,
  DataLine, Histogram, Grid, DataBoard
} from '@element-plus/icons-vue'

import ChartToolbar from './ChartToolbar.vue'
import ChartGallery from './ChartGallery.vue'
import ChartSettingsPanel from './ChartSettingsPanel.vue'
import DataPreviewTable from './DataPreviewTable.vue'
import ThemeSelector from './ThemeSelector.vue'
import QuickActions from './QuickActions.vue'
import DatasetManager from './DatasetManager.vue'
import HelpDialog from './HelpDialog.vue'
import DataStatisticsPanel from './DataStatisticsPanel.vue'

// 图表组件
import ScatterPlot from './charts/ScatterPlot.vue'
import HeatMap from './charts/HeatMap.vue'
import Surface3D from './charts/Surface3D.vue'
import LineChart from './charts/LineChart.vue'
import BarChart from './charts/BarChart.vue'
import BoxPlot from './charts/BoxPlot.vue'
import HistogramChart from './charts/Histogram.vue'

import { useVisualizationStore } from '../../stores/visualizationStore'
import { adaptForChart } from '../../utils/dataAdapter'
import { smartSample, getSamplingRecommendation } from '../../utils/sampling'

const store = useVisualizationStore()
const chartComponentRef = ref(null)

// 界面状态
const leftPanelCollapsed = ref(false)
const rightPanelCollapsed = ref(false)
const isFullscreen = ref(false)
const showDataPreview = ref(false)
const showQuickActions = ref(false)
const showDatasetManager = ref(false)
const showHelp = ref(false)

// 图表配置
const localConfig = reactive({
  type: 'scatter',
  xField: null,
  yField: null,
  zField: null,
  groupField: null,
  colorField: null,
  sizeField: null,
  colorScheme: 'viridis',
  title: '科研图表',
  xAxisLabel: 'X轴',
  yAxisLabel: 'Y轴',
  zAxisLabel: 'Z轴',
  showLegend: true,
  showGrid: true,
  pointSize: 8,
  lineWidth: 2,
  opacity: 0.8,
  theme: 'light'
})

// 数据状态
const fields = ref([])
const chartData = ref({ data: [], type: 'simple' })
const previewData = ref([])
const samplingInfo = ref({ enabled: false, method: 'none', original: 0, sampled: 0, ratio: 1 })

// 图表类型配置
const chartTypes = ref([
  { type: 'scatter', name: '散点图', icon: TrendCharts, color: '#667eea' },
  { type: 'line', name: '折线图', icon: DataLine, color: '#f093fb' },
  { type: 'bar', name: '柱状图', icon: Histogram, color: '#4facfe' },
  { type: 'heatmap', name: '热力图', icon: Grid, color: '#43e97b' },
  { type: 'surface', name: '3D曲面', icon: PieChart, color: '#fa709a' },
  { type: 'box', name: '箱线图', icon: DataBoard, color: '#feca57' },
  { type: 'histogram', name: '直方图', icon: DataAnalysis, color: '#48dbfb' }
])

// 计算属性
const hasData = computed(() => store.hasData)
const datasets = computed(() => store.datasets)
const currentDatasetId = computed(() => store.currentDatasetId)
const datasetList = computed(() => store.datasetList)

const currentChartComponent = computed(() => {
  const components = {
    scatter: ScatterPlot,
    line: LineChart,
    bar: BarChart,
    heatmap: HeatMap,
    surface: Surface3D,
    box: BoxPlot,
    histogram: HistogramChart
  }
  return components[localConfig.type] || ScatterPlot
})

const currentChartTypeLabel = computed(() => {
  const chart = chartTypes.value.find(c => c.type === localConfig.type)
  return chart ? chart.name : '未知图表'
})

const needsZField = computed(() => ['surface'].includes(localConfig.type))
const needsGroupField = computed(() => ['bar', 'line', 'scatter', 'box', 'histogram'].includes(localConfig.type))
const needsColorField = computed(() => ['heatmap', 'scatter'].includes(localConfig.type))

const chartConfig = localConfig

// 方法
const onImported = ({ rows, columns, datasetId }) => {
  try {
    store.setParsedData(datasetId, rows, columns)
    fields.value = columns
    previewData.value = rows

    // 检查是否需要采样
    const recommendation = getSamplingRecommendation(rows)
    let processedData = rows

    if (recommendation.needsSampling) {
      const result = smartSample(rows, {
        maxPoints: recommendation.targetPoints,
        method: 'auto'
      })
      processedData = result.sampled
      samplingInfo.value = {
        enabled: true,
        method: result.info.method,
        original: result.info.original,
        sampled: result.info.sampled,
        ratio: parseFloat(result.info.ratio)
      }
      ElMessage.warning(`数据量较大(${rows.length}行)，已自动采样至${processedData.length}点以优化性能`)
    } else {
      samplingInfo.value = { enabled: false, method: 'none', original: rows.length, sampled: rows.length, ratio: 1 }
    }

    // 自动配置图表
    autoConfigure()

    ElMessage.success(`成功导入 ${rows.length} 条数据${samplingInfo.value.enabled ? `（采样显示${processedData.length}点）` : ''}`)
  } catch (error) {
    ElMessage.error('数据导入失败: ' + error.message)
  }
}

const onExport = (type) => {
  ElMessage.info(`正在导出 ${type.toUpperCase()}...`)
}

const changeChartType = (type) => {
  localConfig.type = type
  if (hasData.value) {
    applyConfig()
  }
}

const applyConfig = () => {
  if (!store.currentDataset) {
    ElMessage.warning('请先导入数据')
    return
  }

  try {
    const { parsedData, columns } = store.currentDataset

    // 应用采样
    let processedData = parsedData
    if (samplingInfo.value.enabled && samplingInfo.value.original > 0) {
      const result = smartSample(parsedData, {
        maxPoints: samplingInfo.value.sampled,
        method: 'auto'
      })
      processedData = result.sampled
    }

    const adapted = adaptForChart(processedData, columns, localConfig)
    chartData.value = adapted
    store.updateChartConfig(localConfig)
  } catch (error) {
    ElMessage.error('应用配置失败: ' + error.message)
  }
}

const autoConfigure = () => {
  store.autoConfigureChart()
  Object.assign(localConfig, store.chartConfig)
  applyConfig()
  ElMessage.success('已自动配置图表参数')
}

const onLoadSample = ({ rows, columns, type }) => {
  try {
    fields.value = columns
    previewData.value = rows
    localConfig.type = type

    const adapted = adaptForChart(rows, columns, localConfig)
    chartData.value = adapted
    samplingInfo.value = { enabled: false, method: 'none', original: rows.length, sampled: rows.length, ratio: 1 }

    ElMessage.success('示例数据加载成功')
  } catch (error) {
    ElMessage.error('示例加载失败: ' + error.message)
  }
}

const onSettingsApply = ({ config }) => {
  Object.assign(localConfig, config)
  applyConfig()
  ElMessage.success('设置已应用')
}

const onThemeChange = (theme) => {
  localConfig.theme = theme
  if (hasData.value) {
    applyConfig()
  }
}

const setCurrentDataset = (id) => {
  store.setCurrentDataset(id)
  const dataset = store.currentDataset
  if (dataset) {
    fields.value = dataset.columns
    previewData.value = dataset.parsedData
    applyConfig()
  }
}

const deleteDataset = (id) => {
  store.deleteDataset(id)
  ElMessage.success('数据集已删除')
}

const resetView = () => {
  if (chartComponentRef.value) {
    chartComponentRef.value.resize()
  }
  ElMessage.info('视图已重置')
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  setTimeout(() => {
    if (chartComponentRef.value) {
      chartComponentRef.value.resize()
    }
  }, 100)
}

const toggleDataPreview = () => {
  // 由 el-switch 自动处理
}

const exportChart = (format) => {
  if (chartComponentRef.value) {
    try {
      chartComponentRef.value.exportChart({
        type: format,
        filename: `chart_${Date.now()}`
      })
      ElMessage.success(`图表已导出为 ${format.toUpperCase()} 格式`)
    } catch (error) {
      ElMessage.error('导出失败: ' + error.message)
    }
  }
}

const triggerDataImport = () => {
  // 触发文件导入
  ElMessage.info('请在左侧面板选择数据文件导入')
}

const onChartReady = (instance) => {
  console.log('Chart ready:', instance)
}

const onChartClick = (params) => {
  console.log('Chart clicked:', params)
}

const handleQuickAction = (action) => {
  switch (action) {
    case 'import':
      triggerDataImport()
      break
    case 'auto-config':
      autoConfigure()
      break
    case 'export':
      exportChart('png')
      break
    case 'reset':
      resetView()
      break
    default:
      break
  }
}

// 生命周期
onMounted(() => {
  // 初始化
})

onUnmounted(() => {
  // 清理
})
</script>

<style scoped>
.improved-visualization-home {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 顶部导航 */
.top-navigation {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.title-icon {
  font-size: 24px;
  color: #409eff;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 主要内容 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 面板通用样式 */
.left-panel, .right-panel {
  background: white;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
}

.left-panel {
  width: 320px;
  border-right: 1px solid #e4e7ed;
}

.left-panel.collapsed {
  width: 60px;
}

.right-panel {
  width: 320px;
  border-left: 1px solid #e4e7ed;
}

.right-panel.collapsed {
  width: 60px;
}

.center-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafbfc;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.collapse-btn {
  padding: 4px;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* 卡片通用样式 */
.el-card {
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
}

.el-card:last-child {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* 数据集列表 */
.dataset-list {
  max-height: 200px;
  overflow-y: auto;
}

.dataset-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dataset-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
}

.dataset-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}

.dataset-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.dataset-meta {
  font-size: 12px;
  color: #909399;
}

/* 图表类型选择 */
.chart-type-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.chart-type-item {
  padding: 12px 8px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.chart-type-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
}

.chart-type-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}

.chart-type-item span {
  font-size: 12px;
  color: #606266;
}

/* 快速工具栏 */
.quick-toolbar {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 图表容器 */
.chart-container {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  flex: 1;
  position: relative;
}

.chart-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  border-radius: 0;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 数据预览 */
.data-preview-toggle {
  padding: 8px 0;
  text-align: center;
}

.data-preview-panel {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  margin-top: 16px;
}

.sample-gallery {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  margin-top: 16px;
}

/* 采样警告 */
.sampling-alert {
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .left-panel {
    width: 280px;
  }
  .right-panel {
    width: 280px;
  }
}

@media (max-width: 992px) {
  .left-panel, .right-panel {
    position: absolute;
    z-index: 100;
    height: 100%;
    box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  }

  .left-panel.collapsed {
    transform: translateX(-100%);
  }

  .right-panel.collapsed {
    transform: translateX(100%);
  }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .improved-visualization-home {
    background: #1a1a1a;
  }

  .top-navigation,
  .el-card,
  .chart-container,
  .quick-toolbar {
    background: #2d2d2d;
    border-color: #404040;
  }

  .panel-header {
    background: #363636;
  }

  .app-title,
  .panel-header h3,
  .chart-title {
    color: #ffffff;
  }
}
</style>