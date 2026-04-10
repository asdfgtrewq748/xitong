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
        <router-link to="/tools" class="menu-item menu-item--primary" @click="closeDrawer">
          <span class="menu-icon">🏠</span>
          <span>工作台</span>
        </router-link>

        <div class="menu-group">
          <div class="group-title">数据与参数</div>
          <router-link to="/tools/database-viewer" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">📂</span><span>数据库管理</span>
          </router-link>
          <router-link to="/tools/csv-formatter" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">📋</span><span>CSV 格式化</span>
          </router-link>
          <router-link to="/tools/data-management" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">📊</span><span>数据管理中心</span>
          </router-link>
        </div>

        <div class="menu-group">
          <div class="group-title">分析计算</div>
          <router-link to="/tools/key-stratum" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">🔑</span><span>关键层计算</span>
          </router-link>
          <router-link to="/tools/tunnel-support" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">🛡️</span><span>巷道支护计算</span>
          </router-link>
          <router-link to="/tools/roof-pressure" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">⚙️</span><span>支架阻力计算</span>
          </router-link>
          <router-link to="/tools/borehole-analysis" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">📍</span><span>钻孔数据分析</span>
          </router-link>
          <router-link to="/tools/upward-mining-feasibility" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">⬆️</span><span>上行开采可行性</span>
          </router-link>
        </div>

        <div class="menu-group">
          <div class="group-title">工程设计</div>
          <router-link to="/tools/mining-design" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">✏️</span><span>采掘设计功能</span>
          </router-link>
        </div>

        <div class="menu-group">
          <div class="group-title">地质与建模</div>
          <router-link to="/tools/geological-modeling" class="menu-item" @click="closeDrawer">
            <span class="menu-icon">🌐</span><span>三维地质建模</span>
          </router-link>
        </div>

        <div class="menu-group">
          <div class="group-title">科研绘图</div>
          <router-link to="/tools/visualization/scatter" class="menu-item menu-item--sub" @click="closeDrawer">散点图</router-link>
          <router-link to="/tools/visualization/line" class="menu-item menu-item--sub" @click="closeDrawer">折线图</router-link>
          <router-link to="/tools/visualization/bar" class="menu-item menu-item--sub" @click="closeDrawer">柱状图</router-link>
          <router-link to="/tools/visualization/heatmap" class="menu-item menu-item--sub" @click="closeDrawer">热力图</router-link>
          <router-link to="/tools/visualization/surface" class="menu-item menu-item--sub" @click="closeDrawer">3D曲面图</router-link>
          <router-link to="/tools/visualization/box" class="menu-item menu-item--sub" @click="closeDrawer">箱线图</router-link>
          <router-link to="/tools/visualization/histogram" class="menu-item menu-item--sub" @click="closeDrawer">直方图</router-link>
          <router-link to="/tools/visualization/statistics" class="menu-item menu-item--sub" @click="closeDrawer">统计分析</router-link>
        </div>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-area">
      <!-- Mobile Top Bar with Hamburger -->
      <header v-if="isMobile" class="topbar topbar--mobile">
        <button class="hamburger" @click="drawerVisible = true" aria-label="打开菜单">
          <span></span><span></span><span></span>
        </button>
        <h1 class="topbar-title">{{ currentTitle }}</h1>
        <div style="width:32px"></div>
      </header>

      <!-- Desktop Header (minimal) -->
      <header v-else class="topbar topbar--desktop">
        <h1 class="topbar-title">{{ currentTitle }}</h1>
        <div class="topbar-breadcrumb">
          <span class="breadcrumb-item">工具</span>
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-item breadcrumb-current">{{ currentTitle }}</span>
        </div>
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
/* ============================================
   Layout Container
   ============================================ */
.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #f8fafc;
}

/* ============================================
   Sidebar
   ============================================ */
.sidebar {
  width: 250px;
  min-width: 250px;
  height: 100%;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  transition: transform 300ms cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 100;
  flex-shrink: 0;
}

.sidebar--mobile {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  transform: translateX(-100%);
  box-shadow: 8px 0 30px rgba(0, 0, 0, 0.08);
}

.sidebar--open {
  transform: translateX(0);
}

.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(2px);
  z-index: 99;
}

/* --- Sidebar Header --- */
.sidebar-header {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.logo-text {
  font-family: 'DM Sans', -apple-system, sans-serif;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #94a3b8;
  padding: 4px 6px;
  border-radius: 6px;
  line-height: 1;
  transition: all 150ms ease;
}
.close-btn:hover {
  background: #f1f5f9;
  color: #475569;
}

/* --- Menu --- */
.menu {
  padding: 10px 10px 16px;
  flex: 1;
  overflow-y: auto;
}

.menu-group {
  margin-bottom: 2px;
}

.group-title {
  padding: 14px 12px 8px;
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-family: 'DM Sans', -apple-system, sans-serif;
}

/* --- Menu Items --- */
.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  color: #475569;
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 500;
  border-radius: 6px;
  transition: 
    background-color 150ms cubic-bezier(0.16, 1, 0.3, 1),
    color 150ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 150ms ease;
  border-left: 2px solid transparent;
  line-height: 1.4;
}

.menu-item:hover {
  background: #f8fafc;
  color: #0f172a;
}

.menu-item.router-link-active {
  background: #ecfdf5;
  color: #059669;
  font-weight: 600;
  border-left-color: #059669;
}

.menu-item--primary {
  font-weight: 600;
  font-size: 13.5px;
}
.menu-item--primary.router-link-active {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
}

.menu-item--sub {
  padding-left: 28px;
  font-size: 13px;
  gap: 6px;
}

.menu-icon {
  font-size: 15px;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

/* ============================================
   Main Area
   ============================================ */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  background: #f8fafc;
}

/* ============================================
   Top Bar / Header
   ============================================ */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.topbar--desktop {
  height: 52px;
  padding: 0 24px;
  gap: 16px;
}

.topbar--mobile {
  height: 50px;
  padding: 0 12px;
}

.topbar-title {
  font-family: 'DM Sans', -apple-system, sans-serif;
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Breadcrumb (desktop) */
.topbar-breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.breadcrumb-item {
  color: #94a3b8;
  font-weight: 500;
}
.breadcrumb-current {
  color: #0f172a;
  font-weight: 600;
}
.breadcrumb-sep {
  color: #cbd5e1;
}

/* Hamburger button */
.hamburger {
  width: 34px;
  height: 34px;
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4.5px;
  padding: 8px;
  transition: all 150ms ease;
  flex-shrink: 0;
}
.hamburger:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}
.hamburger span {
  display: block;
  width: 16px;
  height: 1.5px;
  background: #475569;
  border-radius: 1px;
  transition: all 200ms cubic-bezier(0.16, 1, 0.3, 1);
}

/* ============================================
   Content Body
   ============================================ */
.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* ============================================
   Responsive
   ============================================ */
@media (max-width: 768px) {
  .content-body {
    padding: 16px;
  }
}

/* Scrollbar for sidebar */
.menu::-webkit-scrollbar { width: 4px; }
.menu::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 2px; }
.menu::-webkit-scrollbar-thumb:hover { background: #cbd5e1; }

/* Content scrollbar */
.content-body::-webkit-scrollbar { width: 5px; }
.content-body::-webkit-scrollbar-track { background: transparent; }
.content-body::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
</style>
