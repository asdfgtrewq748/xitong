<template>
  <div class="app-container">
    <el-container style="height: 100vh;">
      <el-aside width="240px" class="sidebar">
        <div class="logo-container">
          <img src="@/assets/logo.png" alt="Logo" class="logo-img"/>
          <h1 class="system-title">矿山工程分析系统</h1>
        </div>
        <el-menu :default-active="$route.path" router class="main-menu">
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>工作台</span>
          </el-menu-item>
          <el-sub-menu index="/data">
            <template #title>
              <el-icon><Coin /></el-icon>
              <span>数据与参数</span>
            </template>
            <el-menu-item index="/database-viewer">数据库管理</el-menu-item>
            <el-menu-item index="/csv-formatter">CSV 格式化</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/analysis">
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>分析计算</span>
            </template>
            <el-menu-item index="/key-stratum">关键层计算</el-menu-item>
            <el-menu-item index="/borehole-analysis">钻孔数据分析</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="/modeling">
             <template #title>
              <el-icon><Picture /></el-icon>
              <span>地质与建模</span>
            </template>
            <el-menu-item index="/geological-modeling">三维地质建模</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="main-header">
          <h2>{{ currentRouteName }}</h2>
        </el-header>
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { House, Coin, DataAnalysis, Picture } from '@element-plus/icons-vue';

const route = useRoute();
const currentRouteName = computed(() => route.meta.title || '工作台');
</script>

<style>
/* 全局样式和布局 */
body { margin: 0; font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }
.app-container { height: 100vh; background-color: #f0f2f5; }

/* 侧边栏 */
.sidebar { background-color: #ffffff; border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; }
.logo-container { padding: 20px; text-align: center; border-bottom: 1px solid #e0e0e0; }
.logo-img { width: 40px; height: 40px; vertical-align: middle; }
.system-title { font-size: 18px; color: #1e3a8a; margin: 0; margin-left: 10px; display: inline-block; vertical-align: middle; }
.main-menu { flex-grow: 1; border-right: none !important; }

/* 主区域 */
.main-header {
  background-color: #ffffff;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #e0e0e0;
}
.main-header h2 { margin: 0; font-size: 20px; color: #303133; }
.main-content { padding: 20px; }

/* Element Plus 菜单样式覆盖 */
.el-menu-item, .el-sub-menu__title { color: #303133; }
.el-menu-item.is-active { color: #409EFF; background-color: #ecf5ff; }
</style>