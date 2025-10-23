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
            class="upload-area"
            drag
            :auto-upload="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            accept=".csv"
            :http-request="customUpload"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="upload-text">
              <em>点击或拖拽CSV文件到此区域上传</em>
              <p>支持BK-1、BK-2等钻孔数据格式</p>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传CSV文件，且不超过10MB
              </div>
            </template>
          </el-upload>

          <div class="quick-actions">
            <el-button
              type="primary"
              icon="upload"
              @click="importSampleData"
              :loading="loading"
            >
              导入示例数据
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
              type="danger"
              icon="delete"
              @click="clearAllData"
            >
              清空数据
            </el-button>
          </div>
        </div>
      </div>
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
            prop="序号(从下到上)"
            label="序号"
            width="80"
            sortable
          />
          <el-table-column
            prop="名称"
            label="岩层名称"
            width="120"
          />
          <el-table-column
            prop="厚度/m"
            label="厚度(m)"
            width="100"
            sortable
          />
          <el-table-column
            prop="弹性模量/Gpa"
            label="弹性模量(GPa)"
            width="130"
            sortable
          />
          <el-table-column
            prop="容重/kN*m-3"
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
            label="操作"
            width="120"
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
          <span>显示 {{ filteredData.length }} / {{ boreholeData.length }} 条记录</span>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="boreholeData.length"
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
import dataService from '@/utils/dataService'
import { UploadFilled } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const boreholeData = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const selectedLithology = ref('')
const detailDialogVisible = ref(false)
const currentRow = ref({})

// 计算属性
const statistics = computed(() => dataService.getDataStatistics())
const uniqueLithologies = computed(() => dataService.getUniqueLithologies())

const filteredData = computed(() => {
  let result = boreholeData.value

  // 搜索过滤
  if (searchQuery.value) {
    result = dataService.searchBoreholes(searchQuery.value)
  }

  // 岩性过滤
  if (selectedLithology.value) {
    result = dataService.filterByLithology(selectedLithology.value)
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 方法
const handleUploadSuccess = () => {
  ElMessage.success('文件上传成功！')
  refreshData()
}

const handleUploadError = (error) => {
  ElMessage.error('文件上传失败：' + error.message)
}

const beforeUpload = (file) => {
  const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isCSV) {
    ElMessage.error('只能上传CSV文件！')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB！')
    return false
  }
  return true
}

const importSampleData = async () => {
  loading.value = true
  try {
    await dataService.getAllData()
    boreholeData.value = dataService.globalData.boreholeData
    ElMessage.success('示例数据导入成功！')
  } catch (error) {
    ElMessage.error('数据导入失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await dataService.getAllData()
    boreholeData.value = dataService.globalData.boreholeData
    ElMessage.success('数据刷新成功！')
  } catch (error) {
    ElMessage.error('数据刷新失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const clearAllData = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有数据吗？此操作不可恢复！',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    dataService.clearData()
    boreholeData.value = []
    currentPage.value = 1
    ElMessage.success('数据已清空！')
  } catch {
    // 用户取消操作
  }
}

const viewDetails = (row) => {
  currentRow.value = row
  detailDialogVisible.value = true
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 自定义上传方法
const customUpload = async ({ file }) => {
  try {
    await dataService.readCSV(file)
    handleUploadSuccess()
  } catch (error) {
    handleUploadError(error)
  }
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
  gap: 30px;
  align-items: flex-start;
}

.upload-area {
  flex: 1;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border: 2px dashed #409EFF;
  border-radius: 8px;
  background: #f0f9ff;
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
</style>