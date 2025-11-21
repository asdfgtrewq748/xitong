<template>
  <div class="container mx-auto px-8 py-12 animate-fadeIn">
     <div class="flex items-end justify-between mb-10">
        <div>
           <h2 class="text-3xl font-black text-slate-900">工作台</h2>
           <p class="text-slate-500 mt-2 font-medium">高精度分析工具与远程遥测终端</p>
        </div>
     </div>

     <!-- Metrics Grid -->
     <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <div class="glass-panel glass-card-hover p-6 rounded-2xl transition-all duration-500 group relative overflow-hidden animate-fadeIn" style="animation-delay: 0ms">
           <div class="flex justify-between items-start mb-4">
              <div class="p-3 bg-slate-50 rounded-xl text-slate-400 group-hover:text-white group-hover:bg-gradient-primary transition-all duration-300 shadow-inner">
                 <Database :size="24" />
              </div>
              <span class="flex h-3 w-3 relative">
                 <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                 <span class="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
              </span>
           </div>
           <h3 class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">钻孔数据</h3>
           <div class="flex items-baseline gap-2">
              <div class="text-3xl font-black text-slate-800 mb-2 tracking-tight">{{ totalBoreholes }}</div>
           </div>
           <div class="flex items-center justify-between">
              <div class="text-xs text-slate-500 font-medium bg-slate-50/80 inline-block px-2 py-1 rounded-md border border-slate-100">
                 已导入
              </div>
              <span class="text-xs font-bold text-emerald-500 flex items-center">+12% <Activity :size="10" class="ml-1"/></span>
           </div>
        </div>

        <div class="glass-panel glass-card-hover p-6 rounded-2xl transition-all duration-500 group relative overflow-hidden animate-fadeIn" style="animation-delay: 100ms">
           <div class="flex justify-between items-start mb-4">
              <div class="p-3 bg-slate-50 rounded-xl text-slate-400 group-hover:text-white group-hover:bg-gradient-primary transition-all duration-300 shadow-inner">
                 <Layers :size="24" />
              </div>
              <span class="flex h-3 w-3 relative">
                 <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
           </div>
           <h3 class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">煤层层数</h3>
           <div class="flex items-baseline gap-2">
              <div class="text-3xl font-black text-slate-800 mb-2 tracking-tight">{{ totalCoalSeams }}</div>
           </div>
           <div class="flex items-center justify-between">
              <div class="text-xs text-slate-500 font-medium bg-slate-50/80 inline-block px-2 py-1 rounded-md border border-slate-100">
                 结构完整
              </div>
           </div>
        </div>

        <div class="glass-panel glass-card-hover p-6 rounded-2xl transition-all duration-500 group relative overflow-hidden animate-fadeIn" style="animation-delay: 200ms">
           <div class="flex justify-between items-start mb-4">
              <div class="p-3 bg-slate-50 rounded-xl text-slate-400 group-hover:text-white group-hover:bg-gradient-primary transition-all duration-300 shadow-inner">
                 <Pickaxe :size="24" />
              </div>
              <span class="flex h-3 w-3 relative">
                 <span class="relative inline-flex rounded-full h-3 w-3 bg-violet-500"></span>
              </span>
           </div>
           <h3 class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">矿井数量</h3>
           <div class="flex items-baseline gap-2">
              <div class="text-3xl font-black text-slate-800 mb-2 tracking-tight">{{ totalMines }}</div>
           </div>
           <div class="flex items-center justify-between">
              <div class="text-xs text-slate-500 font-medium bg-slate-50/80 inline-block px-2 py-1 rounded-md border border-slate-100">
                 运行中
              </div>
           </div>
        </div>

        <div class="glass-panel glass-card-hover p-6 rounded-2xl transition-all duration-500 group relative overflow-hidden animate-fadeIn" style="animation-delay: 300ms">
           <div class="flex justify-between items-start mb-4">
              <div class="p-3 bg-slate-50 rounded-xl text-slate-400 group-hover:text-white group-hover:bg-gradient-primary transition-all duration-300 shadow-inner">
                 <Cpu :size="24" />
              </div>
              <span class="flex h-3 w-3 relative">
                 <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                 <span class="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
              </span>
           </div>
           <h3 class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">系统负载</h3>
           <div class="flex items-baseline gap-2">
              <div class="text-3xl font-black text-slate-800 mb-2 tracking-tight">24%</div>
           </div>
           <div class="flex items-center justify-between">
              <div class="text-xs text-slate-500 font-medium bg-slate-50/80 inline-block px-2 py-1 rounded-md border border-slate-100">
                 计算节点正常
              </div>
           </div>
        </div>
     </div>

     <!-- Global Data Import Section -->
     <div class="mb-12 animate-fadeIn" style="animation-delay: 50ms">
        <div class="glass-panel p-8 rounded-[2rem] relative overflow-hidden group cursor-pointer hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-500" @click="router.push('/tools/data-management')">
           <div class="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-bl from-indigo-500/10 to-transparent rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none"></div>
           
           <div class="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
              <div class="flex items-center gap-6">
                 <div class="w-20 h-20 bg-gradient-primary rounded-3xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 group-hover:scale-110 transition-transform duration-500">
                    <Database :size="40" />
                 </div>
                 <div>
                    <h2 class="text-2xl font-black text-slate-800 mb-2 group-hover:text-indigo-600 transition-colors">全局数据导入中心</h2>
                    <p class="text-slate-500 text-lg max-w-xl">统一管理钻孔数据、煤层信息与工程参数。支持批量导入、格式校验与自动清洗。</p>
                 </div>
              </div>
              
              <button class="px-8 py-4 bg-white text-indigo-600 font-bold rounded-xl shadow-sm border border-indigo-100 hover:bg-indigo-50 hover:border-indigo-200 transition-all flex items-center gap-3 group-hover:translate-x-2">
                 <span class="text-lg">立即导入</span>
                 <Database :size="20" />
              </button>
           </div>
        </div>
     </div>

     <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Tool: Rock Mechanics Database -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-indigo-50 p-3.5 rounded-2xl text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                 <Layers :size="24" />
              </div>
              <div class="bg-emerald-50 text-emerald-600 border border-emerald-100 px-3 py-1 rounded-full text-xs font-bold">Active</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">岩石力学数据库</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">存储与管理岩石物理力学性质参数，提供智能检索与统计分析功能。</p>
           
           <!-- Visualization: Database Stack Animation -->
           <div class="h-40 flex items-center justify-center mb-8 relative">
              <div class="relative w-32 h-32">
                 <div class="absolute inset-0 bg-indigo-100 rounded-full opacity-20 animate-ping"></div>
                 <div class="absolute inset-0 flex flex-col items-center justify-center gap-2">
                    <div class="w-20 h-6 bg-white border border-indigo-100 rounded-lg shadow-sm transform translate-y-4 opacity-0 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-500 delay-300"></div>
                    <div class="w-24 h-6 bg-white border border-indigo-100 rounded-lg shadow-sm transform translate-y-4 opacity-0 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-500 delay-200"></div>
                    <div class="w-28 h-6 bg-white border border-indigo-100 rounded-lg shadow-sm transform translate-y-4 opacity-0 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-500 delay-100"></div>
                    <div class="w-28 h-6 bg-gradient-primary rounded-lg shadow-lg z-10 flex items-center justify-center">
                       <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    </div>
                 </div>
              </div>
           </div>
           <button @click="router.push('/tools/key-stratum')" class="relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">访问数据库</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Borehole Analysis -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-cyan-50 p-3.5 rounded-2xl text-cyan-600 group-hover:bg-cyan-500 group-hover:text-white transition-colors">
                 <Crosshair :size="24" />
              </div>
              <div class="bg-slate-100 text-slate-500 border border-slate-200 px-3 py-1 rounded-full text-xs font-bold">Standby</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">钻孔数据分析</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">深度解析钻孔数据，自动生成地质剖面图与三维模型预览。</p>
           
           <!-- Map Placeholder -->
           <div class="h-40 bg-slate-50 rounded-3xl border border-slate-200 relative overflow-hidden mb-8 group cursor-crosshair shadow-inner">
              <div class="absolute inset-0 bg-[radial-gradient(#94a3b8_1px,transparent_1px)] [background-size:20px_20px] opacity-30"></div>
              
              <!-- Radar Sweep Effect -->
              <div class="absolute top-1/2 left-1/2 w-[200%] h-[200%] bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent -translate-x-1/2 -translate-y-1/2 rotate-45 animate-[shimmer_3s_infinite_linear]"></div>

              <!-- Pulse Ring Animation -->
              <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 bg-cyan-500/10 rounded-full animate-[pulse-ring_2s_infinite]"></div>
              <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-cyan-500 rounded-full shadow-[0_0_20px_rgba(6,182,212,0.6)] border-2 border-white"></div>
              
              <!-- UI Overlay -->
              <div class="absolute bottom-3 left-4 bg-white/80 backdrop-blur px-2 py-1 rounded text-[10px] font-mono text-slate-500 border border-slate-200">
                 DEPTH: 842.5m / AZM: 11.20
              </div>
           </div>
           <button @click="router.push('/tools/borehole-analysis')" class="relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">开始分析</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Upward Mining -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-amber-50 p-3.5 rounded-2xl text-amber-600 group-hover:bg-amber-500 group-hover:text-white transition-colors">
                 <Pickaxe :size="24" />
              </div>
              <div class="bg-slate-100 text-slate-500 border border-slate-200 px-3 py-1 rounded-full text-xs font-bold">Ready</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">上行开采可行性</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">评估多煤层开采条件，计算层间距与岩层移动规律。</p>
           
           <div class="h-40 bg-slate-50 rounded-3xl border border-slate-200 relative overflow-hidden mb-8 flex items-center justify-center">
              <div class="w-3/4 h-2 bg-slate-200 rounded-full relative">
                 <div class="absolute top-0 left-0 h-full w-2/3 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full"></div>
                 <div class="absolute -top-8 left-2/3 -translate-x-1/2 bg-white px-2 py-1 rounded shadow text-xs font-bold text-amber-600">Feasible</div>
              </div>
           </div>

           <button @click="router.push('/tools/upward-mining-feasibility')" class="relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">进入评估系统</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Geological Modeling -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-emerald-50 p-3.5 rounded-2xl text-emerald-600 group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                 <Box :size="24" />
              </div>
              <div class="bg-slate-100 text-slate-500 border border-slate-200 px-3 py-1 rounded-full text-xs font-bold">Beta</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">三维地质建模</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">构建高精度三维地质体模型，支持切片查看与体积计算。</p>
           
           <div class="h-40 bg-slate-50 rounded-3xl border border-slate-200 relative overflow-hidden mb-8 flex items-center justify-center group-hover:bg-slate-100 transition-colors">
              <Box :size="48" class="text-slate-300 group-hover:text-emerald-400 transition-colors duration-500" />
           </div>

           <button @click="router.push('/tools/geological-modeling')" class="relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">启动建模</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>
     </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { 
  Activity, 
  Crosshair, 
  Cpu, 
  Database, 
  Layers, 
  Pickaxe, 
  Box 
} from 'lucide-vue-next';

const router = useRouter();

// Mock Data
const totalBoreholes = ref(12);
const totalCoalSeams = ref(8);
const totalMines = ref(5);

</script>

<style scoped>
/* Animations are inherited from global styles or Tailwind config */
</style>
