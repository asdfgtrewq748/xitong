/**
 * 统计分析工具
 */

/**
 * 计算皮尔逊相关系数
 * @param {Array} x - X轴数据数组
 * @param {Array} y - Y轴数据数组
 * @returns {Object} 相关系数和相关统计
 */
export function calculateCorrelation(x, y) {
  if (x.length !== y.length || x.length === 0) {
    throw new Error('数据长度不一致或为空')
  }

  const n = x.length
  const sumX = x.reduce((a, b) => a + b, 0)
  const sumY = y.reduce((a, b) => a + b, 0)
  const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0)
  const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0)
  const sumYY = y.reduce((sum, yi) => sum + yi * yi, 0)

  const meanX = sumX / n
  const meanY = sumY / n

  // 计算相关系数
  const numerator = sumXY - n * meanX * meanY
  const denominatorX = Math.sqrt(sumXX - n * meanX * meanX)
  const denominatorY = Math.sqrt(sumYY - n * meanY * meanY)
  const denominator = denominatorX * denominatorY

  const r = denominator === 0 ? 0 : numerator / denominator

  // 计算R²
  const r2 = r * r

  // 计算p值（简化版本，实际应用中可能需要更复杂的计算）
  const t = Math.abs(r * Math.sqrt((n - 2) / (1 - r * r)))
  const pValue = 2 * (1 - tDistributionCDF(t, n - 2))

  return {
    r,
    r2,
    pValue,
    n,
    meanX,
    meanY,
    significant: pValue < 0.05
  }
}

/**
 * t分布累积分布函数（简化版）
 * @param {number} t - t统计量
 * @param {number} df - 自由度
 * @returns {number} 累积概率
 */
function tDistributionCDF(t, df) {
  // 使用正态分布近似（df > 30时较准确）
  if (df > 30) {
    return normalCDF(t)
  }

  // 对于小自由度，使用简化近似
  const a = df / (df + t * t)
  const b = 0.5 * df
  return 1 - 0.5 * betaIncomplete(b, 0.5, a)
}

/**
 * 正态分布累积分布函数
 * @param {number} x - 标准正态分布值
 * @returns {number} 累积概率
 */
function normalCDF(x) {
  return 0.5 * (1 + erf(x / Math.sqrt(2)))
}

/**
 * 误差函数（近似）
 * @param {number} x - 输入值
 * @returns {number} 误差函数值
 */
function erf(x) {
  const a1 =  0.254829592
  const a2 = -0.284496736
  const a3 =  1.421413741
  const a4 = -1.453152027
  const a5 =  1.061405429
  const p  =  0.3275911

  const sign = x < 0 ? -1 : 1
  x = Math.abs(x)

  const t = 1.0 / (1.0 + p * x)
  const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x)

  return sign * y
}

/**
 * Beta不完全函数（简化版）
 * @param {number} a - 参数a
 * @param {number} b - 参数b
 * @param {number} x - 输入值
 * @returns {number} Beta不完全函数值
 */
function betaIncomplete(a, b, x) {
  // 简化实现，实际应用中可能需要更精确的计算
  if (x === 0) return 0
  if (x === 1) return 1

  // 使用连分式展开的简化版本
  return Math.pow(x, a) * Math.pow(1 - x, b) / a
}

/**
 * 线性回归计算
 * @param {Array} x - X轴数据
 * @param {Array} y - Y轴数据
 * @returns {Object} 回归结果
 */
export function linearRegression(x, y) {
  if (x.length !== y.length || x.length === 0) {
    throw new Error('数据长度不一致或为空')
  }

  const n = x.length
  const sumX = x.reduce((a, b) => a + b, 0)
  const sumY = y.reduce((a, b) => a + b, 0)
  const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0)
  const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0)

  const meanX = sumX / n
  const meanY = sumY / n

  // 计算斜率和截距
  const slope = (sumXY - n * meanX * meanY) / (sumXX - n * meanX * meanX)
  const intercept = meanY - slope * meanX

  // 计算预测值
  const predictions = x.map(xi => slope * xi + intercept)

  // 计算残差
  const residuals = y.map((yi, i) => yi - predictions[i])

  // 计算R²
  const ssTotal = y.reduce((sum, yi) => sum + Math.pow(yi - meanY, 2), 0)
  const ssResidual = residuals.reduce((sum, ri) => sum + ri * ri, 0)
  const r2 = 1 - (ssResidual / ssTotal)

  // 计算标准误差
  const mse = ssResidual / (n - 2)
  const standardError = Math.sqrt(mse)

  return {
    slope,
    intercept,
    r2,
    predictions,
    residuals,
    standardError,
    equation: `y = ${slope.toFixed(3)}x + ${intercept.toFixed(3)}`
  }
}

/**
 * 多项式回归计算
 * @param {Array} x - X轴数据
 * @param {Array} y - Y轴数据
 * @param {number} degree - 多项式次数
 * @returns {Object} 回归结果
 */
export function polynomialRegression(x, y, degree = 2) {
  if (x.length !== y.length || x.length === 0) {
    throw new Error('数据长度不一致或为空')
  }

  const n = x.length
  if (n <= degree) {
    throw new Error('数据点数量不足')
  }

  // 构建设计矩阵
  const X = []
  for (let i = 0; i < n; i++) {
    const row = []
    for (let j = 0; j <= degree; j++) {
      row.push(Math.pow(x[i], j))
    }
    X.push(row)
  }

  // 使用最小二乘法求解 (简化版本)
  const coefficients = solveLeastSquares(X, y)

  // 计算预测值
  const predictions = x.map(xi => {
    let sum = 0
    for (let j = 0; j <= degree; j++) {
      sum += coefficients[j] * Math.pow(xi, j)
    }
    return sum
  })

  // 计算R²
  const meanY = y.reduce((a, b) => a + b, 0) / n
  const ssTotal = y.reduce((sum, yi) => sum + Math.pow(yi - meanY, 2), 0)
  const ssResidual = y.reduce((sum, yi, i) => sum + Math.pow(yi - predictions[i], 2), 0)
  const r2 = 1 - (ssResidual / ssTotal)

  return {
    coefficients,
    predictions,
    r2,
    degree,
    equation: formatPolynomialEquation(coefficients)
  }
}

/**
 * 解最小二乘问题（简化版）
 * @param {Array} X - 设计矩阵
 * @param {Array} y - Y向量
 * @returns {Array} 系数向量
 */
function solveLeastSquares(X, y) {
  // 简化实现，实际应用中应该使用更稳健的数值方法
  // const m = X.length
  // const n = X[0].length

  // 计算X'X
  const XT = transposeMatrix(X)
  const XTX = multiplyMatrix(XT, X)

  // 计算X'y
  const XTy = multiplyMatrixVector(XT, y)

  // 简化的矩阵求逆（仅适用于小型矩阵）
  const XTX_inv = invertMatrix(XTX)

  return multiplyMatrixVector(XTX_inv, XTy)
}

/**
 * 矩阵转置
 * @param {Array} matrix - 输入矩阵
 * @returns {Array} 转置矩阵
 */
function transposeMatrix(matrix) {
  return matrix[0].map((_, colIndex) => matrix.map(row => row[colIndex]))
}

/**
 * 矩阵乘法
 * @param {Array} A - 矩阵A
 * @param {Array} B - 矩阵B
 * @returns {Array} 乘积矩阵
 */
function multiplyMatrix(A, B) {
  const result = []
  for (let i = 0; i < A.length; i++) {
    result[i] = []
    for (let j = 0; j < B[0].length; j++) {
      let sum = 0
      for (let k = 0; k < A[0].length; k++) {
        sum += A[i][k] * B[k][j]
      }
      result[i][j] = sum
    }
  }
  return result
}

/**
 * 矩阵向量乘法
 * @param {Array} matrix - 矩阵
 * @param {Array} vector - 向量
 * @returns {Array} 结果向量
 */
function multiplyMatrixVector(matrix, vector) {
  return matrix.map(row =>
    row.reduce((sum, val, i) => sum + val * vector[i], 0)
  )
}

/**
 * 矩阵求逆（简化版，仅适用于2x2或3x3矩阵）
 * @param {Array} matrix - 输入矩阵
 * @returns {Array} 逆矩阵
 */
function invertMatrix(matrix) {
  const n = matrix.length

  if (n === 1) {
    return [[1 / matrix[0][0]]]
  }

  if (n === 2) {
    const [[a, b], [c, d]] = matrix
    const det = a * d - b * c
    if (det === 0) throw new Error('矩阵不可逆')
    return [[d / det, -b / det], [-c / det, a / det]]
  }

  // 对于更大的矩阵，应该使用更复杂的算法
  throw new Error('不支持的矩阵大小')
}

/**
 * 格式化多项式方程
 * @param {Array} coefficients - 系数数组
 * @returns {string} 方程字符串
 */
function formatPolynomialEquation(coefficients) {
  let equation = 'y = '

  for (let i = coefficients.length - 1; i >= 0; i--) {
    const coeff = coefficients[i]
    if (Math.abs(coeff) < 0.001) continue

    if (i === coefficients.length - 1) {
      equation += `${coeff.toFixed(3)}`
    } else {
      const sign = coeff >= 0 ? ' + ' : ' - '
      const absCoeff = Math.abs(coeff)
      equation += `${sign}${absCoeff.toFixed(3)}`
    }

    if (i > 1) {
      equation += `x^${i}`
    } else if (i === 1) {
      equation += 'x'
    }
  }

  return equation
}

/**
 * 计算数据的描述性统计
 * @param {Array} data - 数据数组
 * @returns {Object} 统计结果
 */
export function descriptiveStatistics(data) {
  if (!data || data.length === 0) {
    return null
  }

  const validData = data.filter(d => d != null && !isNaN(d))
  if (validData.length === 0) {
    return null
  }

  const sorted = [...validData].sort((a, b) => a - b)
  const n = sorted.length

  const sum = sorted.reduce((a, b) => a + b, 0)
  const mean = sum / n

  const variance = sorted.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / n
  const std = Math.sqrt(variance)

  const median = n % 2 === 0
    ? (sorted[n/2 - 1] + sorted[n/2]) / 2
    : sorted[Math.floor(n/2)]

  const q1Index = Math.floor(n * 0.25)
  const q3Index = Math.floor(n * 0.75)
  const q1 = sorted[q1Index]
  const q3 = sorted[q3Index]

  return {
    count: n,
    mean,
    median,
    std,
    variance,
    min: sorted[0],
    max: sorted[n - 1],
    q1,
    q3,
    iqr: q3 - q1,
    range: sorted[n - 1] - sorted[0]
  }
}