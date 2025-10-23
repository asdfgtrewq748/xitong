<template>
  <div class="virtual-scroll-container" ref="containerRef" @scroll="handleScroll">
    <div class="virtual-scroll-placeholder" :style="{ height: totalHeight + 'px' }"></div>
    <div class="virtual-scroll-content" :style="{ transform: `translateY(${offsetY}px)` }">
      <slot :items="visibleItems" :startIndex="startIndex"></slot>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

export default {
  name: 'VirtualScroll',
  props: {
    items: {
      type: Array,
      required: true
    },
    itemHeight: {
      type: Number,
      default: 45
    },
    bufferSize: {
      type: Number,
      default: 5
    }
  },
  setup(props) {
    const containerRef = ref(null)
    const scrollTop = ref(0)
    const containerHeight = ref(0)

    // 计算总高度
    const totalHeight = computed(() => props.items.length * props.itemHeight)

    // 计算可见区域的起始索引
    const startIndex = computed(() => {
      const index = Math.floor(scrollTop.value / props.itemHeight)
      return Math.max(0, index - props.bufferSize)
    })

    // 计算可见区域的结束索引
    const endIndex = computed(() => {
      const index = Math.ceil((scrollTop.value + containerHeight.value) / props.itemHeight)
      return Math.min(props.items.length, index + props.bufferSize)
    })

    // 计算可见项
    const visibleItems = computed(() => {
      return props.items.slice(startIndex.value, endIndex.value)
    })

    // 计算偏移量
    const offsetY = computed(() => startIndex.value * props.itemHeight)

    // 处理滚动
    const handleScroll = (e) => {
      scrollTop.value = e.target.scrollTop
    }

    // 更新容器高度
    const updateContainerHeight = () => {
      if (containerRef.value) {
        containerHeight.value = containerRef.value.clientHeight
      }
    }

    // 窗口大小改变时更新
    const handleResize = () => {
      updateContainerHeight()
    }

    onMounted(() => {
      updateContainerHeight()
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    // 监听items变化，重置滚动位置
    watch(() => props.items, () => {
      if (containerRef.value) {
        containerRef.value.scrollTop = 0
        scrollTop.value = 0
      }
    })

    return {
      containerRef,
      totalHeight,
      visibleItems,
      startIndex,
      offsetY,
      handleScroll
    }
  }
}
</script>

<style scoped>
.virtual-scroll-container {
  height: 100%;
  overflow-y: auto;
  position: relative;
}

.virtual-scroll-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  pointer-events: none;
}

.virtual-scroll-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  will-change: transform;
}
</style>
