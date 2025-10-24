<template>
  <div class="data-management-container">
    <el-card class="page-header">
      <template #header>
        <div class="header-content">
          <h2>📊 数据管理中心</h2>
          <p>导入、管理和分析全局钻孔数据</p>
        </div>
      </template>
    </el-card>

    <!-- 数据统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon drill-icon">🔍</div>
          <div class="stat-info">
            <h3>{{ statistics.boreholeCount }}</h3>
            <p>钻孔数据</p>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon coal-icon">⛏️</div>
          <div class="stat-info">
            <h3>{{ statistics.coalSeamCount }}</h3>
            <p>煤层层数据</p>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon mine-icon">🏭</div>
          <div class="stat-info">
            <h3>{{ statistics.uniqueMines }}</h3>
            <p>矿井数量</p>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon total-icon">📈</div>
          <div class="stat-info">
            <h3>{{ statistics.totalRecords }}</h3>
            <p>总数据量</p>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 数据导入区域 -->
    <el-card class="upload-card">
      <template #header>
        <span>📤 数据导入</span>
      </template>

      <div class="upload-section">
        <div class="upload-methods">
          <el-upload
            ref="uploadRef"
            class="upload-area"
            drag
            multiple
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :file-list="fileList"
            accept=".csv"
            :limit="100"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="upload-text">
              <em>点击或拖拽CSV文件到此区域（支持批量上传）</em>
              <p>支持同时选择多个CSV文件，如BK-1.csv、BK-2.csv等</p>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持批量上传多个CSV文件，单个文件不超过10MB
              </div>
            </template>
          </el-upload>

          <div class="upload-info" v-if="fileList.length > 0">
            <el-alert
              :title="`已选择 ${fileList.length} 个文件`"
              type="info"
              :closable="false"
              show-icon
            />
          </div>

          <div class="quick-actions">
            <el-button
              type="primary"
              icon="upload"
              @click="batchImportFiles"
              :loading="loading"
              :disabled="fileList.length === 0"
            >
              开始导入 ({{ fileList.length }} 个文件)
            </el-button>
            <el-button
              type="success"
              icon="refresh"
              @click="refreshData"
              :loading="loading"
            >
              刷新数据
            </el-button>
            <el-button
              type="warning"
              icon="document"
              @click="importFromDatabase"
              :loading="loading"
            >
              从数据库加载
            </el-button>
            <el-button
              type="danger"
              icon="delete"
              @click="clearAllData"
            >
              清空数据
            </el-button>
          </div>
        </div>

        <!-- 导入进度显示 -->
        <div class="import-progress" v-if="importing">
          <el-progress
            :percentage="importProgress"
            :status="importStatus"
            :stroke-width="20"
          >
            <span class="progress-text">{{ importMessage }}</span>
          </el-progress>
        </div>
      </div>
    </el-card>

    <!-- 导入历史记录 -->
    <el-card class="history-card" v-if="globalDataStore.importHistory.length > 0">
      <template #header>
        <div class="header-actions">
          <span>📜 导入历史记录</span>
          <el-button
            type="danger"
            size="small"
            @click="handleClearHistory"
          >
            清空历史
          </el-button>
        </div>
      </template>

      <el-timeline>
        <el-timeline-item
          v-for="item in globalDataStore.importHistory"
          :key="item.id"
          :timestamp="item.timestamp"
          placement="top"
        >
          <el-card shadow="hover">
            <div class="history-item">
              <div class="history-info">
                <div class="history-header">
                  <el-tag :type="item.source === '文件导入' ? 'success' : 'primary'">
                    {{ item.source }}
                  </el-tag>
                  <span class="history-count">{{ item.recordCount }} 条记录</span>
                </div>
                <div class="history-columns">
                  <el-text size="small" type="info">
                    包含字段: {{ item.columns.slice(0, 5).join(', ') }}
                    <span v-if="item.columns.length > 5">等 {{ item.columns.length }} 个字段</span>
                  </el-text>
                </div>
              </div>
              <div class="history-actions">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleRollback(item.id)"
                >
                  回滚到此版本
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="handleDeleteHistory(item.id)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 数据预览区域 -->
    <el-card class="preview-card">
      <template #header>
        <div class="header-actions">
          <span>📋 数据预览</span>
          <div class="filter-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索数据..."
              prefix-icon="search"
              class="search-input"
            />
            <el-select
              v-model="selectedLithology"
              placeholder="按岩性过滤"
              clearable
              class="filter-select"
            >
              <el-option
                v-for="lithology in uniqueLithologies"
                :key="lithology"
                :label="lithology"
                :value="lithology"
              />
            </el-select>
          </div>
        </div>
      </template>

      <div class="table-container">
        <el-table
          :data="filteredData"
          stripe
          border
          style="width: 100%"
          :loading="loading"
          height="400"
        >
          <el-table-column
            prop="钻孔名"
            label="钻孔名"
            width="120"
            fixed
          />
          <el-table-column
            prop="岩层"
            label="岩层名称"
            width="150"
          />
          <el-table-column
            prop="厚度/m"
            label="厚度(m)"
            width="100"
            sortable
          />
          <el-table-column
            prop="弹性模量/GPa"
            label="弹性模量(GPa)"
            width="130"
            sortable
          />
          <el-table-column
            prop="容重/kN·m-3"
            label="容重(kN/m³)"
            width="130"
            sortable
          />
          <el-table-column
            prop="抗拉强度/MPa"
            label="抗拉强度(MPa)"
            width="140"
            sortable
          />
          <el-table-column
            prop="泊松比"
            label="泊松比"
            width="100"
            sortable
          />
          <el-table-column
            prop="数据来源"
            label="数据来源"
            width="180"
          />
          <el-table-column
            label="操作"
            width="120"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click="viewDetails(row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="table-footer">
          <span>显示 {{ filteredData.length }} / {{ globalDataStore.keyStratumData.length }} 条记录</span>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="globalDataStore.keyStratumData.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>

    <!-- 数据详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="数据详情"
      width="60%"
      class="detail-dialog"
    >
      <div class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item
            v-for="(value, key) in currentRow"
            :key="key"
            :label="key"
          >
            {{ value }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useGlobalDataStore } from '@/stores/globalData'

// 初始化store
const globalDataStore = useGlobalDataStore()

// 响应式数据
const loading = ref(false)
const boreholeData = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const selectedLithology = ref('')
const detailDialogVisible = ref(false)
const currentRow = ref({})
const uploadRef = ref(null)
const fileList = ref([])

// 导入进度相关
const importing = ref(false)
const importProgress = ref(0)
const importStatus = ref('')
const importMessage = ref('')

// 计算属性
const statistics = computed(() => {
  return {
    boreholeCount: globalDataStore.keyStratumData.length,
    coalSeamCount: globalDataStore.keyStratumData.filter(row => 
      row['岩层'] && row['岩层'].includes('煤')
    ).length,
    uniqueMines: new Set(globalDataStore.keyStratumData.map(row => row['钻孔名'])).size,
    totalRecords: globalDataStore.keyStratumData.length
  }
})

const uniqueLithologies = computed(() => {
  const lithologies = new Set()
  globalDataStore.keyStratumData.forEach(row => {
    if (row['岩层']) {
      lithologies.add(row['岩层'])
    }
  })
  return Array.from(lithologies)
})

const filteredData = computed(() => {
  let result = globalDataStore.keyStratumData

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(row => {
      return Object.values(row).some(value =>
        value && value.toString().toLowerCase().includes(query)
      )
    })
  }

  // 岩性过滤
  if (selectedLithology.value) {
    result = result.filter(row => 
      row['岩层'] && row['岩层'].includes(selectedLithology.value)
    )
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 文件选择处理
const handleFileChange = (file, files) => {
  // 验证文件类型
  const isCSV = file.name.endsWith('.csv') || file.raw?.type === 'text/csv'
  if (!isCSV) {
    ElMessage.error(`文件 ${file.name} 不是CSV格式！`)
    files.splice(files.indexOf(file), 1)
    return false
  }

  // 验证文件大小
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error(`文件 ${file.name} 超过10MB！`)
    files.splice(files.indexOf(file), 1)
    return false
  }

  fileList.value = files
}

const handleFileRemove = (file, files) => {
  fileList.value = files
}

// 批量导入文件
const batchImportFiles = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要导入的CSV文件')
    return
  }

  importing.value = true
  importProgress.value = 0
  importStatus.value = ''
  loading.value = true

    try {
      const formData = new FormData()

      // 添加所有文件
      fileList.value.forEach((fileWrapper) => {
        formData.append('files', fileWrapper.raw)
      })

      importMessage.value = `正在导入 ${fileList.value.length} 个文件...`
      importProgress.value = 30

      // 使用全局 store 的统一导入方法
      const result = await globalDataStore.importRawFiles(formData)

      importProgress.value = 80

      if (result && result.status === 'success') {
        importProgress.value = 100
        importStatus.value = 'success'
        importMessage.value = `导入成功！共处理 ${result.valid_count}/${result.file_count} 个文件，${result.record_count} 条记录`

        if (result.errors && result.errors.length > 0) {
          console.warn('导入时发生的错误:', result.errors)
          ElMessage.warning({
            message: `部分文件导入失败，成功: ${result.valid_count}/${result.file_count}`,
            duration: 5000
          })
        } else {
          ElMessage.success(`成功导入 ${result.record_count} 条记录`)
        }

        // 清空文件列表
        fileList.value = []
        if (uploadRef.value) {
          uploadRef.value.clearFiles()
        }

        // 刷新显示
        await refreshData()
      } else {
        throw new Error((result && result.message) || '导入失败')
      }
    } catch (error) {
      console.error('批量导入失败:', error)
      importProgress.value = 100
      importStatus.value = 'exception'
      importMessage.value = '导入失败: ' + (error.message || error)
      ElMessage.error('批量导入失败: ' + (error.message || error))
    } finally {
      loading.value = false
      setTimeout(() => {
        importing.value = false
      }, 2000)
    }
}

// 从数据库加载
const importFromDatabase = async () => {
  loading.value = true
  try {
    const result = await globalDataStore.loadFromDatabase(1, 10000)
    if (result && result.status === 'success') {
      ElMessage.success(`从数据库加载 ${result.total || globalDataStore.keyStratumData.length} 条记录`)
      await refreshData()
    } else {
      throw new Error((result && result.message) || '加载失败')
    }
  } catch (error) {
    console.error('从数据库加载失败:', error)
    ElMessage.error('从数据库加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  // 直接从全局存储刷新显示
  boreholeData.value = globalDataStore.keyStratumData
  currentPage.value = 1
}

const clearAllData = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有全局数据吗？此操作不可恢复！',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    globalDataStore.clearKeyStratumData()
    boreholeData.value = []
    fileList.value = []
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
    currentPage.value = 1
    ElMessage.success('全局数据已清空！')
  } catch {
    // 用户取消操作
  }
}

const viewDetails = (row) => {
  currentRow.value = row
  detailDialogVisible.value = true
}

// 历史记录操作
const handleRollback = async (historyId) => {
  try {
    await ElMessageBox.confirm(
      '确定要回滚到此历史版本吗？当前数据将被替换！',
      '确认回滚',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const snapshot = globalDataStore.rollbackToHistory(historyId)
    await refreshData()
    ElMessage.success(`已回滚到 ${snapshot.timestamp} 的数据 (${snapshot.recordCount} 条记录)`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('回滚失败: ' + error.message)
    }
  }
}

const handleDeleteHistory = async (historyId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条历史记录吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    globalDataStore.deleteHistoryItem(historyId)
    ElMessage.success('历史记录已删除')
  } catch {
    // 用户取消操作
  }
}

const handleClearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有历史记录吗？',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    globalDataStore.clearHistory()
    ElMessage.success('历史记录已清空')
  } catch {
    // 用户取消操作
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 初始化
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.data-management-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.page-header :deep(.el-card__header) {
  background: transparent;
  color: white;
}

.header-content {
  text-align: center;
}

.header-content h2 {
  margin: 0 0 10px 0;
  font-size: 28px;
}

.header-content p {
  margin: 0;
  opacity: 0.9;
  font-size: 16px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  transition: transform 0.2s;
  background: white;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.drill-icon { color: #409EFF; }
.coal-icon { color: #67C23A; }
.mine-icon { color: #E6A23C; }
.total-icon { color: #F56C6C; }

.stat-info h3 {
  margin: 0 0 5px 0;
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.upload-card {
  margin-bottom: 20px;
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-methods {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border: 2px dashed #409EFF;
  border-radius: 8px;
  background: #f0f9ff;
}

.upload-info {
  margin-top: 10px;
}

.import-progress {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.progress-text {
  font-size: 14px;
  color: #606266;
  margin-left: 10px;
}

.upload-text {
  text-align: center;
  margin-top: 20px;
}

.upload-text em {
  display: block;
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.upload-text p {
  color: #909399;
  font-size: 14px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.preview-card {
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-actions {
  display: flex;
  gap: 15px;
}

.search-input {
  width: 250px;
}

.filter-select {
  width: 180px;
}

.table-container {
  overflow: hidden;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
}

.detail-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.detail-dialog :deep(.el-dialog__title) {
  color: white;
}

.detail-content {
  max-height: 400px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .upload-section {
    flex-direction: column;
  }

  .filter-actions {
    flex-direction: column;
  }

  .search-input,
  .filter-select {
    width: 100%;
  }

  .header-actions {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
}

/* 历史记录样式 */
.history-card {
  margin-bottom: 20px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.history-info {
  flex: 1;
}

.history-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.history-count {
  font-weight: 500;
  color: #409eff;
}

.history-columns {
  margin-top: 8px;
}

.history-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
</style>