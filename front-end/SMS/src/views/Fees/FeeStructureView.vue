<template>
  <div class="space-y-5">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Fee Structures</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Define fixed program-wise fees for each fee type</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="h-4 w-4" />
        Add Structure
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div class="card !p-5">
        <p class="text-sm text-slate-500 dark:text-slate-400">Structures</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ structures.length }}</p>
      </div>
      <div class="card !p-5">
        <p class="text-sm text-slate-500 dark:text-slate-400">Active</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ activeCount }}</p>
      </div>
      <div class="card !p-5">
        <p class="text-sm text-slate-500 dark:text-slate-400">Total Value</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ money(totalValue) }}</p>
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
            <tr v-for="structure in structures" :key="structure.name" class="hover:bg-slate-50 dark:hover:bg-slate-800/60">
              <td class="px-5 py-4 text-sm font-semibold text-slate-900 dark:text-white">{{ programLabel(structure.program) }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ structure.fee_type }}</td>
              <td class="px-5 py-4 text-sm font-semibold text-slate-900 dark:text-white">{{ money(structure.amount) }}</td>
              <td class="px-5 py-4"><Badge :variant="Number(structure.is_active) ? 'Active' : 'Inactive'">{{ Number(structure.is_active) ? 'Active' : 'Inactive' }}</Badge></td>
              <td class="px-5 py-4">
                <div class="flex items-center gap-1">
                  <button class="icon-btn" @click="openEdit(structure)"><Pencil class="h-4 w-4" /></button>
                  <button class="icon-btn danger" @click="confirmDelete(structure)"><Trash2 class="h-4 w-4" /></button>
                </div>
              </td>
            </tr>
            <tr v-if="!structures.length">
              <td colspan="5" class="px-5 py-14 text-center text-sm text-slate-400">No fee structures found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal :show="showModal" :title="editMode ? 'Edit Fee Structure' : 'Add Fee Structure'" size="lg" @close="closeModal">
      <form class="space-y-5" @submit.prevent="saveStructure">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="label">Program *</label>
            <select v-model="form.program" class="input-field" required>
              <option value="">Select Program</option>
              <option v-for="program in programs" :key="program.name" :value="program.name">
                {{ program.program_code }} - {{ program.program_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Fee Type *</label>
            <select v-model="form.fee_type" class="input-field" required>
              <option>Tuition Fee</option>
              <option>Exam Fee</option>
              <option>Library Fee</option>
              <option>Lab Fee</option>
              <option>Hostel Fee</option>
              <option>Other</option>
            </select>
          </div>
          <div>
            <label class="label">Amount *</label>
            <input v-model.number="form.amount" type="number" min="0" class="input-field" required />
          </div>
          <label class="flex items-center gap-3 rounded-xl border border-slate-200 p-3 dark:border-slate-700">
            <input v-model="form.is_active" type="checkbox" :true-value="1" :false-value="0" />
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Active structure</span>
          </label>
        </div>
        <div class="flex justify-end gap-3">
          <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving...' : 'Save Structure' }}
          </button>
        </div>
      </form>
    </Modal>

    <Modal :show="showDelete" title="Delete Fee Structure" size="sm" @close="showDelete = false">
      <p class="text-sm text-slate-500 dark:text-slate-400">Delete fee structure <strong>{{ selected?.fee_type }}</strong>?</p>
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancel</button>
        <button class="btn-danger" @click="deleteStructure"><Trash2 class="h-4 w-4" /> Delete</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Pencil, Plus, Save, Trash2 } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import Modal from '@/components/ui/Modal.vue'
import { useApi } from '@/composables/useApi'

const { callApi } = useApi()
const structures = ref([])
const programs = ref([])
const saving = ref(false)
const showModal = ref(false)
const showDelete = ref(false)
const editMode = ref(false)
const selected = ref(null)
const form = ref({})
const defaultForm = { program: '', fee_type: 'Tuition Fee', amount: 0, is_active: 1 }

const columns = ['Program', 'Fee Type', 'Amount', 'Status', 'Actions']
const money = (value) => `₹${Number(value || 0).toLocaleString()}`

const totalValue = computed(() => structures.value.reduce((sum, row) => sum + Number(row.amount || 0), 0))
const activeCount = computed(() => structures.value.filter((row) => Number(row.is_active) === 1).length)

const programLabel = (programName) => {
  const program = programs.value.find((row) => row.name === programName)
  return program ? `${program.program_code} - ${program.program_name}` : programName || '-'
}

const fetchStructures = async () => {
  structures.value = await callApi('sms.api.meta.get_fee_structures')
}

const openCreate = () => {
  form.value = { ...defaultForm }
  editMode.value = false
  showModal.value = true
}

const openEdit = (structure) => {
  selected.value = structure
  form.value = { ...defaultForm, ...structure }
  editMode.value = true
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selected.value = null
}

const confirmDelete = (structure) => {
  selected.value = structure
  showDelete.value = true
}

const saveStructure = async () => {
  saving.value = true
  try {
    if (editMode.value) {
      await callApi('sms.api.meta.update_fee_structure', { structure_name: selected.value.name, data: form.value }, { method: 'POST' })
    } else {
      await callApi('sms.api.meta.create_fee_structure', { data: form.value }, { method: 'POST' })
    }
    closeModal()
    await fetchStructures()
  } finally {
    saving.value = false
  }
}

const deleteStructure = async () => {
  await callApi('sms.api.meta.delete_fee_structure', { structure_name: selected.value.name }, { method: 'POST' })
  showDelete.value = false
  await fetchStructures()
}

onMounted(async () => {
  programs.value = await callApi('sms.api.meta.get_programs')
  await fetchStructures()
})
</script>
