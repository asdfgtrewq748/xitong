import dataset from './boreholes.json'

const boreholes = dataset.boreholes || []
const summary = dataset.summary || {}

const boreholeMap = boreholes.reduce((acc, item) => {
  acc[item.id] = item
  return acc
}, {})

const coordinateSeries = boreholes.map((hole) => ({
  id: hole.id,
  x: hole.coordinate?.x || 0,
  y: hole.coordinate?.y || 0,
  depth: hole.totalThickness,
  coal: hole.coalThickness,
}))

const keyStrataRanking = boreholes
  .flatMap((hole) =>
    (hole.keyStrataCandidates || []).map((layer) => ({
      ...layer,
      borehole: hole.id,
    })),
  )
  .sort((a, b) => b.mechanicalIndex - a.mechanicalIndex)

function getBorehole(id) {
  return boreholeMap[id] || null
}

function buildSubsidenceProfile(id) {
  const hole = getBorehole(id)
  if (!hole) return []
  const maxSubsidence = Math.min(
    5,
    0.032 * hole.totalThickness + 0.25 * hole.coalThickness,
  )
  const sigma = 220 + hole.coalThickness * 8
  const profile = []
  for (let offset = -500; offset <= 500; offset += 50) {
    const value = -maxSubsidence * Math.exp(-(offset ** 2) / (2 * sigma ** 2))
    profile.push({ x: offset, z: Number(value.toFixed(2)) })
  }
  return profile
}

function buildPressureSeries(id) {
  const hole = getBorehole(id)
  if (!hole) return []
  const base = 2800 + hole.coalThickness * 80
  const variability = Math.min(600, hole.totalThickness * 1.8)
  const steps = ['10:00', '10:10', '10:20', '10:30', '10:40', '10:50', '11:00', '11:10']
  return steps.map((label, index) => {
    const phase = Math.sin((index / (steps.length - 1)) * Math.PI)
    const actual = base + variability * phase
    const predicted = actual - (40 - hole.coalThickness * 2)
    return {
      step: label,
      actual: Number(actual.toFixed(0)),
      predicted: Number(predicted.toFixed(0)),
    }
  })
}

function getLayerStack(id) {
  const hole = getBorehole(id)
  if (!hole) return []
  const sorted = [...(hole.layers || [])].sort(
    (a, b) => (a.order ?? 0) - (b.order ?? 0),
  )
  return sorted.map((layer, idx) => {
    const prevBottom = idx === 0 ? 0 : sorted[idx - 1].cumulativeDepth || 0
    return {
      ...layer,
      depthTop: Number(prevBottom.toFixed(2)),
      depthBottom: Number((layer.cumulativeDepth ?? 0).toFixed(2)),
    }
  })
}

function getCoalThicknessTrend() {
  return boreholes.map((hole) => ({
    id: hole.id,
    coalThickness: Number(hole.coalThickness?.toFixed(2) || 0),
    totalThickness: Number(hole.totalThickness?.toFixed(2) || 0),
  }))
}

export {
  dataset,
  boreholes,
  summary,
  boreholeMap,
  coordinateSeries,
  keyStrataRanking,
  buildSubsidenceProfile,
  buildPressureSeries,
  getLayerStack,
  getBorehole,
  getCoalThicknessTrend,
}
