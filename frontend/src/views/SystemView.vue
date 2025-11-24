<template>
  <div class="app-container bg-aurora">
    <el-container style="height: 100%; background: transparent;">
      <el-aside width="260px" class="sidebar">
        <!-- Logo removed as per request -->

        <el-menu
          :default-active="$route.path"
          router
          class="main-menu"
          :collapse="isCollapsed"
          background-color="transparent"
          text-color="#475569"
          active-text-color="#fff"
        >
          <div class="menu-section">
            <div class="menu-section-title">
              <el-icon><Menu /></el-icon>
              <span>主要功能</span>
            </div>

            <el-menu-item index="/tools">
              <el-icon><House /></el-icon>
              <template #title>工作台</template>
            </el-menu-item>

            <el-sub-menu index="/tools/data">
              <template #title>
                <el-icon><DataLine /></el-icon>
                <span>数据与参数</span>
              </template>
              <el-menu-item index="/tools/database-viewer">
                <el-icon><Document /></el-icon>
                <template #title>数据库管理</template>
              </el-menu-item>
              <el-menu-item index="/tools/csv-formatter">
                <el-icon><Operation /></el-icon>
                <template #title>CSV 格式化</template>
              </el-menu-item>
              <el-menu-item index="/tools/data-management">
                <el-icon><Grid /></el-icon>
                <template #title>数据管理中心</template>
              </el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="/tools/analysis">
              <template #title>
                <el-icon><Odometer /></el-icon>
                <span>分析计算</span>
              </template>
              <el-menu-item index="/tools/key-stratum">
                <el-icon><TrendCharts /></el-icon>
                <template #title>关键层计算</template>
              </el-menu-item>
              <el-menu-item index="/tools/tunnel-support">
                <el-icon><Odometer /></el-icon>
                <template #title>巷道支护计算</template>
              </el-menu-item>
              <el-menu-item index="/tools/borehole-analysis">
                <el-icon><Location /></el-icon>
                <template #title>钻孔数据分析</template>
              </el-menu-item>
              <el-menu-item index="/tools/upward-mining-feasibility">
                <el-icon><Location /></el-icon>
                <template #title>上行开采可行性</template>
              </el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="/tools/design">
              <template #title>
                <el-icon><Edit /></el-icon>
                <span>工程设计</span>
              </template>
              <el-menu-item index="/tools/mining-design">
                <el-icon><Edit /></el-icon>
                <template #title>采掘设计功能</template>
              </el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="/tools/modeling">
              <template #title>
                <el-icon><Histogram /></el-icon>
                <span>地质与建模</span>
              </template>
              <el-menu-item index="/tools/geological-modeling">
                <el-icon><Box /></el-icon>
                <template #title>三维地质建模</template>
              </el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="/tools/visualization">
              <template #title>
                <el-icon><TrendCharts /></el-icon>
                <span>科研绘图</span>
              </template>
              <el-menu-item index="/tools/visualization/scatter">
                <el-icon><TrendCharts /></el-icon>
                <template #title>散点图</template>
              </el-menu-item>
              <el-menu-item index="/tools/visualization/line">
                <el-icon><DataLine /></el-icon>
                <template #title>折线图</template>
              </el-menu-item>
              <el-menu-item index="/tools/visualization/bar">
                <el-icon><Histogram /></el-icon>
                <template #title>柱状图</template>
              </el-menu-item>
              <el-menu-item index="/tools/visualization/heatmap">
                <el-icon><Grid /></el-icon>
                <template #title>热力图</template>
              </el-menu-item>
              <el-menu-item index="/tools/visualization/surface">
                <el-icon><Box /></el-icon>
                <template #title>3D曲面图</template>
              </el-menu-item>
              <el-menu-item index="/tools/visualization/box">
                <el-icon><Box /></el-icon>
                <template #title>箱线图</template>
              </el-menu-item>
              <el-menu-item index="/tools/visualization/histogram">
                <el-icon><Histogram /></el-icon>
                <template #title>直方图</template>
              </el-menu-item>
              <el-menu-item index="/tools/visualization/statistics">
                <el-icon><DataAnalysis /></el-icon>
                <template #title>统计分析</template>
              </el-menu-item>
            </el-sub-menu>
          </div>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="main-header">
          <div class="header-left">
            <el-button
              type="text"
              @click="toggleSidebar"
              class="collapse-btn"
            >
              <el-icon><Expand v-if="isCollapsed" /><Fold v-else /></el-icon>
            </el-button>
            <h2>{{ currentRouteName }}</h2>
          </div>

          <div class="header-right">
            <div class="header-actions">
              <el-button type="text" class="action-btn" @click="toggleTheme" :title="isDarkMode ? '切换到浅色模式' : '切换到深色模式'">
                <el-icon><Sunny v-if="isDarkMode" /><Moon v-else /></el-icon>
              </el-button>
            </div>
          </div>
        </el-header>

        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import {
  House, DataLine, Document, Operation, Grid,
  TrendCharts, Location, Menu, Odometer,
  Histogram, Box, Expand, Fold, Sunny, Moon, Edit
} from '@element-plus/icons-vue';

const route = useRoute();
const currentRouteName = computed(() => route.meta.title || '工作台');

// 响应式数据
const isCollapsed = ref(false);
const isDarkMode = ref(false); // Default to light mode for Helios

// 方法
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  // Theme logic can be expanded later if dark mode is needed for Helios
};
</script>

<style scoped>
/* Helios Style Overrides */
.app-container {
  height: calc(100vh - 80px);
  position: relative;
}

/* Sidebar Glassmorphism */
.sidebar {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(16px);
  border-right: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 2px 0 20px rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
}

/* Menu Styles */
.main-menu {
  flex: 1;
  border: none !important;
  overflow-y: auto;
  background: transparent !important;
}

.menu-section {
  padding: 10px 0;
}

.menu-section-title {
  padding: 0 20px 10px;
  display: flex;
  align-items: center;
  color: #94a3b8;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.menu-section-title .el-icon {
  margin-right: 8px;
}

/* Element Plus Menu Overrides */
:deep(.el-menu) {
  background: transparent !important;
  border: none !important;
}

:deep(.el-menu-item), :deep(.el-sub-menu__title) {
  color: #475569 !important;
  margin: 4px 12px;
  border-radius: 12px !important;
  height: 46px;
  line-height: 46px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
}

:deep(.el-menu-item:hover), :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.6) !important;
  color: #7c3aed !important; /* Violet-600 */
  border-color: rgba(139, 92, 246, 0.2);
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%) !important;
  color: #fff !important;
  box-shadow: 0 8px 20px -4px rgba(99, 102, 241, 0.3);
  border: none;
}

:deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: #7c3aed !important;
  font-weight: 700;
}

/* Header Styles */
.main-header {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.6);
  height: 70px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  color: #64748b;
  font-size: 18px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  padding: 8px;
  transition: all 0.3s ease;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  background: white;
  color: #7c3aed;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transform: translateY(-1px);
}

.main-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1e293b;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.action-btn {
  color: #64748b;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: white;
  color: #f59e0b; /* Amber for sun */
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transform: translateY(-1px);
}

.main-content {
  padding: 30px;
  background: transparent;
  overflow-y: auto;
  min-height: calc(100vh - 150px);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.5);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.6);
}
</style>