<template>
  <header class="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/70 bg-white/80 px-4 backdrop-blur-xl dark:border-slate-700/70 dark:bg-slate-900/80 sm:px-6">
    <!-- Left: Toggle + Breadcrumb -->
    <div class="flex items-center gap-4">
      <button
        @click="$emit('toggle-sidebar')"
        class="w-9 h-9 flex items-center justify-center rounded-xl
               hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
      >
        <Menu class="w-5 h-5 text-gray-500 dark:text-gray-400" />
      </button>

      <!-- Breadcrumb -->
      <div class="flex items-center gap-2 text-sm">
        <span class="text-gray-400 dark:text-gray-500">Pages</span>
        <ChevronRight class="w-4 h-4 text-gray-300 dark:text-gray-600" />
        <span class="font-semibold text-gray-800 dark:text-white">
          {{ currentRoute }}
        </span>
      </div>
    </div>

    <!-- Right -->
    <div class="flex items-center gap-2">

      <!-- Search -->
      <form class="relative hidden md:block" @submit.prevent="submitSearch">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Quick search..."
          class="pl-9 pr-4 py-2 text-sm rounded-xl bg-gray-50 dark:bg-gray-700
                 border border-gray-200 dark:border-slate-700 text-gray-700
                 dark:text-gray-300 w-56 focus:outline-none focus:ring-2
                 focus:ring-primary-500 focus:border-transparent
                 placeholder-gray-400 dark:placeholder-gray-500"
        />
      </form>

      <!-- Notification -->
      <div class="relative">
        <button
          class="relative w-9 h-9 flex items-center justify-center rounded-xl hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
          @click="showNotifications = !showNotifications"
        >
          <Bell class="w-5 h-5 text-gray-500 dark:text-gray-400" />
          <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>
        <Transition name="fade">
          <div
            v-if="showNotifications"
            class="absolute right-0 mt-3 w-80 rounded-2xl border border-slate-200 bg-white p-3 shadow-xl shadow-slate-900/10 dark:border-slate-700 dark:bg-slate-900"
          >
            <p class="px-2 pb-2 text-sm font-bold text-slate-900 dark:text-white">Notifications</p>
            <button
              v-for="item in notifications"
              :key="item.to"
              class="flex w-full items-start gap-3 rounded-xl p-3 text-left hover:bg-slate-50 dark:hover:bg-slate-800"
              @click="goTo(item.to)"
            >
              <component :is="item.icon" class="mt-0.5 h-4 w-4 text-primary-500" />
              <span>
                <span class="block text-sm font-semibold text-slate-800 dark:text-slate-100">{{ item.title }}</span>
                <span class="block text-xs text-slate-500 dark:text-slate-400">{{ item.text }}</span>
              </span>
            </button>
          </div>
        </Transition>
      </div>

      <!-- Theme Toggle -->
      <ThemeToggle />

      <!-- Avatar -->
      <button
        class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-400
                     to-cyan-500 flex items-center justify-center text-white
                     font-bold text-sm shadow-sm hover:shadow-md transition-shadow"
        @click="goTo('/settings')"
      >
        A
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, ChevronRight, Search, Bell, Banknote, ClipboardList, UserPlus } from 'lucide-vue-next'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'

defineEmits(['toggle-sidebar'])

const route = useRoute()
const router = useRouter()
const searchQuery = ref('')
const showNotifications = ref(false)
const currentRoute = computed(() => route.meta.title || 'Dashboard')

const notifications = [
  { title: 'Review pending fees', text: 'Open fee records and update payments.', to: '/fees', icon: Banknote },
  { title: 'Add exam results', text: 'Record course marks and grades.', to: '/results', icon: ClipboardList },
  { title: 'Create student profile', text: 'Add a new student from the student page.', to: '/students?add=1', icon: UserPlus },
]

const submitSearch = () => {
  const q = searchQuery.value.trim()
  if (!q) return
  router.push({ path: '/students', query: { search: q } })
}

const goTo = (to) => {
  showNotifications.value = false
  router.push(to)
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
