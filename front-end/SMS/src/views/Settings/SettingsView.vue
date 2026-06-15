<template>
  <div class="space-y-5">
    <div>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
      <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Control app preferences and jump to key management areas</p>
    </div>

    <div class="grid grid-cols-1 gap-5 lg:grid-cols-3">
      <div class="card">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-300">
            <Palette class="h-5 w-5" />
          </div>
          <div>
            <h2 class="font-bold text-slate-900 dark:text-white">Appearance</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">Switch between light and dark UI</p>
          </div>
        </div>
        <div class="mt-6 flex items-center justify-between rounded-xl bg-slate-50 p-4 dark:bg-slate-800/70">
          <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Theme mode</span>
          <ThemeToggle />
        </div>
      </div>

      <div class="card">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-50 text-cyan-600 dark:bg-cyan-500/10 dark:text-cyan-300">
            <Smartphone class="h-5 w-5" />
          </div>
          <div>
            <h2 class="font-bold text-slate-900 dark:text-white">Mobile App</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">PWA is enabled for install</p>
          </div>
        </div>
        <div class="mt-6 rounded-xl bg-slate-50 p-4 text-sm text-slate-500 dark:bg-slate-800/70 dark:text-slate-400">
          Install prompt appears on supported browsers after production build.
        </div>
      </div>

      <div class="card">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300">
            <ShieldCheck class="h-5 w-5" />
          </div>
          <div>
            <h2 class="font-bold text-slate-900 dark:text-white">Backend</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">API proxy and read endpoints ready</p>
          </div>
        </div>
        <div class="mt-6 rounded-xl bg-slate-50 p-4 text-sm text-slate-500 dark:bg-slate-800/70 dark:text-slate-400">
          Create, edit, and delete actions are routed through app APIs.
        </div>
      </div>
    </div>

    <div class="card">
      <h2 class="font-bold text-slate-900 dark:text-white">Management Shortcuts</h2>
      <div class="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <router-link v-for="item in shortcuts" :key="item.to" :to="item.to" class="rounded-2xl border border-slate-200 p-4 transition hover:-translate-y-0.5 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800/70">
          <component :is="item.icon" class="h-5 w-5 text-primary-500" />
          <p class="mt-3 font-semibold text-slate-900 dark:text-white">{{ item.label }}</p>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ item.text }}</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Banknote, BookOpen, Building2, CalendarRange, ClipboardList, Palette, ShieldCheck, Smartphone, Users } from 'lucide-vue-next'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'

const shortcuts = [
  { to: '/students', label: 'Students', text: 'Add, edit, and review student profiles', icon: Users },
  { to: '/fees', label: 'Fees', text: 'Manage billing and payments', icon: Banknote },
  { to: '/fee-structures', label: 'Fee Structures', text: 'Set fixed program-wise fee amounts', icon: ClipboardList },
  { to: '/results', label: 'Results', text: 'Record exam marks and grades', icon: ClipboardList },
  { to: '/courses', label: 'Courses', text: 'Maintain course catalog', icon: BookOpen },
  { to: '/departments', label: 'Departments', text: 'Organize academic departments', icon: Building2 },
  { to: '/programs', label: 'Programs', text: 'Manage programs and departments', icon: Users },
  { to: '/academic-years', label: 'Academic Years', text: 'Track reporting cycles', icon: CalendarRange },
]
</script>
