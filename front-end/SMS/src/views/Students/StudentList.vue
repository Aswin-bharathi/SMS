<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white">Students</h1>
        <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">
          {{ studentStore.total }} total students enrolled
        </p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="exportData" class="btn-secondary text-sm">
          <Download class="w-4 h-4" />
          Export
        </button>
        <button @click="showModal = true" class="btn-primary text-sm">
          <Plus class="w-4 h-4" />
          Add Student
        </button>
      </div>
    </div>

    <!-- Filters Card -->
    <div class="card !p-4">
      <div class="flex flex-wrap items-center gap-3">
        <!-- Search -->
        <div class="relative flex-1 min-w-60">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            placeholder="Search students..."
            class="input-field pl-9 py-2 text-sm"
          />
        </div>

        <!-- Status Filter -->
        <select v-model="filters.status" @change="fetchStudents" class="input-field w-auto py-2 text-sm">
          <option value="">All Status</option>
          <option>Active</option>
          <option>Inactive</option>
          <option>Graduated</option>
          <option>Dropped</option>
        </select>

        <!-- Program Filter -->
        <select v-model="filters.program" @change="fetchStudents" class="input-field w-auto py-2 text-sm">
          <option value="">All Programs</option>
          <option v-for="p in programs" :key="p.name" :value="p.name">{{ p.program_name }}</option>
        </select>

        <select v-model="filters.department" @change="fetchStudents" class="input-field w-auto py-2 text-sm">
          <option value="">All Departments</option>
          <option v-for="d in departments" :key="d.name" :value="d.name">{{ d.department_name }}</option>
        </select>

        <select v-model="filters.batch" @change="fetchStudents" class="input-field w-auto py-2 text-sm">
          <option value="">All Batches</option>
          <option v-for="b in batches" :key="b.name" :value="b.name">{{ b.batch }}</option>
        </select>

        <select v-model="filters.academic_year" @change="fetchStudents" class="input-field w-auto py-2 text-sm">
          <option value="">All Years</option>
          <option v-for="y in academicYears" :key="y.name" :value="y.name">{{ y.year_name }}</option>
        </select>

        <!-- View Toggle -->
        <div class="flex items-center bg-gray-100 dark:bg-gray-700 rounded-xl p-1">
          <button
            v-for="v in ['list', 'grid']"
            :key="v"
            @click="viewMode = v"
            :class="[
              'w-8 h-8 flex items-center justify-center rounded-lg transition-all',
              viewMode === v
                ? 'bg-white dark:bg-gray-600 shadow-sm text-primary-600 dark:text-primary-400'
                : 'text-gray-400 dark:text-gray-500 hover:text-gray-600'
            ]"
          >
            <component :is="v === 'list' ? List : LayoutGrid" class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="studentStore.loading" class="flex items-center justify-center h-64">
      <div class="text-center space-y-3">
        <div class="w-12 h-12 border-4 border-primary-600 border-t-transparent
                    rounded-full animate-spin mx-auto" />
        <p class="text-gray-400 dark:text-gray-500 text-sm">Loading students...</p>
      </div>
    </div>

    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="student in studentStore.students"
        :key="student.name"
        class="card !p-5 cursor-pointer hover:shadow-md hover:-translate-y-0.5
               transition-all duration-200 group"
        @click="$router.push(`/students/${getStudentId(student)}`)"
      >
        <!-- Avatar + Status -->
        <div class="flex items-start justify-between mb-4">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-400 to-cyan-500
                      flex items-center justify-center text-white font-bold text-xl shadow-sm">
            {{ getStudentName(student).charAt(0) }}
          </div>
          <Badge :variant="student.status">{{ student.status }}</Badge>
        </div>

        <!-- Info -->
        <h3 class="font-bold text-gray-800 dark:text-white group-hover:text-primary-600
                   dark:group-hover:text-primary-400 transition-colors">
          {{ getStudentName(student) }}
        </h3>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5 mb-3">
          {{ getStudentId(student) }}
        </p>

        <div class="space-y-1.5">
          <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <BookOpen class="w-3.5 h-3.5" />
            <span class="truncate">{{ student.department || student.program }}</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <Mail class="w-3.5 h-3.5" />
            <span class="truncate">{{ student.email || 'No email' }}</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700
                    flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            @click.stop="editStudent(student)"
            class="flex-1 py-1.5 text-xs text-center rounded-lg
                   bg-primary-50 dark:bg-primary-900/20 text-primary-600
                   dark:text-primary-400 hover:bg-primary-100 transition-colors font-medium"
          >
            Edit
          </button>
          <button
            @click.stop="confirmDelete(student)"
            class="flex-1 py-1.5 text-xs text-center rounded-lg
                   bg-red-50 dark:bg-red-900/20 text-red-500
                   dark:text-red-400 hover:bg-red-100 transition-colors font-medium"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- List View / Table -->
    <div v-else class="card !p-0 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-700">
              <th
                v-for="col in columns"
                :key="col.key"
                class="px-5 py-4 text-left text-xs font-semibold text-gray-500
                       dark:text-gray-400 uppercase tracking-wider"
              >
                {{ col.label }}
              </th>
              <th class="px-5 py-4 text-right text-xs font-semibold text-gray-500
                         dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50 dark:divide-gray-700/50">
            <tr
              v-for="student in studentStore.students"
              :key="student.name"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/30 cursor-pointer transition-colors group"
              @click="$router.push(`/students/${getStudentId(student)}`)"
            >
              <!-- Student Info -->
              <td class="px-5 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-400 to-cyan-500
                              flex items-center justify-center text-white font-bold text-sm shrink-0">
                    {{ getStudentName(student).charAt(0) }}
                  </div>
                  <div>
                    <p class="font-semibold text-gray-800 dark:text-white text-sm">
                      {{ getStudentName(student) }}
                    </p>
                    <p class="text-xs text-gray-400 dark:text-gray-500">{{ getStudentId(student) }}</p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">
                {{ student.email }}
              </td>
              <td class="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">
                {{ student.department || '—' }}
              </td>
              <td class="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">
                {{ student.batch || '—' }}
              </td>
              <td class="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">
                {{ student.gender }}
              </td>
              <td class="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">
                Sem {{ student.current_semester || '—' }}
              </td>
              <td class="px-5 py-4">
                <Badge :variant="student.status">{{ student.status }}</Badge>
              </td>
              <td class="px-5 py-4 text-right">
                <div class="flex items-center justify-end gap-1
                            opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    @click.stop="editStudent(student)"
                    class="w-8 h-8 flex items-center justify-center rounded-lg
                           hover:bg-primary-50 dark:hover:bg-primary-900/20
                           text-gray-400 hover:text-primary-600 transition-colors"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button
                    @click.stop="confirmDelete(student)"
                    class="w-8 h-8 flex items-center justify-center rounded-lg
                           hover:bg-red-50 dark:hover:bg-red-900/20
                           text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex items-center justify-between px-5 py-4 border-t border-gray-100 dark:border-gray-700">
        <p class="text-sm text-gray-400 dark:text-gray-500">
          Showing {{ ((currentPage - 1) * pageSize) + 1 }}–{{ Math.min(currentPage * pageSize, studentStore.total) }}
          of {{ studentStore.total }} students
        </p>
        <div class="flex items-center gap-1">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="w-8 h-8 flex items-center justify-center rounded-lg
                   text-gray-400 hover:text-gray-600 hover:bg-gray-100
                   dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>

          <button
            v-for="page in visiblePages"
            :key="page"
            @click="changePage(page)"
            :class="[
              'w-8 h-8 flex items-center justify-center rounded-lg text-sm font-medium',
              page === currentPage
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
            ]"
          >
            {{ page }}
          </button>

          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="w-8 h-8 flex items-center justify-center rounded-lg
                   text-gray-400 hover:text-gray-600 hover:bg-gray-100
                   dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Student Modal -->
    <Modal
      :show="showModal"
      :title="editMode ? 'Edit Student' : 'Add New Student'"
      size="lg"
      @close="closeModal"
    >
      <StudentForm
        :initial-data="selectedStudent"
        :edit-mode="editMode"
        @saved="onStudentSaved"
        @cancel="closeModal"
      />
    </Modal>

    <!-- Delete Confirmation Modal -->
    <Modal :show="showDeleteModal" title="Delete Student" size="sm" @close="showDeleteModal = false">
      <div class="text-center py-4">
        <div class="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full
                    flex items-center justify-center mx-auto mb-4">
          <Trash2 class="w-8 h-8 text-red-500" />
        </div>
        <h3 class="font-bold text-gray-800 dark:text-white mb-2">Are you sure?</h3>
        <p class="text-gray-500 dark:text-gray-400 text-sm">
          This will permanently delete <strong>{{ selectedStudent?.full_name }}</strong>.
          This action cannot be undone.
        </p>
      </div>

      <template #footer>
        <button @click="showDeleteModal = false" class="btn-secondary">Cancel</button>
        <button @click="deleteStudent" :disabled="deleting" class="btn-danger">
          <Trash2 class="w-4 h-4" />
          {{ deleting ? 'Deleting...' : 'Delete' }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Plus, Search, Download, List, LayoutGrid, Pencil, Trash2,
  ChevronLeft, ChevronRight, BookOpen, Mail
} from 'lucide-vue-next'
import { useStudentStore } from '@/stores/student'
import { useApi } from '@/composables/useApi'
import Badge from '@/components/ui/Badge.vue'
import Modal from '@/components/ui/Modal.vue'
import StudentForm from './StudentForm.vue'

const studentStore = useStudentStore()
const { callApi } = useApi()
const route = useRoute()
const router = useRouter()

const viewMode = ref('list')
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const filters = ref({ status: '', program: '', department: '', batch: '', academic_year: '' })
const programs = ref([])
const departments = ref([])
const batches = ref([])
const academicYears = ref([])
const showModal = ref(false)
const showDeleteModal = ref(false)
const editMode = ref(false)
const selectedStudent = ref(null)
const deleting = ref(false)

const totalPages = computed(() => Math.ceil(studentStore.total / pageSize.value))
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const columns = [
  { key: 'full_name', label: 'Student' },
  { key: 'email', label: 'Email' },
  { key: 'department', label: 'Department' },
  { key: 'batch', label: 'Batch' },
  { key: 'gender', label: 'Gender' },
  { key: 'current_semester', label: 'Semester' },
  { key: 'status', label: 'Status' },
]

const getStudentId = (student) => student.student_id || student.name
const getStudentName = (student) => {
  if (student.full_name) return student.full_name
  if (student.student_name) return student.student_name
  return [student.first_name, student.last_name].filter(Boolean).join(' ') || student.name || 'Student'
}

const fetchStudents = async () => {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value,
    search: searchQuery.value || undefined,
    program: filters.value.program || undefined,
    status: filters.value.status || undefined,
    department: filters.value.department || undefined,
    batch: filters.value.batch || undefined,
    academic_year: filters.value.academic_year || undefined,
  }
  await studentStore.fetchStudents(params)
}

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchStudents()
  }, 400)
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchStudents()
}

const editStudent = (student) => {
  selectedStudent.value = { ...student }
  editMode.value = true
  showModal.value = true
}

const confirmDelete = (student) => {
  selectedStudent.value = student
  showDeleteModal.value = true
}

const deleteStudent = async () => {
  deleting.value = true
  try {
    await studentStore.deleteStudent(getStudentId(selectedStudent.value))
    showDeleteModal.value = false
    fetchStudents()
  } finally {
    deleting.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  editMode.value = false
  selectedStudent.value = null
  if (route.query.add) router.replace({ path: '/students', query: { ...route.query, add: undefined } })
}

const onStudentSaved = () => {
  closeModal()
  if (route.query.add) router.replace({ path: '/students', query: { ...route.query, add: undefined } })
  fetchStudents()
}

const exportData = () => {
  // Download as CSV
  const headers = ['Student ID', 'Full Name', 'Email', 'Program', 'Status']
  const rows = studentStore.students.map(s =>
    [getStudentId(s), getStudentName(s), s.email, s.program, s.status]
  )
  const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'students.csv'
  a.click()
}

onMounted(async () => {
  if (route.query.search) searchQuery.value = String(route.query.search)
  if (route.query.add === '1') showModal.value = true
  fetchStudents()
  programs.value = await callApi('sms.api.meta.get_programs')
  departments.value = await callApi('sms.api.meta.get_departments')
  batches.value = await callApi('sms.api.meta.get_batches')
  academicYears.value = await callApi('sms.api.meta.get_academic_years')
})

watch(() => route.query, (query) => {
  if (query.search && query.search !== searchQuery.value) {
    searchQuery.value = String(query.search)
    currentPage.value = 1
    fetchStudents()
  }
  if (query.add === '1') showModal.value = true
})
</script>
