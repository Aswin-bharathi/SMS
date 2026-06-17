<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Academics</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Browse the Department → Batch → Students hierarchy
        </p>
      </div>
      <div class="flex items-center gap-2 flex-wrap">
        <div class="flex items-center gap-3 rounded-xl bg-white dark:bg-slate-800 px-4 py-2.5 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700">
          <Building2 class="h-5 w-5 text-primary-500" />
          <div class="text-sm">
            <span class="font-bold text-slate-900 dark:text-white">{{ activeDepts.length }}</span>
            <span class="text-slate-400 ml-1">active</span>
          </div>
        </div>
        <div class="flex items-center gap-3 rounded-xl bg-white dark:bg-slate-800 px-4 py-2.5 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700">
          <Layers class="h-5 w-5 text-cyan-500" />
          <div class="text-sm">
            <span class="font-bold text-slate-900 dark:text-white">{{ totalBatches }}</span>
            <span class="text-slate-400 ml-1">batches</span>
          </div>
        </div>
        <div class="flex items-center gap-3 rounded-xl bg-white dark:bg-slate-800 px-4 py-2.5 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700">
          <Users class="h-5 w-5 text-emerald-500" />
          <div class="text-sm">
            <span class="font-bold text-slate-900 dark:text-white">{{ totalStudents }}</span>
            <span class="text-slate-400 ml-1">students</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter bar -->
    <div class="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700">
      <div class="flex flex-wrap items-center gap-3">
        <div class="relative flex-1 min-w-60">
          <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            v-model="search"
            class="w-full rounded-lg border border-slate-200 bg-slate-50 dark:bg-slate-900 dark:border-slate-700 py-2 pl-9 pr-3 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Search departments…"
          />
        </div>
        <label class="flex items-center gap-2 text-sm text-slate-500 cursor-pointer">
          <input
            v-model="showEmpty"
            type="checkbox"
            class="rounded border-slate-300 text-primary-500 focus:ring-primary-500"
          />
          Show empty departments
        </label>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="i in 6"
        :key="i"
        class="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 animate-pulse"
      >
        <div class="h-6 w-3/4 bg-slate-200 dark:bg-slate-700 rounded" />
        <div class="mt-4 grid grid-cols-2 gap-3">
          <div class="h-16 bg-slate-100 dark:bg-slate-700/50 rounded" />
          <div class="h-16 bg-slate-100 dark:bg-slate-700/50 rounded" />
        </div>
      </div>
    </div>

    <!-- Cards -->
    <div v-else-if="filteredDepts.length" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="d in filteredDepts"
        :key="d.name"
        class="group relative overflow-hidden rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 transition-all duration-200 hover:ring-2 hover:ring-primary-500 hover:shadow-xl cursor-pointer"
        @click="goToBatches(d)"
      >
        <!-- Background gradient accent -->
        <div class="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-gradient-to-br from-primary-500/10 to-cyan-500/10 group-hover:scale-150 transition-transform duration-500" />

        <div class="relative">
          <div class="flex items-start justify-between mb-3">
            <div class="min-w-0 flex-1">
              <h3 class="text-lg font-bold text-slate-900 dark:text-white truncate">
                {{ d.department_name }}
              </h3>
              <p class="text-xs text-slate-400 mt-0.5">
                {{ d.department_code || d.name }}
              </p>
            </div>
            <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-cyan-500 text-white shadow-lg shadow-primary-500/30">
              <Building2 class="h-5 w-5" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3 mt-4">
            <div class="rounded-lg bg-slate-50 dark:bg-slate-700/40 p-3">
              <div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                <Layers class="h-3 w-3" />
                Batches
              </div>
              <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                {{ d.batch_count }}
              </p>
            </div>
            <div class="rounded-lg bg-slate-50 dark:bg-slate-700/40 p-3">
              <div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                <Users class="h-3 w-3" />
                Students
              </div>
              <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                {{ d.student_count }}
              </p>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between">
            <span
              v-if="d.batch_count === 0"
              class="text-xs text-amber-500 flex items-center gap-1"
            >
              <AlertCircle class="h-3 w-3" />
              No batches yet
            </span>
            <span v-else class="text-xs text-emerald-500 flex items-center gap-1">
              <CheckCircle class="h-3 w-3" />
              Active
            </span>
            <div class="flex items-center gap-1 text-xs font-semibold text-primary-500 opacity-0 group-hover:opacity-100 transition-opacity">
              Explore
              <ArrowRight class="h-3 w-3" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="rounded-xl bg-white dark:bg-slate-800 p-12 text-center shadow-sm ring-1 ring-slate-200 dark:ring-slate-700">
      <Building2 class="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
      <p class="text-slate-400">No departments match your search.</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { plural } from '@/composables/usePlural'
import {
  AlertCircle, ArrowRight, Building2, CheckCircle,
  Layers, Search, Users,
} from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

const router      = useRouter()
const { callApi } = useApi()

const departments = ref([])
const loading     = ref(false)
const search      = ref('')
const showEmpty   = ref(false)

const activeDepts = computed(() =>
  departments.value.filter(d => d.batch_count > 0)
)

const totalBatches = computed(() =>
  departments.value.reduce((sum, d) => sum + (d.batch_count || 0), 0)
)

const totalStudents = computed(() =>
  departments.value.reduce((sum, d) => sum + (d.student_count || 0), 0)
)

const filteredDepts = computed(() => {
  let list = departments.value
  if (!showEmpty.value) {
    list = list.filter(d => d.batch_count > 0)
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(
      d =>
        d.department_name?.toLowerCase().includes(q) ||
        d.department_code?.toLowerCase().includes(q),
    )
  }
  return list
})

const goToBatches = (d) => {
  router.push(`/academics/${encodeURIComponent(d.name)}/batches`)
}

onMounted(async () => {
  loading.value = true
  try {
    departments.value = (await callApi('sms.api.hierarchy.get_department_tree')) ?? []
  } catch (e) {
    console.error('Failed to load departments:', e)
  } finally {
    loading.value = false
  }
})
</script>
