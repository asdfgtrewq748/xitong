<template>
   <div class="relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-slate-50 via-white to-slate-100"></div>
      <div class="relative z-10">
         <!-- Hero -->
         <section class="pt-16 pb-20 px-6 lg:px-12 max-w-7xl mx-auto animate-fadeIn">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
               <div class="space-y-8">
                  <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-600 text-xs font-bold uppercase tracking-wide">
                     <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                     宏观-微观一体化演示 / BK 盆地
                  </div>
                  <h1 class="text-4xl md:text-6xl font-black text-slate-900 leading-tight">
                     集成地质建模 · <span class="text-gradient-primary">真实钻孔数据</span>
                  </h1>
                  <p class="text-lg text-slate-600 leading-relaxed max-w-xl">
                     演示站点内置 {{ summaryCards[0].value }} 个钻孔与 {{ summaryCards[3].value }} 段煤层真实参数。
                     自动驱动关键层识别、三维建模、沉降预测、压力预警等功能模块，完整展示科研到工程的全流程能力。
                  </p>
                  <div class="flex flex-wrap gap-4">
                     <GlassButton @click="goToConsole">
                        <Activity :size="18" /> 体验工作台
                     </GlassButton>
                     <GlassButton variant="secondary" @click="scrollToSection('prediction')">
                        <TrendingUp :size="18" /> 观看预测
                     </GlassButton>
                  </div>
                  <div class="bg-white/80 rounded-2xl border border-slate-100 shadow-lg p-6 space-y-4">
                     <div class="flex flex-wrap items-center justify-between gap-4">
                        <div>
                           <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">重点钻孔</p>
                           <p class="text-2xl font-black text-slate-900 mt-1">{{ selectedHole.id }}</p>
                        </div>
                        <div class="text-right">
                           <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">累计厚度</p>
                           <p class="text-xl font-black text-slate-900 mt-1">{{ formatNumber(selectedHole.totalThickness) }} m</p>
                        </div>
                     </div>
                     <div class="flex flex-wrap gap-2">
                        <button
                           v-for="hole in holeOptions"
                           :key="hole"
                           class="px-3 py-1 rounded-full text-sm font-semibold border transition-all"
                           :class="hole === selectedHoleId ? 'bg-gradient-primary text-white border-transparent shadow-lg shadow-blue-500/20' : 'bg-white text-slate-500 border-slate-200 hover:border-blue-200 hover:text-blue-600'"
                           @click="selectedHoleId = hole"
                        >
                           {{ hole }}
                        </button>
                     </div>
                  </div>
               </div>

               <div class="relative">
                  <div class="absolute -inset-6 bg-gradient-to-r from-blue-100 via-cyan-50 to-emerald-50 blur-3xl opacity-80"></div>
                  <div class="relative bg-white rounded-[34px] p-6 border border-slate-100 shadow-[0_35px_80px_-35px_rgba(15,23,42,0.3)]">
                     <div class="flex justify-between items-center mb-6">
                        <div>
                           <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">钻孔坐标云</p>
                           <p class="text-lg font-bold text-slate-800">BK 区域工程测线</p>
                        </div>
                        <MapPin class="text-blue-500" :size="28" />
                     </div>
                     <div class="relative h-64 rounded-3xl border border-slate-100 bg-slate-900 overflow-hidden">
                        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.15),transparent_60%)]"></div>
                        <div class="absolute inset-0 opacity-30" style="background-image: linear-gradient(0deg, rgba(255,255,255,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.07) 1px, transparent 1px); background-size: 40px 40px;"></div>
                        <div class="absolute inset-6">
                           <div
                              v-for="point in mappedPoints"
                              :key="point.id"
                              class="absolute group"
                              :style="{ left: point.left + '%', top: point.top + '%' }"
                           >
                              <div
                                 class="w-3 h-3 rounded-full border-2 border-white"
                                 :class="point.id === selectedHoleId ? 'bg-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.8)]' : 'bg-slate-500'"
                              ></div>
                              <span class="absolute left-4 top-1 text-[10px] font-mono text-white/70 bg-slate-900/60 rounded px-1 py-0.5 opacity-0 group-hover:opacity-100">
                                 {{ point.id }}
                              </span>
                           </div>
                        </div>
                     </div>
                        <div class="mt-6 grid grid-cols-2 gap-4 text-sm text-slate-600">
                        <div>
                           <p class="text-xs uppercase tracking-wide text-slate-400">横向跨度</p>
                           <p class="text-lg font-bold text-slate-900">{{ mapMetrics.spanX }} m</p>
                        </div>
                        <div>
                           <p class="text-xs uppercase tracking-wide text-slate-400">纵向跨度</p>
                           <p class="text-lg font-bold text-slate-900">{{ mapMetrics.spanY }} m</p>
                        </div>
                     </div>
                  </div>
               </div>
            </div>
         </section>

         <!-- Summary Cards -->
         <section class="max-w-7xl mx-auto px-6 lg:px-12 pb-16">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
               <div
                  v-for="card in summaryCards"
                  :key="card.label"
                  class="glass-panel rounded-3xl p-6 border border-white/60 backdrop-blur shadow-lg shadow-blue-500/5"
               >
                  <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">{{ card.label }}</p>
                  <p class="text-3xl font-black text-slate-900 mt-3">{{ card.value }}</p>
                  <p class="text-xs text-slate-500 mt-1">{{ card.hint }}</p>
               </div>
            </div>
         </section>

         <!-- Theoretical Section -->
         <section id="theoretical" class="bg-white/80 border-y border-slate-100 py-16">
            <div class="max-w-7xl mx-auto px-6 lg:px-12 grid grid-cols-1 lg:grid-cols-2 gap-10">
               <div class="rounded-3xl border border-slate-100 bg-white shadow-xl p-6">
                  <div class="flex items-center justify-between">
                     <div>
                        <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">沉降预测</p>
                        <h3 class="text-2xl font-bold text-slate-900 mt-2">概率积分曲线 ({{ selectedHole.id }})</h3>
                     </div>
                     <div class="text-right">
                        <p class="text-xs text-slate-400">最大沉降</p>
                        <p class="text-xl font-black text-slate-900">{{ maxSubsidence }} m</p>
                     </div>
                  </div>
                  <div class="mt-6 relative">
                     <svg :width="chartSize.width" :height="chartSize.height" class="w-full" viewBox="0 0 620 220">
                        <defs>
                           <linearGradient id="subsidence" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stop-color="#0ea5e9" stop-opacity="0.45" />
                              <stop offset="100%" stop-color="#38bdf8" stop-opacity="0" />
                           </linearGradient>
                        </defs>
                        <path :d="subsidenceAreaPath" fill="url(#subsidence)" />
                        <path :d="subsidenceLine" fill="none" stroke="#0284c7" stroke-width="3" stroke-linecap="round" />
                     </svg>
                     <div class="absolute bottom-0 left-0 flex justify-between w-full text-[10px] text-slate-400">
                        <span>-500m</span>
                        <span>0</span>
                        <span>500m</span>
                     </div>
                  </div>
                  <div class="mt-6 grid grid-cols-3 gap-4 text-sm">
                     <div class="bg-slate-50 rounded-2xl p-4">
                        <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">埋深</p>
                        <p class="text-xl font-black text-slate-900 mt-1">{{ formatNumber(selectedHole.totalThickness) }} m</p>
                     </div>
                     <div class="bg-slate-50 rounded-2xl p-4">
                        <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">煤厚</p>
                        <p class="text-xl font-black text-slate-900 mt-1">{{ formatNumber(selectedHole.coalThickness) }} m</p>
                     </div>
                     <div class="bg-slate-50 rounded-2xl p-4">
                        <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">关键层</p>
                        <p class="text-xl font-black text-slate-900 mt-1">{{ highlightStrata.length }}</p>
                     </div>
                  </div>
               </div>

               <div class="rounded-3xl border border-slate-100 bg-slate-900 text-white shadow-2xl p-6">
                  <div class="flex items-center justify-between">
                     <div>
                        <p class="text-xs font-semibold text-white/60 uppercase tracking-widest">关键层定位</p>
                        <h3 class="text-2xl font-bold mt-2">Key Strata Identification</h3>
                     </div>
                     <Layers :size="32" class="text-cyan-400" />
                  </div>
                  <div class="mt-6 space-y-4">
                     <div
                        v-for="stratum in highlightStrata"
                        :key="stratum.order"
                        class="bg-white/5 border border-white/10 rounded-2xl p-4 flex items-center justify-between"
                     >
                        <div>
                           <p class="text-xs uppercase tracking-wide text-white/60">{{ stratum.badge }}</p>
                           <p class="text-lg font-bold">{{ stratum.name }}</p>
                           <p class="text-sm text-white/70">厚度 {{ formatNumber(stratum.thickness) }} m · E = {{ formatNumber(stratum.elasticModulus) }} GPa</p>
                        </div>
                        <div class="text-right">
                           <p class="text-xs text-emerald-300">Feasibility {{ stratum.feasibility }}</p>
                           <p class="text-sm text-white/60">MI {{ formatNumber(stratum.mechanicalIndex) }}</p>
                        </div>
                     </div>
                  </div>
               </div>
            </div>
         </section>

         <!-- Modeling Section -->
         <section id="modeling" class="max-w-7xl mx-auto px-6 lg:px-12 py-16 grid grid-cols-1 lg:grid-cols-2 gap-10">
            <div class="rounded-3xl border border-slate-100 bg-white shadow-xl p-8 relative overflow-hidden">
               <div class="absolute -top-16 -right-16 w-56 h-56 bg-gradient-primary rounded-full blur-3xl opacity-20"></div>
               <div class="relative">
                  <p class="text-xs font-semibold text-slate-500 uppercase tracking-widest">三维建模剖面</p>
                  <h3 class="text-3xl font-bold text-slate-900 mt-2">Layered Geological Block</h3>
                  <p class="text-slate-500 mt-4">利用真实层序参数驱动 Kriging / IDW 插值内核。模型自动拼装顶板层，满足 FLAC3D 平坦边界施加载荷要求。</p>
                  <div class="mt-10 flex justify-center">
                     <div class="relative w-64 h-64" style="perspective: 1200px;">
                        <div class="absolute inset-0" style="transform-style: preserve-3d; animation: spin 18s linear infinite;">
                           <div
                              v-for="(layer, idx) in modeledLayers"
                              :key="layer.name + idx"
                              class="absolute left-1/2 -translate-x-1/2 w-48 rounded-3xl border border-white/40 shadow-lg flex items-center justify-center text-xs font-bold text-white"
                              :style="{
                                 height: `${28 + idx * 4}px`,
                                 transform: `translateZ(${idx * 18}px)`
                              }"
                              :class="layer.className"
                           >
                              {{ layer.label }}
                           </div>
                        </div>
                     </div>
                  </div>
               </div>
            </div>
            <div class="rounded-3xl border border-slate-100 bg-white shadow-xl p-8 space-y-4">
               <div class="flex items-center justify-between">
                  <div>
                     <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">层序展开</p>
                     <h3 class="text-2xl font-bold text-slate-900">{{ selectedHole.id }} 层位表</h3>
                  </div>
                  <Box :size="30" class="text-emerald-500" />
               </div>
               <div class="max-h-[420px] overflow-y-auto space-y-3 pr-2 custom-scroll">
                  <div
                     v-for="layer in layerStack"
                     :key="layer.order"
                     class="flex items-center justify-between p-4 rounded-2xl border"
                     :class="layer.name.includes('煤') ? 'bg-amber-50 border-amber-100' : 'bg-slate-50 border-slate-100'"
                  >
                     <div>
                        <p class="text-sm font-bold text-slate-800">{{ layer.name }}</p>
                        <p class="text-xs text-slate-500">{{ layer.depthTop }}m → {{ layer.depthBottom }}m</p>
                     </div>
                     <div class="text-right">
                        <p class="text-sm font-semibold text-slate-700">{{ layer.thickness }}m</p>
                        <p class="text-xs text-slate-400">E {{ layer.elasticModulus }} GPa</p>
                     </div>
                  </div>
               </div>
            </div>
         </section>

         <!-- Pressure Prediction -->
         <section id="prediction" class="bg-slate-900 text-white py-16">
            <div class="max-w-7xl mx-auto px-6 lg:px-12 grid grid-cols-1 lg:grid-cols-2 gap-10">
               <div>
                  <p class="text-xs font-semibold text-white/60 uppercase tracking-[0.3em]">ST-GCN & Ensemble</p>
                  <h3 class="text-3xl font-bold mt-2">支架压力智能预测</h3>
                  <p class="mt-4 text-white/70">融合静态地质特征（砂岩厚度、关键层强度）与动态监测曲线，实时预测支架阻力峰值位置与回落趋势。</p>
                  <div class="mt-8 grid grid-cols-2 gap-4">
                     <div class="bg-white/5 border border-white/10 rounded-2xl p-4">
                        <p class="text-xs text-white/60 uppercase tracking-wide">预测峰值</p>
                        <p class="text-3xl font-black text-emerald-300 mt-2">{{ peakPressure.predicted }} kN</p>
                     </div>
                     <div class="bg-white/5 border border-white/10 rounded-2xl p-4">
                        <p class="text-xs text-white/60 uppercase tracking-wide">实测峰值</p>
                        <p class="text-3xl font-black text-white mt-2">{{ peakPressure.actual }} kN</p>
                     </div>
                  </div>
                  <div class="mt-8 bg-white/5 rounded-2xl border border-white/10 p-4">
                     <p class="text-xs text-white/60 uppercase tracking-wide">煤厚 vs. 阻力</p>
                     <div class="mt-4 space-y-2">
                        <div v-for="item in coalTrendTop" :key="item.id" class="flex items-center gap-3">
                           <span class="w-12 text-xs font-mono text-white/60">{{ item.id }}</span>
                           <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                              <div class="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-300" :style="{ width: `${item.normalized}%` }"></div>
                           </div>
                           <span class="text-xs font-bold text-white/80">{{ item.coalThickness }}m</span>
                        </div>
                     </div>
                  </div>
               </div>
               <div class="rounded-3xl bg-white text-slate-900 p-8 border border-white/20 shadow-2xl">
                  <div class="flex items-center justify-between">
                     <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-widest">支架阻力曲线</p>
                        <h3 class="text-2xl font-bold text-slate-900 mt-2">工作面时间序列</h3>
                     </div>
                     <TrendingUp :size="32" class="text-blue-500" />
                  </div>
                  <div class="mt-6">
                     <svg width="620" height="220" viewBox="0 0 620 220" class="w-full">
                        <path :d="pressureActualPath" fill="none" stroke="#2563eb" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" />
                        <path :d="pressurePredPath" fill="none" stroke="#f97316" stroke-width="3" stroke-dasharray="6 6" stroke-linecap="round" />
                     </svg>
                     <div class="flex justify-between text-xs text-slate-400 mt-2">
                        <span v-for="point in pressureSeries" :key="point.step">{{ point.step }}</span>
                     </div>
                  </div>
                  <div class="mt-6 grid grid-cols-2 gap-4 text-sm">
                     <div class="bg-slate-50 rounded-2xl p-4">
                        <p class="text-xs text-slate-500 uppercase tracking-wide">预测误差</p>
                        <p class="text-xl font-black text-slate-900 mt-1">± {{ peakPressure.error }} kN</p>
                     </div>
                     <div class="bg-slate-50 rounded-2xl p-4">
                        <p class="text-xs text-slate-500 uppercase tracking-wide">采场安全状态</p>
                        <p class="text-xl font-black text-emerald-500 mt-1">稳定</p>
                     </div>
                  </div>
               </div>
            </div>
         </section>

         <!-- Architecture -->
         <section id="architecture" class="max-w-7xl mx-auto px-6 lg:px-12 py-16">
            <div class="text-center mb-12">
               <p class="text-xs font-semibold text-slate-400 uppercase tracking-[0.35em]">Architecture</p>
               <h3 class="text-3xl font-bold text-slate-900 mt-3">技术栈与模块划分</h3>
               <p class="text-slate-500 mt-4">前后端完全容器化，可在服务器与本地一键部署；数据资产通过 Pinia & IndexedDB 长期缓存。</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
               <div v-for="card in techStacks" :key="card.title" class="rounded-3xl border border-slate-100 bg-white shadow-lg p-6 space-y-4">
                  <div class="w-10 h-10 rounded-2xl" :class="card.iconBg">
                     <component :is="card.icon" :size="20" class="text-white" />
                  </div>
                  <h4 class="text-xl font-bold text-slate-900">{{ card.title }}</h4>
                  <ul class="space-y-1 text-sm text-slate-500">
                     <li v-for="item in card.items" :key="item">• {{ item }}</li>
                  </ul>
               </div>
            </div>
         </section>
      </div>
   </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
   Activity,
   TrendingUp,
   Layers,
   MapPin,
   Box,
   Database,
   Share2,
   Github,
   Mail,
} from 'lucide-vue-next'
import GlassButton from '../components/helios/GlassButton.vue'
import {
   boreholes,
   summary as datasetSummary,
   coordinateSeries,
   buildSubsidenceProfile,
   buildPressureSeries,
   getLayerStack,
   getBorehole,
   getCoalThicknessTrend,
} from '@/data'

const router = useRouter()
const holeOptions = boreholes.map((hole) => hole.id)
const selectedHoleId = ref(holeOptions[0])

const selectedHole = computed(() => getBorehole(selectedHoleId.value) || boreholes[0])
const subsidenceProfile = computed(() => buildSubsidenceProfile(selectedHoleId.value))
const pressureSeries = computed(() => buildPressureSeries(selectedHoleId.value))
const layerStack = computed(() => getLayerStack(selectedHoleId.value))

const highlightStrata = computed(() =>
   (selectedHole.value?.keyStrataCandidates || []).map((layer, idx) => ({
      ...layer,
      badge: `SK${idx + 1}`,
      feasibility: idx === 0 ? 'V' : idx === 1 ? 'IV' : 'III',
   })),
)

const summaryCards = [
   { label: '钻孔数量', value: datasetSummary.boreholeCount, hint: '多孔位并行计算' },
   {
      label: '平均剖面厚度',
      value: `${formatNumber(datasetSummary.averageThickness)} m`,
      hint: '支撑概率积分参数',
   },
   {
      label: '最大剖面厚度',
      value: `${formatNumber(datasetSummary.maxThickness)} m`,
      hint: '用于边界条件设置',
   },
   { label: '煤层段数', value: datasetSummary.totalCoalLayers, hint: '覆盖 5-7 号煤层段' },
]

const chartSize = { width: 620, height: 220 }
const subsidenceAreaPath = computed(() => buildAreaPath(subsidenceProfile.value, chartSize))
const subsidenceLine = computed(() => buildLinePath(subsidenceProfile.value, chartSize))

const pressureActualPath = computed(() => buildLinePath(pressureSeries.value, chartSize, 'actual'))
const pressurePredPath = computed(() => buildLinePath(pressureSeries.value, chartSize, 'predicted'))

const maxSubsidence = computed(() => {
   if (!subsidenceProfile.value.length) return '0.00'
   const min = Math.min(...subsidenceProfile.value.map((p) => p.z))
   return Math.abs(min).toFixed(2)
})

const coalTrend = computed(() => getCoalThicknessTrend())
const coalTrendTop = computed(() => {
   const maxValue = Math.max(...coalTrend.value.map((item) => item.coalThickness)) || 1
   return coalTrend.value
      .slice()
      .sort((a, b) => b.coalThickness - a.coalThickness)
      .slice(0, 5)
      .map((item) => ({
         ...item,
         normalized: Number(((item.coalThickness / maxValue) * 100).toFixed(1)),
      }))
})

const peakPressure = computed(() => {
   if (!pressureSeries.value.length) {
      return { predicted: 0, actual: 0, error: 0 }
   }
   const actual = Math.max(...pressureSeries.value.map((p) => p.actual))
   const predicted = Math.max(...pressureSeries.value.map((p) => p.predicted))
   return {
      actual,
      predicted,
      error: Math.abs(actual - predicted),
   }
})

const modeledLayers = computed(() => {
   const strata = highlightStrata.value
   if (!strata.length) return []
   return strata.map((layer, idx) => ({
      label: `${layer.name} (${layer.thickness}m)`,
      className: idx === 0 ? 'bg-gradient-to-r from-blue-500 to-cyan-400' : idx === 1 ? 'bg-gradient-to-r from-emerald-400 to-lime-400' : 'bg-gradient-to-r from-slate-500 to-slate-400',
   }))
})

const techStacks = [
   {
      title: 'Frontend · 可视化',
      icon: Database,
      iconBg: 'bg-blue-500',
      items: ['Vue 3 + Pinia', 'Tailwind CSS', 'ECharts Lite (自绘 SVG)', 'Lucide Icon System'],
   },
   {
      title: 'Backend · 算法',
      icon: Share2,
      iconBg: 'bg-teal-500',
      items: ['FastAPI/Flask 微服务', 'Pandas + NumPy', 'Kriging / IDW 内核', 'ST-GCN 预测器'],
   },
   {
      title: '数据通道',
      icon: Github,
      iconBg: 'bg-purple-500',
      items: ['内置 CSV/JSON', '任务队列缓存', '自动清洗与归一化', 'FLAC3D STL 导出'],
   },
   {
      title: '运维部署',
      icon: Mail,
      iconBg: 'bg-amber-500',
      items: ['Docker Compose', 'Nginx 反向代理', '负载探针', '实时日志通道'],
   },
]

const mapBounds = computed(() => {
   if (!coordinateSeries.length) {
      return null
   }
   const xs = coordinateSeries.map((p) => p.x)
   const ys = coordinateSeries.map((p) => p.y)
   const minX = Math.min(...xs)
   const maxX = Math.max(...xs)
   const minY = Math.min(...ys)
   const maxY = Math.max(...ys)
   return {
      minX,
      maxX,
      minY,
      maxY,
      spanX: maxX - minX || 1,
      spanY: maxY - minY || 1,
   }
})

const mappedPoints = computed(() => {
   const bounds = mapBounds.value
   if (!bounds) {
      return []
   }
   const { minX, spanX, maxY, spanY } = bounds
   return coordinateSeries.map((point) => ({
      ...point,
      left: (((point.x - minX) / spanX) * 80 + 10).toFixed(2),
      top: (((maxY - point.y) / spanY) * 80 + 10).toFixed(2),
   }))
})

const mapMetrics = computed(() => {
   const bounds = mapBounds.value
   if (!bounds) {
      return { spanX: 0, spanY: 0 }
   }
   return {
      spanX: Math.round(bounds.spanX),
      spanY: Math.round(bounds.spanY),
   }
})

function formatNumber(value) {
   if (value === undefined || value === null) return '0.00'
   return Number(value).toFixed(2)
}

function buildAreaPath(points, size) {
   if (!points.length) return ''
   const { width, height } = size
   const xs = points.map((p) => p.x)
   const zs = points.map((p) => p.z)
   const minX = Math.min(...xs)
   const maxX = Math.max(...xs)
   const minZ = Math.min(...zs)
   const maxZ = Math.max(...zs)
   const rangeX = maxX - minX || 1
   const rangeZ = maxZ - minZ || 1

   const coords = points.map((p, idx) => {
      const x = ((p.x - minX) / rangeX) * width
      const y = height - ((p.z - minZ) / rangeZ) * height
      return `${idx === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`
   })
   coords.push(`L${width},${height}`)
   coords.push(`L0,${height}Z`)
   return coords.join(' ')
}

function buildLinePath(points, size, key = 'z') {
   if (!points.length) return ''
   const { width, height } = size
   const xs = points.map((_, idx) => idx)
   const ys = points.map((p) => p[key])
   const maxIndex = xs[xs.length - 1] || 1
   const minY = Math.min(...ys)
   const maxY = Math.max(...ys)
   const rangeY = maxY - minY || 1
   return points
      .map((p, idx) => {
         const x = (idx / maxIndex) * width
         const y = height - ((p[key] - minY) / rangeY) * height
         return `${idx === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`
      })
      .join(' ')
}

const goToConsole = () => router.push('/tools')
const scrollToSection = (id) => {
   const el = document.getElementById(id)
   if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
   }
}
</script>

<style scoped>
@keyframes spin {
   from {
      transform: rotateX(12deg) rotateY(-16deg) rotate(0deg);
   }
   to {
      transform: rotateX(12deg) rotateY(-16deg) rotate(360deg);
   }
}

.custom-scroll::-webkit-scrollbar {
   width: 6px;
}
.custom-scroll::-webkit-scrollbar-thumb {
   background: rgba(148, 163, 184, 0.4);
   border-radius: 999px;
}
.text-gradient-primary {
   background: linear-gradient(135deg, #2563eb, #06b6d4);
   -webkit-background-clip: text;
   -webkit-text-fill-color: transparent;
}
</style>
