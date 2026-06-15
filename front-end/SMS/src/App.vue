<template>
  <div :class="['min-h-dvh font-sans', themeStore.isDark ? 'dark' : '']">
    <div class="app-surface min-h-dvh overflow-x-hidden transition-colors duration-300">
      <router-view />
      <InstallPrompt />
    </div>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
import InstallPrompt from '@/components/ui/InstallPrompt.vue'
const themeStore = useThemeStore()
</script>
