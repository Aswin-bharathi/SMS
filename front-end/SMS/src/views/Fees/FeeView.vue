<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Fees</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Manage student invoices and payments
        </p>
      </div>
      <div class="flex items-center gap-2">
        <button class="btn-secondary text-sm" @click="openBulkAssign">
          <LayersIcon class="h-4 w-4" />
          Bulk Assign
        </button>
        <button class="btn-primary" @click="openCreate">
          <Plus class="h-4 w-4" />
          Add Fee
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="item in summary"
        :key="item.label"
        :class="[
          'card !p-5 transition-all duration-200',
          item.filterKey !== null ? 'cursor-pointer select-none' : 'cursor-default',
          item.filterKey !== null && statusFilter === item.filterKey
            ? `ring-2 ${item.ring}`
            : '',
          item.filterKey !== null && statusFilter !== item.filterKey
            ? `hover:ring-2 hover:${item.ring} hover:shadow-md`
            : '',
        ]"
        @click="setStatusFilter(item.filterKey)"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ item.label }}</p>
            <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {{ item.value }}
            </p>
            <p v-if="item.sub" class="mt-0.5 text-xs text-slate-400">{{ item.sub }}</p>
          </div>
          <div :class="['flex h-11 w-11 items-center justify-center rounded-xl', item.bg]">
            <component :is="item.icon" :class="['h-5 w-5', item.color]" />
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card !p-4">
      <div class="flex flex-wrap gap-3">
        <div class="relative min-w-56 flex-1">
          <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            v-model="filters.student"
            class="input-field py-2 pl-9 text-sm"
            placeholder="Search by Student ID or name…"
            @input="onStudentSearch"
          />
        </div>
        <select
          v-model="filters.semester"
          class="input-field w-auto py-2 text-sm"
          @change="fetchFees"
        >
          <option value="">All Semesters</option>``
          <option v-for="sem in semesterOptions" :key="sem" :value="sem">{{ sem }}</option>
        </select>
        <select
          v-model="filters.academic_year"
          class="input-field w-auto py-2 text-sm"
          @change="fetchFees"
        >
          <option value="">All Years</option>
          <option v-for="yr in academicYearOptions" :key="yr" :value="yr">{{ yr }}</option>
        </select>
        <select
          v-model="filters.status"
          class="input-field w-auto py-2 text-sm"
          @change="fetchFees"
        >
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

    <!-- Table -->
    <div class="card !p-0 overflow-hidden">
      <!-- Loading bar -->
      <div v-if="loading" class="h-1 w-full overflow-hidden bg-slate-100 dark:bg-slate-700">
        <div class="h-full animate-pulse bg-primary-500" style="width: 60%" />
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 dark:border-slate-700">
              <th
                v-for="col in columns"
                :key="col"
                class="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
            <tr
              v-for="fee in displayedFees"
              :key="fee.name"
              class="transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/60"
            >
              <!-- Student -->
              <td class="px-5 py-4">
                <p class="text-sm font-semibold text-slate-900 dark:text-white">
                  {{ fee.student_name || fee.student }}
                </p>
                <p class="text-xs text-slate-400">{{ fee.student }}</p>
              </td>
              <!-- Fee Type -->
              <td class="px-5 py-4">
                <span class="text-sm text-slate-700 dark:text-slate-300">
                  {{ fee.fee_type }}
                </span>
              </td>
              <!-- Semester / Year -->
              <td class="px-5 py-4">
                <p class="text-sm text-slate-700 dark:text-slate-300">
                  {{ fee.semester || '—' }}
                </p>
                <p class="text-xs text-slate-400">{{ fee.academic_year || '' }}</p>
              </td>
              <!-- Due Date -->
              <td class="px-5 py-4">
                <p
                  :class="[
                    'text-sm',
                    isOverdue(fee)
                      ? 'font-semibold text-red-500 dark:text-red-400'
                      : 'text-slate-600 dark:text-slate-300',
                  ]"
                >
                  {{ fee.due_date || '—' }}
                </p>
              </td>
              <!-- Total -->
              <td class="px-5 py-4 text-sm font-semibold text-slate-900 dark:text-white">
                {{ money(fee.total_amount) }}
              </td>
              <!-- Paid / Outstanding -->
              <td class="px-5 py-4">
                <p class="text-sm text-emerald-600 dark:text-emerald-400">
                  {{ money(fee.paid_amount) }}
                </p>
                <p class="text-xs text-slate-400">due {{ money(fee.outstanding_amount) }}</p>
              </td>
              <!-- Status -->
              <td class="px-5 py-4">
                <Badge :variant="fee.payment_status">{{ fee.payment_status }}</Badge>
              </td>
              <!-- Actions -->
              <td class="px-5 py-4">
                <div class="flex items-center gap-1">
                  <button
                    v-if="fee.payment_status !== 'Paid'"
                    class="icon-btn"
                    title="Record Payment"
                    @click="openPayment(fee)"
                  >
                    <CreditCard class="h-4 w-4" />
                  </button>
                  <button class="icon-btn" title="Edit" @click="openEdit(fee)">
                    <Pencil class="h-4 w-4" />
                  </button>
                  <button class="icon-btn danger" title="Delete" @click="confirmDelete(fee)">
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>

            <!-- Empty state -->
            <tr v-if="!loading && !displayedFees.length">
              <td :colspan="columns.length" class="px-5 py-16 text-center">
                <div class="flex flex-col items-center gap-2 text-slate-400">
                  <Banknote class="h-10 w-10 text-slate-300 dark:text-slate-600" />
                  <span class="text-sm">No fee records found.</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div
        v-if="filteredFees.length > perPage"
        class="flex items-center justify-between border-t border-slate-100 px-5 py-3 dark:border-slate-700"
      >
        <p class="text-xs text-slate-400">
          Showing {{ displayedFees.length }} of {{ filteredFees.length }} records
        </p>
        <div class="flex items-center gap-2">
          <button
            class="btn-secondary px-3 py-1 text-xs"
            :disabled="page === 1"
            @click="page--"
          >
            Prev
          </button>
          <span class="text-xs text-slate-500">{{ page }} / {{ totalPages }}</span>
          <button
            class="btn-secondary px-3 py-1 text-xs"
            :disabled="page >= totalPages"
            @click="page++"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- ── Add / Edit Fee Modal ── -->
    <Modal
      :show="showModal"
      :title="editMode ? 'Edit Fee' : 'Add Fee'"
      size="lg"
      @close="closeModal"
    >
      <form class="space-y-5" @submit.prevent="saveFee">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <!-- Student -->
          <div>
            <label class="label">Student *</label>
            <select
              v-model="form.student"
              class="input-field"
              required
              @change="onStudentChange"
            >
              <option value="">Select Student</option>
              <option
                v-for="s in students"
                :key="s.name"
                :value="s.student_id || s.name"
              >
                {{ s.student_id || s.name }} — {{ s.full_name || s.student_id }}
              </option>
            </select>
          </div>

          <!-- Fee Type -->
          <div>
            <label class="label">Fee Type *</label>
            <select
              v-model="form.fee_type"
              class="input-field"
              required
              @change="onFeeTypeChange"
            >
              <option>Tuition Fee</option>
              <option>Exam Fee</option>
              <option>Library Fee</option>
              <option>Lab Fee</option>
              <option>Hostel Fee</option>
              <option>Other</option>
            </select>
          </div>

          <!-- Semester -->
          <div>
            <label class="label">Semester *</label>
            <select
              v-model="form.semester"
              class="input-field"
              required
              @change="onSemesterChange"
            >
              <option value="">Select Semester</option>
              <option v-for="sem in semesterOptions" :key="sem" :value="sem">
                {{ sem }}
              </option>
            </select>
          </div>

          <!-- Academic Year -->
          <div>
            <label class="label">Academic Year</label>
            <input
              v-model="form.academic_year"
              class="input-field"
              placeholder="e.g. 2025-26"
            />
          </div>

          <!-- Due Date -->
          <div>
            <label class="label">Due Date *</label>
            <input
              v-model="form.due_date"
              type="date"
              class="input-field"
              required
            />
          </div>

          <!-- Total Amount -->
          <div>
            <label class="label">Total Amount *</label>
            <input
              v-model.number="form.total_amount"
              type="number"
              min="0"
              class="input-field"
              required
              @input="clampPaid"
            />
          </div>

          <!-- Paid Amount -->
          <div>
            <label class="label">Paid Amount</label>
            <input
              v-model.number="form.paid_amount"
              type="number"
              min="0"
              :max="form.total_amount"
              class="input-field"
              @input="clampPaid"
            />
          </div>

          <!-- Payment Date -->
          <div>
            <label class="label">Payment Date</label>
            <input
              v-model="form.payment_date"
              type="date"
              class="input-field"
            />
          </div>

          <!-- Payment Method -->
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

          <!-- Transaction ID -->
         <div>
          <label class="label flex items-center justify-between">
            <span>Transaction ID</span>
            <button
              type="button"
              class="text-xs text-primary-500 hover:underline"
              @click="form.transaction_id = generateTxnId()"
            >
              Auto-generate
            </button>
          </label>
          <input v-model="form.transaction_id" class="input-field" placeholder="TXN..." />
        </div>

          <!-- Remarks -->
          <div class="sm:col-span-2">
            <label class="label">Remarks</label>
            <textarea v-model="form.remarks" class="input-field" rows="2" />
          </div>

          <!-- Fee Structure match notice -->
          <div
            v-if="matchedStructure"
            class="sm:col-span-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 dark:border-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300"
          >
            <strong>Fee structure matched:</strong>
            {{ matchedStructure.program }} · {{ matchedStructure.semester }} ·
            {{ matchedStructure.fee_type }} = {{ money(matchedStructure.amount) }}
          </div>

          <!-- Summary tiles -->
          <div class="sm:col-span-2 grid grid-cols-3 gap-3">
            <div class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70">
              <p class="text-xs text-slate-400">Total Amount</p>
              <p class="mt-1 text-lg font-bold text-slate-900 dark:text-white">
                {{ money(form.total_amount) }}
              </p>
            </div>
            <div class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70">
              <p class="text-xs text-slate-400">Paid</p>
              <p class="mt-1 text-lg font-bold text-emerald-600 dark:text-emerald-400">
                {{ money(form.paid_amount) }}
              </p>
            </div>
            <div class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70">
              <p class="text-xs text-slate-400">Outstanding</p>
              <p class="mt-1 text-lg font-bold text-amber-600 dark:text-amber-400">
                {{ money(remainingAmount) }}
              </p>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving…' : 'Save Fee' }}
          </button>
        </div>
      </form>
    </Modal>

    <!-- ── Record Payment Modal ── -->
    <Modal
      :show="showPaymentModal"
      title="Record Payment"
      size="sm"
      @close="showPaymentModal = false"
    >
      <div v-if="paymentFee" class="space-y-4">
        <!-- Fee summary -->
        <div class="rounded-xl bg-slate-50 p-4 dark:bg-slate-800/70 space-y-1">
          <p class="text-sm font-semibold text-slate-900 dark:text-white">
            {{ paymentFee.student_name || paymentFee.student }}
          </p>
          <p class="text-xs text-slate-500">
            {{ paymentFee.fee_type }}
            <span v-if="paymentFee.semester"> · {{ paymentFee.semester }}</span>
          </p>
          <div class="mt-2 flex gap-4 text-sm">
            <span class="text-slate-500">
              Outstanding:
              <strong class="text-amber-600">
                {{ money(paymentFee.outstanding_amount) }}
              </strong>
            </span>
          </div>
        </div>

        <form class="space-y-4" @submit.prevent="submitPayment">
          <div>
            <label class="label">Amount to Pay *</label>
            <input
              v-model.number="paymentForm.amount"
              type="number"
              min="1"
              :max="paymentFee.outstanding_amount"
              class="input-field"
              required
            />
            <p class="mt-1 text-xs text-slate-400">
              Max payable: {{ money(paymentFee.outstanding_amount) }}
            </p>
          </div>
          <div>
            <label class="label">Payment Date *</label>
            <input
              v-model="paymentForm.payment_date"
              type="date"
              class="input-field"
              required
            />
          </div>
          <div>
            <label class="label">Payment Method *</label>
            <select v-model="paymentForm.payment_method" class="input-field" required>
              <option value="">Select Method</option>
              <option>Cash</option>
              <option>Bank Transfer</option>
              <option>Online</option>
              <option>Cheque</option>
            </select>
          </div>
          <div>
            <label class="label">Transaction ID</label>
            <input
              v-model="paymentForm.transaction_id"
              class="input-field"
              placeholder="TXN123456"
            />
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" class="btn-secondary" @click="showPaymentModal = false">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="paymentSaving">
              <CreditCard class="h-4 w-4" />
              {{ paymentSaving ? 'Processing…' : 'Record Payment' }}
            </button>
          </div>
        </form>
      </div>
    </Modal>

    <!-- ── Bulk Assign Modal ── -->
    <Modal
      :show="showBulkModal"
      title="Bulk Assign Fees by Semester"
      size="lg"
      @close="showBulkModal = false"
    >
      <div class="space-y-5">
        <p class="text-sm text-slate-500 dark:text-slate-400">
          Select a semester and fee type to auto-generate fee records for all enrolled
          students in that semester based on active fee structures.
        </p>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="label">Semester *</label>
            <select v-model="bulkForm.semester" class="input-field">
              <option value="">Select Semester</option>
              <option v-for="sem in semesterOptions" :key="sem" :value="sem">
                {{ sem }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Fee Type *</label>
            <select v-model="bulkForm.fee_type" class="input-field">
              <option>Tuition Fee</option>
              <option>Exam Fee</option>
              <option>Library Fee</option>
              <option>Lab Fee</option>
              <option>Hostel Fee</option>
              <option>Other</option>
            </select>
          </div>
          <div>
            <label class="label">Academic Year *</label>
            <input
              v-model="bulkForm.academic_year"
              class="input-field"
              placeholder="2025-26"
            />
          </div>
          <div>
            <label class="label">Due Date *</label>
            <input v-model="bulkForm.due_date" type="date" class="input-field" />
          </div>
          <div class="sm:col-span-2">
            <label class="label">Override Amount
              <span class="text-slate-400 font-normal">(optional — leave empty to use fee structure)</span>
            </label>
            <input
              v-model.number="bulkForm.override_amount"
              type="number"
              min="0"
              class="input-field"
              placeholder="e.g. 15000"
            />
          </div>
        </div>

        <!-- Preview result -->
        <div
          v-if="bulkPreviewCount !== null"
          class="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700 dark:border-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
        >
          This will create fee records for
          <strong>{{ bulkPreviewCount }}</strong> student(s) in
          <strong>{{ bulkForm.semester }}</strong>.
        </div>

        <!-- Error notice -->
        <div
          v-if="bulkError"
          class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-700 dark:bg-red-900/20 dark:text-red-300"
        >
          {{ bulkError }}
        </div>

        <div class="flex justify-end gap-3">
          <button class="btn-secondary" @click="showBulkModal = false">Cancel</button>
          <button
            class="btn-secondary"
            :disabled="!bulkForm.semester"
            @click="previewBulk"
          >
            <Search class="h-4 w-4" />
            Preview
          </button>
          <button
            class="btn-primary"
            :disabled="bulkSaving || !bulkForm.semester || !bulkForm.due_date"
            @click="submitBulkAssign"
          >
            <LayersIcon class="h-4 w-4" />
            {{ bulkSaving ? 'Assigning…' : 'Assign Fees' }}
          </button>
        </div>
      </div>
    </Modal>

    <!-- ── Delete Confirm Modal ── -->
    <Modal :show="showDelete" title="Delete Fee" size="sm" @close="showDelete = false">
      <p class="text-sm text-slate-500 dark:text-slate-400">
        Are you sure you want to delete fee record
        <strong class="text-slate-900 dark:text-white">{{ selected?.name }}</strong>?
        This action cannot be undone.
      </p>
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancel</button>
        <button class="btn-danger" :disabled="deleting" @click="deleteFee">
          <Trash2 class="h-4 w-4" />
          {{ deleting ? 'Deleting…' : 'Delete' }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
// ── Imports ────────────────────────────────────────────────────────────────────
import Badge from '@/components/ui/Badge.vue'
import Modal from '@/components/ui/Modal.vue'
import { useApi } from '@/composables/useApi'
import {
  Banknote,
  CheckCircle,
  Clock,
  CreditCard,
  IndianRupee,
  Layers as LayersIcon,
  Pencil,
  Plus,
  Save,
  Search,
  Trash2,
  X,
} from 'lucide-vue-next'
// ✅ FIX: added onMounted to imports
import { computed, onMounted, ref, watch } from 'vue'

// ── Composable ─────────────────────────────────────────────────────────────────
const { callApi } = useApi()

// ── Remote data ────────────────────────────────────────────────────────────────
const students       = ref([])
const feeStructures  = ref([])
const semesterOptions = ref([])
const fees           = ref([])

// ── UI state ───────────────────────────────────────────────────────────────────
const loading      = ref(false)
const saving       = ref(false)
const deleting     = ref(false)
const paymentSaving = ref(false)
const bulkSaving   = ref(false)
const bulkError    = ref('')

const showModal        = ref(false)
const showDelete       = ref(false)
const showPaymentModal = ref(false)
const showBulkModal    = ref(false)

const editMode   = ref(false)
const selected   = ref(null)
const paymentFee = ref(null)

const statusFilter = ref('')
const page    = ref(1)
const perPage = 15

const filters = ref({
  student: '',
  status: '',
  semester: '',
  academic_year: '',
})

// ── Forms ──────────────────────────────────────────────────────────────────────
const defaultForm = () => ({
  student: '',
  student_name: '',
  program: '',
  semester: '',
  academic_year: '',
  fee_type: 'Tuition Fee',
  due_date: '',
  total_amount: 0,
  paid_amount: 0,
  payment_date: '',
  payment_method: '',
  transaction_id: '',
  remarks: '',
})

const form = ref(defaultForm())

const paymentForm = ref({
  amount: 0,
  payment_date: new Date().toISOString().slice(0, 10),
  payment_method: '',
  transaction_id: '',
})

const bulkForm = ref({
  semester: '',
  fee_type: 'Tuition Fee',
  academic_year: '',
  due_date: '',
  override_amount: null,
})
const bulkPreviewCount = ref(null)

// ── Constants ──────────────────────────────────────────────────────────────────
const columns = [
  'Student',
  'Fee Type',
  'Semester / Year',
  'Due Date',
  'Amount',
  'Paid / Due',
  'Status',
  'Actions',
]

// ── Helpers ────────────────────────────────────────────────────────────────────
const money = (v) => `₹${Number(v || 0).toLocaleString('en-IN')}`
const todayStr = () => new Date().toISOString().slice(0, 10)

const isOverdue = (fee) =>
  ['Unpaid', 'Partially Paid', 'Overdue'].includes(fee.payment_status) &&
  !!fee.due_date &&
  fee.due_date < todayStr()

// ── Computed ───────────────────────────────────────────────────────────────────

/** Academic years derived from loaded fee records */
const academicYearOptions = computed(() => {
  const years = new Set(fees.value.map((f) => f.academic_year).filter(Boolean))
  return [...years].sort().reverse()
})

/** All client-side filtering happens here */
const filteredFees = computed(() => {
  let list = fees.value

  // Card click filter
  if (statusFilter.value) {
    list = list.filter((f) => f.payment_status === statusFilter.value)
  }
  // Dropdown status filter
  if (filters.value.status) {
    list = list.filter((f) => f.payment_status === filters.value.status)
  }
  // Semester filter
  if (filters.value.semester) {
    list = list.filter((f) => f.semester === filters.value.semester)
  }
  // Academic year filter
  if (filters.value.academic_year) {
    list = list.filter((f) => f.academic_year === filters.value.academic_year)
  }
  // Student name / ID search (client-side for instant response)
  if (filters.value.student) {
    const q = filters.value.student.toLowerCase()
    list = list.filter(
      (f) =>
        f.student?.toLowerCase().includes(q) ||
        f.student_name?.toLowerCase().includes(q),
    )
  }

  return list
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredFees.value.length / perPage)),
)

const displayedFees = computed(() => {
  const start = (page.value - 1) * perPage
  return filteredFees.value.slice(start, start + perPage)
})

/** Summary cards */
const summary = computed(() => {
  const all = fees.value
  const total       = all.reduce((s, f) => s + Number(f.total_amount || 0), 0)
  const paid        = all.reduce((s, f) => s + Number(f.paid_amount || 0), 0)
  const outstanding = all.reduce((s, f) => s + Number(f.outstanding_amount || 0), 0)
  const overdueCount = all.filter((f) => f.payment_status === 'Overdue').length

  return [
    {
      label: 'Total Billed',
      value: money(total),
      sub: `${all.length} records`,
      filterKey: '',
      icon: IndianRupee,
      bg: 'bg-primary-50 dark:bg-primary-500/10',
      color: 'text-primary-600 dark:text-primary-300',
      ring: 'ring-primary-500',
    },
    {
      label: 'Collected',
      value: money(paid),
      sub: null,
      filterKey: 'Paid',
      icon: CheckCircle,
      bg: 'bg-emerald-50 dark:bg-emerald-500/10',
      color: 'text-emerald-600 dark:text-emerald-300',
      ring: 'ring-emerald-500',
    },
    {
      label: 'Outstanding',
      value: money(outstanding),
      sub: null,
      filterKey: 'Unpaid',
      icon: Clock,
      bg: 'bg-amber-50 dark:bg-amber-500/10',
      color: 'text-amber-600 dark:text-amber-300',
      ring: 'ring-amber-500',
    },
    {
      label: 'Overdue',
      value: overdueCount,
      sub: 'records',
      filterKey: 'Overdue',
      icon: Banknote,
      bg: 'bg-red-50 dark:bg-red-500/10',
      color: 'text-red-600 dark:text-red-300',
      ring: 'ring-red-500',
    },
  ]
})

/** Auto-matched fee structure based on current form values */
const matchedStructure = computed(() =>
  feeStructures.value.find(
    (s) =>
      s.program   === form.value.program &&
      s.semester  === form.value.semester &&
      s.fee_type  === form.value.fee_type &&
      Number(s.is_active) === 1,
  ) ?? null,
)

/** Remaining / outstanding in the form */
const remainingAmount = computed(
  () => Number(form.value.total_amount || 0) - Number(form.value.paid_amount || 0),
)

// ── Watch ──────────────────────────────────────────────────────────────────────
// Reset to page 1 whenever the filtered list changes
watch(
  () => form.value.paid_amount,
  (val) => {
    if (Number(val) > 0) {
      if (!form.value.transaction_id) form.value.transaction_id = generateTxnId()
      if (!form.value.payment_date)   form.value.payment_date   = todayStr()
    }
  },
)

// ── Data fetching ──────────────────────────────────────────────────────────────
const fetchFees = async () => {
  loading.value = true
  try {
    // Only pass server-filterable params; student search stays client-side
    const params = {}
    if (filters.value.status)        params.status        = filters.value.status
    if (filters.value.semester)      params.semester      = filters.value.semester
    if (filters.value.academic_year) params.academic_year = filters.value.academic_year

    fees.value = await callApi('sms.api.fee.get_fees', params)
  } finally {
    loading.value = false
  }
}
// Debounced version for the student search input
let debounceTimer = null
const onStudentSearch = () => {
  clearTimeout(debounceTimer)
  // Client-side filter — no need to re-fetch, just let computed handle it.
  // But reset page immediately.
  debounceTimer = setTimeout(() => { page.value = 1 }, 150)
}

// ── Fee structure helpers ──────────────────────────────────────────────────────
const resolveStudent = () =>
  students.value.find((s) => (s.student_id || s.name) === form.value.student)

/** Called when the student dropdown changes */
const onStudentChange = () => {
  const s = resolveStudent()
  if (!s) return
  form.value.student_name  = s.full_name || s.student_id || s.name
  form.value.program       = s.program        || form.value.program
  form.value.academic_year = s.academic_year  || form.value.academic_year
  applyFeeStructure()
}

const onFeeTypeChange  = () => applyFeeStructure()
const onSemesterChange = () => applyFeeStructure()

/** Fill amount / due_date / academic_year from matched fee structure */
const applyFeeStructure = () => {
  const match = matchedStructure.value
  if (!match) return
  form.value.total_amount  = Number(match.amount || 0)
  if (match.due_date)      form.value.due_date      = match.due_date
  if (match.academic_year) form.value.academic_year = match.academic_year
  clampPaid()
}

/** Ensure paid_amount never exceeds total_amount */
const clampPaid = () => {
  const total = Number(form.value.total_amount || 0)
  if (Number(form.value.paid_amount || 0) > total) {
    form.value.paid_amount = total
  }
}

const generateTxnId = () => {
  const ts  = Date.now().toString(36).toUpperCase()
  const rnd = Math.random().toString(36).slice(2, 6).toUpperCase()
  return `TXN${ts}${rnd}`
}

// ── Filter helpers ─────────────────────────────────────────────────────────────
const setStatusFilter = (key) => {
  if (key === null) return
  statusFilter.value = statusFilter.value === key ? '' : key
}

const clearFilters = () => {
  filters.value  = { student: '', status: '', semester: '', academic_year: '' }
  statusFilter.value = ''
  fetchFees()
}

// ── Modal openers ──────────────────────────────────────────────────────────────
const openCreate = () => {
  form.value     = defaultForm()
  editMode.value = false
  showModal.value = true
}

const openEdit = (fee) => {
  selected.value  = fee
  form.value      = { ...defaultForm(), ...fee }
  editMode.value  = true
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selected.value  = null
}

const confirmDelete = (fee) => {
  selected.value   = fee
  showDelete.value = true
}

const openPayment = (fee) => {
  paymentFee.value  = fee
  paymentForm.value = {
    amount:         fee.outstanding_amount || 0,
    payment_date:   todayStr(),
    payment_method: '',
    transaction_id: generateTxnId(),
  }
  showPaymentModal.value = true
}
const openBulkAssign = () => {
  bulkForm.value = {
    semester: '',
    fee_type: 'Tuition Fee',
    academic_year: '',
    due_date: '',
    override_amount: null,
  }
  bulkPreviewCount.value = null
  bulkError.value        = ''
  showBulkModal.value    = true
}

// ── CRUD actions ───────────────────────────────────────────────────────────────
const saveFee = async () => {
  saving.value = true
  try {
    if (editMode.value) {
      await callApi(
        'sms.api.fee.update_fee',
        { fee_name: selected.value.name, data: form.value },
        { method: 'POST' },
      )
    } else {
      await callApi('sms.api.fee.create_fee', { data: form.value }, { method: 'POST' })
    }
    closeModal()
    await fetchFees()
  } finally {
    saving.value = false
  }
}

const deleteFee = async () => {
  deleting.value = true
  try {
    await callApi(
      'sms.api.fee.delete_fee',
      { fee_name: selected.value.name },
      { method: 'POST' },
    )
    showDelete.value = false
    await fetchFees()
  } finally {
    deleting.value = false
  }
}

const submitPayment = async () => {
  paymentSaving.value = true
  try {
    await callApi(
      'sms.api.fee.record_payment',
      {
        fee_name:       paymentFee.value.name,
        amount:         paymentForm.value.amount,
        payment_date:   paymentForm.value.payment_date,
        payment_method: paymentForm.value.payment_method,
        transaction_id: paymentForm.value.transaction_id,
      },
      { method: 'POST' },
    )
    showPaymentModal.value = false
    await fetchFees()
  } finally {
    paymentSaving.value = false
  }
}

// ── Bulk assign ────────────────────────────────────────────────────────────────
const previewBulk = () => {
  bulkError.value = ''
  if (!bulkForm.value.semester) {
    bulkError.value = 'Please select a semester first.'
    return
  }
  // Count students whose program matches an active fee structure for this semester
  const count = students.value.filter((s) =>
    feeStructures.value.some(
      (fs) =>
        fs.semester  === bulkForm.value.semester &&
        fs.fee_type  === bulkForm.value.fee_type &&
        fs.program   === s.program &&
        Number(fs.is_active) === 1,
    ),
  ).length
  bulkPreviewCount.value = count
}

const submitBulkAssign = async () => {
  bulkError.value = ''
  if (!bulkForm.value.semester || !bulkForm.value.due_date) {
    bulkError.value = 'Semester and Due Date are required.'
    return
  }
  bulkSaving.value = true
  try {
    const res = await callApi(
      'sms.api.fee.bulk_assign_fees',
      { data: bulkForm.value },
      { method: 'POST' },
    )
    showBulkModal.value = false
    // Show result message briefly via bulkError re-purposed as info — or just refresh
    await fetchFees()
    // Optional: surface result
    if (res?.message) console.info(res.message)
  } catch (err) {
    bulkError.value = err?.message || 'Bulk assign failed. Please try again.'
  } finally {
    bulkSaving.value = false
  }
}

// ── Lifecycle ──────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    // Load reference data in parallel
    const [studentsData, structuresData, semestersData] = await Promise.all([
      callApi('sms.api.meta.get_student_options'),
      callApi('sms.api.meta.get_fee_structures'),
      callApi('sms.api.meta.get_semester_options'),
    ])
    students.value       = studentsData       ?? []
    feeStructures.value  = structuresData     ?? []
    semesterOptions.value = semestersData     ?? []
  } catch (e) {
    console.error('Failed to load reference data:', e)
  }
  // Load fees after reference data is ready
  await fetchFees()
})
</script>
