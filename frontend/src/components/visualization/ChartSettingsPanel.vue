<template>
  <div class="chart-settings-panel">
    <el-collapse v-model="activeNames" accordion>
      <!-- 基础设置 -->
      <el-collapse-item title="📊 基础设置" name="basic">
        <el-form label-position="top" size="small">
          <el-form-item label="图表标题">
            <el-input v-model="localConfig.title" placeholder="输入图表标题" />
          </el-form-item>
          
          <el-form-item label="X轴标签">
            <el-input v-model="localConfig.xAxisLabel" placeholder="X轴标签" />
          </el-form-item>
          
          <el-form-item label="Y轴标签">
            <el-input v-model="localConfig.yAxisLabel" placeholder="Y轴标签" />
          </el-form-item>
          
          <el-form-item v-if="showZAxis" label="Z轴标签">
            <el-input v-model="localConfig.zAxisLabel" placeholder="Z轴标签" />
          </el-form-item>
        </el-form>
      </el-collapse-item>

      <!-- 样式设置 -->
      <el-collapse-item title="🎨 样式设置" name="style">
        <el-form label-position="top" size="small">
          <el-form-item label="主题">
            <el-radio-group v-model="localConfig.theme">
              <el-radio-button value="light">浅色</el-radio-button>
              <el-radio-button value="dark">深色</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="颜色方案">
            <el-select v-model="localConfig.colorScheme" style="width: 100%">
              <el-option label="viridis" value="viridis" />
              <el-option label="plasma" value="plasma" />
              <el-option label="coolwarm" value="coolwarm" />
              <el-option label="jet" value="jet" />
              <el-option label="rainbow" value="rainbow" />
              <el-option label="blues" value="blues" />
              <el-option label="reds" value="reds" />
            </el-select>
          </el-form-item>
          
          <el-form-item v-if="showPointSize" label="点大小">
            <el-slider v-model="localConfig.pointSize" :min="2" :max="20" />
          </el-form-item>
          
          <el-form-item v-if="showLineWidth" label="线宽">
            <el-slider v-model="localConfig.lineWidth" :min="1" :max="5" />
          </el-form-item>
          
          <el-form-item label="透明度">
            <el-slider v-model="localConfig.opacity" :min="0.1" :max="1" :step="0.1" />
          </el-form-item>
        </el-form>
      </el-collapse-item>

      <!-- 显示设置 -->
      <el-collapse-item title="👁️ 显示设置" name="display">
        <el-form label-position="top" size="small">
          <el-form-item>
            <el-checkbox v-model="localConfig.showLegend">显示图例</el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="localConfig.showGrid">显示网格</el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="enableSampling">启用数据采样（大数据集优化）</el-checkbox>
          </el-form-item>
          
          <el-form-item v-if="enableSampling" label="最大点数">
            <el-input-number 
              v-model="maxSamplePoints" 
              :min="1000" 
              :max="50000" 
              :step="1000"
              style="width: 100%"
            />
          </el-form-item>
        </el-form>
      </el-collapse-item>
    </el-collapse>
    
    <div class="actions">
      <el-button type="primary" @click="handleApply" style="width: 100%">
        <el-icon><Check /></el-icon>
        应用设置
      </el-button>
      <el-button @click="handleReset" style="width: 100%; margin-top: 8px;">
        <el-icon><RefreshRight /></el-icon>
        重置默认
      </el-button>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, computed, watch } from 'vue'
import { Check, RefreshRight } from '@element-plus/icons-vue'

const props = defineProps({
  config: { type: Object, required: true },
  chartType: { type: String, default: 'scatter' }
})

const emit = defineEmits(['update', 'apply'])

const activeNames = ref('basic')
const localConfig = ref({ ...props.config })
const enableSampling = ref(false)
const maxSamplePoints = ref(10000)

const showZAxis = computed(() => props.chartType === 'surface')
const showPointSize = computed(() => ['scatter', 'bubble'].includes(props.chartType))
const showLineWidth = computed(() => ['line', 'area'].includes(props.chartType))

watch(() => props.config, (newConfig) => {
  localConfig.value = { ...newConfig }
}, { deep: true })

function handleApply() {
  emit('apply', {
    config: localConfig.value,
    sampling: {
      enabled: enableSampling.value,
      maxPoints: maxSamplePoints.value
    }
  })
}

function handleReset() {
  localConfig.value = {
    type: props.chartType,
    xField: null,
    yField: null,
    zField: null,
    colorField: null,
    sizeField: null,
    groupField: null,
    title: '科研图表',
    xAxisLabel: 'X轴',
    yAxisLabel: 'Y轴',
    zAxisLabel: 'Z轴',
    showLegend: true,
    showGrid: true,
    colorScheme: 'viridis',
    pointSize: 8,
    lineWidth: 2,
    opacity: 0.8,
    theme: 'light'
  }
  enableSampling.value = false
  maxSamplePoints.value = 10000
  emit('apply', { config: localConfig.value, sampling: { enabled: false } })
}
</script>

<style scoped>
.chart-settings-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.el-collapse {
  flex: 1;
  overflow-y: auto;
  border: none;
}

:deep(.el-collapse-item__header) {
  font-weight: 600;
  padding-left: 8px;
}

:deep(.el-collapse-item__content) {
  padding: 12px 8px;
}

.actions {
  padding: 12px;
  border-top: 1px solid #e4e7ed;
  background: #f5f7fa;
}

.el-form-item {
  margin-bottom: 16px;
}
</style>
