<template>
  <div class="enhanced-line-chart">
    <!-- 顶部工具栏 -->
    <div class="top-toolbar">
      <div class="toolbar-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/visualization' }">科研绘图</el-breadcrumb-item>
          <el-breadcrumb-item>折线图</el-breadcrumb-item>
        </el-breadcrumb>
        <h2 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          折线图 - 高质量科研图表
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
                    v-for="field in allFields"
                    :key="field.name"
                    :label="field.name"
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
                    :label="field.name"
                    :value="field.name"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="分组变量 (可选)">
                <el-select
                  v-model="chartConfig.groupField"
                  placeholder="按类别分组"
                  clearable
                  @change="applyConfig"
                  filterable
                >
                  <el-option
                    v-for="field in categoricalFields"
                    :key="field.name"
                    :label="field.name"
                    :value="field.name"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="数据排序">
                <el-select v-model="sortConfig.sortBy" @change="applySorting">
                  <el-option label="按X轴升序" value="x-asc" />
                  <el-option label="按X轴降序" value="x-desc" />
                  <el-option label="按Y轴升序" value="y-asc" />
                  <el-option label="按Y轴降序" value="y-desc" />
                  <el-option label="原始顺序" value="none" />
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
                  <el-option label="Colorbrewer Set1" value="set1" />
                  <el-option label="Colorbrewer Set2" value="set2" />
                  <el-option label="Tableau 10" value="tableau10" />
                  <el-option label="Viridis" value="viridis" />
                  <el-option label="Scientific" value="scientific" />
                </el-select>
              </el-form-item>

              <el-form-item label="线条样式">
                <el-radio-group v-model="chartConfig.lineStyle" @change="applyConfig">
                  <el-radio-button label="solid">实线</el-radio-button>
                  <el-radio-button label="dashed">虚线</el-radio-button>
                  <el-radio-button label="dotted">点线</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="数据点">
                <el-switch
                  v-model="chartConfig.showDataPoints"
                  active-text="显示数据点"
                  @change="applyConfig"
                />
              </el-form-item>

              <el-form-item label="平滑曲线">
                <el-switch
                  v-model="chartConfig.smooth"
                  active-text="启用平滑"
                  @change="applyConfig"
                />
              </el-form-item>

              <el-form-item label="填充区域">
                <el-switch
                  v-model="chartConfig.showArea"
                  active-text="区域填充"
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
            <el-empty description="请导入数据开始创建折线图">
              <el-button type="primary" @click="triggerDataImport">
                <el-icon><Upload /></el-icon>
                导入数据
              </el-button>
            </el-empty>
          </div>
          <line-chart
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
            <el-tab-pane label="趋势分析" name="trends">
              <trend-analysis-panel
                :data="sampledData"
                :x-field="chartConfig.xField"
                :y-field="chartConfig.yField"
                :group-field="chartConfig.groupField"
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
                  <el-option label="PNAS" value="pnas" />
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

              <el-form-item label="坐标轴类型">
                <el-select v-model="chartConfig.xAxisType" @change="applyConfig">
                  <el-option label="数值轴" value="value" />
                  <el-option label="类别轴" value="category" />
                  <el-option label="时间轴" value="time" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 趋势分析 -->
          <el-card shadow="never" class="trend-analysis-card">
            <template #header>
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>趋势分析</span>
              </div>
            </template>

            <el-form label-position="top" size="small">
              <el-form-item>
                <el-checkbox v-model="showTrendLine" @change="toggleTrendLine">
                  显示趋势线
                </el-checkbox>
              </el-form-item>

              <el-form-item v-if="showTrendLine">
                <el-select v-model="trendType">
                  <el-option label="线性趋势" value="linear" />
                  <el-option label="多项式趋势" value="polynomial" />
                  <el-option label="移动平均" value="moving" />
                  <el-option label="指数平滑" value="exponential" />
                </el-select>
              </el-form-item>

              <el-form-item v-if="trendType === 'moving'">
                <el-input-number
                  v-model="movingWindow"
                  :min="2"
                  :max="50"
                  placeholder="窗口大小"
                  @change="applyTrendAnalysis"
                />
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="showConfidenceInterval" @change="toggleConfidenceInterval">
                  显示置信区间
                </el-checkbox>
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="showOutliers" @change="toggleOutliers">
                  标记异常值
                </el-checkbox>
              </el-form-item>

              <div v-if="trendResult" class="trend-result">
                <div class="stat-item">
                  <span class="stat-label">斜率:</span>
                  <span class="stat-value">{{ trendResult.slope?.toFixed(4) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">R²:</span>
                  <span class="stat-value">{{ trendResult.r2?.toFixed(4) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">趋势:</span>
                  <span class="stat-value" :class="trendResult.trend">
                    {{ trendResult.trend === 'upward' ? '上升' : trendResult.trend === 'downward' ? '下降' : '平稳' }}
                  </span>
                </div>
              </div>
            </el-form>
          </el-card>

          <!-- 注释和标记 -->
          <el-card shadow="never" class="annotation-card">
            <template #header>
              <div class="card-header">
                <el-icon><EditPen /></el-icon>
                <span>注释标记</span>
              </div>
            </template>

            <el-form label-position="top" size="small">
              <el-form-item>
                <el-checkbox v-model="showAnnotations" @change="toggleAnnotations">
                  显示注释
                </el-checkbox>
              </el-form-item>

              <el-form-item v-if="showAnnotations">
                <el-input
                  v-model="annotationText"
                  placeholder="输入注释文本"
                  @keyup.enter="addAnnotation"
                >
                  <template #append>
                    <el-button @click="addAnnotation">添加</el-button>
                  </template>
                </el-input>
              </el-form-item>

              <div v-if="annotations.length > 0" class="annotation-list">
                <div
                  v-for="(annotation, index) in annotations"
                  :key="index"
                  class="annotation-item"
                >
                  <span class="annotation-text">{{ annotation.text }}</span>
                  <el-button text type="danger" size="small" @click="removeAnnotation(index)">
                    删除
                  </el-button>
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

<script setup name="EnhancedLineChart">
/* eslint-disable no-undef */
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  TrendCharts, Upload, Setting, Brush, Download, FullScreen,
  Document, ZoomIn, ZoomOut, RefreshLeft, ArrowLeft, ArrowRight,
  Reading, Coordinate, EditPen
} from '@element-plus/icons-vue'

import ChartToolbar from './ChartToolbar.vue'
import DataPreviewTable from './DataPreviewTable.vue'
import DataStatisticsPanel from './DataStatisticsPanel.vue'
import TrendAnalysisPanel from './TrendAnalysisPanel.vue'
import LineChart from './charts/LineChart.vue'
import { adaptForChart } from '../../utils/dataAdapter'
import { smartSample } from '../../utils/sampling'
import { linearRegression } from '../../utils/statistics'

const chartRef = ref(null)
const showDataPreview = ref(true)
const activeDataTab = ref('preview')
const leftPanelCollapsed = ref(false)
const rightPanelCollapsed = ref(false)
const isFullscreen = ref(false)
const showTemplateDialog = ref(false)
const showTrendLine = ref(false)
const showConfidenceInterval = ref(false)
const showOutliers = ref(false)
const showAnnotations = ref(false)
const trendType = ref('linear')
const movingWindow = ref(5)
const annotationText = ref('')
const annotations = ref([])
const trendResult = ref(null)

// 排序配置
const sortConfig = ref({
  sortBy: 'none'
})

// 数据
const rawData = ref([])
const fields = ref([])
const chartData = ref({ data: [], type: 'simple' })
const sampledData = ref([])

// 图表配置
const chartConfig = ref({
  type: 'line',
  xField: null,
  yField: null,
  groupField: null,
  title: '时间序列分析',
  xAxisLabel: 'X轴',
  yAxisLabel: 'Y轴',
  colorScheme: 'set1',
  lineStyle: 'solid',
  showDataPoints: true,
  smooth: false,
  showArea: false,
  showGrid: true,
  showLegend: true,
  xAxisType: 'value',
  lineWidth: 2
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
    id: 'time-series-basic',
    name: '时间序列基础',
    description: '标准时间序列图，包含数据点和趋势线',
    preview: '/api/placeholder/200/150',
    tags: ['时间序列', '趋势'],
    config: {
      showTrendLine: true,
      showDataPoints: true,
      smooth: false
    }
  },
  {
    id: 'multi-series',
    name: '多系列对比',
    description: '多组数据的时间序列对比图',
    preview: '/api/placeholder/200/150',
    tags: ['多系列', '对比'],
    config: {
      requireGroupField: true,
      showLegend: true,
      showDataPoints: true
    }
  },
  {
    id: 'area-chart',
    name: '面积图',
    description: '显示累积趋势的面积图',
    preview: '/api/placeholder/200/150',
    tags: ['面积图', '累积'],
    config: {
      showArea: true,
      opacity: 0.6,
      showDataPoints: false
    }
  },
  {
    id: 'smooth-curve',
    name: '平滑曲线',
    description: '用于连续数据的平滑曲线图',
    preview: '/api/placeholder/200/150',
    tags: ['平滑', '连续'],
    config: {
      smooth: true,
      showTrendLine: false,
      showDataPoints: true
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
const allFields = computed(() => fields.value)
const chartHeight = computed(() => isFullscreen.value ? window.innerHeight - 100 : 500)

// 方法
function onImported({ rows, columns }) {
  rawData.value = rows
  fields.value = columns

  // 自动选择字段
  if (allFields.value.length > 0) {
    chartConfig.value.xField = allFields.value[0].name
    chartConfig.value.xAxisLabel = allFields.value[0].name
  }
  if (numericFields.value.length > 0) {
    chartConfig.value.yField = numericFields.value[0].name
    chartConfig.value.yAxisLabel = numericFields.value[0].name
  }

  applyConfig()
  ElMessage.success(`成功导入 ${rows.length} 条数据`)
}

function applyConfig() {
  if (!hasData.value) return

  try {
    // 应用排序
    let processedData = [...rawData.value]
    applySorting()

    // 数据采样
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

    // 计算趋势分析
    if (showTrendLine.value && chartConfig.value.xField && chartConfig.value.yField) {
      calculateTrendAnalysis()
    }
  } catch (error) {
    ElMessage.error('配置应用失败: ' + error.message)
  }
}

function applySorting() {
  if (!hasData.value || !chartConfig.value.xField || !chartConfig.value.yField) return

  const { sortBy } = sortConfig.value

  if (sortBy === 'none') return

  rawData.value.sort((a, b) => {
    const aX = a[chartConfig.value.xField]
    const bX = b[chartConfig.value.xField]
    const aY = a[chartConfig.value.yField]
    const bY = b[chartConfig.value.yField]

    switch (sortBy) {
      case 'x-asc':
        return aX - bX
      case 'x-desc':
        return bX - aX
      case 'y-asc':
        return aY - bY
      case 'y-desc':
        return bY - aY
      default:
        return 0
    }
  })
}

function autoConfigureFields() {
  if (!hasData.value) {
    ElMessage.warning('请先导入数据')
    return
  }

  // 智能选择X轴字段（优先选择时间或有序字段）
  let xField = null
  if (allFields.value.length > 0) {
    // 优先选择包含时间相关字段的字段
    const timeFields = allFields.value.filter(f =>
      f.name.toLowerCase().includes('time') ||
      f.name.toLowerCase().includes('date') ||
      f.name.toLowerCase().includes('month') ||
      f.name.toLowerCase().includes('year')
    )

    if (timeFields.length > 0) {
      xField = timeFields[0].name
    } else {
      xField = allFields.value[0].name
    }
  }

  // 智能选择Y轴字段（优先选择数值字段）
  let yField = null
  if (numericFields.value.length > 0) {
    yField = numericFields.value[0].name
  } else if (allFields.value.length > 1) {
    yField = allFields.value[1].name
  }

  if (xField && yField) {
    chartConfig.value.xField = xField
    chartConfig.value.yField = yField
    chartConfig.value.xAxisLabel = xField
    chartConfig.value.yAxisLabel = yField

    // 如果有分组字段，自动设置
    if (categoricalFields.value.length > 0) {
      chartConfig.value.groupField = categoricalFields.value[0].name
    }
  }

  applyConfig()
  ElMessage.success('已智能配置字段')
}

function applyAcademicConfig() {
  applyConfig()
}

function calculateTrendAnalysis() {
  if (!chartConfig.value.xField || !chartConfig.value.yField || !sampledData.value.length) return

  const xData = sampledData.value.map(d => d[chartConfig.value.xField]).filter(v => v != null)
  const yData = sampledData.value.map(d => d[chartConfig.value.yField]).filter(v => v != null)

  if (xData.length !== yData.length || xData.length === 0) return

  try {
    const regression = linearRegression(xData, yData)

    // 判断趋势
    let trend = 'stable'
    if (Math.abs(regression.slope) > 0.001) {
      trend = regression.slope > 0 ? 'upward' : 'downward'
    }

    trendResult.value = {
      ...regression,
      trend,
      dataPoints: xData.length
    }
  } catch (error) {
    console.error('趋势分析失败:', error)
  }
}

function toggleTrendLine() {
  if (showTrendLine.value) {
    calculateTrendAnalysis()
  } else {
    trendResult.value = null
  }
  applyConfig()
}

function toggleConfidenceInterval() {
  applyConfig()
}

function toggleOutliers() {
  applyConfig()
}

function toggleAnnotations() {
  applyConfig()
}

function addAnnotation() {
  if (!annotationText.value.trim()) return

  annotations.value.push({
    text: annotationText.value,
    timestamp: Date.now()
  })

  annotationText.value = ''
  applyConfig()
}

function removeAnnotation(index) {
  annotations.value.splice(index, 1)
  applyConfig()
}

function zoomIn() {
  if (chartRef.value) {
    chartRef.value.zoomIn()
  }
}

function zoomOut() {
  if (chartRef.value) {
    chartRef.value.zoomOut()
  }
}

function resetZoom() {
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

    const link = document.createElement('a')
    link.download = `line_chart_${Date.now()}.png`
    link.href = dataURL
    link.click()

    ElMessage.success('图表已导出，可直接用于论文发表')
  }).catch(() => {
    // SVG导出
    const svgStr = chartRef.value.exportChart({ type: 'svg' })
    const blob = new Blob([svgStr], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.download = `line_chart_${Date.now()}.svg`
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

  // 应用模板配置
  Object.assign(chartConfig.value, template.config)

  if (template.config.requireGroupField && categoricalFields.value.length > 0) {
    chartConfig.value.groupField = categoricalFields.value[0].name
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
  applyConfig()
}

onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.enhanced-line-chart {
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

.trend-result {
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

.stat-value.upward {
  color: #67c23a;
}

.stat-value.downward {
  color: #f56c6c;
}

.annotation-list {
  max-height: 200px;
  overflow-y: auto;
}

.annotation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.annotation-item:last-child {
  border-bottom: none;
}

.annotation-text {
  flex: 1;
  font-size: 12px;
  color: #606266;
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