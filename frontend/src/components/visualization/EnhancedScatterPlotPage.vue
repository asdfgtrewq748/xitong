<template>
  <div class="enhanced-scatter-plot">
    <!-- 顶部工具栏 -->
    <div class="top-toolbar">
      <div class="toolbar-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/visualization' }">科研绘图</el-breadcrumb-item>
          <el-breadcrumb-item>散点图</el-breadcrumb-item>
        </el-breadcrumb>
        <h2 class="page-title">
          <el-icon><Coordinate /></el-icon>
          散点图 - 高质量科研图表
        </h2>
      </div>
      <div class="toolbar-right">
        <el-button-group>
          <el-button @click="showTemplateDialog = true">
            <el-icon><Document /></el-icon>
            科研模板
          </el-button>
          <el-button @click="exportAsPublication" type="primary">
            <el-icon><Download /></el-icon>
            学术导出
          </el-button>
          <el-button @click="toggleFullscreen">
            <el-icon><FullScreen /></el-icon>
            全屏
          </el-button>
        </el-button-group>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧数据面板 -->
      <div class="left-panel" :class="{ collapsed: leftPanelCollapsed }">
        <div class="panel-header">
          <h3>数据配置</h3>
          <el-button text @click="leftPanelCollapsed = !leftPanelCollapsed">
            <el-icon>
              <ArrowLeft v-if="!leftPanelCollapsed" />
              <ArrowRight v-else />
            </el-icon>
          </el-button>
        </div>

        <div class="panel-content" v-show="!leftPanelCollapsed">
          <!-- 数据导入 -->
          <el-card shadow="never" class="data-import-card">
            <template #header>
              <div class="card-header">
                <el-icon><Upload /></el-icon>
                <span>数据导入</span>
              </div>
            </template>
            <chart-toolbar
              @imported="onImported"
              :has-data="hasData"
            />
          </el-card>

          <!-- 字段配置 -->
          <el-card shadow="never" class="field-config-card">
            <template #header>
              <div class="card-header">
                <el-icon><Setting /></el-icon>
                <span>字段配置</span>
                <el-button
                  type="primary"
                  text
                  size="small"
                  @click="autoConfigureFields"
                  :disabled="!hasData"
                >
                  智能配置
                </el-button>
              </div>
            </template>

            <el-form label-position="top" size="small" :model="chartConfig">
              <el-form-item label="X 轴变量">
                <el-select
                  v-model="chartConfig.xField"
                  placeholder="选择X轴变量"
                  @change="applyConfig"
                  filterable
                >
                  <el-option
                    v-for="field in numericFields"
                    :key="field.name"
                    :label="`${field.name} (${field.stats?.min?.toFixed(2)} - ${field.stats?.max?.toFixed(2)})`"
                    :value="field.name"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="Y 轴变量">
                <el-select
                  v-model="chartConfig.yField"
                  placeholder="选择Y轴变量"
                  @change="applyConfig"
                  filterable
                >
                  <el-option
                    v-for="field in numericFields"
                    :key="field.name"
                    :label="`${field.name} (${field.stats?.min?.toFixed(2)} - ${field.stats?.max?.toFixed(2)})`"
                    :value="field.name"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="分组变量 (可选)">
                <el-select
                  v-model="chartConfig.groupField"
                  placeholder="按类别着色"
                  clearable
                  @change="applyConfig"
                  filterable
                >
                  <el-option
                    v-for="field in categoricalFields"
                    :key="field.name"
                    :label="`${field.name} (${field.stats?.unique} 个类别)`"
                    :value="field.name"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="大小变量 (可选)">
                <el-select
                  v-model="chartConfig.sizeField"
                  placeholder="气泡大小映射"
                  clearable
                  @change="applyConfig"
                  filterable
                >
                  <el-option
                    v-for="field in numericFields"
                    :key="field.name"
                    :label="field.name"
                    :value="field.name"
                  />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 样式配置 -->
          <el-card shadow="never" class="style-config-card">
            <template #header>
              <div class="card-header">
                <el-icon><Brush /></el-icon>
                <span>样式配置</span>
              </div>
            </template>

            <el-form label-position="top" size="small" :model="chartConfig">
              <el-form-item label="配色方案">
                <el-select v-model="chartConfig.colorScheme" @change="applyConfig">
                  <el-option label="Viridis (推荐)" value="viridis" />
                  <el-option label="Plasma" value="plasma" />
                  <el-option label="Coolwarm" value="coolwarm" />
                  <el-option label="RdBu" value="rdbu" />
                  <el-option label="Spectral" value="spectral" />
                </el-select>
              </el-form-item>

              <el-form-item label="点大小">
                <el-slider
                  v-model="chartConfig.pointSize"
                  :min="2"
                  :max="20"
                  show-input
                  @change="applyConfig"
                />
              </el-form-item>

              <el-form-item label="透明度">
                <el-slider
                  v-model="chartConfig.opacity"
                  :min="0.1"
                  :max="1"
                  :step="0.1"
                  show-input
                  @change="applyConfig"
                />
              </el-form-item>
            </el-form>
          </el-card>
        </div>
      </div>

      <!-- 中间图表区域 -->
      <div class="center-panel">
        <!-- 图表工具栏 -->
        <div class="chart-toolbar">
          <div class="toolbar-left">
            <el-input
              v-model="chartConfig.title"
              placeholder="输入图表标题"
              @change="applyConfig"
              style="width: 300px;"
            />
          </div>
          <div class="toolbar-center">
            <el-button-group>
              <el-button @click="zoomIn" :disabled="!hasData">
                <el-icon><ZoomIn /></el-icon>
              </el-button>
              <el-button @click="zoomOut" :disabled="!hasData">
                <el-icon><ZoomOut /></el-icon>
              </el-button>
              <el-button @click="resetZoom" :disabled="!hasData">
                <el-icon><RefreshLeft /></el-icon>
              </el-button>
            </el-button-group>
          </div>
          <div class="toolbar-right">
            <el-switch
              v-model="showDataPreview"
              active-text="数据预览"
              inactive-text=""
            />
          </div>
        </div>

        <!-- 图表容器 -->
        <div class="chart-container" :class="{ fullscreen: isFullscreen }">
          <div v-if="!hasData" class="empty-state">
            <el-empty description="请导入数据开始创建散点图">
              <el-button type="primary" @click="triggerDataImport">
                <el-icon><Upload /></el-icon>
                导入数据
              </el-button>
            </el-empty>
          </div>
          <scatter-plot
            v-else
            :data="chartData"
            :config="chartConfig"
            :height="chartHeight"
            ref="chartRef"
            @ready="onChartReady"
            @click="onChartClick"
            @brush="onChartBrush"
          />
        </div>

        <!-- 数据预览面板 -->
        <div v-if="showDataPreview && hasData" class="data-preview">
          <el-tabs v-model="activeDataTab">
            <el-tab-pane label="数据预览" name="preview">
              <data-preview-table
                :data="sampledData"
                :columns="fields"
                :height="200"
              />
            </el-tab-pane>
            <el-tab-pane label="统计分析" name="stats">
              <data-statistics-panel
                :data="sampledData"
                :fields="fields"
                @suggestion-applied="onSuggestionApplied"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>

      <!-- 右侧学术配置面板 -->
      <div class="right-panel" :class="{ collapsed: rightPanelCollapsed }">
        <div class="panel-header">
          <h3>学术配置</h3>
          <el-button text @click="rightPanelCollapsed = !rightPanelCollapsed">
            <el-icon>
              <ArrowRight v-if="!rightPanelCollapsed" />
              <ArrowLeft v-else />
            </el-icon>
          </el-button>
        </div>

        <div class="panel-content" v-show="!rightPanelCollapsed">
          <!-- 学术规范配置 -->
          <el-card shadow="never" class="academic-config-card">
            <template #header>
              <div class="card-header">
                <el-icon><Reading /></el-icon>
                <span>学术规范</span>
              </div>
            </template>

            <el-form label-position="top" size="small" :model="academicConfig">
              <el-form-item label="期刊格式">
                <el-select v-model="academicConfig.journalFormat" @change="applyAcademicConfig">
                  <el-option label="Nature" value="nature" />
                  <el-option label="Science" value="science" />
                  <el-option label="Cell" value="cell" />
                  <el-option label="PLOS ONE" value="plos" />
                  <el-option label="通用学术" value="general" />
                </el-select>
              </el-form-item>

              <el-form-item label="字体大小">
                <el-input-number
                  v-model="academicConfig.fontSize"
                  :min="8"
                  :max="20"
                  @change="applyAcademicConfig"
                />
              </el-form-item>

              <el-form-item label="线条宽度">
                <el-input-number
                  v-model="academicConfig.lineWidth"
                  :min="0.5"
                  :max="5"
                  :step="0.5"
                  @change="applyAcademicConfig"
                />
              </el-form-item>

              <el-form-item label="图片分辨率">
                <el-select v-model="academicConfig.resolution">
                  <el-option label="300 DPI (印刷质量)" :value="300" />
                  <el-option label="600 DPI (高质量)" :value="600" />
                  <el-option label="1200 DPI (超高质量)" :value="1200" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 轴标签配置 -->
          <el-card shadow="never" class="axis-config-card">
            <template #header>
              <div class="card-header">
                <el-icon><Coordinate /></el-icon>
                <span>轴标签配置</span>
              </div>
            </template>

            <el-form label-position="top" size="small" :model="chartConfig">
              <el-form-item label="X轴标签">
                <el-input
                  v-model="chartConfig.xAxisLabel"
                  placeholder="X轴标签"
                  @change="applyConfig"
                />
              </el-form-item>

              <el-form-item label="Y轴标签">
                <el-input
                  v-model="chartConfig.yAxisLabel"
                  placeholder="Y轴标签"
                  @change="applyConfig"
                />
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="chartConfig.showGrid" @change="applyConfig">
                  显示网格
                </el-checkbox>
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="chartConfig.showLegend" @change="applyConfig">
                  显示图例
                </el-checkbox>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 回归分析 -->
          <el-card shadow="never" class="regression-card">
            <template #header>
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>统计分析</span>
              </div>
            </template>

            <el-form label-position="top" size="small">
              <el-form-item>
                <el-checkbox v-model="showRegression" @change="toggleRegression">
                  显示回归线
                </el-checkbox>
              </el-form-item>

              <el-form-item v-if="showRegression">
                <el-select v-model="regressionType">
                  <el-option label="线性回归" value="linear" />
                  <el-option label="二次回归" value="quadratic" />
                  <el-option label="三次回归" value="cubic" />
                </el-select>
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="showCorrelation" @change="toggleCorrelation">
                  显示相关系数
                </el-checkbox>
              </el-form-item>

              <div v-if="correlationResult" class="correlation-result">
                <div class="stat-item">
                  <span class="stat-label">相关系数 (r):</span>
                  <span class="stat-value">{{ correlationResult.r.toFixed(3) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">R²:</span>
                  <span class="stat-value">{{ correlationResult.r2.toFixed(3) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">p值:</span>
                  <span class="stat-value">{{ correlationResult.pValue.toExponential(2) }}</span>
                </div>
              </div>
            </el-form>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 科研模板对话框 -->
    <el-dialog v-model="showTemplateDialog" title="科研图表模板" width="800px">
      <div class="template-grid">
        <div
          v-for="template in researchTemplates"
          :key="template.id"
          class="template-item"
          @click="applyTemplate(template)"
        >
          <div class="template-preview">
            <img :src="template.preview" :alt="template.name" />
          </div>
          <div class="template-info">
            <h4>{{ template.name }}</h4>
            <p>{{ template.description }}</p>
            <div class="template-tags">
              <el-tag v-for="tag in template.tags" :key="tag" size="small">
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup name="EnhancedScatterPlot">
/* eslint-disable no-undef */
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Coordinate, Upload, Setting, Brush, Download, FullScreen,
  Document, ZoomIn, ZoomOut, RefreshLeft, ArrowLeft, ArrowRight,
  Reading, TrendCharts
} from '@element-plus/icons-vue'

import ChartToolbar from './ChartToolbar.vue'
import DataPreviewTable from './DataPreviewTable.vue'
import DataStatisticsPanel from './DataStatisticsPanel.vue'
import ScatterPlot from './charts/ScatterPlot.vue'
import { adaptForChart } from '../../utils/dataAdapter'
import { smartSample } from '../../utils/sampling'
import { calculateCorrelation } from '../../utils/statistics'

const chartRef = ref(null)
const showDataPreview = ref(true)
const activeDataTab = ref('preview')
const leftPanelCollapsed = ref(false)
const rightPanelCollapsed = ref(false)
const isFullscreen = ref(false)
const showTemplateDialog = ref(false)
const showRegression = ref(false)
const showCorrelation = ref(false)
const regressionType = ref('linear')
const correlationResult = ref(null)

// 数据
const rawData = ref([])
const fields = ref([])
const chartData = ref({ data: [], type: 'simple' })
const sampledData = ref([])

// 图表配置
const chartConfig = ref({
  type: 'scatter',
  xField: null,
  yField: null,
  groupField: null,
  sizeField: null,
  title: '散点图分析',
  xAxisLabel: 'X轴',
  yAxisLabel: 'Y轴',
  colorScheme: 'viridis',
  pointSize: 8,
  opacity: 0.8,
  showGrid: true,
  showLegend: true
})

// 学术配置
const academicConfig = ref({
  journalFormat: 'general',
  fontSize: 12,
  lineWidth: 1.5,
  resolution: 300
})

// 科研模板
const researchTemplates = ref([
  {
    id: 'correlation-basic',
    name: '基础相关性分析',
    description: '标准的散点图，包含回归线和相关系数',
    preview: '/api/placeholder/200/150',
    tags: ['相关性', '回归分析'],
    config: {
      showRegression: true,
      showCorrelation: true,
      regressionType: 'linear'
    }
  },
  {
    id: 'grouped-scatter',
    name: '分组散点图',
    description: '按类别分组的散点图，适合多组数据比较',
    preview: '/api/placeholder/200/150',
    tags: ['分组', '比较'],
    config: {
      requireGroupField: true,
      showLegend: true
    }
  },
  {
    id: 'bubble-scatter',
    name: '气泡图',
    description: '三维数据可视化，用大小表示第三维数据',
    preview: '/api/placeholder/200/150',
    tags: ['气泡图', '三维'],
    config: {
      requireSizeField: true,
      opacity: 0.6
    }
  }
])

// 计算属性
const hasData = computed(() => rawData.value.length > 0)
const numericFields = computed(() => {
  if (!rawData.value.length) return []
  return fields.value.filter(f => f.type === 'number')
})
const categoricalFields = computed(() => {
  if (!rawData.value.length) return []
  return fields.value.filter(f => f.type === 'string')
})
const chartHeight = computed(() => isFullscreen.value ? window.innerHeight - 100 : 500)

// 方法
function onImported({ rows, columns }) {
  rawData.value = rows
  fields.value = columns

  // 自动选择前两个数值字段
  if (numericFields.value.length >= 2) {
    chartConfig.value.xField = numericFields.value[0].name
    chartConfig.value.yField = numericFields.value[1].name
    chartConfig.value.xAxisLabel = numericFields.value[0].name
    chartConfig.value.yAxisLabel = numericFields.value[1].name
  }

  applyConfig()
  ElMessage.success(`成功导入 ${rows.length} 条数据`)
}

function applyConfig() {
  if (!hasData.value) return

  try {
    // 数据采样
    let processedData = rawData.value
    if (processedData.length > 5000) {
      const result = smartSample(processedData, { maxPoints: 5000 })
      processedData = result.sampled
      sampledData.value = result.sampled
      ElMessage.info(`数据量较大，已智能采样至 ${result.sampled.length} 点以优化性能`)
    } else {
      sampledData.value = processedData
    }

    const adapted = adaptForChart(processedData, fields.value, chartConfig.value)
    chartData.value = adapted

    // 计算相关性
    if (chartConfig.value.xField && chartConfig.value.yField && showCorrelation.value) {
      calculateStats()
    }
  } catch (error) {
    ElMessage.error('配置应用失败: ' + error.message)
  }
}

function autoConfigureFields() {
  if (!hasData.value || numericFields.value.length < 2) {
    ElMessage.warning('需要至少2个数值字段')
    return
  }

  // 智能选择字段
  chartConfig.value.xField = numericFields.value[0].name
  chartConfig.value.yField = numericFields.value[1].name
  chartConfig.value.xAxisLabel = numericFields.value[0].name
  chartConfig.value.yAxisLabel = numericFields.value[1].name

  // 如果有分类字段，自动设置分组
  if (categoricalFields.value.length > 0) {
    chartConfig.value.groupField = categoricalFields.value[0].name
  }

  applyConfig()
  ElMessage.success('已智能配置字段')
}

function applyAcademicConfig() {
  // 应用学术配置到图表
  applyConfig()
}

function calculateStats() {
  if (!chartConfig.value.xField || !chartConfig.value.yField) return

  const xData = sampledData.value.map(d => d[chartConfig.value.xField]).filter(v => v != null)
  const yData = sampledData.value.map(d => d[chartConfig.value.yField]).filter(v => v != null)

  if (xData.length !== yData.length || xData.length === 0) return

  correlationResult.value = calculateCorrelation(xData, yData)
}

function toggleRegression() {
  applyConfig()
}

function toggleCorrelation() {
  if (showCorrelation.value) {
    calculateStats()
  } else {
    correlationResult.value = null
  }
}

function zoomIn() {
  // 实现缩放功能
  if (chartRef.value) {
    chartRef.value.zoomIn()
  }
}

function zoomOut() {
  // 实现缩放功能
  if (chartRef.value) {
    chartRef.value.zoomOut()
  }
}

function resetZoom() {
  // 重置缩放
  if (chartRef.value) {
    chartRef.value.resetZoom()
  }
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
  nextTick(() => {
    if (chartRef.value) {
      chartRef.value.resize()
    }
  })
}

function exportAsPublication() {
  if (!chartRef.value) {
    ElMessage.warning('请先创建图表')
    return
  }

  ElMessageBox.confirm(
    '选择导出格式',
    '学术导出',
    {
      confirmButtonText: 'PNG (高质量)',
      cancelButtonText: 'SVG (矢量)',
      type: 'info'
    }
  ).then(() => {
    // PNG导出
    const dataURL = chartRef.value.exportChart({
      type: 'png',
      pixelRatio: academicConfig.value.resolution / 72,
      backgroundColor: '#ffffff'
    })

    // 创建下载链接
    const link = document.createElement('a')
    link.download = `scatter_plot_${Date.now()}.png`
    link.href = dataURL
    link.click()

    ElMessage.success('图表已导出，可直接用于论文发表')
  }).catch(() => {
    // SVG导出
    const svgStr = chartRef.value.exportChart({ type: 'svg' })
    const blob = new Blob([svgStr], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.download = `scatter_plot_${Date.now()}.svg`
    link.href = url
    link.click()

    URL.revokeObjectURL(url)
    ElMessage.success('图表已导出为SVG格式')
  })
}

function applyTemplate(template) {
  if (template.config.requireGroupField && !categoricalFields.value.length) {
    ElMessage.warning('该模板需要分类字段，但当前数据没有分类字段')
    return
  }

  if (template.config.requireSizeField && numericFields.value.length < 3) {
    ElMessage.warning('该模板需要第三个数值字段作为大小映射')
    return
  }

  // 应用模板配置
  Object.assign(chartConfig.value, template.config)

  if (template.config.requireGroupField && categoricalFields.value.length > 0) {
    chartConfig.value.groupField = categoricalFields.value[0].name
  }

  if (template.config.requireSizeField && numericFields.value.length >= 3) {
    chartConfig.value.sizeField = numericFields.value[2].name
  }

  applyConfig()
  showTemplateDialog.value = false
  ElMessage.success(`已应用模板: ${template.name}`)
}

function triggerDataImport() {
  ElMessage.info('请在左侧面板选择数据文件导入')
}

function onChartReady(instance) {
  console.log('Chart ready:', instance)
}

function onChartClick(params) {
  console.log('Chart clicked:', params)
}

function onChartBrush(params) {
  console.log('Chart brush:', params)
}

function onSuggestionApplied() {
  // 处理统计面板的建议
  applyConfig()
}

onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.enhanced-scatter-plot {
  height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.top-toolbar {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.left-panel, .right-panel {
  background: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
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

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.el-card {
  margin-bottom: 16px;
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

.chart-toolbar {
  background: white;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  flex: 1;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

.data-preview {
  background: white;
  border-radius: 8px;
  margin-top: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.correlation-result {
  background: #f0f9ff;
  padding: 12px;
  border-radius: 6px;
  margin-top: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 13px;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-weight: 600;
  color: #303133;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  max-height: 500px;
  overflow-y: auto;
}

.template-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.template-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.template-preview {
  width: 100%;
  height: 120px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.template-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.template-info p {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}

.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .left-panel, .right-panel {
    width: 280px;
  }
}

@media (max-width: 1200px) {
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
</style>