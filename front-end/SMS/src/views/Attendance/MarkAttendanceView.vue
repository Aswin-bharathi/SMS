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
      class="rounded-xl bg-white dark:bg-slate-800 p-12 shadow-sm
             ring-1 ring-slate-200 dark:ring-slate-700 animate-pulse"
    >
      <div class="h-6 w-1/3 bg-slate-200 dark:bg-slate-700 rounded" />
      <div class="mt-4 space-y-2">
        <div
          v-for="i in 5" :key="i"
          class="h-12 bg-slate-100 dark:bg-slate-700/50 rounded"
        />
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
          <!-- Left: hour badge + details -->
          <div class="flex items-start gap-4">
            <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl
                        bg-gradient-to-br from-primary-500 to-cyan-500 text-white shadow-lg">
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
                {{ data.slot.hour_details?.start_time || '' }} –
                {{ data.slot.hour_details?.end_time   || '' }}
              </p>

              <h1 class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                {{ data.slot.subject_name || data.slot.subject || 'Unknown Subject' }}
              </h1>

              <div class="mt-2 flex flex-wrap items-center gap-3 text-sm
                          text-slate-600 dark:text-slate-300">
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
                  class="inline-flex items-center gap-1 rounded-full
                         bg-purple-100 dark:bg-purple-500/20 px-2 py-0.5
                         text-xs font-semibold text-purple-700 dark:text-purple-300"
                >
                  🧪 LAB
                </span>
              </div>

              <!-- Substitute banner -->
              <div
                v-if="data.substitution"
                class="mt-3 inline-flex items-center gap-2 rounded-lg
                       bg-blue-100 dark:bg-blue-500/20 px-3 py-1.5
                       text-xs font-semibold text-blue-700 dark:text-blue-300"
              >
                <RefreshCcw class="h-3.5 w-3.5" />
                Substituting for
                <strong>{{ data.substitution.original_faculty }}</strong>
                <span v-if="data.substitution.reason">
                  · {{ data.substitution.reason }}
                </span>
              </div>
            </div>
          </div>

          <!-- Right: status badges -->
          <div class="flex flex-col items-end gap-2">
            <!-- Date badge -->
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

            <!-- Mode badge — driven by server mode field -->
            <div
              v-if="data.mode === 'first_time'"
              class="inline-flex items-center gap-1 rounded-lg
                     bg-emerald-50 dark:bg-emerald-500/10 px-3 py-1.5
                     text-xs font-semibold text-emerald-700 dark:text-emerald-300"
            >
              <Unlock class="h-3.5 w-3.5" />
              Ready to mark
            </div>
            <div
              v-else-if="data.mode === 'update'"
              class="inline-flex items-center gap-1 rounded-lg
                     bg-blue-50 dark:bg-blue-500/10 px-3 py-1.5
                     text-xs font-semibold text-blue-700 dark:text-blue-300"
            >
              <Pencil class="h-3.5 w-3.5" />
              Update Attendance
            </div>
            <div
              v-else
              class="inline-flex items-center gap-1 rounded-lg
                     bg-red-50 dark:bg-red-500/10 px-3 py-1.5
                     text-xs font-semibold text-red-700 dark:text-red-300"
            >
              <Lock class="h-3.5 w-3.5" />
              {{ permissionMessage }}
            </div>
          </div>
        </div>
      </div>

      <!-- ─── Status banners (one shown at a time) ────────────── -->
      <!-- Future date -->
      <div
        v-if="data.is_future"
        class="rounded-xl bg-blue-50 dark:bg-blue-500/10 border border-blue-200
               dark:border-blue-700 p-4 text-sm text-blue-800 dark:text-blue-200
               flex items-center gap-2"
      >
        <Calendar class="h-5 w-5 shrink-0" />
        This class is scheduled for the future. Attendance can only be marked after the class begins.
      </div>

      <!-- Today but hour not started -->
      <div
        v-else-if="!data.hour_has_started && data.is_today"
        class="rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200
               dark:border-amber-700 p-4 text-sm text-amber-800 dark:text-amber-200
               flex items-center gap-2"
      >
        <Clock class="h-5 w-5 shrink-0" />
        This hour hasn't started yet ({{ data.slot.hour_details?.start_time }}).
        Attendance can be marked once the class begins.
      </div>

      <!-- Archived batch -->
      <div
        v-else-if="data.is_archived"
        class="rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200
               dark:border-amber-700 p-4 text-sm text-amber-800 dark:text-amber-200
               flex items-center gap-2"
      >
        <AlertTriangle class="h-5 w-5 shrink-0" />
        This batch has been archived. No new attendance can be marked.
      </div>

      <!-- Edit window expired -->
      <div
        v-else-if="data.reason === 'edit_window_expired'"
        class="rounded-xl bg-slate-50 dark:bg-slate-700/30 border border-slate-200
               dark:border-slate-700 p-4 text-sm text-slate-700 dark:text-slate-300
               flex items-center gap-2"
      >
        <Lock class="h-5 w-5 shrink-0" />
        Edit window has closed (24 hours after class ended). Contact admin to make changes.
      </div>

      <!-- Update mode — already marked, still editable -->
      <div
        v-else-if="data.mode === 'update'"
        class="rounded-xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200
               dark:border-emerald-700 p-4 text-sm text-emerald-800 dark:text-emerald-200
               flex items-center gap-2"
      >
        <CheckCircle class="h-5 w-5 shrink-0" />
        Attendance recorded for this class ({{ data.already_marked_count }} students).
        You can update entries below.
      </div>

      <!-- ─── Quick actions + live counters ──────────────────── -->
      <div
        v-if="data.can_mark"
        class="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm
               ring-1 ring-slate-200 dark:ring-slate-700"
      >
        <div class="flex flex-wrap items-center justify-between gap-4">
          <!-- Bulk actions -->
          <div class="flex flex-wrap gap-2">
            <button
              class="inline-flex items-center gap-1.5 rounded-lg
                     bg-emerald-50 dark:bg-emerald-500/10 px-3 py-2
                     text-sm font-semibold text-emerald-700 dark:text-emerald-300
                     hover:bg-emerald-100"
              @click="markAll('Present')"
            >
              <CheckCheck class="h-4 w-4" /> All Present
            </button>
            <button
              class="inline-flex items-center gap-1.5 rounded-lg
                     bg-red-50 dark:bg-red-500/10 px-3 py-2
                     text-sm font-semibold text-red-700 dark:text-red-300
                     hover:bg-red-100"
              @click="markAll('Absent')"
            >
              <X class="h-4 w-4" /> All Absent
            </button>
            <button
              class="inline-flex items-center gap-1.5 rounded-lg
                     bg-slate-100 dark:bg-slate-700 px-3 py-2
                     text-sm font-semibold text-slate-700 dark:text-slate-300
                     hover:bg-slate-200 dark:hover:bg-slate-600"
              @click="resetToOriginal"
            >
              <RotateCcw class="h-4 w-4" /> Reset
            </button>
          </div>

          <!-- Live counters -->
          <div class="flex items-center gap-4 text-sm">
            <div
              v-for="st in STATUSES" :key="st.value"
              class="flex items-center gap-1.5"
            >
              <div :class="['h-2.5 w-2.5 rounded-full', st.dotClass]" />
              <span class="font-semibold">{{ counts[st.value] }}</span>
              <span class="text-slate-500">{{ st.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── Student table ───────────────────────────────────── -->
      <div class="rounded-xl bg-white dark:bg-slate-800 shadow-sm
                  ring-1 ring-slate-200 dark:ring-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-100 dark:border-slate-700
                         bg-slate-50 dark:bg-slate-700/40">
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase
                           tracking-wider text-slate-500 w-16">Roll</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase
                           tracking-wider text-slate-500">Student</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase
                           tracking-wider text-slate-500 w-48">Status</th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase
                           tracking-wider text-slate-500">Remarks</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
              <tr
                v-for="s in students"
                :key="s.name"
                :class="[
                  'transition-colors',
                  s.status === 'Absent'   ? 'bg-red-50/30 dark:bg-red-500/5'    : '',
                  s.status === 'Late'     ? 'bg-amber-50/30 dark:bg-amber-500/5' : '',
                  s.status === 'On Leave' ? 'bg-blue-50/30 dark:bg-blue-500/5'   : '',
                  s.status === 'Present'  ? 'hover:bg-slate-50 dark:hover:bg-slate-700/30' : '',
                ]"
              >
                <!-- Roll number -->
                <td class="px-4 py-3 text-sm font-mono font-bold
                           text-slate-700 dark:text-slate-200">
                  {{ s.roll_number || '—' }}
                </td>

                <!-- Name + saved badge -->
                <td class="px-4 py-3">
                  <p class="text-sm font-semibold text-slate-900 dark:text-white">
                    {{ s.full_name }}
                  </p>
                  <p class="text-xs text-slate-400 flex items-center gap-1">
                    {{ s.student_id || s.name }}
                    <span
                      v-if="s.already_marked"
                      class="inline-flex items-center gap-0.5 rounded-full
                             bg-emerald-100 dark:bg-emerald-500/20 px-1.5 py-0.5
                             text-[10px] font-semibold text-emerald-700 dark:text-emerald-300"
                    >
                      <CheckCircle class="h-2.5 w-2.5" />
                      saved
                      <span v-if="s.edit_count > 0">· edited {{ s.edit_count }}×</span>
                    </span>
                  </p>
                </td>

                <!-- Status toggle -->
                <td class="px-4 py-3">
                  <div class="inline-flex rounded-lg border border-slate-200
                              dark:border-slate-700 overflow-hidden">
                    <button
                      v-for="opt in STATUSES"
                      :key="opt.value"
                      :disabled="!data.can_mark"
                      :class="[
                        'px-2.5 py-1 text-xs font-semibold transition-colors',
                        s.status === opt.value
                          ? opt.activeClass
                          : 'bg-white dark:bg-slate-800 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-700/50',
                        !data.can_mark ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
                      ]"
                      :title="opt.label"
                      @click="data.can_mark && (s.status = opt.value)"
                    >
                      {{ opt.short }}
                    </button>
                  </div>
                </td>

                <!-- Remarks -->
                <td class="px-4 py-3">
                  <input
                    v-model="s.remarks"
                    :disabled="!data.can_mark"
                    type="text"
                    placeholder="Optional"
                    class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                           bg-white dark:bg-slate-900 px-3 py-1.5 text-sm
                           focus:outline-none focus:ring-2 focus:ring-primary-500
                           disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </td>
              </tr>

              <tr v-if="!students.length">
                <td colspan="4" class="px-4 py-12 text-center text-sm text-slate-400">
                  No active students in this batch.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ─── Sticky save bar ──────────────────────────────────── -->
      <div
        v-if="data.can_mark && students.length"
        class="sticky bottom-4 z-10 flex flex-wrap items-center justify-between gap-3
               rounded-xl bg-white dark:bg-slate-800 p-4 shadow-2xl
               ring-1 ring-slate-200 dark:ring-slate-700"
      >
        <p class="text-sm text-slate-600 dark:text-slate-300">
          <strong>{{ students.length }}</strong> students ·
          {{ counts.Present }} present, {{ counts.Absent }} absent

          <!-- Mode indicator pill -->
          <span
            v-if="data.mode === 'first_time'"
            class="ml-2 text-blue-500"
          >
            ● first-time marking
          </span>
          <span
            v-else-if="hasChanges"
            class="ml-2 text-amber-500"
          >
            ● unsaved changes
          </span>
          <span v-else class="ml-2 text-slate-400">
            ● no changes
          </span>
        </p>

        <div class="flex items-center gap-2">
          <!-- Discard button (update mode only) -->
          <button
            v-if="hasChanges && data.mode === 'update'"
            class="rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2
                   text-sm font-medium text-slate-700 dark:text-slate-300
                   hover:bg-slate-50 dark:hover:bg-slate-700"
            @click="loadData"
          >
            Discard
          </button>

          <!-- Save / Update button -->
          <button
            class="inline-flex items-center gap-2 rounded-lg
                   bg-gradient-to-r from-primary-500 to-cyan-500 px-5 py-2
                   text-sm font-semibold text-white shadow-lg shadow-primary-500/30
                   hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="saving || !canSave"
            @click="save"
          >
            <Save class="h-4 w-4" />
            <span v-if="saving">Saving…</span>
            <span v-else-if="data.mode === 'first_time'">Save Attendance</span>
            <span v-else>Update Attendance</span>
          </button>
        </div>
      </div>

      <!-- ─── Toast notification ───────────────────────────────── -->
      <transition name="toast">
        <div
          v-if="toast.show"
          :class="[
            'fixed bottom-24 right-6 z-50 flex items-center gap-3',
            'rounded-xl px-4 py-3 shadow-2xl ring-1',
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

    <!-- ─── Error state ──────────────────────────────────────────── -->
    <div
      v-else-if="error"
      class="rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200
             dark:border-red-700 p-6 text-center"
    >
      <AlertCircle class="h-10 w-10 text-red-500 mx-auto mb-3" />
      <h3 class="text-base font-semibold text-red-900 dark:text-red-300">
        Could not load attendance
      </h3>
      <p class="mt-1 text-sm text-red-700 dark:text-red-400">{{ error }}</p>
      <router-link
        to="/attendance"
        class="mt-4 inline-flex items-center gap-2 rounded-lg
               bg-primary-500 px-4 py-2 text-sm font-semibold text-white
               hover:bg-primary-600"
      >
        ← Back to My Classes
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute }                 from 'vue-router'
import {
  AlertCircle, AlertTriangle, ArrowLeft, Building2, Calendar,
  CheckCheck, CheckCircle, Clock, Lock, MapPin, Pencil,
  RefreshCcw, RotateCcw, Save, Unlock, UserCheck, X,
} from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

// ─── Route params ─────────────────────────────────────────────────────────
const route       = useRoute()
const { callApi } = useApi()

const slotId = route.params.slot   // e.g. "8saerag5ob"
const date   = route.params.date   // e.g. "2026-06-18"

// ─── Reactive state ───────────────────────────────────────────────────────
const data     = ref(null)    // full server response
const students = ref([])      // editable copy of student list
const original = ref([])      // snapshot for change detection + reset
const loading  = ref(true)
const saving   = ref(false)
const error    = ref('')
const toast    = ref({ show: false, type: 'success', message: '' })

// ─── Constants ────────────────────────────────────────────────────────────
const STATUSES = [
  {
    value: 'Present',  label: 'Present',  short: 'P',  dotClass: 'bg-emerald-500',
    activeClass: 'bg-emerald-500 text-white',
  },
  {
    value: 'Absent',   label: 'Absent',   short: 'A',  dotClass: 'bg-red-500',
    activeClass: 'bg-red-500 text-white',
  },
  {
    value: 'Late',     label: 'Late',     short: 'L',  dotClass: 'bg-amber-500',
    activeClass: 'bg-amber-500 text-white',
  },
  {
    value: 'On Leave', label: 'On Leave', short: 'OL', dotClass: 'bg-blue-500',
    activeClass: 'bg-blue-500 text-white',
  },
]

// ─── Computed ─────────────────────────────────────────────────────────────
const formattedDate = computed(() => {
  if (!date) return ''
  // Use T00:00:00 to avoid timezone-shift (date-only string)
  const d = new Date(date + 'T00:00:00')
  return d.toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })
})

/** Live status counts across the editable student list */
const counts = computed(() => {
  const c = { Present: 0, Absent: 0, Late: 0, 'On Leave': 0 }
  students.value.forEach(s => {
    if (c[s.status] !== undefined) c[s.status]++
  })
  return c
})

const effectiveFacultyName = computed(() => {
  if (data.value?.substitution) {
    const sub = data.value.substitution
    return (sub.substitute_name || sub.substitute_faculty) + ' (substitute)'
  }
  return data.value?.slot?.faculty_name || 'Unknown'
})

const permissionMessage = computed(() => {
  const map = {
    batch_archived:         'Batch archived',
    not_authorized:         'Not your class',
    substituted_to_another: 'Substituted away',
    hour_not_started:       'Class not started',
    edit_window_expired:    'Edit window expired',
    slot_not_found:         'Slot not found',
  }
  return map[data.value?.reason] || 'Read only'
})

/**
 * Detect unsaved changes vs the last-loaded snapshot.
 * For first-time mode: any state is considered "ready to save" (no prior data).
 */
const hasChanges = computed(() => {
  if (!data.value) return false
  if (data.value.mode === 'first_time') return true   // always ready in first-time mode
  if (students.value.length !== original.value.length) return true
  return students.value.some((s, i) => {
    const o = original.value[i]
    return !o
      || s.status  !== o.status
      || (s.remarks || '') !== (o.remarks || '')
  })
})

/** Save button is enabled when: can_mark + (first-time OR has real changes) */
const canSave = computed(() => {
  if (!data.value?.can_mark) return false
  if (data.value.mode === 'first_time') return true
  return hasChanges.value
})

// ─── Methods ──────────────────────────────────────────────────────────────
const showToast = (type, message) => {
  toast.value = { show: true, type, message }
  setTimeout(() => { toast.value.show = false }, 3500)
}

const markAll = (status) => {
  if (!data.value?.can_mark) return
  students.value.forEach(s => { s.status = status })
}

const resetToOriginal = () => {
  students.value = original.value.map(s => ({ ...s }))
}

/**
 * Fetch fresh data from the server and rebuild local state.
 * Called on mount AND after every successful save.
 */
const loadData = async () => {
  loading.value = true
  error.value   = ''

  try {
    const res = await callApi(
      'sms.api.attendance_v2.get_marking_screen',
      { timetable_slot: slotId, date },
    )

    // Replace data ref entirely — prevents stale mode/flags
    data.value = res

    // Deep-copy students so edits don't mutate server data
    const list = (res?.students || []).map(s => ({ ...s }))
    students.value = list
    original.value = list.map(s => ({ ...s }))   // snapshot for reset + change detection

  } catch (e) {
    console.error('[MarkAttendance] loadData error:', e)
    error.value = e?.message || 'Failed to load attendance screen'
  } finally {
    loading.value = false
  }
}

const save = async () => {
  if (!canSave.value || saving.value) return
  saving.value = true

  try {
    const records = students.value.map(s => ({
      student: s.name,
      status:  s.status,
      remarks: s.remarks || '',
    }))

    const res = await callApi(
      'sms.api.attendance_v2.save_attendance',
      { timetable_slot: slotId, date, records },
      { method: 'POST' },
    )

    const created = res?.created || 0
    const updated = res?.updated || 0
    const msg = created
      ? `Saved! ${created} marked${updated ? `, ${updated} updated` : ''}.`
      : `Updated ${updated} record(s).`

    showToast('success', msg)

    if (res?.errors?.length) {
      console.warn('[MarkAttendance] partial errors:', res.errors)
    }

    // ✅ Reload from server — this will flip mode from "first_time" → "update"
    //    and refresh all already_marked / edit_count flags
    await loadData()

  } catch (e) {
    console.error('[MarkAttendance] save error:', e)
    showToast('error', e?.message || 'Failed to save attendance')
  } finally {
    saving.value = false
  }
}

// ─── Lifecycle ────────────────────────────────────────────────────────────
onMounted(loadData)
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active  { transition: all 0.3s ease; }
.toast-enter-from,
.toast-leave-to      { opacity: 0; transform: translateY(20px); }
</style>
