<template>
  <div class="page-container">
    <header class="page-header">
      <div class="title-block">
        <h1>CSV 标准化工具</h1>
        <p class="subtitle">上传原始文件，将列映射到标准字段后快速导出整理结果。</p>
      </div>
      <div class="action-buttons">
        <input ref="fileInput" type="file" accept=".csv" class="hidden-input" @change="handleFileChange" />
        <el-button size="large" class="primary-button" @click="triggerFileSelect">
          1. 选择源 CSV 文件
        </el-button>
        <el-button
          size="large"
          type="primary"
          class="primary-button"
          :disabled="!canTransform"
          :loading="isProcessing"
          @click="transformAndSave"
        >
          3. 转换并下载
        </el-button>
      </div>
    </header>

    <section class="content-grid">
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>源文件概览</span>
            <el-tag v-if="sourceFileName" size="small" type="success">已选择</el-tag>
          </div>
        </template>
        <div class="info-body">
          <p v-if="!sourceFileName" class="placeholder">尚未选择文件</p>
          <div v-else class="file-meta">
            <p class="file-name">{{ sourceFileName }}</p>
            <p class="file-hint">文件读取成功，可继续设置列映射。</p>
          </div>
        </div>
      </el-card>

      <el-card class="mapping-card" shadow="hover" v-loading="isProcessing">
        <template #header>
          <div class="card-header">
            <span>2. 列映射</span>
            <span class="card-hint">将目标字段映射到源文件中的列名</span>
          </div>
        </template>
        <el-empty v-if="!sourceColumns.length" description="请先选择 CSV 文件" :image-size="120" />
        <el-form v-else label-width="160px" class="mapping-form">
          <el-form-item v-for="targetCol in targetColumns" :key="targetCol" :label="targetCol">
            <el-select v-model="mapping[targetCol]" placeholder="选择源文件中的列" clearable filterable>
              <el-option v-for="sourceCol in sourceColumns" :key="sourceCol" :label="sourceCol" :value="sourceCol" />
            </el-select>
          </el-form-item>
        </el-form>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { getApiBase } from '@/utils/api';

const API_BASE = getApiBase();
const fileInput = ref(null);
const sourceFile = ref(null);
const sourceColumns = ref([]);
const targetColumns = ['序号', '岩层名称', '厚度/m', '弹性模量/GPa', '容重/kN·m-3', '抗拉强度/MPa'];
const mapping = reactive({});
const isProcessing = ref(false);

const sourceFileName = computed(() => (sourceFile.value ? sourceFile.value.name : ''));
const canTransform = computed(() => !!sourceFile.value && sourceColumns.value.length > 0);

const resetMapping = () => {
  Object.keys(mapping).forEach((key) => delete mapping[key]);
};

const triggerFileSelect = () => {
  fileInput.value?.click();
};

const handleFileChange = async (event) => {
  const [file] = Array.from(event.target.files || []);
  event.target.value = '';
  if (!file) return;
  sourceFile.value = file;
  await fetchColumns();
};

const fetchColumns = async () => {
  if (!sourceFile.value) return;
  isProcessing.value = true;
  const formData = new FormData();
  formData.append('file', sourceFile.value);
  try {
    const res = await fetch(`${API_BASE}/csv/columns`, { method: 'POST', body: formData });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || errData.message || '获取列信息失败');
    }
    const data = await res.json();
    sourceColumns.value = data.columns || [];
    resetMapping();
    ElMessage.success('列信息获取成功');
  } catch (error) {
    sourceColumns.value = [];
    resetMapping();
    ElMessage.error(error.message || '获取列信息失败');
  } finally {
    isProcessing.value = false;
  }
};

const transformAndSave = async () => {
  if (!sourceFile.value) {
    ElMessage.warning('请先选择 CSV 文件');
    return;
  }
  isProcessing.value = true;
  const formData = new FormData();
  formData.append('file', sourceFile.value);
  formData.append('mapping', JSON.stringify(mapping));
  formData.append('target_columns', JSON.stringify(targetColumns));
  try {
    const res = await fetch(`${API_BASE}/csv/transform`, { method: 'POST', body: formData });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || errData.message || '转换失败');
    }
    const blob = await res.blob();
    if (!blob.size) {
      throw new Error('转换结果为空');
    }
    const contentDisposition = res.headers.get('Content-Disposition') || '';
    const match = contentDisposition.match(/filename=([^;]+)/i);
    const filename = match ? decodeURIComponent(match[1]) : `${sourceFileName.value || 'formatted'}`;
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    ElMessage.success('转换成功，文件已下载');
  } catch (error) {
    ElMessage.error(error.message || '转换失败');
  } finally {
    isProcessing.value = false;
  }
};
</script>

<style scoped>
.page-container {
  padding: 24px 32px 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background-color: #f5f7fb;
  min-height: 100%;
  box-sizing: border-box;
}

.hidden-input {
  display: none;
}

.page-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 16px 24px;
}

.title-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.title-block h1 {
  margin: 0;
  font-size: 26px;
  color: #0f172a;
}

.subtitle {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.primary-button {
  min-width: 180px;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(420px, 2fr);
  gap: 24px;
}

.info-card,
.mapping-card {
  border-radius: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1f2937;
}

.card-hint {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 400;
}

.info-body {
  min-height: 84px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  text-align: center;
  color: #475569;
}

.placeholder {
  margin: 0;
  font-size: 14px;
}

.file-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-name {
  margin: 0;
  font-weight: 600;
  color: #1e293b;
}

.file-hint {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

.mapping-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.mapping-form :deep(.el-select) {
  width: 100%;
}

@media (max-width: 960px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .primary-button {
    flex: 1 1 200px;
  }
}
</style>