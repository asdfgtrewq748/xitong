<template>
  <div class="theme-selector">
    <el-radio-group v-model="selectedTheme" @change="handleThemeChange">
      <el-radio-button 
        v-for="theme in themes" 
        :key="theme.value" 
        :value="theme.value"
      >
        <el-icon :size="16" style="margin-right: 4px;">
          <component :is="theme.icon" />
        </el-icon>
        {{ theme.label }}
      </el-radio-button>
    </el-radio-group>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, onMounted } from 'vue'
import { Sunny, Moon, Monitor } from '@element-plus/icons-vue'

const emit = defineEmits(['change'])

const themes = [
  { value: 'light', label: '浅色', icon: Sunny },
  { value: 'dark', label: '深色', icon: Moon },
  { value: 'scientific', label: '科研', icon: Monitor }
]

const selectedTheme = ref('light')

onMounted(() => {
  // 从本地存储恢复主题
  const savedTheme = localStorage.getItem('visualization-theme')
  if (savedTheme && themes.some(t => t.value === savedTheme)) {
    selectedTheme.value = savedTheme
    applyTheme(savedTheme)
  }
})

function handleThemeChange(theme) {
  applyTheme(theme)
  localStorage.setItem('visualization-theme', theme)
  emit('change', theme)
}

function applyTheme(theme) {
  // 这里可以添加全局样式切换逻辑
  document.documentElement.setAttribute('data-theme', theme)
  
  // 通知ECharts组件重新渲染
  window.dispatchEvent(new CustomEvent('theme-change', { detail: theme }))
}
</script>

<style scoped>
.theme-selector {
  display: inline-flex;
  align-items: center;
}

:deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
}
</style>
