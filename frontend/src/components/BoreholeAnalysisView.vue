<template>
  <div class="page-container">
    <h1>钻孔数据批量分析</h1>
    
    <el-card class="box-card">
      <el-alert 
        v-if="globalDataStore.boreholeData.value.length > 0" 
        type="info" 
        :closable="false"
        style="margin-bottom: 16px;"
      >
        <template #title>
          全局数据已加载 ({{ globalDataStore.boreholeData.value.length }} 条记录)
        </template>
      </el-alert>
      
      <el-radio-group v-model="useGlobalData" size="large" style="margin-bottom: 16px;">
        <el-radio-button :value="true">使用全局数据</el-radio-button>
        <el-radio-button :value="false">上传新文件</el-radio-button>
      </el-radio-group>
      
      <div class="control-section">
        <div v-if="!useGlobalData">
          <input ref="fileInput" type="file" class="hidden-input" multiple accept=".csv" @change="handleFileChange" />
          <el-button type="primary" @click="triggerFileSelect" :loading="isProcessing">选择钻孔 CSV 文件</el-button>
          <span v-if="selectedFiles.length > 0" class="file-info">
            已选择 {{ selectedFiles.length }} 个文件
          </span>
        </div>
        <div v-else>
          <el-button 
            type="primary" 
            @click="loadGlobalData" 
            :loading="isProcessing"
            :disabled="globalDataStore.boreholeData.value.length === 0"
          >
            加载全局数据
          </el-button>
          <span v-if="tableData.length > 0" class="file-info">
            已加载 {{ tableData.length }} 条记录
          </span>
        </div>
      </div>
      
      <div v-if="summary" class="summary-section">
        <h3>处理摘要</h3>
        <div class="summary-stats">
          <el-tag type="info" size="large">总文件: {{ summary.total_files }}</el-tag>
          <el-tag type="success" size="large">成功: {{ summary.successful_files }}</el-tag>
          <el-tag v-if="summary.warning_files > 0" type="warning" size="large">警告: {{ summary.warning_files }}</el-tag>
          <el-tag v-if="summary.failed_files > 0" type="danger" size="large">失败: {{ summary.failed_files }}</el-tag>
          <el-tag type="primary" size="large">煤层记录: {{ summary.total_coal_records }}</el-tag>
          <el-tag v-if="summary.processing_time" size="large">耗时: {{ summary.processing_time }}s</el-tag>
        </div>
        
        <el-alert v-if="summary.warning_details && summary.warning_details.length > 0" type="warning" title="警告详情" :closable="false" style="margin-top: 12px;">
          <ul>
            <li v-for="(warn, index) in summary.warning_details.slice(0, 5)" :key="index">{{ warn }}</li>
            <li v-if="summary.warning_details.length > 5">... 还有 {{ summary.warning_details.length - 5 }} 个警告</li>
          </ul>
        </el-alert>
        
        <el-alert v-if="summary.error_details && summary.error_details.length > 0" type="error" title="错误详情" :closable="false" style="margin-top: 12px;">
          <ul>
            <li v-for="(err, index) in summary.error_details.slice(0, 5)" :key="index">{{ err }}</li>
            <li v-if="summary.error_details.length > 5">... 还有 {{ summary.error_details.length - 5 }} 个错误</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <el-card class="box-card" style="margin-top: 20px;">
       <div class="filter-section">
        <el-select v-model="coalFilter" placeholder="按煤层筛选" clearable>
          <el-option v-for="coal in uniqueCoals" :key="coal" :label="coal" :value="coal"></el-option>
        </el-select>
        <el-select v-model="boreholeFilter" placeholder="按钻孔筛选" clearable>
           <el-option v-for="hole in uniqueBoreholes" :key="hole" :label="hole" :value="hole"></el-option>
        </el-select>
      </div>

      <el-table :data="filteredData" border stripe v-loading="isProcessing" height="calc(100vh - 400px)">
        <el-table-column v-for="col in tableColumns" :key="col" :prop="col" :label="col" sortable show-overflow-tooltip min-width="150"></el-table-column>
      </el-table>
    </el-card>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { getApiBase } from '@/utils/api';
import globalDataStore from '@/stores/globalData';

const API_BASE = getApiBase();
const useGlobalData = ref(true); // 默认使用全局数据
const isProcessing = ref(false);
const fileInput = ref(null);
const selectedFiles = ref([]);
const tableData = ref([]);
const tableColumns = ref([]);
const summary = ref(null);
const coalFilter = ref('');
const boreholeFilter = ref('');

const defaultSummary = () => ({
  total_files: 0,
  successful_files: 0,
  failed_files: 0,
  warning_files: 0,
  total_coal_records: 0,
  error_details: [],
  warning_details: [],
  processing_time: 0,
});

const loadGlobalData = () => {
  if (globalDataStore.boreholeData.value.length === 0) {
    ElMessage.warning('全局数据为空，请先在首页导入数据');
    return;
  }
  
  isProcessing.value = true;
  
  try {
    const data = globalDataStore.boreholeData.value;
    const columns = data.length > 0 ? Object.keys(data[0]) : [];
    
    tableData.value = data;
    tableColumns.value = columns;
    
    summary.value = {
      total_files: 1,
      successful_files: 1,
      failed_files: 0,
      warning_files: 0,
      total_coal_records: data.length,
      error_details: [],
      warning_details: [],
      processing_time: 0,
    };
    
    ElMessage.success(`已加载全局数据 (${data.length} 条记录)`);
  } catch (error) {
    console.error('加载全局数据失败:', error);
    ElMessage.error(error.message || '加载全局数据失败');
  } finally {
    isProcessing.value = false;
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
  await processFiles(files);
};

const processFiles = async (files) => {
  isProcessing.value = true;
  summary.value = null;
  tableData.value = [];
  tableColumns.value = [];
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  try {
    const res = await fetch(`${API_BASE}/borehole/analyze`, {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    if (!res.ok || data.status !== 'success') {
      throw new Error(data.detail || data.message || '处理失败');
    }
    tableData.value = Array.isArray(data.records) ? data.records : [];
    tableColumns.value = Array.isArray(data.columns) ? data.columns : [];
    summary.value = data.summary || defaultSummary();
    if (!summary.value.error_details) summary.value.error_details = [];
    if (!summary.value.warning_details) summary.value.warning_details = [];
    
    // 自动保存到全局数据 (仅在非全局数据模式下上传新文件时)
    if (!useGlobalData.value && tableData.value.length > 0) {
      try {
        globalDataStore.loadBoreholeData(tableData.value, tableColumns.value);
        ElMessage.success(`${data.message || '批量处理成功！'} 已同步到全局数据`);
      } catch (saveError) {
        console.error('保存到全局数据失败:', saveError);
        if (summary.value.successful_files > 0) {
          ElMessage.success(data.message || '批量处理成功！');
        } else if (summary.value.warning_files > 0) {
          ElMessage.warning(data.message || '部分文件处理有警告');
        } else {
          ElMessage.warning(data.message || '未成功处理任何文件');
        }
      }
    } else if (summary.value.successful_files > 0) {
      ElMessage.success(data.message || '批量处理成功！');
    } else if (summary.value.warning_files > 0) {
      ElMessage.warning(data.message || '部分文件处理有警告');
    } else {
      ElMessage.warning(data.message || '未成功处理任何文件');
    }
  } catch (error) {
    console.error('处理钻孔文件失败:', error);
    summary.value = defaultSummary();
    ElMessage.error(error.message || '处理失败');
  } finally {
    isProcessing.value = false;
  }
};

const uniqueCoals = computed(() => {
  const values = tableData.value.map((item) => (item && item['煤层'] ? String(item['煤层']) : '')).filter((v) => v);
  return [...new Set(values)];
});

const uniqueBoreholes = computed(() => {
  const values = tableData.value.map((item) => (item && item['钻孔名'] ? String(item['钻孔名']) : '')).filter((v) => v);
  return [...new Set(values)];
});

const filteredData = computed(() => {
  return tableData.value.filter((item) => {
    const coalValue = item ? item['煤层'] : null;
    const boreholeValue = item ? item['钻孔名'] : null;
    const coalMatch = !coalFilter.value || coalValue === coalFilter.value;
    const boreholeMatch = !boreholeFilter.value || boreholeValue === boreholeFilter.value;
    return coalMatch && boreholeMatch;
  });
});
</script>

<style scoped>
.page-container {
  padding: 20px;
  height: 100%;
  box-sizing: border-box;
}
.control-section, .filter-section {
  margin-bottom: 20px;
}
.file-info {
  margin-left: 15px;
  color: #606266;
}
.hidden-input {
  display: none;
}
.summary-section {
  margin-top: 20px;
  padding: 15px;
  background-color: #f9fafb;
  border-radius: 4px;
}
.summary-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
}
.summary-section ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}
.summary-section ul li {
  margin: 4px 0;
}
</style>