<template>
  <div class="space-y-5">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Academic Years</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Track academic cycles and current year status</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="h-4 w-4" />
        Add Academic Year
      </button>
    </div>

    <!-- Replace the 3 stat cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="card !p-5 cursor-pointer transition-all"
          :class="statusFilter === '' ? 'ring-2 ring-primary-500' : 'hover:ring-2 hover:ring-primary-400'"
          @click="statusFilter = ''">
        <p class="text-sm text-slate-500 dark:text-slate-400">Total Years</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ academicYears.length }}</p>
      </div>
      <div class="card !p-5 cursor-pointer transition-all"
          :class="statusFilter === 'current' ? 'ring-2 ring-emerald-500' : 'hover:ring-2 hover:ring-emerald-400'"
          @click="statusFilter = 'current'">
        <p class="text-sm text-slate-500 dark:text-slate-400">Current Year</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ currentYearLabel }}</p>
      </div>
      <div class="card !p-5 cursor-pointer transition-all"
          :class="statusFilter === 'archived' ? 'ring-2 ring-slate-500' : 'hover:ring-2 hover:ring-slate-400'"
          @click="statusFilter = 'archived'">
        <p class="text-sm text-slate-500 dark:text-slate-400">Visible Rows</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ filteredAcademicYears.length }}</p>
      </div>
    </div>

    <div class="card !p-4">
      <div class="relative">
        <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input v-model="search" class="input-field py-2 pl-9 text-sm" placeholder="Search academic years..." />
      </div>
    </div>

    <div class="card !p-0 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 dark:border-slate-700">
              <th v-for="col in columns" :key="col" class="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
            <tr v-for="year in filteredAcademicYears" :key="year.name" class="hover:bg-slate-50 dark:hover:bg-slate-800/60">
              <td class="px-5 py-4">
                <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ year.year_name }}</p>
                <p class="text-xs text-slate-400">{{ year.name }}</p>
              </td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ year.start_date }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ year.end_date }}</td>
              <td class="px-5 py-4"><Badge :variant="Number(year.is_current) ? 'Active' : 'Inactive'">{{ Number(year.is_current) ? 'Current' : 'Archived' }}</Badge></td>
              <td class="px-5 py-4">
                <div class="flex items-center gap-1">
                  <button class="icon-btn" @click="openEdit(year)"><Pencil class="h-4 w-4" /></button>
                  <button class="icon-btn danger" @click="confirmDelete(year)"><Trash2 class="h-4 w-4" /></button>
                </div>
              </td>
            </tr>
            <tr v-if="!filteredAcademicYears.length">
              <td colspan="5" class="px-5 py-14 text-center text-sm text-slate-400">No academic years found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal :show="showModal" :title="editMode ? 'Edit Academic Year' : 'Add Academic Year'" size="lg" @close="closeModal">
      <form class="space-y-5" @submit.prevent="saveAcademicYear">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="label">Academic Year *</label>
            <input v-model="form.year_name" class="input-field" required placeholder="2026-27" />
          </div>
          <div>
            <label class="label">Start Date *</label>
            <input v-model="form.start_date" type="date" class="input-field" required />
          </div>
          <div>
            <label class="label">End Date *</label>
            <input v-model="form.end_date" type="date" class="input-field" required />
          </div>
          <label class="flex items-center gap-3 rounded-xl border border-slate-200 p-3 dark:border-slate-700">
            <input v-model="form.is_current" type="checkbox" :true-value="1" :false-value="0" />
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Mark as current year</span>
          </label>
        </div>
        <div class="flex justify-end gap-3">
          <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving...' : 'Save Academic Year' }}
          </button>
        </div>
      </form>
    </Modal>

    <Modal :show="showDelete" title="Delete Academic Year" size="sm" @close="showDelete = false">
      <p class="text-sm text-slate-500 dark:text-slate-400">Delete academic year <strong>{{ selected?.year_name }}</strong>?</p>
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancel</button>
        <button class="btn-danger" @click="deleteAcademicYear"><Trash2 class="h-4 w-4" /> Delete</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Pencil, Plus, Save, Search, Trash2 } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import Modal from '@/components/ui/Modal.vue'
import { useApi } from '@/composables/useApi'

const { callApi } = useApi()
const academicYears = ref([])
const search = ref('')
const saving = ref(false)
const showModal = ref(false)
const showDelete = ref(false)
const editMode = ref(false)
const selected = ref(null)
const form = ref({})
const defaultForm = {
  year_name: '',
  start_date: '',
  end_date: '',
  is_current: 0,
}

const columns = ['Academic Year', 'Start Date', 'End Date', 'Status', 'Actions']

// Add to script
const statusFilter = ref('')

const filteredAcademicYears = computed(() => {
  let list = academicYears.value
  if (statusFilter.value === 'current') list = list.filter((row) => Number(row.is_current) === 1)
  else if (statusFilter.value === 'archived') list = list.filter((row) => Number(row.is_current) !== 1)
  const q = search.value.trim().toLowerCase()
  if (!q) return list
  return list.filter((row) =>
    [row.year_name, row.start_date, row.end_date]
      .filter(Boolean)
      .some((v) => String(v).toLowerCase().includes(q))
  )
})
const currentYearLabel = computed(() => {
  const current = academicYears.value.find((row) => Number(row.is_current) === 1)
  return current ? current.year_name : 'None'
})

const fetchAcademicYears = async () => {
  academicYears.value = await callApi('sms.api.meta.get_academic_years')
}

const openCreate = () => {
  form.value = { ...defaultForm }
  editMode.value = false
  showModal.value = true
}

const openEdit = (year) => {
  selected.value = year
  form.value = { ...defaultForm, ...year }
  editMode.value = true
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selected.value = null
}

const confirmDelete = (year) => {
  selected.value = year
  showDelete.value = true
}

const saveAcademicYear = async () => {
  saving.value = true
  try {
    if (editMode.value) {
      await callApi('sms.api.meta.update_academic_year', { year_name: selected.value.name, data: form.value }, { method: 'POST' })
    } else {
      await callApi('sms.api.meta.create_academic_year', { data: form.value }, { method: 'POST' })
    }
    closeModal()
    await fetchAcademicYears()
  } finally {
    saving.value = false
  }
}

const deleteAcademicYear = async () => {
  await callApi('sms.api.meta.delete_academic_year', { year_name: selected.value.name }, { method: 'POST' })
  showDelete.value = false
  await fetchAcademicYears()
}

onMounted(fetchAcademicYears)
</script>
