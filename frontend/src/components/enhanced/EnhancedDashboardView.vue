<template>
  <div class="dashboard">
    <!-- Page Header -->
    <header class="page-header">
      <div>
        <h1 class="page-title">工作台</h1>
        <p class="page-desc">采矿工程数据分析平台</p>
      </div>
    </header>

    <!-- Stats Row -->
    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon--cyan">📊</div>
        <div class="stat-body">
          <span class="stat-value">{{ totalBoreholes }}</span>
          <span class="stat-label">钻孔数量</span>
        </div>
        <span class="stat-badge stat-badge--active">实时</span>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon--emerald">📚</div>
        <div class="stat-body">
          <span class="stat-value">{{ totalCoalSeams }}</span>
          <span class="stat-label">煤层段数</span>
        </div>
        <span class="stat-badge">已分类</span>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon--violet">📏</div>
        <div class="stat-body">
          <span class="stat-value">{{ averageThickness.toFixed(1) }}<small class="stat-unit">m</small></span>
          <span class="stat-label">平均剖面厚度</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon--amber">📐</div>
        <div class="stat-body">
          <span class="stat-value">{{ maxThickness.toFixed(1) }}<small class="stat-unit">m</small></span>
          <span class="stat-label">最大剖面厚度</span>
        </div>
      </div>
    </section>

    <!-- Quick Action Banner -->
    <section class="action-banner" @click="router.push('/tools/data-management')">
      <div class="action-banner__icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      </div>
      <div class="action-banner__text">
        <h3 class="action-banner__title">全局数据导入中心</h3>
        <p class="action-banner__desc">统一管理钻孔数据、煤层信息与工程参数 · 支持 CSV、Excel、JSON 格式</p>
      </div>
      <button class="action-banner__btn">立即导入</button>
    </section>

    <!-- Tools Grid -->
    <section class="tools-grid">
      <div v-for="tool in tools" :key="tool.name" 
           class="tool-card" 
           :class="[`tool-card--${tool.color}`]"
           @click="router.push(tool.route)">
        <div class="tool-card__header">
          <span class="tool-card__icon">{{ tool.icon }}</span>
          <span v-if="tool.badge" class="tool-card__badge" :class="`tool-card__badge--${tool.badgeType}`">{{ tool.badge }}</span>
        </div>
        <h3 class="tool-card__title">{{ tool.name }}</h3>
        <p class="tool-card__desc">{{ tool.desc }}</p>
        <div class="tool-card__footer">
          <span class="tool-card__action">{{ tool.action }}</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { summary as datasetSummary } from '@/data'

const router = useRouter()

const totalBoreholes = datasetSummary.boreholeCount
const totalCoalSeams = datasetSummary.totalCoalLayers
const averageThickness = datasetSummary.averageThickness
const maxThickness = datasetSummary.maxThickness

const tools = [
  { name: '岩石力学数据库', icon: '🪨', desc: '存储与管理岩石物理力学性质参数，提供智能检索与统计分析功能', action: '访问数据库', route: '/tools/database-viewer', color: 'indigo', badge: 'Active', badgeType: 'success' },
  { name: '钻孔数据分析', icon: '📍', desc: '深度解析钻孔数据，自动生成地质剖面图与三维模型预览', action: '开始分析', route: '/tools/borehole-analysis', color: 'cyan', badge: 'Standby', badgeType: 'neutral' },
  { name: '上行开采可行性', icon: '⬆️', desc: '评估多煤层开采条件，计算层间距与岩层移动规律', action: '进入评估', route: '/tools/upward-mining-feasibility', color: 'amber', badge: 'Ready', badgeType: 'neutral' },
  { name: '三维地质建模', icon: '🌐', desc: '构建高精度三维地质体模型，支持切片查看与体积计算', action: '启动建模', route: '/tools/geological-modeling', color: 'emerald', badge: 'Beta', badgeType: 'neutral' },
  { name: '巷道支护计算', icon: '🛡️', desc: '智能计算巷道支护参数，生成科学的支护方案建议', action: '开始计算', route: '/tools/tunnel-support', color: 'orange', badge: 'New', badgeType: 'neutral' },
  { name: '采掘设计功能', icon: '✏️', desc: '辅助进行采掘工程设计与规划，优化开采布局', action: '进入设计', route: '/tools/mining-design', color: 'purple', badge: 'Tool', badgeType: 'neutral' },
  { name: '科研绘图', icon: '📈', desc: '生成高质量科研图表，支持散点、折线、热力等多种图表类型', action: '开始绘图', route: '/tools/visualization', color: 'pink', badge: 'Pro', badgeType: 'neutral' },
  { name: 'CSV 格式化工具', icon: '📋', desc: '快速处理和格式化数据文件，一键适配系统输入要求', action: '打开工具', route: '/tools/csv-formatter', color: 'blue', badge: 'Util', badgeType: 'neutral' },
]
</script>

<style scoped>
.dashboard {
  padding: 0;
}

/* ── Header ── */
.page-header {
  margin-bottom: 28px;
}
.page-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
  margin-bottom: 4px;
}
.page-desc {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

/* ── Stats Grid ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}
.stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: box-shadow 200ms cubic-bezier(0.16, 1, 0.3, 1);
}
.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.stat-icon--cyan { background: #ecfeff; }
.stat-icon--emerald { background: #ecfdf5; }
.stat-icon--violet { background: #f5f3ff; }
.stat-icon--amber { background: #fffbeb; }
.stat-body {
  flex: 1;
  min-width: 0;
}
.stat-value {
  display: block;
  font-family: 'DM Sans', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
  letter-spacing: -0.02em;
}
.stat-unit {
  font-size: 13px;
  font-weight: 500;
  color: #94a3b8;
  margin-left: 2px;
}
.stat-label {
  display: block;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}
.stat-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 9999px;
  white-space: nowrap;
  background: #f1f5f9;
  color: #64748b;
}
.stat-badge--active {
  background: #ecfdf5;
  color: #059669;
}

/* ── Action Banner ── */
.action-banner {
  background: linear-gradient(135deg, #059669 0%, #047857 50%, #065f46 100%);
  border-radius: 12px;
  padding: 24px 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: transform 200ms ease, box-shadow 200ms ease;
  margin-bottom: 28px;
  color: #ffffff;
}
.action-banner:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(5, 150, 105, 0.2);
}
.action-banner__icon {
  width: 52px;
  height: 52px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.action-banner__icon svg {
  opacity: 0.9;
}
.action-banner__text {
  flex: 1;
  min-width: 0;
}
.action-banner__title {
  font-family: 'DM Sans', sans-serif;
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 4px;
  color: #fff;
}
.action-banner__desc {
  font-size: 13px;
  opacity: 0.8;
  margin: 0;
  line-height: 1.4;
}
.action-banner__btn {
  background: #ffffff;
  color: #059669;
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  font-weight: 700;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 150ms ease;
  flex-shrink: 0;
}
.action-banner__btn:hover {
  background: #f0fdf4;
}

/* ── Tools Grid ── */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.tool-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: border-color 200ms ease, box-shadow 200ms ease, transform 200ms ease;
}
.tool-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}
.tool-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.tool-card__icon {
  font-size: 22px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}
.tool-card--indigo .tool-card__icon { background: #eef2ff; }
.tool-card--cyan .tool-card__icon { background: #ecfeff; }
.tool-card--amber .tool-card__icon { background: #fffbeb; }
.tool-card--emerald .tool-card__icon { background: #ecfdf5; }
.tool-card--orange .tool-card__icon { background: #fff7ed; }
.tool-card--purple .tool-card__icon { background: #f5f3ff; }
.tool-card--pink .tool-card__icon { background: #fdf2f8; }
.tool-card--blue .tool-card__icon { background: #eff6ff; }

.tool-card__badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 9999px;
}
.tool-card__badge--success { background: #ecfdf5; color: #059669; }
.tool-card__badge--neutral { background: #f1f5f9; color: #64748b; }

.tool-card__title {
  font-family: 'DM Sans', sans-serif;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px;
  line-height: 1.3;
}
.tool-card__desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 18px;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.tool-card__footer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #059669;
  padding-top: 14px;
  border-top: 1px solid #f1f5f9;
}
.tool-card__footer svg {
  color: #059669;
  transition: transform 200ms ease;
}
.tool-card:hover .tool-card__footer svg {
  transform: translateX(3px);
}

/* ── Responsive ── */
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .tools-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .stat-card { padding: 14px 16px; }
  .stat-value { font-size: 20px; }
  .action-banner { flex-direction: column; text-align: center; padding: 20px; }
  .action-banner__btn { width: 100%; }
  .tools-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .tool-card { padding: 16px; }
  .page-header { margin-bottom: 20px; }
  .page-title { font-size: 19px; }
}
</style>
