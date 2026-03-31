<template>
  <el-container class="page">
    <el-header class="header">
      <div>
        <h2>巷道支护计算</h2>
        <p>按更新后的公式计算松动圈、锚索、锚杆、托板承载力和间排距。</p>
      </div>
      <el-space>
        <el-button size="small" type="primary" @click="openUpload"><el-icon><Upload /></el-icon>导入 Excel</el-button>
        <el-button size="small" type="success" @click="showConstantsDialog"><el-icon><Setting /></el-icon>常量设置</el-button>
      </el-space>
      <input ref="fileInput" type="file" accept=".xlsx,.xls" style="display:none" @change="handleExcel" />
    </el-header>

    <el-main>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="never">
            <div class="row between">
              <h3>输入参数</h3>
              <el-button size="small" @click="addToBatch" :disabled="!form.B || !form.H"><el-icon><Plus /></el-icon>加入批量</el-button>
            </div>
            <el-form :model="form" label-width="120px">
              <el-form-item label="巷道宽度 B (m)"><el-input-number v-model="form.B" :step="0.1" :min="0" style="width:100%" /></el-form-item>
              <el-form-item label="巷道高度 H (m)"><el-input-number v-model="form.H" :step="0.1" :min="0" style="width:100%" /></el-form-item>
              <el-form-item label="应力集中系数 K"><el-input-number v-model="form.K" :step="0.1" style="width:100%" /></el-form-item>
              <el-form-item label="埋深 (m)"><el-input-number v-model="form.depth" :step="0.1" :min="0" style="width:100%" /></el-form-item>
              <el-form-item label="容重 (kN/m³)"><el-input-number v-model="form.gamma" :step="0.1" :min="0" style="width:100%" /></el-form-item>
              <el-form-item label="黏聚力 C (MPa)"><el-input-number v-model="form.C" :step="0.01" :min="0" style="width:100%" /></el-form-item>
              <el-form-item label="内摩擦角 φ (°)"><el-input-number v-model="form.phi" :step="0.1" :min="0.1" style="width:100%" /></el-form-item>
              <el-form-item label="顶板普氏系数 f"><el-input-number v-model="form.f_top" :step="0.1" :min="0.1" style="width:100%" /></el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="loading" @click="calculate">计算</el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>

            <div v-if="batchQueue.length">
              <el-divider />
              <div class="row between">
                <h4>批量队列 ({{ batchQueue.length }})</h4>
                <el-space>
                  <el-button size="small" type="primary" :loading="loading" @click="calculateBatchQueue">批量计算</el-button>
                  <el-button size="small" @click="clearQueue">清空</el-button>
                </el-space>
              </div>
              <el-table :data="batchQueue" size="small" max-height="220" stripe>
                <el-table-column type="index" label="#" width="44" />
                <el-table-column prop="B" label="B" width="64" />
                <el-table-column prop="H" label="H" width="64" />
                <el-table-column prop="K" label="K" width="64" />
                <el-table-column label="操作" width="80">
                  <template #default="{ $index }"><el-button type="danger" text size="small" @click="removeFromQueue($index)">删除</el-button></template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-card shadow="never">
            <div class="row between">
              <h3>计算结果</h3>
              <el-space>
                <el-button size="small" type="success" :disabled="!result" @click="exportSingle"><el-icon><Download /></el-icon>导出 CSV</el-button>
                <el-button size="small" :disabled="!result" @click="copyResult"><el-icon><CopyDocument /></el-icon>复制结果</el-button>
              </el-space>
            </div>

            <div v-if="!result && !filteredBatchResults.length" class="hint">填写参数后点击“计算”，或导入 Excel 进行批量计算。</div>

            <div v-if="result && !filteredBatchResults.length">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="塑性区半径 R">{{ result.basic.R }} m</el-descriptions-item>
                <el-descriptions-item label="顶板松动圈 h顶">{{ result.basic.hct }} m</el-descriptions-item>
                <el-descriptions-item label="两帮松动圈 h帮">{{ result.basic.hcs }} m</el-descriptions-item>
                <el-descriptions-item label="压力拱高度 h拱">{{ result.basic.hat }} m</el-descriptions-item>
                <el-descriptions-item label="顶板松动圈深度 Lb">{{ result.basic.Lb }} m</el-descriptions-item>
              </el-descriptions>
              <el-divider />
              <h4>锚索设计</h4>
              <el-table :data="[result.anchor]" border>
                <el-table-column prop="Nt" label="N1 / Nt (kN)" />
                <el-table-column prop="diameter" label="直径 (mm)" />
                <el-table-column prop="Lm" label="Lm (m)" />
                <el-table-column prop="L_resin" label="L药 (m)" />
                <el-table-column prop="L_total" label="L (m)" />
                <el-table-column prop="plate_capacity_min" label="Tb (kN)" />
                <el-table-column prop="spacing_area" label="a*b (m²)" />
              </el-table>
              <el-divider />
              <h4>锚杆设计</h4>
              <el-table :data="[result.rod]" border>
                <el-table-column prop="Nt" label="N2 (kN)" />
                <el-table-column prop="diameter" label="直径 (mm)" />
                <el-table-column prop="L3" label="L3 (m)" />
                <el-table-column prop="L_resin" label="L药 (m)" />
                <el-table-column prop="L_top" label="L顶 (m)" />
                <el-table-column prop="L_side" label="L帮 (m)" />
                <el-table-column prop="plate_capacity_min" label="Q托盘 (kN)" />
                <el-table-column prop="spacing_area_top" label="顶部 a*b (m²)" />
                <el-table-column prop="spacing_area_side" label="帮部 a*b (m²)" />
              </el-table>
            </div>

            <div v-if="filteredBatchResults.length">
              <div class="row between">
                <h4>批量结果 ({{ filteredBatchResults.length }})</h4>
                <el-space>
                  <el-input v-model="searchText" size="small" clearable placeholder="搜索..." style="width:220px"><template #prefix><el-icon><Search /></el-icon></template></el-input>
                  <el-button size="small" type="success" @click="exportBatch"><el-icon><Download /></el-icon>导出 CSV</el-button>
                </el-space>
              </div>
              <el-table :data="filteredBatchResults" border stripe max-height="520">
                <el-table-column type="index" label="#" width="48" />
                <el-table-column prop="B" label="B (m)" width="80" sortable />
                <el-table-column prop="H" label="H (m)" width="80" sortable />
                <el-table-column prop="R(m)" label="R (m)" width="90" sortable />
                <el-table-column prop="Lb(m)" label="Lb (m)" width="90" sortable />
                <el-table-column prop="Nt_anchor(kN)" label="锚索 Nt" width="110" sortable />
                <el-table-column prop="L_total_anchor(m)" label="锚索总长" width="110" sortable />
                <el-table-column prop="Nt_rod(kN)" label="锚杆 N2" width="110" sortable />
                <el-table-column prop="L_top(m)" label="L顶 (m)" width="100" sortable />
                <el-table-column prop="L_side(m)" label="L帮 (m)" width="100" sortable />
                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="{ row, $index }">
                    <el-button type="primary" text size="small" @click="viewDetail(row)">详情</el-button>
                    <el-button type="danger" text size="small" @click="deleteRow($index)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card shadow="never" class="card-gap">
        <h3>支护材料匹配性分析</h3>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form :model="matchForm" label-width="130px" size="small">
              <el-form-item label="锚杆直径 (mm)"><el-input-number v-model="matchForm.rodDiameter" :step="1" :min="4" style="width:100%" /></el-form-item>
              <el-form-item label="锚杆牌号">
                <el-select v-model="matchForm.rodGrade" style="width:100%" @change="onRodGradeChange">
                  <el-option v-for="item in anchorMaterialData" :key="item.grade" :label="item.grade" :value="item.grade" />
                </el-select>
              </el-form-item>
              <el-form-item label="屈服强度 (MPa)"><el-input-number v-model="matchForm.rodYieldStrength" :step="5" :min="0" style="width:100%" /></el-form-item>
              <el-form-item label="托盘承载力 (kN)"><el-input-number v-model="matchForm.plateCapacityRod" :step="5" :min="0" style="width:100%" /></el-form-item>
            </el-form>
          </el-col>
          <el-col :span="12">
            <el-form :model="matchForm" label-width="140px" size="small">
              <el-form-item label="锚索设计承载力 Nt"><el-input-number v-model="matchForm.anchorNt" :step="5" :min="0" style="width:100%" /></el-form-item>
              <el-form-item label="托板承载力 Tb"><el-input-number v-model="matchForm.plateCapacityAnchor" :step="5" :min="0" style="width:100%" /></el-form-item>
            </el-form>
            <el-button type="primary" :loading="matchLoading" @click="calculateMaterialMatch">分析匹配性</el-button>
            <el-button @click="resetMatchForm">重置</el-button>
          </el-col>
        </el-row>
        <el-row v-if="matchResult" :gutter="20" class="match-result">
          <el-col :span="12">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="锚杆屈服力">{{ matchResult.rod.rod_yield_force_kN }} kN</el-descriptions-item>
              <el-descriptions-item label="托盘下限">{{ matchResult.rod.plate_required_kN }} kN</el-descriptions-item>
              <el-descriptions-item label="匹配结果"><el-tag :type="matchResult.rod.matched ? 'success' : 'danger'">{{ matchResult.rod.matched ? '满足' : '不满足' }}</el-tag></el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="锚索设计承载力">{{ matchResult.anchor.Nt_kN }} kN</el-descriptions-item>
              <el-descriptions-item label="托板下限">{{ matchResult.anchor.plate_required_kN }} kN</el-descriptions-item>
              <el-descriptions-item label="匹配结果"><el-tag :type="matchResult.anchor.matched ? 'success' : 'danger'">{{ matchResult.anchor.matched ? '满足' : '不满足' }}</el-tag></el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
      </el-card>

      <el-dialog v-model="constantsDialogVisible" title="计算常量设置" width="680px">
        <el-form v-if="editingConstants" :model="editingConstants" label-width="170px">
          <el-form-item label="锚索截面积 Sn (mm²)"><el-input-number v-model="editingConstants.Sn" :step="1" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚索抗拉强度 (MPa)"><el-input-number v-model="editingConstants.Rm_anchor" :step="10" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚索钻孔半径 (mm)"><el-input-number v-model="editingConstants.anchor_hole_radius_mm" :step="0.5" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚索树脂半径 (mm)"><el-input-number v-model="editingConstants.anchor_resin_radius_mm" :step="0.5" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚索托板厚度 (m)"><el-input-number v-model="editingConstants.anchor_plate_thickness_m" :step="0.05" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚索外露长度 (m)"><el-input-number v-model="editingConstants.anchor_exposed_length_m" :step="0.05" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚杆直径 (mm)"><el-input-number v-model="editingConstants.rod_diameter_mm" :step="1" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚杆屈服强度 (MPa)"><el-input-number v-model="editingConstants.Rm_rod" :step="10" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚杆钻孔半径 (mm)"><el-input-number v-model="editingConstants.rod_hole_radius_mm" :step="0.5" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚杆树脂半径 (mm)"><el-input-number v-model="editingConstants.rod_resin_radius_mm" :step="0.5" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="锚杆外露长度 (m)"><el-input-number v-model="editingConstants.rod_exposed_length_m" :step="0.05" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="树脂粘结强度 c0 (MPa)"><el-input-number v-model="editingConstants.c0" :step="0.1" :min="0" style="width:100%" /></el-form-item>
          <el-form-item label="安全系数 K"><el-input-number v-model="editingConstants.safety_K" :step="0.1" :min="0.1" style="width:100%" /></el-form-item>
          <el-form-item label="锚索张拉控制系数 m"><el-input-number v-model="editingConstants.m" :step="0.1" :min="0" :max="1" style="width:100%" /></el-form-item>
          <el-form-item label="钢绞线根数 n"><el-input-number v-model="editingConstants.n" :step="1" :min="1" style="width:100%" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="resetConstants">恢复默认</el-button>
          <el-button @click="constantsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveConstants">保存</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="detailDialogVisible" title="计算详情" width="820px">
        <el-descriptions v-if="detailRow" :column="2" border>
          <el-descriptions-item label="B">{{ detailRow.B }} m</el-descriptions-item>
          <el-descriptions-item label="H">{{ detailRow.H }} m</el-descriptions-item>
          <el-descriptions-item label="R">{{ detailRow['R(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="Lb">{{ detailRow['Lb(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="锚索树脂长度">{{ detailRow['L_resin_anchor(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="锚索托板下限">{{ detailRow['Tb_anchor(kN)'] }} kN</el-descriptions-item>
          <el-descriptions-item label="锚索间排距">{{ detailRow['a*b_anchor(m2)'] }} m²</el-descriptions-item>
          <el-descriptions-item label="锚杆 L3">{{ detailRow['L3_rod(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="锚杆树脂长度">{{ detailRow['L_resin_rod(m)'] }} m</el-descriptions-item>
          <el-descriptions-item label="锚杆托盘下限">{{ detailRow['Q_tray_rod(kN)'] }} kN</el-descriptions-item>
          <el-descriptions-item label="顶部间排距">{{ detailRow['a*b_top(m2)'] }} m²</el-descriptions-item>
          <el-descriptions-item label="帮部间排距">{{ detailRow['a*b_side(m2)'] }} m²</el-descriptions-item>
        </el-descriptions>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CopyDocument, Download, Plus, Search, Setting, Upload } from '@element-plus/icons-vue'

const form = ref({ B: 4.0, H: 3.0, K: 1.0, depth: 200, gamma: 18.0, C: 0.5, phi: 30.0, f_top: 2.0 })
const loading = ref(false)
const result = ref(null)
const batchResults = ref([])
const batchQueue = ref([])
const constants = ref(null)
const editingConstants = ref(null)
const constantsDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const detailRow = ref(null)
const searchText = ref('')
const fileInput = ref(null)
const matchLoading = ref(false)
const matchResult = ref(null)
const matchForm = ref({ rodDiameter: 20, rodGrade: 'BHRB400', rodYieldStrength: 400, plateCapacityRod: 200, anchorNt: 349.3, plateCapacityAnchor: 600 })
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

const filteredBatchResults = computed(() => !searchText.value ? batchResults.value : batchResults.value.filter(row => Object.values(row).some(v => String(v).toLowerCase().includes(searchText.value.toLowerCase()))))
const normalizeConstants = raw => ({ Sn: raw.Sn ?? 313, Rm_anchor: raw.Rm_anchor ?? 1860, anchor_hole_radius_mm: raw.anchor_hole_radius_mm ?? raw.R_mm ?? 15, anchor_resin_radius_mm: raw.anchor_resin_radius_mm ?? 12.5, anchor_plate_thickness_m: raw.anchor_plate_thickness_m ?? 0.2, anchor_exposed_length_m: raw.anchor_exposed_length_m ?? 0.3, rod_diameter_mm: raw.rod_diameter_mm ?? raw.D_mm ?? 20, Rm_rod: raw.Rm_rod ?? 460, rod_hole_radius_mm: raw.rod_hole_radius_mm ?? raw.tau_rod ?? 14, rod_resin_radius_mm: raw.rod_resin_radius_mm ?? 12.5, rod_exposed_length_m: raw.rod_exposed_length_m ?? 0.1, c0: raw.c0 ?? 3, safety_K: raw.safety_K ?? 2, m: raw.m ?? 0.6, n: raw.n ?? 1 })

const fetchJson = async (url, options) => { const resp = await fetch(url, options); const data = await resp.json(); return { resp, data } }
const downloadCsv = (rows, name) => { if (!rows.length) return; const headers = Object.keys(rows[0]); const csv = [headers.join(','), ...rows.map(row => headers.map(k => JSON.stringify(row[k] ?? '')).join(','))].join('\n'); const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = name; a.click(); URL.revokeObjectURL(url) }

async function loadConstants() { try { const { resp, data } = await fetchJson('/api/tunnel-support/default-constants'); constants.value = normalizeConstants(resp.ok ? data.constants : {}); } catch { constants.value = normalizeConstants({}) } }
function openUpload() { fileInput.value?.click() }
function addToBatch() { if (!form.value.B || !form.value.H) return ElMessage.warning('请先填写完整参数'); batchQueue.value.push({ ...form.value }); ElMessage.success(`已加入批量队列 (${batchQueue.value.length})`) }
function removeFromQueue(index) { batchQueue.value.splice(index, 1) }
function clearQueue() { batchQueue.value = [] }
async function calculateBatchQueue() { if (!batchQueue.value.length) return ElMessage.warning('批量队列为空'); await batchCalculate(batchQueue.value); batchQueue.value = [] }
function onRodGradeChange(grade) { const item = anchorMaterialData.find(v => v.grade === grade); if (item) matchForm.value.rodYieldStrength = item.yieldStrength }

async function handleExcel(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const formData = new FormData(); formData.append('file', file)
  try {
    loading.value = true
    const { resp, data } = await fetchJson('/api/tunnel-support/parse-excel', { method: 'POST', body: formData })
    if (!(resp.ok && data.count > 0)) return ElMessage.warning(data.detail || 'Excel 解析失败')
    if (data.count > 1) return await batchCalculate(data.data)
    const row = data.data[0]
    form.value = { ...form.value, B: Number(row.B ?? row.b ?? form.value.B), H: Number(row.H ?? row.h ?? form.value.H), K: Number(row.K ?? form.value.K), depth: Number(row.depth ?? row.埋深 ?? form.value.depth), gamma: Number(row.gamma ?? row.容重 ?? form.value.gamma), C: Number(row.C ?? row.粘聚力 ?? form.value.C), phi: Number(row.phi ?? row.内摩擦角 ?? form.value.phi), f_top: Number(row.f_top ?? form.value.f_top) }
    ElMessage.success('已将 Excel 参数填入表单')
  } catch (err) { ElMessage.error(`Excel 解析失败: ${err}`) } finally { loading.value = false; if (fileInput.value) fileInput.value.value = '' }
}

async function batchCalculate(dataList) {
  try {
    loading.value = true
    const { resp, data } = await fetchJson('/api/tunnel-support/batch-calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ data: dataList, constants: constants.value }) })
    if (resp.ok && data.status === 'success') { batchResults.value = data.results; result.value = null; ElMessage.success('批量计算完成'); return }
    ElMessage.error(data.detail || '批量计算失败')
  } catch (err) { ElMessage.error(`批量计算失败: ${err}`) } finally { loading.value = false }
}

async function calculate() {
  try {
    loading.value = true
    const { resp, data } = await fetchJson('/api/tunnel-support/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...form.value, constants: constants.value }) })
    if (resp.ok && data.status === 'success') { result.value = data.result; batchResults.value = []; matchForm.value.anchorNt = data.result.anchor.Nt; matchForm.value.rodDiameter = data.result.rod.diameter; ElMessage.success('计算完成'); return }
    ElMessage.error(data.detail || '计算失败')
  } catch (err) { ElMessage.error(`请求失败: ${err}`) } finally { loading.value = false }
}

function resetForm() { form.value = { B: 4.0, H: 3.0, K: 1.0, depth: 200, gamma: 18.0, C: 0.5, phi: 30.0, f_top: 2.0 }; result.value = null; batchResults.value = [] }
function exportSingle() { if (!result.value) return; downloadCsv([{ ...result.value.input, ...result.value.basic, ...result.value.anchor, ...result.value.rod }], 'tunnel_support_result.csv'); ElMessage.success('结果已导出') }
function exportBatch() { if (!batchResults.value.length) return; downloadCsv(batchResults.value, 'tunnel_support_batch_results.csv'); ElMessage.success('批量结果已导出') }
function copyResult() { if (!result.value) return; navigator.clipboard.writeText(JSON.stringify(result.value, null, 2)); ElMessage.success('结果已复制') }
function viewDetail(row) { detailRow.value = row; detailDialogVisible.value = true }
function deleteRow(index) { ElMessageBox.confirm('确认删除这条记录？', '提示', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }).then(() => batchResults.value.splice(index, 1)).catch(() => {}) }
function showConstantsDialog() { editingConstants.value = normalizeConstants(constants.value || {}); constantsDialogVisible.value = true }
function saveConstants() { constants.value = normalizeConstants(editingConstants.value || {}); localStorage.setItem('tunnel_support_constants', JSON.stringify(constants.value)); constantsDialogVisible.value = false; ElMessage.success('常量已保存') }
async function resetConstants() { await loadConstants(); editingConstants.value = normalizeConstants(constants.value || {}) }

async function calculateMaterialMatch() {
  try {
    matchLoading.value = true
    const { resp, data } = await fetchJson('/api/tunnel-support/material-match', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ rod_diameter_mm: matchForm.value.rodDiameter, rod_grade: matchForm.value.rodGrade, rod_yield_strength: matchForm.value.rodYieldStrength, plate_capacity_rod: matchForm.value.plateCapacityRod, anchor_Nt: matchForm.value.anchorNt, plate_capacity_anchor: matchForm.value.plateCapacityAnchor }) })
    if (resp.ok && data.status === 'success') { matchResult.value = data; ElMessage.success('匹配性分析完成'); return }
    ElMessage.error(data.detail || '匹配性分析失败')
  } catch (err) { ElMessage.error(`请求失败: ${err}`) } finally { matchLoading.value = false }
}
function resetMatchForm() { matchForm.value = { rodDiameter: 20, rodGrade: 'BHRB400', rodYieldStrength: 400, plateCapacityRod: 200, anchorNt: 349.3, plateCapacityAnchor: 600 }; matchResult.value = null }

onMounted(async () => { await loadConstants(); try { const saved = localStorage.getItem('tunnel_support_constants'); if (saved) constants.value = normalizeConstants({ ...constants.value, ...JSON.parse(saved) }) } catch {} })
</script>

<style scoped>
.page .header{display:flex;justify-content:space-between;align-items:center;padding:16px 20px;background:linear-gradient(135deg,#0f766e,#2563eb);color:#fff}.header h2{margin:0 0 4px}.header p{margin:0;font-size:13px;opacity:.9}.row{display:flex;align-items:center}.between{justify-content:space-between}.hint{padding:40px 24px;text-align:center;color:#64748b}.card-gap{margin-top:16px}.match-result{margin-top:16px}
</style>
