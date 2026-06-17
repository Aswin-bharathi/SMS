<template>
  <div class="space-y-6">
    <!-- Back -->
    <button @click="$router.back()" class="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors">
      <ArrowLeft class="w-4 h-4" />
      Back to Students
    </button>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
    </div>

    <div v-else-if="student" class="space-y-5">
      <!-- Profile Header -->
      <div class="card">
        <div class="flex flex-col sm:flex-row items-start gap-6">
          <!-- Avatar -->
          <div class="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary-400 to-cyan-500
                      flex items-center justify-center text-white font-bold text-3xl shadow-lg shrink-0">
            {{ studentName.charAt(0) }}
          </div>

          <!-- Info -->
          <div class="flex-1">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h1 class="text-2xl font-bold text-gray-800 dark:text-white">{{ studentName }}</h1>
                <p class="text-gray-400 dark:text-gray-500">{{ student.student_id || student.name }}</p>
              </div>
              <div class="flex items-center gap-2">
                <Badge :variant="student.status">{{ student.status }}</Badge>
                <button @click="showEditModal = true" class="btn-secondary text-sm">
                  <Pencil class="w-4 h-4" />
                  Edit
                </button>
              </div>
            </div>

            <!-- Quick Stats -->
            <div class="mt-5 flex flex-wrap gap-6">
              <div v-for="item in quickInfo" :key="item.label" class="flex items-center gap-2">
                <component :is="item.icon" class="w-4 h-4 text-gray-400" />
                <span class="text-sm text-gray-600 dark:text-gray-300">{{ item.value || '—' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="overflow-x-auto">
        <div class="flex w-max items-center gap-1 bg-white dark:bg-gray-800 p-1 rounded-2xl
                    border border-gray-100 dark:border-gray-700">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            :class="[
              'px-4 py-2 rounded-xl text-sm font-medium transition-all',
              activeTab === tab.key
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
            ]"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div v-for="item in recordSummary" :key="item.label" class="card !p-4">
          <p class="text-sm text-gray-400 dark:text-gray-500">{{ item.label }}</p>
          <p class="mt-2 text-2xl font-bold text-gray-800 dark:text-white">{{ item.value }}</p>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="animate-fade-in">

        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="grid grid-cols-1 lg:grid-cols-2 gap-5">

          <!-- Personal Details -->
          <div class="card space-y-4">
            <h2 class="font-bold text-gray-800 dark:text-white">Personal Details</h2>
            <div class="space-y-1">
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Full Name</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ studentName || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Date of Birth</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.date_of_birth || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Gender</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.gender || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Blood Group</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.blood_group || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Nationality</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.nationality || '—' }}</span>
              </div>
            </div>
          </div>

          <!-- Academic Details -->
          <div class="card space-y-4">
            <h2 class="font-bold text-gray-800 dark:text-white">Academic Details</h2>
            <div class="space-y-1">
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Program</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.program || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Department</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.department || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Academic Year</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.academic_year || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Semester</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.current_semester ? `Semester ${student.current_semester}` : '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Enrollment Date</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.enrollment_date || '—' }}</span>
              </div>
            </div>
          </div>

          <!-- Contact Details -->
          <div class="card space-y-4">
            <h2 class="font-bold text-gray-800 dark:text-white">Contact Details</h2>
            <div class="space-y-1">
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Email</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.email || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Phone</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.phone || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Address</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.address || '—' }}</span>
              </div>
            </div>
          </div>

          <!-- Guardian Details -->
          <div class="card space-y-4">
            <h2 class="font-bold text-gray-800 dark:text-white">Guardian Details</h2>
            <div class="space-y-1">
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Guardian</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.guardian_name || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Guardian Phone</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.guardian_phone || '—' }}</span>
              </div>
              <div class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700/50 last:border-0">
                <span class="text-sm text-gray-400">Record Created</span>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ student.creation || '—' }}</span>
              </div>
            </div>
          </div>

        </div>

        <!-- Attendance Tab -->
        <div v-if="activeTab === 'attendance'" class="card">
          <h2 class="font-bold text-gray-800 dark:text-white mb-5">Attendance Records</h2>
          <div v-if="attendance.length" class="space-y-3">
            <div
              v-for="att in attendance"
              :key="att.name"
              class="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50"
            >
              <div class="flex items-center gap-3">
                <div :class="['w-2 h-2 rounded-full', att.status === 'Present' ? 'bg-green-500' : 'bg-red-500']" />
                <div>
                  <p class="text-sm font-medium text-gray-800 dark:text-white">{{ att.course }}</p>
                  <p class="text-xs text-gray-400">{{ att.attendance_date }}</p>
                </div>
              </div>
              <Badge :variant="att.status">{{ att.status }}</Badge>
            </div>
          </div>
          <p v-else class="text-center text-gray-400 py-8">No attendance records found.</p>
        </div>

        <!-- Fees Tab -->
        <div v-if="activeTab === 'fees'" class="card">
          <h2 class="font-bold text-gray-800 dark:text-white mb-5">Fee Records</h2>
          <div v-if="fees.length" class="space-y-3">
            <div
              v-for="fee in fees"
              :key="fee.name"
              class="flex flex-col gap-3 p-4 rounded-xl border border-gray-100 dark:border-gray-700 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <p class="font-medium text-gray-800 dark:text-white">{{ fee.fee_type }}</p>
                <p class="text-xs text-gray-400">Due: {{ fee.due_date }} · Paid {{ money(fee.paid_amount) }}</p>
              </div>
              <div class="sm:text-right">
                <p class="font-bold text-gray-800 dark:text-white">{{ money(fee.total_amount) }}</p>
                <Badge :variant="fee.payment_status">{{ fee.payment_status }}</Badge>
              </div>
            </div>
          </div>
          <p v-else class="text-center text-gray-400 py-8">No fee records found.</p>
        </div>

        <!-- Results Tab -->
        <div v-if="activeTab === 'results'" class="card">
          <h2 class="font-bold text-gray-800 dark:text-white mb-5">Exam Results</h2>
          <div v-if="results.length" class="space-y-3">
            <div
              v-for="result in results"
              :key="result.name"
              class="p-4 rounded-xl border border-gray-100 dark:border-gray-700"
            >
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium text-gray-800 dark:text-white">
                    {{ result.exam_type }} — Sem {{ result.semester }}
                  </p>
                  <p class="text-xs text-gray-400">{{ result.result_date }}</p>
                </div>
                <div class="text-right">
                  <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">
                    {{ result.overall_percentage?.toFixed(1) }}%
                  </p>
                  <p class="text-sm font-semibold text-gray-500">Grade: {{ result.overall_grade }}</p>
                </div>
              </div>
              <div class="mt-3 h-2 rounded-full bg-gray-100 dark:bg-gray-700">
                <div
                  class="h-full rounded-full bg-primary-600"
                  :style="{ width: `${result.overall_percentage}%` }"
                />
              </div>
            </div>
          </div>
          <p v-else class="text-center text-gray-400 py-8">No results found.</p>
        </div>

      </div>
    </div>

    <!-- Edit Modal -->
    <Modal :show="showEditModal" title="Edit Student" size="lg" @close="showEditModal = false">
      <StudentForm
        :initial-data="student"
        :edit-mode="true"
        @saved="onSaved"
        @cancel="showEditModal = false"
      />
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Pencil, Mail, Phone, BookOpen, Calendar } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import Modal from '@/components/ui/Modal.vue'
import StudentForm from './StudentForm.vue'
import { useStudentStore } from '@/stores/student'
import { useApi } from '@/composables/useApi'

const route = useRoute()
const studentStore = useStudentStore()
const { callApi } = useApi()

const loading = ref(true)
const student = ref(null)
const attendance = ref([])
const fees = ref([])
const results = ref([])
const activeTab = ref('overview')
const showEditModal = ref(false)

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'attendance', label: 'Attendance' },
  { key: 'fees', label: 'Fees' },
  { key: 'results', label: 'Results' },
]

const quickInfo = computed(() => [
  { icon: Mail, value: student.value?.email },
  { icon: Phone, value: student.value?.phone },
  { icon: BookOpen, value: student.value?.program },
  { icon: Calendar, value: student.value?.enrollment_date },
])

const money = (value) => `₹${Number(value || 0).toLocaleString()}`

const recordSummary = computed(() => {
  const present = attendance.value.filter(row => row.status === 'Present').length
  const attendanceRate = attendance.value.length ? Math.round((present / attendance.value.length) * 100) : 0
  const outstanding = fees.value.reduce((sum, fee) => sum + Number(fee.outstanding_amount || 0), 0)
  const bestScore = results.value.reduce((score, result) => Math.max(score, Number(result.overall_percentage || 0)), 0)
  return [
    { label: 'Attendance', value: attendance.value.length ? `${attendanceRate}%` : '0%' },
    { label: 'Fee Outstanding', value: money(outstanding) },
    { label: 'Results', value: results.value.length },
    { label: 'Best Score', value: bestScore ? `${bestScore.toFixed(1)}%` : '-' },
  ]
})

const studentName = computed(() => {
  if (!student.value) return 'Student'
  if (student.value.full_name) return student.value.full_name
  if (student.value.student_name) return student.value.student_name
  return [student.value.first_name, student.value.last_name].filter(Boolean).join(' ') || student.value.name || 'Student'
})

onMounted(async () => {
  try {
    const id = route.params.id
    await studentStore.fetchStudent(id)
    student.value = studentStore.currentStudent

    attendance.value = await callApi('sms.api.attendance.get_attendance', { student: id })
    fees.value = await callApi('sms.api.fee.get_fees', { student: id })
    results.value = await callApi('sms.api.result.get_results', { student: id })
  } finally {
    loading.value = false
  }
})

const onSaved = async () => {
  showEditModal.value = false
  await studentStore.fetchStudent(route.params.id)
  student.value = studentStore.currentStudent
}
</script>
