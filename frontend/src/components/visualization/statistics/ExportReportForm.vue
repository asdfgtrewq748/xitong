<template>
  <div class="export-report-form">
    <el-form label-position="top" size="default">
      <el-form-item label="导出格式">
        <el-radio-group v-model="exportFormat">
          <el-radio label="pdf">PDF报告</el-radio>
          <el-radio label="excel">Excel表格</el-radio>
          <el-radio label="word">Word文档</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="包含内容">
        <el-checkbox-group v-model="includeContent">
          <el-checkbox label="descriptive">描述性统计</el-checkbox>
          <el-checkbox label="correlation">相关性分析</el-checkbox>
          <el-checkbox label="regression">回归分析</el-checkbox>
          <el-checkbox label="charts">图表</el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <el-form-item label="报告标题">
        <el-input v-model="reportTitle" placeholder="输入报告标题" />
      </el-form-item>
    </el-form>

    <div class="dialog-footer">
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleExport" :disabled="includeContent.length === 0">
        导出报告
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  results: Object
})

const emit = defineEmits(['export', 'cancel'])

const exportFormat = ref('pdf')
const includeContent = ref(['descriptive', 'correlation', 'regression', 'charts'])
const reportTitle = ref('统计分析报告')

const handleExport = () => {
  emit('export', {
    format: exportFormat.value,
    content: includeContent.value,
    title: reportTitle.value
  })
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.export-report-form {
  padding: 0;
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
