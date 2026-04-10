<template>
  <div class="app-container">
    <!-- Mobile Overlay -->
    <div v-if="drawerVisible" class="mobile-overlay" @click="drawerVisible = false"></div>

    <!-- Sidebar (desktop: always visible, mobile: drawer) -->
    <aside :class="['sidebar', { 'sidebar--open': drawerVisible, 'sidebar--mobile': isMobile }]">
      <div class="sidebar-header">
        <span class="logo-text">⛏️ 采矿工具箱</span>
        <button v-if="isMobile" class="close-btn" @click="drawerVisible = false">✕</button>
      </div>

      <nav class="menu">
        <router-link to="/tools" class="menu-item" @click="closeDrawer">
          <span class="icon">🏠</span> 工作台
        </router-link>

        <div class="menu-group">
          <div class="group-title">数据与参数</div>
          <router-link to="/tools/database-viewer" class="menu-item sub" @click="closeDrawer">📂 数据库管理</router-link>
          <router-link to="/tools/csv-formatter" class="menu-item sub" @click="closeDrawer">📋 CSV 格式化</router-link>
          <router-link to="/tools/data-management" class="menu-item sub" @click="closeDrawer">📊 数据管理中心</router-link>
        </div>

        <div class="menu-group">
          <div class="group-title">分析计算</div>
          <router-link to="/tools/key-stratum" class="menu-item sub" @click="closeDrawer">🔑 关键层计算</router-link>
          <router-link to="/tools/tunnel-support" class="menu-item sub" @click="closeDrawer">🛡️ 巷道支护计算</router-link>
          <router-link to="/tools/roof-pressure" class="menu-item sub" @click="closeDrawer">⚙️ 支架阻力计算</router-link>
          <router-link to="/tools/borehole-analysis" class="menu-item sub" @click="closeDrawer">📍 钻孔数据分析</router-link>
          <router-link to="/tools/upward-mining-feasibility" class="menu-item sub" @click="closeDrawer">⬆️ 上行开采可行性</router-link>
        </div>

        <div class="menu-group">
          <div class="group-title">工程设计</div>
          <router-link to="/tools/mining-design" class="menu-item sub" @click="closeDrawer">✏️ 采掘设计功能</router-link>
        </div>

        <div class="menu-group">
          <div class="group-title">地质与建模</div>
          <router-link to="/tools/geological-modeling" class="menu-item sub" @click="closeDrawer">🌐 三维地质建模</router-link>
        </div>

        <div class="menu-group">
          <div class="group-title">科研绘图</div>
          <router-link to="/tools/visualization/scatter" class="menu-item sub" @click="closeDrawer">· 散点图</router-link>
          <router-link to="/tools/visualization/line" class="menu-item sub" @click="closeDrawer">· 折线图</router-link>
          <router-link to="/tools/visualization/bar" class="menu-item sub" @click="closeDrawer">· 柱状图</router-link>
          <router-link to="/tools/visualization/heatmap" class="menu-item sub" @click="closeDrawer">· 热力图</router-link>
          <router-link to="/tools/visualization/surface" class="menu-item sub" @click="closeDrawer">· 3D曲面图</router-link>
          <router-link to="/tools/visualization/box" class="menu-item sub" @click="closeDrawer">· 箱线图</router-link>
          <router-link to="/tools/visualization/histogram" class="menu-item sub" @click="closeDrawer">· 直方图</router-link>
          <router-link to="/tools/visualization/statistics" class="menu-item sub" @click="closeDrawer">· 统计分析</router-link>
        </div>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-area">
      <!-- Mobile Top Bar with Hamburger -->
      <header v-if="isMobile" class="mobile-header">
        <button class="hamburger" @click="drawerVisible = true">
          <span></span><span></span><span></span>
        </button>
        <h1>{{ currentTitle }}</h1>
        <div style="width:32px"></div>
      </header>

      <!-- Desktop Header (minimal) -->
      <header v-else class="desktop-header">
        <h1>{{ currentTitle }}</h1>
      </header>

      <div class="content-body">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const drawerVisible = ref(false)
const isMobile = ref(window.innerWidth <= 768)

const currentTitle = computed(() => route.meta.title || '工作台')

const closeDrawer = () => {
  if (isMobile.value) drawerVisible.value = false
}

const handleResize = () => {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) drawerVisible.value = false
}

onMounted(() => window.addEventListener('resize', handleResize))
onUnmounted(() => window.removeEventListener('resize', handleResize))
</script>

<style scoped>
.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #f0f4f8;
}

/* ===== SIDEBAR ===== */
.sidebar {
  width: 240px;
  min-width: 240px;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
  z-index: 100;
}

.sidebar--mobile {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  transform: translateX(-100%);
  box-shadow: 4px 0 20px rgba(0,0,0,0.15);
}

.sidebar--open {
  transform: translateX(0);
}

.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 99;
}

.sidebar-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-text {
  font-size: 16px;
  font-weight: 800;
  color: #1e293b;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #94a3b8;
  padding: 4px 8px;
}

/* ===== MENU ===== */
.menu {
  padding: 12px 0;
  flex: 1;
}

.menu-group {
  margin-bottom: 4px;
}

.group-title {
  padding: 10px 20px 6px;
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.menu-item {
  display: block;
  padding: 10px 20px;
  color: #475569;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: #f1f5f9;
  color: #7c3aed;
}

.menu-item.router-link-active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border-left-color: #4f46e5;
  font-weight: 600;
}

.menu-item.sub {
  padding-left: 32px;
  font-size: 13px;
}

/* ===== MAIN AREA ===== */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* Desktop Header */
.desktop-header {
  height: 56px;
  min-height: 56px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  background: rgba(255,255,255,0.7);
  backdrop-filter: blur(8px);
}

.desktop-header h1 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

/* Mobile Header */
.mobile-header {
  height: 52px;
  min-height: 52px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
}

.hamburger {
  width: 36px;
  height: 36px;
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px;
}

.hamburger span {
  display: block;
  width: 18px;
  height: 2px;
  background: #475569;
  border-radius: 1px;
  transition: all 0.2s;
}

.mobile-header h1 {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

/* Content Body */
.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f0f4f8;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ===== MOBILE ADJUSTMENTS ===== */
@media (max-width: 768px) {
  .content-body {
    padding: 12px;
  }
}
</style>
