/**
 * 3D地质建模LOD(Level of Detail)管理器
 * 提供：视距自适应分辨率、数据降采样、渐进式渲染、性能监控
 */

/**
 * LOD级别配置
 * 根据视距选择合适的网格分辨率
 */
export const LODLevels = {
  // 远距离：使用最低分辨率，快速预览
  LOW: {
    name: '低精度',
    distance: 250,      // 视距 > 250
    resolution: 30,     // 网格分辨率
    surfaceDetail: 1,   // 曲面细节
    skipSides: true,    // 跳过侧面渲染
    wireframeOnly: false
  },
  // 中等距离：平衡性能和质量
  MEDIUM: {
    name: '中精度',
    distance: 180,      // 视距 180-250
    resolution: 60,
    surfaceDetail: 2,
    skipSides: false,
    wireframeOnly: false
  },
  // 标准距离：正常渲染
  HIGH: {
    name: '高精度',
    distance: 120,      // 视距 120-180
    resolution: 100,
    surfaceDetail: 3,
    skipSides: false,
    wireframeOnly: false
  },
  // 近距离：最高细节
  ULTRA: {
    name: '超高精度',
    distance: 0,        // 视距 < 120
    resolution: 150,
    surfaceDetail: 4,
    skipSides: false,
    wireframeOnly: false
  }
}

/**
 * 根据视距获取LOD级别
 * @param {number} distance - 当前视距
 * @returns {Object} LOD配置
 */
export function getLODLevel(distance) {
  if (distance > LODLevels.LOW.distance) return LODLevels.LOW
  if (distance > LODLevels.MEDIUM.distance) return LODLevels.MEDIUM
  if (distance > LODLevels.HIGH.distance) return LODLevels.HIGH
  return LODLevels.ULTRA
}

/**
 * 数据降采样器
 * 根据目标分辨率对网格数据进行降采样
 */
export class DataDownsampler {
  /**
   * 降采样2D网格数据
   * @param {Array} gridX - X轴网格坐标
   * @param {Array} gridY - Y轴网格坐标
   * @param {Array} surfaceZ - Z值矩阵 [yLen][xLen]
   * @param {number} targetResolution - 目标分辨率
   * @returns {Object} 降采样后的数据
   */
  static downsample(gridX, gridY, surfaceZ, targetResolution) {
    const xLen = gridX.length
    const yLen = gridY.length
    
    // 计算降采样步长
    const xStep = Math.max(1, Math.ceil(xLen / targetResolution))
    const yStep = Math.max(1, Math.ceil(yLen / targetResolution))
    
    // 如果不需要降采样，直接返回
    if (xStep === 1 && yStep === 1) {
      return { gridX, gridY, surfaceZ, downsampled: false }
    }
    
    // 降采样X轴
    const newGridX = []
    for (let j = 0; j < xLen; j += xStep) {
      newGridX.push(gridX[j])
    }
    // 确保包含最后一个点
    if (newGridX[newGridX.length - 1] !== gridX[xLen - 1]) {
      newGridX.push(gridX[xLen - 1])
    }
    
    // 降采样Y轴
    const newGridY = []
    for (let i = 0; i < yLen; i += yStep) {
      newGridY.push(gridY[i])
    }
    if (newGridY[newGridY.length - 1] !== gridY[yLen - 1]) {
      newGridY.push(gridY[yLen - 1])
    }
    
    // 降采样Z矩阵
    const newSurfaceZ = []
    for (let i = 0; i < yLen; i += yStep) {
      const row = []
      for (let j = 0; j < xLen; j += xStep) {
        row.push(surfaceZ[i][j])
      }
      // 包含最后一列
      if (row.length < newGridX.length && surfaceZ[i]) {
        row.push(surfaceZ[i][xLen - 1])
      }
      newSurfaceZ.push(row)
    }
    // 包含最后一行
    if (newSurfaceZ.length < newGridY.length && surfaceZ[yLen - 1]) {
      const lastRow = []
      for (let j = 0; j < xLen; j += xStep) {
        lastRow.push(surfaceZ[yLen - 1][j])
      }
      if (lastRow.length < newGridX.length) {
        lastRow.push(surfaceZ[yLen - 1][xLen - 1])
      }
      newSurfaceZ.push(lastRow)
    }
    
    return {
      gridX: newGridX,
      gridY: newGridY,
      surfaceZ: newSurfaceZ,
      downsampled: true,
      originalSize: { x: xLen, y: yLen },
      newSize: { x: newGridX.length, y: newGridY.length },
      compressionRatio: ((xLen * yLen) / (newGridX.length * newGridY.length)).toFixed(2)
    }
  }
  
  /**
   * 批量降采样多个模型
   * @param {Array} models - 模型数组
   * @param {number} targetResolution - 目标分辨率
   * @returns {Array} 降采样后的模型数组
   */
  static downsampleModels(models, targetResolution) {
    return models.map(model => {
      const topResult = this.downsample(
        model.grid_x, 
        model.grid_y, 
        model.top_surface_z, 
        targetResolution
      )
      
      const bottomResult = this.downsample(
        model.grid_x, 
        model.grid_y, 
        model.bottom_surface_z, 
        targetResolution
      )
      
      return {
        ...model,
        grid_x: topResult.gridX,
        grid_y: topResult.gridY,
        top_surface_z: topResult.surfaceZ,
        bottom_surface_z: bottomResult.surfaceZ,
        _lod: {
          downsampled: topResult.downsampled,
          originalSize: topResult.originalSize,
          newSize: topResult.newSize,
          compressionRatio: topResult.compressionRatio
        }
      }
    })
  }
}

/**
 * 渐进式渲染管理器
 * 先渲染低分辨率版本，逐步提升细节
 */
export class ProgressiveRenderer {
  constructor(chartInstance, options = {}) {
    this.chart = chartInstance
    this.options = {
      stages: [30, 60, 100, 150], // 渐进阶段的分辨率
      stageDelay: 300,            // 每阶段延迟(ms)
      enableAnimation: true,
      onStageComplete: null,
      ...options
    }
    this.currentStage = 0
    this.isRendering = false
    this.renderQueue = []
    this.aborted = false
  }
  
  /**
   * 开始渐进式渲染
   * @param {Array} originalModels - 原始模型数据
   * @param {Function} renderFn - 渲染函数 (models, resolution) => option
   */
  async startProgressive(originalModels, renderFn) {
    this.aborted = false
    this.isRendering = true
    this.currentStage = 0
    
    for (const resolution of this.options.stages) {
      if (this.aborted) break
      
      // 降采样数据
      const downsampledModels = DataDownsampler.downsampleModels(originalModels, resolution)
      
      // 生成option并渲染
      const option = renderFn(downsampledModels, resolution)
      
      if (this.chart && !this.aborted) {
        this.chart.setOption(option, { 
          notMerge: true, 
          lazyUpdate: this.currentStage < this.options.stages.length - 1 
        })
      }
      
      // 回调
      if (this.options.onStageComplete) {
        this.options.onStageComplete({
          stage: this.currentStage,
          resolution,
          totalStages: this.options.stages.length
        })
      }
      
      this.currentStage++
      
      // 等待下一阶段
      if (this.currentStage < this.options.stages.length && !this.aborted) {
        await this.delay(this.options.stageDelay)
      }
    }
    
    this.isRendering = false
  }
  
  /**
   * 中止渲染
   */
  abort() {
    this.aborted = true
    this.isRendering = false
  }
  
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

/**
 * 性能监控器
 * 监控FPS、渲染时间、内存使用
 */
export class PerformanceMonitor {
  constructor() {
    this.fps = 0
    this.frameCount = 0
    this.lastTime = performance.now()
    this.renderTimes = []
    this.isMonitoring = false
    this.animationId = null
  }
  
  /**
   * 开始监控
   * @param {Function} onUpdate - FPS更新回调
   */
  start(onUpdate) {
    this.isMonitoring = true
    this.onUpdate = onUpdate
    this.lastTime = performance.now()
    this.frameCount = 0
    this.tick()
  }
  
  tick() {
    if (!this.isMonitoring) return
    
    this.frameCount++
    const currentTime = performance.now()
    const elapsed = currentTime - this.lastTime
    
    if (elapsed >= 1000) {
      this.fps = Math.round((this.frameCount * 1000) / elapsed)
      this.frameCount = 0
      this.lastTime = currentTime
      
      if (this.onUpdate) {
        this.onUpdate({
          fps: this.fps,
          avgRenderTime: this.getAverageRenderTime(),
          memoryUsage: this.getMemoryUsage()
        })
      }
    }
    
    this.animationId = requestAnimationFrame(() => this.tick())
  }
  
  /**
   * 停止监控
   */
  stop() {
    this.isMonitoring = false
    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
    }
  }
  
  /**
   * 记录渲染时间
   * @param {number} time - 渲染耗时(ms)
   */
  recordRenderTime(time) {
    this.renderTimes.push(time)
    if (this.renderTimes.length > 60) {
      this.renderTimes.shift()
    }
  }
  
  /**
   * 获取平均渲染时间
   */
  getAverageRenderTime() {
    if (this.renderTimes.length === 0) return 0
    return Math.round(this.renderTimes.reduce((a, b) => a + b, 0) / this.renderTimes.length)
  }
  
  /**
   * 获取内存使用情况
   */
  getMemoryUsage() {
    if (performance.memory) {
      return {
        usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1048576), // MB
        totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1048576)
      }
    }
    return null
  }
}

/**
 * LOD 3D管理器
 * 整合所有LOD功能的主类
 */
export class LOD3DManager {
  constructor(chartInstance, options = {}) {
    this.chart = chartInstance
    this.options = {
      enableLOD: true,
      enableProgressive: true,
      enablePerformanceMonitor: false,
      autoAdjustQuality: true,
      targetFPS: 30,
      ...options
    }
    
    this.currentLOD = LODLevels.HIGH
    this.originalModels = null
    this.performanceMonitor = new PerformanceMonitor()
    this.progressiveRenderer = null
    
    // 自动质量调整
    if (this.options.autoAdjustQuality) {
      this.setupAutoQualityAdjustment()
    }
  }
  
  /**
   * 设置图表实例
   */
  setChartInstance(chart) {
    this.chart = chart
    if (this.progressiveRenderer) {
      this.progressiveRenderer.chart = chart
    }
  }
  
  /**
   * 存储原始模型数据
   */
  setOriginalModels(models) {
    this.originalModels = models
  }
  
  /**
   * 根据视距更新LOD
   * @param {number} distance - 当前视距
   * @param {Function} renderFn - 渲染函数
   * @returns {boolean} 是否触发了重新渲染
   */
  updateLOD(distance, renderFn) {
    if (!this.options.enableLOD || !this.originalModels) return false
    
    const newLOD = getLODLevel(distance)
    
    if (newLOD.resolution !== this.currentLOD.resolution) {
      console.log(`[LOD] 视距 ${distance} → 切换到 ${newLOD.name} (分辨率: ${newLOD.resolution})`)
      this.currentLOD = newLOD
      
      // 降采样并重新渲染
      const downsampledModels = DataDownsampler.downsampleModels(
        this.originalModels, 
        newLOD.resolution
      )
      
      const option = renderFn(downsampledModels, newLOD)
      if (this.chart) {
        this.chart.setOption(option, { notMerge: true })
      }
      
      return true
    }
    
    return false
  }
  
  /**
   * 渐进式渲染
   * @param {Function} renderFn - 渲染函数
   */
  async renderProgressive(renderFn) {
    if (!this.options.enableProgressive || !this.originalModels) {
      // 直接渲染最终版本
      const option = renderFn(this.originalModels, this.currentLOD)
      if (this.chart) {
        this.chart.setOption(option, { notMerge: true })
      }
      return
    }
    
    // 中止之前的渲染
    if (this.progressiveRenderer) {
      this.progressiveRenderer.abort()
    }
    
    this.progressiveRenderer = new ProgressiveRenderer(this.chart, {
      stages: [30, 60, 100, this.currentLOD.resolution],
      stageDelay: 200,
      onStageComplete: ({ stage, resolution, totalStages }) => {
        console.log(`[Progressive] 阶段 ${stage + 1}/${totalStages} 完成 (分辨率: ${resolution})`)
      }
    })
    
    await this.progressiveRenderer.startProgressive(this.originalModels, renderFn)
  }
  
  /**
   * 设置自动质量调整
   */
  setupAutoQualityAdjustment() {
    if (!this.options.enablePerformanceMonitor) return
    
    this.performanceMonitor.start(({ fps }) => {
      if (fps < this.options.targetFPS * 0.7) {
        // FPS过低，降低质量
        this.reduceQuality()
      } else if (fps > this.options.targetFPS * 1.3 && this.currentLOD !== LODLevels.ULTRA) {
        // FPS充足，提升质量
        this.increaseQuality()
      }
    })
  }
  
  reduceQuality() {
    const levels = [LODLevels.ULTRA, LODLevels.HIGH, LODLevels.MEDIUM, LODLevels.LOW]
    const currentIndex = levels.findIndex(l => l.resolution === this.currentLOD.resolution)
    if (currentIndex < levels.length - 1) {
      this.currentLOD = levels[currentIndex + 1]
      console.log(`[AutoQuality] 降低质量到 ${this.currentLOD.name}`)
    }
  }
  
  increaseQuality() {
    const levels = [LODLevels.ULTRA, LODLevels.HIGH, LODLevels.MEDIUM, LODLevels.LOW]
    const currentIndex = levels.findIndex(l => l.resolution === this.currentLOD.resolution)
    if (currentIndex > 0) {
      this.currentLOD = levels[currentIndex - 1]
      console.log(`[AutoQuality] 提升质量到 ${this.currentLOD.name}`)
    }
  }
  
  /**
   * 获取当前状态
   */
  getStatus() {
    return {
      currentLOD: this.currentLOD,
      isRendering: this.progressiveRenderer?.isRendering || false,
      fps: this.performanceMonitor.fps,
      avgRenderTime: this.performanceMonitor.getAverageRenderTime()
    }
  }
  
  /**
   * 销毁
   */
  dispose() {
    if (this.progressiveRenderer) {
      this.progressiveRenderer.abort()
    }
    this.performanceMonitor.stop()
    this.chart = null
    this.originalModels = null
  }
}

/**
 * 快速创建LOD管理器的工厂函数
 */
export function createLOD3DManager(chartInstance, options = {}) {
  return new LOD3DManager(chartInstance, options)
}

export default {
  LODLevels,
  getLODLevel,
  DataDownsampler,
  ProgressiveRenderer,
  PerformanceMonitor,
  LOD3DManager,
  createLOD3DManager
}
