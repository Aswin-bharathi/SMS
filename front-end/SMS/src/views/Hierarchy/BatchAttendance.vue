<template>
  <div class="space-y-4">
    <!-- Controls bar -->
    <div class="flex flex-wrap items-end gap-3">
      <div>
        <label class="block text-xs text-slate-500 mb-1">Date</label>
        <input
          v-model="date"
          type="date"
          class="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>
      <div>
        <label class="block text-xs text-slate-500 mb-1">Hour</label>
        <select
          v-model="hour"
          class="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option v-for="i in 8" :key="i" :value="`Hour ${i}`">Hour {{ i }}</option>
        </select>
      </div>
      <button
        class="inline-flex items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-700 px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-600"
        :disabled="loading"
        @click="loadRoster"
      >
        <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
        {{ loading ? 'Loading…' : 'Load Roster' }}
      </button>
      <div class="ml-auto flex items-center gap-3">
        <span v-if="!canMark" class="inline-flex items-center gap-1 text-xs text-amber-500">
          <Lock class="h-3 w-3" />
          Read-only — only the class in-charge can mark
        </span>
        <button
          v-if="canMark && roster.length"
          class="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-primary-500 to-cyan-500 px-4 py-2 text-sm font-semibold text-white shadow-lg hover:shadow-xl disabled:opacity-50"
          :disabled="saving"
          @click="saveAll"
        >
          <Save class="h-4 w-4" />
          {{ saving ? 'Saving…' : 'Save Attendance' }}
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div v-if="roster.length" class="grid grid-cols-4 gap-3">
      <div class="rounded-lg bg-emerald-50 dark:bg-emerald-500/10 p-3">
        <p class="text-xs text-emerald-600 dark:text-emerald-400">Present</p>
        <p class="text-xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">
          {{ counts.Present }}
        </p>
      </div>
      <div class="rounded-lg bg-red-50 dark:bg-red-500/10 p-3">
        <p class="text-xs text-red-600 dark:text-red-400">Absent</p>
        <p class="text-xl font-bold text-red-700 dark:text-red-300 mt-1">
          {{ counts.Absent }}
        </p>
      </div>
      <div class="rounded-lg bg-amber-50 dark:bg-amber-500/10 p-3">
        <p class="text-xs text-amber-600 dark:text-amber-400">Late</p>
        <p class="text-xl font-bold text-amber-700 dark:text-amber-300 mt-1">
          {{ counts.Late }}
        </p>
      </div>
      <div class="rounded-lg bg-blue-50 dark:bg-blue-500/10 p-3">
        <p class="text-xs text-blue-600 dark:text-blue-400">On Leave</p>
        <p class="text-xl font-bold text-blue-700 dark:text-blue-300 mt-1">
          {{ counts['On Leave'] }}
        </p>
      </div>
    </div>

    <!-- Quick actions -->
    <div v-if="canMark && roster.length" class="flex flex-wrap gap-2">
      <button
        class="inline-flex items-center gap-1 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100"
        @click="markAll('Present')"
      >
        <CheckCheck class="h-3 w-3" /> All Present
      </button>
      <button
        class="inline-flex items-center gap-1 rounded-lg bg-red-50 dark:bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-700 dark:text-red-300 hover:bg-red-100"
        @click="markAll('Absent')"
      >
        <X class="h-3 w-3" /> All Absent
      </button>
    </div>

    <!-- Roster table -->
    <div v-if="roster.length" class="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <table class="w-full">
        <thead class="bg-slate-50 dark:bg-slate-700/50">
          <tr>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Roll</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Student</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Status</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Remarks</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
          <tr
            v-for="s in roster"
            :key="s.name"
            :class="[
              'transition-colors',
              s.status === 'Present'  ? 'bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/30' : '',
              s.status === 'Absent'   ? 'bg-red-50/40 dark:bg-red-500/5' : '',
              s.status === 'Late'     ? 'bg-amber-50/40 dark:bg-amber-500/5' : '',
              s.status === 'On Leave' ? 'bg-blue-50/40 dark:bg-blue-500/5' : '',
            ]"
          >
            <td class="px-3 py-3 text-sm font-mono font-semibold">{{ s.roll_number }}</td>
            <td class="px-3 py-3">
              <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ s.full_name }}</p>
              <p class="text-xs text-slate-400">{{ s.student_id }}</p>
            </td>
            <td class="px-3 py-3">
              <select
                v-model="s.status"
                :disabled="!canMark"
                :class="[
                  'rounded-lg border px-3 py-1.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-500',
                  s.status === 'Present'  ? 'border-emerald-300 bg-emerald-50 text-emerald-700 dark:border-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300' : '',
                  s.status === 'Absent'   ? 'border-red-300 bg-red-50 text-red-700 dark:border-red-700 dark:bg-red-500/20 dark:text-red-300' : '',
                  s.status === 'Late'     ? 'border-amber-300 bg-amber-50 text-amber-700 dark:border-amber-700 dark:bg-amber-500/20 dark:text-amber-300' : '',
                  s.status === 'On Leave' ? 'border-blue-300 bg-blue-50 text-blue-700 dark:border-blue-700 dark:bg-blue-500/20 dark:text-blue-300' : '',
                  !canMark ? 'opacity-60 cursor-not-allowed' : '',
                ]"
              >
                <option>Present</option>
                <option>Absent</option>
                <option>Late</option>
                <option>On Leave</option>
              </select>
            </td>
            <td class="px-3 py-3">
              <input
                v-model="s.remarks"
                :disabled="!canMark"
                placeholder="Optional"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-1.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-60"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="!loading" class="rounded-xl border border-dashed border-slate-300 dark:border-slate-700 p-12 text-center">
      <Calendar class="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
      <p class="text-sm text-slate-400">Pick a date and hour, then click "Load Roster".</p>
    </div>

    <!-- Toast -->
    <transition name="toast">
      <div
        v-if="toast"
        class="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-xl bg-white dark:bg-slate-800 px-4 py-3 shadow-2xl ring-1 ring-slate-200 dark:ring-slate-700"
      >
        <CheckCircle class="h-5 w-5 text-emerald-500" />
        <span class="text-sm font-medium text-slate-900 dark:text-white">{{ toast }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import {
  Calendar, CheckCheck, CheckCircle, Lock, RefreshCw, Save, X,
} from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

const props = defineProps({ batch: String })
const emit  = defineEmits(['saved'])
const { callApi } = useApi()

const date    = ref(new Date().toISOString().slice(0, 10))
const hour    = ref('Hour 1')
const roster  = ref([])
const loading = ref(false)
const saving  = ref(false)
const canMark = ref(false)
const toast   = ref('')

const counts = computed(() => {
  const c = { Present: 0, Absent: 0, Late: 0, 'On Leave': 0 }
  roster.value.forEach(s => { c[s.status] = (c[s.status] || 0) + 1 })
  return c
})

const showToast = (msg) => {
  toast.value = msg
  setTimeout(() => (toast.value = ''), 3000)
}

const checkPermission = async () => {
  try {
    const r = await callApi('sms.api.attendance.can_mark_batch', { batch: props.batch })
    canMark.value = !!r?.allowed
  } catch { canMark.value = false }
}

const loadRoster = async () => {
  loading.value = true
  try {
    roster.value = (await callApi('sms.api.attendance.get_batch_roster', {
      batch: props.batch, date: date.value, hour: hour.value,
    })) ?? []
  } catch (e) {
    console.error(e)
  } finally { loading.value = false }
}

const markAll = (status) => {
  roster.value.forEach(s => (s.status = status))
}

const saveAll = async () => {
  saving.value = true
  try {
    const res = await callApi(
      'sms.api.attendance.mark_attendance_bulk',
      {
        batch: props.batch, date: date.value, hour: hour.value,
        records: roster.value.map(s => ({
          student: s.name, status: s.status, remarks: s.remarks,
        })),
      },
      { method: 'POST' },
    )
    showToast(`✓ ${res?.total || 0} attendance records saved`)
    emit('saved')
    await loadRoster()
  } catch (e) {
    alert(e?.message || 'Failed to save')
  } finally { saving.value = false }
}

watch([date, hour], () => {
  if (roster.value.length) loadRoster()
})

onMounted(async () => {
  await checkPermission()
  await loadRoster()
})
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(20px); }
</style>
