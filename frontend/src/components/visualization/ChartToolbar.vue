<template>
  <div class="chart-toolbar">
    <input ref="fileInput" type="file" accept=".csv,.json" style="display:none" @change="onFileChange" />
    <el-button type="primary" size="small" @click="triggerFileInput">
      <el-icon><Upload /></el-icon>
      导入数据
    </el-button>
    
    <el-dropdown @command="handleExport" :disabled="!hasData">
      <el-button type="success" size="small" :disabled="!hasData">
        <el-icon><Download /></el-icon>
        导出
        <el-icon class="el-icon--right"><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <!-- 科研级图像导出 -->
          <el-dropdown-item divided command="png_high">
            <el-icon><Picture /></el-icon>
            PNG (300 DPI) - 高质量
          </el-dropdown-item>
          <el-dropdown-item command="png_print">
            <el-icon><Picture /></el-icon>
            PNG (600 DPI) - 出版级
          </el-dropdown-item>
          <el-dropdown-item command="svg">
            <el-icon><Picture /></el-icon>
            SVG 矢量图
          </el-dropdown-item>
          <el-dropdown-item command="pdf">
            <el-icon><Document /></el-icon>
            PDF 学术版
          </el-dropdown-item>
          <el-dropdown-item command="tiff">
            <el-icon><Picture /></el-icon>
            TIFF (期刊专用)
          </el-dropdown-item>

          <!-- 数据导出 -->
          <el-dropdown-item divided command="csv">
            <el-icon><Document /></el-icon>
            导出为 CSV 数据
          </el-dropdown-item>
          <el-dropdown-item command="xlsx">
            <el-icon><Document /></el-icon>
            导出为 Excel
          </el-dropdown-item>

          <!-- 期刊格式快速导出 -->
          <el-dropdown-item divided command="nature">
            <el-icon><Star /></el-icon>
            Nature 期刊格式
          </el-dropdown-item>
          <el-dropdown-item command="science">
            <el-icon><Star /></el-icon>
            Science 期刊格式
          </el-dropdown-item>
          <el-dropdown-item command="ieee">
            <el-icon><Star /></el-icon>
            IEEE 期刊格式
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
    
    <el-button type="warning" size="small" @click="onClear">
      <el-icon><Delete /></el-icon>
      清空
    </el-button>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Download, ArrowDown, Picture, Document, Delete, Star } from '@element-plus/icons-vue'
import { useVisualizationStore } from '../../stores/visualizationStore'
import { parseCSV, parseJSON } from '../../utils/dataAdapter'
import {
  exportChartAsPNG,
  exportChartAsSVG,
  exportChartAsPDF,
  exportChartAsTIFF,
  exportDataAsCSV,
  exportDataAsExcel,
  exportForJournal,
  generateFilename
} from '../../utils/exportHelpers'

const props = defineProps({
  hasData: { type: Boolean, default: false },
  chartRef: { type: Object, default: null }
})

const emit = defineEmits(['imported','export'])
const store = useVisualizationStore()
const fileInput = ref(null)

function triggerFileInput() {
  fileInput.value && fileInput.value.click()
}

async function onFileChange(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  
  try {
    const text = await file.text()
    if (file.name.toLowerCase().endsWith('.csv')) {
      const result = await parseCSV(text)
      const id = store.importDataset({ name: file.name, rawData: text, source: 'upload', fileType: 'csv' })
      store.setParsedData(id, result.rows, result.columns)
      emit('imported', { rows: result.rows, columns: result.columns, datasetId: id })
      ElMessage.success(`成功导入 ${result.rows.length} 条数据`)
    } else if (file.name.toLowerCase().endsWith('.json')) {
      const result = parseJSON(text)
      const id = store.importDataset({ name: file.name, rawData: text, source: 'upload', fileType: 'json' })
      store.setParsedData(id, result.rows, result.columns)
      emit('imported', { rows: result.rows, columns: result.columns, datasetId: id })
      ElMessage.success(`成功导入 ${result.rows.length} 条数据`)
    }
  } catch (err) {
    console.error('导入失败', err)
    ElMessage.error('导入失败: ' + err.message)
  } finally {
    // 清空输入，便于重复选择同一文件
    e.target.value = null
  }
}

async function handleExport(command) {
  if (!props.hasData) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  // 获取图表实例
  const chartComponent = props.chartRef
  if (!chartComponent || !chartComponent.getChartInstance) {
    ElMessage.warning('图表组件未就绪')
    return
  }

  const chartInstance = chartComponent.getChartInstance()
  if (!chartInstance) {
    ElMessage.warning('图表实例未初始化')
    return
  }

  try {
    store.startExport()

    switch (command) {
      case 'png_high':
        await exportChartAsPNG(chartInstance, {
          filename: generateFilename('chart', 'high_quality'),
          quality: 'high'
        })
        ElMessage.success('导出高质量 PNG 成功 (300 DPI)')
        break

      case 'png_print':
        await exportChartAsPNG(chartInstance, {
          filename: generateFilename('chart', 'print_quality'),
          quality: 'print'
        })
        ElMessage.success('导出出版级 PNG 成功 (600 DPI)')
        break

      case 'svg':
        await exportChartAsSVG(chartInstance, {
          filename: generateFilename('chart', 'vector')
        })
        ElMessage.success('导出 SVG 矢量图成功')
        break

      case 'pdf':
        await exportChartAsPDF(chartInstance, {
          filename: generateFilename('chart', 'academic')
        })
        ElMessage.success('导出 PDF 学术版成功')
        break

      case 'tiff':
        await exportChartAsTIFF(chartInstance, {
          filename: generateFilename('chart', 'journal')
        })
        ElMessage.success('导出 TIFF 期刊格式成功')
        break

      case 'csv':
        {
          const dataset = store.currentDataset
          if (!dataset || !dataset.parsedData) {
            throw new Error('没有可导出的数据')
          }
          await exportDataAsCSV(dataset.parsedData, {
            filename: generateFilename('data', 'csv')
          })
          ElMessage.success('导出 CSV 数据成功')
        }
        break

      case 'xlsx':
        {
          const dataset = store.currentDataset
          if (!dataset || !dataset.parsedData) {
            throw new Error('没有可导出的数据')
          }
          await exportDataAsExcel(dataset.parsedData, {
            filename: generateFilename('data', 'xlsx'),
            sheetName: '数据表'
          })
          ElMessage.success('导出 Excel 数据成功')
        }
        break

      // 期刊格式快速导出
      case 'nature':
        await exportForJournal(chartInstance, 'nature', {
          filename: generateFilename('chart', 'nature_journal')
        })
        ElMessage.success('导出 Nature 期刊格式成功')
        break

      case 'science':
        await exportForJournal(chartInstance, 'science', {
          filename: generateFilename('chart', 'science_journal')
        })
        ElMessage.success('导出 Science 期刊格式成功')
        break

      case 'ieee':
        await exportForJournal(chartInstance, 'ieee', {
          filename: generateFilename('chart', 'ieee_journal')
        })
        ElMessage.success('导出 IEEE 期刊格式成功')
        break

      default:
        ElMessage.warning('暂不支持该导出格式')
        return
    }

    emit('export', { format: command, success: true })
  } catch (error) {
    console.error('导出失败', error)
    store.failExport(error.message)
    ElMessage.error('导出失败: ' + error.message)
    emit('export', { format: command, success: false, error: error.message })
  }
}

function onClear() {
  store.clearAllDatasets()
  emit('imported', { rows: [], columns: [], datasetId: null })
  ElMessage.info('数据已清空')
}
</script>

<style scoped>
.chart-toolbar {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.el-button {
  flex-shrink: 0;
}
</style>
