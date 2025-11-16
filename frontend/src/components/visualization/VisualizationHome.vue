<template>
  <div class="visualization-home">
    <el-page-header @back="$router.push('/')">
      <template #content>
        <span class="page-title">数据可视化</span>
      </template>
    </el-page-header>

    <div class="content-area">
      <div class="chart-grid">
        <el-card
          v-for="chart in chartTypes"
          :key="chart.name"
          class="chart-card"
          shadow="hover"
          @click="navigateTo(chart.route)"
        >
          <template #header>
            <div class="card-header">
              <el-icon :size="24" :color="chart.color">
                <component :is="chart.icon" />
              </el-icon>
              <span class="chart-name">{{ chart.name }}</span>
            </div>
          </template>
          <div class="chart-description">{{ chart.description }}</div>
          <div class="chart-features">
            <el-tag v-for="feature in chart.features" :key="feature" size="small" type="info">
              {{ feature }}
            </el-tag>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { markRaw } from 'vue'
import { useRouter } from 'vue-router'
import {
  TrendCharts,
  DataLine,
  Histogram,
  Grid,
  DataBoard,
  DataAnalysis,
  PieChart
} from '@element-plus/icons-vue'

const router = useRouter()

const chartTypes = [
  {
    name: '散点图',
    route: '/visualization/scatter',
    icon: markRaw(TrendCharts),
    color: '#409EFF',
    description: '适用于展示两个变量之间的相关性和分布',
    features: ['相关分析', '回归拟合', '分组着色']
  },
  {
    name: '折线图',
    route: '/visualization/line',
    icon: markRaw(DataLine),
    color: '#67C23A',
    description: '适用于展示数据随时间或连续变量的变化趋势',
    features: ['趋势分析', '多条线对比', '仅导出曲线']
  },
  {
    name: '柱状图',
    route: '/visualization/bar',
    icon: markRaw(Histogram),
    color: '#E6A23C',
    description: '适用于比较不同类别或组之间的数值差异',
    features: ['分类对比', '分组显示', '数据排序']
  },
  {
    name: '热力图',
    route: '/visualization/heatmap',
    icon: markRaw(Grid),
    color: '#F56C6C',
    description: '适用于展示二维数据的密度和模式',
    features: ['密度分析', '矩阵可视化', '颜色映射']
  },
  {
    name: '3D曲面图',
    route: '/visualization/surface',
    icon: markRaw(PieChart),
    color: '#909399',
    description: '适用于展示三维数据的空间分布和曲面变化',
    features: ['空间分析', '曲面拟合', '交互旋转']
  },
  {
    name: '箱线图',
    route: '/visualization/box',
    icon: markRaw(DataBoard),
    color: '#73C0DE',
    description: '适用于展示数据的分布、离散程度和异常值',
    features: ['分位数', '异常检测', '多组对比']
  },
  {
    name: '直方图',
    route: '/visualization/histogram',
    icon: markRaw(DataAnalysis),
    color: '#5470C6',
    description: '适用于展示数据的频率分布和统计特征',
    features: ['频数统计', '分布分析', '累积频率']
  }
]

function navigateTo(route) {
  router.push(route)
}
</script>

<style scoped>
.visualization-home {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.content-area {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.chart-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.chart-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
  min-height: 48px;
}

.chart-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.el-page-header {
  padding: 16px 24px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}
</style>
