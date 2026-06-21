<template>
  <div class="space-y-3">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <p class="text-sm font-semibold text-slate-700 dark:text-slate-300">
        Select Your Class *
      </p>
      <p class="text-xs text-slate-400">
        {{ slots.length }} class{{ slots.length !== 1 ? 'es' : '' }}/week
      </p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="rounded-lg bg-slate-50 dark:bg-slate-900/50 p-8 text-center">
      <Loader2 class="h-6 w-6 animate-spin text-slate-400 mx-auto" />
      <p class="mt-2 text-xs text-slate-400">Loading your timetable…</p>
    </div>

    <!-- Empty -->
    <div
      v-else-if="!slots.length"
      class="rounded-lg bg-amber-50 dark:bg-amber-500/10 border border-amber-200
             dark:border-amber-700/50 p-4 text-sm text-amber-700 dark:text-amber-300
             flex items-center gap-2"
    >
      <AlertCircle class="h-5 w-5 shrink-0" />
      You have no classes scheduled in any active timetable.
    </div>

    <!-- Grid -->
    <div v-else class="overflow-x-auto -mx-1 px-1">
      <table class="w-full border-separate border-spacing-1 min-w-[640px]">
        <thead>
          <tr>
            <th class="w-14 sticky left-0 bg-white dark:bg-slate-800 z-10"></th>
            <th
              v-for="day in days"
              :key="day"
              class="px-2 py-1.5 text-xs font-bold uppercase tracking-wider
                     text-slate-500 dark:text-slate-400 text-center"
            >
              {{ day.slice(0, 3) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="hour in hours" :key="hour.label">
            <!-- Hour label cell -->
            <td
              class="w-14 px-1 py-1 text-xs font-bold text-slate-600
                     dark:text-slate-400 text-right sticky left-0
                     bg-white dark:bg-slate-800 z-10"
            >
              <div class="leading-tight">
                <p>{{ hour.short }}</p>
                <p class="text-[10px] font-normal text-slate-400">
                  {{ hour.time }}
                </p>
              </div>
            </td>

            <!-- Slot cells -->
            <td
              v-for="day in days"
              :key="`${day}-${hour.label}`"
              class="p-0 align-top"
            >
              <button
                v-if="cellSlot(day, hour.label)"
                :class="cellClasses(day, hour.label)"
                @click="selectCell(day, hour.label)"
              >
                <p class="text-[11px] font-bold leading-tight truncate">
                  {{ cellSlot(day, hour.label).subject_name
                       || cellSlot(day, hour.label).subject }}
                </p>
                <p class="text-[9px] opacity-80 leading-tight truncate">
                  {{ shortBatch(cellSlot(day, hour.label).batch) }}
                </p>
                <span
                  v-if="cellSlot(day, hour.label).is_lab"
                  class="inline-block mt-0.5 text-[8px] font-bold
                         bg-white/30 px-1 rounded"
                >LAB</span>
              </button>

              <!-- Empty cell -->
              <div
                v-else
                class="h-14 rounded-md bg-slate-50 dark:bg-slate-900/40
                       border border-dashed border-slate-200 dark:border-slate-700"
              >
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Selected display -->
    <div
      v-if="selected"
      class="rounded-lg bg-gradient-to-r from-primary-50 to-cyan-50
             dark:from-primary-500/10 dark:to-cyan-500/10
             border border-primary-200 dark:border-primary-700/50 p-3
             flex items-center gap-3"
    >
      <div class="flex h-10 w-10 items-center justify-center rounded-lg
                  bg-gradient-to-br from-primary-500 to-cyan-500
                  text-white shadow">
        <CheckCircle class="h-5 w-5" />
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-xs text-slate-500">Selected</p>
        <p class="text-sm font-semibold text-slate-900 dark:text-white truncate">
          {{ selected.day }} · {{ selected.hour }} ·
          {{ selected.subject_name || selected.subject }}
        </p>
        <p class="text-xs text-slate-500 truncate">
          {{ selected.batch }}
          <span v-if="selected.is_lab" class="ml-1 text-purple-600 font-semibold">
            🧪 LAB
          </span>
        </p>
      </div>
      <button
        class="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
        @click="clearSelection"
      >
        Clear
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

const props = defineProps({
  userEmail: { type: String, required: true },
})
const emit = defineEmits(['select'])

const { callApi } = useApi()

const slots    = ref([])     // flat list of all slots faculty teaches
const loading  = ref(false)
const selected = ref(null)

const days  = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
const hours = [
  { label: 'Hour 1',     short: 'H1', time: '10–11' },
  { label: 'Hour 2',     short: 'H2', time: '11–12' },
  { label: 'Hour 3',     short: 'H3', time: '12–1'  },
  { label: 'Hour 4',     short: 'H4', time: '2–3'   },
  { label: 'Hour 5',     short: 'H5', time: '3–4'   },
  { label: 'Hour 6',     short: 'H6', time: '4–5'   },
  { label: 'Sat Hour 1', short: 'S1', time: '9–9:45' },
  { label: 'Sat Hour 2', short: 'S2', time: '9:45–10:30' },
  { label: 'Sat Hour 3', short: 'S3', time: '10:30–11:15' },
  { label: 'Sat Hour 4', short: 'S4', time: '11:20–12:10' },
  { label: 'Sat Hour 5', short: 'S5', time: '12:10–1:00' },
]

// ─── Helpers ──────────────────────────────────────────────────────────────
const cellSlot = (day, hourLabel) =>
  slots.value.find(s => s.day === day && s.hour === hourLabel)

const shortBatch = (batch) => {
  if (!batch) return ''
  // "Computer Science-2025-2029" → "CS-25-29"
  return batch
    .replace('Computer Science', 'CS')
    .replace('Mechanical Engineering', 'ME')
    .replace(/(\d{4})-(\d{4})/, '$1-$2')
    .replace(/-(\d{2})(\d{2})-(\d{2})(\d{2})/, '-$2-$4')
}

const cellClasses = (day, hourLabel) => {
  const slot = cellSlot(day, hourLabel)
  const isSelected = selected.value && selected.value.slot_id === slot.slot_id
  const base = 'h-14 w-full px-1.5 py-1 rounded-md text-left transition-all'
  if (isSelected) {
    return `${base} bg-gradient-to-br from-primary-500 to-cyan-500 text-white
            shadow-lg shadow-primary-500/40 ring-2 ring-primary-300`
  }
  return `${base} bg-white dark:bg-slate-700/50
          ring-1 ring-slate-200 dark:ring-slate-600
          text-slate-700 dark:text-slate-200
          hover:bg-primary-50 dark:hover:bg-primary-500/10
          hover:ring-primary-300 hover:shadow-md cursor-pointer`
}

const selectCell = (day, hourLabel) => {
  const slot = cellSlot(day, hourLabel)
  if (!slot) return
  selected.value = slot
  emit('select', slot)
}

const clearSelection = () => {
  selected.value = null
  emit('select', null)
}

// ─── Load timetable ───────────────────────────────────────────────────────
// We iterate days and grab the user's classes from each.
const loadTimetable = async () => {
  if (!props.userEmail) return
  loading.value = true
  slots.value = []
  selected.value = null

  try {
    const dedupe = {}
    for (const day of days) {
      const refDate = nextWeekdayISO(day)
      const res = await callApi('sms.api.timetable.get_my_classes_today', {
        date: refDate,
        user: props.userEmail,
      })
      for (const cls of (res?.classes || [])) {
        // Attach `day` and dedupe by slot_id
        if (!dedupe[cls.slot_id]) {
          dedupe[cls.slot_id] = { ...cls, day }
        }
      }
    }
    slots.value = Object.values(dedupe)
  } catch (e) {
    console.error('[MyTimetableGrid] load failed:', e)
  } finally {
    loading.value = false
  }
}

const nextWeekdayISO = (dayName) => {
  const order = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
  const target = order.indexOf(dayName)
  const d = new Date()
  const diff = (target - d.getDay() + 7) % 7 || 7
  d.setDate(d.getDate() + diff)
  return d.toISOString().slice(0, 10)
}

// Re-load when user changes
watch(() => props.userEmail, loadTimetable)
onMounted(loadTimetable)

// Expose method for parent to reset
defineExpose({ clearSelection })
</script>
