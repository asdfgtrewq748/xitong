// 组件目录的 ChartWrapper 只是桥接到 utils 中的实现，避免 import 路径混淆
import { ChartWrapper as UtilsChartWrapper, getColorScheme, generateScatterOption, generateLineOption, generateHeatmapOption, generateSurfaceOption } from '../../utils/chartWrapper'

export const ChartWrapper = UtilsChartWrapper
export const getColorSchemes = getColorScheme
export const generateOptions = {
  scatter: generateScatterOption,
  line: generateLineOption,
  heatmap: generateHeatmapOption,
  surface: generateSurfaceOption
}
