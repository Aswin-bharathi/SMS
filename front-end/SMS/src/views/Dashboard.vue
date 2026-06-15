<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white sm:text-3xl">
          Good {{ timeOfDay }}, Admin
        </h1>
        <p class="text-gray-500 dark:text-gray-400 text-sm mt-1">
          Here's what's happening today — {{ formattedDate }}
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <button v-if="showSeedAction" class="btn-secondary" :disabled="seeding" @click="seedDemoData">
          <Database class="w-4 h-4" />
          {{ seeding ? 'Loading...' : 'Load Demo Data' }}
        </button>
        <button class="btn-primary" @click="$router.push('/students?add=1')">
          <Plus class="w-4 h-4" />
          Add Student
        </button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
      <StatCard
        v-for="stat in stats"
        :key="stat.label"
        v-bind="stat"
      />
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
      <div
        v-for="item in detailCards"
        :key="item.label"
        class="card !p-5 overflow-hidden relative"
      >
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ item.label }}</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ item.value }}</p>
        <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">{{ item.caption }}</p>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Enrollment Chart -->
      <div class="lg:col-span-2 card">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="font-bold text-gray-800 dark:text-white">Student Enrollment</h2>
            <p class="text-sm text-gray-400 dark:text-gray-500">Last 6 months</p>
          </div>
          <select v-model="selectedMonths" class="text-sm input-field w-auto py-1.5" @change="fetchDashboard">
            <option :value="6">Last 6 months</option>
            <option :value="12">Last year</option>
          </select>
        </div>
        <div class="h-72 max-h-72">
          <Bar :data="enrollmentChartData" :options="chartOptions" />
        </div>
      </div>

      <!-- Program Distribution -->
      <div class="card">
        <div class="mb-6">
          <h2 class="font-bold text-gray-800 dark:text-white">By Program</h2>
          <p class="text-sm text-gray-400 dark:text-gray-500">Active students</p>
        </div>
        <div class="h-52 max-h-52">
          <Doughnut :data="programChartData" :options="doughnutOptions" />
        </div>
        <!-- Legend -->
        <div class="mt-4 space-y-2">
          <div
            v-for="(prog, i) in programData"
            :key="prog.label"
            class="flex items-center justify-between text-sm"
          >
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full" :style="{ background: chartColors[i] }" />
              <span class="text-gray-600 dark:text-gray-400">{{ prog.label }}</span>
            </div>
            <span class="font-semibold text-gray-800 dark:text-white">{{ prog.count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Recent Students -->
      <div class="lg:col-span-2 card">
        <div class="flex items-center justify-between mb-5">
          <h2 class="font-bold text-gray-800 dark:text-white">Recent Students</h2>
          <router-link to="/students" class="text-sm text-primary-600 dark:text-primary-400 font-medium hover:underline">
            View all
          </router-link>
        </div>

        <div class="space-y-3">
          <div
            v-for="student in recentStudents"
            :key="student.name"
            class="flex items-center gap-4 p-3 rounded-xl hover:bg-gray-50
                   dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
            @click="$router.push(`/students/${getStudentId(student)}`)"
          >
            <!-- Avatar -->
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-400 to-cyan-500
                        flex items-center justify-center text-white font-bold text-sm shrink-0">
              {{ getStudentName(student).charAt(0) }}
            </div>

            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-800 dark:text-white text-sm truncate">
                {{ getStudentName(student) }}
              </p>
              <p class="text-xs text-gray-400 dark:text-gray-500 truncate">
                {{ student.program || 'Unassigned' }} · {{ getStudentId(student) }}
              </p>
            </div>

            <Badge :variant="student.status">{{ student.status }}</Badge>
          </div>
        </div>
      </div>

      <!-- Attendance Today -->
      <div class="card">
        <h2 class="font-bold text-gray-800 dark:text-white mb-5">Today's Attendance</h2>
        <div class="space-y-4">
          <div
            v-for="item in attendanceSummary"
            :key="item.label"
            class="space-y-1.5"
          >
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600 dark:text-gray-400 font-medium">{{ item.label }}</span>
              <span class="font-bold text-gray-800 dark:text-white">{{ item.value }}</span>
            </div>
            <div class="h-2 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-1000"
                :class="item.color"
                :style="{ width: `${item.percent}%` }"
              />
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="mt-6 pt-5 border-t border-gray-100 dark:border-gray-700 grid grid-cols-2 gap-3">
          <div class="text-center p-3 rounded-xl bg-green-50 dark:bg-green-900/20">
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">
              {{ dashStats.attendance?.present_today || 0 }}
            </p>
            <p class="text-xs text-green-600/70 dark:text-green-400/70 font-medium">Present</p>
          </div>
          <div class="text-center p-3 rounded-xl bg-red-50 dark:bg-red-900/20">
            <p class="text-2xl font-bold text-red-500 dark:text-red-400">
              {{ dashStats.attendance?.absent_today || 0 }}
            </p>
            <p class="text-xs text-red-500/70 dark:text-red-400/70 font-medium">Absent</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-5">
      <div class="card xl:col-span-2">
        <div class="flex items-center justify-between mb-5">
          <div>
            <h2 class="font-bold text-gray-800 dark:text-white">Program Health</h2>
            <p class="text-sm text-gray-400 dark:text-gray-500">Student distribution across active programs</p>
          </div>
          <span class="text-xs font-medium text-gray-400 dark:text-gray-500">{{ programData.length }} programs</span>
        </div>
        <div class="space-y-3">
          <div
            v-for="prog in programData"
            :key="prog.label"
            class="flex items-center justify-between gap-4 rounded-xl bg-gray-50/80 dark:bg-gray-800/50 px-4 py-3"
          >
            <div class="min-w-0">
              <p class="font-semibold text-gray-800 dark:text-white truncate">{{ prog.label }}</p>
              <p class="text-xs text-gray-400 dark:text-gray-500">Students enrolled in program</p>
            </div>
            <div class="flex items-center gap-3 shrink-0">
              <div class="h-2 w-32 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                <div class="h-full rounded-full bg-gradient-to-r from-primary-500 to-cyan-500" :style="{ width: `${Math.max(8, prog.percent)}%` }" />
              </div>
              <span class="w-10 text-right text-sm font-bold text-gray-800 dark:text-white">{{ prog.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="font-bold text-gray-800 dark:text-white mb-5">Quick Summary</h2>
        <div class="space-y-4">
          <div v-for="item in quickSummary" :key="item.label" class="rounded-xl border border-gray-100 dark:border-gray-700 p-4">
            <div class="flex items-center justify-between">
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ item.label }}</p>
              <p class="text-base font-bold text-gray-800 dark:text-white">{{ item.value }}</p>
            </div>
            <div class="mt-3 h-2 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden">
              <div class="h-full rounded-full" :class="item.bar" :style="{ width: `${item.percent}%` }" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  ArcElement, Tooltip, Legend
} from 'chart.js'
import { Database, Plus, Users, BookOpen, CreditCard, TrendingUp } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import { useApi } from '@/composables/useApi'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const StatCard = {
  props: ['label', 'value', 'icon', 'color', 'iconColor', 'trend', 'trendUp'],
  template: `
    <div class="card group overflow-hidden">
      <div class="flex items-start justify-between gap-4">
        <div class="min-w-0">
          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ label }}</p>
          <p class="mt-2 truncate text-2xl font-bold text-slate-900 dark:text-white">{{ value }}</p>
        </div>
        <div :class="['flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl shadow-sm transition-transform duration-300 group-hover:scale-105', color]">
          <component :is="icon" :class="['h-5 w-5', iconColor]" />
        </div>
      </div>
      <div class="mt-5 flex items-center gap-2 text-xs font-semibold">
        <span
          :class="trendUp === false ? 'bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-300' : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300'"
          class="rounded-full px-2 py-1"
        >
          {{ trend }}
        </span>
        <span class="text-slate-400">from last term</span>
      </div>
    </div>
  `
}

const { callApi } = useApi()
const dashStats = ref({})
const recentStudents = ref([])
const selectedMonths = ref(6)
const seeding = ref(false)

const chartColors = ['#6366f1', '#22c55e', '#f59e0b', '#ec4899', '#14b8a6']

const timeOfDay = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Morning'
  if (h < 17) return 'Afternoon'
  return 'Evening'
})

const formattedDate = computed(() =>
  new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
)

const stats = computed(() => [
  {
    label: 'Total Students',
    value: dashboardTotals.value.total_students || 0,
    icon: Users,
    color: 'bg-primary-50 dark:bg-primary-900/20',
    iconColor: 'text-primary-600 dark:text-primary-400',
    trend: '+12%',
    trendUp: true
  },
  {
    label: 'Active Students',
    value: dashboardTotals.value.active_students || 0,
    icon: TrendingUp,
    color: 'bg-green-50 dark:bg-green-900/20',
    iconColor: 'text-green-600 dark:text-green-400',
    trend: '+5%',
    trendUp: true
  },
  {
    label: 'Total Courses',
    value: dashboardTotals.value.total_courses || 0,
    icon: BookOpen,
    color: 'bg-yellow-50 dark:bg-yellow-900/20',
    iconColor: 'text-yellow-600 dark:text-yellow-400',
    trend: 'Stable',
    trendUp: null
  },
  {
    label: 'Fee Outstanding',
    value: `₹${(dashStats.value.fee_stats?.total_outstanding || 0).toLocaleString()}`,
    icon: CreditCard,
    color: 'bg-red-50 dark:bg-red-900/20',
    iconColor: 'text-red-500 dark:text-red-400',
    trend: `${dashStats.value.fee_stats?.collection_rate || 0}% collected`,
    trendUp: false
  }
])

const dashboardTotals = computed(() => dashStats.value.totals || dashStats.value)
const showSeedAction = computed(() => !Number(dashboardTotals.value.total_students || 0))
const studentAttendanceRate = computed(() => {
  const present = dashStats.value.attendance?.present_today || 0
  const absent = dashStats.value.attendance?.absent_today || 0
  const total = present + absent
  return total ? Math.round((present / total) * 100) : 0
})

const programData = computed(() => {
  const items = (dashStats.value.by_program || []).map((p) => ({
    label: p.program,
    count: p.count,
  }))
  const total = items.reduce((sum, item) => sum + Number(item.count || 0), 0) || 1
  return items.map((item) => ({
    ...item,
    percent: Math.max(8, Math.round((Number(item.count || 0) / total) * 100)),
  }))
})

const detailCards = computed(() => [
  {
    label: 'Departments',
    value: dashboardTotals.value.total_departments || 0,
    caption: 'Academic units currently configured',
  },
  {
    label: 'Programs',
    value: dashboardTotals.value.total_programs || 0,
    caption: 'Active and inactive programs combined',
  },
  {
    label: 'Attendance Rate',
    value: `${studentAttendanceRate.value}%`,
    caption: `Present ${dashStats.value.attendance?.present_today || 0} / Total ${((dashStats.value.attendance?.present_today || 0) + (dashStats.value.attendance?.absent_today || 0)) || 0}`,
  },
  {
    label: 'Fee Collection',
    value: `${dashStats.value.fee_stats?.collection_rate || 0}%`,
    caption: `Collected ₹${(dashStats.value.fee_stats?.total_collected || 0).toLocaleString()} of billed ₹${(dashStats.value.fee_stats?.total_billed || 0).toLocaleString()}`,
  },
])

const quickSummary = computed(() => [
  {
    label: 'Active Students',
    value: dashboardTotals.value.active_students || 0,
    percent: dashboardTotals.value.total_students ? Math.round(((dashboardTotals.value.active_students || 0) / dashboardTotals.value.total_students) * 100) : 0,
    bar: 'bg-emerald-500',
  },
  {
    label: 'Inactive Students',
    value: dashboardTotals.value.inactive_students || 0,
    percent: dashboardTotals.value.total_students ? Math.round(((dashboardTotals.value.inactive_students || 0) / dashboardTotals.value.total_students) * 100) : 0,
    bar: 'bg-red-500',
  },
  {
    label: 'Open Fees',
    value: `₹${(dashStats.value.fee_stats?.total_outstanding || 0).toLocaleString()}`,
    percent: 100,
    bar: 'bg-amber-500',
  },
])

const getStudentId = (student) => student.student_id || student.name
const getStudentName = (student) => {
  if (student.full_name) return student.full_name
  if (student.student_name) return student.student_name
  return [student.first_name, student.last_name].filter(Boolean).join(' ') || student.name || 'Student'
}

const enrollmentChartData = computed(() => {
  const data = dashStats.value.enrollment_trend || dashStats.value.monthly_enrollment || []
  return {
    labels: data.map(d => d.month),
    datasets: [{
      label: 'Enrollments',
      data: data.map(d => d.count),
      backgroundColor: '#6366f1',
      borderRadius: 8,
      borderSkipped: false,
    }]
  }
})

const programChartData = computed(() => ({
  labels: programData.value.map(p => p.label),
  datasets: [{
    data: programData.value.map(p => p.count),
    backgroundColor: chartColors,
    borderWidth: 0,
    hoverOffset: 6,
  }]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, border: { display: false } },
    y: { grid: { color: 'rgba(0,0,0,0.05)' }, border: { display: false } }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  cutout: '70%'
}

const totalAttendance = computed(() => {
  const p = dashStats.value.attendance?.present_today || 0
  const a = dashStats.value.attendance?.absent_today || 0
  return p + a || 1
})

const attendanceSummary = computed(() => [
  {
    label: 'Present',
    value: dashStats.value.attendance?.present_today || 0,
    percent: ((dashStats.value.attendance?.present_today || 0) / totalAttendance.value) * 100,
    color: 'bg-green-500'
  },
  {
    label: 'Absent',
    value: dashStats.value.attendance?.absent_today || 0,
    percent: ((dashStats.value.attendance?.absent_today || 0) / totalAttendance.value) * 100,
    color: 'bg-red-500'
  }
])

const fetchDashboard = async () => {
  try {
    dashStats.value = await callApi('sms.api.student.get_dashboard_stats', { months: selectedMonths.value })
    // The backend already includes 'recent_students' inside the dashStats response. 
    // No need for a second call to get_all_students.
    recentStudents.value = dashStats.value.recent_students || []
  } catch (e) {
    console.error(e)
  }
}

const seedDemoData = async () => {
  seeding.value = true
  try {
    await callApi('sms.api.student.seed_demo_data', {}, { method: 'POST' })
    await fetchDashboard()
  } finally {
    seeding.value = false
  }
}

onMounted(async () => {
  await fetchDashboard()
  if (import.meta.env.DEV && !Number(dashboardTotals.value.total_students || 0) && !sessionStorage.getItem('sms-demo-seeded')) {
    await seedDemoData()
    sessionStorage.setItem('sms-demo-seeded', '1')
  }
})
</script>
