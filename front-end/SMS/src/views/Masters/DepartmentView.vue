<template>
  <div class="space-y-5">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Departments</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Manage departments and academic ownership</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="h-4 w-4" />
        Add Department
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="card !p-5">
        <p class="text-sm text-slate-500 dark:text-slate-400">Total Departments</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ departments.length }}</p>
      </div>
      <div class="card !p-5">
        <p class="text-sm text-slate-500 dark:text-slate-400">Active Departments</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ activeCount }}</p>
      </div>
      <div class="card !p-5">
        <p class="text-sm text-slate-500 dark:text-slate-400">Visible Rows</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ filteredDepartments.length }}</p>
      </div>
    </div>

    <div class="card !p-4">
      <div class="relative">
        <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input v-model="search" class="input-field py-2 pl-9 text-sm" placeholder="Search departments..." />
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
            <tr v-for="department in filteredDepartments" :key="department.name" class="hover:bg-slate-50 dark:hover:bg-slate-800/60">
              <td class="px-5 py-4">
                <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ department.department_name }}</p>
                <p class="text-xs text-slate-400">{{ department.name }}</p>
              </td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ department.department_code || '-' }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ department.head_of_department || '-' }}</td>
              <td class="px-5 py-4"><Badge :variant="Number(department.is_active) ? 'Active' : 'Inactive'">{{ Number(department.is_active) ? 'Active' : 'Inactive' }}</Badge></td>
              <td class="px-5 py-4">
                <div class="flex items-center gap-1">
                  <button class="icon-btn" @click="openEdit(department)"><Pencil class="h-4 w-4" /></button>
                  <button class="icon-btn danger" @click="confirmDelete(department)"><Trash2 class="h-4 w-4" /></button>
                </div>
              </td>
            </tr>
            <tr v-if="!filteredDepartments.length">
              <td colspan="5" class="px-5 py-14 text-center text-sm text-slate-400">No departments found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal :show="showModal" :title="editMode ? 'Edit Department' : 'Add Department'" size="lg" @close="closeModal">
      <form class="space-y-5" @submit.prevent="saveDepartment">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="label">Department Name *</label>
            <input v-model="form.department_name" class="input-field" required />
          </div>
          <div>
            <label class="label">Department Code</label>
            <input v-model="form.department_code" class="input-field" />
          </div>
          <div>
            <label class="label">Head of Department</label>
            <input v-model="form.head_of_department" class="input-field" />
          </div>
          <label class="flex items-center gap-3 rounded-xl border border-slate-200 p-3 dark:border-slate-700">
            <input v-model="form.is_active" type="checkbox" :true-value="1" :false-value="0" />
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Active department</span>
          </label>
        </div>
        <div class="flex justify-end gap-3">
          <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving...' : 'Save Department' }}
          </button>
        </div>
      </form>
    </Modal>

    <Modal :show="showDelete" title="Delete Department" size="sm" @close="showDelete = false">
      <p class="text-sm text-slate-500 dark:text-slate-400">Delete department <strong>{{ selected?.department_name }}</strong>?</p>
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancel</button>
        <button class="btn-danger" @click="deleteDepartment"><Trash2 class="h-4 w-4" /> Delete</button>
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
const departments = ref([])
const search = ref('')
const saving = ref(false)
const showModal = ref(false)
const showDelete = ref(false)
const editMode = ref(false)
const selected = ref(null)
const form = ref({})
const defaultForm = {
  department_name: '',
  department_code: '',
  head_of_department: '',
  is_active: 1,
}

const columns = ['Department', 'Code', 'Head', 'Status', 'Actions']

const filteredDepartments = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return departments.value
  return departments.value.filter((row) =>
    [row.department_name, row.department_code, row.head_of_department]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(q))
  )
})

const activeCount = computed(() => departments.value.filter((row) => Number(row.is_active) === 1).length)

const fetchDepartments = async () => {
  departments.value = await callApi('sms.api.meta.get_departments')
}

const openCreate = () => {
  form.value = { ...defaultForm }
  editMode.value = false
  showModal.value = true
}

const openEdit = (department) => {
  selected.value = department
  form.value = { ...defaultForm, ...department }
  editMode.value = true
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selected.value = null
}

const confirmDelete = (department) => {
  selected.value = department
  showDelete.value = true
}

const saveDepartment = async () => {
  saving.value = true
  try {
    if (editMode.value) {
      await callApi('sms.api.meta.update_department', { department_name: selected.value.name, data: form.value }, { method: 'POST' })
    } else {
      await callApi('sms.api.meta.create_department', { data: form.value }, { method: 'POST' })
    }
    closeModal()
    await fetchDepartments()
  } finally {
    saving.value = false
  }
}

const deleteDepartment = async () => {
  await callApi('sms.api.meta.delete_department', { department_name: selected.value.name }, { method: 'POST' })
  showDelete.value = false
  await fetchDepartments()
}

onMounted(fetchDepartments)
</script>
