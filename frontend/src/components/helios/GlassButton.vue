<template>
  <button :class="[baseStyle, variants[variant], className]" @click="$emit('click')">
    <div v-if="variant === 'primary'" class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
    <div v-if="variant === 'primary'" class="absolute inset-0 w-full h-full pointer-events-none">
      <div class="absolute top-0 left-0 h-full w-1/2 bg-gradient-to-r from-transparent via-white/10 to-transparent -skew-x-12 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
    </div>
    <span class="relative z-10 flex items-center gap-2">
      <slot></slot>
    </span>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary'
  },
  className: {
    type: String,
    default: ''
  }
});

defineEmits(['click']);

const baseStyle = "relative px-6 py-3 font-bold text-sm transition-all duration-300 rounded-xl flex items-center gap-2 overflow-hidden group shadow-[0_2px_10px_rgba(99,102,241,0.1)] hover:shadow-[0_8px_20px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 active:translate-y-0 cursor-pointer";

const variants = {
  primary: "bg-gradient-primary text-white border border-transparent",
  secondary: "bg-white text-slate-600 border border-slate-100 hover:border-violet-200 hover:text-violet-600",
  outline: "bg-transparent text-violet-600 border border-violet-200 hover:bg-violet-50"
};
</script>
