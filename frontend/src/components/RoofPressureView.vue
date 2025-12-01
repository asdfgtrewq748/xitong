<template>
  <div class="flex flex-col h-full bg-slate-50 p-6 font-sans">
    <!-- 顶部标题栏 -->
    <div class="mb-4 bg-white p-3 rounded-lg shadow-sm border border-slate-200 flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-sm text-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-slate-800">支架工作阻力计算</h2>
          <p class="text-slate-500 text-xs">近距离煤层覆岩破断结构力学模型</p>
        </div>
      </div>
      <button @click="showHistory = !showHistory" class="px-3 py-1.5 bg-white border border-slate-300 text-slate-600 rounded-lg hover:bg-slate-50 hover:text-blue-600 transition-all flex items-center gap-2 text-xs font-medium shadow-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        历史记录
        <span v-if="historyRecords.length" class="bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full text-xs">{{ historyRecords.length }}</span>
      </button>
    </div>

    <div class="flex-1 flex gap-6 min-h-0">
      <!-- 左侧：参数输入区 -->
      <div class="w-2/5 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
        <div class="p-4 border-b border-slate-100 bg-slate-50/50">
          <label class="block text-sm font-bold text-slate-700 mb-2">选择计算模型（层间距类型）</label>
          <div class="relative">
            <select v-model="currentModel" class="w-full appearance-none bg-white border border-slate-300 rounded-lg py-2.5 px-4 pr-8 text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow font-medium">
              <option value="0.87m">层间距 ≤ 5m (散体给定载荷模型)</option>
              <option value="10.47m">层间距 5m-15m (块-散平衡结构)</option>
              <option value="18.03m">层间距 ≥ 15m (砌体梁承载结构)</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
          
          <!-- 快速模板 -->
          <div class="mt-3">
            <label class="text-xs font-medium text-slate-500 mb-2 block">快速加载参数模板</label>
            <div class="grid grid-cols-3 gap-2">
              <button @click="loadTemplate('0.87m_standard')" class="text-xs py-2 px-2 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg hover:bg-amber-100 transition-colors font-medium">
                极近距离
              </button>
              <button @click="loadTemplate('10.47m_standard')" class="text-xs py-2 px-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors font-medium">
                中近距离
              </button>
              <button @click="loadTemplate('18.03m_standard')" class="text-xs py-2 px-2 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors font-medium">
                较近距离
              </button>
            </div>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-4 custom-scrollbar">
          <!-- 直接顶参数 -->
          <div class="mb-4">
            <h3 class="text-sm font-bold text-slate-700 mb-3 pb-2 border-b border-slate-200 flex items-center">
              <span class="w-1 h-4 bg-blue-500 rounded mr-2"></span>直接顶参数
            </h3>
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">容重 γ1 <span class="text-slate-400">(kN/m³)</span></label>
                <input type="number" v-model.number="form.r1" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">厚度 h1 <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.h1" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">控顶距 l1 <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.l1" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
              </div>
              <template v-if="currentModel === '0.87m'">
                <div class="space-y-1">
                  <label class="text-xs font-medium text-slate-600">直接顶2容重 γ2 <span class="text-slate-400">(kN/m³)</span></label>
                  <input type="number" v-model.number="form.r2" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
                </div>
                <div class="space-y-1">
                  <label class="text-xs font-medium text-slate-600">直接顶2厚度 h2 <span class="text-slate-400">(m)</span></label>
                  <input type="number" v-model.number="form.h2_d" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
                </div>
              </template>
            </div>
          </div>

          <!-- 基本顶参数 -->
          <div v-if="currentModel !== '0.87m'" class="mb-4">
            <h3 class="text-sm font-bold text-slate-700 mb-3 pb-2 border-b border-slate-200 flex items-center">
              <span class="w-1 h-4 bg-purple-500 rounded mr-2"></span>基本顶参数
            </h3>
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">容重 γ2 <span class="text-slate-400">(kN/m³)</span></label>
                <input type="number" v-model.number="form.r2" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">厚度 h2 <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.h2" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">周期来压步距 l0 <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.l0" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">岩块下沉量 D <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.D" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">摩擦角 φ <span class="text-slate-400">(°)</span></label>
                <input type="number" v-model.number="form.F" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">破断角 θ <span class="text-slate-400">(°)</span></label>
                <input type="number" v-model.number="form.S" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none" />
              </div>
            </div>
          </div>

            <!-- 散体与煤柱 -->
          <div v-if="currentModel !== '18.03m'" class="mb-4">
            <h3 class="text-sm font-bold text-slate-700 mb-3 pb-2 border-b border-slate-200 flex items-center">
              <span class="w-1 h-4 bg-amber-500 rounded mr-2"></span>散体拱与煤柱
            </h3>
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">散体拱高 Σh <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.hs" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">散体跨距 lc <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.ls" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">安息角 α <span class="text-slate-400">(°)</span></label>
                <input type="number" v-model.number="form.alpha" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">煤柱载荷 pm <span class="text-slate-400">(MPa)</span></label>
                <input type="number" v-model.number="form.pm" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">水平距离 r <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.r" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">垂直距离 z <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.z" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none" />
              </div>
            </div>
          </div>

          <!-- 其他参数 -->
          <div class="mb-4">
            <h3 class="text-sm font-bold text-slate-700 mb-3 pb-2 border-b border-slate-200 flex items-center">
              <span class="w-1 h-4 bg-gray-500 rounded mr-2"></span>其他参数
            </h3>
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="text-xs font-medium text-slate-600">支架宽度 b <span class="text-slate-400">(m)</span></label>
                <input type="number" v-model.number="form.b" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-gray-500 focus:border-gray-500 outline-none" />
              </div>
              <template v-if="currentModel !== '0.87m'">
                <div class="space-y-1">
                  <label class="text-xs font-medium text-slate-600">上覆岩层载荷 q <span class="text-slate-400">(kPa)</span></label>
                  <input type="number" v-model.number="form.qn2" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-gray-500 focus:border-gray-500 outline-none" />
                </div>
              </template>
              <template v-if="currentModel !== '18.03m'">
                <div class="space-y-1">
                  <label class="text-xs font-medium text-slate-600">富余系数 k</label>
                  <input type="number" v-model.number="form.ks" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-gray-500 focus:border-gray-500 outline-none" />
                </div>
                <div class="space-y-1">
                  <label class="text-xs font-medium text-slate-600">散体容重 γ3 <span class="text-slate-400">(kN/m³)</span></label>
                  <input type="number" v-model.number="form.rs" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-gray-500 focus:border-gray-500 outline-none" />
                </div>
                <div class="space-y-1">
                  <label class="text-xs font-medium text-slate-600">均布载荷宽 L1 <span class="text-slate-400">(m)</span></label>
                  <input type="number" v-model.number="form.L1" class="w-full border border-slate-300 bg-white rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:ring-2 focus:ring-gray-500 focus:border-gray-500 outline-none" />
                </div>
              </template>
            </div>
          </div>
        </div>

        <div class="p-5 border-t border-slate-100 bg-white">
          <button @click="calculate" :disabled="calculating" class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3.5 rounded-xl font-bold shadow-lg shadow-blue-200 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2 transform active:scale-[0.98]">
            <svg v-if="calculating" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span v-else>开始计算</span>
          </button>
        </div>
      </div>

      <!-- 右侧：结果与图示 -->
      <div class="w-2/3 flex flex-col gap-6 min-h-0 overflow-y-auto custom-scrollbar pr-2">
        
        <!-- 历史记录浮层 -->
        <div v-if="showHistory" class="bg-white p-6 rounded-xl shadow-lg border border-slate-200 mb-2 animate-fade-in-down">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-lg text-slate-800">历史计算记录</h3>
            <div class="flex gap-2">
              <button @click="clearHistory" class="text-xs px-3 py-1.5 bg-red-50 text-red-600 rounded-md hover:bg-red-100 transition-colors font-medium">
                清空
              </button>
              <button @click="showHistory = false" class="text-xs px-3 py-1.5 bg-slate-100 text-slate-600 rounded-md hover:bg-slate-200 transition-colors font-medium">
                关闭
              </button>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3 max-h-60 overflow-y-auto">
            <div v-if="historyRecords.length === 0" class="col-span-2 text-center text-slate-400 py-8 bg-slate-50 rounded-lg border border-dashed border-slate-200">
              暂无历史记录
            </div>
            <div v-for="record in historyRecords" :key="record.id" 
                 class="p-3 bg-white border border-slate-200 rounded-lg hover:border-blue-300 hover:shadow-md cursor-pointer transition-all group"
                 @click="loadFromHistory(record)">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600 group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">{{ record.model }}</span>
                <span class="text-xs text-slate-400">{{ record.timestamp }}</span>
              </div>
              <div class="flex justify-between items-end">
                <div class="text-sm font-bold text-slate-800">
                  P = <span class="text-blue-600 text-lg">{{ record.result }}</span> kN
                </div>
                <div class="text-xs text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity">
                  点击加载
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 主要结果卡片 -->
        <div class="bg-gradient-to-br from-white to-blue-50 p-8 rounded-xl shadow-sm border border-blue-100 text-center relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700"></div>
          <div class="absolute -right-10 -top-10 w-40 h-40 bg-blue-100 rounded-full opacity-50 blur-3xl"></div>
          <div class="absolute -left-10 -bottom-10 w-40 h-40 bg-indigo-100 rounded-full opacity-50 blur-3xl"></div>
          
          <h3 class="text-slate-500 text-lg mb-2 font-medium relative z-10">计算结果：支架工作阻力 P</h3>
          <div class="flex items-baseline justify-center gap-2 my-4 relative z-10">
            <span class="text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 tracking-tight">
              {{ result !== null ? result : '---' }}
            </span>
            <span class="text-2xl text-slate-400 font-medium">kN</span>
          </div>
          <div v-if="result" class="inline-block bg-white/80 backdrop-blur-sm border border-blue-200 rounded-full px-6 py-2 text-sm text-blue-700 font-medium shadow-sm relative z-10">
            建议选型：ZY{{ Math.ceil(result/100)*100 }}/18/38
          </div>
        </div>

        <!-- 详细结果网格 -->
        <div v-if="detailedResults" class="grid grid-cols-4 gap-4 animate-fade-in-up">
          <div class="bg-blue-50 border border-blue-100 p-4 rounded-xl flex flex-col items-center justify-center text-center transition-transform hover:scale-105">
            <div class="text-blue-600 text-xs font-bold uppercase tracking-wider mb-1">直接顶重量</div>
            <div class="text-blue-700 text-xl font-extrabold">
              {{ detailedResults.Q_direct || 0 }} <span class="text-xs font-normal opacity-70">kN</span>
            </div>
          </div>
          <div v-if="currentModel !== '18.03m'" class="bg-amber-50 border border-amber-100 p-4 rounded-xl flex flex-col items-center justify-center text-center transition-transform hover:scale-105">
            <div class="text-amber-600 text-xs font-bold uppercase tracking-wider mb-1">散体拱重量</div>
            <div class="text-amber-700 text-xl font-extrabold">
              {{ detailedResults.Q_loose || 0 }} <span class="text-xs font-normal opacity-70">kN</span>
            </div>
          </div>
          <div v-if="currentModel !== '18.03m'" class="bg-orange-50 border border-orange-100 p-4 rounded-xl flex flex-col items-center justify-center text-center transition-transform hover:scale-105">
            <div class="text-orange-600 text-xs font-bold uppercase tracking-wider mb-1">应力传递载荷</div>
            <div class="text-orange-700 text-xl font-extrabold">
              {{ detailedResults.F_stress || 0 }} <span class="text-xs font-normal opacity-70">kN</span>
            </div>
          </div>
          <div v-if="currentModel !== '0.87m'" class="bg-purple-50 border border-purple-100 p-4 rounded-xl flex flex-col items-center justify-center text-center transition-transform hover:scale-105">
            <div class="text-purple-600 text-xs font-bold uppercase tracking-wider mb-1">基本顶载荷</div>
            <div class="text-purple-700 text-xl font-extrabold">
              {{ detailedResults.Q_block || 0 }} <span class="text-xs font-normal opacity-70">kN</span>
            </div>
          </div>
          <div v-if="currentModel !== '0.87m'" class="bg-pink-50 border border-pink-100 p-4 rounded-xl flex flex-col items-center justify-center text-center transition-transform hover:scale-105">
            <div class="text-pink-600 text-xs font-bold uppercase tracking-wider mb-1">结构系数</div>
            <div class="text-pink-700 text-xl font-extrabold">
              {{ detailedResults.struct_factor || 0 }}
            </div>
          </div>
        </div>

        <!-- 模型示意图 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 flex-1 flex flex-col overflow-hidden min-h-[400px]">
          <div class="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
            <h3 class="font-bold text-slate-700 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              力学模型示意图
            </h3>
            <span class="text-xs text-slate-400 bg-white px-2 py-1 rounded border border-slate-200">地质模型图</span>
          </div>
          
          <div class="flex-1 bg-slate-100 relative flex items-center justify-center p-8 overflow-hidden">
            <!-- 0.87m 模型：散体给定载荷平衡结构 -->
            <div v-if="currentModel === '0.87m'" class="w-full h-full flex flex-col items-center justify-center">
              <img :src="require('@/assets/images/model-0.87m.png')" alt="散体给定载荷平衡结构" class="w-full h-auto max-h-[400px] object-contain drop-shadow-lg rounded-lg" />
              <p class="text-sm text-slate-600 mt-4 font-medium bg-white/50 px-4 py-2 rounded-full border border-slate-200">
                模型说明：支架载荷 = 直接顶重量 + 散体拱内岩重 + 煤柱应力传递
              </p>
            </div>

            <!-- 10.47m 模型：块-散平衡结构 -->
            <div v-else-if="currentModel === '10.47m'" class="w-full h-full flex flex-col items-center justify-center">
              <img :src="require('@/assets/images/model-10.47m.png')" alt="块-散平衡结构" class="w-full h-auto max-h-[400px] object-contain drop-shadow-lg rounded-lg" />
              <p class="text-sm text-slate-600 mt-4 font-medium bg-white/50 px-4 py-2 rounded-full border border-slate-200">
                模型说明：支架载荷 = 直接顶 + 结构系数 × (基本顶 + 散体)
              </p>
            </div>

            <!-- 18.03m 模型：砌体梁承载结构 -->
            <div v-else class="w-full h-full flex flex-col items-center justify-center">
              <img :src="require('@/assets/images/model-18.03m.png')" alt="砌体梁承载结构" class="w-full h-auto max-h-[400px] object-contain drop-shadow-lg rounded-lg" />
              <p class="text-sm text-slate-600 mt-4 font-medium bg-white/50 px-4 py-2 rounded-full border border-slate-200">
                模型说明：支架载荷 = 直接顶 + 结构系数 × 基本顶 (形成稳定砌体梁)
              </p>
            </div>
          </div>
        </div>

        <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3 animate-shake">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-red-700 font-medium">{{ errorMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'

// 默认模型
const currentModel = ref('0.87m')
const result = ref(null)
const calculating = ref(false)
const errorMessage = ref('')
const detailedResults = ref(null) // 详细计算结果
const historyRecords = ref([]) // 历史记录
const showHistory = ref(false) // 显示历史记录面板

// 参数预设模板
const parameterTemplates = {
  '0.87m_standard': {
    name: '0.87m 标准工况',
    model: '0.87m',
    params: { r1: 22, h1: 0.59, l1: 9, b: 1.75, r2: 27, h2_d: 0.28, hs: 7.056, ls: 18, ks: 1.3, alpha: 20, rs: 24, pm: 16.49, L1: 15, r: 35, z: 0.87 }
  },
  '10.47m_standard': {
    name: '10.47m 标准工况',
    model: '10.47m',
    params: { r1: 25, h1: 1.2, l1: 8, b: 1.75, r2: 26, h2: 6.44, l0: 18, D: 1.5, F: 45, S: 7, qn2: 0, hs: 6.5, ls: 16, ks: 1.3, alpha: 20, rs: 24, pm: 15, L1: 15, r: 30, z: 10.47 }
  },
  '18.03m_standard': {
    name: '18.03m 标准工况',
    model: '18.03m',
    params: { r1: 25, h1: 1.5, l1: 8, b: 1.75, r2: 27, h2: 8, l0: 20, D: 2, F: 45, S: 7 }
  }
}

// 表单数据 (预填默认值，参考源程序)
const form = reactive({
  r1: 22, h1: 0.59, l1: 9, b: 1.75,
  r2: 27, h2_d: 0.28, // 0.87m模型的直接顶2
  h2: 6.44, // 基本顶厚度
  hs: 7.056, ls: 18, ks: 1.3, alpha: 20, rs: 24,
  pm: 16.49, L1: 15, r: 35, z: 0.87,
  l0: 18, D: 1.5, F: 45, S: 7, qn2: 0
})

// 从 localStorage 加载参数
const loadFromLocalStorage = () => {
  try {
    const saved = localStorage.getItem('roofPressure_params')
    if (saved) {
      const data = JSON.parse(saved)
      Object.assign(form, data.params)
      currentModel.value = data.model || '0.87m'
    }
    
    const savedHistory = localStorage.getItem('roofPressure_history')
    if (savedHistory) {
      historyRecords.value = JSON.parse(savedHistory)
    }
  } catch (e) {
    console.error('加载保存的参数失败:', e)
  }
}

// 保存参数到 localStorage
const saveToLocalStorage = () => {
  try {
    localStorage.setItem('roofPressure_params', JSON.stringify({
      model: currentModel.value,
      params: { ...form }
    }))
  } catch (e) {
    console.error('保存参数失败:', e)
  }
}

// 监听表单变化自动保存
watch([form, currentModel], () => {
  saveToLocalStorage()
}, { deep: true })

// 加载模板
const loadTemplate = (templateKey) => {
  const template = parameterTemplates[templateKey]
  if (template) {
    currentModel.value = template.model
    Object.assign(form, template.params)
  }
}

// 保存到历史记录
const saveToHistory = (calcResult, details) => {
  const record = {
    id: Date.now(),
    timestamp: new Date().toLocaleString('zh-CN'),
    model: currentModel.value,
    params: { ...form },
    result: calcResult,
    details: details
  }
  
  historyRecords.value.unshift(record)
  // 只保留最近10条
  if (historyRecords.value.length > 10) {
    historyRecords.value = historyRecords.value.slice(0, 10)
  }
  
  localStorage.setItem('roofPressure_history', JSON.stringify(historyRecords.value))
}

// 从历史记录加载
const loadFromHistory = (record) => {
  currentModel.value = record.model
  Object.assign(form, record.params)
  result.value = record.result
  detailedResults.value = record.details
  showHistory.value = false
}

// 清空历史记录
const clearHistory = () => {
  if (confirm('确定要清空所有历史记录吗？')) {
    historyRecords.value = []
    localStorage.removeItem('roofPressure_history')
  }
}

const calculate = async () => {
  calculating.value = true
  errorMessage.value = ''
  detailedResults.value = null
  
  try {
    // 调用后端 API (通过 window.pywebview.api)
    if (window.pywebview) {
      const res = await window.pywebview.api.calculate_support_resistance({
        model_type: currentModel.value,
        data: { ...form }
      })
      
      if (res.status === 'success') {
        result.value = res.result
        detailedResults.value = res.details || null
        
        // 保存到历史记录
        saveToHistory(res.result, res.details)
      } else {
        errorMessage.value = '计算失败: ' + res.message
      }
    } else {
      // 开发环境模拟
      console.warn('PyWebView API not found. Mocking result.')
      await new Promise(resolve => setTimeout(resolve, 800)) // 增加一点延迟模拟真实感
      
      // 模拟详细结果
      const mockResult = (Math.random() * 5000 + 5000).toFixed(2)
      const mockDetails = {
        Q_direct: (Math.random() * 2000 + 1000).toFixed(2),
        Q_loose: currentModel.value !== '18.03m' ? (Math.random() * 1500 + 800).toFixed(2) : 0,
        F_stress: currentModel.value !== '18.03m' ? (Math.random() * 1000 + 500).toFixed(2) : 0,
        Q_block: currentModel.value !== '0.87m' ? (Math.random() * 3000 + 2000).toFixed(2) : 0,
        struct_factor: currentModel.value !== '0.87m' ? (Math.random() * 0.5 + 1.5).toFixed(2) : 0
      }
      
      result.value = mockResult
      detailedResults.value = mockDetails
      
      // 保存到历史记录
      saveToHistory(mockResult, mockDetails)
    }
  } catch (error) {
    errorMessage.value = '计算过程中发生错误: ' + error.message
  } finally {
    calculating.value = false
  }
}

// 组件挂载时加载保存的参数
onMounted(() => {
  loadFromLocalStorage()
})
</script>

<style scoped>
/* 自定义滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

/* 动画 */
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-down {
  animation: fadeInDown 0.3s ease-out;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up {
  animation: fadeInUp 0.4s ease-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
  20%, 40%, 60%, 80% { transform: translateX(2px); }
}
.animate-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}
</style>