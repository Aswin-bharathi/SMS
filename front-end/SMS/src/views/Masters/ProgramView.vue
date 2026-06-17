<template>
  <div class="space-y-5">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Programs</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Manage academic programs and their owning departments</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="h-4 w-4" />
        Add Program
      </button>
    </div>

   <!-- Replace the 3 stat cards with these -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="card !p-5 cursor-pointer transition-all"
          :class="statusFilter === '' ? 'ring-2 ring-primary-500' : 'hover:ring-2 hover:ring-primary-400'"
          @click="statusFilter = ''">
        <p class="text-sm text-slate-500 dark:text-slate-400">Total Programs</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ programs.length }}</p>
      </div>
      <div class="card !p-5 cursor-pointer transition-all"
          :class="statusFilter === 'active' ? 'ring-2 ring-emerald-500' : 'hover:ring-2 hover:ring-emerald-400'"
          @click="statusFilter = 'active'">
        <p class="text-sm text-slate-500 dark:text-slate-400">Active Programs</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ activeCount }}</p>
      </div>
      <div class="card !p-5 cursor-pointer transition-all"
          :class="statusFilter === 'inactive' ? 'ring-2 ring-rose-500' : 'hover:ring-2 hover:ring-rose-400'"
          @click="statusFilter = 'inactive'">
        <p class="text-sm text-slate-500 dark:text-slate-400">Inactive Programs</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ inactiveCount }}</p>
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
            <tr v-for="program in filteredPrograms" :key="program.name" class="hover:bg-slate-50 dark:hover:bg-slate-800/60">
              <td class="px-5 py-4">
                <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ program.program_name }}</p>
                <p class="text-xs text-slate-400">{{ program.name }}</p>
              </td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ program.program_code }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ departmentLabel(program.department) }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ program.duration_years || '-' }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ program.total_credits || '-' }}</td>
              <td class="px-5 py-4"><Badge :variant="Number(program.is_active) ? 'Active' : 'Inactive'">{{ Number(program.is_active) ? 'Active' : 'Inactive' }}</Badge></td>
              <td class="px-5 py-4">
                <div class="flex items-center gap-1">
                  <button class="icon-btn" @click="openEdit(program)"><Pencil class="h-4 w-4" /></button>
                  <button class="icon-btn danger" @click="confirmDelete(program)"><Trash2 class="h-4 w-4" /></button>
                </div>
              </td>
            </tr>
            <tr v-if="!filteredPrograms.length">
              <td colspan="7" class="px-5 py-14 text-center text-sm text-slate-400">No programs found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal :show="showModal" :title="editMode ? 'Edit Program' : 'Add Program'" size="lg" @close="closeModal">
      <form class="space-y-5" @submit.prevent="saveProgram">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="label">Program Name *</label>
            <input v-model="form.program_name" class="input-field" required />
          </div>
          <div>
            <label class="label">Program Code *</label>
            <input v-model="form.program_code" class="input-field" required />
          </div>
          <div>
            <label class="label">Department *</label>
            <select v-model="form.department" class="input-field" required>
              <option value="">Select Department</option>
              <option v-for="dept in departments" :key="dept.name" :value="dept.name">
                {{ deptOptionLabel(dept) }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Duration (Years)</label>
            <input v-model.number="form.duration_years" type="number" min="1" class="input-field" />
          </div>
          <div>
            <label class="label">Total Credits</label>
            <input v-model.number="form.total_credits" type="number" min="0" class="input-field" />
          </div>
          <label class="flex items-center gap-3 rounded-xl border border-slate-200 p-3 dark:border-slate-700">
            <input v-model="form.is_active" type="checkbox" :true-value="1" :false-value="0" />
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Active program</span>
          </label>
        </div>
        <div class="flex justify-end gap-3">
          <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving...' : 'Save Program' }}
          </button>
        </div>
      </form>
    </Modal>

    <Modal :show="showDelete" title="Delete Program" size="sm" @close="showDelete = false">
      <p class="text-sm text-slate-500 dark:text-slate-400">Delete program <strong>{{ selected?.program_name }}</strong>?</p>
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancel</button>
        <button class="btn-danger" @click="deleteProgram"><Trash2 class="h-4 w-4" /> Delete</button>
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
const programs = ref([])
const departments = ref([])
const search = ref('')
const saving = ref(false)
const showModal = ref(false)
const showDelete = ref(false)
const editMode = ref(false)
const selected = ref(null)
const form = ref({})
const defaultForm = {
  program_name: '',
  program_code: '',
  department: '',
  duration_years: 4,
  total_credits: 0,
  is_active: 1,
}

const columns = ['Program', 'Code', 'Department', 'Years', 'Credits', 'Status', 'Actions']

// Add these to script
const statusFilter = ref('')
const inactiveCount = computed(() => programs.value.filter((row) => Number(row.is_active) !== 1).length)

const filteredPrograms = computed(() => {
  let list = programs.value
  if (statusFilter.value === 'active') list = list.filter((row) => Number(row.is_active) === 1)
  else if (statusFilter.value === 'inactive') list = list.filter((row) => Number(row.is_active) !== 1)
  const q = search.value.trim().toLowerCase()
  if (!q) return list
  return list.filter((row) =>
    [row.program_name, row.program_code, row.department]
      .filter(Boolean)
      .some((v) => String(v).toLowerCase().includes(q))
  )
})

// Replace deptOptionLabel or just fix the option directly:
const deptOptionLabel = (dept) => {
  if (dept.department_code && dept.department_code !== dept.department_name) {
    return `${dept.department_name} (${dept.department_code})`
  }
  return dept.department_name
}

const activeCount = computed(() => programs.value.filter((row) => Number(row.is_active) === 1).length)

const departmentLabel = (departmentName) => {
  const department = departments.value.find((row) => row.name === departmentName)
  return department ? department.department_name : departmentName || '-'
}

const fetchPrograms = async () => {
  programs.value = await callApi('sms.api.meta.get_programs')
}

const openCreate = () => {
  form.value = { ...defaultForm }
  editMode.value = false
  showModal.value = true
}

const openEdit = (program) => {
  selected.value = program
  form.value = { ...defaultForm, ...program }
  editMode.value = true
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selected.value = null
}

const confirmDelete = (program) => {
  selected.value = program
  showDelete.value = true
}

const saveProgram = async () => {
  saving.value = true
  try {
    if (editMode.value) {
      await callApi('sms.api.meta.update_program', { program_name: selected.value.name, data: form.value }, { method: 'POST' })
    } else {
      await callApi('sms.api.meta.create_program', { data: form.value }, { method: 'POST' })
    }
    closeModal()
    await fetchPrograms()
  } finally {
    saving.value = false
  }
}

const deleteProgram = async () => {
  await callApi('sms.api.meta.delete_program', { program_name: selected.value.name }, { method: 'POST' })
  showDelete.value = false
  await fetchPrograms()
}

onMounted(async () => {
  departments.value = await callApi('sms.api.meta.get_departments')
  await fetchPrograms()
})
</script>
