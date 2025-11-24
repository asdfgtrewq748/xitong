<template>
  <div class="page-container">
    <!-- 顶部导航栏 -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="brand">
          <div class="logo-icon">📊</div>
          <div>
            <h1>数据管理中心</h1>
            <p class="subtitle">地质数据全生命周期管理平台</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" plain round @click="startOnboarding">
            <el-icon class="mr-1"><Guide /></el-icon> 新手引导
          </el-button>
        </div>
      </div>
    </header>

    <main class="dashboard-main">
      <!-- 顶部统计与快捷入口 -->
      <section class="top-section">
        <!-- 左侧：统计卡片矩阵 -->
        <div class="stats-grid" ref="statsRef">
          <div class="stat-card primary">
            <div class="stat-icon"><el-icon><DataLine /></el-icon></div>
            <div class="stat-value">{{ statistics.boreholeCount }}</div>
            <div class="stat-label">钻孔总数</div>
          </div>
          <div class="stat-card success">
            <div class="stat-icon"><el-icon><Collection /></el-icon></div>
            <div class="stat-value">{{ statistics.coalSeamCount }}</div>
            <div class="stat-label">煤层数据</div>
          </div>
          <div class="stat-card warning">
            <div class="stat-icon"><el-icon><OfficeBuilding /></el-icon></div>
            <div class="stat-value">{{ statistics.uniqueMines }}</div>
            <div class="stat-label">矿井数量</div>
          </div>
          <div class="stat-card info">
            <div class="stat-icon"><el-icon><Files /></el-icon></div>
            <div class="stat-value">{{ statistics.totalRecords }}</div>
            <div class="stat-label">总记录数</div>
          </div>
        </div>

        <!-- 右侧：快捷操作 -->
        <div class="quick-actions-panel">
          <h3>快捷操作</h3>
          <div class="action-buttons">
            <el-button type="primary" bg icon="Download" @click="downloadSampleCSV">下载模板</el-button>
            <el-button type="success" bg icon="VideoPlay" @click="loadExampleData" :loading="loading">加载示例</el-button>
            <el-button type="danger" bg icon="Delete" plain @click="clearAllData">清空数据</el-button>
          </div>
        </div>
      </section>

      <div class="main-grid">
        <!-- 左侧主要区域：上传与列表 -->
        <div class="left-column">
          <!-- 上传区域 -->
          <div class="content-card upload-card" ref="uploadRef">
            <div class="card-header">
              <h3><el-icon><Upload /></el-icon> 数据导入</h3>
              <el-tag size="small" effect="plain">支持 .csv 格式</el-tag>
            </div>
            <div class="upload-wrapper">
              <el-upload
                ref="uploadRefInner"
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
                  <strong>点击或拖拽文件到此处</strong>
                  <p>支持批量上传多个 CSV 文件</p>
                </div>
              </el-upload>
              
              <div class="upload-actions" v-if="fileList.length > 0">
                <div class="file-count">已选择 {{ fileList.length }} 个文件</div>
                <el-button type="primary" size="large" @click="batchImportFiles" :loading="loading">
                  开始导入
                </el-button>
              </div>

              <!-- 进度条 -->
              <transition name="fade">
                <div class="progress-bar-wrapper" v-if="importing">
                  <el-progress :percentage="importProgress" :status="importStatus" :stroke-width="16" striped striped-flow />
                  <p class="progress-text">{{ importMessage }}</p>
                </div>
              </transition>
            </div>
          </div>

          <!-- 数据表格 -->
          <div class="content-card table-card" ref="tableRef">
            <div class="card-header">
              <div class="header-left">
                <h3><el-icon><List /></el-icon> 数据预览</h3>
              </div>
              <div class="header-right">
                <el-input v-model="searchQuery" placeholder="搜索..." prefix-icon="Search" clearable style="width: 200px" />
                <el-select v-model="selectedLithology" placeholder="岩性筛选" clearable style="width: 140px">
                  <el-option v-for="l in uniqueLithologies" :key="l" :label="l" :value="l" />
                </el-select>
                <el-button icon="Refresh" circle @click="refreshData" :loading="loading" />
              </div>
            </div>
            
            <el-table :data="filteredData" stripe style="width: 100%" height="500" v-loading="loading">
              <el-table-column prop="钻孔名" label="钻孔名" width="120" fixed />
              <el-table-column prop="岩层" label="岩层" width="120">
                <template #default="{ row }">
                  <el-tag :type="getLithologyColor(row['岩层'])" size="small">{{ row['岩层'] }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="厚度/m" label="厚度(m)" sortable />
              <el-table-column prop="弹性模量/GPa" label="弹模(GPa)" sortable />
              <el-table-column prop="容重/kN·m-3" label="容重" sortable />
              <el-table-column prop="抗拉强度/MPa" label="抗拉" sortable />
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="viewDetails(row)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :total="globalDataStore.keyStratumData.length"
                layout="total, prev, pager, next"
              />
            </div>
          </div>
        </div>

        <!-- 右侧侧边栏：历史记录 -->
        <div class="right-column">
          <div class="content-card history-card" ref="historyRef">
            <div class="card-header">
              <h3><el-icon><Timer /></el-icon> 导入历史</h3>
              <el-button link type="danger" size="small" @click="handleClearHistory" v-if="globalDataStore.importHistory.length">清空</el-button>
            </div>
            <div class="history-list">
              <el-empty v-if="!globalDataStore.importHistory.length" description="暂无历史记录" :image-size="60" />
              <el-timeline v-else>
                <el-timeline-item
                  v-for="item in globalDataStore.importHistory"
                  :key="item.id"
                  :timestamp="formatDate(item.timestamp)"
                  :type="item.source === '文件导入' ? 'success' : 'primary'"
                  size="large"
                >
                  <div class="history-item-content">
                    <div class="history-meta">
                      <span class="source-tag">{{ item.source }}</span>
                      <span class="count-tag">+{{ item.recordCount }}条</span>
                    </div>
                    <div class="history-actions">
                      <el-button link type="primary" size="small" @click="handleRollback(item.id)">回滚</el-button>
                      <el-button link type="danger" size="small" @click="handleDeleteHistory(item.id)">删除</el-button>
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 数据详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="数据详情"
      width="600px"
      class="detail-dialog"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item
          v-for="(value, key) in currentRow"
          :key="key"
          :label="key"
        >
          {{ value }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 新手引导覆盖层 -->
    <div v-if="showOnboarding" class="onboarding-overlay">
      <div class="spotlight-box" :style="spotlightStyle"></div>
      <div class="onboarding-card" :style="cardStyle">
        <h3>{{ onboardingSteps[onboardingStep].title }}</h3>
        <p>{{ onboardingSteps[onboardingStep].desc }}</p>
        <div class="onboarding-controls">
          <el-button size="small" @click="prevOnboarding" :disabled="onboardingStep===0">上一步</el-button>
          <el-button size="small" type="primary" @click="nextOnboarding">{{ onboardingStep < onboardingSteps.length-1 ? '下一步' : '完成' }}</el-button>
          <el-button size="small" type="text" @click="skipOnboarding">跳过</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
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
const statsRef = ref(null)
const tableRef = ref(null)
const historyRef = ref(null)
const fileList = ref([])

// 导入进度相关
const importing = ref(false)
const importProgress = ref(0)
const importStatus = ref('')
const importMessage = ref('')

// 新手引导 & 示例数据
const showOnboarding = ref(false)
const onboardingStep = ref(0)
const spotlightStyle = ref({ top: '50%', left: '50%', width: '0', height: '0', opacity: 0 })
const cardStyle = ref({})

const onboardingSteps = [
  { title: '欢迎来到数据管理中心', desc: '这里可以导入、预览和管理全局钻孔与关键层数据。我们将带你快速熟悉常用操作。', target: null },
  { title: '数据统计概览', desc: '这里展示了当前系统中钻孔、煤层和矿井的统计信息，让你对数据规模一目了然。', target: 'statsRef' },
  { title: '数据导入区域', desc: '支持拖拽上传CSV文件，或点击“导入示例数据”快速体验。支持批量上传多个文件。', target: 'uploadRef' },
  { title: '导入历史管理', desc: '每次导入都会生成一条历史记录。如果数据有问题，可以随时回滚到之前的版本。', target: 'historyRef' },
  { title: '数据预览与筛选', desc: '在这里查看详细数据表格。使用顶部的搜索框和岩性筛选器快速查找特定数据。', target: 'tableRef' }
]

const updateSpotlight = async () => {
  if (!showOnboarding.value) return
  await nextTick()
  
  const step = onboardingSteps[onboardingStep.value]
  const targetName = step.target
  
  // 默认居中样式 (无目标时)
  if (!targetName) {
    spotlightStyle.value = {
      top: '50%',
      left: '50%',
      width: '0',
      height: '0',
      opacity: 0,
      boxShadow: '0 0 0 9999px rgba(0,0,0,0.7)'
    }
    cardStyle.value = {
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      margin: 0
    }
    return
  }

  // 获取目标元素
  let el = null
  if (targetName === 'statsRef') el = statsRef.value?.$el || statsRef.value
  else if (targetName === 'uploadRef') el = uploadRef.value?.$el || uploadRef.value
  else if (targetName === 'historyRef') el = historyRef.value?.$el || historyRef.value
  else if (targetName === 'tableRef') el = tableRef.value?.$el || tableRef.value

  if (el && el.getBoundingClientRect) {
    const rect = el.getBoundingClientRect()
    const padding = 10
    
    spotlightStyle.value = {
      top: `${rect.top - padding}px`,
      left: `${rect.left - padding}px`,
      width: `${rect.width + padding * 2}px`,
      height: `${rect.height + padding * 2}px`,
      opacity: 1,
      borderRadius: '8px',
      boxShadow: '0 0 0 9999px rgba(0,0,0,0.7), 0 0 15px rgba(255,255,255,0.3)'
    }
    
    // 计算卡片位置 (优先在下方，如果不够则在上方)
    const cardHeight = 200 // 预估高度
    const spaceBelow = window.innerHeight - rect.bottom
    const showBelow = spaceBelow > cardHeight + 20
    
    cardStyle.value = {
      position: 'fixed',
      left: `${Math.max(20, Math.min(window.innerWidth - 380, rect.left))}px`,
      top: showBelow ? `${rect.bottom + 20}px` : `${rect.top - cardHeight - 20}px`,
      transform: 'none',
      margin: 0
    }
  }
}

watch(onboardingStep, updateSpotlight)
watch(showOnboarding, (val) => {
  if (val) {
    // 禁用滚动
    document.body.style.overflow = 'hidden'
    updateSpotlight()
  } else {
    document.body.style.overflow = ''
  }
})

const downloadSampleCSV = () => {
  const headers = ['钻孔名','岩层','厚度/m','弹性模量/GPa','容重/kN·m-3','抗拉强度/MPa','泊松比','数据来源']
  const rows = [
    ['BK-1', '泥岩', '12.5', '15.2', '26.5', '4.2', '0.25', '钻孔数据'],
    ['BK-1', '砂岩', '8.4', '22.1', '27.2', '8.5', '0.21', '钻孔数据'],
    ['BK-1', '煤层', '3.5', '10.5', '14.2', '2.1', '0.32', '钻孔数据']
  ]
  
  const csvContent = '\uFEFF' + [ // 添加BOM防止乱码
    headers.join(','),
    ...rows.map(r => r.join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'sample_data_template.csv'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('示例CSV模板已下载')
}

const loadExampleData = async () => {
  loading.value = true
  try {
    // 生成若干示例记录
    const cols = ['钻孔名','岩层','厚度/m','弹性模量/GPa','容重/kN·m-3','抗拉强度/MPa','泊松比','数据来源']
    const records = []
    for (let i = 1; i <= 30; i++) {
      records.push({
        '钻孔名': `示例孔_${i}`,
        '岩层': i % 3 === 0 ? '煤层' : (i % 3 === 1 ? '砂岩' : '泥岩'),
        '厚度/m': (2 + (i % 8)).toFixed(2),
        '弹性模量/GPa': (10 + (i % 5)).toFixed(2),
        '容重/kN·m-3': (25 + (i % 4)).toFixed(2),
        '抗拉强度/MPa': (5 + (i % 6)).toFixed(2),
        '泊松比': (0.2 + (i % 10) * 0.01).toFixed(2),
        '数据来源': '示例数据'
      })
    }

    // 使用 store 的加载函数
    await globalDataStore.loadKeyStratumData(records, cols)
    // 保存到历史（模拟）
    // store 内部会记录 last updated, 我们这里直接刷新界面
    await refreshData()
    ElMessage.success('已加载 30 条示例数据，开始体验吧！')
  } catch (err) {
    console.error('加载示例数据失败', err)
    ElMessage.error('加载示例数据失败: ' + err.message)
  } finally {
    loading.value = false
  }
}

const startOnboarding = () => {
  onboardingStep.value = 0
  showOnboarding.value = true
}

const nextOnboarding = () => {
  if (onboardingStep.value < onboardingSteps.length - 1) onboardingStep.value++
  else showOnboarding.value = false
}

const prevOnboarding = () => {
  if (onboardingStep.value > 0) onboardingStep.value--
}

const skipOnboarding = () => {
  showOnboarding.value = false
}

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
// eslint-disable-next-line no-unused-vars
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

// eslint-disable-next-line no-unused-vars
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

// eslint-disable-next-line no-unused-vars
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

/* 快速上手横幅 */
.quick-start-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  background: linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
  box-shadow: 0 6px 18px rgba(102,126,234,0.12);
  animation: bannerIn 600ms ease;
}
.quick-start-banner .banner-left h3 { margin: 0; font-size: 20px }
.quick-start-banner .banner-left p { margin: 4px 0 0 0; color: #4b5563 }
.quick-start-banner .banner-actions { display: flex; gap: 12px }

@keyframes bannerIn {
  from { transform: translateY(-8px); opacity: 0 }
  to { transform: translateY(0); opacity: 1 }
}

/* 卡片动画 */
.stat-card { transition: transform 400ms cubic-bezier(.2,.8,.2,1), box-shadow 400ms; }
.stat-card:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 18px 40px rgba(102,126,234,0.12); }
.stat-content { transition: transform 600ms ease; }

/* 上传区动画 */
.upload-area :deep(.el-upload-dragger) { transition: transform 300ms ease, box-shadow 300ms ease; }
.upload-area :deep(.el-upload-dragger):hover { transform: translateY(-6px); box-shadow: 0 12px 30px rgba(64,158,255,0.12); }

/* 历史记录淡入 */
.history-card :deep(.el-timeline-item) { animation: fadeInUp 500ms ease both; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px) }
  to { opacity: 1; transform: translateY(0) }
}

/* 新手引导覆盖层 */
.onboarding-overlay { position: fixed; inset: 0; z-index: 2000; pointer-events: auto; }
.spotlight-box { position: absolute; transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); pointer-events: none; z-index: 2001; border: 2px solid rgba(255,255,255,0.5); }
.onboarding-card { position: fixed; z-index: 2002; width: 360px; background: linear-gradient(180deg,#fff,#fbfdff); padding: 24px; border-radius: 12px; box-shadow: 0 18px 60px rgba(2,6,23,0.3); transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); }
.onboarding-card h3 { margin:0 0 8px 0; color: #1f2937; font-size: 18px; font-weight: 600; }
.onboarding-card p { margin:0 0 16px 0; color:#4b5563; line-height: 1.5; }
.onboarding-controls { display:flex; gap:10px; justify-content:flex-end }

/* 浮动动画 */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
  100% { transform: translateY(0px); }
}

/* 脉冲发光动画 */
@keyframes pulse-glow {
  0% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(64, 158, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0); }
}

.stat-icon { animation: float 3s ease-in-out infinite; }
.stat-card:nth-child(1) .stat-icon { animation-delay: 0s; }
.stat-card:nth-child(2) .stat-icon { animation-delay: 0.5s; }
.stat-card:nth-child(3) .stat-icon { animation-delay: 1s; }
.stat-card:nth-child(4) .stat-icon { animation-delay: 1.5s; }

.upload-area :deep(.el-upload-dragger):hover {
  animation: pulse-glow 2s infinite;
}

/* 按钮微交互动效 */
.el-button { transition: transform 180ms ease, box-shadow 180ms ease }
.el-button:active { transform: translateY(1px) }


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