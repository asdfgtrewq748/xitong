<template>
  <div class="editor-container">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchText"
          :placeholder="searchPlaceholder"
          clearable
          size="small"
          class="toolbar-search"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #suffix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button size="small" @click="handleSearch" :loading="isLoading">搜索</el-button>
      </div>
      <div v-if="isProvinceFiltered" class="toolbar-filter">
        <el-tag type="info" closable @close="clearProvinceFilter">
          当前省份：{{ provinceDisplay }}
        </el-tag>
      </div>
      <div class="toolbar-right">
        <el-button size="small" @click="addRow">添加新行</el-button>
        <el-button size="small" type="danger" @click="deleteSelectedRows" :disabled="!selectedKeys.size">删除选中行</el-button>
        <el-button size="small" type="primary" @click="saveChanges" :loading="isSaving" :disabled="!hasPendingChanges">保存修改</el-button>
      </div>
    </div>
    <div class="table-wrapper" v-loading="isLoading">
      <el-auto-resizer>
        <template #default="{ height, width }">
          <div v-if="tableColumns.length" class="table-scroll" :style="{ height: `${height}px` }">
            <el-table-v2
              :columns="tableColumns"
              :data="tableData"
              :width="Math.max(width, minTableWidth)"
              :height="height"
              row-key="__key"
              class="virtual-table"
            />
          </div>
          <div v-else class="empty-hint">暂无数据，请检查数据源</div>
        </template>
      </el-auto-resizer>
    </div>
    <div class="pagination-bar">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next, jumper"
        :current-page="page"
        :page-sizes="[50, 100, 200, 500]"
        :page-size="pageSize"
        :total="total"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, h, onMounted, ref, watch } from 'vue';
import { ElCheckbox, ElInput, ElMessage, ElMessageBox } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { getApiBase } from '@/utils/api';

const API_BASE = getApiBase();

const props = defineProps({
  province: { type: String, default: '' },
  provinceLabel: { type: String, default: '' },
});

const emit = defineEmits(['clear-province']);

const columns = ref([]);
const tableData = ref([]);
const page = ref(1);
const pageSize = ref(100);
const total = ref(0);
const searchText = ref('');
const isLoading = ref(false);
const isSaving = ref(false);

const selectedKeys = ref(new Set());
const dirtyRows = ref(new Map());
const deletedRowIds = ref(new Set());
const tempIdCounter = ref(-1);

const fetchData = async () => {
  isLoading.value = true;
  try {
    const params = new URLSearchParams({
      page: String(page.value),
      page_size: String(pageSize.value),
    });
    if (searchText.value.trim()) {
      params.set('search', searchText.value.trim());
    }
    if (props.province) {
      params.set('province', props.province);
    }
    const res = await fetch(`${API_BASE}/database/records?${params.toString()}`).then((r) => r.json());
    if (res.status !== 'success') {
      const msg = res.detail || res.message || '加载数据库失败';
      ElMessage.error(msg);
      return;
    }
    columns.value = Array.isArray(res.columns) ? res.columns : [];
    total.value = Number(res.total) || 0;
    const normalized = Array.isArray(res.records)
      ? res.records.map((row, index) => {
          const record = {};
          columns.value.forEach((col) => {
            record[col] = row[col] ?? '';
          });
          record.__rowid__ = row.__rowid__;
          record.__key = row.__rowid__ != null ? String(row.__rowid__) : `row-${page.value}-${index}`;
          return record;
        })
      : [];
    tableData.value = normalized;
    selectedKeys.value = new Set();
    dirtyRows.value = new Map();
    deletedRowIds.value = new Set();
    tempIdCounter.value = -1;
  } catch (error) {
    console.error('加载数据库失败:', error);
    ElMessage.error('加载数据库失败，请稍后重试');
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchData();
});

watch(
  () => props.province,
  (newVal, oldVal) => {
    if (newVal === oldVal) {
      return;
    }
    page.value = 1;
    searchText.value = '';
    fetchData();
  }
);

const provinceDisplay = computed(() => props.provinceLabel || props.province || '');

const isProvinceFiltered = computed(() => Boolean(props.province));

const searchPlaceholder = computed(() => {
  if (!props.province && !props.provinceLabel) {
    return '输入关键字搜索';
  }
  const label = props.provinceLabel || props.province;
  return `在${label}内搜索`;
});

const clearProvinceFilter = () => {
  emit('clear-province');
};

const getRowKey = (row) => row.__key;

const toggleRow = (key, checked) => {
  const next = new Set(selectedKeys.value);
  if (checked) {
    next.add(key);
  } else {
    next.delete(key);
  }
  selectedKeys.value = next;
};

const toggleAll = (checked) => {
  if (!checked) {
    selectedKeys.value = new Set();
    return;
  }
  const next = new Set();
  tableData.value.forEach((row) => {
    next.add(getRowKey(row));
  });
  selectedKeys.value = next;
};

const markDirty = (row) => {
  if (row.__isNew) {
    row.__isDirty = true;
    return;
  }
  const snapshot = { __rowid__: row.__rowid__ };
  columns.value.forEach((col) => {
    snapshot[col] = row[col];
  });
  const map = new Map(dirtyRows.value);
  map.set(getRowKey(row), snapshot);
  dirtyRows.value = map;
};

const updateCell = (rowKey, column, value) => {
  const target = tableData.value.find((item) => getRowKey(item) === rowKey);
  if (!target) return;
  if (target[column] === value) return;
  target[column] = value;
  markDirty(target);
};

const tableColumns = computed(() => {
  if (!columns.value.length) {
    return [];
  }
  const selectionColumn = {
    key: '__select__',
    dataKey: '__key',
    width: 60,
    fixed: 'left',
    headerRenderer: () => {
      const totalRows = tableData.value.length;
      const selectedCount = selectedKeys.value.size;
      const allChecked = totalRows > 0 && selectedCount === totalRows;
      const indeterminate = selectedCount > 0 && selectedCount < totalRows;
      return h(ElCheckbox, {
        modelValue: allChecked,
        indeterminate,
        disabled: totalRows === 0,
        onChange: toggleAll,
      });
    },
    cellRenderer: ({ rowData }) => {
      const key = getRowKey(rowData);
      return h(ElCheckbox, {
        modelValue: selectedKeys.value.has(key),
        onChange: (val) => toggleRow(key, val),
      });
    },
  };
  const dataColumns = columns.value.map((col, index) => {
    const isFirst = index === 0;
    const targetWidth = isFirst ? 220 : 140;
    const minWidth = isFirst ? 180 : 120;
    return {
      key: col,
      dataKey: col,
      title: col,
      minWidth,
      width: targetWidth,
      cellRenderer: ({ rowData }) =>
        h(ElInput, {
          modelValue: rowData[col] ?? '',
          size: 'small',
          onInput: (val) => updateCell(getRowKey(rowData), col, val),
        }),
    };
  });
  return [selectionColumn, ...dataColumns];
});

const minTableWidth = computed(() => {
  if (!columns.value.length) {
    return 0;
  }
  const selectionWidth = 60;
  const dataWidth = columns.value.reduce((total, _, index) => {
    return total + (index === 0 ? 220 : 140);
  }, 0);
  return selectionWidth + dataWidth;
});

const hasPendingChanges = computed(() => {
  if (deletedRowIds.value.size > 0) return true;
  if (dirtyRows.value.size > 0) return true;
  return tableData.value.some((row) => row.__isNew || row.__isDirty);
});

const handleSearch = () => {
  page.value = 1;
  fetchData();
};

const handlePageChange = (newPage) => {
  page.value = newPage;
  fetchData();
};

const handleSizeChange = (newSize) => {
  pageSize.value = newSize;
  page.value = 1;
  fetchData();
};

const addRow = () => {
  if (!columns.value.length) {
    ElMessage.warning('尚未获取到列信息');
    return;
  }
  const newRow = columns.value.reduce((acc, col) => ({ ...acc, [col]: '' }), {});
  newRow.__isNew = true;
  newRow.__tempId = tempIdCounter.value--;
  newRow.__key = String(newRow.__tempId);
  tableData.value = [newRow, ...tableData.value];
};

const deleteSelectedRows = () => {
  if (!selectedKeys.value.size) {
    ElMessage.warning('请先选择要删除的行');
    return;
  }
  ElMessageBox.confirm('确定要删除选中的行吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      const targets = new Set(selectedKeys.value);
      selectedKeys.value = new Set();
      const remaining = [];
      const deleted = new Set(deletedRowIds.value);
      for (const row of tableData.value) {
        const key = getRowKey(row);
        if (targets.has(key)) {
          if (row.__rowid__ != null) {
            deleted.add(row.__rowid__);
          }
        } else {
          remaining.push(row);
        }
      }
      tableData.value = remaining;
      deletedRowIds.value = deleted;
      const map = new Map(dirtyRows.value);
      targets.forEach((key) => map.delete(key));
      dirtyRows.value = map;
      ElMessage.success('删除成功');
    })
    .catch(() => {});
};

const stripMeta = (row) => {
  const payload = {};
  columns.value.forEach((col) => {
    payload[col] = row[col];
  });
  if (row.__rowid__ != null) {
    payload.__rowid__ = row.__rowid__;
  }
  return payload;
};

const saveChanges = async () => {
  const inserted = tableData.value.filter((row) => row.__isNew).map(stripMeta);
  const updated = Array.from(dirtyRows.value.values()).map(stripMeta);
  const deleted = Array.from(deletedRowIds.value);

  if (!inserted.length && !updated.length && !deleted.length) {
    ElMessage.info('没有待保存的修改');
    return;
  }

  isSaving.value = true;
  try {
    const res = await fetch(`${API_BASE}/database/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ inserted, updated, deleted }),
    }).then((r) => r.json());
    if (res.status === 'success') {
      ElMessage.success(res.message || '保存成功');
      fetchData();
    } else {
      ElMessage.error(res.detail || res.message || '保存失败');
    }
  } catch (error) {
    console.error('保存数据库失败:', error);
    ElMessage.error('保存数据库失败，请稍后重试');
  } finally {
    isSaving.value = false;
  }
};

</script>

<style scoped>
.editor-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 12px;
  box-sizing: border-box;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
  flex-wrap: wrap;
}
.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.toolbar-filter {
  display: flex;
  align-items: center;
  gap: 4px;
}
.toolbar-search {
  width: 220px;
}
.table-wrapper {
  flex: 1;
  min-height: 360px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  overflow: hidden;
}
.table-scroll {
  width: 100%;
  height: 100%;
  overflow: auto;
}
.virtual-table {
  --el-table-row-hover-bg-color: var(--el-color-primary-light-9);
}
.empty-hint {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}
.pagination-bar {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>