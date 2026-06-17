<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h3 class="text-lg font-bold text-slate-900 dark:text-white">Fee Management</h3>
        <p class="text-xs text-slate-400">
          {{ structures.length }} active structure(s) · {{ fees.length }} student fee record(s)
        </p>
      </div>
      <button
        class="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-primary-500 to-cyan-500 px-4 py-2 text-sm font-semibold text-white shadow-lg hover:shadow-xl"
        @click="showAddStructure = true"
      >
        <Plus class="h-4 w-4" />
        Assign Fee Structure
      </button>
    </div>

    <!-- Active structures -->
    <div
      v-if="structures.length"
      class="rounded-xl bg-white dark:bg-slate-800 p-4 ring-1 ring-slate-200 dark:ring-slate-700"
    >
      <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
        Active Fee Structures
      </h4>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div
          v-for="s in structures"
          :key="s.name"
          class="rounded-lg border border-slate-200 dark:border-slate-700 p-3 flex items-center justify-between bg-slate-50 dark:bg-slate-700/30"
        >
          <div>
            <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ s.fee_type }}</p>
            <p class="text-xs text-slate-400">
              {{ s.semester || 'All semesters' }} · Due {{ s.due_date || '—' }}
            </p>
          </div>
          <p class="text-lg font-bold text-primary-600 dark:text-primary-400">
            ₹{{ formatMoney(s.amount) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Fee records table -->
    <div class="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden bg-white dark:bg-slate-800">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 dark:bg-slate-700/50">
            <tr>
              <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Student</th>
              <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Fee Type</th>
              <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Semester</th>
              <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Total</th>
              <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Paid</th>
              <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Pending</th>
              <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
            <tr
              v-for="f in fees"
              :key="f.name"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
            >
              <td class="px-3 py-3 text-sm font-semibold text-slate-900 dark:text-white">
                {{ f.student_name || f.student }}
              </td>
              <td class="px-3 py-3 text-sm text-slate-600 dark:text-slate-300">
                <p>{{ f.fee_type }}</p>
                <p v-if="f.installment_label" class="text-xs text-blue-500 dark:text-blue-400 font-medium mt-0.5">
                  {{ f.installment_label }}
                </p>
              </td>
              <td class="px-3 py-3 text-sm text-slate-600 dark:text-slate-300">{{ f.semester || '—' }}</td>
              <td class="px-3 py-3 text-sm font-semibold text-slate-900 dark:text-white">
                ₹{{ formatMoney(f.total_amount) }}
              </td>
              <td class="px-3 py-3 text-sm font-semibold text-emerald-600">
                ₹{{ formatMoney(f.paid_amount) }}
              </td>
              <td class="px-3 py-3 text-sm font-semibold text-amber-600">
                ₹{{ formatMoney(f.outstanding_amount) }}
              </td>
              <td class="px-3 py-3">
                <span :class="statusClass(f.payment_status)">{{ f.payment_status }}</span>
              </td>
            </tr>
            <tr v-if="!fees.length">
              <td colspan="7" class="px-3 py-16 text-center">
                <IndianRupee class="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-2" />
                <p class="text-sm text-slate-400">
                  No fee records yet. Click "Assign Fee Structure" to create one for all students.
                </p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Structure Modal -->
    <div
      v-if="showAddStructure"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      @click.self="showAddStructure = false"
    >
      <div class="w-full max-w-md rounded-2xl bg-white dark:bg-slate-800 p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-slate-900 dark:text-white">Assign Fee Structure</h2>
          <button
            class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            @click="showAddStructure = false"
          >
            <X class="h-5 w-5" />
          </button>
        </div>

        <p class="text-xs text-slate-500 bg-blue-50 dark:bg-blue-500/10 rounded-lg p-3 mb-4">
          This will auto-create fee records for all active students in this batch.
        </p>

        <form class="space-y-4" @submit.prevent="createStructure">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Fee Type *
            </label>
            <select
              v-model="form.fee_type"
              required
              class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option>Tuition Fee</option>
              <option>Exam Fee</option>
              <option>Library Fee</option>
              <option>Lab Fee</option>
              <option>Hostel Fee</option>
              <option>Other</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Amount (₹) *
              </label>
              <input
                v-model.number="form.amount"
                type="number"
                min="0"
                required
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Due Date *
              </label>
              <input
                v-model="form.due_date"
                type="date"
                required
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Semester
              </label>
              <select
                v-model="form.semester"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All</option>
                <option v-for="i in 8" :key="i" :value="`Sem ${i}`">Sem {{ i }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Academic Year
              </label>
              <input
                v-model="form.academic_year"
                placeholder="2025-26"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              class="rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
              @click="showAddStructure = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600 disabled:opacity-50"
            >
              <Save class="h-4 w-4" />
              {{ saving ? 'Assigning…' : 'Assign to Batch' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { IndianRupee, Plus, Save, X } from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

const props = defineProps({ batch: String })
const emit = defineEmits(['changed'])
const { callApi } = useApi()

const structures = ref([])
const fees = ref([])
const saving = ref(false)
const showAddStructure = ref(false)

const form = ref({
  fee_type: 'Tuition Fee',
  amount: 0,
  due_date: '',
  semester: '',
  academic_year: '',
})

const formatMoney = (v) => Number(v || 0).toLocaleString('en-IN')

const statusClass = (status) => {
  const base = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium'
  const map = {
    Paid: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300',
    Unpaid: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
    'Partially Paid': 'bg-amber-50 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300',
    Overdue: 'bg-red-50 text-red-700 dark:bg-red-500/20 dark:text-red-300',
  }
  return `${base} ${map[status] || map.Unpaid}`
}

const loadAll = async () => {
  try {
    structures.value =
      (await callApi('sms.api.fee_structure.get_structures_for_batch', {
        batch: props.batch,
      })) ?? []
    fees.value =
      (await callApi('sms.api.fee_structure.get_fees_by_batch', {
        batch: props.batch,
      })) ?? []
  } catch (e) {
    console.error(e)
  }
}

const createStructure = async () => {
  saving.value = true
  try {
    const dept = await callApi('frappe.client.get_value', {
      doctype: 'Batch',
      filters: { name: props.batch },
      fieldname: 'department',
    })

    await callApi(
      'frappe.client.insert',
      {
        doc: {
          doctype: 'Program Fee Structure',
          department: dept?.department || '',
          batch: props.batch,
          fee_type: form.value.fee_type,
          amount: form.value.amount,
          due_date: form.value.due_date,
          semester: form.value.semester || null,
          academic_year: form.value.academic_year || null,
          is_active: 1,
        },
      },
      { method: 'POST' },
    )

    showAddStructure.value = false
    form.value = {
      fee_type: 'Tuition Fee',
      amount: 0,
      due_date: '',
      semester: '',
      academic_year: '',
    }
    await loadAll()
    emit('changed')
  } catch (e) {
    alert(e?.message || 'Failed to create structure')
  } finally {
    saving.value = false
  }
}

onMounted(loadAll)
</script>
