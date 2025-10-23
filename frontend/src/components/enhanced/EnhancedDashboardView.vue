<template>
  <div class="enhanced-dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1 class="welcome-title">🏔️ 欢迎使用矿山工程分析系统</h1>
          <p class="welcome-subtitle">专业的地质数据处理与分析平台</p>
          <p class="welcome-description">
            本系统集成了钻孔数据分析、关键层计算、上行开采可行性分析等核心功能，
            为矿山工程提供专业的技术支持。
          </p>
        </div>
        <div class="welcome-stats">
          <div class="stat-item">
            <div class="stat-number">{{ totalBoreholes }}</div>
            <div class="stat-label">钻孔数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ totalCoalSeams }}</div>
            <div class="stat-label">煤层层数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ totalMines }}</div>
            <div class="stat-label">矿井数量</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能模块网格 -->
    <div class="modules-grid">
      <div class="module-card" @click="navigateTo('/')">
        <div class="module-icon">📊</div>
        <h3>工作台</h3>
        <p>数据概览和快速操作</p>
      </div>

      <div class="module-card data-module" @click="navigateTo('/data-management')">
        <div class="module-icon">📊</div>
        <h3>数据管理</h3>
        <p>钻孔数据导入与管理</p>
        <div class="module-badge">新功能</div>
      </div>

      <div class="module-card analysis-module" @click="navigateTo('/key-stratum')">
        <div class="module-icon">🔬</div>
        <h3>关键层计算</h3>
        <p>岩层力学参数分析</p>
      </div>

      <div class="module-card borehole-module" @click="navigateTo('/borehole-analysis')">
        <div class="module-icon">🔍</div>
        <h3>钻孔分析</h3>
        <p>钻孔数据深度分析</p>
      </div>

      <div class="module-card mining-module" @click="navigateTo('/upward-mining-feasibility')">
        <div class="module-icon">⛏️</div>
        <h3>开采分析</h3>
        <p>上行开采可行性评估</p>
      </div>

      <div class="module-card modeling-module" @click="navigateTo('/geological-modeling')">
        <div class="module-icon">🏗️</div>
        <h3>地质建模</h3>
        <p>三维地质模型构建</p>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="recent-activity">
      <el-card>
        <template #header>
          <div class="activity-header">
            <span>🕐 最近活动</span>
            <el-button type="text" @click="refreshActivity">刷新</el-button>
          </div>
        </template>
        <div class="activity-list">
          <div class="activity-item" v-for="activity in recentActivities" :key="activity.id">
            <div class="activity-icon">{{ activity.icon }}</div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-card>
        <template #header>
          <span>⚡ 快速操作</span>
        </template>
        <div class="actions-grid">
          <el-button
            type="primary"
            size="large"
            @click="quickAction('import')"
            icon="upload"
          >
            导入数据
          </el-button>
          <el-button
            type="success"
            size="large"
            @click="quickAction('analyze')"
            icon="data-analysis"
          >
            快速分析
          </el-button>
          <el-button
            type="warning"
            size="large"
            @click="quickAction('export')"
            icon="download"
          >
            导出报告
          </el-button>
          <el-button
            type="info"
            size="large"
            @click="quickAction('help')"
            icon="question"
          >
            使用帮助
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 响应式数据
const totalBoreholes = ref(12)
const totalCoalSeams = ref(8)
const totalMines = ref(5)

const recentActivities = ref([
  { id: 1, icon: '📥', title: '导入了BK-1钻孔数据', time: '2分钟前' },
  { id: 2, icon: '🔬', title: '完成了关键层计算分析', time: '15分钟前' },
  { id: 3, icon: '📊', title: '生成了地质报告', time: '1小时前' },
  { id: 4, icon: '⚡', title: '更新了系统参数', time: '2小时前' },
  { id: 5, icon: '🎯', title: '完成了开采可行性评估', time: '3小时前' }
])

// 方法
const navigateTo = (path) => {
  router.push(path)
}

const refreshActivity = () => {
  // 模拟刷新活动
  ElMessage.success('活动列表已刷新')
}

const quickAction = (action) => {
  switch (action) {
    case 'import':
      router.push('/data-management')
      break
    case 'analyze':
      router.push('/key-stratum')
      break
    case 'export':
      ElMessage.info('正在生成报告...')
      break
    case 'help':
      ElMessage.info('正在打开帮助文档...')
      break
  }
}

// 初始化
onMounted(() => {
  // 可以在这里加载数据统计
  console.log('Enhanced Dashboard loaded')
})
</script>

<style scoped>
.enhanced-dashboard {
  padding: 0;
  min-height: 100vh;
}

/* 欢迎区域 */
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  border-radius: 20px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-text {
  flex: 1;
}

.welcome-title {
  font-size: 2.5em;
  margin: 0 0 15px 0;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.welcome-subtitle {
  font-size: 1.2em;
  margin: 0 0 20px 0;
  opacity: 0.9;
}

.welcome-description {
  font-size: 1em;
  line-height: 1.6;
  opacity: 0.8;
  max-width: 500px;
}

.welcome-stats {
  display: flex;
  gap: 30px;
  margin-left: 50px;
}

.stat-item {
  text-align: center;
  background: rgba(255,255,255,0.1);
  padding: 20px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  min-width: 120px;
}

.stat-number {
  font-size: 2.5em;
  font-weight: bold;
  margin-bottom: 5px;
  background: linear-gradient(45deg, #fff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.9em;
  opacity: 0.8;
}

/* 功能模块网格 */
.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.module-card {
  background: white;
  border-radius: 15px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  position: relative;
  overflow: hidden;
}

.module-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.2);
}

.module-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.module-card.data-module::before {
  background: linear-gradient(90deg, #52c41a, #73d13d);
}

.module-card.analysis-module::before {
  background: linear-gradient(90deg, #1890ff, #40a9ff);
}

.module-card.borehole-module::before {
  background: linear-gradient(90deg, #722ed1, #9254de);
}

.module-card.mining-module::before {
  background: linear-gradient(90deg, #fa8c16, #ffa940);
}

.module-card.modeling-module::before {
  background: linear-gradient(90deg, #13c2c2, #18a058);
}

.module-icon {
  font-size: 3em;
  margin-bottom: 15px;
  display: block;
}

.module-card h3 {
  margin: 0 0 10px 0;
  font-size: 1.3em;
  color: #303133;
  font-weight: 600;
}

.module-card p {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 0.95em;
  line-height: 1.4;
}

.module-badge {
  display: inline-block;
  background: #ff4757;
  color: white;
  font-size: 0.8em;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 500;
}

/* 最近活动 */
.recent-activity {
  margin-bottom: 30px;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: background 0.3s ease;
}

.activity-item:hover {
  background: #e9ecef;
}

.activity-icon {
  font-size: 1.5em;
  margin-right: 15px;
  width: 40px;
  height: 40px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.activity-time {
  font-size: 0.85em;
  color: #666;
}

/* 快速操作 */
.quick-actions {
  margin-bottom: 30px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .welcome-stats {
    margin-left: 0;
    justify-content: center;
  }

  .modules-grid {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .welcome-section {
    padding: 20px;
  }

  .welcome-title {
    font-size: 2em;
  }

  .stat-item {
    min-width: 100px;
    padding: 15px;
  }

  .module-card {
    padding: 20px;
  }

  .module-icon {
    font-size: 2em;
  }
}
</style>