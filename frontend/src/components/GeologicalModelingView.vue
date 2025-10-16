<template>
  <div class="geo-modeling-container">
    <el-steps :active="step" finish-status="success" align-center style="margin-bottom: 20px;">
      <el-step title="数据加载" />
      <el-step title="参数选择" />
      <el-step title="建模与可视化" />
    </el-steps>
    <el-row :gutter="20" class="content-row">
      <el-col :span="6" class="panel-col">
        <div class="panel">
          <div v-show="step === 0" class="panel-step">
            <el-alert
              title="请准备钻孔数据与坐标文件"
              description="支持使用全局数据或上传新文件。坐标文件需包含相同的钻孔标识列"
              type="info"
              :closable="false"
              show-icon
            />
            
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
            
            <!-- 钻孔数据选择 -->
            <div v-if="!useGlobalData" class="file-group">
              <div class="file-group__header">
                <h5>钻孔数据 (可多选)</h5>
                <el-button type="primary" plain size="small" @click="triggerBoreholeSelection">选择文件</el-button>
                <input ref="boreholeInput" class="hidden-input" type="file" accept=".csv" multiple @change="handleBoreholeFiles" />
              </div>
              <el-empty v-if="boreholeFiles.length === 0" description="未选择文件" :image-size="80" />
              <el-scrollbar v-else class="file-scroll">
                <ul class="file-list">
                  <li v-for="(file, idx) in boreholeFiles" :key="`${file.name}-${idx}`">
                    <span>{{ file.name }}</span>
                    <el-tag size="small" type="info" effect="plain">{{ formatFileSize(file.size) }}</el-tag>
                  </li>
                </ul>
              </el-scrollbar>
            </div>
            <div v-else class="file-group">
              <div class="file-group__header">
                <h5>钻孔数据来源</h5>
              </div>
              <div class="global-data-summary">
                <el-icon class="data-icon"><DataAnalysis /></el-icon>
                <div class="data-info">
                  <span class="data-label">全局钻孔数据</span>
                  <span class="data-count">{{ globalDataStore.keyStratumData.value.length }} 条记录</span>
                </div>
              </div>
            </div>
            
            <!-- 坐标文件 (必需) -->
            <div class="file-group">
              <div class="file-group__header">
                <h5>坐标文件 <el-tag size="small" type="danger">必需</el-tag></h5>
                <el-button type="primary" plain size="small" @click="triggerCoordsSelection">选择文件</el-button>
                <input ref="coordsInput" class="hidden-input" type="file" accept=".csv" @change="handleCoordsFile" />
              </div>
              <div class="coords-summary">
                <span v-if="coordsFile">{{ coordsFile.name }} ({{ formatFileSize(coordsFile.size) }})</span>
                <span v-else class="muted">未选择文件</span>
              </div>
            </div>
            
            <el-button type="primary" @click="loadAndMergeData" :loading="isLoading" class="full-width">
              加载并合并数据
            </el-button>
          </div>
          <div v-show="step === 1">
            <el-form label-position="top" :disabled="isLoading || columns.numeric.length === 0">
              <el-form-item label="X坐标"><el-select v-model="params.x_col" placeholder="选择X坐标列" style="width: 100%;"><el-option v-for="c in columns.numeric" :key="c" :label="c" :value="c"/></el-select></el-form-item>
              <el-form-item label="Y坐标"><el-select v-model="params.y_col" placeholder="选择Y坐标列" style="width: 100%;"><el-option v-for="c in columns.numeric" :key="c" :label="c" :value="c"/></el-select></el-form-item>
              <el-form-item label="Z值/厚度"><el-select v-model="params.thickness_col" placeholder="选择厚度/Z值列" style="width: 100%;"><el-option v-for="c in columns.numeric" :key="c" :label="c" :value="c"/></el-select></el-form-item>
              <el-form-item label="岩层列"><el-select v-model="params.seam_col" @change="updateSeamList" placeholder="选择岩层列" style="width: 100%;"><el-option v-for="c in columns.text" :key="c" :label="c" :value="c"/></el-select></el-form-item>
            </el-form>
            <div v-if="availableSeams.length > 0">
              <h5>选择建模岩层 (可多选)</h5>
              <el-select v-model="params.selected_seams" multiple placeholder="选择岩层" style="width: 100%;"><el-option v-for="s in availableSeams" :key="s" :label="s" :value="s"/></el-select>
            </div>
            <el-button type="primary" @click="step = 2" :disabled="!canProceedToModeling" class="full-width">下一步</el-button>
            <el-button text type="info" @click="step = 0" class="full-width">重新选择文件</el-button>
          </div>
          <div v-show="step === 2">
            <el-form label-position="top">
              <el-form-item label="插值方法">
                <el-select v-model="params.method" style="width: 100%;">
                  <el-option v-for="(name, key) in interpolationMethods" :key="key" :label="name" :value="key" />
                </el-select>
              </el-form-item>
              <el-divider content-position="left">高级参数</el-divider>
              <el-form-item label="网格分辨率">
                <el-input-number v-model="params.resolution" :min="20" :max="200" :step="10" style="width: 100%;" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px;">分辨率越高，模型越精细，但计算时间更长</div>
              </el-form-item>
              <el-form-item label="首层基底高程 (m)">
                <el-input-number v-model="params.base_level" :step="0.5" style="width: 100%;" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px;">最底层岩层的底面高程基准值</div>
              </el-form-item>
              <el-form-item label="层间可视化间隔 (m)">
                <el-input-number v-model="params.gap" :min="0" :step="0.1" style="width: 100%;" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px;">用于3D可视化时各层之间的间距,不影响实际厚度</div>
              </el-form-item>
            </el-form>
            <el-row :gutter="10" style="margin-bottom: 10px;">
              <el-col :span="12">
                <el-button type="success" @click="generateContour" :loading="isLoading" :disabled="!params.thickness_col" class="full-width">生成 2D 等值线图</el-button>
              </el-col>
              <el-col :span="12">
                <el-button type="success" @click="generate3DModel" :loading="isLoading" :disabled="params.selected_seams.length === 0" class="full-width">生成 3D 块体模型</el-button>
              </el-col>
            </el-row>
            <el-divider content-position="left">插值方法对比</el-divider>
            <el-form label-position="top">
              <el-form-item label="验证集比例 (%)">
                <el-slider v-model="params.validation_ratio" :min="10" :max="50" show-input></el-slider>
              </el-form-item>
            </el-form>
            <el-button type="warning" @click="runComparison" :loading="isLoading" :disabled="!params.thickness_col" class="full-width">
              对比所有插值方法
            </el-button>
            <el-button text type="info" @click="step = 1" class="full-width">返回列选择</el-button>
          </div>
        </div>
      </el-col>
      <el-col :span="18" class="chart-col">
        <el-card class="chart-card" v-loading="isLoading" element-loading-text="正在计算和渲染模型...">
          <div class="chart-wrapper">
            <div v-show="chartMessage" class="chart-placeholder">{{ chartMessage }}</div>
            <div ref="chartRef" class="chart-canvas"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-dialog v-model="comparisonDialogVisible" title="插值方法对比结果" width="70%">
      <el-alert v-if="bestMethod" type="success" :closable="false" style="margin-bottom: 15px;">
        <b>推荐方法: {{ bestMethod.method }}</b> (R²: {{ bestMethod.r2 }}, RMSE: {{ bestMethod.rmse }})
      </el-alert>
      <el-table :data="comparisonResults" border stripe height="400px" :default-sort="{ prop: 'r2', order: 'descending' }">
        <el-table-column property="method" label="方法" width="180"/>
        <el-table-column property="r2" label="R² (决定系数)" sortable />
        <el-table-column property="mae" label="MAE (平均绝对误差)" sortable />
        <el-table-column property="rmse" label="RMSE (均方根误差)" sortable />
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="comparisonDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>

import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { CircleCheckFilled, DataAnalysis } from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import 'echarts-gl'; // 必须导入 echarts-gl 以支持 3D 图表
import { getApiBase } from '@/utils/api';
import globalDataStore from '@/stores/globalData';

console.log('[GeologicalModeling] echarts版本:', echarts.version);
console.log('[GeologicalModeling] 可用图表类型:', Object.keys(echarts.ComponentModel || {}));


// 所有变量和方法都直接声明，模板可直接访问
const isLoading = ref(false);
const step = ref(0);
const useGlobalData = ref(true); // 默认使用全局数据
const boreholeFiles = ref([]); // File[]
const coordsFile = ref(null); // File
const boreholeInput = ref(null);
const coordsInput = ref(null);
const columns = ref({ numeric: [], text: [] });
const availableSeams = ref([]);
const chartMessage = ref('请先上传钻孔数据与坐标文件。');

// 为不同岩层分配颜色
const layerColors = [
  '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', 
  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#d4a373',
  '#8b5a3c', '#546570', '#c4ccd3'
];
function getColorForLayer(index) {
  return layerColors[index % layerColors.length];
}
const interpolationMethods = {
  "linear": "线性 (Linear)",
  "cubic": "三次样条 (Cubic)",
  "nearest": "最近邻 (Nearest)",
  "multiquadric": "多重二次 (Multiquadric)",
  "inverse": "反距离 (Inverse)",
  "gaussian": "高斯 (Gaussian)",
  "linear_rbf": "线性RBF (Linear RBF)",
  "cubic_rbf": "三次RBF (Cubic RBF)",
  "quintic_rbf": "五次RBF (Quintic RBF)",
  "thin_plate": "薄板样条 (Thin Plate)",
  "modified_shepard": "修正谢泼德 (Modified Shepard)",
  "ordinary_kriging": "普通克里金 (Ordinary Kriging)"
};
const API_BASE = getApiBase();
const params = reactive({
  x_col: '', y_col: '', thickness_col: '', seam_col: '',
  selected_seams: [],
  method: 'linear',
  validation_ratio: 20,
  resolution: 80,    // 网格分辨率
  base_level: 0.0,   // 首层基底高程
  gap: 0.0,          // 层间可视化间隔
});
const chartRef = ref(null);
let myChart = null;
let resizeHandler = null;
const comparisonDialogVisible = ref(false);
const comparisonResults = ref([]);
const bestMethod = computed(() => (comparisonResults.value.length > 0 ? comparisonResults.value[0] : null));
const canProceedToModeling = computed(() =>
  !!(params.x_col && params.y_col && params.thickness_col && params.seam_col && params.selected_seams.length > 0)
);

function triggerBoreholeSelection() {
  boreholeInput.value?.click();
}
function triggerCoordsSelection() {
  coordsInput.value?.click();
}
function handleBoreholeFiles(event) {
  const files = Array.from(event.target.files || []);
  boreholeFiles.value = files;
  chartMessage.value = files.length ? '数据已选择，请点击“加载并合并数据”。' : '请先上传钻孔数据与坐标文件。';
}
function handleCoordsFile(event) {
  const [file] = Array.from(event.target.files || []);
  coordsFile.value = file || null;
}
function formatFileSize(size) {
  if (size === undefined || size === null) return '';
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}
async function loadAndMergeData() {
  // 验证数据
  if (useGlobalData.value) {
    if (globalDataStore.keyStratumData.value.length === 0) {
      ElMessage.warning('全局数据为空，请先在Dashboard导入钻孔数据');
      return;
    }
    if (!coordsFile.value) {
      ElMessage.warning('请上传坐标文件');
      return;
    }
  } else {
    if (boreholeFiles.value.length === 0 || !coordsFile.value) {
      ElMessage.warning('请上传钻孔文件和坐标文件');
      return;
    }
  }
  
  isLoading.value = true;
  try {
    const formData = new FormData();
    
    if (useGlobalData.value) {
      // 使用全局数据：将数据转换为CSV并上传
      const data = globalDataStore.keyStratumData.value;
      const columns = globalDataStore.keyStratumColumns.value;
      
      if (!columns || columns.length === 0) {
        throw new Error('全局数据列信息缺失');
      }
      
      // 转换为CSV格式
      const csvHeader = columns.join(',');
      const csvRows = data.map(record => 
        columns.map(col => {
          const value = record[col];
          if (value === null || value === undefined) return '';
          const strValue = String(value);
          return strValue.includes(',') ? `"${strValue}"` : strValue;
        }).join(',')
      );
      const csv = [csvHeader, ...csvRows].join('\n');
      
      // 创建Blob并上传
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
      formData.append('borehole_files', blob, 'global_data.csv');
      console.log('使用全局数据，记录数:', data.length);
    } else {
      // 使用上传的文件
      boreholeFiles.value.forEach(f => formData.append('borehole_files', f));
      console.log('使用上传文件，文件数:', boreholeFiles.value.length);
    }
    
    formData.append('coords_file', coordsFile.value);
    
    const response = await fetch(`${API_BASE}/modeling/columns`, {
      method: 'POST',
      body: formData
    });
    
    // 检查响应是否为 JSON
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const text = await response.text();
      console.error('服务器返回非JSON响应:', text.substring(0, 200));
      throw new Error(`服务器返回错误: ${response.status} ${response.statusText}`);
    }
    
    const res = await response.json();
    
    if (res.status === 'success') {
      columns.value.numeric = res.numeric_columns;
      columns.value.text = res.text_columns;
      ElMessage.success(`数据合并成功，共 ${res.record_count} 条记录`);
      params.x_col = res.numeric_columns.find(c => c.toLowerCase().includes('x')) || res.numeric_columns[0] || '';
      params.y_col = res.numeric_columns.find(c => c.toLowerCase().includes('y')) || res.numeric_columns[1] || '';
      params.thickness_col = res.numeric_columns.find(c => c.toLowerCase().includes('厚')) || res.numeric_columns.find(c => c.toLowerCase().includes('z')) || res.numeric_columns[2] || '';
      params.seam_col = res.text_columns.find(c => c.toLowerCase().includes('岩')) || res.text_columns[0] || '';
      if (params.seam_col) await updateSeamList(params.seam_col);
      step.value = 1;
      chartMessage.value = '请选择列并生成等值线或三维模型。';
    } else {
      const errorMsg = res.detail || res.message || '数据合并失败';
      ElMessage.error(errorMsg);
      chartMessage.value = errorMsg;
    }
  } catch (e) {
    console.error('数据加载失败:', e);
    const errorMsg = e.message || '数据加载失败';
    ElMessage.error(errorMsg);
    chartMessage.value = errorMsg;
  } finally {
    isLoading.value = false;
  }
}
async function updateSeamList(seamCol) {
  if (!seamCol) {
    availableSeams.value = [];
    params.selected_seams = [];
    return;
  }
  const previousLoading = isLoading.value;
  isLoading.value = true;
  try {
  const res = await fetch(`${API_BASE}/modeling/seams?column=${encodeURIComponent(seamCol)}`).then(r => r.json());
    if (res.status === 'success') {
      availableSeams.value = res.values;
      params.selected_seams = res.values;
    } else {
      ElMessage.error(res.message);
    }
  } catch (e) {
    ElMessage.error('岩层获取失败: ' + e.message);
  } finally {
    isLoading.value = previousLoading;
  }
}
function initChart() {
  console.log('[initChart] 开始初始化图表...');
  console.log('[initChart] chartRef.value:', chartRef.value);
  console.log('[initChart] myChart 当前状态:', myChart);
  
  if (myChart) {
    console.log('[initChart] 销毁旧图表实例');
    myChart.dispose();
    myChart = null;
  }
  
  if (chartRef.value) {
    console.log('[initChart] 图表容器尺寸:', {
      width: chartRef.value.offsetWidth,
      height: chartRef.value.offsetHeight,
      clientWidth: chartRef.value.clientWidth,
      clientHeight: chartRef.value.clientHeight
    });
    
    try {
      myChart = echarts.init(chartRef.value);
      console.log('[initChart] ✅ 图表实例创建成功:', myChart);
    } catch (error) {
      console.error('[initChart] ❌ 创建图表实例失败:', error);
    }
  } else {
    console.error('[initChart] ❌ chartRef.value 为空!');
  }
}
onMounted(() => {
  console.log('[onMounted] 组件已挂载');
  console.log('[onMounted] echarts版本:', echarts.version);
  console.log('[onMounted] echarts对象keys:', Object.keys(echarts).slice(0, 20));
  
  // 检查 echarts-gl 是否加载
  try {
    // 尝试创建一个简单的3D图表来测试
    const testDiv = document.createElement('div');
    testDiv.style.width = '100px';
    testDiv.style.height = '100px';
    const testChart = echarts.init(testDiv);
    const testOption = {
      xAxis3D: {},
      yAxis3D: {},
      zAxis3D: {},
      grid3D: {},
      series: []
    };
    testChart.setOption(testOption);
    console.log('[onMounted] ✅ echarts-gl 3D支持可用');
    testChart.dispose();
  } catch (error) {
    console.error('[onMounted] ❌ echarts-gl 3D支持不可用:', error);
  }
  
  initChart();
  resizeHandler = () => myChart?.resize();
  window.addEventListener('resize', resizeHandler);
});
onUnmounted(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler);
    resizeHandler = null;
  }
  chartMessage.value = '请先上传钻孔数据与坐标文件。';
  myChart?.dispose();
});
async function generateContour() {
  isLoading.value = true;
  try {
  const res = await fetch(`${API_BASE}/modeling/contour`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        x_col: params.x_col,
        y_col: params.y_col,
        z_col: params.thickness_col,
        method: params.method,
        seams: params.selected_seams
      })
    }).then(r => r.json());
    if (res.status === 'success') {
      initChart();
      const option = {
        title: { text: `${params.thickness_col} 等值线图 (${interpolationMethods[params.method]})`, left: 'center' },
        tooltip: { trigger: 'item', formatter: 'X: {b0}<br/>Y: {b1}<br/>Z: {c2}' },
        grid: { right: '15%' },
        visualMap: {
          min: Math.min(...res.points.z),
          max: Math.max(...res.points.z),
          calculable: true, orient: 'vertical', left: 'left', top: 'center',
          inRange: { color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'].reverse() },
        },
        xAxis: { type: 'category', data: res.grid.x, name: params.x_col, axisLabel: {formatter: v => Number(v).toFixed(0)} },
        yAxis: { type: 'category', data: res.grid.y, name: params.y_col, axisLabel: {formatter: v => Number(v).toFixed(0)} },
        series: [{
          name: '等值线', type: 'heatmap',
          data: res.grid.z.flatMap((row, i) => row.map((val, j) => [j, i, val])),
          progressive: 1000,
          animation: false
        }, {
          name: '原始数据点', type: 'scatter',
          data: res.points.x.map((x, i) => [x, res.points.y[i], res.points.z[i]]),
          symbolSize: 8, itemStyle: { color: '#000' },
          xAxisIndex: 0, yAxisIndex: 0
        }]
      };
      myChart.setOption(option, true);
      ElMessage.success('2D等值线图生成成功！');
      chartMessage.value = '';
    } else {
      ElMessage.error(res.message);
      chartMessage.value = res.message || '生成等值线失败。';
    }
  } catch (e) {
    ElMessage.error('等值线生成失败: ' + e.message);
    chartMessage.value = '等值线生成失败，请检查数据输入。';
  } finally {
    isLoading.value = false;
  }
}
async function generate3DModel() {
  isLoading.value = true;
  try {
    const res = await fetch(`${API_BASE}/modeling/block_model`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        x_col: params.x_col,
        y_col: params.y_col,
        thickness_col: params.thickness_col,
        seam_col: params.seam_col,
        selected_seams: params.selected_seams,
        method: params.method,
        resolution: params.resolution,
        base_level: params.base_level,
        gap: params.gap
      })
    }).then(r => r.json());
    if (res.status === 'success') {
      console.log('[3D建模] 响应数据:', res);
      console.log('[3D建模] 模型数量:', res.models?.length);
      
      if (!res.models || res.models.length === 0) {
        ElMessage.warning('未能生成任何块体模型');
        chartMessage.value = '所有岩层数据不足,无法生成模型';
        return;
      }
      
      // 检查第一个模型的数据格式
      if (res.models[0]) {
        console.log('[3D建模] 第一个模型:', res.models[0].name);
        console.log('[3D建模] X网格长度:', res.models[0].grid_x?.length);
        console.log('[3D建模] Y网格长度:', res.models[0].grid_y?.length);
        console.log('[3D建模] Z矩阵维度:', res.models[0].top_surface_z?.length, 'x', res.models[0].top_surface_z?.[0]?.length);
      }
      
      initChart();
      
      // 为每个岩层生成顶面的 surface
      const series = [];
      res.models.forEach((model, idx) => {
        // 检查数据有效性
        if (!model.grid_x || !model.grid_y || !model.top_surface_z) {
          console.warn(`[3D建模] 岩层 ${model.name} 的数据不完整`);
          return;
        }
        
        // 构建 wireframe 数据: [[x, y, z], ...]
        const wireframeData = [];
        for (let i = 0; i < model.grid_y.length; i++) {
          for (let j = 0; j < model.grid_x.length; j++) {
            wireframeData.push([
              model.grid_x[j],
              model.grid_y[i],
              model.top_surface_z[i][j]
            ]);
          }
        }
        
        console.log(`[3D建模] 岩层 ${model.name}: 生成 ${wireframeData.length} 个数据点`);
        
        // 顶面 Surface (使用 wireframe data)
        series.push({
          type: 'surface',
          name: model.name,
          wireframe: {
            show: false
          },
          data: wireframeData,
          shading: 'color',
          itemStyle: {
            color: getColorForLayer(idx),
            opacity: 0.85
          },
          emphasis: {
            itemStyle: {
              color: getColorForLayer(idx),
              opacity: 1.0
            }
          }
        });
      });
      
      console.log('[3D建模] 生成的 series 数量:', series.length);
      
      // 计算数据范围用于设置坐标轴
      let xMin = Infinity, xMax = -Infinity;
      let yMin = Infinity, yMax = -Infinity;
      let zMin = Infinity, zMax = -Infinity;
      
      res.models.forEach(model => {
        if (model.grid_x && model.grid_x.length > 0) {
          xMin = Math.min(xMin, ...model.grid_x);
          xMax = Math.max(xMax, ...model.grid_x);
        }
        if (model.grid_y && model.grid_y.length > 0) {
          yMin = Math.min(yMin, ...model.grid_y);
          yMax = Math.max(yMax, ...model.grid_y);
        }
        if (model.top_surface_z) {
          model.top_surface_z.forEach(row => {
            if (row && row.length > 0) {
              zMin = Math.min(zMin, ...row.filter(v => isFinite(v)));
              zMax = Math.max(zMax, ...row.filter(v => isFinite(v)));
            }
          });
        }
      });
      
      console.log('[3D建模] 数据范围:', { xMin, xMax, yMin, yMax, zMin, zMax });
      
      const option = {
        title: { 
          text: `三维岩层块体模型 (${res.models.length}个岩层)`, 
          left: 'center',
          textStyle: { fontSize: 16, fontWeight: 'bold' }
        },
        tooltip: { 
          formatter: (p) => {
            if(p.value && p.value.length >= 3) {
              return `<b>${p.seriesName}</b><br/>X: ${p.value[0].toFixed(2)} m<br/>Y: ${p.value[1].toFixed(2)} m<br/>高程: ${p.value[2].toFixed(2)} m`;
            }
            return p.seriesName;
          }
        },
        legend: { 
          data: series.map(s => s.name), 
          orient: 'vertical', 
          right: 10, 
          top: 60,
          textStyle: { fontSize: 11 },
          backgroundColor: 'rgba(255,255,255,0.9)',
          padding: 8,
          borderRadius: 4,
          type: 'scroll',
          pageButtonPosition: 'end'
        },
        xAxis3D: { 
          type: 'value', 
          name: params.x_col,
          min: isFinite(xMin) ? xMin : undefined,
          max: isFinite(xMax) ? xMax : undefined
        },
        yAxis3D: { 
          type: 'value', 
          name: params.y_col,
          min: isFinite(yMin) ? yMin : undefined,
          max: isFinite(yMax) ? yMax : undefined
        },
        zAxis3D: { 
          type: 'value', 
          name: '高程(m)',
          min: isFinite(zMin) ? zMin : undefined,
          max: isFinite(zMax) ? zMax : undefined
        },
        grid3D: {
          viewControl: { 
            projection: 'perspective', 
            autoRotate: false,
            distance: 150,
            alpha: 30,
            beta: 40,
            minAlpha: -90,
            maxAlpha: 90
          },
          boxWidth: 100,
          boxDepth: 100,
          boxHeight: 60,
          light: {
            main: {
              intensity: 1.2,
              shadow: true
            },
            ambient: {
              intensity: 0.4
            }
          },
          environment: '#f5f5f5'
        },
        series: series
      };
      
      console.log('[3D建模] 设置 echarts option, series数量:', option.series.length);
      
      if (!myChart) {
        console.error('[3D建模] ❌ myChart 实例不存在! 重新初始化...');
        initChart();
        if (!myChart) {
          ElMessage.error('图表初始化失败');
          return;
        }
      }
      
      try {
        myChart.setOption(option, true);
        console.log('[3D建模] ✅ echarts setOption 完成');
        
        // 强制刷新
        setTimeout(() => {
          if (myChart) {
            myChart.resize();
            console.log('[3D建模] 图表resize完成');
          }
        }, 100);
      } catch (error) {
        console.error('[3D建模] ❌ setOption 失败:', error);
        ElMessage.error('图表渲染失败: ' + error.message);
        return;
      }
      
      // 成功消息
      ElMessage.success(`3D块体模型生成成功! 已建模 ${res.models.length} 个岩层`);
      chartMessage.value = '';
      
      // 跳过的岩层提示
      if(res.skipped && res.skipped.length > 0) {
        const skippedCount = res.skipped.length;
        
        ElMessageBox.alert(
          `<div style="max-height: 300px; overflow-y: auto;">
            <p><b>以下岩层因数据点不足未能建模:</b></p>
            <ul style="text-align: left; padding-left: 20px;">
              ${res.skipped.map(s => `<li>${s}</li>`).join('')}
            </ul>
            <p style="margin-top: 12px; color: #606266; font-size: 13px;">
              <b>建议:</b><br/>
              • 数据点过少(1-3个)的岩层会自动使用最近邻插值<br/>
              • 对于重要岩层,建议补充更多钻孔数据<br/>
              • 可以取消选择数据点不足的岩层以提高建模质量
            </p>
          </div>`,
          `部分岩层被跳过 (${skippedCount}个)`,
          {
            dangerouslyUseHTMLString: true,
            confirmButtonText: '我知道了'
          }
        );
      }
    } else {
      ElMessage.error(res.message);
      chartMessage.value = res.message || '生成3D模型失败。';
    }
  } catch(e) {
    ElMessage.error('3D建模失败: ' + e.message);
    chartMessage.value = '3D建模失败，请调整参数或检查数据。';
  } finally {
    isLoading.value = false;
  }
}
async function runComparison() {
  isLoading.value = true;
  try {
    const res = await fetch(`${API_BASE}/modeling/comparison`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        x_col: params.x_col,
        y_col: params.y_col,
        z_col: params.thickness_col,
        validation_ratio: params.validation_ratio / 100,
        seams: params.selected_seams
      })
    }).then(r => r.json());
    if (res.status === 'success') {
      comparisonResults.value = res.results;
      comparisonDialogVisible.value = true;
      if(res.results.length > 0){
        const bestMethodKey = Object.keys(interpolationMethods).find(key => interpolationMethods[key] === res.results[0].method);
        if(bestMethodKey) params.method = bestMethodKey;
      }
      ElMessage.success('插值方法对比完成！');
    } else {
      ElMessage.error(res.message);
    }
  } catch (e) {
    ElMessage.error('插值对比失败: ' + e.message);
  } finally {
    isLoading.value = false;
  }
}

</script>

<style scoped>
.geo-modeling-container {
  height: 100%;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}
.content-row { flex: 1; }
.panel-col, .chart-col { height: 100%; }
.panel {
  height: 100%;
  padding: 14px;
  background-color: #fff;
  border-radius: 8px;
  overflow-y: auto;
  box-sizing: border-box;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.panel-step { display: flex; flex-direction: column; gap: 16px; }

/* 全局数据状态信息 */
.data-status-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  border-radius: 10px;
  margin-bottom: 12px;
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
  margin-bottom: 16px;
}

.data-source-selector :deep(.el-radio-group) {
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

.data-source-selector :deep(.el-radio-button__inner) {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 0;
  padding: 10px 14px;
  font-size: 13px;
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

/* 全局数据摘要 */
.global-data-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  border: 1px solid #bae6fd;
}

.global-data-summary .data-icon {
  font-size: 28px;
  color: #0284c7;
}

.global-data-summary .data-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.global-data-summary .data-label {
  font-size: 13px;
  color: #0c4a6e;
  font-weight: 500;
}

.global-data-summary .data-count {
  font-size: 12px;
  color: #075985;
}

.file-group {
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  padding: 12px;
  background: #f8fafc;
}
.file-group__header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.hidden-input { display: none; }
.file-scroll { max-height: 160px; }
.file-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 6px; }
.file-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #334155;
  padding: 6px 8px;
  background: #ffffff;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}
.coords-summary {
  font-size: 13px;
  color: #334155;
  background: #ffffff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}
.coords-summary .muted { color: #94a3b8; }
.chart-card { height: 100%; }
.chart-wrapper { 
  position: relative; 
  height: 100%; 
  min-height: 460px;
  display: flex;
  flex-direction: column;
}
.chart-canvas { 
  width: 100%; 
  height: 100%;
  flex: 1;
  min-height: 400px;
}
.chart-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 16px;
  pointer-events: none;
  z-index: 10;
  background-color: #fafafa;
}
.full-width { 
  width: 100%; 
  min-height: 40px;
  height: auto;
  white-space: normal;
  line-height: 1.4;
  padding: 10px 15px;
}
.full-width :deep(span) {
  white-space: normal;
  word-break: break-word;
  text-align: center;
}
.el-form-item { margin-bottom: 12px; }
h5 { margin: 0; font-size: 14px; color: #1f2937; }
</style>
