<template>
  <el-container class="key-layout">
    <el-header class="page-header">
      <div class="page-header__titles">
        <h2>关键层批量分析</h2>
        <p>按流程完成数据上传、参数填充、关键层识别与结果导出。</p>
      </div>
      <el-space wrap size="small" class="status-chips">
        <el-tag
          v-for="item in statusItems"
          :key="item.label"
          :type="item.type"
          effect="dark"
        >
          <span class="chip-label">{{ item.label }}</span>
          <span class="chip-value">{{ item.value }}</span>
        </el-tag>
      </el-space>
    </el-header>

    <el-container class="body-layout">
      <el-aside width="360px" class="control-panel">
        <el-scrollbar>
          <div class="step-list">
            <el-card shadow="never" class="step-card">
              <template #header>
                <div class="step-header">
                  <div class="step-index">1</div>
                  <div>
                    <h3 class="step-title">导入岩层数据</h3>
                    <p class="step-desc">支持多 CSV 文件批量上传，立即预览解析结果。</p>
                  </div>
                </div>
              </template>
              <div class="card-body">
                <!-- 全局数据状态提示 -->
                <div v-if="globalDataStore.keyStratumData.value.length > 0" class="data-status-info">
                  <el-icon class="status-icon"><CircleCheckFilled /></el-icon>
                  <span class="status-text">全局数据已加载</span>
                  <span class="status-count">({{ globalDataStore.keyStratumData.value.length }} 条)</span>
                </div>
                
                <!-- 数据源选择 -->
                <div class="data-source-selector">
                  <el-radio-group v-model="useGlobalData" size="default">
                    <el-radio-button :value="true">使用全局数据</el-radio-button>
                    <el-radio-button :value="false">上传新文件</el-radio-button>
                  </el-radio-group>
                </div>
                
                <!-- 上传新文件模式 -->
                <div v-if="!useGlobalData" class="action-section">
                  <input ref="fileInput" type="file" multiple accept=".csv" class="hidden-input" @change="handleFileChange" />
                  <el-row :gutter="10">
                    <el-col :span="12">
                      <el-button
                        type="primary"
                        size="large"
                        @click="triggerFileSelect"
                        :loading="isLoadingFiles"
                        class="action-button primary"
                        style="width: 100%;"
                      >
                        <el-icon><Upload /></el-icon>
                        <span>选择岩层数据文件</span>
                      </el-button>
                    </el-col>
                    <el-col :span="12">
                      <el-button
                        @click="handleFillFromDatabase"
                        :disabled="!isFilesLoaded"
                        :loading="isFilling"
                        size="large"
                        class="action-button secondary"
                        style="width: 100%;"
                      >
                        <el-icon><Search /></el-icon>
                        <span>从数据库填充参数</span>
                      </el-button>
                    </el-col>
                  </el-row>
                </div>
                
                <!-- 使用全局数据模式 -->
                <div v-else class="action-section">
                  <el-row :gutter="10">
                    <el-col :span="12">
                      <el-button
                        type="primary"
                        size="large"
                        @click="loadGlobalData"
                        :loading="isLoadingFiles"
                        :disabled="globalDataStore.keyStratumData.value.length === 0"
                        class="action-button primary"
                        style="width: 100%;"
                      >
                        <el-icon><Download /></el-icon>
                        <span>加载全局数据 ({{ globalDataStore.keyStratumData.value.length }} 条)</span>
                      </el-button>
                    </el-col>
                    <el-col :span="12">
                      <el-button
                        @click="handleFillFromDatabase"
                        :disabled="!isFilesLoaded"
                        :loading="isFilling"
                        size="large"
                        class="action-button secondary"
                        style="width: 100%;"
                      >
                        <el-icon><Search /></el-icon>
                        <span>从数据库填充参数</span>
                      </el-button>
                    </el-col>
                  </el-row>
                </div>
                
                <div class="file-summary" :class="{ 'file-summary--empty': filesInfo.count === 0 }">
                  <p v-if="filesInfo.count > 0">
                    已选择 {{ filesInfo.count }} 个文件，其中有效 {{ filesInfo.valid_count }} 个。
                  </p>
                  <p v-else>尚未选择数据文件</p>
                  <el-alert v-if="filesInfo.errors.length" type="warning" show-icon :closable="false">
                    <p>以下文件加载失败:</p>
                    <ul>
                      <li v-for="(err, i) in filesInfo.errors" :key="i">{{ err }}</li>
                    </ul>
                  </el-alert>
                </div>
              </div>
            </el-card>

            <el-card shadow="never" class="step-card">
              <template #header>
                <div class="step-header">
                  <div class="step-index">2</div>
                  <div>
                    <h3 class="step-title">确认目标岩层</h3>
                    <p class="step-desc">检测并选择包含 "煤" 的目标岩层，作为关键层计算依据。</p>
                  </div>
                </div>
              </template>
              <div class="card-body">
                <div class="button-stack">
                  <el-button
                    @click="detectCoals"
                    :disabled="!isFilesLoaded"
                    size="large"
                    class="full-button"
                  >
                    检测可用岩层
                  </el-button>
                </div>
                <el-select
                  v-model="selectedCoal"
                  placeholder="请选择目标岩层"
                  class="full-select"
                  :disabled="availableCoals.length === 0"
                  filterable
                >
                  <el-option
                    v-for="coal in availableCoals"
                    :key="coal"
                    :label="coal"
                    :value="coal"
                  />
                </el-select>
              </div>
            </el-card>

            <el-card shadow="never" class="step-card">
              <template #header>
                <div class="step-header">
                  <div class="step-index">3</div>
                  <div>
                    <h3 class="step-title">执行批量计算</h3>
                    <p class="step-desc">启动关键层识别，完成后可导出 Excel / CSV 结果。</p>
                  </div>
                </div>
              </template>
              <div class="card-body">
                <el-button
                  type="success"
                  @click="runProcessing"
                  :loading="isProcessing"
                  :disabled="!selectedCoal"
                  size="large"
                  class="full-button"
                >
                  批量计算关键层
                </el-button>
                <el-divider content-position="left">导出</el-divider>
                <div class="button-row">
                  <el-button
                    type="primary"
                    :disabled="!hasProcessed || isExporting"
                    :loading="exportState === 'xlsx'"
                    size="large"
                    class="full-button is-secondary"
                    @click="exportResults('xlsx')"
                  >
                    导出 Excel
                  </el-button>
                  <el-button
                    :disabled="!hasProcessed || isExporting"
                    :loading="exportState === 'csv'"
                    size="large"
                    class="full-button"
                    @click="exportResults('csv')"
                  >
                    导出 CSV
                  </el-button>
                </div>
                </div>
            </el-card>
          </div>
        </el-scrollbar>
      </el-aside>

      <el-main class="result-panel">
        <div class="result-stack">
          <el-card class="snapshot-card" shadow="never">
            <div class="snapshot-grid">
              <div v-for="item in summaryMetrics" :key="item.label" class="snapshot-item">
                <span class="snapshot-label">{{ item.label }}</span>
                <span class="snapshot-value">{{ item.value }}</span>
              </div>
            </div>
          </el-card>

          <el-card shadow="never" class="result-card">
            <template #header>
              <div class="card-header">
                <span>分析结果 ({{ tableTitle }})</span>
              </div>
            </template>

            <el-table
              :data="tableData"
              v-loading="isLoading"
              border
              height="calc(100vh - 260px)"
              class="result-table"
              :row-class-name="getRowClass"
              :cell-class-name="getCellClass"
            >
              <el-table-column
                v-for="column in tableColumns"
                :key="column"
                :prop="column"
                :label="column"
                min-width="150"
                sortable
                show-overflow-tooltip
              />
            </el-table>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { CircleCheckFilled, Upload, Download, Search } from '@element-plus/icons-vue';
import { getApiBase } from '@/utils/api';
import globalDataStore from '@/stores/globalData';

const API_BASE = getApiBase();
const useGlobalData = ref(true); // 默认使用全局数据
const fileInput = ref(null);
const selectedFiles = ref([]);
const isLoadingFiles = ref(false);
const isProcessing = ref(false);
const isFilling = ref(false);
const exportState = ref('');
const filesInfo = ref({ count: 0, valid_count: 0, errors: [] });
const tableData = ref([]);
const tableColumns = ref([]);
const tableTitle = ref('数据预览');
const availableCoals = ref([]);
const selectedCoal = ref(null);
const hasProcessed = ref(false);

const KEY_FLAG_COLUMN = '关键层标记';
const KEY_DISTANCE_COLUMN = '距煤层距离/m';
const KEY_COLUMN_PRIORITIES = ['钻孔名', KEY_FLAG_COLUMN, '岩层名称', KEY_DISTANCE_COLUMN];
const COAL_LABEL = '煤层';

const isLoading = computed(() => isLoadingFiles.value || isProcessing.value || isFilling.value);
const isFilesLoaded = computed(() => filesInfo.value.valid_count > 0);
const isExporting = computed(() => exportState.value !== '');
const statusItems = computed(() => [
  {
    label: '数据文件',
    value:
      filesInfo.value.count > 0
        ? `${filesInfo.value.valid_count}/${filesInfo.value.count}`
        : '未选择',
    type: filesInfo.value.valid_count > 0 ? 'success' : 'info',
  },
  {
    label: '目标岩层',
    value: selectedCoal.value || '未选择',
    type: selectedCoal.value ? 'success' : 'warning',
  },
  {
    label: '计算状态',
    value: isProcessing.value
      ? '计算中'
      : hasProcessed.value
        ? '已完成'
        : '待计算',
    type: isProcessing.value ? 'warning' : hasProcessed.value ? 'success' : 'info',
  },
]);
const summaryMetrics = computed(() => [
  {
    label: '当前数据视图',
    value: tableTitle.value,
  },
  {
    label: '可选含煤岩层',
    value: availableCoals.value.length > 0 ? `${availableCoals.value.length} 种` : '待检测',
  },
  {
    label: '已完成导出',
    value: hasProcessed.value ? '可导出' : '暂不可导出',
  },
]);

const reorderColumns = (columns = []) => {
  if (!Array.isArray(columns) || !columns.length) return [];
  const seen = new Set();
  const result = [];
  KEY_COLUMN_PRIORITIES.forEach((column) => {
    if (columns.includes(column) && !seen.has(column)) {
      result.push(column);
      seen.add(column);
    }
  });
  columns.forEach((column) => {
    if (!seen.has(column)) {
      result.push(column);
      seen.add(column);
    }
  });
  return result;
};

const resetTable = (preview) => {
  const rows = preview?.rows ?? [];
  const columns = preview?.columns ?? [];
  tableData.value = rows;
  tableColumns.value = columns;
  hasProcessed.value = false;
};

const loadGlobalData = async () => {
  console.log('loadGlobalData 被调用');
  console.log('globalDataStore:', globalDataStore);
  console.log('keyStratumData:', globalDataStore.keyStratumData);
  console.log('keyStratumData.value:', globalDataStore.keyStratumData.value);
  console.log('数据长度:', globalDataStore.keyStratumData.value.length);
  
  if (!globalDataStore.keyStratumData.value || globalDataStore.keyStratumData.value.length === 0) {
    ElMessage.warning('全局数据为空，请先在首页导入岩层数据');
    return;
  }
  
  isLoadingFiles.value = true;
  tableTitle.value = '全局数据预览';
  availableCoals.value = [];
  selectedCoal.value = null;
  
  try {
    const data = globalDataStore.keyStratumData.value;
    console.log('加载的数据:', data);
    console.log('数据条数:', data.length);
    
    const columns = data.length > 0 ? Object.keys(data[0]) : [];
    console.log('提取的列:', columns);
    
    tableData.value = data;
    tableColumns.value = columns;
    
    filesInfo.value = {
      count: 1,
      valid_count: 1,
      errors: [],
    };
    
    ElMessage.success(`已加载全局数据 (${data.length} 条记录)`);
    
    // 自动检测可用煤层
    await detectCoals();
  } catch (error) {
    console.error('加载全局数据失败:', error);
    ElMessage.error(error.message || '加载全局数据失败');
  } finally {
    isLoadingFiles.value = false;
  }
};

const triggerFileSelect = () => {
  fileInput.value?.click();
};

const handleFileChange = async (event) => {
  const files = Array.from(event.target.files || []);
  event.target.value = '';
  if (!files.length) return;
  selectedFiles.value = files;
  await uploadFiles(files);
};

const uploadFiles = async (files) => {
  isLoadingFiles.value = true;
  tableTitle.value = '数据预览';
  availableCoals.value = [];
  selectedCoal.value = null;
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  try {
    const res = await fetch(`${API_BASE}/keystratum/files`, { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok || data.status !== 'success') {
      throw new Error(data.detail || data.message || '文件加载失败');
    }
    filesInfo.value = {
      count: data.file_count || files.length,
      valid_count: data.valid_count || 0,
      errors: data.errors || [],
    };
    resetTable(data.preview);
    if (data.valid_count > 0) {
      ElMessage.success(`成功加载 ${data.valid_count} 个有效文件`);
      await detectCoals();
    } else {
      ElMessage.warning('未成功解析任何文件');
    }
  } catch (error) {
    console.error('上传岩层数据失败:', error);
    filesInfo.value = { count: files.length, valid_count: 0, errors: [error.message] };
    resetTable();
    ElMessage.error(error.message || '文件加载失败');
  } finally {
    isLoadingFiles.value = false;
  }
};

const handleFillFromDatabase = async () => {
  if (!isFilesLoaded.value) {
    ElMessage.warning('请先上传岩层数据文件');
    return;
  }
  isFilling.value = true;
  tableTitle.value = '数据填充后预览';
  try {
    const res = await fetch(`${API_BASE}/keystratum/fill`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok || data.status !== 'success') {
      throw new Error(data.detail || data.message || '填充失败');
    }
    resetTable(data.preview);
    ElMessage.success(data.message || '已根据数据库填充缺失参数');
  } catch (error) {
    console.error('填充参数失败:', error);
    ElMessage.error(error.message || '填充失败');
  } finally {
    isFilling.value = false;
  }
};

const detectCoals = async () => {
  if (!isFilesLoaded.value) return;
  
  // 如果使用全局数据,直接从前端数据中检测
  if (useGlobalData.value && tableData.value.length > 0) {
    detectCoalsFromLocalData();
    return;
  }
  
  // 否则调用后端API检测
  try {
    const res = await fetch(`${API_BASE}/keystratum/coals`);
    const data = await res.json();
    if (!res.ok || data.status !== 'success') {
      throw new Error(data.detail || data.message || '检测煤层失败');
    }
    availableCoals.value = data.coals || [];
    hasProcessed.value = false;
    if (availableCoals.value.length > 0) {
      selectedCoal.value = availableCoals.value[0];
      ElMessage.info(`检测到 ${availableCoals.value.length} 种含"煤"的岩层`);
    } else {
      ElMessage.warning('未检测到包含"煤"的岩层');
    }
  } catch (error) {
    console.error('检测煤层失败:', error);
    ElMessage.error(error.message || '检测煤层失败');
  }
};

// 从本地数据中检测含煤岩层
const detectCoalsFromLocalData = () => {
  const data = tableData.value;
  if (!data || !data.length) {
    ElMessage.warning('没有可检测的数据');
    return;
  }
  
  // 检查可能的列名
  const possibleColumns = ['岩层名称', '岩层', '名称', '岩性', '煤层'];
  let nameColumn = null;
  
  for (const col of possibleColumns) {
    if (tableColumns.value.includes(col)) {
      nameColumn = col;
      break;
    }
  }
  
  if (!nameColumn) {
    ElMessage.warning('未找到岩层名称列');
    return;
  }
  
  // 提取包含"煤"的唯一岩层名称
  const coalsSet = new Set();
  data.forEach(row => {
    const name = row[nameColumn];
    if (name && String(name).includes('煤')) {
      coalsSet.add(String(name).trim());
    }
  });
  
  availableCoals.value = Array.from(coalsSet).sort();
  hasProcessed.value = false;
  
  console.log('检测到的煤层:', availableCoals.value);
  
  if (availableCoals.value.length > 0) {
    selectedCoal.value = availableCoals.value[0];
    ElMessage.success(`从本地数据检测到 ${availableCoals.value.length} 种含"煤"的岩层`);
  } else {
    ElMessage.warning('未检测到包含"煤"的岩层');
  }
};

const runProcessing = async () => {
  if (!selectedCoal.value) {
    ElMessage.warning('请先选择目标岩层');
    return;
  }
  isProcessing.value = true;
  tableTitle.value = '计算结果';
  
  try {
    // 如果使用全局数据,需要先上传到后端再处理
    if (useGlobalData.value && tableData.value.length > 0) {
      await processWithGlobalData();
    } else {
      // 使用上传文件模式,直接调用后端API
      await processWithUploadedFiles();
    }
  } catch (error) {
    console.error('关键层计算失败:', error);
    ElMessage.error(error.message || '计算失败');
    hasProcessed.value = false;
  } finally {
    isProcessing.value = false;
  }
};

// 使用上传文件模式处理
const processWithUploadedFiles = async () => {
  const res = await fetch(`${API_BASE}/keystratum/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ coal: selectedCoal.value }),
  });
  const data = await res.json();
  if (!res.ok || data.status !== 'success') {
    throw new Error(data.detail || data.message || '计算失败');
  }
  tableData.value = data.records || [];
  tableColumns.value = reorderColumns(data.columns || []);
  hasProcessed.value = (tableData.value?.length || 0) > 0;
  const count = data.processed_count || 0;
  
  if (count > 0) {
    ElMessage.success(`计算完成，处理了 ${count} 个钻孔`);
  } else {
    ElMessage.warning('未成功处理任何钻孔');
  }
  
  if (Array.isArray(data.errors) && data.errors.length) {
    filesInfo.value.errors = data.errors;
  }
};

// 使用全局数据处理
const processWithGlobalData = async () => {
  // 将全局数据按钻孔名分组，每个钻孔一个文件
  const formData = new FormData();
  
  // 按钻孔名分组
  const boreholeGroups = {};
  tableData.value.forEach(record => {
    const boreholeName = record['钻孔名'] || 'unknown';
    if (!boreholeGroups[boreholeName]) {
      boreholeGroups[boreholeName] = [];
    }
    boreholeGroups[boreholeName].push(record);
  });
  
  console.log('钻孔分组:', Object.keys(boreholeGroups));
  console.log('各钻孔记录数:', Object.entries(boreholeGroups).map(([name, data]) => `${name}: ${data.length}条`));
  
  // 为每个钻孔创建单独的CSV文件
  let fileCount = 0;
  for (const [boreholeName, records] of Object.entries(boreholeGroups)) {
    const csv = convertTableDataToCSV(records, tableColumns.value);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    formData.append('files', blob, `${boreholeName}.csv`);
    fileCount++;
    if (fileCount === 1) {
      console.log(`${boreholeName}.csv 前200字符:`, csv.substring(0, 200));
    }
  }
  
  console.log(`准备上传 ${fileCount} 个钻孔文件`);
  
  // 先上传数据
  const uploadRes = await fetch(`${API_BASE}/keystratum/files`, {
    method: 'POST',
    body: formData,
  });
  const uploadData = await uploadRes.json();
  console.log('上传响应:', uploadData);
  
  if (!uploadRes.ok || uploadData.status !== 'success') {
    console.error('上传失败详情:', uploadData);
    throw new Error(uploadData.detail || uploadData.message || '上传数据失败');
  }
  
  console.log('上传成功，开始计算，煤层:', selectedCoal.value);
  
  // 然后进行计算
  const res = await fetch(`${API_BASE}/keystratum/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ coal: selectedCoal.value }),
  });
  const data = await res.json();
  console.log('计算响应:', data);
  if (!res.ok || data.status !== 'success') {
    if (data.errors && data.errors.length > 0) {
      console.error('计算错误详情:', data.errors);
      throw new Error(`计算失败: ${data.errors[0]}`);
    }
    throw new Error(data.detail || data.message || '计算失败');
  }
  
  tableData.value = data.records || [];
  tableColumns.value = reorderColumns(data.columns || []);
  hasProcessed.value = (tableData.value?.length || 0) > 0;
  const count = data.processed_count || 0;
  
  // 自动合并结果到全局数据
  if (hasProcessed.value && globalDataStore.keyStratumData.value.length > 0) {
    try {
      globalDataStore.mergeKeyStratumResults(tableData.value);
      ElMessage.success(`计算完成，处理了 ${count} 个钻孔，并已更新全局数据`);
    } catch (mergeError) {
      console.error('合并到全局数据失败:', mergeError);
      ElMessage.success(`计算完成，处理了 ${count} 个钻孔 (全局数据更新失败)`);
    }
  } else if (count > 0) {
    ElMessage.success(`计算完成，处理了 ${count} 个钻孔`);
  } else {
    ElMessage.warning('未成功处理任何钻孔');
  }
  
  if (Array.isArray(data.errors) && data.errors.length) {
    filesInfo.value.errors = data.errors;
  }
};

// 将表格数据转换为CSV格式
const convertTableDataToCSV = (data, columns) => {
  if (!data || !data.length) return '';
  const header = columns.join(',');
  const rows = data.map(record => 
    columns.map(col => {
      const value = record[col];
      if (value === null || value === undefined) return '';
      const strValue = String(value);
      return strValue.includes(',') ? `"${strValue}"` : strValue;
    }).join(',')
  );
  return [header, ...rows].join('\n');
};

const parseDispositionFilename = (response, fallback) => {
  const disposition = response.headers.get('Content-Disposition') || '';
  const match = disposition.match(/filename\*=UTF-8''([^;]+)/i) || disposition.match(/filename="?([^";]+)"?/i);
  if (match && match[1]) {
    try {
      return decodeURIComponent(match[1]);
    } catch (error) {
      return match[1];
    }
  }
  return fallback;
};

const exportResults = async (format = 'xlsx') => {
  if (!hasProcessed.value) {
    ElMessage.warning('请先完成关键层计算');
    return;
  }
  exportState.value = format;
  try {
    const res = await fetch(`${API_BASE}/keystratum/export?format=${format}`);
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || errData.message || '导出失败');
    }
    const blob = await res.blob();
    if (!blob.size) {
      throw new Error('导出结果为空');
    }
    const fallback = format === 'csv' ? '关键层计算结果.csv' : '关键层计算结果.xlsx';
    const filename = parseDispositionFilename(res, fallback);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    ElMessage.success('关键层计算结果已导出');
  } catch (error) {
    console.error('导出关键层结果失败:', error);
    ElMessage.error(error.message || '导出失败');
  } finally {
    exportState.value = '';
  }
};

const getRowClass = ({ row }) => {
  const flag = row?.[KEY_FLAG_COLUMN];
  if (!flag || flag === '-') {
    return '';
  }
  if (flag === COAL_LABEL) {
    return 'row-coal';
  }
  return 'row-key-stratum';
};

const getCellClass = ({ column, row }) => {
  if (column?.property === KEY_FLAG_COLUMN) {
    const flag = row?.[KEY_FLAG_COLUMN];
    if (flag === COAL_LABEL) {
      return 'cell-flag-coal';
    }
    if (flag && flag !== '-') {
      return 'cell-flag-key';
    }
    return 'cell-flag-empty';
  }
  return '';
};
</script>

<style scoped>
.key-layout {
  min-height: 100vh;
  background: #eef2fb;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 36px 16px 36px;
  background: transparent;
  border-bottom: 1px solid #dbe3f5;
}

.page-header__titles h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #1f2a44;
}

.page-header__titles p {
  margin: 6px 0 0 0;
  color: #55627a;
  font-size: 14px;
}

.status-chips {
  max-width: 420px;
  justify-content: flex-end;
}

.chip-label {
  margin-right: 6px;
  font-size: 12px;
  opacity: 0.9;
}

.chip-value {
  font-weight: 600;
}

.body-layout {
  flex: 1;
  min-height: 0;
}

.control-panel {
  padding: 24px 18px;
  box-sizing: border-box;
  background: #f5f7fb;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding-bottom: 32px;
}

.step-card {
  border-radius: 18px;
  border: none;
  overflow: hidden;
}

.step-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.step-index {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #5d7bff, #3a5bff);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.step-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.step-desc {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: #6b7a96;
}

.card-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #1f2937;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.button-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

/* START: MODIFICATION */
/* 用于水平排列、靠左对齐的按钮组 */
.button-row {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  gap: 12px;
  width: 100%;
}

/* 让 .button-row 中的按钮平分宽度 */
.button-row .full-button {
  flex: 1;
  padding: 0 12px; /* 调整内边距以适应可能变窄的空间 */
}

/* 让 .button-row 中的按钮文本居中 */
.button-row .full-button :deep(span) {
  text-align: center;
}
/* END: MODIFICATION */

/* 数据状态信息 */
.data-status-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  border-radius: 10px;
  margin-bottom: 16px;
  font-size: 13px;
}

.data-status-info .status-icon {
  font-size: 18px;
  color: #0284c7;
}

.data-status-info .status-text {
  color: #0c4a6e;
  font-weight: 500;
}

.data-status-info .status-count {
  color: #075985;
  font-weight: 600;
  margin-left: auto;
}

/* 数据源选择器 */
.data-source-selector {
  margin-bottom: 18px;
}

.data-source-selector .el-radio-group {
  display: flex;
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.data-source-selector :deep(.el-radio-button) {
  flex: 1;
  margin: 0;
}

.data-source-selector :deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-radius: 10px 0 0 10px;
}

.data-source-selector :deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 0 10px 10px 0;
}

.data-source-selector :deep(.el-radio-button__inner) {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 0;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  text-align: center;
  background: #ffffff;
  color: #64748b;
  margin: 0;
  box-shadow: none;
}

.data-source-selector :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
  box-shadow: none;
}

/* 操作区域 */
.action-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-button {
  width: 100%;
  min-height: 44px;
  height: auto;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  padding: 10px 15px !important;
  box-sizing: border-box;
  border: 1px solid transparent;
  white-space: normal;
  line-height: 1.4;
}

.action-button :deep(.el-icon) {
  font-size: 16px;
  margin-right: 0;
  flex-shrink: 0;
}

.action-button :deep(span) {
  display: inline-flex;
  align-items: center;
  white-space: normal;
  word-break: break-word;
  text-align: center;
}

/* 主按钮样式 */
.action-button.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
  border-color: transparent !important;
  color: #ffffff !important;
}

.action-button.primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.action-button.primary:disabled {
  background: #cbd5e1 !important;
  color: #94a3b8 !important;
  cursor: not-allowed;
  opacity: 0.6;
}

/* 次要按钮样式 */
.action-button.secondary {
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
  color: #475569 !important;
}

.action-button.secondary:hover:not(:disabled) {
  background: #e2e8f0 !important;
  border-color: #cbd5e1 !important;
  color: #334155 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.action-button.secondary:disabled {
  background: #f8fafc !important;
  border-color: #f1f5f9 !important;
  color: #cbd5e1 !important;
  cursor: not-allowed;
  opacity: 0.6;
}


.full-button {
  box-sizing: border-box;
  min-height: 44px;
  display: flex;
  width: 100%;
  justify-content: flex-start;
  align-items: center;
  padding: 0 18px;
}

.full-button :deep(.el-button) {
  padding: 0 !important;
}

.full-button :deep(span) {
  width: 100%;
  text-align: left;
  display: inline-block;
}

.full-select {
  width: 100%;
}

.file-summary {
  margin-top: 16px;
  padding: 12px 14px;
  background-color: #f9fafb;
  border-radius: 12px;
  font-size: 13px;
  color: #475569;
}

.file-summary--empty {
  background-color: #f1f5f9;
  color: #64748b;
}

.file-summary ul {
  padding-left: 18px;
  margin: 6px 0 0 0;
}

.hidden-input {
  display: none;
}

.result-panel {
  padding: 24px 32px 36px 18px;
  background: transparent;
  display: flex;
  flex-direction: column;
}

.result-stack {
  display: flex;
  flex-direction: column;
  gap: 18px;
  flex: 1;
}

.snapshot-card {
  border-radius: 20px;
  border: none;
}

.snapshot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.snapshot-item {
  padding: 12px 14px;
  background: #f3f6ff;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.snapshot-label {
  font-size: 12px;
  color: #67738d;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.snapshot-value {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.result-card {
  height: 100%;
  border-radius: 20px;
  border: none;
}

.result-table {
  --el-table-tr-bg-color: transparent;
}

.row-key-stratum td {
  background-color: #fef3c7 !important;
}

.row-coal td {
  background-color: #dbeafe !important;
}

.cell-flag-key {
  font-weight: 700;
  color: #d97706;
}

.cell-flag-coal {
  font-weight: 700;
  color: #1d4ed8;
}

.cell-flag-empty {
  color: #94a3b8;
}
</style>