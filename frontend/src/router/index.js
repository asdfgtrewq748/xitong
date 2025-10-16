// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

import DashboardView from '../components/DashboardView.vue'
import KeyStratumView from '../components/KeyStratumView.vue'
import BoreholeAnalysisView from '../components/BoreholeAnalysisView.vue'
import CsvFormatterView from '../components/CsvFormatterView.vue'
import DatabaseViewerView from '../components/DatabaseViewerView.vue'
import GeologicalModelingView from '../components/GeologicalModelingView.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { title: '工作台' }
  },
  {
    path: '/key-stratum',
    name: 'KeyStratum',
    component: KeyStratumView,
    meta: { title: '关键层计算' }
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
    meta: { title: '数据库管理' }
  }, 
  { 
    path: '/geological-modeling',
    name: 'GeologicalModeling',
    component: GeologicalModelingView,
    meta: { title: '三维地质建模' }
  } 
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router