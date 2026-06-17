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
          <div
            v-if="isItemActive(item)"
            class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary-600 rounded-r-full"
          />

          <component
            :is="item.icon"
            :class="['w-5 h-5 shrink-0', isItemActive(item) ? 'text-primary-600 dark:text-primary-400' : '']"
          />

          <Transition name="fade">
            <span v-if="!collapsed" class="text-sm font-medium whitespace-nowrap">
              {{ item.name }}
            </span>
          </Transition>

          <div
            v-if="collapsed"
            class="absolute left-full ml-3 px-2.5 py-1.5 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap transition-opacity z-50"
          >
            {{ item.name }}
          </div>
        </div>
      </router-link>
    </nav>

    <!-- Bottom User Section -->
    <div class="p-4 border-t border-gray-100 dark:border-gray-700 relative">
      <button
        class="w-full flex items-center gap-3 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700/50 p-2 transition-colors"
        @click="showUserMenu = !showUserMenu"
      >
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-400 to-cyan-500 flex items-center justify-center shrink-0 text-white font-bold text-sm">
          {{ initials }}
        </div>
        <Transition name="fade">
          <div v-if="!collapsed" class="overflow-hidden flex-1 text-left">
            <p class="text-sm font-semibold text-gray-800 dark:text-white truncate">
              {{ fullName }}
            </p>
            <p class="text-xs text-gray-400 dark:text-gray-500 truncate">
              {{ roleLabel }}
            </p>
          </div>
        </Transition>
        <ChevronUp
          v-if="!collapsed"
          class="h-4 w-4 text-slate-400 transition-transform"
          :class="showUserMenu ? '' : 'rotate-180'"
        />
      </button>

      <!-- Dropdown menu -->
      <Transition name="fade">
        <div
          v-if="showUserMenu && !collapsed"
          class="absolute bottom-full left-4 right-4 mb-2 rounded-xl bg-white dark:bg-slate-800 shadow-2xl ring-1 ring-slate-200 dark:ring-slate-700 overflow-hidden z-50"
        >
          <div class="px-4 py-3 border-b border-slate-100 dark:border-slate-700">
            <p class="text-xs text-slate-400">Signed in as</p>
            <p class="text-sm font-semibold text-slate-900 dark:text-white truncate">
              {{ email }}
            </p>
          </div>
          <router-link
            v-if="isStudent"
            to="/me/profile"
            class="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50"
            @click="showUserMenu = false"
          >
            <User class="h-4 w-4" />
            My Profile
          </router-link>
          <button
            class="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10"
            @click="handleLogout"
          >
            <LogOut class="h-4 w-4" />
            Log out
          </button>
        </div>
      </Transition>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  GraduationCap, LayoutDashboard, Users, CalendarCheck,
  CreditCard, FileText, BookOpen, Settings, X, Building2,
  CalendarRange, Network, ChevronUp, LogOut, User,
  GraduationCap as ProgramIcon,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'

defineProps({ collapsed: Boolean, mobileOpen: Boolean })
const emit = defineEmits(['close-mobile'])
const route = useRoute()

const { fullName, email, roleLabel, isStudent, logout } = useAuth()
const showUserMenu = ref(false)

const initials = computed(() => {
  const name = fullName.value || 'U'
  return name
    .split(' ')
    .map(n => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})

const handleLogout = async () => {
  showUserMenu.value = false
  await logout()
}

const isItemActive = (item) => {
  if (item.disabled) return false
  if (item.to === '/') return route.path === '/'
  if (route.path === item.to || route.path.startsWith(item.to + '/')) return true
  if (item.to === '/academics' && route.path.startsWith('/batches/')) return true
  return false
}

const handleNavigate = (item, navigate) => {
  if (item.disabled) return
  navigate()
  emit('close-mobile')
}

const navItems = [
  { name: 'Dashboard',      to: '/',                icon: LayoutDashboard },
  { name: 'Academics',      to: '/academics',       icon: Network },
  { name: 'Students',       to: '/students',        icon: Users },
  { name: 'Attendance',     to: '/attendance',      icon: CalendarCheck },
  { name: 'Fees',           to: '/fees',            icon: CreditCard },
  { name: 'Fee Structures', to: '/fee-structures',  icon: FileText },
  { name: 'Results',        to: '/results',         icon: FileText },
  { name: 'Courses',        to: '/courses',         icon: BookOpen },
  { name: 'Departments',    to: '/departments',     icon: Building2 },
  { name: 'Programs',       to: '/programs',        icon: ProgramIcon },
  { name: 'Academic Years', to: '/academic-years',  icon: CalendarRange },
  { name: 'Settings',       to: '/settings',        icon: Settings },
]
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: all 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>
