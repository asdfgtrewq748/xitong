<template>
  <div class="min-h-screen bg-aurora text-slate-800 font-sans selection:bg-violet-200 selection:text-violet-900 flex flex-col">
    
    <!-- Glass Navbar -->
    <header class="sticky top-0 z-50 bg-white/70 backdrop-blur-2xl border-b border-white/50">
      <div class="w-full px-8 h-20 flex items-center justify-between">
         <div class="flex items-center gap-3 cursor-pointer group" @click="router.push('/')">
            <div class="bg-gradient-primary text-white p-2.5 rounded-xl shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform duration-300">
               <Hexagon :size="24" :strokeWidth="2.5" />
            </div>
            <span class="text-xl font-black tracking-tight text-slate-800 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-primary transition-all">HELIOS</span>
         </div>

         <nav class="hidden md:flex bg-slate-100/50 p-1.5 rounded-full backdrop-blur-sm border border-white/50">
            <router-link 
              to="/" 
              class="px-6 py-2 rounded-full text-sm font-bold transition-all duration-300 capitalize"
              active-class="bg-white text-violet-600 shadow-sm"
              :class="{'text-slate-500 hover:text-slate-700': $route.path !== '/'}"
            >
              首页
            </router-link>
            <router-link 
              to="/tools" 
              class="px-6 py-2 rounded-full text-sm font-bold transition-all duration-300 capitalize"
              active-class="bg-white text-violet-600 shadow-sm"
              :class="{'text-slate-500 hover:text-slate-700': !$route.path.startsWith('/tools')}"
            >
              工具
            </router-link>
            <router-link 
              to="/downloads" 
              class="px-6 py-2 rounded-full text-sm font-bold transition-all duration-300 capitalize"
              active-class="bg-white text-violet-600 shadow-sm"
              :class="{'text-slate-500 hover:text-slate-700': $route.path !== '/downloads'}"
            >
              下载
            </router-link>
         </nav>

         <!-- User info removed as per request -->
         <div class="w-10"></div> 
      </div>
    </header>

    <main class="flex-1 relative">
       <router-view v-slot="{ Component }">
         <transition name="fade" mode="out-in">
           <component :is="Component" />
         </transition>
       </router-view>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { Hexagon } from 'lucide-vue-next';

const router = useRouter();
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
