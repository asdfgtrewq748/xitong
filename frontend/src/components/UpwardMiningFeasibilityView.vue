<template>
  <div class="upward-mining-container">
    <!-- 页面标题 -->
    <el-row :gutter="20" class="page-header">
      <el-col :span="24">
        <el-card shadow="hover" class="header-card">
          <div class="header-content">
            <div class="header-title">
              <h2><el-icon><DataAnalysis /></el-icon> 上行开采可行度分析</h2>
              <p>基于钻孔CSV数据计算上行开采可行度，评估顶板稳定性</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20">
      <!-- 左侧控制面板 -->
      <el-col :span="8">
        <div class="control-panel">
          <!-- 数据输入区域 -->
          <el-card shadow="hover" class="panel-card">
            <template #header>
              <div class="card-header">
                <span><el-icon><Upload /></el-icon> 钻孔数据输入</span>
              </div>
            </template>

            <!-- 文件选择 -->
            <div class="file-selection">
              <el-button type="primary" @click="selectFiles" :loading="loading">
                <el-icon><Upload /></el-icon>
                {{ selectedFiles.length > 0 ? `已选择 ${selectedFiles.length} 个文件` : '选择钻孔CSV文件' }}
              </el-button>
              <el-button type="info" @click="clearFiles">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
            </div>

            <!-- 文件列表 -->
            <div v-if="selectedFiles.length > 0" class="file-list">
              <div class="file-item" v-for="(file, index) in selectedFiles" :key="index">
                <el-icon><Document /></el-icon>
                {{ getFileName(file) }}
              </div>
            </div>

            <!-- 煤层选择 -->
            <div class="coal-selection">
              <h4>煤层选择</h4>
              <div class="coal-group">
                <div class="coal-item">
                  <label>开采煤层（下层）:</label>
                  <el-select v-model="selectedBottomCoal" placeholder="选择开采煤层" @change="onCoalSelectionChange">
                    <el-option
                      v-for="coal in coalLayers"
                      :key="coal"
                      :label="coal"
                      :value="coal"
                    />
                  </el-select>
                </div>
                <div class="coal-item">
                  <label>上煤层:</label>
                  <el-select v-model="selectedUpperCoal" placeholder="选择上煤层" @change="onCoalSelectionChange">
                    <el-option
                      v-for="coal in coalLayers"
                      :key="coal"
                      :value="coal"
                    />
                  </el-select>
                </div>
              </div>
              <div v-if="coalSelectionError" class="error-message">
                {{ coalSelectionError }}
              </div>
            </div>
          </el-card>

          <!-- 参数设置 -->
          <el-card shadow="hover" class="panel-card">
            <template #header>
              <div class="card-header">
                <span><el-icon><Setting /></el-icon> 计算参数</span>
              </div>
            </template>

            <div class="parameter-group">
              <div class="parameter-item">
                <label>影响因子 λ:</label>
                <el-input-number
                  v-model="lambdaParam"
                  :min="0.1"
                  :max="20"
                  :step="0.001"
                  :precision="3"
                  size="small"
                />
              </div>
              <div class="parameter-item">
                <label>地质常数 C:</label>
                <el-input-number
                  v-model="cParam"
                  :min="-10"
                  :max="10"
                  :step="0.001"
                  :precision="3"
                  size="small"
                />
              </div>
            </div>

            <!-- 自动标定按钮 -->
            <el-button
              type="warning"
              @click="autoCalibrate"
              :disabled="selectedFiles.length < 2 || !canAutoCalibrate"
              class="auto-calibrate-btn"
            >
              <el-icon><MagicStick /></el-icon>
              自动标定参数
            </el-button>
          </el-card>

          <!-- 操作按钮 -->
          <el-card shadow="hover" class="panel-card">
            <template #header>
              <div class="card-header">
                <span><el-icon><Operation /></el-icon> 操作</span>
              </div>
            </template>

            <div class="action-buttons">
              <!-- 主操作按钮：批量计算（全宽） -->
              <el-button
                type="danger"
                @click="batchCalculate"
                :loading="calculating"
                :disabled="!canCalculate"
                size="large"
                style="width: 100%; margin-bottom: 12px;"
              >
                <el-icon><Calculator /></el-icon>
                {{ calculating ? '计算中...' : '批量计算可行度' }}
              </el-button>

              <!-- 次要操作：水平排列 -->
              <el-row :gutter="10" style="margin-bottom: 0;">
                <el-col :span="12">
                  <el-button
                    type="primary"
                    @click="exportResults"
                    :disabled="!hasResults"
                    size="large"
                    style="width: 100%;"
                  >
                    <el-icon><Download /></el-icon>
                    导出结果
                  </el-button>
                </el-col>
                <el-col :span="12">
                  <el-button
                    @click="clearAll"
                    size="large"
                    style="width: 100%;"
                  >
                    <el-icon><Delete /></el-icon>
                    清空数据
                  </el-button>
                </el-col>
              </el-row>
            </div>

            <!-- 输出设置 -->
            <div class="output-settings">
              <h4>输出设置</h4>
              <div class="output-item">
                <label>输出文件夹:</label>
                <div class="output-path">
                  <el-input v-model="outputFolder" readonly />
                  <el-button @click="selectOutputFolder" size="small">更改</el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>

      <!-- 右侧结果区域 -->
      <el-col :span="16">
        <div class="results-panel">
          <!-- 计算结果表格 -->
          <el-card shadow="hover" class="results-card">
            <template #header>
              <div class="card-header">
                <span><el-icon><List /></el-icon> 计算结果</span>
                <el-tag v-if="calculationResults.length > 0" type="success">
                  成功计算 {{ successfulCount }} 个钻孔
                </el-tag>
              </div>
            </template>

            <div v-if="calculationResults.length === 0" class="empty-state">
              <el-empty description="暂无计算结果，请先上传文件并计算" />
            </div>

            <div v-else class="results-table">
              <el-table
                :data="displayResults"
                stripe
                height="400"
                style="width: 100%"
              >
                <el-table-column prop="filename" label="文件名" width="150" />
                <el-table-column prop="feasibility_omega" label="可行度ω" width="100">
                  <template #default="scope">
                    <span :class="getFeasibilityClass(scope.row.feasibility_omega)">
                      {{ scope.row.feasibility_omega }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="feasibility_level" label="可行性等级" width="120">
                  <template #default="scope">
                    <el-tag :type="getLevelTagType(scope.row.feasibility_level)" size="small">
                      {{ scope.row.feasibility_level }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="bottom_coal" label="开采煤层" width="100" />
                <el-table-column prop="target_coal" label="上煤层" width="100" />
                <el-table-column prop="mining_coal_thickness_M" label="开采厚度(m)" width="100" />
                <el-table-column prop="total_thickness_H" label="中间岩层厚度(m)" width="120" />
                <el-table-column prop="middle_layer_count" label="中间层数" width="80" />
                <el-table-column prop="avg_tensile_strength" label="平均抗拉强度(MPa)" width="120" />
                <el-table-column label="操作" width="100">
                  <template #default="scope">
                    <el-button
                      size="small"
                      @click="showDetails(scope.row)"
                      type="primary"
                    >
                      详情
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>

          <!-- 统计信息 -->
          <el-card shadow="hover" class="stats-card">
            <template #header>
              <div class="card-header">
                <span><el-icon><TrendCharts /></el-icon> 统计信息</span>
              </div>
            </template>

            <div v-if="calculationResults.length === 0" class="empty-state">
              <el-empty description="暂无统计数据" />
            </div>

            <div v-else class="stats-content">
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ successfulCount }}</div>
                    <div class="stat-label">成功计算</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ errorCount }}</div>
                    <div class="stat-label">计算失败</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ avgFeasibility.toFixed(3) }}</div>
                    <div class="stat-label">平均可行度</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-value">{{ maxFeasibility.toFixed(3) }}</div>
                    <div class="stat-label">最高可行度</div>
                  </div>
                </el-col>
              </el-row>

              <div class="level-distribution">
                <h4>可行性等级分布</h4>
                <div class="level-bars">
                  <div
                    v-for="(count, level) in levelDistribution"
                    :key="level"
                    class="level-bar-item"
                  >
                    <div class="level-bar-label">{{ level }}</div>
                    <div class="level-bar">
                      <div
                        class="level-bar-fill"
                        :style="{ width: getBarWidth(count) + '%', backgroundColor: getLevelColor(level) }"
                      >
                        {{ count }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailsDialogVisible"
      title="计算详情"
      width="80%"
      :before-close="closeDetailsDialog"
    >
      <div v-if="selectedResult" class="details-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">{{ selectedResult.filename }}</el-descriptions-item>
          <el-descriptions-item label="开采煤层">{{ selectedResult.bottom_coal }}</el-descriptions-item>
          <el-descriptions-item label="上煤层">{{ selectedResult.target_coal }}</el-descriptions-item>
          <el-descriptions-item label="开采厚度(M)">{{ selectedResult.mining_coal_thickness_M }} m</el-descriptions-item>
          <el-descriptions-item label="中间岩层总厚度(H)">{{ selectedResult.total_thickness_H }} m</el-descriptions-item>
          <el-descriptions-item label="中间岩层总厚度(D)">{{ selectedResult.total_thickness_D }} m</el-descriptions-item>
          <el-descriptions-item label="中间岩层数">{{ selectedResult.middle_layer_count }}</el-descriptions-item>
          <el-descriptions-item label="平均抗拉强度">{{ selectedResult.avg_tensile_strength }} MPa</el-descriptions-item>
          <el-descriptions-item label="平均弹性模量">{{ selectedResult.avg_elastic_modulus }} GPa</el-descriptions-item>
          <el-descriptions-item label="平均碎胀系数">{{ selectedResult.avg_bulking_factor }}</el-descriptions-item>
          <el-descriptions-item label="影响因子λ">{{ selectedResult.lambda }}</el-descriptions-item>
          <el-descriptions-item label="地质常数C">{{ selectedResult.C }}</el-descriptions-item>
          <el-descriptions-item label="上行开采可行度(ω)" :span="2">
            <span :class="getFeasibilityClass(selectedResult.feasibility_omega)">
              {{ selectedResult.feasibility_omega }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="可行性等级" :span="2">
            <el-tag :type="getLevelTagType(selectedResult.feasibility_level)" size="large">
              {{ selectedResult.feasibility_level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ selectedResult.description }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="layer-details">
          <h4>中间岩层详情</h4>
          <el-table :data="selectedResult.layer_details" stripe max-height="200">
            <el-table-column prop="name" label="岩层名称" />
            <el-table-column prop="thickness" label="厚度(m)" width="80" />
            <el-table-column prop="tensile_strength" label="抗拉强度(MPa)" width="100" />
            <el-table-column prop="elastic_modulus" label="弹性模量(GPa)" width="100" />
            <el-table-column prop="bulking_factor" label="碎胀系数" width="80" />
            <el-table-column prop="sequence" label="序号" width="60" />
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 自动标定对话框 -->
    <el-dialog
      v-model="calibrateDialogVisible"
      title="自动标定参数"
      width="60%"
    >
      <div v-if="calibrateInfo" class="calibrate-content">
        <el-alert
          :title="calibrateInfo.status === 'success' ? '标定成功' : '标定失败'"
          :type="calibrateInfo.status === 'success' ? 'success' : 'error'"
          :description="calibrateInfo.message"
          show-icon
          style="margin-bottom: 20px;"
        />

        <div v-if="calibrateInfo.status === 'success' && calibrateInfo.data" class="calibrate-results">
          <h4>标定结果</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="样本数量">{{ calibrateInfo.data.sample_count }}</el-descriptions-item>
            <el-descriptions-item label="KHD范围">{{ calibrate_info.data.khd_range }}</el-descriptions-item>
            <el-descriptions-item label="初始λ">{{ calibrate_info.data.initial_lambda }}</el-descriptions-item>
            <el-descriptions-item label="初始C">{{ calibrate_info.data.initial_C }}</el-descriptions-item>
            <el-descriptions-item label="标定λ">
              <span class="highlight-value">{{ calibrate_info.data.calculated_lambda }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="标定C">
              <span class="highlight-value">{{ calibrate_info.data.calculated_C }}</span>
            </el-descriptions-item>
          </el-descriptions>
          <div class="calibrate-actions">
            <el-button type="primary" @click="applyCalibratedCoefficients">
              应用标定结果
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 可行性等级说明对话框 -->
    <el-dialog v-model="levelsDialogVisible" title="可行性等级说明" width="60%">
      <div class="levels-content">
        <el-table :data="feasibilityLevels" stripe>
          <el-table-column prop="level" label="等级" width="120">
            <template #default="scope">
              <el-tag :type="getLevelTagType(scope.row.level)" size="large">
                {{ scope.row.level }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="omega_range" label="ω值范围" width="100" />
          <el-table-column prop="description" label="说明" />
        </el-table>
      </div>
    </el-dialog>

    <!-- 快速帮助按钮 -->
    <el-button
      class="help-button"
      type="info"
      circle
      @click="showLevelsDialog"
      position="fixed"
      style="bottom: 20px; right: 20px;"
    >
      <el-icon><QuestionFilled /></el-icon>
    </el-button>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload, Delete, Document, Setting, MagicStick, Operation, Calculator,
  Download, List, TrendCharts, QuestionFilled, DataAnalysis
} from '@element-plus/icons-vue'
import { api } from '../utils/upwardMiningApi'

export default {
  name: 'UpwardMiningFeasibilityView',
  components: {
    Upload, Delete, Document, Setting, MagicStick, Operation, Calculator,
    Download, List, TrendCharts, QuestionFilled, DataAnalysis
  },

  setup() {
    // 响应式数据
    const selectedFiles = ref([])
    const coalLayers = ref([])
    const selectedBottomCoal = ref('')
    const selectedUpperCoal = ref('')
    const lambdaParam = ref(4.95)
    const cParam = ref(-0.84)
    const outputFolder = ref('D:/xiangmu/keshihua/raodongdu/data/output')
    const loading = ref(false)
    const calculating = ref(false)
    const calculationResults = ref([])
    const detailsDialogVisible = ref(false)
    const calibrateDialogVisible = ref(false)
    const levelsDialogVisible = ref(false)
    const selectedResult = ref(null)
    const calibrateInfo = ref(null)
    const feasibilityLevels = ref([])

    // 计算属性
    const canCalculate = computed(() => {
      return selectedFiles.value.length > 0 &&
             selectedBottomCoal.value &&
             selectedUpperCoal.value &&
             selectedBottomCoal.value !== selectedUpperCoal.value
    })

    const canAutoCalibrate = computed(() => {
      return selectedBottomCoal.value &&
             selectedUpperCoal.value &&
             selectedBottomCoal.value !== selectedUpperCoal.value
    })

    const hasResults = computed(() => {
      return calculationResults.value.length > 0
    })

    const successfulCount = computed(() => {
      return calculationResults.value.filter(r => !r.error).length
    })

    const errorCount = computed(() => {
      return calculationResults.value.filter(r => r.error).length
    })

    const avgFeasibility = computed(() => {
      const validResults = calculationResults.value.filter(r => r.feasibility_omega)
      return validResults.length > 0
        ? validResults.reduce((sum, r) => sum + r.feasibility_omega, 0) / validResults.length
        : 0
    })

    const maxFeasibility = computed(() => {
      const validResults = calculationResults.value.filter(r => r.feasibility_omega)
      return validResults.length > 0
        ? Math.max(...validResults.map(r => r.feasibility_omega))
        : 0
    })

    const minFeasibility = computed(() => {
      const validResults = calculationResults.value.filter(r => r.feasibility_omega)
      return validResults.length > 0
        ? Math.min(...validResults.map(r => r.feasibility_omega))
        : 0
    })

    const levelDistribution = computed(() => {
      const distribution = {}
      calculationResults.value.forEach(result => {
        if (result.feasibility_level) {
          distribution[result.feasibility_level] = (distribution[result.feasibility_level] || 0) + 1
        }
      })
      return distribution
    })

    const displayResults = computed(() => {
      return calculationResults.value.filter(r => !r.error)
    })

    const coalSelectionError = computed(() => {
      if (selectedBottomCoal.value && selectedUpperCoal.value) {
        if (selectedBottomCoal.value === selectedUpperCoal.value) {
          return '开采煤层和上煤层不能相同'
        }
      }
      return ''
    })

    // 方法
    const getFileName = (filePath) => {
      return filePath.split('\\').pop() || filePath.split('/').pop()
    }

    const getFeasibilityClass = (omega) => {
      if (omega < 2) return 'level-i'
      if (omega < 4) return 'level-ii'
      if (omega < 6) return 'level-iii'
      if (omega < 8) return 'level-iv'
      return 'level-v'
    }

    const getLevelTagType = (level) => {
      if (level.includes('I级')) return 'danger'
      if (level.includes('II级')) return 'warning'
      if (level.includes('III级')) return 'primary'
      if (level.includes('IV级')) return 'success'
      if (level.includes('V级')) return 'info'
      return ''
    }

    const getLevelColor = (level) => {
      if (level.includes('I级')) return '#f56c6c'
      if (level.includes('II级')) return '#e6a23c'
      if (level.includes('III级')) return '#409eff'
      if (level.includes('IV级')) return '#67c23a'
      if (level.includes('V级')) return '#909399'
      return '#909399'
    }

    const getBarWidth = (count) => {
      const maxCount = Math.max(...Object.values(levelDistribution.value), 1)
      return (count / maxCount) * 100
    }

    // 文件操作
    const selectFiles = async () => {
      try {
        loading.value = true
        const result = await api.selectFiles({
          title: '选择钻孔CSV文件',
          filters: [
            { name: 'CSV文件', extensions: ['csv'] }
          ]
        })

        if (result && result.filePaths && result.filePaths.length > 0) {
          selectedFiles.value = result.filePaths
          await analyzeCoalLayers()
          ElMessage.success(`成功选择 ${selectedFiles.value.length} 个文件`)
        }
      } catch (error) {
        console.error('选择文件失败:', error)
        ElMessage.error('选择文件失败')
      } finally {
        loading.value = false
      }
    }

    const clearFiles = () => {
      selectedFiles.value = []
      coalLayers.value = []
      selectedBottomCoal.value = ''
      selectedUpperCoal.value = ''
      calculationResults.value = []
    }

    const analyzeCoalLayers = async () => {
      if (!selectedFiles.value.length) return

      try {
        loading.value = true
        const coalNameSet = new Set()

        for (const filePath of selectedFiles.value) {
          try {
            // 简化分析，先读取文件提取煤层名称
            // eslint-disable-next-line no-unused-vars
            const result = await api.readFile(filePath)
            if (result && result.data) {
              const df = result.data
              // 查找包含"煤"的层位
              const coalRows = df.filter(row =>
                row['名称'] && row['名称'].toString().includes('煤')
              )
              coalRows.forEach(row => {
                const baseName = getBaseCoalName(row['名称'])
                coalNameSet.add(baseName)
              })
            }
          } catch (error) {
            console.warn(`分析文件 ${filePath} 失败:`, error)
          }
        }

        coalLayers.value = Array.from(coalNameSet).sort()

        // 自动选择默认煤层
        if (coalLayers.value.length >= 2) {
          selectedBottomCoal.value = coalLayers.value[0]
          selectedUpperCoal.value = coalLayers.value[coalLayers.value.length - 1]
        }

        ElMessage.success(`识别到 ${coalLayers.value.length} 个煤层`)
      } catch (error) {
        console.error('分析煤层数据失败:', error)
        ElMessage.error('分析煤层数据失败')
      } finally {
        loading.value = false
      }
    }

    const getBaseCoalName = (name) => {
      const match = name.toString().match(/^(\d+)/)
      return match ? `${match[1]}煤` : name.toString()
    }

    const onCoalSelectionChange = () => {
      if (coalSelectionError.value) {
        ElMessage.warning(coalSelectionError.value)
      }
    }

    const selectOutputFolder = async () => {
      try {
        const result = await api.selectFolder('选择输出文件夹')
        if (result) {
          outputFolder.value = result
        }
      } catch (error) {
        console.error('选择输出文件夹失败:', error)
      }
    }

    const batchCalculate = async () => {
      if (!canCalculate.value) {
        ElMessage.warning('请正确选择煤层后再计算')
        return
      }

      try {
        calculating.value = true

        // 准备批量计算参数
        const params = {
          csv_file_paths: selectedFiles.value,
          bottom_coal_name: selectedBottomCoal.value,
          upper_coal_name: selectedUpperCoal.value,
          lamda: lambdaParam.value,
          C: cParam.value
        }

        const result = await api.batchCalculateUpwardMiningFeasibility(params)

        if (result && result.status === 'success') {
          // eslint-disable-next-line no-unused-vars
          calculationResults.value = result.data.results

          ElMessage.success(`批量计算完成！成功 ${successfulCount.value} 个，失败 ${errorCount.value} 个`)
        } else {
          throw new Error(result?.message || '计算失败')
        }
      } catch (error) {
        console.error('批量计算失败:', error)
        ElMessage.error(`计算失败: ${error.message}`)
      } finally {
        calculating.value = false
      }
    }

    const autoCalibrate = async () => {
      if (!canAutoCalibrate.value) {
        ElMessage.warning('请正确选择煤层后再标定')
        return
      }

      try {
        loading.value = true

        const params = {
          csv_file_paths: selectedFiles.value,
          bottom_coal_name: selectedBottomCoal.value,
          upper_coal_name: selectedUpperCoal.value,
          initial_lamda: lambdaParam.value,
          initial_C: cParam.value
        }

        const result = await api.autoCalibrateUpwardMiningCoefficients(params)

        calibrateInfo.value = result
        calibrateDialogVisible.value = true

        if (result.status === 'success') {
          ElMessage.success('参数标定成功！')
        } else {
          ElMessage.error(`标定失败: ${result.message}`)
        }
      } catch (error) {
        console.error('自动标定失败:', error)
        ElMessage.error(`标定失败: ${error.message}`)
      } finally {
        loading.value = false
      }
    }

    const applyCalibratedCoefficients = () => {
      if (calibrateInfo.value?.data?.calculated_lambda && calibrateInfo.value?.data?.calculated_C) {
        lambdaParam.value = calibrateInfo.value.data.calculated_lambda
        cParam.value = calibrateInfo.value.data.calculated_C
        calibrateDialogVisible.value = false
        ElMessage.success('已应用标定参数')
      }
    }

    const exportResults = async () => {
      try {
        const params = {
          results: calculationResults.value,
          outputFolder: outputFolder.value
        }

        const result = await api.exportResults(params)

        if (result && result.success) {
          ElMessage.success('结果导出成功！')
        } else {
          throw new Error(result?.message || '导出失败')
        }
      } catch (error) {
        console.error('导出结果失败:', error)
        ElMessage.error(`导出失败: ${error.message}`)
      }
    }

    const clearAll = () => {
      ElMessageBox.confirm(
        '确定要清空所有数据吗？此操作不可恢复。',
        '确认清空',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        clearFiles()
        calculationResults.value = []
        selectedResult.value = null
        ElMessage.success('已清空所有数据')
      }).catch(() => {
        // 用户取消操作
      })
    }

    const showDetails = (result) => {
      selectedResult.value = result
      detailsDialogVisible.value = true
    }

    const closeDetailsDialog = () => {
      detailsDialogVisible.value = false
      selectedResult.value = null
    }

    const showLevelsDialog = async () => {
      try {
        const result = await api.getFeasibilityEvaluationLevels()
        feasibilityLevels.value = result.data.levels
        levelsDialogVisible.value = true
      } catch (error) {
        console.error('获取可行性等级失败:', error)
        ElMessage.error('获取可行性等级失败')
      }
    }

    // 生命周期钩子
    onMounted(async () => {
      // 初始化时获取可行性等级标准
      try {
        const result = await api.getFeasibilityEvaluationLevels()
        feasibilityLevels.value = result.data.levels
      } catch (error) {
        console.error('获取可行性等级标准失败:', error)
      }
    })

    return {
      // 数据
      selectedFiles,
      coalLayers,
      selectedBottomCoal,
      selectedUpperCoal,
      lambdaParam,
      cParam,
      outputFolder,
      loading,
      calculating,
      calculationResults,
      detailsDialogVisible,
      calibrateDialogVisible,
      levelsDialogVisible,
      selectedResult,
      calibrateInfo,
      feasibilityLevels,
      coalSelectionError,

      // 计算属性
      canCalculate,
      canAutoCalibrate,
      hasResults,
      successfulCount,
      errorCount,
      avgFeasibility,
      maxFeasibility,
      minFeasibility,
      levelDistribution,
      displayResults,

      // 方法
      getFileName,
      getFeasibilityClass,
      getLevelTagType,
      getLevelColor,
      getBarWidth,
      selectFiles,
      clearFiles,
      onCoalSelectionChange,
      selectOutputFolder,
      batchCalculate,
      autoCalibrate,
      applyCalibratedCoefficients,
      exportResults,
      clearAll,
      showDetails,
      closeDetailsDialog,
      showLevelsDialog
    }
  }
}
</script>

<style scoped>
.upward-mining-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
}

.header-title p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.control-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.panel-card {
  height: fit-content;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #303133;
}

.file-selection {
  margin-bottom: 15px;
}

.file-list {
  max-height: 120px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 8px;
  background: #f9fafb;
}

.file-item {
  padding: 4px 8px;
  margin: 2px 0;
  background: white;
  border-radius: 3px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.coal-selection {
  margin-bottom: 15px;
}

.coal-selection h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.coal-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.coal-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.coal-item label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 5px;
  padding: 5px;
  background: #fef0f0;
  border-radius: 3px;
}

.parameter-group {
  margin-bottom: 15px;
}

.parameter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.parameter-item label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.auto-calibrate-btn {
  width: 100%;
  margin-top: 10px;
}

.action-buttons {
  margin-bottom: 20px;
}

.output-settings {
  border-top: 1px solid #e4e7ed;
  padding-top: 15px;
}

.output-settings h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.output-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.output-item label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.output-path {
  display: flex;
  gap: 5px;
}

.results-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.results-card {
  height: fit-content;
}

.stats-card {
  height: fit-content;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.results-table {
  overflow-x: auto;
}

.level-i {
  color: #f56c6c;
  font-weight: bold;
}

.level-ii {
  color: #e6a23c;
  font-weight: bold;
}

.level-iii {
  color: #409eff;
  font-weight: bold;
}

.level-iv {
  color: #67c23a;
  font-weight: bold;
}

.level-v {
  color: #909399;
  font-weight: bold;
}

.stats-content {
  padding: 10px 0;
}

.stat-item {
  text-align: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #606266;
}

.level-distribution {
  margin-top: 20px;
  border-top: 1px solid #e4e7ed;
  padding-top: 15px;
}

.level-distribution h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.level-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.level-bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.level-bar-label {
  font-size: 12px;
  color: #606266;
  min-width: 80px;
}

.level-bar {
  flex: 1;
  height: 20px;
  background: #e4e7ed;
  border-radius: 10px;
  overflow: hidden;
}

.level-bar-fill {
  height: 100%;
  color: white;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

.details-content {
  padding: 10px 0;
}

.layer-details {
  margin-top: 20px;
}

.layer-details h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.calibrate-content {
  padding: 10px 0;
}

.calibrate-results {
  margin-top: 15px;
}

.calibrate-results h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.highlight-value {
  color: #409eff;
  font-weight: bold;
  font-size: 16px;
}

.calibrate-actions {
  margin-top: 15px;
  text-align: center;
}

.levels-content {
  padding: 10px 0;
}

.help-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .upward-mining-container {
    padding: 15px;
  }

  .control-panel {
    gap: 10px;
  }

  .panel-card {
    height: fit-content;
  }
}

@media (max-width: 768px) {
  .upward-mining-container {
    padding: 10px;
  }

  .page-header {
    margin-bottom: 10px;
  }

  .header-title h2 {
    font-size: 20px;
  }

  .control-panel {
    gap: 8px;
  }

  .action-buttons {
    margin-bottom: 10px;
  }

  .output-settings {
    padding-top: 10px;
  }

  .results-panel {
    gap: 10px;
  }

  .level-bars {
    gap: 5px;
  }

  .help-button {
    bottom: 10px;
    right: 10px;
  }
}
</style>