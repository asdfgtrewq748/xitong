<template>
  <div class="visualization-home">
    <!-- 顶部工具栏 -->
    <el-card shadow="never" class="top-toolbar">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 16px;">
          <h2 style="margin: 0;">科研绘图工作台</h2>
          <theme-selector @change="onThemeChange" />
        </div>
        <chart-toolbar 
          @imported="onImported" 
          @export="onExport"
          :has-data="hasData"
          :chart-ref="chartComponentRef"
        />
      </div>
    </el-card>

    <el-row :gutter="16" style="margin-top: 16px;">
      <!-- 左侧配置面板 -->
      <el-col :span="5">
        <el-card shadow="hover" style="height: calc(100vh - 180px); overflow-y: auto;">
          <h3>数据与基础配置</h3>
          <el-form label-position="top" :model="localConfig" size="small">
            <el-form-item label="图表类型">
              <el-select v-model="localConfig.type" placeholder="选择图表类型" @change="onTypeChange">
                <el-option label="散点图" value="scatter" />
                <el-option label="热力图" value="heatmap" />
                <el-option label="三维曲面" value="surface" />
                <el-option label="折线图" value="line" />
              </el-select>
            </el-form-item>

            <el-form-item label="X 字段">
              <el-select v-model="localConfig.xField" placeholder="选择 X 字段">
                <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name"/>
              </el-select>
            </el-form-item>

            <el-form-item label="Y 字段">
              <el-select v-model="localConfig.yField" placeholder="选择 Y 字段">
                <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name"/>
              </el-select>
            </el-form-item>

            <el-form-item v-if="localConfig.type === 'surface'" label="Z 字段">
              <el-select v-model="localConfig.zField" placeholder="选择 Z 字段">
                <el-option v-for="f in fields" :key="f.name" :label="f.name" :value="f.name"/>
              </el-select>
            </el-form-item>

            <el-form-item label="颜色方案">
              <el-select v-model="localConfig.colorScheme">
                <el-option label="viridis" value="viridis" />
                <el-option label="plasma" value="plasma" />
                <el-option label="coolwarm" value="coolwarm" />
                <el-option label="jet" value="jet" />
              </el-select>
            </el-form-item>

            <el-button type="primary" @click="applyConfig" :disabled="!hasData" block>
              应用配置
            </el-button>
          </el-form>

          <el-divider />
          
          <!-- 数据采样信息 -->
          <el-alert 
            v-if="samplingInfo.enabled"
            :title="`数据采样已启用: ${samplingInfo.method}`"
            :description="`原始 ${samplingInfo.original} 点 → 采样后 ${samplingInfo.sampled} 点 (${(samplingInfo.ratio * 100).toFixed(1)}%)`"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 12px;"
          />
        </el-card>
      </el-col>

      <!-- 中间图表区域 -->
      <el-col :span="14">
        <el-card shadow="hover" style="height: calc(100vh - 180px);">
          <div class="chart-area">
            <component 
              :is="currentChartComponent" 
              :data="chartData" 
              :config="chartConfig" 
              ref="chartComponentRef"
            />
          </div>
        </el-card>

        <!-- 数据预览表格 -->
        <el-card shadow="never" style="margin-top: 12px;" v-if="showDataPreview && hasData">
          <data-preview-table 
            :data="previewData" 
            :columns="fields.map(f => f.name)" 
            :height="250"
          />
        </el-card>

        <!-- 示例画廊 -->
        <el-card shadow="never" style="margin-top: 12px;" v-if="!hasData">
          <chart-gallery @load-sample="onLoadSample" />
        </el-card>
      </el-col>

      <!-- 右侧高级设置面板 -->
      <el-col :span="5">
        <el-card shadow="hover" style="height: calc(100vh - 180px); overflow-y: auto;">
          <chart-settings-panel 
            :config="localConfig" 
            :chart-type="localConfig.type"
            @apply="onSettingsApply"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import ChartToolbar from './ChartToolbar.vue'
import ChartGallery from './ChartGallery.vue'
import ChartSettingsPanel from './ChartSettingsPanel.vue'
import DataPreviewTable from './DataPreviewTable.vue'
import ThemeSelector from './ThemeSelector.vue'
import ScatterPlot from './charts/ScatterPlot.vue'
import HeatMap from './charts/HeatMap.vue'
import Surface3D from './charts/Surface3D.vue'
import LineChart from './charts/LineChart.vue'
import { useVisualizationStore } from '../../stores/visualizationStore'
import { adaptForChart } from '../../utils/dataAdapter'
import { smartSample, getSamplingRecommendation } from '../../utils/sampling'

const store = useVisualizationStore()
const chartComponentRef = ref(null)

const localConfig = reactive({
  type: 'scatter',
  xField: null,
  yField: null,
  zField: null,
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

const fields = ref([])
const chartData = ref({ data: [], type: 'simple' })
const previewData = ref([])
const showDataPreview = ref(true)
const samplingInfo = ref({ enabled: false, method: 'none', original: 0, sampled: 0, ratio: 1 })

const hasData = computed(() => chartData.value.data && (Array.isArray(chartData.value.data) ? chartData.value.data.length > 0 : Object.keys(chartData.value.data).length > 0))

const currentChartComponent = computed(() => {
  switch (localConfig.type) {
    case 'heatmap': return HeatMap
    case 'surface': return Surface3D
    case 'line': return LineChart
    default: return ScatterPlot
  }
})

const chartConfig = localConfig

function onImported({ rows, columns, datasetId }) {
  try {
    // 设置到 store
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
    
    // 自动适配当前配置为图表数据
    const adapted = adaptForChart(processedData, columns, localConfig)
    chartData.value = adapted
    
    ElMessage.success(`成功导入 ${rows.length} 条数据${samplingInfo.value.enabled ? `（采样显示${processedData.length}点）` : ''}`)
  } catch (error) {
    ElMessage.error('数据导入失败: ' + error.message)
  }
}

function onExport(type) {
  // 导出功能委托给 ChartToolbar，它会调用 chartComponentRef 的导出方法
  ElMessage.info(`正在导出 ${type.toUpperCase()}...`)
}

function onTypeChange() {
  if (hasData.value && store.currentDataset) {
    // 类型变化时自动重新适配数据
    applyConfig()
  }
}

function applyConfig() {
  // 生成 chartData
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
    ElMessage.success('配置已应用')
  } catch (error) {
    ElMessage.error('应用配置失败: ' + error.message)
  }
}

function onLoadSample({ rows, columns, type }) {
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

function onSettingsApply({ config, sampling }) {
  // 应用高级设置
  Object.assign(localConfig, config)
  
  if (sampling && sampling.enabled !== samplingInfo.value.enabled) {
    if (sampling.enabled && previewData.value.length > sampling.maxPoints) {
      const result = smartSample(previewData.value, {
        maxPoints: sampling.maxPoints,
        method: 'auto'
      })
      samplingInfo.value = {
        enabled: true,
        method: result.info.method,
        original: result.info.original,
        sampled: result.info.sampled,
        ratio: parseFloat(result.info.ratio)
      }
    } else {
      samplingInfo.value = { enabled: false, method: 'none', original: previewData.value.length, sampled: previewData.value.length, ratio: 1 }
    }
  }
  
  applyConfig()
  ElMessage.success('高级设置已应用')
}

function onThemeChange(theme) {
  localConfig.theme = theme
  if (hasData.value) {
    applyConfig()
  }
  ElMessage.success(`主题已切换至: ${theme}`)
}
</script>

<style scoped>
.visualization-home {
  min-height: 100%;
  padding: 16px;
}

.top-toolbar {
  margin-bottom: 0;
}

.chart-area {
  min-height: calc(100vh - 240px);
  position: relative;
}

h2 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.el-form {
  margin-top: 12px;
}

:deep(.el-card__body) {
  padding: 16px;
}

:deep(.el-select) {
  width: 100%;
}
</style>
