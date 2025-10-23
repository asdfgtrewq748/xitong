// frontend/src/utils/performance.js
// 前端性能优化工具集

/**
 * 性能配置
 */
export const PerformanceConfig = {
  // 虚拟滚动配置
  virtualScroll: {
    enabled: true,
    itemHeight: 45,        // 表格行高
    bufferSize: 5,         // 缓冲区大小（上下额外渲染的行数）
    threshold: 50          // 超过这个数量启用虚拟滚动
  },

  // ECharts配置
  echarts: {
    lazyLoad: true,        // 延迟加载
    downSample: true,      // 数据降采样
    maxDataPoints: 5000,   // 最大数据点数
    animationDuration: 300 // 动画时长
  },

  // 3D建模配置
  modeling3D: {
    autoResolution: true,  // 自动分辨率
    lowEndDevice: false,   // 是否低端设备（自动检测）
    maxResolution: 150,    // 最大分辨率
    defaultResolution: 80, // 默认分辨率
    lowResolution: 50      // 低端设备分辨率
  },

  // 图片和资源
  assets: {
    lazyLoadImages: true,  // 图片懒加载
    webpSupport: false     // WebP支持（自动检测）
  }
}

/**
 * 检测设备性能
 */
export function detectDevicePerformance() {
  const canvas = document.createElement('canvas')
  const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')

  // 检查WebGL支持
  if (!gl) {
    PerformanceConfig.modeling3D.lowEndDevice = true
    return 'low'
  }

  // 检查GPU渲染器
  const debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
  if (debugInfo) {
    const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
    // 简单判断：包含Intel集成显卡的视为低端设备
    if (renderer.toLowerCase().includes('intel')) {
      PerformanceConfig.modeling3D.lowEndDevice = true
      return 'medium'
    }
  }

  // 检查内存
  if (navigator.deviceMemory && navigator.deviceMemory < 4) {
    PerformanceConfig.modeling3D.lowEndDevice = true
    return 'low'
  }

  return 'high'
}

/**
 * 获取推荐的3D分辨率
 */
export function getRecommended3DResolution() {
  const performance = detectDevicePerformance()

  if (performance === 'low') {
    return PerformanceConfig.modeling3D.lowResolution
  } else if (performance === 'medium') {
    return PerformanceConfig.modeling3D.defaultResolution
  } else {
    return PerformanceConfig.modeling3D.maxResolution
  }
}

/**
 * 数据降采样
 * @param {Array} data - 原始数据
 * @param {Number} maxPoints - 最大点数
 * @returns {Array} 采样后的数据
 */
export function downSampleData(data, maxPoints = 5000) {
  if (!data || data.length <= maxPoints) {
    return data
  }

  const step = Math.ceil(data.length / maxPoints)
  const sampled = []

  for (let i = 0; i < data.length; i += step) {
    sampled.push(data[i])
  }

  return sampled
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {Number} delay - 延迟时间(ms)
 * @returns {Function}
 */
export function debounce(func, delay = 300) {
  let timeoutId
  return function(...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => {
      func.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {Number} limit - 时间限制(ms)
 * @returns {Function}
 */
export function throttle(func, limit = 300) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 简单的内存缓存
 */
class SimpleCache {
  constructor(maxSize = 50) {
    this.cache = new Map()
    this.maxSize = maxSize
  }

  get(key) {
    return this.cache.get(key)
  }

  set(key, value) {
    if (this.cache.size >= this.maxSize) {
      // 删除最早的条目
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }
    this.cache.set(key, value)
  }

  has(key) {
    return this.cache.has(key)
  }

  clear() {
    this.cache.clear()
  }

  get size() {
    return this.cache.size
  }
}

export const dataCache = new SimpleCache(50)

/**
 * 缓存包装器
 * @param {Function} fn - 要缓存的函数
 * @param {Function} keyGenerator - 缓存键生成函数
 * @returns {Function}
 */
export function withCache(fn, keyGenerator = (...args) => JSON.stringify(args)) {
  return function(...args) {
    const key = keyGenerator(...args)

    if (dataCache.has(key)) {
      console.log('[缓存命中]', key)
      return dataCache.get(key)
    }

    const result = fn.apply(this, args)
    dataCache.set(key, result)
    return result
  }
}

/**
 * 异步任务队列（避免同时发起过多请求）
 */
class TaskQueue {
  constructor(concurrency = 3) {
    this.concurrency = concurrency
    this.running = 0
    this.queue = []
  }

  async add(task) {
    if (this.running >= this.concurrency) {
      await new Promise(resolve => this.queue.push(resolve))
    }

    this.running++
    try {
      return await task()
    } finally {
      this.running--
      const resolve = this.queue.shift()
      if (resolve) resolve()
    }
  }
}

export const requestQueue = new TaskQueue(3)

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 检查WebP支持
 */
export function checkWebPSupport() {
  return new Promise(resolve => {
    const img = new Image()
    img.onload = () => {
      PerformanceConfig.assets.webpSupport = img.width === 1
      resolve(PerformanceConfig.assets.webpSupport)
    }
    img.onerror = () => {
      PerformanceConfig.assets.webpSupport = false
      resolve(false)
    }
    img.src = 'data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAwA0JaQAA3AA/vuUAAA='
  })
}

/**
 * 性能监控
 */
export class PerformanceMonitor {
  constructor() {
    this.marks = new Map()
  }

  start(label) {
    this.marks.set(label, performance.now())
  }

  end(label) {
    const startTime = this.marks.get(label)
    if (!startTime) return 0

    const duration = performance.now() - startTime
    this.marks.delete(label)
    console.log(`[性能] ${label}: ${duration.toFixed(2)}ms`)
    return duration
  }

  measure(label, fn) {
    this.start(label)
    const result = fn()
    this.end(label)
    return result
  }

  async measureAsync(label, fn) {
    this.start(label)
    const result = await fn()
    this.end(label)
    return result
  }
}

export const performanceMonitor = new PerformanceMonitor()

/**
 * 初始化性能优化
 */
export async function initPerformanceOptimization() {
  console.log('[性能优化] 初始化...')

  // 检测设备性能
  const devicePerformance = detectDevicePerformance()
  console.log(`[性能优化] 设备性能等级: ${devicePerformance}`)

  // 检测WebP支持
  const webpSupport = await checkWebPSupport()
  console.log(`[性能优化] WebP支持: ${webpSupport}`)

  // 调整配置
  if (devicePerformance === 'low') {
    PerformanceConfig.echarts.maxDataPoints = 3000
    PerformanceConfig.virtualScroll.threshold = 30
  }

  console.log('[性能优化] 配置:', PerformanceConfig)

  return PerformanceConfig
}

export default {
  PerformanceConfig,
  detectDevicePerformance,
  getRecommended3DResolution,
  downSampleData,
  debounce,
  throttle,
  dataCache,
  withCache,
  requestQueue,
  formatFileSize,
  checkWebPSupport,
  performanceMonitor,
  initPerformanceOptimization
}
