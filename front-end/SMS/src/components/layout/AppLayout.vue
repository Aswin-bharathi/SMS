<template>
  <div class="min-h-dvh overflow-x-hidden">
    <Sidebar
      :collapsed="sidebarCollapsed"
      :mobile-open="mobileSidebarOpen"
      @close-mobile="mobileSidebarOpen = false"
    />

    <div
      v-if="mobileSidebarOpen"
      class="fixed inset-0 z-30 bg-slate-950/50 backdrop-blur-sm lg:hidden"
      @click="mobileSidebarOpen = false"
    />

    <div
      :class="[
        'min-h-dvh transition-all duration-300',
        sidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'
      ]"
    >
      <Navbar @toggle-sidebar="toggleSidebar" />
      <main class="mx-auto w-full max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Navbar from './Navbar.vue'
import Sidebar from './Sidebar.vue'

const sidebarCollapsed = ref(false)
const mobileSidebarOpen = ref(false)

const toggleSidebar = () => {
  if (window.innerWidth < 1024) {
    mobileSidebarOpen.value = !mobileSidebarOpen.value
    return
  }
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>
