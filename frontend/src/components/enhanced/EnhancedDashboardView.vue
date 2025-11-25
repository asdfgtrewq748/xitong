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

     <!-- Global Data Import Section - Hero Banner -->
     <div class="mb-12 animate-fadeIn" style="animation-delay: 50ms">
        <div class="relative overflow-hidden rounded-[2rem] bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700 p-1 shadow-2xl shadow-indigo-500/25 group cursor-pointer" @click="router.push('/tools/data-management')">
           <!-- Animated Background -->
           <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23ffffff%22 fill-opacity=%220.05%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-50"></div>
           
           <!-- Glow Effects -->
           <div class="absolute top-0 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
           <div class="absolute bottom-0 right-1/4 w-64 h-64 bg-purple-300/20 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s"></div>
           
           <!-- Inner Card -->
           <div class="relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-[1.75rem] p-8 md:p-10">
              <div class="flex flex-col lg:flex-row items-center justify-between gap-8">
                 <!-- Left: Icon + Text -->
                 <div class="flex items-center gap-6 md:gap-8">
                    <!-- Animated Icon Container -->
                    <div class="relative">
                       <div class="absolute inset-0 bg-white/20 rounded-3xl blur-xl animate-pulse"></div>
                       <div class="relative w-24 h-24 md:w-28 md:h-28 bg-white/20 backdrop-blur rounded-3xl flex items-center justify-center border border-white/30 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500">
                          <Upload :size="48" class="text-white drop-shadow-lg" />
                       </div>
                       <!-- Floating particles -->
                       <div class="absolute -top-2 -right-2 w-4 h-4 bg-yellow-400 rounded-full animate-bounce shadow-lg shadow-yellow-400/50"></div>
                       <div class="absolute -bottom-1 -left-1 w-3 h-3 bg-cyan-400 rounded-full animate-bounce shadow-lg shadow-cyan-400/50" style="animation-delay: 0.5s"></div>
                    </div>
                    
                    <!-- Text Content -->
                    <div class="text-center lg:text-left">
                       <div class="flex items-center gap-3 mb-2 justify-center lg:justify-start">
                          <span class="px-3 py-1 bg-white/20 backdrop-blur rounded-full text-xs font-bold text-white/90 border border-white/20">
                             ⚡ 核心功能
                          </span>
                          <span class="px-3 py-1 bg-emerald-400/20 backdrop-blur rounded-full text-xs font-bold text-emerald-300 border border-emerald-400/30 animate-pulse">
                             推荐使用
                          </span>
                       </div>
                       <h2 class="text-3xl md:text-4xl font-black text-white mb-3 drop-shadow-lg">
                          全局数据导入中心
                       </h2>
                       <p class="text-white/80 text-lg max-w-xl leading-relaxed">
                          统一管理钻孔数据、煤层信息与工程参数<br class="hidden md:block" />
                          支持<span class="text-cyan-300 font-semibold">批量导入</span>、<span class="text-yellow-300 font-semibold">格式校验</span>与<span class="text-emerald-300 font-semibold">自动清洗</span>
                       </p>
                    </div>
                 </div>
                 
                 <!-- Right: CTA Button -->
                 <div class="flex flex-col items-center gap-3">
                    <button class="relative px-10 py-5 bg-white text-indigo-600 font-black text-lg rounded-2xl shadow-xl shadow-black/20 hover:shadow-2xl hover:shadow-black/30 hover:-translate-y-1 active:translate-y-0 transition-all duration-300 flex items-center gap-3 group/btn overflow-hidden">
                       <span class="relative z-10">立即导入数据</span>
                       <ArrowRight :size="24" class="relative z-10 group-hover/btn:translate-x-1 transition-transform" />
                       <div class="absolute inset-0 bg-gradient-to-r from-indigo-100 to-purple-100 translate-y-full group-hover/btn:translate-y-0 transition-transform duration-300"></div>
                    </button>
                    <span class="text-white/60 text-sm">支持 CSV、Excel、JSON 格式</span>
                 </div>
              </div>
              
              <!-- Bottom Stats Bar -->
              <div class="mt-8 pt-6 border-t border-white/10 grid grid-cols-3 gap-4">
                 <div class="text-center">
                    <div class="text-2xl font-black text-white">{{ totalBoreholes }}</div>
                    <div class="text-white/60 text-sm">已导入钻孔</div>
                 </div>
                 <div class="text-center border-x border-white/10">
                    <div class="text-2xl font-black text-white">{{ totalCoalSeams }}</div>
                    <div class="text-white/60 text-sm">煤层数据</div>
                 </div>
                 <div class="text-center">
                    <div class="text-2xl font-black text-white">99.8%</div>
                    <div class="text-white/60 text-sm">数据完整率</div>
                 </div>
              </div>
           </div>
        </div>
     </div>

     <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Tool: Rock Mechanics Database -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden flex flex-col h-full">
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
           <button @click="router.push('/tools/key-stratum')" class="mt-auto relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">访问数据库</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Borehole Analysis -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden flex flex-col h-full">
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
           <button @click="router.push('/tools/borehole-analysis')" class="mt-auto relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">开始分析</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Upward Mining -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden flex flex-col h-full">
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

           <button @click="router.push('/tools/upward-mining-feasibility')" class="mt-auto relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">进入评估系统</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Geological Modeling -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden flex flex-col h-full">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-emerald-50 p-3.5 rounded-2xl text-emerald-600 group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                 <Box :size="24" />
              </div>
              <div class="bg-slate-100 text-slate-500 border border-slate-200 px-3 py-1 rounded-full text-xs font-bold">Beta</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">三维地质建模</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">构建高精度三维地质体模型，支持切片查看与体积计算。</p>
           
           <!-- Visualization: 3D Layers Animation -->
           <div class="h-40 bg-slate-50 rounded-3xl border border-slate-200 relative overflow-hidden mb-8 flex items-center justify-center group-hover:bg-slate-100 transition-colors">
              <div class="relative w-24 h-24">
                 <!-- Bottom Layer -->
                 <div class="absolute inset-x-0 bottom-0 h-12 bg-emerald-200/50 rounded-xl transform scale-90 translate-y-2 group-hover:translate-y-4 transition-transform duration-500"></div>
                 <!-- Middle Layer -->
                 <div class="absolute inset-x-0 bottom-4 h-12 bg-emerald-300/50 rounded-xl transform scale-95 translate-y-1 group-hover:translate-y-0 transition-transform duration-500 delay-75"></div>
                 <!-- Top Layer -->
                 <div class="absolute inset-x-0 bottom-8 h-12 bg-emerald-400/50 rounded-xl shadow-sm group-hover:-translate-y-4 transition-transform duration-500 delay-150 flex items-center justify-center">
                    <Box :size="24" class="text-emerald-700" />
                 </div>
              </div>
           </div>

           <button @click="router.push('/tools/geological-modeling')" class="mt-auto relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">启动建模</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Tunnel Support -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden flex flex-col h-full">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-orange-50 p-3.5 rounded-2xl text-orange-600 group-hover:bg-orange-500 group-hover:text-white transition-colors">
                 <Hammer :size="24" />
              </div>
              <div class="bg-slate-100 text-slate-500 border border-slate-200 px-3 py-1 rounded-full text-xs font-bold">New</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">巷道支护计算</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">智能计算巷道支护参数，生成科学的支护方案建议。</p>
           
           <!-- Visualization: Tunnel Arch Support -->
           <div class="h-40 bg-slate-900 rounded-3xl relative overflow-hidden mb-8 flex items-center justify-center group-hover:shadow-lg transition-all duration-500">
              <!-- Tunnel shape -->
              <div class="w-32 h-24 border-4 border-slate-700 border-b-0 rounded-t-full relative">
                 <!-- Anchor bolts -->
                 <div class="absolute -top-2 left-1/2 -translate-x-1/2 w-1 h-4 bg-orange-500 rounded-full animate-pulse"></div>
                 <div class="absolute top-4 -left-2 w-4 h-1 bg-orange-500 rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
                 <div class="absolute top-4 -right-2 w-4 h-1 bg-orange-500 rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
                 
                 <!-- Inner glow -->
                 <div class="absolute inset-0 bg-orange-500/10 rounded-t-full blur-md"></div>
              </div>
              <div class="absolute bottom-4 text-xs font-mono text-orange-400 bg-orange-900/30 px-2 py-1 rounded border border-orange-500/30">
                 SUPPORT: ACTIVE
              </div>
           </div>

           <button @click="router.push('/tools/tunnel-support')" class="mt-auto relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">开始计算</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Mining Design -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden flex flex-col h-full">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-purple-50 p-3.5 rounded-2xl text-purple-600 group-hover:bg-purple-500 group-hover:text-white transition-colors">
                 <PenTool :size="24" />
              </div>
              <div class="bg-slate-100 text-slate-500 border border-slate-200 px-3 py-1 rounded-full text-xs font-bold">Tool</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">采掘设计功能</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">辅助进行采掘工程设计与规划，优化开采布局。</p>
           
           <!-- Visualization: Blueprint Grid -->
           <div class="h-40 bg-slate-50 rounded-3xl border border-slate-200 relative overflow-hidden mb-8 group-hover:border-purple-200 transition-colors">
              <!-- Grid -->
              <div class="absolute inset-0 bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f0_1px,transparent_1px)] bg-[size:16px_16px]"></div>
              
              <!-- Design Elements -->
              <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-16 border-2 border-dashed border-purple-300 rounded-lg group-hover:border-purple-500 group-hover:w-28 group-hover:h-20 transition-all duration-500"></div>
              <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-purple-500 rounded-full shadow-[0_0_15px_rgba(168,85,247,0.5)]"></div>
              
              <!-- Cursor -->
              <div class="absolute bottom-8 right-12 text-slate-400 group-hover:text-purple-500 group-hover:translate-x-2 group-hover:-translate-y-2 transition-all duration-700">
                 <PenTool :size="24" />
              </div>
           </div>

           <button @click="router.push('/tools/mining-design')" class="mt-auto relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">进入设计</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Scientific Visualization -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden flex flex-col h-full">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-pink-50 p-3.5 rounded-2xl text-pink-600 group-hover:bg-pink-500 group-hover:text-white transition-colors">
                 <BarChart3 :size="24" />
              </div>
              <div class="bg-slate-100 text-slate-500 border border-slate-200 px-3 py-1 rounded-full text-xs font-bold">Pro</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">科研绘图</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">生成高质量科研图表，支持散点、折线、热力等多种图表。</p>
           
           <!-- Visualization: Animated Charts -->
           <div class="h-40 bg-slate-50 rounded-3xl border border-slate-200 relative overflow-hidden mb-8 flex items-end justify-center gap-3 pb-8 px-8">
              <div class="w-8 bg-pink-200 rounded-t-lg h-12 group-hover:h-20 transition-all duration-500 ease-out relative overflow-hidden">
                 <div class="absolute bottom-0 left-0 w-full h-full bg-gradient-to-t from-pink-500 to-pink-300 opacity-80"></div>
              </div>
              <div class="w-8 bg-pink-200 rounded-t-lg h-16 group-hover:h-28 transition-all duration-700 ease-out delay-75 relative overflow-hidden">
                 <div class="absolute bottom-0 left-0 w-full h-full bg-gradient-to-t from-pink-500 to-pink-300 opacity-90"></div>
              </div>
              <div class="w-8 bg-pink-200 rounded-t-lg h-10 group-hover:h-16 transition-all duration-500 ease-out delay-150 relative overflow-hidden">
                 <div class="absolute bottom-0 left-0 w-full h-full bg-gradient-to-t from-pink-500 to-pink-300 opacity-70"></div>
              </div>
              
              <!-- Floating Stats -->
              <div class="absolute top-4 right-4 bg-white/80 backdrop-blur px-2 py-1 rounded text-[10px] font-bold text-pink-500 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity delay-300">
                 +128%
              </div>
           </div>

           <button @click="router.push('/tools/visualization')" class="mt-auto relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">开始绘图</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: CSV Formatter -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden flex flex-col h-full">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-blue-50 p-3.5 rounded-2xl text-blue-600 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                 <FileSpreadsheet :size="24" />
              </div>
              <div class="bg-slate-100 text-slate-500 border border-slate-200 px-3 py-1 rounded-full text-xs font-bold">Util</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">CSV 格式化工具</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">快速处理和格式化数据文件，一键适配系统输入要求。</p>
           
           <!-- Visualization: Data Processing -->
           <div class="h-40 bg-slate-50 rounded-3xl border border-slate-200 relative overflow-hidden mb-8 flex flex-col items-center justify-center gap-2 p-6">
              <!-- Rows -->
              <div class="w-full h-8 bg-white rounded-lg border border-slate-100 shadow-sm flex items-center px-3 gap-2 transform translate-x-0 group-hover:translate-x-2 transition-transform duration-500">
                 <div class="w-2 h-2 rounded-full bg-red-400 group-hover:bg-emerald-400 transition-colors duration-1000"></div>
                 <div class="h-2 w-20 bg-slate-100 rounded-full"></div>
                 <div class="h-2 w-12 bg-slate-100 rounded-full ml-auto"></div>
              </div>
              <div class="w-full h-8 bg-white rounded-lg border border-slate-100 shadow-sm flex items-center px-3 gap-2 transform translate-x-0 group-hover:-translate-x-2 transition-transform duration-500 delay-75">
                 <div class="w-2 h-2 rounded-full bg-red-400 group-hover:bg-emerald-400 transition-colors duration-1000 delay-100"></div>
                 <div class="h-2 w-16 bg-slate-100 rounded-full"></div>
                 <div class="h-2 w-10 bg-slate-100 rounded-full ml-auto"></div>
              </div>
              <div class="w-full h-8 bg-white rounded-lg border border-slate-100 shadow-sm flex items-center px-3 gap-2 transform translate-x-0 group-hover:translate-x-1 transition-transform duration-500 delay-150">
                 <div class="w-2 h-2 rounded-full bg-red-400 group-hover:bg-emerald-400 transition-colors duration-1000 delay-200"></div>
                 <div class="h-2 w-24 bg-slate-100 rounded-full"></div>
                 <div class="h-2 w-8 bg-slate-100 rounded-full ml-auto"></div>
              </div>
              
              <!-- Scan Line -->
              <div class="absolute top-0 left-0 w-full h-1 bg-blue-400/50 blur-sm translate-y-[-100%] group-hover:translate-y-[1000%] transition-transform duration-[1.5s] ease-in-out"></div>
           </div>

           <button @click="router.push('/tools/csv-formatter')" class="mt-auto relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">打开工具</span>
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
           </button>
        </div>

        <!-- Tool: Downloads -->
        <div class="glass-panel glass-card-hover p-8 rounded-[2rem] transition-all group relative overflow-hidden flex flex-col h-full">
           <div class="flex justify-between items-start mb-8">
              <div class="bg-slate-50 p-3.5 rounded-2xl text-slate-600 group-hover:bg-slate-500 group-hover:text-white transition-colors">
                 <Download :size="24" />
              </div>
              <div class="bg-slate-100 text-slate-500 border border-slate-200 px-3 py-1 rounded-full text-xs font-bold">Res</div>
           </div>
           <h3 class="text-xl font-bold text-slate-800 mb-2">下载中心</h3>
           <p class="text-slate-500 text-sm mb-8 leading-relaxed">获取系统说明书、示例数据包与离线辅助工具。</p>
           
           <!-- Visualization: Download Stream -->
           <div class="h-40 bg-slate-50 rounded-3xl border border-slate-200 relative overflow-hidden mb-8 flex items-center justify-center group-hover:bg-slate-100 transition-colors">
              <div class="relative">
                 <!-- Circle Progress -->
                 <svg class="w-20 h-20 transform -rotate-90">
                    <circle cx="40" cy="40" r="36" stroke="currentColor" stroke-width="4" fill="transparent" class="text-slate-200" />
                    <circle cx="40" cy="40" r="36" stroke="currentColor" stroke-width="4" fill="transparent" stroke-dasharray="226" stroke-dashoffset="226" class="text-emerald-500 group-hover:stroke-dashoffset-0 transition-all duration-[1.5s] ease-out" />
                 </svg>
                 <!-- Icon -->
                 <div class="absolute inset-0 flex items-center justify-center text-slate-300 group-hover:text-emerald-500 transition-colors">
                    <Download :size="24" class="group-hover:animate-bounce" />
                 </div>
              </div>
           </div>

           <button @click="router.push('/downloads')" class="mt-auto relative w-full px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center justify-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 bg-gradient-primary text-white border border-transparent">
              <span class="relative z-10 flex items-center gap-2">前往下载</span>
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
  Box,
  Hammer,
  PenTool,
  BarChart3,
  FileSpreadsheet,
  Download,
  Upload,
  ArrowRight
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

