<template>
  <el-dialog
    v-model="dialogVisible"
    title="帮助中心"
    width="600px"
  >
    <div class="help-content">
      <h3>快速开始</h3>
      <ol>
        <li>点击"导入数据"上传CSV或JSON文件</li>
        <li>选择适合的图表类型</li>
        <li>配置X、Y轴字段和其他参数</li>
        <li>导出图表或分享链接</li>
      </ol>

      <h3>快捷键</h3>
      <ul>
        <li><kbd>Ctrl+O</kbd> - 导入数据</li>
        <li><kbd>Ctrl+S</kbd> - 导出图表</li>
        <li><kbd>Ctrl+A</kbd> - 智能配置</li>
        <li><kbd>Ctrl+R</kbd> - 重置视图</li>
        <li><kbd>F11</kbd> - 全屏模式</li>
      </ul>

      <h3>支持的图表类型</h3>
      <ul>
        <li>散点图 - 相关性分析</li>
        <li>折线图 - 趋势分析</li>
        <li>柱状图 - 数据对比</li>
        <li>箱线图 - 分布分析</li>
        <li>直方图 - 频数分布</li>
        <li>热力图 - 密度可视化</li>
        <li>三维曲面 - 立体数据展示</li>
      </ul>
    </div>
  </el-dialog>
</template>

<script setup>
/* eslint-disable no-undef */
import { computed } from 'vue'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>

<style scoped>
.help-content h3 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #303133;
}

.help-content ul, .help-content ol {
  margin: 10px 0;
  padding-left: 20px;
}

.help-content li {
  margin: 5px 0;
  color: #606266;
}

kbd {
  background: #f5f5f5;
  border: 1px solid #ccc;
  border-radius: 3px;
  padding: 2px 6px;
  font-family: monospace;
  font-size: 12px;
}
</style>