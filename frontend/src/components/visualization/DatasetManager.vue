<template>
  <el-drawer
    v-model="drawerVisible"
    title="数据集管理"
    direction="rtl"
    size="500px"
  >
    <div class="dataset-manager">
      <p>数据集管理功能正在开发中...</p>
    </div>
  </el-drawer>
</template>

<script setup>
/* eslint-disable no-undef */
import { computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  datasets: Object
})

const emit = defineEmits(['update:modelValue', 'select', 'delete'])

const drawerVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>

<style scoped>
.dataset-manager {
  padding: 16px;
}
</style>