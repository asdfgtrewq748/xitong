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
                    <el-option label="Jet (Matplotlib)" value="jet" />
                    <el-option label="Seismic" value="seismic" />
                    <el-option label="黄橙红" value="YlOrRd" />
                    <el-option label="红黄蓝" value="RdYlBu" />
                    <el-option label="光谱" value="Spectral" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.showWireframe" active-text="显示线框" @change="updateChart" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="config.grid3D" active-text="显示3D网格" @change="updateChart" />
                </el-form-item>

                <el-divider content-position="left">渲染与采样</el-divider>
                <el-form-item label="平滑 (高斯 σ)">
                  <el-slider v-model="config.smoothingSigma" :min="0" :max="5" :step="0.1" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item label="网格分辨率 (每轴点数)">
                  <el-slider v-model="config.resolution" :min="20" :max="200" :step="10" show-input @change="updateChart" />
                  <div style="font-size:12px;color:#909399;margin-top:6px">设置空为使用原始数据分辨率</div>
                </el-form-item>

                <el-divider content-position="left">色条设置</el-divider>
                <el-form-item>
                  <el-switch v-model="config.showColorBar" active-text="显示色条" @change="updateChart" />
                </el-form-item>
                <el-form-item label="色条位置">
                  <el-select v-model="config.colorBarPosition" @change="updateChart">
                    <el-option label="右侧" value="right" />
                    <el-option label="左侧" value="left" />
                    <el-option label="底部" value="bottom" />
                  </el-select>
                </el-form-item>
                <el-form-item label="色条缩放">
                  <el-slider v-model="config.colorBarShrink" :min="0.3" :max="1" :step="0.1" show-input @change="updateChart" />
                </el-form-item>
                <el-form-item label="色条标签">
                  <el-input v-model="config.colorBarLabel" placeholder="数值" @change="updateChart" />
                </el-form-item>

                <el-divider content-position="left">导出设置</el-divider>
                <el-form-item label="导出质量 (pixelRatio)">
                  <el-slider v-model="config.exportPixelRatio" :min="1" :max="4" :step="0.5" show-input />
                  <div style="font-size:12px;color:#909399;margin-top:6px">2 对应 DPI 150, 4 对应 DPI 300</div>
                </el-form-item>

                <el-divider content-position="left">字体设置</el-divider>
                <el-form-item label="标题字号">
                  <el-slider v-model="config.titleFontSize" :min="12" :max="32" show-input @change="updateChart" />
                </el-form-item>

                <el-divider content-position="left">视角预设</el-divider>
                <el-form-item label="快速切换">
                  <div style="display:flex;flex-wrap:wrap;gap:8px;">
                    <el-button size="small" @click="applyViewPreset(20, 45)">视角1</el-button>
                    <el-button size="small" @click="applyViewPreset(30, 60)">视角2</el-button>
                    <el-button size="small" @click="applyViewPreset(40, 90)">视角3</el-button>
                    <el-button size="small" @click="applyViewPreset(20, 120)">视角4</el-button>
                    <el-button size="small" @click="applyViewPreset(60, 45)">视角5</el-button>
                  </div>
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
                <el-button @click="exportMultiAngles" title="导出多角度 PNG"><el-icon><Document /></el-icon></el-button>
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
  // 高级渲染参数
  smoothingSigma: 0,
  resolution: null,
  // 色条设置
  showColorBar: true,
  colorBarPosition: 'right',
  colorBarShrink: 0.8,
  colorBarLabel: '数值',
  // 导出设置
  exportPixelRatio: 2,
  backgroundColor: 'transparent',
  fontFamily: 'SimSun, "Times New Roman", serif',
  titleFontSize: 18
  ,
  // 是否对坐标进行归一化（将模型边界映射到 0 起点并缩放到 [0,1]）
  normalizeCoordinates: true
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

// 导出多角度图片（默认四个方位）
const downloadDataUrl = (dataUrl, filename) => {
  const a = document.createElement('a')
  a.href = dataUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
}

// 快速应用视角预设
const applyViewPreset = (pitch, angle) => {
  config.pitchAngle = pitch
  config.viewAngle = angle
  updateChart()
  ElMessage.success(`已切换到视角: 俯仰=${pitch}°, 方位=${angle}°`)
}

const exportMultiAngles = async () => {
  if (!chartRef.value) {
    ElMessage.error('图表未初始化')
    return
  }
  const instance = chartRef.value.getChartInstance()
  if (!instance) {
    ElMessage.error('无法获取图表实例')
    return
  }

  // 使用 sanweiyuntu.py 中的 5 个预设角度
  const angles = [
    { elev: 20, azim: 45 },
    { elev: 30, azim: 60 },
    { elev: 40, azim: 90 },
    { elev: 20, azim: 120 },
    { elev: 60, azim: 45 }
  ]
  const original = { alpha: config.pitchAngle, beta: config.viewAngle }
  try {
    for (let i = 0; i < angles.length; i++) {
      const { elev, azim } = angles[i]
      instance.setOption({ grid3D: { viewControl: { alpha: elev, beta: azim } } })
      // 等待渲染稳定
      await new Promise(r => setTimeout(r, 300))
      const dataUrl = chartRef.value.exportChart({ pixelRatio: config.exportPixelRatio })
      const safeTitle = (config.title || 'surface').replace(/\s+/g, '_')
      downloadDataUrl(dataUrl, `${safeTitle}_view${i+1}_elev${elev}_azim${azim}.png`)
    }
    ElMessage.success('多角度导出完成（5个预设视角）')
  } catch (e) {
    ElMessage.error('导出失败: ' + (e?.message || e))
  } finally {
    // 恢复视角
    instance.setOption({ grid3D: { viewControl: { alpha: original.alpha, beta: original.beta } } })
  }
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
