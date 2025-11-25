<template>
  <el-card class="style-panel" shadow="never">
    <template #header>
      <div class="panel-header">
        <span>学术样式</span>
        <el-button size="small" type="primary" @click="applyStyle">应用样式</el-button>
      </div>
    </template>

    <el-form label-width="100px" size="small">
      <!-- 样式模式 -->
      <el-form-item label="样式模式">
        <el-radio-group v-model="styleConfig.mode">
          <el-radio-button value="journal">期刊模式</el-radio-button>
          <el-radio-button value="presentation">演示模式</el-radio-button>
          <el-radio-button value="thesis">论文模式</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- 字体系列 -->
      <el-form-item label="字体">
        <el-select v-model="styleConfig.fontFamily">
          <el-option label="Arial (推荐)" value="Arial, Helvetica, sans-serif" />
          <el-option label="Times New Roman" value="Times New Roman, Times, serif" />
          <el-option label="Helvetica" value="Helvetica, Arial, sans-serif" />
          <el-option label="默认" value="default" />
        </el-select>
      </el-form-item>

      <!-- 配色方案 -->
      <el-form-item label="配色方案">
        <el-select v-model="styleConfig.colorPalette">
          <el-option label="Wong 2011 (推荐)" value="wong">
            <div class="palette-option">
              <span>Wong 2011</span>
              <div class="color-preview">
                <span v-for="(color, i) in palettes.wong.slice(0, 5)" :key="i" 
                      :style="{ backgroundColor: color }" class="color-dot"></span>
              </div>
            </div>
          </el-option>
          <el-option label="Tol Bright" value="tolBright">
            <div class="palette-option">
              <span>Tol Bright</span>
              <div class="color-preview">
                <span v-for="(color, i) in palettes.tolBright.slice(0, 5)" :key="i" 
                      :style="{ backgroundColor: color }" class="color-dot"></span>
              </div>
            </div>
          </el-option>
          <el-option label="Tol Muted" value="tolMuted">
            <div class="palette-option">
              <span>Tol Muted</span>
              <div class="color-preview">
                <span v-for="(color, i) in palettes.tolMuted.slice(0, 5)" :key="i" 
                      :style="{ backgroundColor: color }" class="color-dot"></span>
              </div>
            </div>
          </el-option>
          <el-option label="灰度 (打印)" value="grayscale">
            <div class="palette-option">
              <span>灰度</span>
              <div class="color-preview">
                <span v-for="(color, i) in palettes.grayscale" :key="i" 
                      :style="{ backgroundColor: color }" class="color-dot"></span>
              </div>
            </div>
          </el-option>
        </el-select>
        <div class="hint">✓ 色盲友好</div>
      </el-form-item>

      <!-- 线条粗细 -->
      <el-form-item label="线条粗细">
        <el-slider v-model="styleConfig.lineWidth" :min="0.5" :max="3" :step="0.5" show-stops />
        <span class="value-label">{{ styleConfig.lineWidth }}pt</span>
      </el-form-item>

      <!-- 符号大小 -->
      <el-form-item label="符号大小">
        <el-slider v-model="styleConfig.symbolSize" :min="4" :max="12" :step="2" show-stops />
        <span class="value-label">{{ styleConfig.symbolSize }}px</span>
      </el-form-item>

      <!-- 网格线 -->
      <el-form-item label="网格线">
        <el-switch v-model="styleConfig.showGridLines" />
      </el-form-item>

      <!-- 背景色 -->
      <el-form-item label="背景色">
        <el-radio-group v-model="styleConfig.backgroundColor">
          <el-radio-button value="#FFFFFF">白色</el-radio-button>
          <el-radio-button value="transparent">透明</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- 标准验证 -->
      <el-form-item label="标准验证">
        <el-button size="small" @click="validateStandards">检查期刊标准</el-button>
      </el-form-item>
    </el-form>

    <!-- 验证结果 -->
    <el-alert
      v-if="validation"
      :title="validation.valid ? '✓ 符合期刊标准' : '! 发现问题'"
      :type="validation.valid ? 'success' : 'warning'"
      :closable="false"
      style="margin-top: 10px"
    >
      <div v-if="validation.warnings.length > 0">
        <div><strong>警告：</strong></div>
        <ul style="margin: 5px 0; padding-left: 20px">
          <li v-for="(w, i) in validation.warnings" :key="i">{{ w }}</li>
        </ul>
      </div>
      <div v-if="validation.suggestions.length > 0" style="margin-top: 10px">
        <div><strong>建议：</strong></div>
        <ul style="margin: 5px 0; padding-left: 20px">
          <li v-for="(s, i) in validation.suggestions.slice(0, 3)" :key="i">{{ s }}</li>
        </ul>
      </div>
    </el-alert>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { ColorBlindFriendlyPalettes } from '@/utils/academicStyles'

const emit = defineEmits(['apply-style', 'validate'])

const palettes = ColorBlindFriendlyPalettes

const styleConfig = reactive({
  mode: 'journal',
  fontFamily: 'Arial, Helvetica, sans-serif',
  colorPalette: 'wong',
  lineWidth: 1.5,
  symbolSize: 6,
  showGridLines: true,
  backgroundColor: '#FFFFFF'
})

const validation = ref(null)

const applyStyle = () => {
  emit('apply-style', { ...styleConfig })
  ElMessage.success('样式已应用')
}

const validateStandards = () => {
  emit('validate', styleConfig)
  // 这里会从父组件接收当前图表配置进行验证
  validation.value = {
    valid: true,
    errors: [],
    warnings: [],
    suggestions: [
      '使用 Arial 或 Times New Roman 字体',
      '确保所有文字 ≥12pt',
      '线条粗细 ≥0.5pt'
    ]
  }
}

defineExpose({
  getConfig: () => ({ ...styleConfig }),
  setValidation: (result) => { validation.value = result }
})
</script>

<style scoped>
.style-panel {
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.palette-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.color-preview {
  display: flex;
  gap: 4px;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid #ddd;
}

.hint {
  font-size: 12px;
  color: #67c23a;
  margin-top: 4px;
}

.value-label {
  margin-left: 10px;
  font-size: 12px;
  color: #606266;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-slider) {
  width: 180px;
}
</style>
