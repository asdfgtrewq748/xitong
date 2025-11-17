<template>
  <div class="data-import-form">
    <el-upload
      ref="uploadRef"
      class="upload-area"
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      :limit="1"
      accept=".csv,.xlsx,.xls"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 CSV、Excel 格式，文件大小不超过 10MB
        </div>
      </template>
    </el-upload>

    <div v-if="previewData" class="preview-section">
      <el-divider />
      <div class="preview-header">
        <span>数据预览</span>
        <span class="data-info">{{ previewData.rows }} 行 × {{ previewData.columns.length }} 列</span>
      </div>
      
      <el-table
        :data="previewData.data.slice(0, 5)"
        border
        size="small"
        max-height="200"
        style="margin-top: 12px"
      >
        <el-table-column
          v-for="col in previewData.columns"
          :key="col"
          :prop="col"
          :label="col"
          min-width="100"
          show-overflow-tooltip
        />
      </el-table>

      <div class="column-selection" style="margin-top: 16px">
        <div class="selection-header">选择数值列（用于统计分析）：</div>
        <el-checkbox-group v-model="selectedNumericColumns">
          <el-checkbox
            v-for="col in detectedNumericColumns"
            :key="col"
            :label="col"
          >
            {{ col }}
          </el-checkbox>
        </el-checkbox-group>
      </div>
    </div>

    <div class="dialog-footer">
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleConfirm" :disabled="!canConfirm" :loading="loading">
        确认导入
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

const emit = defineEmits(['imported', 'cancel'])

const uploadRef = ref(null)
const previewData = ref(null)
const detectedNumericColumns = ref([])
const selectedNumericColumns = ref([])
const loading = ref(false)

const canConfirm = computed(() => {
  return previewData.value && selectedNumericColumns.value.length > 0
})

// 处理文件变化
const handleFileChange = async (file) => {
  try {
    const rawFile = file.raw
    if (!rawFile) return

    // 检查文件大小
    if (rawFile.size > 10 * 1024 * 1024) {
      ElMessage.error('文件大小不能超过 10MB')
      return
    }

    const data = await readFile(rawFile)
    parseFileData(data, rawFile.name)
  } catch (error) {
    ElMessage.error('文件读取失败: ' + error.message)
  }
}

// 读取文件
const readFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const data = e.target.result
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
        const jsonData = XLSX.utils.sheet_to_json(firstSheet, { defval: null })
        resolve(jsonData)
      } catch (error) {
        reject(error)
      }
    }
    
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsArrayBuffer(file)
  })
}

// 解析文件数据
const parseFileData = (data, fileName) => {
  if (!data || data.length === 0) {
    ElMessage.error('文件内容为空')
    return
  }

  const columns = Object.keys(data[0])
  
  // 检测数值列
  const numericCols = columns.filter(col => {
    const values = data.map(row => row[col]).filter(v => v !== null && v !== undefined)
    if (values.length === 0) return false
    
    // 检查是否至少80%的值可以转换为数字
    const numericCount = values.filter(v => !isNaN(parseFloat(v))).length
    return numericCount / values.length > 0.8
  })

  detectedNumericColumns.value = numericCols
  selectedNumericColumns.value = numericCols

  previewData.value = {
    data: data,
    columns: columns,
    rows: data.length,
    fileName: fileName
  }

  ElMessage.success(`已加载 ${data.length} 行数据，检测到 ${numericCols.length} 个数值列`)
}

// 确认导入
const handleConfirm = () => {
  if (!canConfirm.value) return

  loading.value = true

  try {
    // 构建只包含选中数值列的数据
    const processedData = {}
    selectedNumericColumns.value.forEach(col => {
      processedData[col] = previewData.value.data.map(row => {
        const val = row[col]
        return val === null || val === undefined || val === '' ? null : parseFloat(val)
      }).filter(v => v !== null && !isNaN(v))
    })

    emit('imported', {
      data: processedData,
      numericColumns: selectedNumericColumns.value,
      originalData: previewData.value.data,
      fileName: previewData.value.fileName
    })
  } catch (error) {
    ElMessage.error('数据处理失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 取消
const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.data-import-form {
  padding: 0;
}

.upload-area {
  margin-bottom: 16px;
}

.el-icon--upload {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 16px;
}

.preview-section {
  margin-top: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.data-info {
  font-size: 13px;
  color: #909399;
  font-weight: normal;
}

.column-selection {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.selection-header {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}
</style>
