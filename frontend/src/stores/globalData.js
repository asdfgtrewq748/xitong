import { ref, computed } from 'vue';

// 全局数据存储 - 使用 Vue 3 Composition API
class GlobalDataStore {
  constructor() {
    // 钻孔数据
    this.boreholeData = ref([]);
    this.boreholeColumns = ref([]);
    
    // 关键层数据
    this.keyStratumData = ref([]);
    this.keyStratumColumns = ref([]);
    
    // 元数据
    this.metadata = ref({
      boreholeFileCount: 0,
      boreholeRecordCount: 0,
      boreholeLastUpdated: null,
      keyStratumFileCount: 0,
      keyStratumRecordCount: 0,
      keyStratumLastUpdated: null,
    });
  }

  // 加载钻孔数据
  loadBoreholeData(records, columns) {
    this.boreholeData.value = records || [];
    this.boreholeColumns.value = columns || [];
    this.metadata.value.boreholeRecordCount = records?.length || 0;
    this.metadata.value.boreholeLastUpdated = new Date().toLocaleString('zh-CN');
  }

  // 加载关键层数据
  loadKeyStratumData(records, columns) {
    this.keyStratumData.value = records || [];
    this.keyStratumColumns.value = columns || [];
    this.metadata.value.keyStratumRecordCount = records?.length || 0;
    this.metadata.value.keyStratumLastUpdated = new Date().toLocaleString('zh-CN');
  }

  // 合并关键层计算结果到全局数据
  mergeKeyStratumResults(keyStratumRecords) {
    if (!keyStratumRecords || !keyStratumRecords.length) {
      return;
    }

    const existingData = this.keyStratumData.value;
    if (!existingData || !existingData.length) {
      // 如果没有现有数据，直接设置
      this.keyStratumData.value = keyStratumRecords;
      this.keyStratumColumns.value = Object.keys(keyStratumRecords[0] || {});
      this.metadata.value.keyStratumRecordCount = keyStratumRecords.length;
      this.metadata.value.keyStratumLastUpdated = new Date().toLocaleString('zh-CN');
      return;
    }

    // 合并逻辑：根据钻孔名匹配并更新关键层信息
    const updatedData = existingData.map(row => {
      const match = keyStratumRecords.find(
        ks => ks['钻孔名'] === row['钻孔名'] && ks['岩层名称'] === row['岩层名称']
      );
      if (match) {
        // 合并关键层相关字段
        return { ...row, ...match };
      }
      return row;
    });

    // 添加新增的记录（在原数据中不存在的）
    const existingKeys = new Set(
      existingData.map(r => `${r['钻孔名']}_${r['岩层名称']}`)
    );
    const newRecords = keyStratumRecords.filter(
      ks => !existingKeys.has(`${ks['钻孔名']}_${ks['岩层名称']}`)
    );

    this.keyStratumData.value = [...updatedData, ...newRecords];
    
    // 更新列信息
    const allColumns = new Set(this.keyStratumColumns.value);
    keyStratumRecords.forEach(record => {
      Object.keys(record).forEach(key => allColumns.add(key));
    });
    this.keyStratumColumns.value = Array.from(allColumns);
    
    this.metadata.value.keyStratumRecordCount = this.keyStratumData.value.length;
    this.metadata.value.keyStratumLastUpdated = new Date().toLocaleString('zh-CN');
  }

  // 清空全局数据
  clear() {
    this.boreholeData.value = [];
    this.boreholeColumns.value = [];
    this.keyStratumData.value = [];
    this.keyStratumColumns.value = [];
    this.metadata.value = {
      boreholeFileCount: 0,
      boreholeRecordCount: 0,
      boreholeLastUpdated: null,
      keyStratumFileCount: 0,
      keyStratumRecordCount: 0,
      keyStratumLastUpdated: null,
    };
  }

  // 检查是否有数据
  hasBoreholeData() {
    return computed(() => this.boreholeData.value.length > 0);
  }

  hasKeyStratumData() {
    return computed(() => this.keyStratumData.value.length > 0);
  }

  // 导出数据（供其他模块使用）
  exportData(type = 'all') {
    if (type === 'borehole') {
      return {
        records: this.boreholeData.value,
        columns: this.boreholeColumns.value,
      };
    } else if (type === 'keystratum') {
      return {
        records: this.keyStratumData.value,
        columns: this.keyStratumColumns.value,
      };
    } else {
      return {
        borehole: {
          records: this.boreholeData.value,
          columns: this.boreholeColumns.value,
        },
        keystratum: {
          records: this.keyStratumData.value,
          columns: this.keyStratumColumns.value,
        },
        metadata: this.metadata.value,
      };
    }
  }
}

// 创建单例
const globalDataStore = new GlobalDataStore();

export default globalDataStore;
