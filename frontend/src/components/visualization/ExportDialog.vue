<template>
  <el-dialog
    v-model="visible"
    title="导出图表"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="export-dialog">
      <!-- 格式选择 -->
      <el-form :model="form" label-width="100px" size="default">
        <el-form-item label="导出格式">
          <el-radio-group v-model="form.format">
            <el-radio-button value="png">PNG</el-radio-button>
            <el-radio-button value="svg">SVG</el-radio-button>
            <el-radio-button value="jpg">JPG</el-radio-button>
          </el-radio-group>
          <div class="format-hint">
            <span v-if="form.format === 'png'">推荐：适合印刷和网络，支持透明背景</span>
            <span v-if="form.format === 'svg'">推荐：矢量格式，无损缩放，适合编辑</span>
            <span v-if="form.format === 'jpg'">网络用：文件较小，不支持透明</span>
          </div>
        </el-form-item>

        <!-- 质量预设 -->
        <el-form-item label="质量预设">
          <el-select v-model="form.preset" placeholder="选择预设" @change="handlePresetChange">
            <el-option label="印刷质量 (300 DPI)" value="printQuality" />
            <el-option label="高分辨率 (600 DPI)" value="highRes" />
            <el-option label="演示用 (150 DPI)" value="presentation" />
            <el-option label="网页用 (72 DPI)" value="webQuality" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>

        <!-- 期刊标准尺寸 -->
        <el-form-item label="期刊标准">
          <el-select v-model="form.journalPreset" placeholder="选择期刊" @change="handleJournalChange">
            <el-option label="Nature - 单栏 (89mm)" value="nature-single" />
            <el-option label="Nature - 双栏 (183mm)" value="nature-double" />
            <el-option label="Science - 单栏 (90mm)" value="science-single" />
            <el-option label="Science - 双栏 (180mm)" value="science-double" />
            <el-option label="PNAS - 单栏 (87mm)" value="pnas-single" />
            <el-option label="PNAS - 双栏 (178mm)" value="pnas-double" />
            <el-option label="自定义尺寸" value="custom" />
          </el-select>
        </el-form-item>

        <!-- 自定义尺寸 -->
        <el-form-item label="图表尺寸" v-if="form.preset === 'custom' || form.journalPreset === 'custom'">
          <el-row :gutter="10">
            <el-col :span="8">
              <el-input v-model.number="form.width" placeholder="宽度">
                <template #append>px</template>
              </el-input>
            </el-col>
            <el-col :span="8">
              <el-input v-model.number="form.height" placeholder="高度">
                <template #append>px</template>
              </el-input>
            </el-col>
            <el-col :span="8">
              <el-input v-model.number="form.dpi" placeholder="DPI">
                <template #append>DPI</template>
              </el-input>
            </el-col>
          </el-row>
          <div class="size-hint">
            当前：{{ form.width }}×{{ form.height }}px @ {{ form.dpi }} DPI
            <span v-if="form.dpi >= 300" style="color: #67c23a">（印刷级）</span>
          </div>
        </el-form-item>

        <!-- 背景色 -->
        <el-form-item label="背景颜色">
          <el-radio-group v-model="form.backgroundColor">
            <el-radio-button value="#ffffff">白色</el-radio-button>
            <el-radio-button value="transparent">透明</el-radio-button>
            <el-radio-button value="#f5f5f5">浅灰</el-radio-button>
            <el-radio-button value="custom">自定义</el-radio-button>
          </el-radio-group>
          <el-color-picker 
            v-if="form.backgroundColor === 'custom'" 
            v-model="form.customBgColor" 
            show-alpha
            style="margin-left: 10px"
          />
        </el-form-item>

        <!-- 文件名 -->
        <el-form-item label="文件名">
          <el-input v-model="form.filename" placeholder="输入文件名（不含扩展名）">
            <template #append>.{{ form.format }}</template>
          </el-input>
        </el-form-item>

        <!-- 预览信息 -->
        <el-form-item label="导出信息">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="格式">{{ form.format.toUpperCase() }}</el-descriptions-item>
            <el-descriptions-item label="DPI">{{ form.dpi }}</el-descriptions-item>
            <el-descriptions-item label="尺寸">{{ form.width }} × {{ form.height }} px</el-descriptions-item>
            <el-descriptions-item label="物理尺寸">
              {{ (form.width / form.dpi * 25.4).toFixed(1) }} × {{ (form.height / form.dpi * 25.4).toFixed(1) }} mm
            </el-descriptions-item>
          </el-descriptions>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleExport" :loading="exporting">
        <el-icon v-if="!exporting"><Download /></el-icon>
        {{ exporting ? '导出中...' : '导出' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { ChartExporter, JournalDimensions } from '@/utils/chartExporter'

const props = defineProps({
  modelValue: Boolean,
  chartInstance: Object
})

const emit = defineEmits(['update:modelValue', 'export-success'])

const visible = ref(props.modelValue)
const exporting = ref(false)

const form = reactive({
  format: 'png',
  preset: 'printQuality',
  journalPreset: 'nature-single',
  width: 1050,  // 89mm @ 300dpi
  height: 1050,
  dpi: 300,
  backgroundColor: '#ffffff',
  customBgColor: '#ffffff',
  filename: `chart_${new Date().toISOString().slice(0, 10)}`
})

// 监听外部变化
watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 预设变化处理
const handlePresetChange = (preset) => {
  const dpiMap = {
    printQuality: 300,
    highRes: 600,
    presentation: 150,
    webQuality: 72
  }
  
  if (preset !== 'custom') {
    form.dpi = dpiMap[preset] || 300
    // 重新计算尺寸
    if (form.journalPreset !== 'custom') {
      handleJournalChange(form.journalPreset)
    }
  }
}

// 期刊标准变化处理
const handleJournalChange = (preset) => {
  if (preset === 'custom') return

  const [journal, size] = preset.split('-')
  const sizeMap = { single: 'singleColumn', double: 'doubleColumn' }
  
  const dimensions = JournalDimensions[journal]?.[sizeMap[size]]
  if (dimensions) {
    const mmToPixels = (mm, dpi) => Math.round((mm / 25.4) * dpi)
    form.width = mmToPixels(dimensions.width, form.dpi)
    form.height = mmToPixels(dimensions.height, form.dpi)
  }
}

// 导出处理
const handleExport = async () => {
  if (!props.chartInstance) {
    ElMessage.error('图表实例不存在')
    return
  }

  exporting.value = true

  try {
    const exporter = new ChartExporter(props.chartInstance)
    
    const backgroundColor = form.backgroundColor === 'custom' ? 
      form.customBgColor : form.backgroundColor

    const options = {
      format: form.format,
      width: form.width,
      height: form.height,
      dpi: form.dpi,
      backgroundColor,
      filename: form.filename,
      title: form.filename
    }

    const result = await exporter.export(options)

    if (result.success) {
      ElMessage.success(`导出成功：${result.filename}`)
      emit('export-success', result)
      handleClose()
    } else {
      ElMessage.error(`导出失败：${result.error}`)
    }
  } catch (error) {
    console.error('导出错误:', error)
    ElMessage.error(`导出失败：${error.message}`)
  } finally {
    exporting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.export-dialog {
  padding: 10px 0;
}

.format-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.size-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

:deep(.el-radio-button__inner) {
  padding: 8px 15px;
}

:deep(.el-descriptions) {
  margin-top: 10px;
}
</style>
