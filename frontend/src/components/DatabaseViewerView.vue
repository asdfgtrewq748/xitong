<template>
  <div class="page-container">
    <el-tabs v-model="activeTab" class="db-tabs">
      <el-tab-pane label="数据库概览" name="overview">
        <DatabaseOverview :active="activeTab === 'overview'" />
      </el-tab-pane>
      <el-tab-pane label="参数取值查询" name="lookup">
        <ParameterLookup :active="activeTab === 'lookup'" />
      </el-tab-pane>
      <el-tab-pane label="编辑数据库" name="editor">
        <DatabaseEditor
          :active="activeTab === 'editor'"
          :province="provinceFilter.code"
          :province-label="provinceFilter.label"
          @clear-province="clearProvinceFilter"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import DatabaseOverview from './database/DatabaseOverview.vue';
import ParameterLookup from './database/ParameterLookup.vue';
import DatabaseEditor from './database/DatabaseEditor.vue';

const activeTab = ref('overview');
const route = useRoute();
const router = useRouter();
const provinceFilter = ref({ code: '', label: '' });
const hasInitialized = ref(false);

watch(
  () => [route.query.tab, route.query.province, route.query.provinceLabel],
  ([tab, province, provinceLabel]) => {
    const provinceValue = typeof province === 'string' ? province : '';
    const labelValue = typeof provinceLabel === 'string' ? provinceLabel : '';
    provinceFilter.value = {
      code: provinceValue,
      label: labelValue || provinceValue,
    };

    if (!hasInitialized.value) {
      if (typeof tab === 'string') {
        activeTab.value = tab;
      } else if (provinceValue) {
        activeTab.value = 'editor';
      } else {
        activeTab.value = 'overview';
      }
      hasInitialized.value = true;
    } else {
      if (typeof tab === 'string') {
        if (tab !== activeTab.value) {
          activeTab.value = tab;
        }
      } else if (provinceValue && activeTab.value !== 'editor') {
        activeTab.value = 'editor';
      }
    }
  },
  { immediate: true }
);

watch(
  activeTab,
  (newTab, oldTab) => {
    if (newTab === oldTab) {
      return;
    }
    const nextQuery = { ...route.query };
    if (newTab === 'overview') {
      delete nextQuery.tab;
      if (provinceFilter.value.code) {
        provinceFilter.value = { code: '', label: '' };
      }
      delete nextQuery.province;
      delete nextQuery.provinceLabel;
    } else {
      nextQuery.tab = newTab;
    }
    router.replace({ path: route.path, query: nextQuery });
  }
);

const clearProvinceFilter = () => {
  provinceFilter.value = { code: '', label: '' };
  const nextQuery = { ...route.query };
  delete nextQuery.province;
  delete nextQuery.provinceLabel;
  router.replace({ path: route.path, query: nextQuery });
};
</script>

<style scoped>
.page-container {
  height: 100%;
  padding: 0 20px;
  box-sizing: border-box;
}
.db-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}
:deep(.el-tabs__content) {
  flex-grow: 1;
  overflow-y: auto;
}
:deep(.el-tab-pane) {
  height: 100%;
}
</style>