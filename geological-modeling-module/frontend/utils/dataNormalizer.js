/**
 * 数据归一化工具
 * 用于标准化从不同来源导入的数据
 */

// 列名标准化映射表
const COLUMN_NAME_MAP = {
  // 钻孔相关
  '钻孔名称': '钻孔名',
  '钻孔编号': '钻孔名',
  '孔名': '钻孔名',
  'BK': '钻孔名',
  
  // 岩层相关
  '岩性': '岩层',
  '岩层名': '岩层名称',
  '层名': '岩层名称',
  
  // 厚度相关
  '厚度': '厚度/m',
  '厚度(m)': '厚度/m',
  '层厚': '厚度/m',
  
  // 坐标相关
  'X': 'X坐标',
  'x': 'X坐标',
  'Y': 'Y坐标',
  'y': 'Y坐标',
  'Z': 'Z坐标',
  'z': 'Z坐标',
  
  // 力学参数 - 统一单位标识
  '弹性模量/Gpa': '弹性模量/GPa',
  '弹性模量(Gpa)': '弹性模量/GPa',
  '弹性模量': '弹性模量/GPa',
  
  '抗压强度/Mpa': '抗压强度/MPa',
  '抗压强度(Mpa)': '抗压强度/MPa',
  '抗压强度': '抗压强度/MPa',
  
  '抗拉强度/Mpa': '抗拉强度/MPa',
  '抗拉强度(Mpa)': '抗拉强度/MPa',
  '抗拉强度': '抗拉强度/MPa',
  
  '泊松比': '泊松比',
  'υ': '泊松比',
  
  '密度/g/cm3': '密度/g·cm⁻³',
  '密度(g/cm3)': '密度/g·cm⁻³',
  '密度': '密度/g·cm⁻³',
  
  // 其他
  '矿名': '矿井名称',
  '矿井': '矿井名称',
}

// 需要转换为数字的列
const NUMERIC_COLUMNS = [
  '厚度/m',
  'X坐标',
  'Y坐标',
  'Z坐标',
  '弹性模量/GPa',
  '抗压强度/MPa',
  '抗拉强度/MPa',
  '泊松比',
  '密度/g·cm⁻³',
  '距煤层距离/m',
  '顶板高度/m',
  '底板高度/m',
]

/**
 * 标准化列名
 * @param {string} columnName - 原始列名
 * @returns {string} - 标准化后的列名
 */
export function normalizeColumnName(columnName) {
  if (!columnName || typeof columnName !== 'string') {
    return columnName
  }
  
  // 去除首尾空格
  const trimmed = columnName.trim()
  
  // 查找映射
  if (COLUMN_NAME_MAP[trimmed]) {
    return COLUMN_NAME_MAP[trimmed]
  }
  
  return trimmed
}

/**
 * 标准化所有列名
 * @param {Array<string>} columns - 原始列名数组
 * @returns {Array<string>} - 标准化后的列名数组
 */
export function normalizeColumns(columns) {
  if (!Array.isArray(columns)) {
    return columns
  }
  
  return columns.map(col => normalizeColumnName(col))
}

/**
 * 转换值为数字
 * @param {*} value - 原始值
 * @returns {number|null} - 转换后的数字或null
 */
export function toNumber(value) {
  // 已经是数字
  if (typeof value === 'number') {
    return isNaN(value) ? null : value
  }
  
  // 空值处理
  if (value === null || value === undefined || value === '') {
    return null
  }
  
  // 字符串转数字
  if (typeof value === 'string') {
    const trimmed = value.trim()
    
    // 空字符串
    if (trimmed === '' || trimmed === '-' || trimmed === 'N/A' || trimmed === 'NA') {
      return null
    }
    
    const num = Number(trimmed)
    return isNaN(num) ? null : num
  }
  
  return null
}

/**
 * 标准化空值
 * @param {*} value - 原始值
 * @returns {*} - 标准化后的值
 */
export function normalizeNull(value) {
  if (value === null || value === undefined) {
    return null
  }
  
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (trimmed === '' || trimmed === '-' || trimmed === 'N/A' || trimmed === 'NA' || trimmed === 'null') {
      return null
    }
  }
  
  return value
}

/**
 * 标准化单条记录
 * @param {Object} record - 原始记录
 * @returns {Object} - 标准化后的记录
 */
export function normalizeRecord(record) {
  if (!record || typeof record !== 'object') {
    return record
  }
  
  const normalized = {}
  
  Object.keys(record).forEach(key => {
    const normalizedKey = normalizeColumnName(key)
    let value = normalizeNull(record[key])
    
    // 如果是数值列,转换为数字
    if (NUMERIC_COLUMNS.includes(normalizedKey)) {
      value = toNumber(value)
    }
    
    normalized[normalizedKey] = value
  })
  
  return normalized
}

/**
 * 标准化数据集
 * @param {Array<Object>} records - 原始记录数组
 * @param {Array<string>} columns - 原始列名数组
 * @returns {Object} - 包含标准化后的records和columns
 */
export function normalizeData(records, columns) {
  if (!Array.isArray(records) || !Array.isArray(columns)) {
    return { records, columns }
  }
  
  // 标准化列名
  const normalizedColumns = normalizeColumns(columns)
  
  // 标准化记录
  const normalizedRecords = records.map(record => 
    normalizeRecord(record)
  )
  
  return {
    records: normalizedRecords,
    columns: normalizedColumns
  }
}

/**
 * 验证必需字段
 * @param {Object} record - 记录
 * @param {Array<string>} requiredFields - 必需字段列表
 * @returns {Object} - {valid: boolean, missing: Array<string>}
 */
export function validateRequiredFields(record, requiredFields = ['钻孔名', '岩层']) {
  const missing = []
  
  requiredFields.forEach(field => {
    if (!record[field] || record[field] === null) {
      missing.push(field)
    }
  })
  
  return {
    valid: missing.length === 0,
    missing
  }
}

/**
 * 批量验证记录
 * @param {Array<Object>} records - 记录数组
 * @param {Array<string>} requiredFields - 必需字段列表
 * @returns {Object} - {validRecords, invalidRecords, errors}
 */
export function validateRecords(records, requiredFields = ['钻孔名', '岩层']) {
  const validRecords = []
  const invalidRecords = []
  const errors = []
  
  records.forEach((record, index) => {
    const validation = validateRequiredFields(record, requiredFields)
    
    if (validation.valid) {
      validRecords.push(record)
    } else {
      invalidRecords.push(record)
      errors.push({
        index,
        record,
        missing: validation.missing
      })
    }
  })
  
  return {
    validRecords,
    invalidRecords,
    errors
  }
}

export default {
  normalizeColumnName,
  normalizeColumns,
  normalizeRecord,
  normalizeData,
  toNumber,
  normalizeNull,
  validateRequiredFields,
  validateRecords,
}
