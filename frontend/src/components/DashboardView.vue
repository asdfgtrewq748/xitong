<template>
  <div class="dashboard-container">
    <!-- 全局数据管理卡片 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="global-data-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">🌐 全局钻孔数据</span>
              <div>
                <el-tag v-if="globalDataStore.keyStratumData.value.length > 0" type="primary">
                  {{ globalDataStore.keyStratumData.value.length }} 条记录
                </el-tag>
              </div>
            </div>
          </template>
          
          <div v-if="!hasGlobalData" class="empty-state">
            <el-empty description="暂无全局钻孔数据，请先导入原始岩层数据">
              <el-button type="primary" @click="showImportDialog = true">导入钻孔数据</el-button>
            </el-empty>
          </div>
          
          <div v-else class="data-summary">
            <div class="summary-grid">
              <div class="summary-item">
                <div class="summary-label">记录数量</div>
                <div class="summary-value">{{ globalDataStore.keyStratumData.value.length }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">字段数量</div>
                <div class="summary-value">{{ globalDataStore.keyStratumColumns.value.length }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">钻孔数量</div>
                <div class="summary-value">{{ uniqueBoreholes }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">数据状态</div>
                <div class="summary-value">原始数据</div>
              </div>
            </div>
            
            <div class="action-buttons">
              <el-button type="primary" @click="showImportDialog = true">重新导入</el-button>
              <el-button type="info" @click="previewGlobalData">预览数据</el-button>
              <el-button type="warning" @click="exportGlobalData">导出CSV</el-button>
              <el-button type="danger" @click="clearGlobalData">清空数据</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="welcome-card">
          <h1>欢迎使用矿山工程分析系统</h1>
          <p>快速了解项目状态，并一键进入常用分析模块。</p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-icon" style="background-color: #E6A23C;"><el-icon><Coin /></el-icon></div>
            <div class="stat-text">
              <div class="stat-title">岩石数据库记录</div>
              <div class="stat-value">{{ stats.rock_db_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
             <div class="stat-icon" style="background-color: #409EFF;"><el-icon><Files /></el-icon></div>
            <div class="stat-text">
              <div class="stat-title">已加载钻孔文件</div>
              <div class="stat-value">{{ stats.borehole_file_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
         <el-card shadow="hover">
          <div class="stat-item">
             <div class="stat-icon" style="background-color: #67C23A;"><el-icon><Picture /></el-icon></div>
            <div class="stat-text">
              <div class="stat-title">建模数据记录</div>
              <div class="stat-value">{{ stats.modeling_record_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover">
           <template #header>
            <div class="card-header">
              <span>快捷入口</span>
            </div>
          </template>
          <div class="quick-links">
            <el-button @click="$router.push('/key-stratum')">关键层计算</el-button>
            <el-button @click="$router.push('/geological-modeling')">地质建模</el-button>
            <el-button @click="$router.push('/database-viewer')">数据库管理</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 导入数据对话框 -->
    <el-dialog v-model="showImportDialog" title="导入钻孔数据" width="600px">
      <div class="import-section">
        <input ref="boreholeFileInput" type="file" multiple accept=".csv" class="hidden-input" @change="handleBoreholeImport" />
        <el-button type="primary" size="large" @click="$refs.boreholeFileInput?.click()" :loading="isImporting">
          <el-icon style="margin-right: 8px;"><UploadFilled /></el-icon>
          选择钻孔 CSV 文件
        </el-button>
        <p class="import-tip">💡 支持批量选择多个钻孔 CSV 文件，自动过滤关键层计算字段，保留原始岩层数据</p>
      </div>
    </el-dialog>
    
    <!-- 数据预览对话框 -->
    <el-dialog v-model="showPreviewDialog" title="全局数据预览" width="90%" top="5vh">
      <div style="margin-bottom: 12px;">
        <el-text>
          显示前 100 条记录 (共 {{ globalDataStore.keyStratumData.value.length }} 条原始钻孔数据)
        </el-text>
      </div>
      <el-table :data="previewData" border stripe height="60vh" style="width: 100%">
        <el-table-column
          v-for="col in (previewData.length > 0 ? Object.keys(previewData[0]) : [])"
          :key="col"
          :prop="col"
          :label="col"
          min-width="120"
          show-overflow-tooltip
        />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Coin, Files, Picture, UploadFilled } from '@element-plus/icons-vue';
import { getApiBase } from '@/utils/api';
import globalDataStore from '@/stores/globalData';

const API_BASE = getApiBase();
const stats = ref({
  rock_db_count: 0,
  borehole_file_count: 0,
  modeling_record_count: 0
});

const showImportDialog = ref(false);
const showPreviewDialog = ref(false);
const isImporting = ref(false);
const boreholeFileInput = ref(null);

const hasGlobalData = computed(() => 
  globalDataStore.boreholeData.value.length > 0 || 
  globalDataStore.keyStratumData.value.length > 0
);

const uniqueBoreholes = computed(() => {
  const data = globalDataStore.keyStratumData.value;
  if (!data || !data.length) return 0;
  const boreholes = new Set(data.map(row => row['钻孔名'] || row['钻孔'] || row['BK']).filter(Boolean));
  return boreholes.size;
});

const previewData = computed(() => {
  // 只显示岩层数据(钻孔原始数据)
  if (globalDataStore.keyStratumData.value.length > 0) {
    return globalDataStore.keyStratumData.value.slice(0, 100);
  }
  return [];
});

const fetchStats = async () => {
  try {
    const res = await fetch(`${API_BASE}/dashboard/stats`).then((r) => r.json());
    if (res.status === 'success') {
      stats.value = {
        rock_db_count: res.stats?.rock_db_count ?? 0,
        borehole_file_count: res.stats?.borehole_file_count ?? 0,
        modeling_record_count: res.stats?.modeling_record_count ?? 0,
      };
    } else {
      ElMessage.error(res.message || '获取统计数据失败');
    }
  } catch (e) {
    console.error('获取统计数据失败:', e);
    ElMessage.error('获取统计数据失败，请稍后重试');
  }
};

const handleBoreholeImport = async (event) => {
  const files = Array.from(event.target.files || []);
  event.target.value = '';
  if (!files.length) return;

  isImporting.value = true;
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  try {
    // 使用原始数据导入接口,不做业务处理
    const res = await fetch(`${API_BASE}/raw/import`, {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    
    if (!res.ok || data.status !== 'success') {
      throw new Error(data.detail || data.message || '导入失败');
    }

    const records = data.records || [];
    const columns = data.columns || [];
    const excludedColumns = data.excluded_columns || [];
    
    console.log('原始钻孔数据导入成功');
    console.log('记录数:', records.length);
    console.log('保留的列名:', columns);
    console.log('排除的列名:', excludedColumns);
    
    // 保存到岩层数据存储(用于关键层计算)
    globalDataStore.loadKeyStratumData(
      records,
      columns
    );

    let message = `成功导入 ${records.length} 条原始钻孔数据`;
    if (excludedColumns.length > 0) {
      message += ` (已过滤 ${excludedColumns.length} 个计算字段)`;
    }
    
    ElMessage.success(message);
    showImportDialog.value = false;
  } catch (error) {
    console.error('导入钻孔数据失败:', error);
    ElMessage.error(error.message || '导入失败');
  } finally {
    isImporting.value = false;
  }
};

const previewGlobalData = () => {
  showPreviewDialog.value = true;
};

const exportGlobalData = async () => {
  try {
    if (globalDataStore.keyStratumData.value.length === 0) {
      ElMessage.warning('没有可导出的数据');
      return;
    }
    
    const records = globalDataStore.keyStratumData.value;
    const columns = globalDataStore.keyStratumColumns.value;
    const filename = `钻孔原始数据_${new Date().toISOString().slice(0,10)}.csv`;
    
    const csv = convertToCSV(records, columns);
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
    ElMessage.success('数据已导出');
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('导出失败');
  }
};

const convertToCSV = (records, columns) => {
  if (!records || !records.length) return '';
  const header = columns.join(',');
  const rows = records.map(record => 
    columns.map(col => {
      const value = record[col];
      return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
    }).join(',')
  );
  return [header, ...rows].join('\n');
};

const clearGlobalData = async () => {
  try {
    await ElMessageBox.confirm('确定要清空全局数据吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    globalDataStore.clear();
    ElMessage.success('已清空全局数据');
  } catch {
    // 用户取消
  }
};

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
.dashboard-container { padding: 20px; }

.global-data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.data-summary {
  padding: 12px 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.summary-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  text-align: center;
}

.summary-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.summary-time {
  font-size: 14px;
  font-weight: 400;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.import-section {
  padding: 40px 20px;
  text-align: center;
}

.import-tip {
  margin-top: 16px;
  color: #909399;
  font-size: 13px;
}

.hidden-input {
  display: none;
}

.welcome-card { 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; 
  margin-bottom: 20px; 
}

.welcome-card h1 { 
  margin-top: 0; 
  font-size: 28px;
}

.welcome-card p {
  opacity: 0.9;
  font-size: 14px;
}

.stats-row { margin-bottom: 20px; }

.stat-item { 
  display: flex; 
  align-items: center; 
}

.stat-icon {
  width: 60px; 
  height: 60px; 
  border-radius: 12px;
  display: flex; 
  align-items: center; 
  justify-content: center;
  font-size: 30px; 
  color: white; 
  margin-right: 15px;
}

.stat-title { 
  font-size: 14px; 
  color: #909399; 
}

.stat-value { 
  font-size: 24px; 
  font-weight: bold; 
  color: #303133; 
}

.quick-links .el-button { 
  margin: 0 10px 10px 0; 
}
</style>