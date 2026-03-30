<template>
  <el-container class="tunnel-support-layout">
    <el-header class="page-header">
      <div class="page-header__titles">
        <h2>巷道支护计算</h2>
        <p>基于《巷道支护理论公式.docx》实现完整计算，支持单次计算与批量处理。</p>
      </div>
      <el-space>
        <el-button type="primary" size="small" @click="openUpload">
          <el-icon><Upload /></el-icon>
          导入参数 Excel
        </el-button>
        <el-button type="success" size="small" @click="showConstantsDialog">
          <el-icon><Setting /></el-icon>
          常量设置
        </el-button>
        <el-button type="warning" size="small" @click="showTemplateDialog" v-if="false">
          <el-icon><Document /></el-icon>
          下载模板
        </el-button>
      </el-space>
      <input ref="fileInput" type="file" accept=".xlsx,.xls" @change="handleExcel" style="display:none" />
    </el-header>

    <el-main>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="never" class="control-card">
            <div class="card-header-with-action">
              <h3>输入参数</h3>
              <el-button size="small" @click="addToBatch" :disabled="!form.B || !form.H">
                <el-icon><Plus /></el-icon>
                添加到批量队列
              </el-button>
            </div>
            <el-form :model="form" label-width="110px" class="input-form">
              <el-form-item label="巷道宽度 B (m)">
                <el-input-number v-model="form.B" :step="0.1" :min="0" style="width:100%" />
              </el-form-item>
              <el-form-item label="巷道高度 H (m)">
                <el-input-number v-model="form.H" :step="0.1" :min="0" style="width:100%" />
              </el-form-item>
              <el-form-item label="应力集中系数 K">
                <el-input-number v-model="form.K" :step="0.1" style="width:100%" />
              </el-form-item>
              <el-form-item label="埋深 (m)">
                <el-input-number v-model="form.depth" :step="0.1" :min="0" style="width:100%" />
              </el-form-item>
              <el-form-item label="容重 (kN/m³)">
                <el-input-number v-model="form.gamma" :step="0.1" style="width:100%" />
              </el-form-item>
              <el-form-item label="粘聚力 C (MPa)">
                <el-input-number v-model="form.C" :step="0.01" style="width:100%" />
              </el-form-item>
              <el-form-item label="内摩擦角 φ (°)">
                <el-input-number v-model="form.phi" :step="0.1" style="width:100%" />
              </el-form-item>
              <el-form-item label="顶板普氏系数 f">
                <el-input-number v-model="form.f_top" :step="0.1" :min="0.1" style="width:100%" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="calculate" :loading="loading">计算</el-button>
                <el-button @click="resetForm" style="margin-left:8px">重置</el-button>
              </el-form-item>
            </el-form>

            <!-- 批量队列预览 -->
            <div v-if="batchQueue.length > 0" class="batch-queue-preview">
              <el-divider />
              <div class="queue-header">
                <h4>批量队列 ({{ batchQueue.length }} 条)</h4>
                <el-space>
                  <el-button size="small" type="primary" @click="calculateBatchQueue" :loading="loading">
                    批量计算
                  </el-button>
                  <el-button size="small" @click="clearQueue">清空</el-button>
                </el-space>
              </div>
              <el-table :data="batchQueue" size="small" max-height="200" stripe>
                <el-table-column type="index" label="#" width="40"></el-table-column>
                <el-table-column prop="B" label="B" width="60"></el-table-column>
                <el-table-column prop="H" label="H" width="60"></el-table-column>
                <el-table-column prop="K" label="K" width="50"></el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="{ $index }">
                    <el-button size="small" type="danger" text @click="removeFromQueue($index)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-card shadow="never" class="result-card">
            <div class="result-header">
              <h3>计算结果</h3>
              <div>
                <el-button type="success" @click="exportCsv" :disabled="!result" size="small">
                  <el-icon><Download /></el-icon>
                  导出 CSV
                </el-button>
                <el-button @click="copyToClipboard" :disabled="!result" size="small">
                  <el-icon><CopyDocument /></el-icon>
                  复制结果
                </el-button>
                <el-button @click="addResultToHistory" :disabled="!result" type="primary" size="small">
                  <el-icon><Plus /></el-icon>
                  添加到历史
                </el-button>
              </div>
            </div>

            <div v-if="!result && batchResults.length === 0">
              <p class="hint">请填写参数并点击"计算"，或导入包含列 (B,H,应力集中系数K,埋深,容重,粘聚力,内摩擦角) 的 Excel 文件。</p>
            </div>

            <!-- 单次计算结果 -->
            <div v-if="result && batchResults.length === 0" class="result-body">
              <el-descriptions column="2" border>
                <el-descriptions-item label="塑性区半径 R (m)">{{ result.basic.R }}</el-descriptions-item>
                <el-descriptions-item label="顶板松动圈 hct (m)">{{ result.basic.hct }}</el-descriptions-item>
                <el-descriptions-item label="两帮松动圈 hcs (m)">{{ result.basic.hcs }}</el-descriptions-item>
                <el-descriptions-item label="压力拱高度 hat (m)">{{ result.basic.hat }}</el-descriptions-item>
              </el-descriptions>

              <el-divider />

              <h4>锚索设计</h4>
              <el-table :data="[result.anchor]" style="width:100%">
                <el-table-column prop="Nt" label="Nt (kN)"></el-table-column>
                <el-table-column prop="diameter" label="直径 (mm)"></el-table-column>
                <el-table-column prop="Lm" label="锚固长度 Lm (m)"></el-table-column>
                <el-table-column prop="L_total" label="总长 L (m)"></el-table-column>
                <el-table-column prop="spacing_area" label="间排距 a*b (m²)"></el-table-column>
              </el-table>

              <el-divider />
              <h4>锚杆设计</h4>
              <el-table :data="[result.rod]" style="width:100%">
                <el-table-column prop="Nt" label="Nt (kN)"></el-table-column>
                <el-table-column prop="diameter" label="直径 (mm)"></el-table-column>
                <el-table-column prop="La" label="锚固长度 La (m)"></el-table-column>
                <el-table-column prop="L_top" label="顶部长度 (m)"></el-table-column>
                <el-table-column prop="L_side" label="侧部长度 (m)"></el-table-column>
                <el-table-column prop="spacing_area_top" label="a*b (顶部) (m²)"></el-table-column>
                <el-table-column prop="spacing_area_side" label="a*b (侧部) (m²)"></el-table-column>
              </el-table>
            </div>

            <!-- 批量计算结果 -->
            <div v-if="batchResults.length > 0" class="batch-results">
              <div class="batch-result-header">
                <h4>批量计算结果 ({{ batchResults.length }} 条)</h4>
                <el-space>
                  <el-input
                    v-model="searchText"
                    placeholder="搜索..."
                    size="small"
                    style="width: 200px"
                    clearable
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                  <el-button size="small" @click="showStatistics">
                    <el-icon><DataAnalysis /></el-icon>
                    统计
                  </el-button>
                  <el-button size="small" @click="showCompareDialog" :disabled="selectedRows.length < 2">
                    <el-icon><Connection /></el-icon>
                    对比 ({{ selectedRows.length }})
                  </el-button>
                </el-space>
              </div>
              <el-table 
                :data="filteredBatchResults" 
                style="width:100%" 
                max-height="500" 
                border 
                stripe
                @selection-change="handleSelectionChange"
              >
                <el-table-column type="selection" width="45"></el-table-column>
                <el-table-column type="index" label="#" width="50"></el-table-column>
                <el-table-column prop="B" label="B (m)" width="80" sortable></el-table-column>
                <el-table-column prop="H" label="H (m)" width="80" sortable></el-table-column>
                <el-table-column prop="R(m)" label="塑性区半径 R (m)" width="120" sortable></el-table-column>
                <el-table-column prop="hct(m)" label="顶板松动圈 hct (m)" width="130" sortable></el-table-column>
                <el-table-column prop="hcs(m)" label="两帮松动圈 hcs (m)" width="130" sortable></el-table-column>
                <el-table-column prop="Nt_anchor(kN)" label="锚索 Nt (kN)" width="120" sortable></el-table-column>
                <el-table-column prop="L_total_anchor(m)" label="锚索长度 (m)" width="120" sortable></el-table-column>
                <el-table-column prop="Nt_rod(kN)" label="锚杆 Nt (kN)" width="120" sortable></el-table-column>
                <el-table-column prop="L_top(m)" label="顶锚杆长 (m)" width="120" sortable></el-table-column>
                <el-table-column prop="L_side(m)" label="侧锚杆长 (m)" width="120" sortable></el-table-column>
                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="{ row, $index }">
                    <el-button type="primary" size="small" text @click="viewDetail(row)">详情</el-button>
                    <el-button type="danger" size="small" text @click="deleteRow($index)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div style="margin-top: 12px">
                <el-button type="success" @click="exportBatchCsv">
                  <el-icon><Download /></el-icon>
                  导出批量结果 CSV
                </el-button>
                <el-button type="primary" @click="exportBatchExcel">
                  <el-icon><Download /></el-icon>
                  导出 Excel
                </el-button>
                <el-button @click="clearBatchResults" style="margin-left:8px">清空批量结果</el-button>
                <el-button @click="mergeToBatchResults" v-if="historyResults.length > 0">
                  合并历史记录 ({{ historyResults.length }})
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 锚杆材质参考表 -->
      <el-card shadow="never" style="margin-top: 16px">
        <h3 style="margin: 0 0 12px 0">锚杆材质及性质参考表</h3>
        <el-table :data="anchorMaterialData" border stripe size="small">
          <el-table-column prop="grade" label="牌号" align="center" />
          <el-table-column prop="diameter" label="公称直径 / mm" align="center" />
          <el-table-column prop="yieldStrength" label="屈服强度 / MPa" align="center" />
          <el-table-column prop="tensileStrength" label="抗拉强度 / MPa" align="center" />
          <el-table-column prop="elongation" label="伸长率 / %" align="center" />
        </el-table>
      </el-card>

      <!-- 支护材料匹配性分析 -->
      <el-card shadow="never" style="margin-top: 16px">
        <h3 style="margin: 0 0 8px 0">支护材料匹配性分析</h3>
        <p style="color: #888; font-size: 13px; margin: 0 0 16px 0">
          根据锚杆牌号与托盘承载力、锚索设计承载力与托板承载力的匹配关系，检验支护材料是否满足要求。
        </p>

        <el-row :gutter="24">
          <!-- 锚杆与托盘匹配 -->
          <el-col :span="12">
            <el-card shadow="never" class="match-sub-card">
              <template #header>
                <span style="font-weight: 600">锚杆与托盘匹配性</span>
              </template>
              <el-form :model="matchForm" label-width="150px" size="small">
                <el-form-item label="锚杆直径 (mm)">
                  <el-input-number v-model="matchForm.rodDiameter" :step="1" :min="4" style="width:100%" />
                </el-form-item>
                <el-form-item label="锚杆牌号">
                  <el-select v-model="matchForm.rodGrade" placeholder="选择牌号" style="width:100%" @change="onRodGradeChange">
                    <el-option v-for="item in anchorMaterialData" :key="item.grade" :label="item.grade" :value="item.grade" />
                  </el-select>
                </el-form-item>
                <el-form-item label="屈服强度 (MPa)">
                  <el-input-number v-model="matchForm.rodYieldStrength" :step="5" :min="0" style="width:100%" />
                </el-form-item>
                <el-form-item label="托盘承载力 (kN)">
                  <el-input-number v-model="matchForm.plateCapacityRod" :step="5" :min="0" style="width:100%" />
                </el-form-item>
              </el-form>
              <div v-if="matchResult && matchResult.rod" class="match-result">
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="锚杆屈服力 Q_锚">{{ matchResult.rod.rod_yield_force_kN }} kN</el-descriptions-item>
                  <el-descriptions-item label="托盘最低要求">{{ matchResult.rod.plate_required_kN }} kN</el-descriptions-item>
                  <el-descriptions-item label="实际托盘承载力">{{ matchResult.rod.plate_actual_kN }} kN</el-descriptions-item>
                  <el-descriptions-item label="匹配结果">
                    <el-tag :type="matchResult.rod.matched ? 'success' : 'danger'" size="small">
                      {{ matchResult.rod.matched ? '匹配' : '不匹配' }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </el-card>
          </el-col>

          <!-- 锚索与托板匹配 -->
          <el-col :span="12">
            <el-card shadow="never" class="match-sub-card">
              <template #header>
                <span style="font-weight: 600">锚索与托板匹配性</span>
              </template>
              <el-form :model="matchForm" label-width="150px" size="small">
                <el-form-item label="锚索设计承载力 Nt (kN)">
                  <el-input-number v-model="matchForm.anchorNt" :step="5" :min="0" style="width:100%" />
                </el-form-item>
                <el-form-item label="托板承载力 Tb (kN)">
                  <el-input-number v-model="matchForm.plateCapacityAnchor" :step="5" :min="0" style="width:100%" />
                </el-form-item>
              </el-form>
              <div v-if="matchResult && matchResult.anchor" class="match-result">
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="锚索设计承载力 Nt">{{ matchResult.anchor.Nt_kN }} kN</el-descriptions-item>
                  <el-descriptions-item label="托板最低要求">{{ matchResult.anchor.plate_required_kN }} kN</el-descriptions-item>
                  <el-descriptions-item label="实际托板承载力">{{ matchResult.anchor.plate_actual_kN }} kN</el-descriptions-item>
                  <el-descriptions-item label="匹配结果">
                    <el-tag :type="matchResult.anchor.matched ? 'success' : 'danger'" size="small">
                      {{ matchResult.anchor.matched ? '匹配' : '不匹配' }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <div style="margin-top: 16px; text-align: center">
          <el-button type="primary" @click="calculateMaterialMatch" :loading="matchLoading">
            分析匹配性
          </el-button>
          <el-button @click="resetMatchForm">重置</el-button>
        </div>
      </el-card>

      <!-- 常量编辑对话框 -->
      <el-dialog v-model="constantsDialogVisible" title="计算常量设置" width="680px">
        <el-form :model="editingConstants" label-width="170px" v-if="editingConstants">
          <el-form-item label="锚索截面积 Sn (mm²)">
            <el-input-number v-model="editingConstants.Sn" :step="1" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item label="安全系数 K">
            <el-input-number v-model="editingConstants.safety_K" :step="0.1" :min="0.1" style="width:100%" />
          </el-form-item>
          <el-form-item label="锚索抗拉强度 (MPa)">
            <el-input-number v-model="editingConstants.Rm_anchor" :step="10" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item label="锚杆抗拉强度 (MPa)">
            <el-input-number v-model="editingConstants.Rm_rod" :step="10" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item label="锚索设计荷载 (kN)">
            <el-input-number v-model="editingConstants.Q_anchor" :step="10" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item label="锚杆设计荷载 (kN)">
            <el-input-number v-model="editingConstants.Q_rod" :step="5" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item label="树脂锚固力 (MPa)">
            <el-input-number v-model="editingConstants.c0" :step="0.1" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item label="锚杆锚固力 (MPa)">
            <el-input-number v-model="editingConstants.tau_rod" :step="0.1" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item label="锚索半径 (mm)">
            <el-input-number v-model="editingConstants.R_mm" :step="1" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item label="锚杆直径 (mm)">
            <el-input-number v-model="editingConstants.D_mm" :step="1" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item label="工作状态系数 m">
            <el-input-number v-model="editingConstants.m" :step="0.1" :min="0" :max="1" style="width:100%" />
          </el-form-item>
          <el-form-item label="根数 n">
            <el-input-number v-model="editingConstants.n" :step="1" :min="1" style="width:100%" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="resetConstants">恢复默认</el-button>
          <el-button @click="constantsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveConstants">保存</el-button>
        </template>
      </el-dialog>

      <!-- 统计信息对话框 -->
      <el-dialog v-model="statisticsDialogVisible" title="批量结果统计" width="700px">
        <el-descriptions :column="2" border v-if="statistics">
          <el-descriptions-item label="总记录数">{{ statistics.count }}</el-descriptions-item>
          <el-descriptions-item label="平均 R">{{ statistics.avg_R.toFixed(3) }} m</el-descriptions-item>
          <el-descriptions-item label="最大 R">{{ statistics.max_R.toFixed(3) }} m</el-descriptions-item>
          <el-descriptions-item label="最小 R">{{ statistics.min_R.toFixed(3) }} m</el-descriptions-item>
          <el-descriptions-item label="平均锚索长度">{{ statistics.avg_anchor_length.toFixed(3) }} m</el-descriptions-item>
          <el-descriptions-item label="平均锚杆长度(顶)">{{ statistics.avg_rod_top.toFixed(3) }} m</el-descriptions-item>
        </el-descriptions>
      </el-dialog>

      <!-- 对比对话框 -->
      <el-dialog v-model="compareDialogVisible" title="结果对比" width="900px">
        <el-table :data="selectedRows" border>
          <el-table-column type="index" label="#" width="50"></el-table-column>
          <el-table-column prop="B" label="B (m)" width="80"></el-table-column>
          <el-table-column prop="H" label="H (m)" width="80"></el-table-column>
          <el-table-column prop="R(m)" label="塑性区半径 R (m)" width="120"></el-table-column>
          <el-table-column prop="Nt_anchor(kN)" label="锚索 Nt" width="100"></el-table-column>
          <el-table-column prop="Nt_rod(kN)" label="锚杆 Nt" width="100"></el-table-column>
          <el-table-column prop="L_total_anchor(m)" label="锚索长度" width="100"></el-table-column>
          <el-table-column prop="L_top(m)" label="顶锚杆长" width="100"></el-table-column>
        </el-table>
      </el-dialog>

      <!-- 详情对话框 -->
      <el-dialog v-model="detailDialogVisible" title="计算详情" width="800px">
        <el-descriptions :column="2" border v-if="detailRow">
          <el-descriptions-item label="巷道宽度 B">{{ detailRow.B }} m</el-descriptions-item>
          <el-descriptions-item label="巷道高度 H">{{ detailRow.H }} m</el-descriptions-item>
          <el-descriptions-item label="塑性区半径 R">{{ detailRow['R(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="顶板松动圈 hct">{{ detailRow['hct(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="两帮松动圈 hcs">{{ detailRow['hcs(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="压力拱高度 hat">{{ detailRow['hat(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="锚索 Nt">{{ detailRow['Nt_anchor(kN)'] }} kN</el-descriptions-item>
          <el-descriptions-item label="锚索直径">{{ detailRow['diameter_anchor(mm)'] }} mm</el-descriptions-item>
          <el-descriptions-item label="锚索锚固长度">{{ detailRow['Lm_anchor(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="锚索总长">{{ detailRow['L_total_anchor(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="锚杆 Nt">{{ detailRow['Nt_rod(kN)'] }} kN</el-descriptions-item>
          <el-descriptions-item label="锚杆直径">{{ detailRow['diameter_rod(mm)'] }} mm</el-descriptions-item>
          <el-descriptions-item label="顶锚杆长">{{ detailRow['L_top(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="侧锚杆长">{{ detailRow['L_side(m)'] }} m</el-descriptions-item>
        </el-descriptions>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Setting, Download, Plus, CopyDocument, Search, DataAnalysis, Connection, Document } from '@element-plus/icons-vue'

const form = ref({ B: 4.0, H: 3.0, K: 1.0, depth: 200, gamma: 18.0, C: 0.5, phi: 30.0, f_top: 2.0 })
const loading = ref(false)
const result = ref(null)
const batchResults = ref([])
const batchQueue = ref([])
const historyResults = ref([])
const fileInput = ref(null)
const constantsDialogVisible = ref(false)
const statisticsDialogVisible = ref(false)
const compareDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const constants = ref(null)
const editingConstants = ref(null)
const searchText = ref('')
const selectedRows = ref([])
const detailRow = ref(null)
const statistics = ref(null)

const anchorMaterialData = [
  { grade: 'Q235', diameter: '4~20', yieldStrength: 235, tensileStrength: 380, elongation: 25 },
  { grade: 'BHRB335', diameter: '16~22', yieldStrength: 335, tensileStrength: 490, elongation: 22 },
  { grade: 'BHRB400', diameter: '16~22', yieldStrength: 400, tensileStrength: 570, elongation: 22 },
  { grade: 'BHRB500', diameter: '16~25', yieldStrength: 500, tensileStrength: 670, elongation: 20 },
  { grade: 'BHRB600', diameter: '16~25', yieldStrength: 600, tensileStrength: 780, elongation: 18 },
  { grade: 'BHTB600', diameter: '16~25', yieldStrength: 600, tensileStrength: 780, elongation: 25 },
  { grade: 'BHRB700', diameter: '16~25', yieldStrength: 700, tensileStrength: 870, elongation: 21 },
  { grade: '预应力钢棒', diameter: '14~20', yieldStrength: 1140, tensileStrength: 1270, elongation: 15 },
]

// 支护材料匹配性分析
const matchForm = ref({
  rodDiameter: 20,
  rodGrade: 'BHRB400',
  rodYieldStrength: 400,
  plateCapacityRod: 200,
  anchorNt: 349.3,
  plateCapacityAnchor: 600,
})
const matchResult = ref(null)
const matchLoading = ref(false)

function onRodGradeChange(grade) {
  const item = anchorMaterialData.find(m => m.grade === grade)
  if (item) {
    matchForm.value.rodYieldStrength = item.yieldStrength
  }
}

async function calculateMaterialMatch() {
  try {
    matchLoading.value = true
    const resp = await fetch('/api/tunnel-support/material-match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rod_diameter_mm: matchForm.value.rodDiameter,
        rod_grade: matchForm.value.rodGrade,
        rod_yield_strength: matchForm.value.rodYieldStrength,
        plate_capacity_rod: matchForm.value.plateCapacityRod,
        anchor_Nt: matchForm.value.anchorNt,
        plate_capacity_anchor: matchForm.value.plateCapacityAnchor,
      })
    })
    const data = await resp.json()
    if (resp.ok && data.status === 'success') {
      matchResult.value = data
      ElMessage.success('匹配性分析完成')
    } else {
      ElMessage.error(data.detail || '分析失败')
    }
  } catch (err) {
    ElMessage.error('请求失败: ' + err)
  } finally {
    matchLoading.value = false
  }
}

function resetMatchForm() {
  matchForm.value = {
    rodDiameter: 20,
    rodGrade: 'BHRB400',
    rodYieldStrength: 400,
    plateCapacityRod: 200,
    anchorNt: 349.3,
    plateCapacityAnchor: 600,
  }
  matchResult.value = null
}

// 过滤批量结果
const filteredBatchResults = computed(() => {
  if (!searchText.value) return batchResults.value
  const search = searchText.value.toLowerCase()
  return batchResults.value.filter(row => {
    return Object.values(row).some(val => 
      String(val).toLowerCase().includes(search)
    )
  })
})

onMounted(async () => {
  // 先尝试从本地存储加载已保存的常量
  try {
    const savedConstants = localStorage.getItem('tunnel_support_constants')
    if (savedConstants) {
      constants.value = JSON.parse(savedConstants)
    }
  } catch (err) {
    console.error('加载保存的常量失败:', err)
  }

  // 如果没有保存的常量，从后端获取默认常量
  if (!constants.value) {
    try {
      const resp = await fetch('/api/tunnel-support/default-constants')
      const data = await resp.json()
      if (resp.ok) {
        constants.value = data.constants
      }
    } catch (err) {
      console.error('加载常量失败:', err)
    }
  }

  // 从本地存储加载历史
  loadHistory()
})

function loadHistory() {
  try {
    const saved = localStorage.getItem('tunnel_support_history')
    if (saved) {
      historyResults.value = JSON.parse(saved)
    }
  } catch (err) {
    console.error('加载历史失败:', err)
  }
}

function saveHistory() {
  try {
    localStorage.setItem('tunnel_support_history', JSON.stringify(historyResults.value))
  } catch (err) {
    console.error('保存历史失败:', err)
  }
}

function addResultToHistory() {
  if (!result.value) return
  const flat = {
    ...result.value.input,
    ...result.value.basic,
    ...result.value.anchor,
    ...result.value.rod,
    timestamp: new Date().toLocaleString()
  }
  historyResults.value.unshift(flat)
  // 限制历史记录数量
  if (historyResults.value.length > 50) {
    historyResults.value = historyResults.value.slice(0, 50)
  }
  saveHistory()
  ElMessage.success('已添加到历史记录')
}

function mergeToBatchResults() {
  ElMessageBox.confirm(
    `将 ${historyResults.value.length} 条历史记录合并到当前批量结果?`,
    '确认',
    {
      confirmButtonText: '合并',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    batchResults.value = [...batchResults.value, ...historyResults.value]
    historyResults.value = []
    saveHistory()
    ElMessage.success('已合并历史记录')
  }).catch(() => {})
}

function addToBatch() {
  if (!form.value.B || !form.value.H) {
    ElMessage.warning('请填写完整参数')
    return
  }
  batchQueue.value.push({ ...form.value })
  ElMessage.success(`已添加到队列 (${batchQueue.value.length} 条)`)
}

function removeFromQueue(index) {
  batchQueue.value.splice(index, 1)
}

function clearQueue() {
  batchQueue.value = []
  ElMessage.info('已清空队列')
}

async function calculateBatchQueue() {
  if (batchQueue.value.length === 0) {
    ElMessage.warning('队列为空')
    return
  }
  await batchCalculate(batchQueue.value)
  batchQueue.value = []
}

function handleSelectionChange(selection) {
  selectedRows.value = selection
}

function showStatistics() {
  if (batchResults.value.length === 0) {
    ElMessage.warning('没有结果可统计')
    return
  }
  
  const RValues = batchResults.value.map(r => parseFloat(r['R(m)']))
  const anchorLengths = batchResults.value.map(r => parseFloat(r['L_total_anchor(m)']))
  const rodTopLengths = batchResults.value.map(r => parseFloat(r['L_top(m)']))
  
  statistics.value = {
    count: batchResults.value.length,
    avg_R: RValues.reduce((a, b) => a + b, 0) / RValues.length,
    max_R: Math.max(...RValues),
    min_R: Math.min(...RValues),
    avg_anchor_length: anchorLengths.reduce((a, b) => a + b, 0) / anchorLengths.length,
    avg_rod_top: rodTopLengths.reduce((a, b) => a + b, 0) / rodTopLengths.length
  }
  
  statisticsDialogVisible.value = true
}

function showCompareDialog() {
  if (selectedRows.value.length < 2) {
    ElMessage.warning('请至少选择 2 条记录进行对比')
    return
  }
  compareDialogVisible.value = true
}

function viewDetail(row) {
  detailRow.value = row
  detailDialogVisible.value = true
}

function deleteRow(index) {
  ElMessageBox.confirm('确认删除这条记录?', '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    batchResults.value.splice(index, 1)
    ElMessage.success('已删除')
  }).catch(() => {})
}

function openUpload() {
  fileInput.value && fileInput.value.click()
}

async function handleExcel(e) {
  const f = e.target.files && e.target.files[0]
  if (!f) return
  const formData = new FormData()
  formData.append('file', f)

  try {
    loading.value = true
    const resp = await fetch('/api/tunnel-support/parse-excel', { method: 'POST', body: formData })
    const data = await resp.json()
    if (resp.ok && data.count > 0) {
      // 如果有多条数据，进行批量计算
      if (data.count > 1) {
        await batchCalculate(data.data)
        ElMessage.success(`已解析 ${data.count} 条参数并完成批量计算`)
      } else {
        // 单条数据填充表单
        const first = data.data[0]
        form.value.B = Number(first.B || first.b || form.value.B)
        form.value.H = Number(first.H || first.h || form.value.H)
        form.value.K = Number(first.K || form.value.K)
        form.value.depth = Number(first.depth || first.埋深 || form.value.depth)
        form.value.gamma = Number(first.gamma || first.容重 || form.value.gamma)
        form.value.C = Number(first.C || first.粘聚力 || form.value.C)
        form.value.phi = Number(first.phi || first.内摩擦角 || form.value.phi)
        ElMessage.success('已加载参数到输入框')
      }
    } else {
      ElMessage.warning(data.detail || 'Excel 解析但没有数据')
    }
  } catch (err) {
    ElMessage.error('解析失败: ' + err)
  } finally {
    loading.value = false
    // 重置文件输入
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function batchCalculate(dataList) {
  try {
    const resp = await fetch('/api/tunnel-support/batch-calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: dataList, constants: constants.value })
    })
    const data = await resp.json()
    if (resp.ok && data.status === 'success') {
      batchResults.value = data.results
      result.value = null // 清空单次结果
    } else {
      ElMessage.error(data.detail || '批量计算失败')
    }
  } catch (err) {
    ElMessage.error('批量计算请求失败: ' + err)
  }
}

async function calculate() {
  try {
    loading.value = true
    // 调试：打印发送的参数
    console.log('发送的计算参数:', form.value)
    console.log('f_top 值:', form.value.f_top)
    
    const resp = await fetch('/api/tunnel-support/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form.value, constants: constants.value })
    })
    const data = await resp.json()
    
    // 调试：打印返回结果
    console.log('返回的计算结果:', data)
    
    if (resp.ok && data.status === 'success') {
      result.value = data.result
      batchResults.value = [] // 清空批量结果
      ElMessage.success('计算完成')
    } else {
      ElMessage.error(data.detail || '计算失败')
    }
  } catch (err) {
    ElMessage.error('请求失败: ' + err)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = { B: 4.0, H: 3.0, K: 1.0, depth: 200, gamma: 18.0, C: 0.5, phi: 30.0, f_top: 2.0 }
  result.value = null
  batchResults.value = []
}

function showConstantsDialog() {
  editingConstants.value = { ...constants.value }
  constantsDialogVisible.value = true
}

function saveConstants() {
  constants.value = { ...editingConstants.value }
  try {
    localStorage.setItem('tunnel_support_constants', JSON.stringify(constants.value))
  } catch (err) {
    console.error('保存常量失败:', err)
  }
  constantsDialogVisible.value = false
  ElMessage.success('常量已保存')
}

async function resetConstants() {
  try {
    const resp = await fetch('/api/tunnel-support/default-constants')
    const data = await resp.json()
    if (resp.ok) {
      editingConstants.value = { ...data.constants }
    }
  } catch (err) {
    console.error('重置常量失败:', err)
  }
}

function exportCsv() {
  if (!result.value) return
  const flat = {
    ...result.value.input,
    ...result.value.basic,
    ...result.value.anchor,
    ...result.value.rod
  }
  downloadCsv([flat], 'tunnel_support_result.csv')
}

function exportBatchCsv() {
  if (batchResults.value.length === 0) return
  downloadCsv(batchResults.value, 'tunnel_support_batch_results.csv')
}

function exportBatchExcel() {
  if (batchResults.value.length === 0) return
  // 简单实现：导出为 CSV 格式，用户可用 Excel 打开
  // 如果需要真正的 Excel 格式，需要安装 xlsx 库
  exportBatchCsv()
  ElMessage.info('已导出为 CSV 格式，可用 Excel 打开')
}

function downloadCsv(data, filename) {
  if (!data || data.length === 0) return
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(h => row[h]).join(','))
  ].join('\n')
  
  // 添加 BOM 以支持中文
  const bom = '\uFEFF'
  const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

function clearBatchResults() {
  ElMessageBox.confirm('确认清空所有批量结果?', '提示', {
    confirmButtonText: '清空',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    batchResults.value = []
    ElMessage.info('已清空批量结果')
  }).catch(() => {})
}

function copyToClipboard() {
  if (!result.value) return
  navigator.clipboard.writeText(JSON.stringify(result.value, null, 2))
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.tunnel-support-layout .page-header { 
  display:flex; 
  justify-content:space-between; 
  align-items:center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.page-header__titles h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
}

.page-header__titles p {
  margin: 0;
  font-size: 13px;
  opacity: 0.9;
}

.control-card { 
  margin-bottom: 12px;
}

.control-card h3,
.result-card h3,
.result-card h4 {
  margin-top: 0;
  color: #333;
}

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header-with-action h3 {
  margin: 0;
}

.result-header { 
  display:flex; 
  justify-content:space-between; 
  align-items:center;
  margin-bottom: 16px;
}

.hint { 
  color: #888;
  padding: 40px;
  text-align: center;
}

.result-body {
  margin-top: 16px;
}

.batch-results {
  margin-top: 16px;
}

.batch-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.batch-result-header h4 {
  margin: 0;
}

.input-form .el-form-item {
  margin-bottom: 18px;
}

.batch-queue-preview {
  margin-top: 12px;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.queue-header h4 {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.match-sub-card {
  min-height: 100%;
}

.match-sub-card :deep(.el-card__header) {
  padding: 12px 16px;
  background: #f5f7fa;
}

.match-result {
  margin-top: 12px;
}
</style>
