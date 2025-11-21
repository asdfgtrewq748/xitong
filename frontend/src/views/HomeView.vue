<template>
  <div class="animate-fadeIn pb-12">
    <!-- Hero Section -->
    <div class="relative min-h-[450px] flex items-center overflow-hidden">
      <!-- Advanced Mesh Gradient Background -->
      <div class="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-violet-200/30 rounded-full blur-[100px] mix-blend-multiply animate-float"></div>
      <div class="absolute bottom-[-20%] left-[-10%] w-[600px] h-[600px] bg-cyan-200/30 rounded-full blur-[100px] mix-blend-multiply animate-float" style="animation-delay: 2s"></div>
      <div class="absolute top-[20%] left-[30%] w-[400px] h-[400px] bg-fuchsia-100/40 rounded-full blur-[80px] mix-blend-multiply animate-float" style="animation-delay: 4s"></div>

      <div class="container mx-auto px-8 relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center pt-12 pb-12">
        <div class="space-y-8">
          <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/60 border border-white/50 text-slate-600 text-xs font-bold uppercase tracking-wide shadow-sm backdrop-blur-md">
            <span class="w-2 h-2 rounded-full bg-gradient-primary"></span>
            Helios System v2.4
          </div>
          
          <h1 class="text-6xl lg:text-8xl font-black text-slate-900 tracking-tight leading-[1.05]">
            Pure <span class="text-gradient-primary">Prism</span> <br/>
            Intelligence
          </h1>
          
          <p class="text-slate-500 text-lg max-w-md leading-relaxed font-medium">
            通过全息数据光谱，洞察深层地质结构。体验前所未有的清晰度与精准度。
          </p>
          
          <div class="flex gap-4 pt-2">
            <GlassButton @click="startConsole">
              <LayoutGrid :size="18" /> 启动控制台
            </GlassButton>
            <GlassButton variant="secondary">
               <Activity :size="18" /> 实时监控
            </GlassButton>
          </div>
        </div>

        <!-- 3D Glass Morphism Dashboard Mockup -->
        <div class="relative hidden lg:block perspective-1000">
          <div class="relative z-10 bg-white/40 backdrop-blur-2xl rounded-[2.5rem] shadow-[0_25px_50px_-12px_rgba(0,0,0,0.1)] border border-white/60 p-8 animate-float transform rotate-y-12 hover:rotate-y-0 transition-transform duration-700 ease-out">
            <!-- Header Fake UI -->
            <div class="flex items-center justify-between mb-8">
              <div class="flex items-center gap-3">
                 <div class="w-10 h-10 rounded-2xl bg-gradient-primary flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
                    <Hexagon :size="20" :strokeWidth="3" />
                 </div>
                 <div>
                    <div class="h-2 w-24 bg-slate-800/10 rounded-full mb-1"></div>
                    <div class="h-2 w-16 bg-slate-800/5 rounded-full"></div>
                 </div>
              </div>
              <div class="p-2 bg-white/50 rounded-xl">
                 <MoreHorizontal :size="20" class="text-slate-400" />
              </div>
            </div>

            <!-- Charts Fake UI -->
            <div class="grid grid-cols-2 gap-6 mb-6">
               <div class="h-32 bg-white/60 rounded-3xl shadow-sm p-4 relative overflow-hidden">
                  <div class="absolute top-4 left-4 text-xs font-bold text-slate-400">EFFICIENCY</div>
                  <div class="absolute bottom-4 left-4 text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-cyan-500">98.4%</div>
                  <div class="absolute -right-4 -bottom-4 w-24 h-24 bg-violet-100 rounded-full blur-xl"></div>
               </div>
               <div class="h-32 bg-gradient-primary rounded-3xl shadow-lg shadow-indigo-500/20 p-4 flex flex-col justify-between text-white relative overflow-hidden">
                  <div class="absolute top-0 left-0 w-full h-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
                  <div class="relative z-10">
                     <Activity class="opacity-80" :size="24" />
                  </div>
                  <div class="relative z-10 text-lg font-bold">Active Scanning</div>
               </div>
            </div>
            
            <!-- Bottom Bars -->
            <div class="space-y-4">
               <div class="flex items-center justify-between text-xs font-bold text-slate-400 mb-1">
                  <span>SYSTEM LOAD</span>
                  <span>42%</span>
               </div>
               <div class="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div class="h-full w-[42%] bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full"></div>
               </div>
            </div>
          </div>
          
          <!-- Floating Elements behind -->
          <div class="absolute top-10 -right-10 bg-white/80 backdrop-blur-xl p-4 rounded-2xl shadow-xl animate-float" style="animation-delay: 1s">
             <Shield class="text-emerald-500" :size="24" />
          </div>
          <div class="absolute -bottom-5 -left-5 bg-white/80 backdrop-blur-xl p-4 rounded-2xl shadow-xl animate-float" style="animation-delay: 2.5s">
             <Zap class="text-amber-500" :size="24" />
          </div>
        </div>
      </div>
    </div>

    <!-- Content Body -->
    <div class="container mx-auto px-8 py-8 space-y-12">
      <!-- Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
         <CleanCard title="实时算力" value="142 TH/s" sub="Optimal" :icon="Cpu" :delay="0" :trend="12" />
         <CleanCard title="地质勘测" value="4,200m" sub="Deep Scan" :icon="Globe" :delay="100" />
         <CleanCard title="核心温度" value="42°C" sub="Stable" :icon="Wind" :delay="200" />
         <CleanCard title="网络状态" value="5ms" sub="Ultra Low" :icon="Wifi" :delay="300" />
      </div>

      <!-- Server Status Grid -->
      <div class="glass-panel rounded-[2rem] p-10">
         <div class="flex items-center justify-between mb-8">
            <div>
               <h3 class="text-xl font-bold text-slate-800 flex items-center gap-2 mb-1">
                 <Server class="text-violet-500" :size="24"/> 节点全息阵列
               </h3>
               <p class="text-slate-500 text-sm">实时监控所有计算节点的健康状态与负载。</p>
            </div>
            <div class="flex gap-4">
               <div class="flex items-center gap-2 text-xs font-bold text-slate-500 bg-white px-3 py-1.5 rounded-full shadow-sm border border-slate-100">
                  <span class="w-2 h-2 rounded-full bg-emerald-400"></span> 14 Online
               </div>
               <div class="flex items-center gap-2 text-xs font-bold text-slate-500 bg-white px-3 py-1.5 rounded-full shadow-sm border border-slate-100">
                  <span class="w-2 h-2 rounded-full bg-amber-400"></span> 2 Updating
               </div>
            </div>
         </div>
         
         <div class="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-16 gap-4">
            <div v-for="(status, i) in nodes" :key="i" :class="[
              'aspect-square rounded-2xl transition-all duration-500 flex items-center justify-center relative group cursor-pointer',
              status === 'updating' ? 'bg-amber-50 border border-amber-100' : 'bg-white border border-slate-100 hover:border-violet-300 hover:shadow-lg hover:shadow-violet-500/10 hover:-translate-y-1'
            ]">
               <div :class="[
                 'w-3 h-3 rounded-full transition-all duration-500 relative',
                 status === 'updating' ? 'bg-amber-400' : 'bg-slate-200 group-hover:bg-transparent'
               ]">
                  <div v-if="status !== 'updating'" class="absolute inset-0 bg-gradient-primary rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
               </div>
               
               <!-- Tooltip -->
               <div class="absolute -top-12 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] font-bold px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-all pointer-events-none whitespace-nowrap shadow-xl transform group-hover:-translate-y-1 z-20">
                  Node-{{ i+1 }} <span class="text-slate-400">|</span> 98%
                  <div class="absolute bottom-[-4px] left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900 rotate-45"></div>
               </div>
            </div>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
  Activity, Cpu, Zap, Wind, Hexagon, Globe, Shield, Server, Wifi, LayoutGrid, MoreHorizontal 
} from 'lucide-vue-next';
import GlassButton from '../components/helios/GlassButton.vue';
import CleanCard from '../components/helios/CleanCard.vue';

const router = useRouter();
const nodes = ref(Array(16).fill('active'));
let interval;

onMounted(() => {
  interval = setInterval(() => {
    nodes.value = nodes.value.map(() => Math.random() > 0.9 ? 'updating' : 'active');
  }, 2000);
});

onUnmounted(() => {
  clearInterval(interval);
});

const startConsole = () => {
  router.push('/tools');
};
</script>
