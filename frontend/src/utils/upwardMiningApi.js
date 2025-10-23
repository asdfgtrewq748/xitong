import { getApiBase } from './api'

// 创建API实例
const api = {
  // 基础API调用方法
  async callApi(endpoint, params = {}) {
    try {
      const response = await fetch(`${getApiBase()}/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API调用失败 ${endpoint}:`, error)
      throw error
    }
  },

  // 文件操作相关
  async selectFiles(options = {}) {
    return this.callApi('select_files', options)
  },

  async readFile(filePath) {
    return this.callApi('read_file', { file_path: filePath })
  },

  async selectFolder(title = '选择文件夹') {
    return this.callApi('select_folder', { title })
  },

  // 上行开采可行度计算相关
  async calculateUpwardMiningFeasibility(params) {
    return this.callApi('calculate_upward_mining_feasibility', params)
  },

  async batchCalculateUpwardMiningFeasibility(params) {
    return this.callApi('batch_calculate_upward_mining_feasibility', params)
  },

  async autoCalibrateUpwardMiningCoefficients(params) {
    return this.callApi('auto_calibrate_upward_mining_coefficients', params)
  },

  async getFeasibilityEvaluationLevels() {
    return this.callApi('get_feasibility_evaluation_levels')
  },

  async exportResults(params) {
    return this.callApi('export_results', params)
  },

  // 其他现有API方法保持不变
  async getDashboardStats() {
    return this.callApi('get_dashboard_stats')
  },

  async getChinaGeojson() {
    return this.callApi('get_china_geojson')
  },

  async getModelingDataColumns(params) {
    return this.callApi('get_modeling_data_columns', params)
  },

  async getUniqueColumnValues(params) {
    return this.callApi('get_unique_column_values', params)
  },

  async generateContourData(params) {
    return this.callApi('generate_contour_data', params)
  },

  async compareInterpolationMethods(params) {
    return this.callApi('compare_interpolation_methods', params)
  },

  async generateBlockModelData(params) {
    return this.callApi('generate_block_model_data', params)
  }
}

export { api }

// 为了向后兼容，默认导出
export default api