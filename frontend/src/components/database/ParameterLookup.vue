<template>
  <div class="lookup-container">
    <div class="control-bar">
      <el-select
        v-model="selectedLithology"
        placeholder="请选择岩性"
        filterable
        clearable
        :loading="isLoadingList"
        class="lithology-select"
        @change="handleLithologyChange"
      >
        <el-option v-for="l in lithologies" :key="l" :label="labelWithCount(l)" :value="l" />
      </el-select>
      <div class="meta" v-if="selectedLithology">
        <span class="meta-label">样本数：</span>
        <span class="meta-value">{{ selectedCount }}</span>
      </div>
    </div>

    <div class="content-grid">
      <el-card class="chart-card" body-style="padding: 0;">
        <template #header>
          <div class="card-header">
            <span>{{ chartTitle }}</span>
            <span class="card-subtitle" v-if="selectedLithology">参数分布可视化（箱线图 + 小提琴图）</span>
          </div>
        </template>
        <div class="chart-area">
          <div ref="violinChart" class="chart-canvas"></div>
          <div v-if="isLoadingChart" class="chart-loading">
            <span class="loader"></span>
            <span class="loading-text">正在加载参数数据...</span>
          </div>
        </div>
      </el-card>

      <el-card class="stats-card">
        <template #header>
          <div class="card-header">
            <span>统计指标</span>
            <span class="card-subtitle" v-if="selectedLithology">最小值/最大值/平均值/中位数/标准差</span>
          </div>
        </template>
        <el-table :data="statTableRows" height="100%" stripe border :loading="isLoadingChart">
          <el-table-column
            prop="metric"
            label="参数"
            width="96"
            fixed
            align="center"
            header-align="center"
            class-name="stat-metric-col"
            header-class-name="stat-metric-col"
          />
          <el-table-column
            v-for="field in STAT_FIELDS"
            :key="field.key"
            :prop="field.key"
            :label="field.label"
            :min-width="88"
            align="center"
            header-align="center"
          />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, nextTick, ref } from 'vue';
import * as echarts from 'echarts';
import 'echarts/extension/dataTool';
import { ElMessage } from 'element-plus';
import { getApiBase } from '@/utils/api';

const API_BASE = getApiBase();

const formatNumber = (value, digits = 2) => {
  if (!Number.isFinite(value)) return '-';
  return Number(value).toFixed(digits);
};

const quantile = (sorted, q) => {
  if (!sorted.length) return NaN;
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  if (sorted[base + 1] !== undefined) {
    return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
  }
  return sorted[base];
};

const calculateBoxplot = (series) => {
  const cleaned = series.filter((value) => Number.isFinite(value));
  if (!cleaned.length) {
    return [0, 0, 0, 0, 0];
  }
  const sorted = [...cleaned].sort((a, b) => a - b);
  const min = sorted[0];
  const max = sorted[sorted.length - 1];
  const median = quantile(sorted, 0.5);
  const q1 = quantile(sorted, 0.25);
  const q3 = quantile(sorted, 0.75);
  return [min, q1, median, q3, max];
};

const gaussianKernel = (u) => Math.exp(-0.5 * u * u) / Math.sqrt(2 * Math.PI);

const computeStd = (values) => {
  const mean = values.reduce((acc, cur) => acc + cur, 0) / values.length;
  const variance = values.reduce((acc, cur) => acc + (cur - mean) ** 2, 0) / values.length;
  return Math.sqrt(Math.max(variance, 0));
};

const computeBandwidth = (values) => {
  if (values.length < 2) return 0;
  const std = computeStd(values);
  const sorted = [...values].sort((a, b) => a - b);
  const q1 = quantile(sorted, 0.25);
  const q3 = quantile(sorted, 0.75);
  const iqr = q3 - q1;
  const sigma = std || iqr / 1.34 || Math.max(Math.abs(sorted[0]), Math.abs(sorted[sorted.length - 1])) || 1;
  const bandwidth = 1.06 * sigma * Math.pow(values.length, -0.2);
  return Number.isFinite(bandwidth) && bandwidth > 0 ? bandwidth : 0;
};

const densityEstimate = (values, x, bandwidth) => {
  const bw = Math.max(bandwidth, 1e-6);
  const inv = 1 / (values.length * bw);
  let sum = 0;
  for (const value of values) {
    sum += gaussianKernel((x - value) / bw);
  }
  return sum * inv;
};

const linspace = (min, max, count) => {
  if (count <= 1 || max === min) {
    return [min];
  }
  const step = (max - min) / (count - 1);
  return Array.from({ length: count }, (_, idx) => min + step * idx);
};

const buildViolinPolygon = (values, idx) => {
  if (!values.length) return null;
  const count = values.length;
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (!Number.isFinite(min) || !Number.isFinite(max)) return null;
  if (min === max) {
    const width = Math.max(Math.abs(min) * 0.02, 0.15);
    const offset = 0.25;
    const points = [
      [min - width, idx - offset],
      [min - width, idx + offset],
      [max + width, idx + offset],
      [max + width, idx - offset],
      [min - width, idx - offset],
    ];
    return { points, stats: { min, max, count } };
  }
  const sampleCount = Math.min(80, Math.max(40, count * 2));
  const samples = linspace(min, max, sampleCount);
  const bandwidth = Math.max(computeBandwidth(values), (max - min) / 100 || 1e-6);
  const densities = samples.map((x) => densityEstimate(values, x, bandwidth));
  const maxDensity = Math.max(...densities) || 1;
  const widthScale = 0.45 / maxDensity;
  const upper = samples.map((x, i) => [x, idx + densities[i] * widthScale]);
  const lower = samples
    .slice()
    .reverse()
    .map((x, i) => {
      const density = densities[densities.length - 1 - i];
      return [x, idx - density * widthScale];
    });
  const points = lower.concat(upper);
  if (points.length) {
    points.push(points[0]);
  }
  return { points, stats: { min, max, count } };
};

const STAT_FIELDS = [
  { key: 'count', label: '样本数', formatter: (value) => (Number.isFinite(value) ? Math.round(value) : '-') },
  { key: 'min', label: '最小值', formatter: (value) => formatNumber(value) },
  { key: 'max', label: '最大值', formatter: (value) => formatNumber(value) },
  { key: 'mean', label: '平均值', formatter: (value) => formatNumber(value) },
  { key: 'median', label: '中位数', formatter: (value) => formatNumber(value) },
  { key: 'std', label: '标准差', formatter: (value) => formatNumber(value) },
];

const DEFAULT_COLUMNS = [
  '弹性模量/GPa',
  '容重/kN·m-3',
  '抗拉强度/MPa',
  '泊松比',
  '内摩擦角',
  '粘聚力/MPa',
];

const AXIS_GROUP_RULES = [
  {
    key: 'depthThickness',
    axisName: '埋深 / 厚度 (m)',
    keywords: ['埋深', '厚度'],
  },
  {
    key: 'mechanical',
    axisName: '力学参数 (MPa/GPa)',
    keywords: ['弹性模量', '抗拉强度', '粘聚力', '内聚力', '黏聚力'],
  },
];

const renderViolinItem = (params, api) => {
  const source = Array.isArray(params.data?.points) ? params.data.points : [];
  if (!source.length) {
    return null;
  }
  const pts = source.map((pt) => api.coord(pt));
  if (!pts.length) {
    return null;
  }
  return {
    type: 'group',
    children: [
      {
        type: 'polygon',
        shape: { points: pts },
        style: {
          fill: 'rgba(79, 134, 217, 0.32)',
          stroke: 'rgba(28, 100, 199, 0.85)',
          lineWidth: 1,
        },
      },
      {
        type: 'polyline',
        shape: { points: pts },
        style: {
          stroke: 'rgba(28, 100, 199, 0.92)',
          lineWidth: 1,
        },
      },
    ],
  };
};

const violinChart = ref(null);
const lithologies = ref([]);
const lithologyCounts = ref({});
const selectedLithology = ref('');
const numericColumns = ref([...DEFAULT_COLUMNS]);
const valueSeries = ref({});
const statsSeries = ref({});
const selectedCount = ref(0);

const isLoadingList = ref(false);
const isLoadingChart = ref(false);

let chartInstance = null;
let resizeHandler = null;
let renderFrame = null;
let resizeTimeout = null;
let initFrame = null;

const chartTitle = computed(() => {
  if (!selectedLithology.value) {
    return '参数分布预览';
  }
  return `${selectedLithology.value} - 参数分布`;
});

const statTableRows = computed(() => {
  if (!numericColumns.value.length) return [];
  return numericColumns.value.map((metric) => {
    const stats = statsSeries.value?.[metric] || {};
    const row = { metric };
    STAT_FIELDS.forEach(({ key, formatter }) => {
      row[key] = formatter(stats[key]);
    });
    return row;
  });
});

const labelWithCount = (name) => {
  const count = lithologyCounts.value?.[name];
  return typeof count === 'number' ? `${name}（${count}）` : name;
};

const waitForContainer = async (elRef, timeoutMs = 2500) => {
  await nextTick();
  return new Promise((resolve) => {
    const start = performance.now();
    const poll = () => {
      const el = elRef?.value;
      if (
        el &&
        el.clientWidth > 0 &&
        el.clientHeight > 0 &&
        getComputedStyle(el).display !== 'none' &&
        getComputedStyle(el).visibility !== 'hidden'
      ) {
        resolve(true);
        return;
      }
      if (performance.now() - start >= timeoutMs) {
        resolve(false);
        return;
      }
      requestAnimationFrame(poll);
    };
    poll();
  });
};

const renderChart = () => {
  if (!chartInstance) {
    return;
  }
  if (renderFrame) {
    cancelAnimationFrame(renderFrame);
  }
  renderFrame = requestAnimationFrame(() => {
    renderFrame = null;
    if (!chartInstance) {
      return;
    }
    const container = violinChart.value;
    if (!container || !container.clientWidth || !container.clientHeight) {
      renderFrame = requestAnimationFrame(renderChart);
      return;
    }
    if (!selectedLithology.value) {
      chartInstance.clear();
      chartInstance.setOption({
        title: {
          text: '请选择岩性以查看参数分布',
          left: 'center',
          top: 'center',
          textStyle: { color: '#999' },
        },
      });
      return;
    }

    const axisLabels = [];
    const cleanedSeries = [];
    const dataMap = valueSeries.value || {};

    for (const col of numericColumns.value) {
      const rawSeries = Array.isArray(dataMap[col]) ? dataMap[col] : [];
      const numericSeries = rawSeries
        .map((value) => Number(value))
        .filter((value) => Number.isFinite(value));
      if (numericSeries.length) {
        axisLabels.push(col);
        cleanedSeries.push(numericSeries);
      }
    }

    if (!axisLabels.length) {
      chartInstance.clear();
      chartInstance.setOption({
        title: {
          text: `岩性 "${selectedLithology.value}" 缺少可分析的数值数据`,
          left: 'center',
          top: 'center',
          textStyle: { color: '#999' },
        },
      });
      return;
    }

    const metricEntries = axisLabels.map((metric, idx) => ({
      metric,
      values: cleanedSeries[idx],
    }));

    const groups = [];
    const groupLookup = new Map();
    const findRule = (name) =>
      AXIS_GROUP_RULES.find((rule) => rule.keywords.some((keyword) => name.includes(keyword)));

    metricEntries.forEach((entry) => {
      const matchedRule = findRule(entry.metric);
      const groupKey = matchedRule ? matchedRule.key : `single:${entry.metric}`;
      let group = groupLookup.get(groupKey);
      if (!group) {
        group = {
          key: groupKey,
          axisName: matchedRule?.axisName || entry.metric,
          metrics: [],
        };
        groupLookup.set(groupKey, group);
        groups.push(group);
      }
      group.metrics.push(entry);
    });

    const totalMetricCount = groups.reduce((sum, group) => sum + group.metrics.length, 0) || 1;
    const topPercent = 12;
    const bottomPercent = 8;
    const gapPercent =
      groups.length > 1 ? Math.max(2, Math.min(6, 18 / Math.max(groups.length - 1, 1))) : 0;
    const availablePercent = Math.max(
      10,
      100 - topPercent - bottomPercent - gapPercent * Math.max(groups.length - 1, 0),
    );

    let currentTop = topPercent;
    const toPercent = (value) => `${Number(value.toFixed(4))}%`;
  const grids = [];
  const xAxes = [];
  const yAxes = [];
  const seriesList = [];
  const gridLeft = 110;  // 增加左边距，为Y轴标签留出更多空间
  const gridRight = 68;
  const xAxisSplitNumber = 6;

    groups.forEach((group, groupIndex) => {
      const ratio = group.metrics.length / totalMetricCount;
      const heightPercent = ratio * availablePercent;
      const allValues = group.metrics.flatMap((item) => item.values);
      const nonEmpty = allValues.length > 0;
      const allNonNegative = nonEmpty && allValues.every((value) => value >= 0);

      let axisMin = null;
      if (allNonNegative) {
        axisMin = 0;
      }

      grids.push({
        top: toPercent(currentTop),
        height: toPercent(heightPercent),
        left: gridLeft,
        right: gridRight,
        containLabel: false,
      });

      const xAxisConfig = {
        type: 'value',
        gridIndex: groupIndex,
        splitLine: { show: true },
        nameLocation: 'end',
        nameGap: 22,
        nameTextStyle: { color: '#1f2937', fontWeight: 500, align: 'left' },
        axisLabel: { color: '#475569', margin: 10 },
        axisLine: { show: true, lineStyle: { color: '#cbd5f5' } },
        axisTick: { show: true, length: 4 },
        splitNumber: xAxisSplitNumber,
      };
      if (axisMin !== null) {
        xAxisConfig.min = axisMin;
      }
      xAxes.push(xAxisConfig);

      yAxes.push({
        type: 'category',
        gridIndex: groupIndex,
        data: group.metrics.map((item) => item.metric),
        boundaryGap: 0.4,
        axisLabel: {
          color: '#475569',
          align: 'right',
          margin: 16,
          // 启用文字换行
          width: 70,
          overflow: 'break',
          lineHeight: 14,
          fontSize: 12
        },
        axisLine: { show: true, lineStyle: { color: '#cbd5f5' } },
        axisTick: { show: false },
      });

      const groupBoxData = group.metrics.map((item) => ({
        value: calculateBoxplot(item.values),
        name: item.metric,
      }));

      seriesList.push({
        name: '箱线图',
        type: 'boxplot',
        layout: 'horizontal',
        xAxisIndex: groupIndex,
        yAxisIndex: groupIndex,
        data: groupBoxData,
        itemStyle: { color: '#4c78a8', borderColor: '#1f4d8f', borderWidth: 1.2 },
        emphasis: { itemStyle: { color: '#355f9c', borderColor: '#163d7a' } },
      });

      const violinData = group.metrics
        .map((item, localIdx) => {
          const polygon = buildViolinPolygon(item.values, localIdx);
          if (!polygon) return null;
          return {
            name: item.metric,
            metric: item.metric,
            points: polygon.points,
            stats: polygon.stats,
          };
        })
        .filter(Boolean);

      if (violinData.length) {
        seriesList.push({
          name: '小提琴',
          type: 'custom',
          coordinateSystem: 'cartesian2d',
          xAxisIndex: groupIndex,
          yAxisIndex: groupIndex,
          silent: false,
          z: -1,
          data: violinData,
          renderItem: renderViolinItem,
        });
      }

      currentTop += heightPercent + (groupIndex < groups.length - 1 ? gapPercent : 0);
    });

    const option = {
      animationDuration: 400,
      title: {
        text: `${selectedLithology.value} - 参数分布`,
        left: gridLeft,
        top: 24,
        textStyle: { align: 'left', textAlign: 'left' },
      },
      legend: {
        data: ['箱线图', '小提琴'],
        selected: { 箱线图: true, 小提琴: seriesList.some((item) => item.type === 'custom') },
        top: 16,
        right: 20,
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (items) => {
          if (!Array.isArray(items) || !items.length) return '';
          const boxItem = items.find((item) => item.seriesType === 'boxplot');
          if (boxItem) {
            const stats = Array.isArray(boxItem.data?.value) ? boxItem.data.value : boxItem.data;
            const label = boxItem.name || boxItem.axisValueLabel || boxItem.axisValue || '';
            if (Array.isArray(stats) && stats.length >= 5) {
              return [
                `${label}`,
                `最小值：${formatNumber(stats[0])}`,
                `下四分位数：${formatNumber(stats[1])}`,
                `中位数：${formatNumber(stats[2])}`,
                `上四分位数：${formatNumber(stats[3])}`,
                `最大值：${formatNumber(stats[4])}`,
              ].join('<br/>');
            }
          }
          const customItem = items.find((item) => item.seriesType === 'custom');
          if (customItem) {
            const stats = customItem.data?.stats || {};
            const label = customItem.name || customItem.axisValueLabel || '';
            return [
              `${label}`,
              `范围：${formatNumber(stats.min)} ~ ${formatNumber(stats.max)}`,
              `样本数：${stats.count ?? '-'}`,
            ].join('<br/>');
          }
          return '';
        },
      },
      grid: grids,
      xAxis: xAxes,
      yAxis: yAxes,
      series: seriesList,
    };

    chartInstance.clear();
    chartInstance.setOption(option, true);
  });
};

const initChart = async () => {
  await waitForContainer(violinChart);
  if (initFrame) {
    cancelAnimationFrame(initFrame);
    initFrame = null;
  }
  const container = violinChart.value;
  if (!container) {
    return;
  }
  const attemptInit = () => {
    if (!container.clientWidth || !container.clientHeight) {
      initFrame = requestAnimationFrame(attemptInit);
      return;
    }
    if (chartInstance) {
      chartInstance.dispose();
    }
    chartInstance = echarts.init(container);
    renderChart();
  };
  attemptInit();
};

const fetchLithologyList = async () => {
  isLoadingList.value = true;
  try {
    const res = await fetch(`${API_BASE}/database/lithologies`).then((r) => r.json());
    if (res.status !== 'success') {
      throw new Error(res.detail || res.message || '获取岩性列表失败');
    }
    lithologies.value = res.lithologies || [];
    lithologyCounts.value = res.counts || {};
    if (Array.isArray(res.numeric_columns) && res.numeric_columns.length) {
      numericColumns.value = res.numeric_columns;
    } else {
      numericColumns.value = [...DEFAULT_COLUMNS];
    }
    if (!selectedLithology.value && lithologies.value.length) {
      selectedLithology.value = lithologies.value[0];
      await fetchLithologyValues(selectedLithology.value);
    }
  } catch (error) {
    console.error('获取岩性列表失败:', error);
    ElMessage.error(error.message || '获取岩性数据失败');
  } finally {
    isLoadingList.value = false;
  }
};

const fetchLithologyValues = async (name) => {
  if (!name) {
    valueSeries.value = {};
    statsSeries.value = {};
    selectedCount.value = 0;
    renderChart();
    return;
  }
  isLoadingChart.value = true;
  try {
    const query = new URLSearchParams({ lithology: name });
    const res = await fetch(`${API_BASE}/database/lithology-data?${query.toString()}`).then((r) => r.json());
    if (res.status !== 'success') {
      throw new Error(res.detail || res.message || '获取岩性数值失败');
    }
    valueSeries.value = res.values || {};
    statsSeries.value = res.stats || {};
    selectedCount.value = Number(res.count) || 0;
  } catch (error) {
    console.error('获取岩性数值失败:', error);
    valueSeries.value = {};
    statsSeries.value = {};
    selectedCount.value = 0;
    ElMessage.error(error.message || '获取岩性数值失败');
  } finally {
    isLoadingChart.value = false;
    nextTick(() => {
      renderChart();
    });
  }
};

const handleLithologyChange = async (name) => {
  await fetchLithologyValues(name || '');
};

onMounted(async () => {
  await initChart();
  await fetchLithologyList();
  const scheduleResize = () => {
    if (!chartInstance || isLoadingChart.value) return;
    if (resizeTimeout) {
      clearTimeout(resizeTimeout);
    }
    resizeTimeout = setTimeout(() => {
      resizeTimeout = null;
      const target = violinChart.value;
      if (!target) return;
      const width = target.clientWidth;
      const height = target.clientHeight;
      if (!width || !height) return;
      try {
        chartInstance?.resize();
      } catch (error) {
        console.warn('Chart resize skipped:', error);
      }
    }, 80);
  };
  resizeHandler = () => {
    scheduleResize();
  };
  window.addEventListener('resize', resizeHandler);
});

onUnmounted(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler);
    resizeHandler = null;
  }
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
    resizeTimeout = null;
  }
  if (renderFrame) {
    cancelAnimationFrame(renderFrame);
    renderFrame = null;
  }
  if (initFrame) {
    cancelAnimationFrame(initFrame);
    initFrame = null;
  }
  chartInstance?.dispose();
});
</script>

<style scoped>
.lookup-container {
  padding: 20px;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: #f5f7fa;
}

.control-bar {
  display: flex;
  align-items: center;
  gap: 16px;
}

.lithology-select {
  min-width: 260px;
}

.meta {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #475569;
  font-size: 14px;
}

.meta-label {
  color: #64748b;
}

.meta-value {
  font-weight: 600;
  color: #1d4ed8;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: minmax(380px, 2fr) minmax(260px, 1fr);
  gap: 20px;
  flex: 1;
  min-height: 560px;
}

.chart-card,
.stats-card {
  height: 100%;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
}

.chart-card :deep(.el-card__body),
.stats-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stats-card :deep(.el-table) {
  flex: 1;
}

.chart-area {
  flex: 1;
  width: 100%;
  min-height: 360px;
  position: relative;
}

.chart-canvas {
  width: 100%;
  height: 100%;
}

.chart-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background-color: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(2px);
  z-index: 2;
  color: #1f2937;
  font-size: 14px;
}

.loader {
  width: 32px;
  height: 32px;
  border: 3px solid #dbeafe;
  border-top-color: #1d4ed8;
  border-radius: 50%;
  animation: spinner 0.8s linear infinite;
}

.loading-text {
  color: #1e293b;
  font-weight: 500;
}

.stat-metric-col {
  color: #1d4ed8;
  font-weight: 600;
}

@keyframes spinner {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-weight: 600;
  color: #1f2937;
}

.card-subtitle {
  font-size: 12px;
  font-weight: 400;
  color: #94a3b8;
}

@media (min-width: 1400px) {
  .content-grid {
    grid-template-columns: 3fr 2fr;
    grid-template-rows: 1fr;
  }

  .chart-area {
    min-height: 540px;
  }
}
</style>