<template>
  <div v-if="visible" class="guide-overlay" :style="{ zIndex: baseZIndex }">
    <!-- 高亮遮罩 -->
    <div class="guide-mask" @click="handleSkip">
      <!-- 高亮区域镂空 -->
      <svg class="highlight-svg">
        <defs>
          <mask id="highlight-mask">
            <rect x="0" y="0" width="100%" height="100%" fill="white"/>
            <rect
              v-if="currentStepData"
              :x="highlightRect.x"
              :y="highlightRect.y"
              :width="highlightRect.width"
              :height="highlightRect.height"
              :rx="highlightRect.radius"
              fill="black"
            />
          </mask>
        </defs>
        <rect x="0" y="0" width="100%" height="100%" fill="rgba(0, 0, 0, 0.7)" mask="url(#highlight-mask)"/>
      </svg>
    </div>

    <!-- 提示卡片 -->
    <div
      v-if="currentStepData"
      class="guide-tooltip"
      :style="tooltipStyle"
      @click.stop
    >
      <!-- 步骤编号 -->
      <div class="guide-header">
        <div class="step-number">{{ currentStep + 1 }} / {{ steps.length }}</div>
        <button class="btn-close" @click="handleClose">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <line x1="6" y1="6" x2="18" y2="18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
        </button>
      </div>

      <!-- 标题 -->
      <h3 class="guide-title">{{ currentStepData.title }}</h3>

      <!-- 描述 -->
      <p class="guide-description">{{ currentStepData.description }}</p>

      <!-- 图片（可选） -->
      <img
        v-if="currentStepData.image"
        :src="currentStepData.image"
        :alt="currentStepData.title"
        class="guide-image"
      />

      <!-- 操作按钮 -->
      <div class="guide-actions">
        <button
          v-if="currentStep > 0"
          class="btn-prev"
          @click="handlePrev"
        >
          上一步
        </button>
        <button
          v-if="showSkip && currentStep < steps.length - 1"
          class="btn-skip"
          @click="handleSkip"
        >
          跳过引导
        </button>
        <button
          v-if="currentStep < steps.length - 1"
          class="btn-next"
          @click="handleNext"
        >
          下一步
        </button>
        <button
          v-else
          class="btn-finish"
          @click="handleFinish"
        >
          完成
        </button>
      </div>

      <!-- 进度点 -->
      <div class="guide-dots">
        <span
          v-for="(step, index) in steps"
          :key="index"
          class="dot"
          :class="{ active: index === currentStep }"
          @click="goToStep(index)"
        ></span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GuideOverlay',
  data() {
    return {
      visible: false,
      currentStep: 0,
      steps: [],
      showSkip: true,
      baseZIndex: 10000,
      onFinish: null,
      onSkip: null,
      highlightRect: {
        x: 0,
        y: 0,
        width: 0,
        height: 0,
        radius: 8
      },
      tooltipPosition: {
        top: 0,
        left: 0
      }
    }
  },
  computed: {
    currentStepData() {
      return this.steps[this.currentStep] || null
    },
    tooltipStyle() {
      return {
        top: this.tooltipPosition.top + 'px',
        left: this.tooltipPosition.left + 'px'
      }
    }
  },
  methods: {
    /**
     * 开始引导
     * @param {Object} options - 配置选项
     * @param {Array} options.steps - 引导步骤
     * @param {Boolean} options.showSkip - 是否显示跳过按钮
     * @param {Number} options.baseZIndex - 基础层级
     * @param {Function} options.onFinish - 完成回调
     * @param {Function} options.onSkip - 跳过回调
     */
    start(options = {}) {
      this.steps = options.steps || []
      this.showSkip = options.showSkip !== false
      this.baseZIndex = options.baseZIndex || 10000
      this.onFinish = options.onFinish || null
      this.onSkip = options.onSkip || null
      this.currentStep = 0

      if (this.steps.length === 0) {
        console.warn('[GuideOverlay] 没有提供引导步骤')
        return
      }

      this.visible = true
      this.$nextTick(() => {
        this.updateHighlight()
      })
    },

    stop() {
      this.visible = false
      this.currentStep = 0
    },

    handleNext() {
      if (this.currentStep < this.steps.length - 1) {
        this.currentStep++
        this.$nextTick(() => {
          this.updateHighlight()
        })
      }
    },

    handlePrev() {
      if (this.currentStep > 0) {
        this.currentStep--
        this.$nextTick(() => {
          this.updateHighlight()
        })
      }
    },

    handleSkip() {
      if (this.onSkip) {
        this.onSkip(this.currentStep)
      }
      this.stop()
    },

    handleClose() {
      this.handleSkip()
    },

    handleFinish() {
      if (this.onFinish) {
        this.onFinish()
      }
      this.stop()
    },

    goToStep(index) {
      if (index >= 0 && index < this.steps.length) {
        this.currentStep = index
        this.$nextTick(() => {
          this.updateHighlight()
        })
      }
    },

    /**
     * 更新高亮区域和提示位置
     */
    updateHighlight() {
      const step = this.currentStepData
      if (!step) return

      let targetElement = null

      // 获取目标元素
      if (step.element) {
        if (typeof step.element === 'string') {
          targetElement = document.querySelector(step.element)
        } else if (step.element instanceof HTMLElement) {
          targetElement = step.element
        }
      }

      if (targetElement) {
        // 滚动到目标元素
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' })

        // 获取元素位置
        const rect = targetElement.getBoundingClientRect()
        const padding = step.padding || 8

        this.highlightRect = {
          x: rect.left - padding,
          y: rect.top - padding,
          width: rect.width + padding * 2,
          height: rect.height + padding * 2,
          radius: step.radius || 8
        }

        // 计算提示框位置
        this.calculateTooltipPosition(rect, step.position || 'bottom')
      } else {
        // 无目标元素时，居中显示
        this.highlightRect = { x: 0, y: 0, width: 0, height: 0, radius: 0 }
        this.tooltipPosition = {
          top: window.innerHeight / 2 - 150,
          left: window.innerWidth / 2 - 200
        }
      }
    },

    /**
     * 计算提示框位置
     */
    calculateTooltipPosition(targetRect, position) {
      const tooltipWidth = 400
      const tooltipHeight = 300
      const spacing = 20

      let top = 0
      let left = 0

      switch (position) {
        case 'top':
          top = targetRect.top - tooltipHeight - spacing
          left = targetRect.left + targetRect.width / 2 - tooltipWidth / 2
          break
        case 'bottom':
          top = targetRect.bottom + spacing
          left = targetRect.left + targetRect.width / 2 - tooltipWidth / 2
          break
        case 'left':
          top = targetRect.top + targetRect.height / 2 - tooltipHeight / 2
          left = targetRect.left - tooltipWidth - spacing
          break
        case 'right':
          top = targetRect.top + targetRect.height / 2 - tooltipHeight / 2
          left = targetRect.right + spacing
          break
        default:
          top = targetRect.bottom + spacing
          left = targetRect.left + targetRect.width / 2 - tooltipWidth / 2
      }

      // 边界检查
      if (left < 20) left = 20
      if (left + tooltipWidth > window.innerWidth - 20) {
        left = window.innerWidth - tooltipWidth - 20
      }
      if (top < 20) top = 20
      if (top + tooltipHeight > window.innerHeight - 20) {
        top = window.innerHeight - tooltipHeight - 20
      }

      this.tooltipPosition = { top, left }
    }
  },
  mounted() {
    // 监听窗口大小变化
    window.addEventListener('resize', this.updateHighlight)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.updateHighlight)
  }
}
</script>

<style scoped>
.guide-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: auto;
}

.guide-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.highlight-svg {
  width: 100%;
  height: 100%;
}

/* 提示卡片 */
.guide-tooltip {
  position: absolute;
  width: 400px;
  max-width: 90vw;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
  animation: fadeInUp 0.3s ease-out;
  pointer-events: auto;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 头部 */
.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.step-number {
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
  background: #e8f4fd;
  padding: 4px 12px;
  border-radius: 12px;
}

.btn-close {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #909399;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #f5f7fa;
  color: #606266;
}

.btn-close svg {
  width: 16px;
  height: 16px;
}

/* 标题和描述 */
.guide-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.guide-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin: 0 0 16px 0;
}

/* 图片 */
.guide-image {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 16px;
}

/* 操作按钮 */
.guide-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.guide-actions button {
  flex: 1;
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-prev {
  background: #f4f4f5;
  color: #606266;
}

.btn-prev:hover {
  background: #e9e9eb;
}

.btn-skip {
  background: transparent;
  color: #909399;
  border: 1px solid #dcdfe6;
}

.btn-skip:hover {
  color: #606266;
  border-color: #c0c4cc;
}

.btn-next,
.btn-finish {
  background: #409eff;
  color: white;
}

.btn-next:hover,
.btn-finish:hover {
  background: #66b1ff;
}

/* 进度点 */
.guide-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #dcdfe6;
  cursor: pointer;
  transition: all 0.3s;
}

.dot:hover {
  background: #c0c4cc;
}

.dot.active {
  width: 24px;
  border-radius: 4px;
  background: #409eff;
}

/* 响应式 */
@media (max-width: 768px) {
  .guide-tooltip {
    width: 90vw;
    padding: 20px;
  }

  .guide-actions {
    flex-wrap: wrap;
  }

  .btn-skip {
    order: 3;
    width: 100%;
  }
}
</style>
