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
          查看常量
        </el-button>
      </el-space>
      <input ref="fileInput" type="file" accept=".xlsx,.xls" @change="handleExcel" style="display:none" />
    </el-header>

    <el-main>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="never" class="control-card">
            <h3>输入参数</h3>
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
              <el-form-item>
                <el-button type="primary" @click="calculate" :loading="loading">计算</el-button>
                <el-button @click="resetForm" style="margin-left:8px">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-card shadow="never" class="result-card">
            <div class="result-header">
              <h3>计算结果</h3>
              <div>
                <el-button type="success" @click="exportCsv" :disabled="!result">导出 CSV</el-button>
                <el-button @click="copyToClipboard" :disabled="!result" style="margin-left:8px">复制结果</el-button>
              </div>
            </div>

            <div v-if="!result && batchResults.length === 0">
              <p class="hint">请填写参数并点击"计算"，或导入包含列 (B,H,应力集中系数K,埋深,容重,粘聚力,内摩擦角) 的 Excel 文件。</p>
            </div>

            <!-- 单次计算结果 -->
            <div v-if="result && batchResults.length === 0" class="result-body">
              <el-descriptions column="2" border>
                <el-descriptions-item label="R (m)">{{ result.basic.R }}</el-descriptions-item>
                <el-descriptions-item label="hct (m)">{{ result.basic.hct }}</el-descriptions-item>
                <el-descriptions-item label="hcs (m)">{{ result.basic.hcs }}</el-descriptions-item>
                <el-descriptions-item label="hat (m)">{{ result.basic.hat }}</el-descriptions-item>
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
              <h4>批量计算结果 ({{ batchResults.length }} 条)</h4>
              <el-table :data="batchResults" style="width:100%" max-height="500" border stripe>
                <el-table-column type="index" label="#" width="50"></el-table-column>
                <el-table-column prop="B" label="B (m)" width="80"></el-table-column>
                <el-table-column prop="H" label="H (m)" width="80"></el-table-column>
                <el-table-column prop="R(m)" label="R (m)" width="90"></el-table-column>
                <el-table-column prop="hct(m)" label="hct (m)" width="90"></el-table-column>
                <el-table-column prop="hcs(m)" label="hcs (m)" width="90"></el-table-column>
                <el-table-column prop="Nt_anchor(kN)" label="锚索 Nt (kN)" width="120"></el-table-column>
                <el-table-column prop="L_total_anchor(m)" label="锚索长度 (m)" width="120"></el-table-column>
                <el-table-column prop="Nt_rod(kN)" label="锚杆 Nt (kN)" width="120"></el-table-column>
                <el-table-column prop="L_top(m)" label="顶锚杆长 (m)" width="120"></el-table-column>
                <el-table-column prop="L_side(m)" label="侧锚杆长 (m)" width="120"></el-table-column>
              </el-table>
              <div style="margin-top: 12px">
                <el-button type="success" @click="exportBatchCsv">
                  <el-icon><Download /></el-icon>
                  导出批量结果 CSV
                </el-button>
                <el-button @click="clearBatchResults" style="margin-left:8px">清空批量结果</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 常量查看对话框 -->
      <el-dialog v-model="constantsDialogVisible" title="默认计算常量" width="600px">
        <el-descriptions :column="2" border v-if="constants">
          <el-descriptions-item label="Sn (mm²)">{{ constants.Sn }}</el-descriptions-item>
          <el-descriptions-item label="安全系数 K">{{ constants.safety_K }}</el-descriptions-item>
          <el-descriptions-item label="锚索抗拉强度 (MPa)">{{ constants.Rm_anchor }}</el-descriptions-item>
          <el-descriptions-item label="锚杆抗拉强度 (MPa)">{{ constants.Rm_rod }}</el-descriptions-item>
          <el-descriptions-item label="锚索设计荷载 (kN)">{{ constants.Q_anchor }}</el-descriptions-item>
          <el-descriptions-item label="锚杆设计荷载 (kN)">{{ constants.Q_rod }}</el-descriptions-item>
          <el-descriptions-item label="树脂锚固力 (MPa)">{{ constants.c0 }}</el-descriptions-item>
          <el-descriptions-item label="锚杆锚固力 (MPa)">{{ constants.tau_rod }}</el-descriptions-item>
          <el-descriptions-item label="锚索半径 (mm)">{{ constants.R_mm }}</el-descriptions-item>
          <el-descriptions-item label="锚杆直径 (mm)">{{ constants.D_mm }}</el-descriptions-item>
          <el-descriptions-item label="工作状态系数 m">{{ constants.m }}</el-descriptions-item>
          <el-descriptions-item label="根数 n">{{ constants.n }}</el-descriptions-item>
        </el-descriptions>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Setting, Download } from '@element-plus/icons-vue'

const form = ref({ B: 4.0, H: 3.0, K: 1.0, depth: 200, gamma: 18.0, C: 0.5, phi: 30.0 })
const loading = ref(false)
const result = ref(null)
const batchResults = ref([])
const fileInput = ref(null)
const constantsDialogVisible = ref(false)
const constants = ref(null)

onMounted(async () => {
  // 加载默认常量
  try {
    const resp = await fetch('/api/tunnel-support/default-constants')
    const data = await resp.json()
    if (resp.ok) {
      constants.value = data.constants
    }
  } catch (err) {
    console.error('加载常量失败:', err)
  }
})

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
      body: JSON.stringify({ data: dataList })
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
    const resp = await fetch('/api/tunnel-support/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    const data = await resp.json()
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
  form.value = { B: 4.0, H: 3.0, K: 1.0, depth: 200, gamma: 18.0, C: 0.5, phi: 30.0 }
  result.value = null
  batchResults.value = []
}

function showConstantsDialog() {
  constantsDialogVisible.value = true
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
  batchResults.value = []
  ElMessage.info('已清空批量结果')
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

.input-form .el-form-item {
  margin-bottom: 18px;
}
</style>
