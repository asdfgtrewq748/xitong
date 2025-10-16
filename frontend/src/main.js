// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 全局加载 ECharts GL 扩展，避免在组件内重复注册
import 'echarts-gl'

const app = createApp(App)

app.use(router)
app.use(ElementPlus) // 全局注册 Element Plus

app.mount('#app')