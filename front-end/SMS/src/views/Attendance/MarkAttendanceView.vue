<template>
  <div class="space-y-5">
    <!-- Back link -->
    <router-link
      to="/attendance"
      class="inline-flex items-center gap-1.5 text-sm font-medium text-primary-500 hover:underline"
    >
      <ArrowLeft class="h-4 w-4" />
      Back to My Classes
    </router-link>

    <!-- Loading -->
    <div
      v-if="loading"
      class="rounded-xl bg-white dark:bg-slate-800 p-12 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 animate-pulse"
    >
      <div class="h-6 w-1/3 bg-slate-200 dark:bg-slate-700 rounded" />
      <div class="mt-4 space-y-2">
        <div v-for="i in 5" :key="i" class="h-12 bg-slate-100 dark:bg-slate-700/50 rounded" />
      </div>
    </div>

    <template v-else-if="data">
      <!-- ─── Header card ─────────────────────────────────────── -->
      <div
        :class="[
          'rounded-xl p-6 shadow-sm ring-1 transition-colors',
          data.substitution
            ? 'bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-500/10 dark:to-cyan-500/10 ring-blue-200 dark:ring-blue-700/50'
            : 'bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-800/50 ring-slate-200 dark:ring-slate-700',
        ]"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="flex items-start gap-4">
            <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-cyan-500 text-white shadow-lg">
              <div class="text-center">
                <p class="text-[10px] font-medium opacity-90 leading-none">HOUR</p>
                <p class="text-2xl font-bold leading-none mt-1">
                  {{ data.slot.hour_details?.hour_number || '?' }}
                </p>
              </div>
            </div>

            <div>
              <p class="text-xs text-slate-500">
                {{ formattedDate }} ·
                {{ formatTime(data.slot.hour_details?.start_time) }} –
                {{ formatTime(data.slot.hour_details?.end_time) }}
              </p>

              <h1 class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                {{ data.slot.subject_name || data.slot.subject || 'Unknown Subject' }}
              </h1>

              <div class="mt-2 flex flex-wrap items-center gap-3 text-sm text-slate-600 dark:text-slate-300">
                <span class="flex items-center gap-1">
                  <UserCheck class="h-3.5 w-3.5" />
                  <strong>{{ effectiveFacultyName }}</strong>
                </span>
                <span class="flex items-center gap-1">
                  <Building2 class="h-3.5 w-3.5" />
                  {{ data.batch.batch_year }} · {{ data.batch.department }}
                </span>
                <span v-if="data.slot.room" class="flex items-center gap-1">
                  <MapPin class="h-3.5 w-3.5" />
                  Room {{ data.slot.room }}
                </span>
                <span
                  v-if="data.slot.is_lab"
                  class="inline-flex items-center gap-1 rounded-full bg-purple-100 dark:bg-purple-500/20 px-2 py-0.5 text-xs font-semibold text-purple-700 dark:text-purple-300"
                >
                  🧪 LAB
                </span>
              </div>

              <!-- Substitute banner -->
              <div
                v-if="data.substitution"
                class="mt-3 inline-flex items-center gap-2 rounded-lg bg-blue-100 dark:bg-blue-500/20 px-3 py-1.5 text-xs font-semibold text-blue-700 dark:text-blue-300"
              >
                <RefreshCcw class="h-3.5 w-3.5" />
                Substituting for
                <strong>{{ getName(data.substitution.original_faculty) }}</strong>
                <span v-if="data.substitution.reason">· {{ data.substitution.reason }}</span>
              </div>
            </div>
          </div>

          <!-- Right: Status badges -->
          <div class="flex flex-col items-end gap-2">
            <!-- Date relativity -->
            <div
              :class="[
                'inline-flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-semibold',
                data.is_today
                  ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'
                  : data.is_past
                  ? 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'
                  : 'bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-300',
              ]"
            >
              <Calendar class="h-3.5 w-3.5" />
              <span v-if="data.is_today">Today</span>
              <span v-else-if="data.days_ago === 1">Yesterday</span>
              <span v-else-if="data.is_past">{{ data.days_ago }} days ago</span>
              <span v-else>Future date</span>
            </div>

            <!-- Permission state -->
            <div
              v-if="data.can_mark"
              class="inline-flex items-center gap-1 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-700 dark:text-emerald-300"
            >
              <Unlock class="h-3.5 w-3.5" />
              {{ data.is_first_time_marking ? 'Ready to mark' : 'Editable' }}
            </div>
            <div
              v-else
              class="inline-flex items-center gap-1 rounded-lg bg-red-50 dark:bg-red-500/10 px-3 py-1.5 text-xs font-semibold text-red-700 dark:text-red-300"
            >
              <Lock class="h-3.5 w-3.5" />
              {{ permissionMessage }}
            </div>
          </div>
        </div>
      </div>

      <!-- ─── Status banners ──────────────────────────────────── -->
      <div
        v-if="data.is_future"
        class="rounded-xl bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-700 p-4 text-sm text-blue-800 dark:text-blue-200 flex items-center gap-2"
      >
        <Calendar class="h-5 w-5 shrink-0" />
        This class is scheduled for the future. You can only mark attendance after the class begins.
      </div>

      <div
        v-else-if="!data.hour_has_started && data.is_today"
        class="rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-700 p-4 text-sm text-amber-800 dark:text-amber-200 flex items-center gap-2"
      >
        <Clock class="h-5 w-5 shrink-0" />
        This hour hasn't started yet ({{ formatTime(data.slot.hour_details?.start_time) }}).
        Attendance can be marked once the class begins.
      </div>

      <div
        v-else-if="data.is_archived"
        class="rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-700 p-4 text-sm text-amber-800 dark:text-amber-200 flex items-center gap-2"
      >
        <AlertTriangle class="h-5 w-5 shrink-0" />
        This batch has been archived. No new attendance can be marked.
      </div>

      <div
        v-else-if="data.is_past && data.days_ago > 1 && !data.can_mark"
        class="rounded-xl bg-slate-50 dark:bg-slate-700/30 border border-slate-200 dark:border-slate-700 p-4 text-sm text-slate-700 dark:text-slate-300 flex items-center gap-2"
      >
        <Lock class="h-5 w-5 shrink-0" />
        This record is older than 24 hours. Read-only — contact admin to make changes.
      </div>

      <div
        v-else-if="!data.is_first_time_marking"
        class="rounded-xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-700 p-4 text-sm text-emerald-800 dark:text-emerald-200 flex items-center gap-2"
      >
        <CheckCircle class="h-5 w-5 shrink-0" />
        Attendance already recorded for this class. You can edit existing entries below.
      </div>

      <!-- ─── Quick actions + counters ────────────────────────── -->
      <div
        v-if="data.can_mark"
        class="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700"
      >
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex flex-wrap gap-2">
            <button
              class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 px-3 py-2 text-sm font-semibold text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100"
              @click="markAll('Present')"
            >
              <CheckCheck class="h-4 w-4" /> All Present
            </button>
            <button
              class="inline-flex items-center gap-1.5 rounded-lg bg-red-50 dark:bg-red-500/10 px-3 py-2 text-sm font-semibold text-red-700 dark:text-red-300 hover:bg-red-100"
              @click="markAll('Absent')"
            >
              <X class="h-4 w-4" /> All Absent
            </button>
            <button
              class="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 dark:bg-slate-700 px-3 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
              @click="resetToOriginal"
            >
              <RotateCcw class="h-4 w-4" /> Reset
            </button>
          </div>

          <div class="flex items-center gap-4 text-sm">
            <div class="flex items-center gap-1.5">
              <div class="h-2.5 w-2.5 rounded-full bg-emerald-500" />
              <span class="font-semibold">{{ counts.Present }}</span>
              <span class="text-slate-500">Present</span>
            </div>
            <div class="flex items-center gap-1.5">
              <div class="h-2.5 w-2.5 rounded-full bg-red-500" />
              <span class="font-semibold">{{ counts.Absent }}</span>
              <span class="text-slate-500">Absent</span>
            </div>
            <div class="flex items-center gap-1.5">
              <div class="h-2.5 w-2.5 rounded-full bg-amber-500" />
              <span class="font-semibold">{{ counts.Late }}</span>
              <span class="text-slate-500">Late</span>
            </div>
            <div class="flex items-center gap-1.5">
              <div class="h-2.5 w-2.5 rounded-full bg-blue-500" />
              <span class="font-semibold">{{ counts['On Leave'] }}</span>
              <span class="text-slate-500">On Leave</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── Student table ───────────────────────────────────── -->
      <div class="rounded-xl bg-white dark:bg-slate-800 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-700/40">
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 w-16">Roll</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Student</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 w-48">Status</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Remarks</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
              <tr
                v-for="s in students"
                :key="s.name"
                :class="[
                  'transition-colors',
                  s.status === 'Absent'   ? 'bg-red-50/30 dark:bg-red-500/5' : '',
                  s.status === 'Late'     ? 'bg-amber-50/30 dark:bg-amber-500/5' : '',
                  s.status === 'On Leave' ? 'bg-blue-50/30 dark:bg-blue-500/5' : '',
                  s.status === 'Present'  ? 'hover:bg-slate-50 dark:hover:bg-slate-700/30' : '',
                ]"
              >
                <td class="px-4 py-3 text-sm font-mono font-bold text-slate-700 dark:text-slate-200">
                  {{ s.roll_number || '—' }}
                </td>
                <td class="px-4 py-3">
                  <p class="text-sm font-semibold text-slate-900 dark:text-white">
                    {{ s.full_name }}
                  </p>
                  <p class="text-xs text-slate-400 flex items-center gap-1">
                    {{ s.student_id || s.name }}
                    <span
                      v-if="s.already_marked"
                      class="inline-flex items-center gap-0.5 rounded-full bg-emerald-100 dark:bg-emerald-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700 dark:text-emerald-300"
                    >
                      <CheckCircle class="h-2.5 w-2.5" /> saved
                      <span v-if="s.edit_count > 0">· edited {{ s.edit_count }}x</span>
                    </span>
                  </p>
                </td>
                <td class="px-4 py-3">
                  <div class="inline-flex rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
                    <button
                      v-for="opt in STATUSES"
                      :key="opt.value"
                      :disabled="!data.can_mark"
                      :class="[
                        'px-2.5 py-1 text-xs font-semibold transition-colors',
                        s.status === opt.value
                          ? opt.activeClass
                          : 'bg-white dark:bg-slate-800 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-700/50',
                        !data.can_mark ? 'opacity-50 cursor-not-allowed' : '',
                      ]"
                      :title="opt.label"
                      @click="s.status = opt.value"
                    >
                      {{ opt.short }}
                    </button>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <input
                    v-model="s.remarks"
                    :disabled="!data.can_mark"
                    type="text"
                    placeholder="Optional"
                    class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
                  />
                </td>
              </tr>
              <tr v-if="!students.length">
                <td colspan="4" class="px-4 py-12 text-center text-sm text-slate-400">
                  No students in this batch.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ─── Save bar (sticky bottom) ────────────────────────── -->
      <div
        v-if="data.can_mark && students.length"
        class="sticky bottom-4 z-10 flex flex-wrap items-center justify-between gap-3 rounded-xl bg-white dark:bg-slate-800 p-4 shadow-2xl ring-1 ring-slate-200 dark:ring-slate-700"
      >
        <p class="text-sm text-slate-600 dark:text-slate-300">
          <strong>{{ students.length }}</strong> students ·
          {{ counts.Present }} present, {{ counts.Absent }} absent
          <span v-if="data.is_first_time_marking" class="text-blue-500 ml-2">
            ● first-time marking
          </span>
          <span v-else-if="hasChanges" class="text-amber-500 ml-2">
            ● unsaved changes
          </span>
        </p>
        <div class="flex items-center gap-2">
          <button
            v-if="hasChanges && !data.is_first_time_marking"
            class="rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
            @click="loadData"
          >
            Discard
          </button>
          <button
            class="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-primary-500 to-cyan-500 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-primary-500/30 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="saving || !canSave"
            @click="save"
          >
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving…' : (data.is_first_time_marking ? 'Save Attendance' : 'Update Attendance') }}
          </button>
        </div>
      </div>

      <!-- Toast -->
      <transition name="toast">
        <div
          v-if="toast.show"
          :class="[
            'fixed bottom-24 right-6 z-50 flex items-center gap-3 rounded-xl px-4 py-3 shadow-2xl ring-1',
            toast.type === 'success'
              ? 'bg-emerald-50 ring-emerald-200 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300 dark:ring-emerald-700'
              : 'bg-red-50 ring-red-200 text-red-800 dark:bg-red-500/20 dark:text-red-300 dark:ring-red-700',
          ]"
        >
          <CheckCircle v-if="toast.type === 'success'" class="h-5 w-5" />
          <AlertCircle v-else class="h-5 w-5" />
          <span class="text-sm font-medium">{{ toast.message }}</span>
        </div>
      </transition>
    </template>

    <!-- Error state -->
    <div
      v-else-if="error"
      class="rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-700 p-6 text-center"
    >
      <AlertCircle class="h-10 w-10 text-red-500 mx-auto mb-3" />
      <h3 class="text-base font-semibold text-red-900 dark:text-red-300">
        Could not load attendance
      </h3>
      <p class="mt-1 text-sm text-red-700 dark:text-red-400">{{ error }}</p>
      <router-link
        to="/attendance"
        class="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600"
      >
        ← Back to My Classes
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  AlertCircle, AlertTriangle, ArrowLeft, Building2, Calendar,
  CheckCheck, CheckCircle, Clock, Lock, MapPin, RefreshCcw,
  RotateCcw, Save, Unlock, UserCheck, X,
} from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

const route       = useRoute()
const router      = useRouter()
const { callApi } = useApi()

const slotId = route.params.slot
const date   = route.params.date

const data     = ref(null)
const students = ref([])
const original = ref([])
const loading  = ref(true)
const saving   = ref(false)
const error    = ref('')
const toast    = ref({ show: false, type: 'success', message: '' })

const STATUSES = [
  { value: 'Present',  label: 'Present',  short: 'P',
    activeClass: 'bg-emerald-500 text-white' },
  { value: 'Absent',   label: 'Absent',   short: 'A',
    activeClass: 'bg-red-500 text-white' },
  { value: 'Late',     label: 'Late',     short: 'L',
    activeClass: 'bg-amber-500 text-white' },
  { value: 'On Leave', label: 'On Leave', short: 'OL',
    activeClass: 'bg-blue-500 text-white' },
]

// ─── Computed ────────────────────────────────────────────────────────────
const formattedDate = computed(() => {
  if (!date) return ''
  const d = new Date(date + 'T00:00:00')
  return d.toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })
})

const counts = computed(() => {
  const c = { Present: 0, Absent: 0, Late: 0, 'On Leave': 0 }
  students.value.forEach(s => { c[s.status] = (c[s.status] || 0) + 1 })
  return c
})

const effectiveFacultyName = computed(() => {
  if (data.value?.substitution) {
    return getName(data.value.substitution.substitute_faculty) + ' (substitute)'
  }
  return data.value?.slot?.faculty_name || 'Unknown'
})

const permissionMessage = computed(() => {
  const reason = data.value?.reason
  const map = {
    'batch_archived':         'Batch archived',
    'not_authorized':         'Not your class',
    'substituted_to_another': 'Substituted away',
    'hour_not_started':       'Class not started',
    'edit_window_expired':    'Edit window expired',
  }
  return map[reason] || 'Locked'
})

const hasChanges = computed(() => {
  if (students.value.length !== original.value.length) return true
  return students.value.some((s, i) => {
    const o = original.value[i]
    return !o || s.status !== o.status || (s.remarks || '') !== (o.remarks || '')
  })
})

// 🔑 KEY FIX: Allow save when first-time OR has changes
const canSave = computed(() => {
  if (!data.value?.can_mark) return false
  // First time: always allow save (even if all defaults are Present)
  if (data.value.is_first_time_marking) return true
  // Subsequent: only if there are changes
  return hasChanges.value
})

// ─── Methods ─────────────────────────────────────────────────────────────
const formatTime = (t) => (t || '').slice(0, 5)

const getName = (email) => {
  if (!email) return 'someone'
  return email.split('@')[0].toUpperCase().replace('.', '. ')
}

const showToast = (type, message) => {
  toast.value = { show: true, type, message }
  setTimeout(() => (toast.value.show = false), 3500)
}

const markAll = (status) => {
  if (!data.value?.can_mark) return
  students.value.forEach(s => (s.status = status))
}

const resetToOriginal = () => {
  // Reset to what the server returned
  students.value = original.value.map(s => ({ ...s }))
}

const loadData = async () => {
  loading.value = true
  error.value   = ''
  try {
    const res = await callApi('sms.api.attendance_v2.get_marking_screen', {
      timetable_slot: slotId,
      date: date,
    })
    data.value = res
    students.value = (res?.students || []).map(s => ({ ...s }))
    original.value = students.value.map(s => ({ ...s }))
  } catch (e) {
    console.error(e)
    error.value = e?.message || 'Failed to load attendance screen'
  } finally {
    loading.value = false
  }
}

const save = async () => {
  saving.value = true
  try {
    const records = students.value.map(s => ({
      student: s.name,
      status:  s.status,
      remarks: s.remarks || '',
    }))
    const res = await callApi(
      'sms.api.attendance_v2.save_attendance',
      {
        timetable_slot: slotId,
        date: date,
        records,
      },
      { method: 'POST' },
    )

    const created = res?.created || 0
    const updated = res?.updated || 0
    const msg = created
      ? `Saved! ${created} marked, ${updated} updated.`
      : `Updated ${updated} record(s).`
    showToast('success', msg)

    if (res?.errors?.length) {
      console.warn('Some records had errors:', res.errors)
    }

    await loadData()
  } catch (e) {
    console.error(e)
    showToast('error', e?.message || 'Failed to save attendance')
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.toast-enter-active, .toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
