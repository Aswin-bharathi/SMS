<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white">Attendance</h1>
        <p class="text-sm text-gray-400 mt-1">Track and manage student attendance</p>
      </div>
      <button @click="showMarkModal = true" class="btn-primary">
        <Plus class="w-4 h-4" />
        Mark Attendance
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="item in summary"
        :key="item.label"
        :class="['card text-center !py-5', item.bg]"
      >
        <p class="text-3xl font-bold" :class="item.textColor">{{ item.value }}</p>
        <p class="text-sm mt-1" :class="item.labelColor">{{ item.label }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card !p-4 flex flex-wrap gap-3">
      <input v-model="filters.date" type="date" class="input-field w-auto py-2 text-sm" @change="fetchAttendance" />
      <input v-model="filters.student" placeholder="Student ID..." class="input-field w-56 py-2 text-sm" @input="debouncedFetch" />
      <select v-model="filters.department" class="input-field w-auto py-2 text-sm" @change="fetchAttendance">
        <option value="">All Departments</option>
        <option v-for="d in departments" :key="d.name" :value="d.name">{{ d.department_name }}</option>
      </select>
      <select v-model="filters.batch" class="input-field w-auto py-2 text-sm" @change="fetchAttendance">
        <option value="">All Batches</option>
        <option v-for="b in batches" :key="b.name" :value="b.name">{{ b.batch }}</option>
      </select>
      <select v-model="filters.hour" class="input-field w-auto py-2 text-sm" @change="fetchAttendance">
        <option value="">All Hours</option>
        <option v-for="hour in 5" :key="hour" :value="hour">Hour {{ hour }}</option>
      </select>
      <select v-model="filters.status" class="input-field w-auto py-2 text-sm" @change="fetchAttendance">
        <option value="">All Status</option>
        <option>Present</option>
        <option>Absent</option>
        <option>Late</option>
        <option>Excused</option>
      </select>
      <button @click="clearFilters" class="btn-secondary text-sm">
        <X class="w-4 h-4" />
        Clear
      </button>
    </div>

    <!-- Table -->
    <div class="card !p-0 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-700">
              <th v-for="col in ['Student', 'Department', 'Batch', 'Course', 'Date', 'Hour', 'Status', 'Remarks']" :key="col"
                class="px-5 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50 dark:divide-gray-700/50">
            <tr v-for="att in attendance" :key="att.name"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
              <td class="px-5 py-4">
                <p class="font-medium text-gray-800 dark:text-white text-sm">{{ att.student_name }}</p>
                <p class="text-xs text-gray-400">{{ att.student }}</p>
              </td>
              <td class="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">{{ att.department || '-' }}</td>
              <td class="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">{{ att.batch || '-' }}</td>
              <td class="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">{{ att.course }}</td>
              <td class="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">{{ att.attendance_date }}</td>
              <td class="px-5 py-4 text-sm font-semibold text-gray-700 dark:text-gray-200">Hour {{ att.attendance_hour }}</td>
              <td class="px-5 py-4"><Badge :variant="att.status">{{ att.status }}</Badge></td>
              <td class="px-5 py-4 text-sm text-gray-400 dark:text-gray-500">{{ att.remarks || '—' }}</td>
            </tr>
            <tr v-if="!attendance.length">
              <td colspan="8" class="text-center py-16 text-gray-400 dark:text-gray-500">
                No attendance records found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Mark Attendance Modal -->
    <Modal :show="showMarkModal" title="Mark Attendance" size="md" @close="showMarkModal = false">
      <form @submit.prevent="markAttendance" class="space-y-4">
        <div>
          <label class="label">Student *</label>
          <select v-model="markForm.student" class="input-field" required @change="syncStudentDefaults">
            <option value="">Select Student</option>
            <option v-for="student in students" :key="student.name" :value="student.student_id || student.name">
              {{ student.student_id || student.name }} - {{ student.full_name || student.student_id }}
            </option>
          </select>
        </div>
        <div>
          <label class="label">Course *</label>
          <select v-model="markForm.course" class="input-field" required>
            <option value="">Select Course</option>
            <option v-for="c in courses" :key="c.name" :value="c.name">{{ c.course_name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Hour *</label>
          <select v-model="markForm.attendance_hour" class="input-field" required>
            <option v-for="hour in 5" :key="hour" :value="hour">Hour {{ hour }}</option>
          </select>
        </div>
        <div>
          <label class="label">Date *</label>
          <input v-model="markForm.attendance_date" type="date" class="input-field" required />
        </div>
        <div>
          <label class="label">Status *</label>
          <select v-model="markForm.status" class="input-field" required>
            <option>Present</option>
            <option>Absent</option>
            <option>Late</option>
            <option>Excused</option>
          </select>
        </div>
        <div>
          <label class="label">Remarks</label>
          <textarea v-model="markForm.remarks" class="input-field" rows="2" />
        </div>
        <div class="flex items-center justify-end gap-3 pt-2">
          <button type="button" @click="showMarkModal = false" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary">
            <CheckCircle class="w-4 h-4" />
            Mark Attendance
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, X, CheckCircle } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import Modal from '@/components/ui/Modal.vue'
import { useApi } from '@/composables/useApi'

const { callApi } = useApi()
const students = ref([])
const attendance = ref([])
const courses = ref([])
const departments = ref([])
const batches = ref([])
const showMarkModal = ref(false)

const filters = ref({ date: '', student: '', department: '', batch: '', hour: '', status: '' })
const markForm = ref({
  student: '', course: '', attendance_date: new Date().toISOString().split('T')[0],
  attendance_hour: 1, status: 'Present', remarks: '',
  department: '', academic_year: '', batch: '', student_name: ''
})

const syncStudentDefaults = () => {
  const student = students.value.find((row) => (row.student_id || row.name) === markForm.value.student)
  if (!student) return
  markForm.value.student_name = student.full_name || student.student_id || student.name
  markForm.value.department = student.department || ''
  markForm.value.academic_year = student.academic_year || ''
  markForm.value.batch = student.batch || ''
}

const summary = computed(() => {
  const total = attendance.value.length
  const present = attendance.value.filter(a => a.status === 'Present').length
  const absent = attendance.value.filter(a => a.status === 'Absent').length
  const late = attendance.value.filter(a => a.status === 'Late').length
  return [
    { label: 'Total', value: total, bg: '', textColor: 'text-gray-800 dark:text-white', labelColor: 'text-gray-400' },
    { label: 'Present', value: present, bg: 'bg-green-50 dark:bg-green-900/10', textColor: 'text-green-600 dark:text-green-400', labelColor: 'text-green-500' },
    { label: 'Absent', value: absent, bg: 'bg-red-50 dark:bg-red-900/10', textColor: 'text-red-500 dark:text-red-400', labelColor: 'text-red-400' },
    { label: 'Late', value: late, bg: 'bg-yellow-50 dark:bg-yellow-900/10', textColor: 'text-yellow-600 dark:text-yellow-400', labelColor: 'text-yellow-500' },
  ]
})

const fetchAttendance = async () => {
  const params = {}
  if (filters.value.date) params.from_date = params.to_date = filters.value.date
  if (filters.value.student) params.student = filters.value.student
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.department) params.department = filters.value.department
  if (filters.value.batch) params.batch = filters.value.batch
  // ✅ FIX - AttendanceView.vue fetchAttendance()
  if (filters.value.hour) 
    params.attendance_hour = String(filters.value.hour)  // ← force string
  attendance.value = await callApi('sms.api.attendance.get_attendance', params)
}

let t = null
const debouncedFetch = () => { clearTimeout(t); t = setTimeout(fetchAttendance, 400) }

const clearFilters = () => {
  filters.value = { date: '', student: '', department: '', batch: '', hour: '', status: '' }
  fetchAttendance()
}

const markAttendance = async () => {
  // Ensure attendance_hour is a string before sending to backend
  const payload = { 
    ...markForm.value, 
    attendance_hour: String(markForm.value.attendance_hour) 
  }
  await callApi('sms.api.attendance.mark_attendance', {
    data: payload
  }, { method: 'POST' })
  showMarkModal.value = false
  fetchAttendance()
}
onMounted(async () => {
  fetchAttendance()
  courses.value = await callApi('sms.api.meta.get_course_options')
  departments.value = await callApi('sms.api.meta.get_departments')
  batches.value = await callApi('sms.api.meta.get_batches')
  students.value = await callApi('sms.api.meta.get_student_options')
})
</script>
