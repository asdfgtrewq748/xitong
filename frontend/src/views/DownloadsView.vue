<template>
  <div class="container mx-auto px-8 py-12 max-w-5xl animate-fadeIn">
     <!-- Glass Header Banner -->
     <div class="glass-panel rounded-[2.5rem] p-12 mb-12 relative overflow-hidden">
        <!-- Background Gradients -->
        <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-violet-100 to-cyan-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none"></div>
        
        <div class="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
           <div>
              <div class="inline-block px-3 py-1 bg-white/50 rounded-full text-[10px] font-bold text-slate-500 mb-4 border border-white/60">ARCHIVES</div>
              <h2 class="text-4xl font-black text-slate-800 mb-3 tracking-tight">下载中心</h2>
              <p class="text-slate-500 text-lg max-w-md">获取最新的驱动程序、固件更新以及详细的地质分析报告。</p>
           </div>
           <div class="bg-white p-6 rounded-[2rem] shadow-xl shadow-indigo-100 transform rotate-3 hover:rotate-0 transition-transform duration-500">
              <div class="w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center text-white">
                 <Download :size="32" />
              </div>
           </div>
        </div>
     </div>

     <div class="grid grid-cols-1 gap-4">
        <div v-for="(item, i) in items" :key="i" class="bg-white/60 backdrop-blur-md border border-white/60 rounded-2xl p-5 flex items-center justify-between hover:bg-white hover:shadow-xl hover:shadow-violet-500/5 hover:scale-[1.01] transition-all duration-300 group cursor-pointer">
           <div class="flex items-center gap-6">
              <div class="w-14 h-14 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400 group-hover:bg-gradient-primary group-hover:text-white transition-all duration-300 shadow-sm group-hover:shadow-lg group-hover:shadow-indigo-500/20">
                 <component :is="item.icon" :size="24" />
              </div>
              <div>
                 <h4 class="text-lg font-bold text-slate-800 mb-1 group-hover:text-violet-600 transition-colors">{{ item.name }}</h4>
                 <div class="flex gap-4 text-xs text-slate-400 font-medium">
                    <span class="flex items-center gap-1"><LayoutGrid :size="12"/> {{ item.type }}</span>
                    <span>{{ item.size }}</span>
                    <span>Updated: {{ item.update }}</span>
                 </div>
              </div>
           </div>
           <button class="w-12 h-12 rounded-full border border-slate-100 bg-white flex items-center justify-center text-slate-400 hover:border-violet-500 hover:bg-violet-500 hover:text-white transition-all shadow-sm">
              <Download :size="20" />
           </button>
        </div>
     </div>
  </div>
</template>

<script setup>
import { Download, Cpu, FileText, Shield, Server, LayoutGrid } from 'lucide-vue-next';

const items = [
  { name: "系统固件 v2.4.0", size: "128 MB", type: "FIRMWARE", update: "Today", icon: Cpu },
  { name: "地质勘测报告 Q3", size: "24 MB", type: "PDF", update: "Yesterday", icon: FileText },
  { name: "安全协议手册", size: "4.5 MB", type: "DOC", update: "Oct 24", icon: Shield },
  { name: "节点日志_Oct_2024", size: "2 MB", type: "LOG", update: "Oct 20", icon: Server },
];
</script>
