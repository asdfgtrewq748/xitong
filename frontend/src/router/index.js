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

// 科研绘图模块 - 统一工作台
const VisualizationHome = () => import(/* webpackChunkName: "visualization" */ '../components/visualization/ImprovedVisualizationHome.vue')
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
    name: 'Visualization',
    component: VisualizationHome,
    meta: { title: '科研绘图工作台' }
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