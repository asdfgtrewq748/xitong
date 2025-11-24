<template>
  <div class="min-h-screen w-full px-8 py-8 animate-fadeIn bg-slate-50">
    <!-- Page Header -->
    <div class="flex items-end justify-between mb-8">
      <div>
        <h2 class="text-3xl font-black text-slate-900">采掘设计功能</h2>
        <p class="text-slate-500 mt-2 font-medium">智能化矿井采掘方案设计与规程生成</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="hidden md:flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-xl text-sm font-medium text-slate-600 border border-slate-200">
          <Cpu :size="16" class="text-violet-500" /> AI 引擎 V2.4
        </div>
        <button class="px-4 py-2 font-bold text-sm transition-all duration-300 rounded-xl flex items-center gap-2 bg-white text-slate-600 border border-slate-200 hover:border-violet-300 hover:text-violet-600 hover:shadow-lg hover:shadow-violet-100">
          <Save :size="16" />
          <span>保存项目</span>
        </button>
      </div>
    </div>

    <div class="flex gap-6 relative min-h-[calc(100vh-220px)]">
      <!-- LEFT: Parameters Panel -->
      <div :class="['transition-all duration-300 flex-shrink-0 h-full', leftPanelOpen ? 'w-80' : 'w-0 overflow-hidden']">
        <div class="glass-panel rounded-2xl flex flex-col overflow-hidden shadow-lg h-full">
          <div class="p-6 border-b border-slate-200 bg-white/60 flex justify-between items-center">
            <span class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <Settings :size="18" class="text-violet-500" /> 地质参数设定
            </span>
            <button @click="leftPanelOpen = false" class="text-slate-400 hover:text-violet-600 transition-colors">
              <X :size="18" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scroll">
            <section v-for="group in parameterGroups" :key="group.title" class="bg-white/60 p-4 rounded-xl border border-slate-200 shadow-sm">
              <h3 class="text-xs font-bold text-slate-600 uppercase mb-4 flex items-center gap-2">
                <component :is="group.icon" :size="16" /> {{ group.title }}
              </h3>
              <div v-if="group.highlight" class="flex items-center gap-2 bg-amber-50 p-3 rounded-lg border border-amber-200 mb-4">
                <component :is="group.highlight.icon" :size="14" class="text-amber-600" />
                <span class="text-sm font-bold text-amber-800">{{ group.highlight.text }}</span>
              </div>
              <div v-for="field in group.fields" :key="field.key" class="mb-5">
                <div class="flex justify-between mb-2">
                  <label class="text-sm font-semibold text-slate-700">{{ field.label }}</label>
                  <span class="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    {{ field.min }}-{{ field.max }}{{ field.unit }}
                  </span>
                </div>
                <div class="relative">
                  <input
                    type="number"
                    v-model.number="parameterValues[field.key]"
                    class="glass-input w-full px-4 py-2.5 rounded-lg text-sm font-mono text-slate-800"
                  />
                  <span class="absolute right-4 top-2.5 text-sm text-slate-500 font-medium pointer-events-none select-none">{{ field.unit }}</span>
                </div>
              </div>
            </section>
          </div>

          <div class="p-6 bg-white/80 border-t border-slate-200">
            <button
              @click="handleGenerate"
              class="w-full py-3.5 rounded-xl bg-gradient-primary text-white font-bold text-base shadow-xl shadow-indigo-500/30 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-2 relative overflow-hidden group"
              :disabled="isGenerating"
            >
              <template v-if="isGenerating">
                <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                <span>AI 计算中...</span>
              </template>
              <template v-else>
                <Sparkles :size="18" class="animate-pulse" />
                <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
                <span class="relative z-10">生成设计规程</span>
                <ArrowRight :size="18" class="group-hover:translate-x-1 transition-transform relative z-10" />
              </template>
            </button>
          </div>
        </div>
      </div>

      <button
        v-if="!leftPanelOpen"
        @click="leftPanelOpen = true"
        class="fixed left-8 top-24 z-20 p-3 bg-white/90 backdrop-blur border border-slate-200 rounded-xl shadow-lg text-slate-600 hover:text-violet-600 transition-all hover:scale-105"
        title="打开参数面板"
      >
        <PanelLeftOpen :size="22" />
      </button>

      <main class="flex-1 glass-panel rounded-2xl overflow-hidden shadow-lg relative flex flex-col min-h-[calc(100vh-220px)] min-w-0">
        <div class="absolute top-4 left-1/2 -translate-x-1/2 glass-panel px-5 py-2.5 rounded-xl shadow-sm flex items-center gap-4 z-10 border border-slate-200">
          <button class="p-2 hover:bg-violet-50 rounded-lg text-slate-600 hover:text-violet-600 transition-colors">
            <MousePointer2 :size="20" />
          </button>
          <button class="p-2 hover:bg-violet-50 rounded-lg text-slate-600 hover:text-violet-600 transition-colors">
            <Move :size="20" />
          </button>
          <div class="w-px h-6 bg-slate-200"></div>
          <button class="p-2 hover:bg-violet-50 rounded-lg text-slate-600 hover:text-violet-600 transition-colors">
            <PenTool :size="20" />
          </button>
          <button class="p-2 hover:bg-violet-50 rounded-lg text-slate-600 hover:text-violet-600 transition-colors">
            <Ruler :size="20" />
          </button>
          <div class="w-px h-6 bg-slate-200"></div>
          <button class="p-2 hover:bg-violet-50 rounded-lg text-slate-600 hover:text-violet-600 transition-colors">
            <Maximize2 :size="20" />
          </button>
        </div>

        <div class="flex-1 relative cad-grid flex items-center justify-center overflow-hidden cursor-crosshair w-full h-full">
          <svg width="0" height="0" class="absolute">
            <defs>
              <pattern id="hatch" patternUnits="userSpaceOnUse" width="4" height="4" patternTransform="rotate(45)">
                <line x1="0" y1="0" x2="0" y2="4" stroke="#94a3b8" stroke-width="1" />
              </pattern>
              <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <path d="M0,0 L6,3 L0,6 L0,0" fill="#64748b" />
              </marker>
            </defs>
          </svg>

          <div class="absolute top-6 left-6 flex flex-col gap-1 text-xs font-mono text-slate-500 select-none pointer-events-none bg-white/90 backdrop-blur px-3 py-2 rounded-lg border border-slate-200 shadow-sm">
            <span>视图: 顶视图_01</span>
            <span>比例: 1:2000</span>
            <span>单位: 公制 (m)</span>
          </div>

          <div class="absolute bottom-6 left-6 text-xs font-mono text-slate-500 pointer-events-none bg-white/90 backdrop-blur px-3 py-2 rounded-lg border border-slate-200 shadow-sm">
            X: 4291.22 Y: 8821.05 Z: -450.00
          </div>

          <div :class="['relative w-full h-full p-16 transition-all duration-1000', isGenerating ? 'opacity-60 blur-[1px] scale-95' : 'opacity-100 scale-100']">
            <template v-if="showResult">
              <svg class="w-full h-full drop-shadow-lg" viewBox="0 0 800 600" preserveAspectRatio="xMidYMid meet">
                <line x1="50" y1="300" x2="750" y2="300" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="10,5" />
                <line x1="400" y1="50" x2="400" y2="550" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="10,5" />

                <g class="blueprint-line">
                  <rect x="100" y="150" width="600" height="300" fill="none" stroke="#334155" stroke-width="1.5" />

                  <g transform="translate(150, 300)">
                    <circle r="15" fill="none" stroke="#0f172a" stroke-width="2" />
                    <line x1="-20" y1="0" x2="20" y2="0" stroke="#0f172a" stroke-width="1" />
                    <line x1="0" y1="-20" x2="0" y2="20" stroke="#0f172a" stroke-width="1" />
                    <text x="25" y="5" class="text-xs fill-slate-700 font-semibold font-mono">主井</text>
                  </g>

                  <g transform="translate(250, 300)">
                    <circle r="12" fill="none" stroke="#0f172a" stroke-width="2" stroke-dasharray="4,2" />
                    <line x1="-16" y1="0" x2="16" y2="0" stroke="#0f172a" stroke-width="1" />
                    <line x1="0" y1="-16" x2="0" y2="16" stroke="#0f172a" stroke-width="1" />
                    <text x="20" y="5" class="text-xs fill-slate-700 font-semibold font-mono">副井</text>
                  </g>

                  <path d="M 150 300 L 150 200 L 650 200 L 650 400 L 150 400 L 150 300" fill="none" stroke="#334155" stroke-width="1.5" />

                  <rect x="350" y="200" width="100" height="200" fill="url(#hatch)" stroke="#334155" stroke-width="1" />
                  <rect x="500" y="200" width="100" height="200" fill="url(#hatch)" stroke="#334155" stroke-width="1" />

                  <line x1="350" y1="420" x2="450" y2="420" stroke="#64748b" stroke-width="1" marker-start="url(#arrow)" marker-end="url(#arrow)" />
                  <line x1="350" y1="415" x2="350" y2="425" stroke="#64748b" stroke-width="1" />
                  <line x1="450" y1="415" x2="450" y2="425" stroke="#64748b" stroke-width="1" />
                  <text x="400" y="435" text-anchor="middle" class="text-xs fill-slate-600 font-mono font-semibold">100m 工作面</text>

                  <text x="400" y="300" text-anchor="middle" class="text-sm fill-slate-900 font-bold font-mono bg-white px-1">工作面-101</text>
                  <text x="550" y="300" text-anchor="middle" class="text-sm fill-slate-900 font-bold font-mono bg-white px-1">工作面-102</text>
                </g>

                <g class="opacity-80">
                  <path d="M 160 210 L 340 210" stroke="#0ea5e9" stroke-width="1.5" stroke-dasharray="4,2" marker-end="url(#arrow)" />
                  <path d="M 460 390 L 640 390" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,2" marker-end="url(#arrow)" />
                </g>
              </svg>
            </template>
            <template v-else>
              <div class="flex flex-col items-center justify-center h-full text-slate-400">
                <div class="w-28 h-28 border-2 border-dashed border-slate-300 rounded-full flex items-center justify-center mb-6 bg-slate-50">
                  <Move :size="40" class="text-slate-400" />
                </div>
                <p class="text-base font-semibold text-slate-500">暂无设计方案</p>
                <p class="text-sm text-slate-400 mt-2">请在左侧设置参数并生成布局</p>
              </div>
            </template>

            <div v-if="isGenerating" class="absolute inset-0 flex flex-col items-center justify-center bg-white/70 backdrop-blur-sm z-20">
              <div class="w-20 h-20 border-4 border-violet-200 border-t-violet-600 rounded-full animate-spin mb-6"></div>
              <div class="text-violet-600 font-bold text-base animate-pulse">AI 设计引擎计算中...</div>
            </div>
          </div>
        </div>
      </main>

      <aside
        :class="['transition-all duration-300 flex-shrink-0 h-full', rightPanelOpen ? 'w-96 ml-6' : 'w-0 overflow-hidden ml-0']"
      >
        <div class="glass-panel rounded-2xl flex flex-col overflow-hidden shadow-lg h-full">
          <div class="h-16 border-b border-slate-200 flex items-center justify-between px-6 bg-white/80">
            <div class="flex items-center gap-2">
              <FileText class="text-cyan-600" :size="20" />
              <h2 class="text-base font-bold text-slate-800">设计说明书</h2>
            </div>
            <button @click="rightPanelOpen = false" class="text-slate-400 hover:text-violet-600 transition-colors">
              <PanelRightClose :size="20" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-6 custom-scroll">
            <template v-if="showResult">
              <div class="space-y-8 animate-fadeIn">
                <div class="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-start gap-3 shadow-sm">
                  <CheckCircle2 :size="20" class="text-emerald-600 mt-0.5 shrink-0" />
                  <div>
                    <div class="text-sm font-bold text-emerald-800">规程已生成</div>
                    <p class="text-xs text-emerald-700 leading-relaxed mt-1">基于地质参数 V2.4 模型优化完毕。</p>
                  </div>
                </div>

                <div>
                  <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4 border-b border-slate-200 pb-2">01. 矿井开拓</h3>
                  <div class="space-y-2">
                    <div v-for="item in mineDevelopmentSpecs" :key="item.label" class="flex justify-between items-center py-2.5 border-b border-slate-100 last:border-0">
                      <span class="text-sm text-slate-600">{{ item.label }}</span>
                      <span class="text-sm font-bold text-slate-900 font-mono text-right select-all">{{ item.value }}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4 border-b border-slate-200 pb-2">02. 采煤工艺</h3>
                  <p class="text-sm text-slate-700 leading-relaxed mb-4 bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                    基于煤层厚度分析,推荐采用 <span class="font-bold text-violet-600">综采一次采全高</span> 工艺。
                  </p>
                  <div class="space-y-2">
                    <div v-for="item in miningProcessSpecs" :key="item.label" class="flex justify-between items-center py-2.5 border-b border-slate-100 last:border-0">
                      <span class="text-sm text-slate-600">{{ item.label }}</span>
                      <span class="text-sm font-bold text-slate-900 font-mono text-right select-all">{{ item.value }}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4 border-b border-slate-200 pb-2">03. 安全专篇</h3>
                  <div class="bg-amber-50 p-4 rounded-lg border border-amber-200">
                    <div class="flex gap-2 mb-2 text-amber-700 font-bold text-sm items-center">
                      <Zap :size="16" /> 高瓦斯防治措施
                    </div>
                    <p class="text-sm text-amber-800 leading-relaxed">
                      强制执行 "U+L" 型通风方式,并在工作面回风巷设置专用回风巷。
                    </p>
                  </div>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="h-full flex flex-col items-center justify-center text-slate-300 space-y-4">
                <div class="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center border border-slate-200">
                  <FileText :size="40" class="text-slate-300" />
                </div>
                <div class="text-center">
                  <p class="text-base font-bold text-slate-500">待生成</p>
                  <p class="text-sm mt-2 text-slate-400">请在左侧设置参数并点击生成</p>
                </div>
              </div>
            </template>
          </div>

          <div class="p-6 border-t border-slate-200 bg-white/90 flex flex-col gap-3">
            <button class="px-6 py-3 font-bold text-base transition-all duration-300 rounded-xl flex items-center justify-center gap-2 bg-gradient-primary text-white shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40 hover:-translate-y-0.5 w-full">
              <Download :size="18" class="text-white" />
              <span>下载完整规程 (PDF)</span>
            </button>
            <div class="grid grid-cols-2 gap-3">
              <button class="px-4 py-2.5 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 bg-white text-slate-600 border border-slate-200 hover:border-violet-300 hover:text-violet-600 hover:shadow-md">
                <Printer :size="16" />
                <span>打印</span>
              </button>
              <button class="px-4 py-2.5 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 bg-white text-slate-600 border border-slate-200 hover:border-violet-300 hover:text-violet-600 hover:shadow-md">
                <Share2 :size="16" />
                <span>分享</span>
              </button>
            </div>
          </div>
        </div>
      </aside>

      <button
        v-if="!rightPanelOpen"
        @click="rightPanelOpen = true"
        class="fixed right-8 top-24 z-20 p-3 bg-white/90 backdrop-blur border border-slate-200 rounded-xl shadow-lg text-slate-600 hover:text-violet-600 transition-all hover:scale-105"
        title="打开报告面板"
      >
        <PanelRightOpen :size="22" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import {
  Layers,
  Settings,
  CheckCircle2,
  Cpu,
  Ruler,
  PenTool,
  FileText,
  Download,
  Sparkles,
  Zap,
  Maximize2,
  Printer,
  Share2,
  Save,
  ArrowRight,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  X,
  MousePointer2,
  Move,
} from 'lucide-vue-next';

const isGenerating = ref(false);
const showResult = ref(false);
const leftPanelOpen = ref(true);
const rightPanelOpen = ref(true);

const parameterValues = reactive({
  avgDepth: 450,
  seamThickness: 3.5,
  seamDip: 5,
  roofHardness: 6.5,
  floorPressure: 2.4,
  gasEmission: 4.2,
});

const parameterGroups = [
  {
    title: '煤层条件',
    icon: Layers,
    fields: [
      { key: 'avgDepth', label: '平均埋深', unit: 'm', min: 100, max: 1200 },
      { key: 'seamThickness', label: '煤层厚度', unit: 'm', min: 0.8, max: 20 },
      { key: 'seamDip', label: '煤层倾角', unit: '°', min: 0, max: 45 },
    ],
  },
  {
    title: '岩石力学',
    icon: Ruler,
    fields: [
      { key: 'roofHardness', label: '顶板硬度 (f)', unit: '', min: 1, max: 12 },
      { key: 'floorPressure', label: '底板比压', unit: 'MPa', min: 0.5, max: 10 },
    ],
  },
  {
    title: '灾害指标',
    icon: Zap,
    highlight: { text: '高瓦斯矿井', icon: Zap },
    fields: [{ key: 'gasEmission', label: '瓦斯涌出', unit: 'm³/t', min: 0, max: 30 }],
  },
];

const mineDevelopmentSpecs = [
  { label: '开拓类型', value: '立井多水平' },
  { label: '主井深度', value: '482.5 m' },
  { label: '年产量', value: '4.00 Mt/a' },
];

const miningProcessSpecs = [
  { label: '支架选型', value: 'ZY12000/28/62D' },
  { label: '采高范围', value: '2.8 - 6.2 m' },
];

const handleGenerate = () => {
  if (isGenerating.value) {
    return;
  }
  isGenerating.value = true;
  setTimeout(() => {
    isGenerating.value = false;
    showResult.value = true;
  }, 2500);
};
</script>

<style scoped>
@keyframes draw-line {
  to {
    stroke-dashoffset: 0;
  }
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.glass-panel {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 4px 24px 0 rgba(31, 38, 135, 0.08);
}

.glass-card-hover:hover {
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.12);
  transform: translateY(-2px);
}

.glass-input {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(203, 213, 225, 0.8);
  transition: all 0.3s ease;
}

.glass-input:focus {
  background: rgba(255, 255, 255, 1);
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
  outline: none;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
}

.cad-grid {
  background-size: 40px 40px;
  background-image: linear-gradient(to right, rgba(99, 102, 241, 0.05) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(99, 102, 241, 0.05) 1px, transparent 1px);
  background-color: #fff;
}

.blueprint-line {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: draw-line 2s ease-out forwards;
}

.custom-scroll::-webkit-scrollbar {
  width: 8px;
}

.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(99, 102, 241, 0.2);
  border-radius: 20px;
}

.custom-scroll::-webkit-scrollbar-thumb:hover {
  background-color: rgba(99, 102, 241, 0.3);
}

.animate-fadeIn {
  animation: fadeIn 0.5s ease forwards;
}
</style>
