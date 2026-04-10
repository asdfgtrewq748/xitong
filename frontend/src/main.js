// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores'

// 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入 Tailwind CSS
import './assets/tailwind.css'

// 引入全局样式（Design System）
import './assets/styles/global.css'

// Load fonts before mounting
const fontLink = document.createElement('link')
fontLink.href = 'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap'
fontLink.rel = 'stylesheet'
document.head.appendChild(fontLink)

// 性能优化初始化
import { initPerformanceOptimization } from './utils/performance'

const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(ElementPlus)

// 初始化性能优化配置
initPerformanceOptimization().then(() => {
  console.log('[App] 性能优化已初始化')
  app.mount('#app')
}).catch(err => {
  console.error('[App] 性能优化初始化失败:', err)
  // 即使失败也正常挂载
  app.mount('#app')
})
