<template>
  <div class="chart-page modern-layout">
    <div class="page-header modern">
      <div class="title-group">
        <h2><el-icon><PieChart /></el-icon> 3D曲面图</h2>
        <p class="subtitle">三维数据空间可视化</p>
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
                <el-form-item label="X 轴字段">
                  <el-select v-model="config.xField" @change="updateChart">
                    <el-option v-for="f in numericFields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Y 轴字段">
                  <el-select v-model="config.yField" @change="updateChart">
                    <el-option v-for="f in numericFields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Z 轴字段">
                  <el-select v-model="config.zField" @change="updateChart">
                    <el-option v-for="f in numericFields" :key="f.name" :label="f.name" :value="f.name" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-collapse-item>

            <el-collapse-item title="高级选项" name="advanced">
              <el-form label-position="top" size="small" class="compact-form">
                <el-divider content-position="left">基础设置</el-divider>
                <el-form-item label="图表标题">
                  <el-input v-model="config.title" placeholder="3D曲面图" @change="updateChart" />
                </el-form-item>
                <el-form-item label="X轴标签">
                  <el-input v-model="config.xAxisLabel" @change="updateChart" />
                </el-form-item>
                <el-form-item label="Y轴标签">
                  <el-input v-model="config.yAxisLabel" @change="updateChart" />
                </el-form-item>
                <el-form-item label="Z轴标签">
                  <el-input v-model="config.zAxisLabel" @change="updateChart" />
                </el-form-item>

                <el-divider content-position="left">3D视角</el-divider>
                <el-form-item label="视角角度">
                  <el-slider v-model="config.viewAngle" :min="0" :max="360" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item label="俯仰角度">
                  <el-slider v-model="config.pitchAngle" :min="-90" :max="90" show-input @change="updateChart" />
                </el-form-item>

                <el-divider content-position="left">曲面样式</el-divider>
                <el-form-item label="配色方案">
                  <el-select v-model="config.colorScheme" @change="updateChart">
                    <el-option label="彩虹色" value="rainbow" />
                    <el-option label="热力" value="hot" />
                    <el-option label="冷色调" value="cool" />
                    <el-option label="地形" value="terrain" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.showWireframe" active-text="显示线框" @change="updateChart" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.grid3D" active-text="显示3D网格" @change="updateChart" />
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
              <el-icon class="card-icon"><Document /></el-icon>
              <div class="card-info">
                <div class="card-value">{{ totalRecords }}</div>
                <div class="card-label">数据点</div>
              </div>
            </div>
          </el-card>
          <el-card shadow="hover" class="summary-card">
            <div class="card-content">
              <el-icon class="card-icon"><DataLine /></el-icon>
              <div class="card-info">
                <div class="card-value">{{ xyzRange.x }}</div>
                <div class="card-label">X范围</div>
              </div>
            </div>
          </el-card>
          <el-card shadow="hover" class="summary-card">
            <div class="card-content">
              <el-icon class="card-icon"><DataLine /></el-icon>
              <div class="card-info">
                <div class="card-value">{{ xyzRange.z }}</div>
                <div class="card-label">Z范围</div>
              </div>
            </div>
          </el-card>
        </div>

        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>3D曲面视图</span>
              <el-button-group size="small">
                <el-button @click="resetView"><el-icon><RefreshLeft /></el-icon></el-button>
              </el-button-group>
            </div>
          </template>
          <div class="chart-wrapper">
            <el-empty v-if="!hasData" description="请导入数据开始分析" :image-size="120" />
            <Surface3D v-else ref="chartRef" :data="chartData" :config="fullChartConfig" :height="560" />
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
import { PieChart, QuestionFilled, RefreshLeft, DataLine, Document } from '@element-plus/icons-vue'
import ChartToolbar from '../ChartToolbar.vue'
import HelpDialog from '../HelpDialog.vue'
import Surface3D from '../charts/Surface3D.vue'
import { useVisualizationStore } from '../../../stores/visualizationStore'
import { adaptForChart } from '../../../utils/dataAdapter'

const store = useVisualizationStore()
const chartRef = ref(null)
const showHelp = ref(false)

const config = reactive({
  type: 'surface',
  xField: null,
  yField: null,
  zField: null,
  title: '3D曲面图',
  xAxisLabel: 'X轴',
  yAxisLabel: 'Y轴',
  zAxisLabel: 'Z轴',
  colorScheme: 'rainbow',
  viewAngle: 45,
  pitchAngle: 30,
  showWireframe: false,
  grid3D: true,
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
    // 确保三个字段各不相同
    if (numFields.length >= 1) config.xField = numFields[0].name
    if (numFields.length >= 2) {
      const differentField = numFields.find(f => f.name !== config.xField)
      config.yField = differentField ? differentField.name : (numFields.length > 1 ? numFields[1].name : numFields[0].name)
    }
    if (numFields.length >= 3) {
      const differentField = numFields.find(f => f.name !== config.xField && f.name !== config.yField)
      config.zField = differentField ? differentField.name : (numFields.length > 2 ? numFields[2].name : numFields[0].name)
    }
    
    updateChart()
    ElMessage.success(`成功导入 ${rows.length} 条数据`)
  } catch (error) {
    ElMessage.error('数据导入失败: ' + error.message)
  }
}

const updateChart = () => {
  if (!store.currentDataset || !config.xField || !config.yField || !config.zField) return
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

// 统计计算
const totalRecords = computed(() => previewData.value.length)

const xyzRange = computed(() => {
  if (!previewData.value.length) return { x: '-', y: '-', z: '-' }
  try {
    const xValues = previewData.value.map(r => r[config.xField]).filter(v => typeof v === 'number')
    const yValues = previewData.value.map(r => r[config.yField]).filter(v => typeof v === 'number')
    const zValues = previewData.value.map(r => r[config.zField]).filter(v => typeof v === 'number')
    return {
      x: xValues.length ? `${Math.min(...xValues).toFixed(1)}~${Math.max(...xValues).toFixed(1)}` : '-',
      y: yValues.length ? `${Math.min(...yValues).toFixed(1)}~${Math.max(...yValues).toFixed(1)}` : '-',
      z: zValues.length ? `${Math.min(...zValues).toFixed(1)}~${Math.max(...zValues).toFixed(1)}` : '-'
    }
  } catch (e) {
    return { x: '-', y: '-', z: '-' }
  }
})
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
.summary-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
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
