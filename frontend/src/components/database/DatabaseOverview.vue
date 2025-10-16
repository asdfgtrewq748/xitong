<template>
  <div class="overview-container">
    <el-skeleton :loading="isLoading" animated>
      <template #template>
        <el-row :gutter="20" class="main-row">
          <el-col :span="17">
            <el-skeleton-item variant="rect" style="width: 100%; height: 100%;" />
          </el-col>
          <el-col :span="7">
            <div class="sidebar-container">
              <el-skeleton-item variant="rect" style="width: 100%; height: 200px;" />
              <el-skeleton-item variant="rect" style="width: 100%; height: 300px; margin-top: 20px;" />
            </div>
          </el-col>
        </el-row>
      </template>

      <template #default>
        <el-row :gutter="20" class="main-row">
          <el-col :span="17">
            <el-card class="map-card" body-style="padding: 0; height: 100%;">
              <div ref="mapChart" style="width: 100%; height: 100%;"></div>
            </el-card>
          </el-col>

          <el-col :span="7">
            <div class="sidebar-container">
              <el-card class="stats-card">
                <template #header><div class="card-header"><span>核心统计</span></div></template>
                <div class="stats-grid">
                  <div class="stat-item">
                    <div class="stat-value">{{ stats.records || 0 }}</div>
                    <div class="stat-title">{{ statTitles.records }}</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ stats.provinces || 0 }}</div>
                    <div class="stat-title">{{ statTitles.provinces }}</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ stats.mines || 0 }}</div>
                    <div class="stat-title">{{ statTitles.mines }}</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ stats.lithologies || 0 }}</div>
                    <div class="stat-title">{{ statTitles.lithologies }}</div>
                  </div>
                </div>
              </el-card>

              <el-card class="stats-card" style="margin-top: 20px;">
                <template #header><div class="card-header"><span>省份样本 Top 8</span></div></template>
                <el-table :data="provinceTopData" stripe class="province-table" height="calc(100vh - 440px)">
                  <el-table-column type="index" label="#" width="50" />
                  <el-table-column prop="label" label="省份" show-overflow-tooltip />
                  <el-table-column prop="value" label="样本数" width="90" align="right" />
                </el-table>
              </el-card>
            </div>
          </el-col>
        </el-row>
      </template>
    </el-skeleton>
  </div>
</template>

<script setup>
/* global defineProps */
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';
import { ElMessage } from 'element-plus';
import { getApiBase } from '@/utils/api';

const props = defineProps({
  active: { type: Boolean, default: false },
});

const API_BASE = getApiBase();
const isLoading = ref(true);
const stats = ref({});
const statTitles = {
  records: '总样本数',
  provinces: '覆盖省份',
  mines: '矿山数量',
  lithologies: '岩性类型',
};
const provinceTopData = ref([]);
const mapChart = ref(null);
let myChart = null;
let resizeHandler = null;
const mapGeoJson = ref(null);
const distributionData = ref([]);
const router = useRouter();

const normalizeProvinceName = (name) => {
  if (!name && name !== 0) return '';
  let value = String(name).trim();
  if (!value) return '';
  const replacements = {
    '内蒙古自治区': '内蒙古',
    '广西壮族自治区': '广西',
    '宁夏回族自治区': '宁夏',
    '新疆维吾尔自治区': '新疆',
    '西藏自治区': '西藏',
    '香港特别行政区': '香港',
    '澳门特别行政区': '澳门',
    '黑龙江省': '黑龙江',
  };
  if (Object.prototype.hasOwnProperty.call(replacements, value)) {
    return replacements[value];
  }
  const suffixes = ['省', '市', '地区', '自治区', '特别行政区'];
  for (const suffix of suffixes) {
    if (value.endsWith(suffix)) {
      value = value.slice(0, -suffix.length);
      break;
    }
  }
  return value.trim();
};

const loadChinaGeoJson = async () => {
  if (mapGeoJson.value) return mapGeoJson.value;
  const response = await fetch('/china.json');
  if (!response.ok) {
    throw new Error('无法加载地图数据');
  }
  mapGeoJson.value = await response.json();
  return mapGeoJson.value;
};

const initChart = async (distribution) => {
  if (!mapChart.value) return;
  const geoJson = await loadChinaGeoJson();
  if (!geoJson) return;
  if (!echarts.getMap('china')) {
    echarts.registerMap('china', geoJson);
  }
  if (myChart) {
    myChart.dispose();
  }
  await nextTick();
  myChart = echarts.init(mapChart.value);
  const values = Array.isArray(distribution) ? distribution : [];
  const featureNames = Array.isArray(geoJson.features)
    ? Array.from(
        new Set(
          geoJson.features
            .map((feature) => feature?.properties?.name || '')
            .filter((name) => Boolean(name))
        )
      )
    : [];
  const valueMap = new Map();
  const labelMap = new Map();
  values.forEach((item) => {
    const rawLabel = item?.label || item?.name || '';
    const normalized = normalizeProvinceName(item?.name || rawLabel);
    if (!normalized) return;
    const num = Number(item?.value);
    valueMap.set(normalized, Number.isFinite(num) ? num : 0);
    labelMap.set(normalized, rawLabel || normalized);
  });
  const seriesData = featureNames.map((name) => {
    const normalized = normalizeProvinceName(name);
    const value = Number.isFinite(valueMap.get(normalized)) ? valueMap.get(normalized) : 0;
    const label = labelMap.get(normalized) || name;
    return { name, value, label };
  });
  const maxValue = seriesData.length
    ? Math.max(seriesData.reduce((acc, cur) => (cur.value > acc ? cur.value : acc), 0), 1)
    : 1;
  myChart.setOption({
    title: { text: '全国岩石样本分布', left: 'center', top: 10, textStyle: { color: '#333' } },
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove|click',
      formatter: (params) => {
        const label = params.data?.label || params.name;
        return `${label}<br/>样本数: ${params.value}`;
      },
    },
    visualMap: {
      min: 0,
      max: maxValue,
      left: '20px',
      bottom: '20px',
      text: ['高', '低'],
      calculable: true,
      inRange: { color: ['#ccebff', '#3377ff', '#0044cc'] },
    },
    series: [
      {
        name: '样本数',
        type: 'map',
        map: 'china',
        roam: true,
        zoom: 1.05,
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            color: '#fff',
            formatter: ({ data, name: featureName }) => {
              const label = data?.label || featureName;
              const value = Number.isFinite(data?.value) ? data.value : 0;
              return `${label}\n样本数：${value}`;
            },
            backgroundColor: 'rgba(0,0,0,0.5)',
            padding: [4, 6],
            borderRadius: 4,
          },
          itemStyle: { areaColor: '#ff7f50' },
        },
        data: seriesData,
      },
    ],
  });
  myChart.off('click');
  myChart.on('click', (params) => {
    if (!params?.name) return;
    const featureLabel = params.data?.label || params.name || '';
    const normalized = normalizeProvinceName(featureLabel || params.name);
    const provinceQuery = normalized || featureLabel;
    if (!provinceQuery) {
      return;
    }
    myChart.dispatchAction({ type: 'showTip', seriesIndex: params.seriesIndex ?? 0, name: params.name });
    router.push({
      path: '/database-viewer',
      query: {
        tab: 'editor',
        province: provinceQuery,
        provinceLabel: featureLabel,
      },
    });
  });
};

const fetchData = async () => {
  isLoading.value = true;
  try {
    const [overview] = await Promise.all([
      fetch(`${API_BASE}/database/overview?limit=40`).then((r) => r.json()),
      loadChinaGeoJson(),
    ]);
    if (overview.status !== 'success') {
      distributionData.value = [];
      const msg = overview.message || overview.detail || '加载数据失败';
      ElMessage.error(msg);
      return;
    }
    stats.value = overview.stats;
    const rawDistribution = Array.isArray(overview.distribution) ? overview.distribution : [];
    const sanitized = rawDistribution.map((item) => {
      const rawName = item?.name ?? item?.label ?? '未知';
      const value = Number(item?.value);
      return {
        name: normalizeProvinceName(rawName) || '未知',
        label: item?.label || rawName || '未知',
        value: Number.isFinite(value) ? value : 0,
      };
    });
    const sortedDistribution = sanitized.slice().sort((a, b) => b.value - a.value);
    provinceTopData.value = sortedDistribution.slice(0, 8);
    distributionData.value = sanitized;
  } catch (error) {
    distributionData.value = [];
    ElMessage.error(`加载数据库概览失败: ${error.message || '未知错误'}`);
  } finally {
    isLoading.value = false;
    await nextTick();
    try {
      await initChart(distributionData.value);
    } catch (chartError) {
      console.error('地图渲染失败:', chartError);
    }
  }
};

onMounted(async () => {
  await fetchData();
  resizeHandler = () => myChart?.resize();
  window.addEventListener('resize', resizeHandler);
});

watch(
  () => props.active,
  (isActive) => {
    if (!isActive) {
      return;
    }
    nextTick(() => {
      try {
        myChart?.resize();
      } catch (error) {
        console.warn('Map resize on activation failed:', error);
      }
    });
  }
);

onUnmounted(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler);
    resizeHandler = null;
  }
  myChart?.dispose();
});
</script>

<style scoped>
.overview-container { height: 100%; padding: 20px; box-sizing: border-box; background-color: #f5f7fa; }
.main-row { height: 100%; }
.map-card { height: 100%; border-radius: 12px; }
.sidebar-container { height: 100%; display: flex; flex-direction: column; }
.stats-card { border-radius: 12px; }
.card-header { font-weight: 600; color: #303133; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.stat-item { background-color: #f8f9fa; padding: 16px; border-radius: 8px; text-align: center; border: 1px solid #e9ecef; }
.stat-value { font-size: 26px; font-weight: 700; color: #1e3a8a; }
.stat-title { font-size: 13px; color: #606266; margin-top: 4px; }
.province-table { width: 100%; }
</style>