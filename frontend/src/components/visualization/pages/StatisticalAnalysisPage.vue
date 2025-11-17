<template>
  <div class="statistics-page modern-layout">
    <div class="page-header modern">
      <div class="title-group">
        <h2><el-icon><DataAnalysis /></el-icon> 统计分析工具箱</h2>
        <p class="subtitle">科研级数据统计与相关性分析</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showDataImportDialog = true">
          <el-icon><Upload /></el-icon> 导入数据
        </el-button>
        <el-button @click="showExportDialog = true" :disabled="!hasData">
          <el-icon><Download /></el-icon> 导出报告
        </el-button>
      </div>
    </div>

    <div class="page-content modern">
      <!-- 左侧数据面板 -->
      <aside class="sidebar modern">
        <el-card shadow="hover" class="panel">
          <template #header>
            <div class="panel-title">数据概览</div>
          </template>
          
          <div v-if="!hasData" class="empty-state">
            <el-empty description="请先导入数据" :image-size="80" />
            <el-button type="primary" @click="showDataImportDialog = true">
              导入数据
            </el-button>
          </div>

          <div v-else class="data-summary">
            <div class="summary-item">
              <span class="label">记录数：</span>
              <span class="value">{{ dataInfo.recordCount }}</span>
            </div>
            <div class="summary-item">
              <span class="label">变量数：</span>
              <span class="value">{{ dataInfo.variableCount }}</span>
            </div>
            
            <el-divider />
            
            <div class="variable-list">
              <div class="list-header">变量列表</div>
              <el-checkbox-group v-model="selectedVariables" @change="onVariableSelect">
                <el-checkbox 
                  v-for="col in numericColumns" 
                  :key="col" 
                  :label="col"
                  class="variable-item"
                >
                  {{ col }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </el-card>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content modern">
        <el-tabs v-model="activeTab" type="border-card" class="stats-tabs">
          <!-- 描述性统计 -->
          <el-tab-pane label="描述性统计" name="descriptive">
            <descriptive-stats-panel
              :data="currentData"
              :selected-variables="selectedVariables"
              @update="updateDescriptiveStats"
            />
          </el-tab-pane>

          <!-- 相关性分析 -->
          <el-tab-pane label="相关性分析" name="correlation">
            <correlation-panel
              :data="currentData"
              :selected-variables="selectedVariables"
              @update="updateCorrelation"
            />
          </el-tab-pane>

          <!-- 回归分析 -->
          <el-tab-pane label="回归分析" name="regression">
            <regression-panel
              :data="currentData"
              :numeric-columns="numericColumns"
              @update="updateRegression"
            />
          </el-tab-pane>

          <!-- 假设检验 -->
          <el-tab-pane label="假设检验" name="hypothesis">
            <hypothesis-panel
              :data="currentData"
              :numeric-columns="numericColumns"
            />
          </el-tab-pane>
        </el-tabs>
      </main>
    </div>

    <!-- 数据导入对话框 -->
    <el-dialog
      v-model="showDataImportDialog"
      title="导入数据"
      width="600px"
      :close-on-click-modal="false"
    >
      <data-import-form @imported="onDataImported" @cancel="showDataImportDialog = false" />
    </el-dialog>

    <!-- 导出报告对话框 -->
    <el-dialog
      v-model="showExportDialog"
      title="导出统计报告"
      width="500px"
    >
      <export-report-form
        :results="allResults"
        @export="handleExport"
        @cancel="showExportDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Upload, Download } from '@element-plus/icons-vue'
import DescriptiveStatsPanel from '../statistics/DescriptiveStatsPanel.vue'
import CorrelationPanel from '../statistics/CorrelationPanel.vue'
import RegressionPanel from '../statistics/RegressionPanel.vue'
import HypothesisPanel from '../statistics/HypothesisPanel.vue'
import DataImportForm from '../statistics/DataImportForm.vue'
import ExportReportForm from '../statistics/ExportReportForm.vue'

// 状态管理
const activeTab = ref('descriptive')
const showDataImportDialog = ref(false)
const showExportDialog = ref(false)

const currentData = ref(null)
const numericColumns = ref([])
const selectedVariables = ref([])

const dataInfo = reactive({
  recordCount: 0,
  variableCount: 0
})

// 分析结果存储
const allResults = reactive({
  descriptive: null,
  correlation: null,
  regression: null,
  hypothesis: null
})

const hasData = computed(() => currentData.value !== null)

// 数据导入处理
const onDataImported = (importedData) => {
  try {
    currentData.value = importedData.data
    numericColumns.value = importedData.numericColumns
    
    dataInfo.recordCount = Object.values(importedData.data)[0]?.length || 0
    dataInfo.variableCount = importedData.numericColumns.length
    
    // 默认选择前5个变量
    selectedVariables.value = numericColumns.value.slice(0, Math.min(5, numericColumns.value.length))
    
    showDataImportDialog.value = false
    ElMessage.success(`成功导入 ${dataInfo.recordCount} 条记录，${dataInfo.variableCount} 个变量`)
  } catch (error) {
    ElMessage.error('数据导入失败: ' + error.message)
  }
}

// 变量选择处理
const onVariableSelect = (selected) => {
  if (selected.length > 20) {
    ElMessage.warning('最多选择20个变量进行分析')
    selectedVariables.value = selected.slice(0, 20)
  }
}

// 更新各分析结果
const updateDescriptiveStats = (result) => {
  allResults.descriptive = result
}

const updateCorrelation = (result) => {
  allResults.correlation = result
}

const updateRegression = (result) => {
  allResults.regression = result
}

// 导出处理
const handleExport = async () => {
  try {
    // 这里实现导出逻辑（PDF/Excel/Word）
    ElMessage.success('报告导出功能开发中...')
    showExportDialog.value = false
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}
</script>

<style scoped>
.statistics-page.modern-layout {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.page-header.modern {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.title-group h2 {
  font-size: 22px;
  margin: 0;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-group .subtitle {
  margin: 4px 0 0 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.page-content.modern {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.sidebar.modern {
  overflow-y: auto;
}

.panel {
  border-radius: 8px;
}

.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.empty-state {
  text-align: center;
  padding: 20px;
}

.empty-state .el-button {
  margin-top: 12px;
}

.data-summary {
  font-size: 13px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.summary-item .label {
  color: #606266;
}

.summary-item .value {
  font-weight: 600;
  color: #303133;
}

.variable-list {
  margin-top: 12px;
}

.list-header {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
}

.variable-item {
  display: block;
  margin-bottom: 8px;
  padding: 4px 0;
}

.main-content.modern {
  overflow-y: auto;
}

.stats-tabs {
  border-radius: 8px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

:deep(.el-tabs__header) {
  margin: 0;
  border-bottom: 1px solid #e4e7ed;
  background: white;
}

:deep(.el-tabs__content) {
  padding: 20px;
  min-height: 600px;
}
</style>
