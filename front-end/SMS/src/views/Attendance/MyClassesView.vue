<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">
          My Classes
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {{ dayLabel }}, {{ formattedDate }}
        </p>
      </div>

      <!-- Date navigator -->
      <div class="flex items-center gap-2">
        <button
          class="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
          @click="changeDate(-1)"
        >
          <ChevronLeft class="h-4 w-4" />
        </button>
        <input
          v-model="selectedDate"
          type="date"
          class="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="loadClasses"
        />
        <button
          class="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
          @click="changeDate(1)"
        >
          <ChevronRight class="h-4 w-4" />
        </button>
        <button
          v-if="selectedDate !== today"
          class="rounded-lg bg-primary-50 dark:bg-primary-500/10 px-3 py-2 text-sm font-semibold text-primary-600 dark:text-primary-300 hover:bg-primary-100"
          @click="goToToday"
        >
          Today
        </button>
      </div>
    </div>

    <!-- Summary stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="rounded-xl bg-white dark:bg-slate-800 p-4 ring-1 ring-slate-200 dark:ring-slate-700">
        <div class="flex items-center gap-2 text-xs text-slate-500">
          <CalendarDays class="h-3.5 w-3.5" />
          Total Classes
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
          {{ classes.length }}
        </p>
      </div>
      <div class="rounded-xl bg-white dark:bg-slate-800 p-4 ring-1 ring-slate-200 dark:ring-slate-700">
        <div class="flex items-center gap-2 text-xs text-slate-500">
          <CheckCircle class="h-3.5 w-3.5 text-emerald-500" />
          Marked
        </div>
        <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
          {{ markedCount }}
        </p>
      </div>
      <div class="rounded-xl bg-white dark:bg-slate-800 p-4 ring-1 ring-slate-200 dark:ring-slate-700">
        <div class="flex items-center gap-2 text-xs text-slate-500">
          <Clock class="h-3.5 w-3.5 text-amber-500" />
          Pending
        </div>
        <p class="text-2xl font-bold text-amber-600 mt-1">
          {{ pendingCount }}
        </p>
      </div>
      <div class="rounded-xl bg-white dark:bg-slate-800 p-4 ring-1 ring-slate-200 dark:ring-slate-700">
        <div class="flex items-center gap-2 text-xs text-slate-500">
          <RefreshCcw class="h-3.5 w-3.5 text-blue-500" />
          Substituting
        </div>
        <p class="text-2xl font-bold text-blue-600 mt-1">
          {{ substituteCount }}
        </p>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-3">
      <div
        v-for="i in 3"
        :key="i"
        class="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 animate-pulse h-40"
      />
    </div>

    <!-- Class list -->
    <div v-else-if="classes.length" class="space-y-3">
      <div
        v-for="cls in classes"
        :key="cls.slot_id"
        :class="[
          'rounded-xl bg-white dark:bg-slate-800 shadow-sm ring-1 transition-all',
          cls.is_substitute
            ? 'ring-blue-300 dark:ring-blue-700/50 bg-blue-50/30 dark:bg-blue-500/5'
            : 'ring-slate-200 dark:ring-slate-700',
        ]"
      >
        <!-- Substitute badge -->
        <div
          v-if="cls.is_substitute"
          class="flex items-center gap-2 px-5 py-2 bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300 text-xs font-semibold rounded-t-xl"
        >
          <RefreshCcw class="h-3.5 w-3.5" />
          You're substituting for
          <strong>{{ getFacultyShort(cls.original_faculty) }}</strong>
          today
          <span v-if="cls.sub_reason" class="text-blue-600 dark:text-blue-400 ml-2">
            · {{ cls.sub_reason }}
          </span>
        </div>

        <div class="p-5">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <!-- Left: class info -->
            <div class="flex-1 min-w-0">
              <!-- Hour -->
              <div class="flex items-center gap-3 mb-2">
                <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-cyan-500 text-white shadow-md">
                  <div class="text-center">
                    <p class="text-[10px] font-medium opacity-90 leading-none">HOUR</p>
                    <p class="text-lg font-bold leading-none mt-0.5">
                      {{ cls.hour_details?.hour_number || '?' }}
                    </p>
                  </div>
                </div>
                <div>
                  <p class="text-xs text-slate-400">
                    {{ formatHour(cls.hour_details) }}
                  </p>
                  <p class="text-lg font-bold text-slate-900 dark:text-white">
                    {{ cls.subject_name || cls.subject || 'Unknown Subject' }}
                  </p>
                </div>
              </div>

              <!-- Batch + Room -->
              <div class="ml-15 flex flex-wrap items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
                <span class="flex items-center gap-1">
                  <Building2 class="h-3.5 w-3.5" />
                  {{ cls.batch }}
                </span>
                <span class="flex items-center gap-1">
                  <Users class="h-3.5 w-3.5" />
                  {{ cls.student_count }} students
                </span>
                <span v-if="cls.room" class="flex items-center gap-1">
                  <MapPin class="h-3.5 w-3.5" />
                  Room {{ cls.room }}
                </span>
                <span
                  v-if="cls.is_lab"
                  class="inline-flex items-center gap-1 rounded-full bg-purple-50 dark:bg-purple-500/20 px-2 py-0.5 text-xs font-semibold text-purple-700 dark:text-purple-300"
                >
                  🧪 LAB
                </span>
              </div>

              <!-- Attendance status -->
              <div class="mt-3 flex items-center gap-2 text-sm">
                <template v-if="cls.attendance_marked > 0">
                  <CheckCircle class="h-4 w-4 text-emerald-500" />
                  <span class="text-emerald-700 dark:text-emerald-400 font-medium">
                    {{ cls.attendance_marked }} of {{ cls.student_count }} marked
                  </span>
                </template>
                <template v-else>
                  <AlertCircle class="h-4 w-4 text-amber-500" />
                  <span class="text-amber-700 dark:text-amber-400 font-medium">
                    Attendance not marked yet
                  </span>
                </template>
              </div>
            </div>

            <!-- Right: action button -->
            <div class="shrink-0">
              <button
                class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-primary-500 to-cyan-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-primary-500/30 hover:shadow-xl transition-all"
                @click="goToMark(cls)"
              >
                <template v-if="cls.attendance_marked > 0">
                  <Edit3 class="h-4 w-4" />
                  Edit Attendance
                </template>
                <template v-else>
                  <ClipboardCheck class="h-4 w-4" />
                  Mark Attendance
                </template>
                <ArrowRight class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-else
      class="rounded-xl bg-white dark:bg-slate-800 p-12 text-center shadow-sm ring-1 ring-slate-200 dark:ring-slate-700"
    >
      <CalendarOff class="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
      <h3 class="text-base font-semibold text-slate-700 dark:text-slate-300">
        No classes scheduled
      </h3>
      <p class="text-sm text-slate-400 mt-1">
        You don't have any classes on {{ dayLabel }}, {{ formattedDate }}.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  AlertCircle, ArrowRight, Building2, CalendarDays, CalendarOff,
  CheckCircle, ChevronLeft, ChevronRight, ClipboardCheck, Clock,
  Edit3, MapPin, RefreshCcw, Users,
} from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'

const router       = useRouter()
const { callApi }  = useApi()
const { user, email, isAdmin } = useAuth()

const today        = new Date().toISOString().slice(0, 10)
const selectedDate = ref(today)
const classes      = ref([])
const loading      = ref(false)

// ─── Computed ────────────────────────────────────────────────────────────────
const formattedDate = computed(() => {
  const d = new Date(selectedDate.value + 'T00:00:00')
  return d.toLocaleDateString('en-IN', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
})

const dayLabel = computed(() => {
  const d = new Date(selectedDate.value + 'T00:00:00')
  return d.toLocaleDateString('en-IN', { weekday: 'long' })
})

const markedCount = computed(() =>
  classes.value.filter(c => c.attendance_marked > 0).length
)

const pendingCount = computed(() =>
  classes.value.filter(c => !c.attendance_marked).length
)

const substituteCount = computed(() =>
  classes.value.filter(c => c.is_substitute).length
)

// ─── Methods ─────────────────────────────────────────────────────────────────
const formatHour = (details) => {
  if (!details?.start_time || !details?.end_time) return ''
  return `${details.start_time.slice(0, 5)} – ${details.end_time.slice(0, 5)}`
}

const getFacultyShort = (email) => {
  if (!email) return 'someone'
  // mrs.sy@college.local → MRS. SY
  const prefix = email.split('@')[0]
  return prefix.toUpperCase().replace('.', '. ')
}

const changeDate = (delta) => {
  const d = new Date(selectedDate.value + 'T00:00:00')
  d.setDate(d.getDate() + delta)
  selectedDate.value = d.toISOString().slice(0, 10)
  loadClasses()
}

const goToToday = () => {
  selectedDate.value = today
  loadClasses()
}

const goToMark = (cls) => {
  router.push({
    name: 'MarkAttendance',
    params: {
      slot: cls.slot_id,
      date: selectedDate.value,
    },
  })
}

const loadClasses = async () => {
  loading.value = true
  try {
    const userParam = email.value || user.value?.user
    const res = await callApi('sms.api.timetable.get_my_classes_today', {
      date: selectedDate.value,
      user: userParam,
    })
    classes.value = res?.classes || []
  } catch (e) {
    console.error('Failed to load classes:', e)
    classes.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadClasses)
</script>
