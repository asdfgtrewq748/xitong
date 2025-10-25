<template>
  <div class="chart-gallery">
    <h4>示例图表</h4>
    <el-row :gutter="12">
      <el-col :span="6">
        <el-card shadow="hover" class="sample-card" @click="loadSample('scatter')">
          <el-icon class="sample-icon"><ScatterChart /></el-icon>
          <div class="sample-title">散点图示例</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="sample-card" @click="loadSample('heatmap')">
          <el-icon class="sample-icon"><Grid /></el-icon>
          <div class="sample-title">热力图示例</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="sample-card" @click="loadSample('surface')">
          <el-icon class="sample-icon"><Histogram /></el-icon>
          <div class="sample-title">三维曲面示例</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="sample-card" @click="loadSample('line')">
          <el-icon class="sample-icon"><TrendCharts /></el-icon>
          <div class="sample-title">折线图示例</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ElMessage } from 'element-plus'
import { ScatterChart, Grid, Histogram, TrendCharts } from '@element-plus/icons-vue'
import { useVisualizationStore } from '../../stores/visualizationStore'
import { parseCSV } from '../../utils/dataAdapter'

const emit = defineEmits(['load-sample'])
const store = useVisualizationStore()

async function loadSample(type) {
  try {
    let path = null
    switch (type) {
      case 'scatter': 
      case 'heatmap': 
        path = '/data/examples/scatter_sample.csv'
        break
      case 'surface': 
        path = '/data/examples/surface_sample.csv'
        break
      case 'line': 
        path = '/data/examples/line_sample.csv'
        break
    }
    
    if (!path) return
    
    const res = await fetch(path)
    if (!res.ok) throw new Error('示例文件加载失败')
    
    const text = await res.text()
    const parsed = await parseCSV(text)
    
    const id = store.importDataset({ 
      name: `sample-${type}`, 
      rawData: text, 
      source: 'sample', 
      fileType: 'csv' 
    })
    store.setParsedData(id, parsed.rows, parsed.columns)
    
    // 通知父组件
    emit('load-sample', { 
      rows: parsed.rows, 
      columns: parsed.columns, 
      type 
    })
    
    ElMessage.success(`${type} 示例加载成功`)
  } catch (err) {
    console.error('加载示例失败', err)
    ElMessage.error('加载示例失败: ' + err.message)
  }
}
</script>

<style scoped>
.chart-gallery {
  padding: 12px 0;
}

h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.sample-card {
  cursor: pointer;
  text-align: center;
  padding: 20px 12px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.sample-card:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transform: translateY(-2px);
}

.sample-icon {
  font-size: 32px;
  color: #409EFF;
  margin-bottom: 8px;
}

.sample-title {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}
</style>