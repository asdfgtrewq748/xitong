// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// 性能优化：首页立即加载，其他组件懒加载
import EnhancedDashboardView from '../components/enhanced/EnhancedDashboardView.vue'

// 懒加载组件
const KeyStratumView = () => import(/* webpackChunkName: "key-stratum" */ '../components/KeyStratumView.vue')
const BoreholeAnalysisView = () => import(/* webpackChunkName: "borehole" */ '../components/BoreholeAnalysisView.vue')
const CsvFormatterView = () => import(/* webpackChunkName: "csv-formatter" */ '../components/CsvFormatterView.vue')
const DatabaseViewerView = () => import(/* webpackChunkName: "database" */ '../components/DatabaseViewerView.vue')
const GeologicalModelingView = () => import(/* webpackChunkName: "modeling" */ '../components/GeologicalModelingView.vue')
const UpwardMiningFeasibilityView = () => import(/* webpackChunkName: "upward-mining" */ '../components/UpwardMiningFeasibilityView.vue')
const DataManagementView = () => import(/* webpackChunkName: "data-management" */ '../components/DataManagementView.vue')

// 科研绘图模块 - 导航页和独立图表页面
const VisualizationHome = () => import(/* webpackChunkName: "visualization-home" */ '../components/visualization/VisualizationHome.vue')
const ScatterPlotPage = () => import(/* webpackChunkName: "scatter" */ '../components/visualization/pages/ScatterPlotPage.vue')
const LineChartPage = () => import(/* webpackChunkName: "line" */ '../components/visualization/pages/LineChartPage.vue')
const BarChartPage = () => import(/* webpackChunkName: "bar" */ '../components/visualization/pages/BarChartPage.vue')
const HeatMapPage = () => import(/* webpackChunkName: "heatmap" */ '../components/visualization/pages/HeatMapPage.vue')
const Surface3DPage = () => import(/* webpackChunkName: "surface" */ '../components/visualization/pages/Surface3DPage.vue')
const BoxPlotPage = () => import(/* webpackChunkName: "box" */ '../components/visualization/pages/BoxPlotPage.vue')
const HistogramPage = () => import(/* webpackChunkName: "histogram" */ '../components/visualization/pages/HistogramPage.vue')
const StatisticalAnalysisPage = () => import(/* webpackChunkName: "statistics" */ '../components/visualization/pages/StatisticalAnalysisPage.vue')
const TunnelSupportView = () => import(/* webpackChunkName: "tunnel-support" */ '../components/TunnelSupportView.vue')

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: EnhancedDashboardView,
    meta: { title: '工作台', keepAlive: true }  // 首页缓存
  },
  {
    path: '/key-stratum',
    name: 'KeyStratum',
    component: KeyStratumView,
    meta: { title: '关键层计算' }
  },
  {
    path: '/tunnel-support',
    name: 'TunnelSupport',
    component: TunnelSupportView,
    meta: { title: '巷道支护计算' }
  },
  {
    path: '/borehole-analysis',
    name: 'BoreholeAnalysis',
    component: BoreholeAnalysisView,
    meta: { title: '钻孔数据分析' }
  },
  {
    path: '/csv-formatter',
    name: 'CsvFormatter',
    component: CsvFormatterView,
    meta: { title: 'CSV 格式化工具' }
  },
  {
    path: '/database-viewer',
    name: 'DatabaseViewer',
    component: DatabaseViewerView,
    meta: { title: '数据库管理', keepAlive: true }  // 数据库页面缓存
  },
  {
    path: '/geological-modeling',
    name: 'GeologicalModeling',
    component: GeologicalModelingView,
    meta: { title: '三维地质建模' }
  },
  {
    path: '/upward-mining-feasibility',
    name: 'UpwardMiningFeasibility',
    component: UpwardMiningFeasibilityView,
    meta: { title: '上行开采可行度分析' }
  },
  {
    path: '/visualization',
    name: 'VisualizationHome',
    component: VisualizationHome,
    meta: { title: '科研绘图' }
  },
  {
    path: '/visualization/scatter',
    name: 'ScatterPlot',
    component: ScatterPlotPage,
    meta: { title: '散点图' }
  },
  {
    path: '/visualization/line',
    name: 'LineChart',
    component: LineChartPage,
    meta: { title: '折线图' }
  },
  {
    path: '/visualization/bar',
    name: 'BarChart',
    component: BarChartPage,
    meta: { title: '柱状图' }
  },
  {
    path: '/visualization/heatmap',
    name: 'HeatMap',
    component: HeatMapPage,
    meta: { title: '热力图' }
  },
  {
    path: '/visualization/surface',
    name: 'Surface3D',
    component: Surface3DPage,
    meta: { title: '3D曲面图' }
  },
  {
    path: '/visualization/box',
    name: 'BoxPlot',
    component: BoxPlotPage,
    meta: { title: '箱线图' }
  },
  {
    path: '/visualization/histogram',
    name: 'Histogram',
    component: HistogramPage,
    meta: { title: '直方图' }
  },
  {
    path: '/visualization/statistics',
    name: 'StatisticalAnalysis',
    component: StatisticalAnalysisPage,
    meta: { title: '统计分析' }
  },
  {
    path: '/data-management',
    name: 'DataManagement',
    component: DataManagementView,
    meta: { title: '数据管理中心' }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router