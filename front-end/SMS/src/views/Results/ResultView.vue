<template>
  <div class="space-y-5">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Results</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Record exams, marks, grades, and student outcomes</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="h-4 w-4" />
        Add Result
      </button>
    </div>

    <div class="card !p-4">
      <div class="flex flex-wrap gap-3">
        <input v-model="filters.student" class="input-field w-56 py-2 text-sm" placeholder="Student ID..." @input="debouncedFetch" />
        <select v-model="filters.exam_type" class="input-field w-auto py-2 text-sm" @change="fetchResults">
          <option value="">All Exams</option>
          <option>Midterm</option>
          <option>Final</option>
          <option>Quiz</option>
          <option>Assignment</option>
          <option>Practical</option>
        </select>
        <button class="btn-secondary text-sm" @click="clearFilters">
          <X class="h-4 w-4" />
          Clear
        </button>
      </div>
    </div>

    <div class="card !p-0 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 dark:border-slate-700">
              <th v-for="col in ['Student', 'Exam', 'Semester', 'Date', 'Percentage', 'Grade', 'Status', 'Actions']" :key="col" class="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
            <tr v-for="result in results" :key="result.name" class="hover:bg-slate-50 dark:hover:bg-slate-800/60">
              <td class="px-5 py-4">
                <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ result.student_name || result.student }}</p>
                <p class="text-xs text-slate-400">{{ result.student }}</p>
              </td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ result.exam_type }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ result.semester || '-' }}</td>
              <td class="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{{ result.result_date || '-' }}</td>
              <td class="px-5 py-4 text-sm font-semibold text-primary-600 dark:text-primary-300">{{ Number(result.overall_percentage || 0).toFixed(1) }}%</td>
              <td class="px-5 py-4 text-sm font-bold text-slate-900 dark:text-white">{{ result.overall_grade || '-' }}</td>
              <td class="px-5 py-4"><Badge :variant="result.result_status">{{ result.result_status }}</Badge></td>
              <td class="px-5 py-4">
                <div class="flex items-center gap-1">
                  <button class="icon-btn" @click="openEdit(result)"><Pencil class="h-4 w-4" /></button>
                  <button class="icon-btn danger" @click="confirmDelete(result)"><Trash2 class="h-4 w-4" /></button>
                </div>
              </td>
            </tr>
            <tr v-if="!loading && !results.length">
              <td colspan="8" class="px-5 py-14 text-center text-sm text-slate-400">No result records found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal :show="showModal" :title="editMode ? 'Edit Result' : 'Add Result'" size="xl" @close="closeModal">
      <form class="space-y-5" @submit.prevent="saveResult">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label class="label">Student *</label>
            <select v-model="form.student" class="input-field" required @change="syncStudentDefaults">
              <option value="">Select Student</option>
              <option v-for="student in students" :key="student.name" :value="student.student_id || student.name">
                {{ student.student_id || student.name }} - {{ student.full_name || student.student_id }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Academic Year</label>
            <input v-model="form.academic_year" class="input-field" placeholder="2026-27" />
          </div>
          <div>
            <label class="label">Exam Type *</label>
            <select v-model="form.exam_type" class="input-field" required>
              <option>Midterm</option>
              <option>Final</option>
              <option>Quiz</option>
              <option>Assignment</option>
              <option>Practical</option>
            </select>
          </div>
          <div>
            <label class="label">Result Date</label>
            <input v-model="form.result_date" type="date" class="input-field" />
          </div>
          <div>
            <label class="label">Semester</label>
            <select v-model="form.semester" class="input-field">
              <option value="">Select Semester</option>
              <option v-for="sem in 8" :key="sem" :value="sem">{{ sem }}</option>
            </select>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 dark:border-slate-700">
          <div class="flex items-center justify-between border-b border-slate-200 p-4 dark:border-slate-700">
            <h2 class="font-bold text-slate-900 dark:text-white">Course Marks</h2>
            <button type="button" class="btn-secondary px-3 py-1.5 text-sm" @click="addRow">
              <Plus class="h-4 w-4" />
              Add Row
            </button>
          </div>
          <div class="space-y-3 p-4">
            <div v-for="(row, index) in form.results" :key="index" class="grid grid-cols-1 gap-3 rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70 sm:grid-cols-4">
              <select v-model="row.course" class="input-field py-2 text-sm" required @change="syncCourseDefaults(row)">
                <option value="">Select Course</option>
                <option v-for="course in courses" :key="course.name" :value="course.name">
                  {{ course.course_code }} - {{ course.course_name }}
                </option>
              </select>
              <input v-model.number="row.max_marks" type="number" min="1" class="input-field py-2 text-sm" placeholder="Max marks" />
              <input v-model.number="row.marks_obtained" type="number" min="0" class="input-field py-2 text-sm" required placeholder="Marks obtained" />
              <button type="button" class="btn-secondary px-3 py-2 text-sm" @click="removeRow(index)">
                <Trash2 class="h-4 w-4" />
                Remove
              </button>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving...' : 'Save Result' }}
          </button>
        </div>
      </form>
    </Modal>

    <Modal :show="showDelete" title="Delete Result" size="sm" @close="showDelete = false">
      <p class="text-sm text-slate-500 dark:text-slate-400">Delete result <strong>{{ selected?.name }}</strong>?</p>
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancel</button>
        <button class="btn-danger" @click="deleteResult"><Trash2 class="h-4 w-4" /> Delete</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Pencil, Plus, Save, Trash2, X } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import Modal from '@/components/ui/Modal.vue'
import { useApi } from '@/composables/useApi'

const { callApi } = useApi()
const students = ref([])
const courses = ref([])
const results = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showDelete = ref(false)
const editMode = ref(false)
const selected = ref(null)
const filters = ref({ student: '', exam_type: '' })
const form = ref({})
const today = new Date().toISOString().split('T')[0]
const defaultForm = {
  student: '', academic_year: '', exam_type: 'Midterm', semester: '',
  result_date: today, results: [{ course: '', max_marks: 100, marks_obtained: 0 }]
}

const syncStudentDefaults = () => {
  const student = students.value.find((row) => (row.student_id || row.name) === form.value.student)
  if (!student) return
  form.value.academic_year = student.academic_year || form.value.academic_year
}

const syncCourseDefaults = (row) => {
  const course = courses.value.find((item) => item.name === row.course)
  if (!course) return
  row.course_name = course.course_name
}

const fetchResults = async () => {
  loading.value = true
  try {
    results.value = await callApi('sms.api.result.get_results', {
      student: filters.value.student || undefined,
      exam_type: filters.value.exam_type || undefined,
    })
  } finally {
    loading.value = false
  }
}

let timer = null
const debouncedFetch = () => { clearTimeout(timer); timer = setTimeout(fetchResults, 350) }
const clearFilters = () => { filters.value = { student: '', exam_type: '' }; fetchResults() }
const openCreate = () => { form.value = { ...defaultForm, results: [{ course: '', max_marks: 100, marks_obtained: 0 }] }; editMode.value = false; showModal.value = true }
const openEdit = async (result) => {
  selected.value = result
  const detail = await callApi('sms.api.result.get_result_detail', { result_name: result.name })
  
  // Clean the results child table rows to remove Frappe internal names
  const cleanResults = (detail.results || []).map(row => ({
    course: row.course,
    max_marks: row.max_marks,
    marks_obtained: row.marks_obtained
  }))

  form.value = { 
    ...defaultForm, 
    ...detail, 
    results: cleanResults.length ? cleanResults : [{ course: '', max_marks: 100, marks_obtained: 0 }] 
  }
  syncStudentDefaults()
  form.value.results.forEach(syncCourseDefaults)
  editMode.value = true
  showModal.value = true
}
const closeModal = () => { showModal.value = false; selected.value = null }
const confirmDelete = (result) => { selected.value = result; showDelete.value = true }
const addRow = () => form.value.results.push({ course: '', max_marks: 100, marks_obtained: 0 })
const removeRow = (index) => {
  if (form.value.results.length === 1) return
  form.value.results.splice(index, 1)
}

const saveResult = async () => {
  saving.value = true
  try {
    if (editMode.value) {
      await callApi('sms.api.result.update_result', { result_name: selected.value.name, data: form.value }, { method: 'POST' })
    } else {
      await callApi('sms.api.result.create_result', { data: form.value }, { method: 'POST' })
    }
    closeModal()
    fetchResults()
  } finally {
    saving.value = false
  }
}

const deleteResult = async () => {
  await callApi('sms.api.result.delete_result', { result_name: selected.value.name }, { method: 'POST' })
  showDelete.value = false
  fetchResults()
}

onMounted(fetchResults)

onMounted(async () => {
  students.value = await callApi('sms.api.meta.get_student_options')
  courses.value = await callApi('sms.api.meta.get_course_options')
  syncStudentDefaults()
})
</script>
