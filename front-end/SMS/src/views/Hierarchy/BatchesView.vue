<template>
  <div class="space-y-5">
    <!-- Breadcrumb -->
    <nav class="flex items-center gap-2 text-sm">
      <router-link to="/academics" class="text-primary-500 hover:underline flex items-center gap-1">
        <Building2 class="h-3.5 w-3.5" />
        Academics
      </router-link>
      <ChevronRight class="h-4 w-4 text-slate-400" />
      <span class="font-semibold text-slate-700 dark:text-slate-200">{{ deptName }}</span>
    </nav>

    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">
          {{ deptName }}
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {{ batches.length }} batch(es) · Click any batch to view students, attendance, and fees
        </p>
      </div>
      <button
        class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-primary-500 to-cyan-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-primary-500/30 hover:shadow-xl transition-all"
        @click="showAddModal = true"
      >
        <Plus class="h-4 w-4" />
        New Batch
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="i in 3"
        :key="i"
        class="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 h-48 animate-pulse"
      />
    </div>

    <!-- Batch cards -->
    <div v-else-if="batches.length" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="b in batches"
        :key="b.name"
        class="group rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 transition-all duration-200 hover:ring-2 hover:ring-primary-500 hover:shadow-xl cursor-pointer"
        @click="openBatch(b)"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="text-xl font-bold text-slate-900 dark:text-white">
              {{ b.batch_year }}
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">
              {{ b.program || 'No program' }}
            </p>
          </div>
          <div class="flex flex-col items-end gap-1">
            <span :class="statusBadgeClass(b.status)">
              {{ b.status || 'Active' }}
            </span>
            <span class="text-xs text-slate-400">{{ b.current_semester || 'Sem 1' }}</span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3 mt-4">
          <div class="rounded-lg bg-slate-50 dark:bg-slate-700/40 p-3">
            <div class="flex items-center gap-1.5 text-xs text-slate-500">
              <Users class="h-3 w-3" />
              Students
            </div>
            <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
              {{ b.student_count }}
            </p>
          </div>
          <div class="rounded-lg bg-slate-50 dark:bg-slate-700/40 p-3">
            <div class="flex items-center gap-1.5 text-xs text-slate-500">
              <Calendar class="h-3 w-3" />
              Total Sems
            </div>
            <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
              {{ b.total_semesters || 8 }}
            </p>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
          <div class="flex items-center gap-2 text-xs">
            <UserCheck class="h-4 w-4 text-slate-400" />
            <span class="text-slate-500">In-charge:</span>
            <strong
              v-if="b.class_in_charge"
              class="text-slate-700 dark:text-slate-200 truncate"
            >
              {{ b.class_in_charge_name || b.class_in_charge }}
            </strong>
            <span v-else class="text-amber-500 font-medium">Not assigned</span>
          </div>
        </div>

        <div class="mt-3 flex items-center justify-end gap-1 text-xs font-semibold text-primary-500 opacity-0 group-hover:opacity-100 transition-opacity">
          Open batch
          <ArrowRight class="h-3 w-3" />
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="rounded-xl bg-white dark:bg-slate-800 p-12 text-center shadow-sm ring-1 ring-slate-200 dark:ring-slate-700">
      <GraduationCap class="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
      <p class="text-slate-400 mb-4">No batches in this department yet.</p>
      <button
        class="inline-flex items-center gap-2 rounded-xl bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600"
        @click="showAddModal = true"
      >
        <Plus class="h-4 w-4" />
        Create First Batch
      </button>
    </div>

    <!-- Add Batch Modal -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      @click.self="showAddModal = false"
    >
      <div class="w-full max-w-md rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-slate-900 dark:text-white">Create New Batch</h2>
          <button
            class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            @click="showAddModal = false"
          >
            <X class="h-5 w-5" />
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="createBatch">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Batch Year *
            </label>
            <input
              v-model="form.batch_year"
              class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="e.g. 2024-2028"
              required
            />
            <p class="text-xs text-slate-400 mt-1">
              Department: <strong>{{ deptName }}</strong>
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Program
            </label>
            <select
              v-model="form.program"
              class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Select Program</option>
              <option v-for="p in programs" :key="p.name" :value="p.name">
                {{ p.program_name }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Current Semester
              </label>
              <select
                v-model="form.current_semester"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option v-for="i in 8" :key="i" :value="`Sem ${i}`">Sem {{ i }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Total Semesters
              </label>
              <input
                v-model.number="form.total_semesters"
                type="number"
                min="1"
                max="12"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Class In-Charge
            </label>
            <select
              v-model="form.class_in_charge"
              class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">No in-charge yet</option>
              <option v-for="u in users" :key="u.name" :value="u.name">
                {{ u.full_name }} ({{ u.email }})
              </option>
            </select>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              class="rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
              @click="showAddModal = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600 disabled:opacity-50"
              :disabled="saving"
            >
              <Save class="h-4 w-4" />
              {{ saving ? 'Creating…' : 'Create Batch' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowRight, Building2, Calendar, ChevronRight, GraduationCap,
  Plus, Save, UserCheck, Users, X,
} from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

const route       = useRoute()
const router      = useRouter()
const { callApi } = useApi()
const deptName    = decodeURIComponent(route.params.dept)

const batches      = ref([])
const programs     = ref([])
const users        = ref([])
const loading      = ref(false)
const saving       = ref(false)
const showAddModal = ref(false)

const form = ref({
  batch_year: '',
  program: '',
  current_semester: 'Sem 1',
  total_semesters: 8,
  class_in_charge: '',
})

const loadBatches = async () => {
  loading.value = true
  try {
    batches.value = (await callApi(
      'sms.api.hierarchy.get_batches_under_dept',
      { department: deptName },
    )) ?? []
  } catch (e) {
    console.error('Failed to load batches:', e)
  } finally {
    loading.value = false
  }
}

const openBatch = (b) => {
  router.push(`/batches/${encodeURIComponent(b.name)}`)
}

const statusBadgeClass = (status) => {
  const base = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold'
  const map = {
    'Active':    'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300',
    'Upcoming':  'bg-blue-50 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300',
    'Graduated': 'bg-purple-50 text-purple-700 dark:bg-purple-500/20 dark:text-purple-300',
    'Archived':  'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400',
  }
  return `${base} ${map[status] || map.Active}`
}

const createBatch = async () => {
  saving.value = true
  try {
    await callApi(
      'frappe.client.insert',
      {
        doc: {
          doctype: 'Batch',
          department: deptName,
          batch_year: form.value.batch_year,
          program: form.value.program || null,
          current_semester: form.value.current_semester,
          total_semesters: form.value.total_semesters,
          class_in_charge: form.value.class_in_charge || null,
          is_active: 1,
        },
      },
      { method: 'POST' },
    )
    showAddModal.value = false
    form.value = {
      batch_year: '', program: '',
      current_semester: 'Sem 1', total_semesters: 8,
      class_in_charge: '',
    }
    await loadBatches()
  } catch (e) {
    alert(e?.message || 'Failed to create batch')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadBatches()
  try {
    programs.value = (await callApi('sms.api.meta.get_programs')) ?? []
  } catch {}
  try {
    const r = await fetch(
      '/api/method/frappe.client.get_list?doctype=User&filters=[["enabled","=",1],["user_type","=","System User"]]&fields=["name","full_name","email"]&limit_page_length=0',
      { credentials: 'include' },
    )
    const j = await r.json()
    users.value = j.message ?? []
  } catch {}
})
</script>
