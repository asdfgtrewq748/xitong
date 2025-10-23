<template>
  <div class="app-container">
    <el-container style="height: 100vh;">
      <el-aside width="260px" class="sidebar">
        <div class="logo-container">
          <div class="logo-wrapper">
            <div class="logo-icon">⛏️</div>
          </div>
          <h1 class="system-title">矿山工程分析系统</h1>
          <div class="system-version">v3.0.3</div>
        </div>

        <el-menu
          :default-active="$route.path"
          router
          class="main-menu"
          :collapse="isCollapsed"
          :background-color="menuBgColor"
          :text-color="menuTextColor"
          :active-text-color="menuActiveTextColor"
        >
          <div class="menu-section">
            <div class="menu-section-title">
              <el-icon><Menu /></el-icon>
              <span>主要功能</span>
            </div>

            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <template #title>工作台</template>
            </el-menu-item>

            <el-sub-menu index="/data">
              <template #title>
                <el-icon><DataLine /></el-icon>
                <span>数据与参数</span>
              </template>
              <el-menu-item index="/database-viewer">
                <el-icon><Document /></el-icon>
                <template #title>数据库管理</template>
              </el-menu-item>
              <el-menu-item index="/csv-formatter">
                <el-icon><Operation /></el-icon>
                <template #title>CSV 格式化</template>
              </el-menu-item>
              <el-menu-item index="/data-management">
                <el-icon><Grid /></el-icon>
                <template #title>数据管理中心</template>
              </el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="/analysis">
              <template #title>
                <el-icon><Calculator /></el-icon>
                <span>分析计算</span>
              </template>
              <el-menu-item index="/key-stratum">
                <el-icon><TrendCharts /></el-icon>
                <template #title>关键层计算</template>
              </el-menu-item>
              <el-menu-item index="/borehole-analysis">
                <el-icon><Location /></el-icon>
                <template #title>钻孔数据分析</template>
              </el-menu-item>
              <el-menu-item index="/upward-mining-feasibility">
                <el-icon><Location /></el-icon>
                <template #title>上行开采可行性</template>
              </el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="/modeling">
              <template #title>
                <el-icon><Histogram /></el-icon>
                <span>地质与建模</span>
              </template>
              <el-menu-item index="/geological-modeling">
                <el-icon><Box /></el-icon>
                <template #title>三维地质建模</template>
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
              <el-button type="text" class="action-btn">
                <el-icon><Bell /></el-icon>
                <span class="badge">3</span>
              </el-button>
              <el-button type="text" class="action-btn">
                <el-icon><Setting /></el-icon>
              </el-button>
              <el-button type="text" class="action-btn">
                <el-icon><Help /></el-icon>
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
import { computed, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import {
  House, DataLine, Document, Operation, Grid,
  TrendCharts, Location,
  Histogram, Box, Bell, Setting, Help, Expand, Fold, Sunny, Moon
} from '@element-plus/icons-vue';

const route = useRoute();
const currentRouteName = computed(() => route.meta.title || '工作台');

// 响应式数据
const isCollapsed = ref(false);
const menuBgColor = ref('#001529');
const menuTextColor = ref('#fff');
const menuActiveTextColor = ref('#1890ff');
const isDarkMode = ref(true);

// 方法
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  applyTheme();
  saveThemePreference();
};

const applyTheme = () => {
  const root = document.documentElement;
  if (isDarkMode.value) {
    // 深色主题
    root.style.setProperty('--bg-primary', '#1a1a2e');
    root.style.setProperty('--bg-secondary', '#16213e');
    root.style.setProperty('--sidebar-bg', '#1e293b');
    root.style.setProperty('--sidebar-bg-dark', '#0f172a');
    root.style.setProperty('--header-bg', '#334155');
    root.style.setProperty('--header-bg-dark', '#475569');
    root.style.setProperty('--text-primary', '#ffffff');
    root.style.setProperty('--text-secondary', '#cbd5e1');
    root.style.setProperty('--menu-bg', '#001529');
    root.style.setProperty('--menu-text', '#ffffff');
    root.style.setProperty('--menu-active-text', '#1890ff');
  } else {
    // 浅色主题
    root.style.setProperty('--bg-primary', '#f8fafc');
    root.style.setProperty('--bg-secondary', '#e2e8f0');
    root.style.setProperty('--sidebar-bg', '#f1f5f9');
    root.style.setProperty('--sidebar-bg-dark', '#e2e8f0');
    root.style.setProperty('--header-bg', '#ffffff');
    root.style.setProperty('--header-bg-dark', '#f8fafc');
    root.style.setProperty('--text-primary', '#1e293b');
    root.style.setProperty('--text-secondary', '#475569');
    root.style.setProperty('--menu-bg', '#ffffff');
    root.style.setProperty('--menu-text', '#374151');
    root.style.setProperty('--menu-active-text', '#3b82f6');
  }
};

const saveThemePreference = () => {
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light');
};

const loadThemePreference = () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark';
  } else {
    // 默认深色主题
    isDarkMode.value = true;
  }
  applyTheme();
};

onMounted(() => {
  loadThemePreference();
});
</script>

<style>
/* 全局样式 */
:root {
  --bg-primary: var(--bg-primary, #1a1a2e);
  --bg-secondary: var(--bg-secondary, #16213e);
  --sidebar-bg: var(--sidebar-bg, #1e293b);
  --sidebar-bg-dark: var(--sidebar-bg-dark, #0f172a);
  --header-bg: var(--header-bg, #334155);
  --header-bg-dark: var(--header-bg-dark, #475569);
  --text-primary: var(--text-primary, #ffffff);
  --text-secondary: var(--text-secondary, #cbd5e1);
  --menu-bg: var(--menu-bg, #001529);
  --menu-text: var(--menu-text, #ffffff);
  --menu-active-text: var(--menu-active-text, #1890ff);
}

body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  overflow: hidden;
}

.app-container {
  height: 100vh;
  background: var(--bg-primary);
  position: relative;
}

/* 侧边栏样式 */
.sidebar {
  background: linear-gradient(180deg, var(--sidebar-bg) 0%, var(--sidebar-bg-dark) 100%);
  box-shadow: 2px 0 20px rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
  border-right: 1px solid rgba(255,255,255,0.1);
}

.logo-container {
  padding: 30px 20px;
  text-align: center;
  border-bottom: 1px solid rgba(0,0,0,0.08);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.logo-wrapper {
  display: inline-block;
  margin-bottom: 15px;
}

.logo-icon {
  font-size: 48px;
  color: white;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.system-title {
  color: #ffffff;
  font-size: 20px;
  font-weight: bold;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.system-version {
  color: rgba(255,255,255,0.85);
  font-size: 12px;
  margin-top: 5px;
  font-weight: 500;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  margin: 20px 10px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 12px;
  font-size: 18px;
}

.user-details {
  flex: 1;
}

.user-name {
  color: #1e293b;
  font-weight: 600;
  margin-bottom: 2px;
}

.user-role {
  color: #64748b;
  font-size: 12px;
}

/* 主菜单样式 */
.main-menu {
  flex: 1;
  border: none !important;
  overflow-y: auto;
}

.menu-section {
  padding: 10px 0;
}

.menu-section-title {
  padding: 0 20px 10px;
  display: flex;
  align-items: center;
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.menu-section-title .el-icon {
  margin-right: 8px;
}

/* Element Plus 菜单样式覆盖 */
.el-menu {
  border: none !important;
}

.el-menu-item, .el-sub-menu__title {
  color: #475569 !important;
  border: none !important;
  margin: 0 10px;
  border-radius: 8px !important;
  height: 50px;
  line-height: 50px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.el-menu-item:hover, .el-sub-menu__title:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%) !important;
  color: #334155 !important;
}

.el-menu-item.is-active {
  background: linear-gradient(45deg, #667eea, #764ba2) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.el-sub-menu.is-active > .el-sub-menu__title {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%) !important;
  color: #334155 !important;
}

.el-sub-menu .el-menu-item {
  background: #ffffff !important;
  margin: 2px 10px;
  border-radius: 6px !important;
  height: 40px;
  line-height: 40px;
  font-size: 14px;
  border: 1px solid rgba(0,0,0,0.04);
}

.el-sub-menu .el-menu-item:hover {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
  color: #334155 !important;
}

.el-sub-menu .el-menu-item.is-active {
  background: linear-gradient(45deg, #667eea, #764ba2) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 主区域样式 */
.el-container {
  background: var(--bg-secondary);
}

.main-header {
  background: linear-gradient(135deg, var(--header-bg) 0%, var(--header-bg-dark) 100%);
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  color: var(--text-secondary);
  font-size: 18px;
  margin-right: 15px;
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 6px;
  padding: 8px;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  background: rgba(255,255,255,0.2);
  color: var(--menu-active-text);
}

.main-header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--text-primary);
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.action-btn {
  color: var(--text-secondary);
  font-size: 18px;
  position: relative;
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255,255,255,0.2);
  color: var(--menu-active-text);
}

.badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: #f56c6c;
  color: white;
  font-size: 10px;
  font-weight: bold;
  border-radius: 10px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-content {
  padding: 30px;
  background: transparent;
  overflow-y: auto;
  min-height: calc(100vh - 70px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px !important;
  }

  .system-title {
    font-size: 16px;
  }

  .logo-icon {
    font-size: 36px;
  }

  .main-header {
    padding: 0 15px;
  }

  .main-header h2 {
    font-size: 20px;
  }

  .header-actions {
    gap: 10px;
  }

  .action-btn {
    font-size: 16px;
    width: 35px;
    height: 35px;
  }

  .main-content {
    padding: 20px;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.6);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.8);
}

/* 菜单样式更新 */
.main-menu {
  flex: 1;
  border: none !important;
  overflow-y: auto;
  background: var(--menu-bg) !important;
}

.el-menu {
  border: none !important;
  background: var(--menu-bg) !important;
}

.el-menu-item, .el-sub-menu__title {
  color: var(--menu-text) !important;
  border: none !important;
  margin: 0 10px;
  border-radius: 8px !important;
  height: 50px;
  line-height: 50px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.el-menu-item:hover, .el-sub-menu__title:hover {
  background: rgba(255,255,255,0.1) !important;
  color: var(--menu-active-text) !important;
}

.el-menu-item.is-active {
  background: linear-gradient(45deg, #667eea, #764ba2) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.el-sub-menu.is-active > .el-sub-menu__title {
  background: rgba(255,255,255,0.1) !important;
  color: var(--menu-active-text) !important;
}

.el-sub-menu .el-menu-item {
  background: rgba(255,255,255,0.05) !important;
  margin: 2px 10px;
  border-radius: 6px !important;
  height: 40px;
  line-height: 40px;
  font-size: 14px;
  border: 1px solid rgba(255,255,255,0.1);
}

.el-sub-menu .el-menu-item:hover {
  background: rgba(255,255,255,0.1) !important;
  color: var(--menu-active-text) !important;
}

.el-sub-menu .el-menu-item.is-active {
  background: linear-gradient(45deg, #667eea, #764ba2) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}
</style>