<template>
  <div 
    class="glass-panel glass-card-hover p-6 rounded-2xl transition-all duration-500 group relative overflow-hidden animate-fadeIn"
    :style="{ animationDelay: `${delay}ms` }"
  >
    <div class="flex justify-between items-start mb-4">
      <div class="p-3 bg-slate-50 rounded-xl text-slate-400 group-hover:text-white group-hover:bg-gradient-primary transition-all duration-300 shadow-inner">
        <component :is="icon" :size="24" />
      </div>
      <!-- Dynamic Status Dot -->
      <span class="flex h-3 w-3 relative">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
      </span>
    </div>
    
    <h3 class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">{{ title }}</h3>
    <div class="flex items-baseline gap-2">
      <div class="text-3xl font-black text-slate-800 mb-2 tracking-tight">{{ value }}</div>
    </div>
    
    <div class="flex items-center justify-between">
      <div class="text-xs text-slate-500 font-medium bg-slate-50/80 inline-block px-2 py-1 rounded-md border border-slate-100">
        {{ sub }}
      </div>
      <span v-if="trend" class="text-xs font-bold text-emerald-500 flex items-center">
        +{{ trend }}% <Activity :size="10" class="ml-1"/>
      </span>
    </div>
    
    <!-- Holographic decorative blur -->
    <div class="absolute -bottom-8 -right-8 w-32 h-32 bg-gradient-to-br from-violet-400/20 to-cyan-300/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700 pointer-events-none"></div>
  </div>
</template>

<script setup>
import { Activity } from 'lucide-vue-next';

defineProps({
  title: String,
  value: String,
  sub: String,
  icon: Object,
  delay: {
    type: Number,
    default: 0
  },
  trend: Number
});
</script>
