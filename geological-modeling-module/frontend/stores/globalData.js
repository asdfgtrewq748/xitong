// Pinia 全局数据存储
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getApiBase } from '@/utils/api'
import { normalizeData, validateRecords } from '@/utils/dataNormalizer'
import demoDataset from '@/data/boreholes.json'

export const useGlobalDataStore = defineStore('globalData', () => {
  // ========== 状态定义 ==========
  // 钻孔数据
  const boreholeData = ref([])
  const boreholeColumns = ref([])
  
  // 关键层数据（主数据源）
  const keyStratumData = ref([])
  const keyStratumColumns = ref([])
  
  // 元数据
  const metadata = ref({
    boreholeFileCount: 0,
    boreholeRecordCount: 0,
    boreholeLastUpdated: null,
    keyStratumFileCount: 0,
    keyStratumRecordCount: 0,
    keyStratumLastUpdated: null,
  })

  // 静态演示数据
  const staticRecords = []
  const staticColumnsSet = new Set([
    '钻孔名',
    '岩层',
    '岩层名称',
    '序号',
    '厚度/m',
    '累计深度/m',
    '弹性模量/GPa',
    '容重/kN*m-3',
    '抗拉强度/MPa',
    '机械指数',
    'X坐标',
    'Y坐标',
    '煤层',
  ])

  if (demoDataset?.boreholes) {
    demoDataset.boreholes.forEach((hole) => {
      (hole.layers || []).forEach((layer) => {
        staticRecords.push({
          钻孔名: hole.id,
          岩层: layer.name,
          岩层名称: layer.name,
          序号: layer.order,
          '厚度/m': layer.thickness,
          '累计深度/m': layer.cumulativeDepth,
          '弹性模量/GPa': layer.elasticModulus,
          '容重/kN*m-3': layer.density,
          '抗拉强度/MPa': layer.tensileStrength,
          机械指数: layer.mechanicalIndex,
          X坐标: hole.coordinate?.x ?? null,
          Y坐标: hole.coordinate?.y ?? null,
          煤层: layer.name?.includes('煤') ? layer.name : null,
        })
      })
    })
  }

  const staticColumns = Array.from(staticColumnsSet)
  let hasBootstrappedStatic = false

  // 导入历史记录
  const importHistory = ref([])
  const maxHistorySize = 10 // 最多保留10条历史记录

  // ========== 计算属性 ==========
  const hasBoreholeData = computed(() => boreholeData.value.length > 0)
  const hasKeyStratumData = computed(() => keyStratumData.value.length > 0)
  const totalRecords = computed(() => keyStratumData.value.length)

  // ========== 历史记录辅助函数 ==========
  function saveToHistory(source, recordCount, columns) {
    const snapshot = {
      id: Date.now(),
      timestamp: new Date().toLocaleString('zh-CN'),
      source, // 'import' 或 'database'
      recordCount,
      columns: [...columns],
      data: JSON.parse(JSON.stringify(keyStratumData.value)), // 深拷贝数据
    }
    
    importHistory.value.unshift(snapshot)
    
    // 限制历史记录数量
    if (importHistory.value.length > maxHistorySize) {
      importHistory.value = importHistory.value.slice(0, maxHistorySize)
    }
  }

  function rollbackToHistory(historyId) {
    const snapshot = importHistory.value.find(h => h.id === historyId)
    if (!snapshot) {
      throw new Error('未找到指定的历史记录')
    }
    
    // 恢复数据
    keyStratumData.value = JSON.parse(JSON.stringify(snapshot.data))
    keyStratumColumns.value = [...snapshot.columns]
    metadata.value.keyStratumRecordCount = snapshot.recordCount
    metadata.value.keyStratumLastUpdated = new Date().toLocaleString('zh-CN')
    
    return snapshot
  }

  function clearHistory() {
    importHistory.value = []
  }

  function deleteHistoryItem(historyId) {
    const index = importHistory.value.findIndex(h => h.id === historyId)
    if (index !== -1) {
      importHistory.value.splice(index, 1)
    }
  }

  // ========== 基础数据加载方法 ==========
  function loadBoreholeData(records, columns) {
    boreholeData.value = records || []
    boreholeColumns.value = columns || []
    metadata.value.boreholeRecordCount = records?.length || 0
    metadata.value.boreholeLastUpdated = new Date().toLocaleString('zh-CN')
  }

  function loadKeyStratumData(records, columns) {
    if (!records || !columns) {
      keyStratumData.value = []
      keyStratumColumns.value = []
      metadata.value.keyStratumRecordCount = 0
      return
    }
    
    // 应用数据归一化
    const normalized = normalizeData(records, columns)
    
    // 验证数据
    const validation = validateRecords(normalized.records, ['钻孔名'])
    
    if (validation.errors.length > 0) {
      console.warn(`[globalDataStore] 发现 ${validation.errors.length} 条无效记录`, validation.errors)
    }
    
    // 使用有效记录
    keyStratumData.value = validation.validRecords
    keyStratumColumns.value = normalized.columns
    metadata.value.keyStratumRecordCount = validation.validRecords.length
    metadata.value.keyStratumLastUpdated = new Date().toLocaleString('zh-CN')
  }

  function bootstrapStaticDataset() {
    if (hasBootstrappedStatic || staticRecords.length === 0) {
      return
    }
    loadBoreholeData(staticRecords, staticColumns)
    loadKeyStratumData(staticRecords, staticColumns)
    metadata.value.boreholeFileCount = 1
    metadata.value.keyStratumFileCount = 1
    hasBootstrappedStatic = true
  }

  // ========== 数据合并方法 ==========
  function mergeKeyStratumResults(keyStratumRecords) {
    if (!keyStratumRecords || !keyStratumRecords.length) {
      return
    }

    const existingData = keyStratumData.value
    if (!existingData || !existingData.length) {
      // 如果没有现有数据，直接设置
      keyStratumData.value = keyStratumRecords
      keyStratumColumns.value = Object.keys(keyStratumRecords[0] || {})
      metadata.value.keyStratumRecordCount = keyStratumRecords.length
      metadata.value.keyStratumLastUpdated = new Date().toLocaleString('zh-CN')
      return
    }

    // 合并逻辑：根据钻孔名匹配并更新关键层信息
    const updatedData = existingData.map(row => {
      const match = keyStratumRecords.find(
        ks => ks['钻孔名'] === row['钻孔名'] && ks['岩层名称'] === row['岩层名称']
      )
      if (match) {
        return { ...row, ...match }
      }
      return row
    })

    // 添加新增的记录
    const existingKeys = new Set(
      existingData.map(r => `${r['钻孔名']}_${r['岩层名称']}`)
    )
    const newRecords = keyStratumRecords.filter(
      ks => !existingKeys.has(`${ks['钻孔名']}_${ks['岩层名称']}`)
    )

    keyStratumData.value = [...updatedData, ...newRecords]
    
    // 更新列信息
    const allColumns = new Set(keyStratumColumns.value)
    keyStratumRecords.forEach(record => {
      Object.keys(record).forEach(key => allColumns.add(key))
    })
    keyStratumColumns.value = Array.from(allColumns)
    
    metadata.value.keyStratumRecordCount = keyStratumData.value.length
    metadata.value.keyStratumLastUpdated = new Date().toLocaleString('zh-CN')
  }

  // ========== 清空方法 ==========
  function clear() {
    boreholeData.value = []
    boreholeColumns.value = []
    keyStratumData.value = []
    keyStratumColumns.value = []
    metadata.value = {
      boreholeFileCount: 0,
      boreholeRecordCount: 0,
      boreholeLastUpdated: null,
      keyStratumFileCount: 0,
      keyStratumRecordCount: 0,
      keyStratumLastUpdated: null,
    }
  }

  function clearBoreholeData() {
    boreholeData.value = []
    boreholeColumns.value = []
    metadata.value.boreholeFileCount = 0
    metadata.value.boreholeRecordCount = 0
    metadata.value.boreholeLastUpdated = null
  }

  function clearKeyStratumData() {
    keyStratumData.value = []
    keyStratumColumns.value = []
    metadata.value.keyStratumFileCount = 0
    metadata.value.keyStratumRecordCount = 0
    metadata.value.keyStratumLastUpdated = null
  }

  // ========== 导出数据方法 ==========
  function exportData(type = 'all') {
    if (type === 'borehole') {
      return {
        records: boreholeData.value,
        columns: boreholeColumns.value,
      }
    } else if (type === 'keystratum') {
      return {
        records: keyStratumData.value,
        columns: keyStratumColumns.value,
      }
    } else {
      return {
        borehole: {
          records: boreholeData.value,
          columns: boreholeColumns.value,
        },
        keystratum: {
          records: keyStratumData.value,
          columns: keyStratumColumns.value,
        },
        metadata: metadata.value,
      }
    }
  }

  // ========== 网络与统一导入接口 ==========
  async function importRawFiles(formData, options = {}) {
    try {
      const baseUrl = options.url || getApiBase()
      const resp = await fetch(`${baseUrl}/raw/import`, {
        method: 'POST',
        body: formData,
      })
      
      if (!resp.ok) {
        const txt = await resp.text()
        throw new Error(`HTTP ${resp.status}: ${txt}`)
      }
      
      const result = await resp.json()
      
      if (result.status === 'success') {
        if (result.records && result.records.length) {
          loadKeyStratumData(result.records, result.columns || [])
          // 保存到历史记录
          saveToHistory('文件导入', result.records.length, result.columns || [])
        }
      }
      
      return result
    } catch (err) {
      console.error('[globalDataStore] importRawFiles error:', err)
      throw err
    }
  }

  async function loadFromDatabase(page = 1, pageSize = 10000) {
    try {
      const baseUrl = getApiBase()
      const url = `${baseUrl}/database/records?page=${page}&page_size=${pageSize}`
      
      const resp = await fetch(url)
      
      if (!resp.ok) {
        const txt = await resp.text()
        throw new Error(`HTTP ${resp.status}: ${txt}`)
      }
      
      const json = await resp.json()
      
      if (json.status === 'success') {
        const formatted = (json.records || []).map(record => {
          if (!record['钻孔名']) {
            record['钻孔名'] = record['矿名'] || '未命名钻孔'
          }
          if (record['岩性'] && !record['岩层']) {
            record['岩层'] = record['岩性']
          }
          return record
        })
        
        loadKeyStratumData(formatted, json.columns || [])
        // 保存到历史记录
        saveToHistory('数据库加载', formatted.length, json.columns || [])
      }
      
      return json
    } catch (err) {
      console.error('[globalDataStore] loadFromDatabase error:', err)
      throw err
    }
  }

  async function refresh() {
    return {
      status: 'success',
      total: keyStratumData.value.length,
    }
  }

  // 初始化内置演示数据
  bootstrapStaticDataset()

  // ========== 返回 store ==========
  return {
    // 状态
    boreholeData,
    boreholeColumns,
    keyStratumData,
    keyStratumColumns,
    metadata,
    importHistory,
    
    // 计算属性
    hasBoreholeData,
    hasKeyStratumData,
    totalRecords,
    
    // 方法
    loadBoreholeData,
    loadKeyStratumData,
    mergeKeyStratumResults,
    clear,
    clearBoreholeData,
    clearKeyStratumData,
    exportData,
    importRawFiles,
    loadFromDatabase,
    refresh,
    // 历史记录方法
    rollbackToHistory,
    clearHistory,
    deleteHistoryItem,
    bootstrapStaticDataset,
  }
})
