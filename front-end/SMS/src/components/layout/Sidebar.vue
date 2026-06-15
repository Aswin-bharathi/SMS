<template>
  <aside
    :class="[
      'fixed left-0 top-0 z-40 flex h-full flex-col',
      'border-r border-white/70 bg-white/90 shadow-xl shadow-slate-200/60 backdrop-blur-xl',
      'dark:border-slate-700/70 dark:bg-slate-900/95 dark:shadow-slate-950/30',
      'transition-all duration-300',
      collapsed ? 'lg:w-20' : 'lg:w-64',
      mobileOpen ? 'translate-x-0 w-72' : '-translate-x-full lg:translate-x-0',
      !collapsed ? 'w-72' : ''
    ]"
  >
    <!-- Logo -->
    <div class="flex items-center h-16 px-4 border-b border-gray-100 dark:border-gray-700">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center shrink-0 shadow-lg shadow-primary-500/25">
          <GraduationCap class="w-5 h-5 text-white" />
        </div>
        <Transition name="fade">
          <div v-if="!collapsed" class="overflow-hidden">
            <p class="font-bold text-gray-800 dark:text-white text-sm leading-tight">
              EduManage
            </p>
            <p class="text-xs text-gray-400 dark:text-gray-500">Student System</p>
          </div>
        </Transition>
      </div>
      <button
        class="ml-auto flex h-9 w-9 items-center justify-center rounded-xl text-gray-400 hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-slate-800 dark:hover:text-white lg:hidden"
        @click="$emit('close-mobile')"
      >
        <X class="h-5 w-5" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 space-y-1 overflow-y-auto px-2 py-4">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        custom
        :to="item.to"
        v-slot="{ navigate }"
      >
        <div
          :class="[
            'flex items-center gap-3 px-3 py-2.5 rounded-xl',
            'transition-all duration-200 group relative',
            item.disabled
              ? 'cursor-not-allowed text-slate-400/70 dark:text-slate-600'
              : 'cursor-pointer',
            isItemActive(item)
              ? 'bg-primary-50 text-primary-700 shadow-sm ring-1 ring-primary-100 dark:bg-primary-500/10 dark:text-primary-300 dark:ring-primary-500/20'
              : !item.disabled
                ? 'text-gray-500 dark:text-gray-400 hover:bg-slate-100/80 hover:text-gray-800 dark:hover:bg-slate-800/80 dark:hover:text-white'
                : ''
          ]"
          @click="handleNavigate(item, navigate)"
        >
          <!-- Active Indicator -->
          <div
            v-if="isItemActive(item)"
            class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary-600 rounded-r-full"
          />

          <!-- Icon -->
          <component
            :is="item.icon"
            :class="['w-5 h-5 shrink-0', isItemActive(item) ? 'text-primary-600 dark:text-primary-400' : '']"
          />

          <!-- Label -->
          <Transition name="fade">
            <span v-if="!collapsed" class="text-sm font-medium whitespace-nowrap">
              {{ item.name }}
            </span>
          </Transition>

          <span
            v-if="item.disabled && !collapsed"
            class="ml-auto rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-500 dark:bg-slate-800 dark:text-slate-500"
          >
            Soon
          </span>

          <!-- Tooltip when collapsed -->
          <div
            v-if="collapsed"
            class="absolute left-full ml-3 px-2.5 py-1.5 bg-gray-900 text-white
                   text-xs rounded-lg opacity-0 group-hover:opacity-100
                   pointer-events-none whitespace-nowrap transition-opacity z-50"
          >
            {{ item.name }}
          </div>
        </div>
      </router-link>
    </nav>

    <!-- Bottom User Section -->
    <div class="p-4 border-t border-gray-100 dark:border-gray-700">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-400 to-cyan-500
                    flex items-center justify-center shrink-0 text-white font-bold text-sm">
          A
        </div>
        <Transition name="fade">
          <div v-if="!collapsed" class="overflow-hidden">
            <p class="text-sm font-semibold text-gray-800 dark:text-white truncate">Admin</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 truncate">System Manager</p>
          </div>
        </Transition>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'
import {
  GraduationCap, LayoutDashboard, Users, CalendarCheck,
  CreditCard, FileText, BookOpen, Settings, X, Building2, CalendarRange, GraduationCap as ProgramIcon
} from 'lucide-vue-next'

defineProps({ collapsed: Boolean, mobileOpen: Boolean })
const emit = defineEmits(['close-mobile'])
const route = useRoute()

const isItemActive = (item) => !item.disabled && route.path === item.to

const handleNavigate = (item, navigate) => {
  if (item.disabled) return
  navigate()
  emit('close-mobile')
}

const navItems = [
  { name: 'Dashboard',  to: '/',           icon: LayoutDashboard },
  { name: 'Students',   to: '/students',   icon: Users },
  { name: 'Attendance', to: '/attendance', icon: CalendarCheck },
  { name: 'Fees',       to: '/fees',       icon: CreditCard },
  { name: 'Fee Structures', to: '/fee-structures', icon: FileText },
  { name: 'Results',    to: '/results',    icon: FileText },
  { name: 'Courses',    to: '/courses',    icon: BookOpen },
  { name: 'Departments', to: '/departments', icon: Building2 },
  { name: 'Programs',    to: '/programs',    icon: ProgramIcon },
  { name: 'Academic Years', to: '/academic-years', icon: CalendarRange },
  { name: 'Settings',   to: '/settings',   icon: Settings },
]
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s, width 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
