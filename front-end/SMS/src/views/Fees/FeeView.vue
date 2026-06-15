<template>
  <div class="space-y-5">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Fees</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Manage student invoices and payments</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="h-4 w-4" />
        Add Fee
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div v-for="item in summary" :key="item.label" class="card !p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ item.label }}</p>
            <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ item.value }}</p>
          </div>
          <div :class="['flex h-11 w-11 items-center justify-center rounded-xl', item.bg]">
            <component :is="item.icon" :class="['h-5 w-5', item.color]" />
          </div>
        </div>
      </div>
    </div>

    <div class="card !p-4">
      <div class="flex flex-wrap gap-3">
        <div class="relative min-w-60 flex-1">
          <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input v-model="filters.student" class="input-field py-2 pl-9 text-sm" placeholder="Student ID..." @input="debouncedFetch" />
        </div>
        <select v-model="filters.status" class="input-field w-auto py-2 text-sm" @change="fetchFees">
          <option value="">All Status</option>
          <option>Unpaid</option>
          <option>Partially Paid</option>
          <option>Paid</option>
          <option>Overdue</option>
        </select>
        <button class="btn-secondary text-sm" @click="clearFilters">
          <X class="h-4 w-4" />
          Clear
        </button>
      </div>
    </div>

    <div class="card !p-0 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 dark:border-slate-700">
              <th v-for="col in ['Student', 'Fee Type', 'Due Date', 'Amount', 'Paid', 'Status', 'Actions']" :key="col" class="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
            <tr v-for="fee in fees" :key="fee.name" class="hover:bg-slate-50 dark:hover:bg-slate-800/60">
              <td class="px-5 py-4">
                <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ fee.student_name || fee.student }}</p>
                <p class="text-xs text-slate-400">{{ fee.student }}</p>
              </td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ fee.fee_type }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ fee.due_date || '-' }}</td>
              <td class="px-5 py-4 text-sm font-semibold text-slate-900 dark:text-white">{{ money(fee.total_amount) }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ money(fee.paid_amount) }}</td>
              <td class="px-5 py-4"><Badge :variant="fee.payment_status">{{ fee.payment_status }}</Badge></td>
              <td class="px-5 py-4">
                <div class="flex items-center gap-1">
                  <button class="icon-btn" @click="openEdit(fee)"><Pencil class="h-4 w-4" /></button>
                  <button class="icon-btn danger" @click="confirmDelete(fee)"><Trash2 class="h-4 w-4" /></button>
                </div>
              </td>
            </tr>
            <tr v-if="!loading && !fees.length">
              <td colspan="7" class="px-5 py-14 text-center text-sm text-slate-400">No fee records found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal :show="showModal" :title="editMode ? 'Edit Fee' : 'Add Fee'" size="lg" @close="closeModal">
      <form class="space-y-5" @submit.prevent="saveFee">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="label">Student *</label>
            <select v-model="form.student" class="input-field" required @change="syncStudentDefaults">
              <option value="">Select Student</option>
              <option v-for="student in students" :key="student.name" :value="student.student_id || student.name">
                {{ student.student_id || student.name }} - {{ student.full_name || student.student_id }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Fee Type *</label>
            <select v-model="form.fee_type" class="input-field" required @change="syncFeeStructure">
              <option>Tuition Fee</option>
              <option>Exam Fee</option>
              <option>Library Fee</option>
              <option>Lab Fee</option>
              <option>Hostel Fee</option>
              <option>Other</option>
            </select>
          </div>
          <div>
            <label class="label">Academic Year</label>
            <input v-model="form.academic_year" class="input-field" placeholder="2026-27" />
          </div>
          <div>
            <label class="label">Due Date *</label>
            <input v-model="form.due_date" type="date" class="input-field" required />
          </div>
          <div>
            <label class="label">Total Amount *</label>
            <input v-model.number="form.total_amount" type="number" min="0" class="input-field bg-slate-50 dark:bg-slate-800/80" readonly required />
          </div>
          <div>
            <label class="label">Paid Amount</label>
            <input v-model.number="form.paid_amount" type="number" min="0" class="input-field" @input="syncRemaining" />
          </div>
          <div>
            <label class="label">Payment Date</label>
            <input v-model="form.payment_date" type="date" class="input-field" />
          </div>
          <div>
            <label class="label">Payment Method</label>
            <select v-model="form.payment_method" class="input-field">
              <option value="">Select Method</option>
              <option>Cash</option>
              <option>Bank Transfer</option>
              <option>Online</option>
              <option>Cheque</option>
            </select>
          </div>
          <div>
            <label class="label">Transaction ID</label>
            <input v-model="form.transaction_id" class="input-field" placeholder="TXN123456" />
          </div>
          <div class="sm:col-span-2">
            <label class="label">Remarks</label>
            <textarea v-model="form.remarks" class="input-field" rows="2" />
          </div>
          <div class="sm:col-span-2 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70">
              <p class="text-xs text-slate-400">Base Fee</p>
              <p class="mt-1 text-lg font-bold text-slate-900 dark:text-white">{{ money(form.total_amount) }}</p>
            </div>
            <div class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70">
              <p class="text-xs text-slate-400">Paid</p>
              <p class="mt-1 text-lg font-bold text-slate-900 dark:text-white">{{ money(form.paid_amount) }}</p>
            </div>
            <div class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70">
              <p class="text-xs text-slate-400">Remaining</p>
              <p class="mt-1 text-lg font-bold text-amber-600 dark:text-amber-400">{{ money(remainingAmount) }}</p>
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-3">
          <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving...' : 'Save Fee' }}
          </button>
        </div>
      </form>
    </Modal>

    <Modal :show="showDelete" title="Delete Fee" size="sm" @close="showDelete = false">
      <p class="text-sm text-slate-500 dark:text-slate-400">Delete fee record <strong>{{ selected?.name }}</strong>?</p>
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancel</button>
        <button class="btn-danger" @click="deleteFee"><Trash2 class="h-4 w-4" /> Delete</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Banknote, CheckCircle, Clock, IndianRupee, Pencil, Plus, Save, Search, Trash2, X } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import Modal from '@/components/ui/Modal.vue'
import { useApi } from '@/composables/useApi'

const { callApi } = useApi()
const students = ref([])
const feeStructures = ref([])
const fees = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showDelete = ref(false)
const editMode = ref(false)
const selected = ref(null)
const filters = ref({ student: '', status: '' })
const form = ref({})

const defaultForm = {
  student: '', student_name: '', program: '', fee_type: 'Tuition Fee', academic_year: '', due_date: '',
  total_amount: 0, paid_amount: 0, payment_date: '', payment_method: '', transaction_id: '', remarks: ''
}

const money = (value) => `₹${Number(value || 0).toLocaleString()}`
const summary = computed(() => {
  const total = fees.value.reduce(
    (sum, fee) => sum + Number(fee.total_amount || 0), 0
  )

  const paid = fees.value.reduce(
    (sum, fee) => sum + Number(fee.paid_amount || 0), 0
  )

  const outstanding = fees.value.reduce(
    (sum, fee) => sum + Number(fee.outstanding_amount || 0), 0
  )

  return [
    {
      label: 'Total Billed',
      value: money(total),
      icon: IndianRupee,
      bg: 'bg-primary-50 dark:bg-primary-500/10',
      color: 'text-primary-600 dark:text-primary-300'
    },
    {
      label: 'Collected',
      value: money(paid),
      icon: CheckCircle,
      bg: 'bg-emerald-50 dark:bg-emerald-500/10',
      color: 'text-emerald-600 dark:text-emerald-300'
    },
    {
      label: 'Outstanding',
      value: money(outstanding),   // ✅ FIXED
      icon: Clock,
      bg: 'bg-amber-50 dark:bg-amber-500/10',
      color: 'text-amber-600 dark:text-amber-300'
    },
    {
      label: 'Records',
      value: fees.value.length,
      icon: Banknote,
      bg: 'bg-cyan-50 dark:bg-cyan-500/10',
      color: 'text-cyan-600 dark:text-cyan-300'
    },
  ]
})

const remainingAmount = computed(() => Number(form.value.total_amount || 0) - Number(form.value.paid_amount || 0))

const fetchFees = async () => {
  loading.value = true
  try {
    fees.value = await callApi('sms.api.fee.get_fees', {
      student: filters.value.student || undefined,
      status: filters.value.status || undefined,
    })
  } finally {
    loading.value = false
  }
}

const syncStudentDefaults = () => {
  const student = students.value.find((row) => (row.student_id || row.name) === form.value.student)
  if (!student) return
  form.value.student_name = student.full_name || student.student_id || student.name
  form.value.program = student.program || form.value.program
  form.value.academic_year = student.academic_year || form.value.academic_year
  syncFeeStructure()
}

const syncFeeStructure = () => {
  const structure = feeStructures.value.find((row) =>
    row.program === form.value.program &&
    row.fee_type === form.value.fee_type &&
    Number(row.is_active) === 1
  )
  if (!structure) return
  form.value.total_amount = Number(structure.amount || 0)
  syncRemaining()
}

const syncRemaining = () => {
  if (Number(form.value.paid_amount || 0) > Number(form.value.total_amount || 0)) {
    form.value.paid_amount = Number(form.value.total_amount || 0)
  }
}

let timer = null
const debouncedFetch = () => { clearTimeout(timer); timer = setTimeout(fetchFees, 350) }
const clearFilters = () => { filters.value = { student: '', status: '' }; fetchFees() }
const openCreate = () => { form.value = { ...defaultForm }; editMode.value = false; showModal.value = true }
const openEdit = (fee) => {
  selected.value = fee
  form.value = { ...defaultForm, ...fee }
  syncStudentDefaults()
  syncFeeStructure()
  editMode.value = true
  showModal.value = true
}
const closeModal = () => { showModal.value = false; selected.value = null }
const confirmDelete = (fee) => { selected.value = fee; showDelete.value = true }

const saveFee = async () => {
  saving.value = true
  try {
    if (editMode.value) {
      await callApi('sms.api.fee.update_fee', { fee_name: selected.value.name, data: form.value }, { method: 'POST' })
    } else {
      await callApi('sms.api.fee.create_fee', { data: form.value }, { method: 'POST' })
    }
    closeModal()
    fetchFees()
  } finally {
    saving.value = false
  }
}

const deleteFee = async () => {
  await callApi('sms.api.fee.delete_fee', { fee_name: selected.value.name }, { method: 'POST' })
  showDelete.value = false
  fetchFees()
}

onMounted(async () => {
  students.value = await callApi('sms.api.meta.get_student_options')
  feeStructures.value = await callApi('sms.api.meta.get_fee_structures')
  syncStudentDefaults()
  syncFeeStructure()
})

onMounted(fetchFees)
</script>
