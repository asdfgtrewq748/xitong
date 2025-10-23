class DataService {
  constructor() {
    this.baseURL = process.env.VUE_APP_API_URL || 'http://localhost:8000'
    this.globalData = {
      boreholeData: [],
      summaryData: [],
      coalSeamData: []
    }
    this.loading = false
  }

  // 读取CSV数据
  async readCSV(file) {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${this.baseURL}/api/upload-csv`, {
        method: 'POST',
        body: formData
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('CSV读取失败:', error)
      throw error
    }
  }

  // 获取钻孔数据
  async getBoreholeData() {
    try {
      const response = await fetch(`${this.baseURL}/api/borehole-data`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      this.globalData.boreholeData = data
      return data
    } catch (error) {
      console.error('获取钻孔数据失败:', error)
      throw error
    }
  }

  // 获取汇总数据
  async getSummaryData() {
    try {
      const response = await fetch(`${this.baseURL}/api/summary-data`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      this.globalData.summaryData = data
      return data
    } catch (error) {
      console.error('获取汇总数据失败:', error)
      throw error
    }
  }

  // 获取煤层数据
  async getCoalSeamData() {
    try {
      const response = await fetch(`${this.baseURL}/api/coal-seam-data`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      this.globalData.coalSeamData = data
      return data
    } catch (error) {
      console.error('获取煤层数据失败:', error)
      throw error
    }
  }

  // 获取所有数据
  async getAllData() {
    try {
      const [borehole, summary, coal] = await Promise.all([
        this.getBoreholeData(),
        this.getSummaryData(),
        this.getCoalSeamData()
      ])
      return {
        borehole: borehole,
        summary: summary,
        coal: coal
      }
    } catch (error) {
      console.error('获取全局数据失败:', error)
      throw error
    }
  }

  // 搜索和过滤数据
  searchBoreholes(query) {
    return this.globalData.boreholeData.filter(item => {
      return Object.values(item).some(value =>
        value && value.toString().toLowerCase().includes(query.toLowerCase())
      )
    })
  }

  filterByLithology(lithology) {
    return this.globalData.boreholeData.filter(item =>
      item.岩性 && item.岩性.includes(lithology)
    )
  }

  getUniqueLithologies() {
    const lithologies = new Set()
    this.globalData.boreholeData.forEach(item => {
      if (item.岩性) {
        lithologies.add(item.岩性)
      }
    })
    return Array.from(lithologies)
  }

  // 数据统计
  getDataStatistics() {
    const boreholeCount = this.globalData.boreholeData.length
    const coalSeamCount = this.globalData.coalSeamData.length
    const uniqueMines = new Set(this.globalData.summaryData.map(item => item.矿名)).size

    return {
      boreholeCount,
      coalSeamCount,
      uniqueMines,
      totalRecords: boreholeCount + coalSeamCount + this.globalData.summaryData.length
    }
  }

  // 清空数据
  clearData() {
    this.globalData = {
      boreholeData: [],
      summaryData: [],
      coalSeamData: []
    }
  }
}

export default new DataService()