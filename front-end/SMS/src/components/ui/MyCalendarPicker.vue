<template>
  <div class="space-y-4">
    <!-- ─── Calendar header ─────────────────────────────────────── -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-1">
        <button
          class="h-9 w-9 inline-flex items-center justify-center rounded-lg
                 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200
                 dark:hover:bg-slate-600 text-slate-600 dark:text-slate-300"
          @click="changeMonth(-1)"
        >
          <ChevronLeft class="h-4 w-4" />
        </button>
        <button
          class="h-9 w-9 inline-flex items-center justify-center rounded-lg
                 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200
                 dark:hover:bg-slate-600 text-slate-600 dark:text-slate-300"
          @click="changeMonth(1)"
        >
          <ChevronRight class="h-4 w-4" />
        </button>
        <button
          class="ml-2 h-9 px-3 inline-flex items-center rounded-lg
                 bg-primary-50 dark:bg-primary-500/20 text-primary-600
                 dark:text-primary-300 text-xs font-semibold
                 hover:bg-primary-100 dark:hover:bg-primary-500/30"
          @click="goToToday"
        >
          Today
        </button>
      </div>

      <h3 class="text-base font-bold text-slate-800 dark:text-white">
        {{ monthLabel }}
      </h3>

      <div class="w-[140px]"></div>
    </div>

    <!-- ─── Loading ─────────────────────────────────────────────── -->
    <div
      v-if="loading"
      class="rounded-lg bg-slate-50 dark:bg-slate-900/50 p-12 text-center"
    >
      <Loader2 class="h-6 w-6 animate-spin text-slate-400 dark:text-slate-500 mx-auto" />
      <p class="mt-2 text-xs text-slate-400 dark:text-slate-500">
        Loading your schedule…
      </p>
    </div>

    <!-- ─── Calendar grid ───────────────────────────────────────── -->
    <div
      v-else
      class="rounded-xl bg-white dark:bg-slate-800
             ring-1 ring-slate-200 dark:ring-slate-700 overflow-hidden"
    >
      <!-- Day headers -->
      <div class="grid grid-cols-7 bg-slate-50 dark:bg-slate-700/40
                  border-b border-slate-200 dark:border-slate-700">
        <div
          v-for="d in ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']"
          :key="d"
          class="px-2 py-2 text-center text-[11px] font-bold uppercase
                 tracking-wider text-slate-500 dark:text-slate-400"
        >
          {{ d }}
        </div>
      </div>

      <!-- Days -->
      <div class="grid grid-cols-7">
        <button
          v-for="cell in calendarCells"
          :key="cell.key"
          :disabled="cell.disabled"
          :class="cellClasses(cell)"
          @click="cell.disabled ? null : selectDate(cell.iso)"
        >
          <span :class="dayNumberClasses(cell)">
            {{ cell.day }}
          </span>

          <!-- Class count dots -->
          <div v-if="cell.classCount > 0" class="flex items-center gap-0.5 mt-1">
            <span
              v-for="n in Math.min(cell.classCount, 3)"
              :key="n"
              :class="[
                'h-1.5 w-1.5 rounded-full',
                cell.iso === selectedDate
                  ? 'bg-white'
                  : 'bg-primary-500 dark:bg-primary-400',
              ]"
            />
            <span
              v-if="cell.classCount > 3"
              :class="[
                'text-[8px] font-bold ml-0.5',
                cell.iso === selectedDate
                  ? 'text-white'
                  : 'text-primary-500 dark:text-primary-400',
              ]"
            >+{{ cell.classCount - 3 }}</span>
          </div>
        </button>
      </div>
    </div>

    <!-- ─── Classes on selected date ────────────────────────────── -->
    <div v-if="selectedDate" class="space-y-2">
      <p class="text-xs font-semibold text-slate-500 dark:text-slate-400
                uppercase tracking-wider px-1">
        {{ selectedDateLabel }}
        <span class="ml-1 text-slate-400 dark:text-slate-500 normal-case font-normal">
          · {{ selectedDateClasses.length }}
          class{{ selectedDateClasses.length !== 1 ? 'es' : '' }}
        </span>
      </p>

      <div v-if="selectedDateClasses.length" class="space-y-2">
        <button
          v-for="cls in selectedDateClasses"
          :key="cls.slot_id"
          :class="classCardClasses(cls)"
          @click="selectClass(cls)"
        >
          <!-- Hour badge -->
          <div :class="[
            'flex h-11 w-11 shrink-0 items-center justify-center rounded-lg shadow-sm',
            selectedSlotId === cls.slot_id
              ? 'bg-white/20'
              : 'bg-gradient-to-br from-primary-500 to-cyan-500',
          ]">
            <div class="text-center text-white">
              <p class="text-[8px] font-medium opacity-90 leading-none">HOUR</p>
              <p class="text-sm font-bold leading-none mt-0.5">
                {{ cls.hour_details?.hour_number || '?' }}
              </p>
            </div>
          </div>

          <!-- Class info -->
          <div class="flex-1 min-w-0 text-left">
            <p :class="[
              'text-sm font-bold truncate',
              selectedSlotId === cls.slot_id
                ? 'text-white'
                : 'text-slate-900 dark:text-white',
            ]">
              {{ cls.subject_name || cls.subject }}
              <span
                v-if="cls.is_lab"
                :class="[
                  'ml-1 text-[10px] font-bold px-1 rounded',
                  selectedSlotId === cls.slot_id
                    ? 'bg-white/20 text-white'
                    : 'bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-300',
                ]"
              >
                🧪 LAB
              </span>
            </p>
            <p :class="[
              'text-xs truncate mt-0.5',
              selectedSlotId === cls.slot_id
                ? 'text-white/80'
                : 'text-slate-500 dark:text-slate-400',
            ]">
              {{ formatTime(cls.hour_details) }} ·
              {{ shortBatch(cls.batch) }}
              <span v-if="cls.room">· Room {{ cls.room }}</span>
            </p>
          </div>

          <!-- Action indicator -->
          <div
            v-if="selectedSlotId === cls.slot_id"
            class="shrink-0 inline-flex items-center gap-1 text-[11px] font-bold text-white"
          >
            <CheckCircle class="h-4 w-4" />
            SELECTED
          </div>
          <ArrowRight
            v-else
            class="h-4 w-4 text-slate-400 dark:text-slate-500 shrink-0"
          />
        </button>
      </div>

      <!-- No classes -->
      <div
        v-else
        class="rounded-lg bg-slate-50 dark:bg-slate-900/50 p-6 text-center
               border border-dashed border-slate-200 dark:border-slate-700"
      >
        <CalendarOff class="h-8 w-8 text-slate-300 dark:text-slate-600 mx-auto mb-2" />
        <p class="text-sm font-semibold text-slate-500 dark:text-slate-400">
          No classes scheduled
        </p>
        <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
          You don't have any classes on this date.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import {
  ArrowRight, CalendarOff, CheckCircle,
  ChevronLeft, ChevronRight, Loader2,
} from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

const props = defineProps({
  userEmail: { type: String, required: true },
})
const emit = defineEmits(['select'])

const { callApi } = useApi()

// ─── State ────────────────────────────────────────────────────────────────
const loading        = ref(false)
const cursorDate     = ref(new Date())
const selectedDate   = ref('')
const selectedSlotId = ref('')
const classesByDate  = ref({})

const today = ref(new Date().toISOString().slice(0, 10))

// ─── Computed ─────────────────────────────────────────────────────────────
const monthLabel = computed(() =>
  cursorDate.value.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })
)

const calendarCells = computed(() => {
  const year  = cursorDate.value.getFullYear()
  const month = cursorDate.value.getMonth()
  const firstOfMonth = new Date(year, month, 1)
  const lastOfMonth  = new Date(year, month + 1, 0)

  const start = new Date(firstOfMonth)
  start.setDate(start.getDate() - start.getDay())

  const end = new Date(lastOfMonth)
  end.setDate(end.getDate() + (6 - end.getDay()))

  const cells = []
  const cursor = new Date(start)
  const todayDate = new Date(today.value + 'T00:00:00')

  while (cursor <= end) {
    const iso = cursor.toISOString().slice(0, 10)
    cells.push({
      key:          iso,
      iso,
      day:          cursor.getDate(),
      isOtherMonth: cursor.getMonth() !== month,
      isToday:      iso === today.value,
      isPast:       cursor < todayDate,
      disabled:     cursor < todayDate,
      classCount:   (classesByDate.value[iso] || []).length,
    })
    cursor.setDate(cursor.getDate() + 1)
  }
  return cells
})

const selectedDateClasses = computed(() =>
  classesByDate.value[selectedDate.value] || []
)

const selectedDateLabel = computed(() => {
  if (!selectedDate.value) return ''
  const d = new Date(selectedDate.value + 'T00:00:00')
  return d.toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long',
  })
})

// ─── Style helpers ────────────────────────────────────────────────────────
const cellClasses = (cell) => {
  const base = 'h-16 flex flex-col items-center justify-center border-r border-b ' +
               'border-slate-100 dark:border-slate-700/50 transition-all'

  if (cell.disabled) {
    return `${base} cursor-not-allowed opacity-40`
  }
  if (cell.iso === selectedDate.value) {
    return `${base} bg-gradient-to-br from-primary-500 to-cyan-500
            shadow-inner cursor-pointer`
  }
  return `${base} cursor-pointer
          hover:bg-primary-50 dark:hover:bg-primary-500/10
          ${cell.isToday
            ? 'bg-primary-50/50 dark:bg-primary-500/10'
            : ''}`
}

const dayNumberClasses = (cell) => {
  // When the cell is selected (gradient bg), ALWAYS white
  if (cell.iso === selectedDate.value) {
    return 'text-sm font-semibold text-white'
  }
  // Other-month days are dimmed
  if (cell.isOtherMonth) {
    return 'text-sm font-semibold text-slate-300 dark:text-slate-600'
  }
  // Today gets accent color
  if (cell.isToday) {
    return 'text-sm font-semibold text-primary-600 dark:text-primary-300'
  }
  // Default
  return 'text-sm font-semibold text-slate-700 dark:text-slate-200'
}

const classCardClasses = (cls) => {
  const base = 'w-full flex items-center gap-3 p-3 rounded-xl transition-all text-left'
  if (selectedSlotId.value === cls.slot_id) {
    return `${base} bg-gradient-to-r from-primary-500 to-cyan-500
            shadow-lg shadow-primary-500/30 ring-2 ring-primary-300`
  }
  return `${base} bg-white dark:bg-slate-700/50
          ring-1 ring-slate-200 dark:ring-slate-600
          hover:ring-primary-300 dark:hover:ring-primary-500
          hover:shadow-md cursor-pointer`
}

const formatTime = (details) => {
  if (!details?.start_time || !details?.end_time) return ''
  const s = String(details.start_time).slice(0, 5)
  const e = String(details.end_time).slice(0, 5)
  return `${s}–${e}`
}

const shortBatch = (batch) => {
  if (!batch) return ''
  return batch
    .replace('Computer Science', 'CS')
    .replace('Mechanical Engineering', 'ME')
    .replace(/-(\d{2})(\d{2})-(\d{2})(\d{2})/, '-$2-$4')
}

// ─── Actions ──────────────────────────────────────────────────────────────
const changeMonth = (delta) => {
  const d = new Date(cursorDate.value)
  d.setMonth(d.getMonth() + delta)
  cursorDate.value = d
  loadMonth()
}

const goToToday = () => {
  cursorDate.value = new Date()
  selectedDate.value = today.value
  loadMonth()
}

const selectDate = (iso) => {
  selectedDate.value = iso
  selectedSlotId.value = ''
  emit('select', null)
}

const selectClass = (cls) => {
  selectedSlotId.value = cls.slot_id
  emit('select', {
    ...cls,
    date: selectedDate.value,
  })
}

// ─── Data loading ─────────────────────────────────────────────────────────
const loadMonth = async () => {
  if (!props.userEmail) return
  loading.value = true

  try {
    const year  = cursorDate.value.getFullYear()
    const month = cursorDate.value.getMonth()
    const start = new Date(year, month, 1)
    const end   = new Date(year, month + 1, 0)
    const todayDate = new Date(today.value + 'T00:00:00')

    const map = {}
    const cursor = new Date(start)

    while (cursor <= end) {
      if (cursor >= todayDate) {
        const iso = cursor.toISOString().slice(0, 10)
        const res = await callApi('sms.api.timetable.get_my_classes_today', {
          date: iso,
          user: props.userEmail,
        })
        const classes = res?.classes || []
        if (classes.length) {
          map[iso] = classes
        }
      }
      cursor.setDate(cursor.getDate() + 1)
    }
    classesByDate.value = map

    if (!selectedDate.value && map[today.value]) {
      selectedDate.value = today.value
    }
  } catch (e) {
    console.error('[MyCalendarPicker] loadMonth failed:', e)
  } finally {
    loading.value = false
  }
}

// ─── Lifecycle ────────────────────────────────────────────────────────────
watch(() => props.userEmail, loadMonth)
onMounted(loadMonth)

defineExpose({
  clearSelection: () => {
    selectedSlotId.value = ''
    selectedDate.value   = ''
  },
})
</script>
