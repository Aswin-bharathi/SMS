<template>
  <button
    @click="themeStore.toggleTheme()"
    :class="[
      'relative w-14 h-7 rounded-full transition-all duration-500 focus:outline-none',
      'focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
      themeStore.isDark
        ? 'bg-primary-600'
        : 'bg-gray-200'
    ]"
    :title="themeStore.isDark ? 'Switch to Light' : 'Switch to Dark'"
  >
    <!-- Track Icons -->
    <span class="absolute left-1.5 top-1/2 -translate-y-1/2 text-xs">🌙</span>
    <span class="absolute right-1.5 top-1/2 -translate-y-1/2 text-xs">☀️</span>

    <!-- Thumb -->
    <span
      :class="[
        'absolute top-0.5 w-6 h-6 rounded-full shadow-md',
        'flex items-center justify-center transition-all duration-500',
        'bg-white',
        themeStore.isDark ? 'translate-x-7' : 'translate-x-0.5'
      ]"
    >
      <component
        :is="themeStore.isDark ? Moon : Sun"
        class="w-3.5 h-3.5"
        :class="themeStore.isDark ? 'text-primary-600' : 'text-yellow-500'"
      />
    </span>
  </button>
</template>

<script setup>
import { Sun, Moon } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'
const themeStore = useThemeStore()
</script>
