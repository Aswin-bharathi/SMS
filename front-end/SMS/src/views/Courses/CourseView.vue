<template>
  <div class="space-y-5">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Courses</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Maintain courses, credits, instructors, and semesters</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <Plus class="h-4 w-4" />
        Add Course
      </button>
    </div>

    <div class="card !p-4">
      <div class="flex flex-wrap gap-3">
        <div class="relative min-w-60 flex-1">
          <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input v-model="filters.search" class="input-field py-2 pl-9 text-sm" placeholder="Search courses..." @input="debouncedFetch" />
        </div>
        <select v-model="filters.is_active" class="input-field w-auto py-2 text-sm" @change="fetchCourses">
          <option value="">All</option>
          <option value="1">Active</option>
          <option value="0">Inactive</option>
        </select>
        <button class="btn-secondary text-sm" @click="clearFilters">
          <X class="h-4 w-4" />
          Clear
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      <div v-for="course in courses" :key="course.name" class="card group !p-5">
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-wide text-primary-500">{{ course.course_code }}</p>
            <h2 class="mt-1 truncate text-lg font-bold text-slate-900 dark:text-white">{{ course.course_name }}</h2>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ course.program || 'No program assigned' }}</p>
          </div>
          <Badge :variant="course.is_active ? 'Active' : 'Inactive'">{{ course.is_active ? 'Active' : 'Inactive' }}</Badge>
        </div>
        <div class="mt-5 grid grid-cols-3 gap-3 text-center">
          <div class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70">
            <p class="text-lg font-bold text-slate-900 dark:text-white">{{ course.credits || 0 }}</p>
            <p class="text-xs text-slate-400">Credits</p>
          </div>
          <div class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70">
            <p class="text-lg font-bold text-slate-900 dark:text-white">{{ course.semester || '-' }}</p>
            <p class="text-xs text-slate-400">Sem</p>
          </div>
          <div class="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/70">
            <BookOpen class="mx-auto h-5 w-5 text-cyan-500" />
            <p class="mt-1 text-xs text-slate-400">Course</p>
          </div>
        </div>
        <p class="mt-4 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">{{ course.description || 'No description added.' }}</p>
        <div class="mt-5 flex items-center justify-between border-t border-slate-100 pt-4 dark:border-slate-700">
          <p class="truncate text-sm text-slate-500 dark:text-slate-400">{{ course.instructor || 'No instructor' }}</p>
          <div class="flex items-center gap-1">
            <button class="icon-btn" @click="openEdit(course)"><Pencil class="h-4 w-4" /></button>
            <button class="icon-btn danger" @click="confirmDelete(course)"><Trash2 class="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && !courses.length" class="card py-14 text-center text-sm text-slate-400">No courses found.</div>

    <Modal :show="showModal" :title="editMode ? 'Edit Course' : 'Add Course'" size="lg" @close="closeModal">
      <form class="space-y-5" @submit.prevent="saveCourse">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="label">Course Name *</label>
            <input v-model="form.course_name" class="input-field" required placeholder="Data Structures" />
          </div>
          <div>
            <label class="label">Course Code *</label>
            <input v-model="form.course_code" class="input-field" required :disabled="editMode" placeholder="CS201" />
          </div>
          <div>
            <label class="label">Program</label>
            <select v-model="form.program" class="input-field" @change="syncProgramDefaults">
              <option value="">Select Program</option>
              <option v-for="program in programs" :key="program.name" :value="program.name">
                {{ program.program_code }} - {{ program.program_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Instructor</label>
            <input v-model="form.instructor" class="input-field" placeholder="Instructor name" />
          </div>
          <div>
            <label class="label">Department</label>
            <select v-model="form.department" class="input-field">
              <option value="">Select Department</option>
              <option v-for="department in departments" :key="department.name" :value="department.name">
                {{ department.department_code || department.department_name }} - {{ department.department_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Academic Year</label>
            <select v-model="form.academic_year" class="input-field">
              <option value="">Select Year</option>
              <option v-for="year in academicYears" :key="year.name" :value="year.name">
                {{ year.year_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Batch</label>
            <input v-model="form.batch" class="input-field" placeholder="2026-27" />
          </div>
          <div>
            <label class="label">Credits</label>
            <input v-model.number="form.credits" type="number" min="0" class="input-field" />
          </div>
          <div>
            <label class="label">Semester</label>
            <select v-model="form.semester" class="input-field">
              <option value="">Select Semester</option>
              <option v-for="sem in 8" :key="sem" :value="sem">{{ sem }}</option>
            </select>
          </div>
          <label class="flex items-center gap-3 rounded-xl border border-slate-200 p-3 dark:border-slate-700">
            <input v-model="form.is_active" type="checkbox" true-value="1" false-value="0" />
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Active course</span>
          </label>
          <div class="sm:col-span-2">
            <label class="label">Description</label>
            <textarea v-model="form.description" class="input-field" rows="3" />
          </div>
        </div>
        <div class="flex justify-end gap-3">
          <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="saving">
            <Save class="h-4 w-4" />
            {{ saving ? 'Saving...' : 'Save Course' }}
          </button>
        </div>
      </form>
    </Modal>

    <Modal :show="showDelete" title="Delete Course" size="sm" @close="showDelete = false">
      <p class="text-sm text-slate-500 dark:text-slate-400">Delete course <strong>{{ selected?.course_name }}</strong>?</p>
      <template #footer>
        <button class="btn-secondary" @click="showDelete = false">Cancel</button>
        <button class="btn-danger" @click="deleteCourse"><Trash2 class="h-4 w-4" /> Delete</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { BookOpen, Pencil, Plus, Save, Search, Trash2, X } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import Modal from '@/components/ui/Modal.vue'
import { useApi } from '@/composables/useApi'

const { callApi } = useApi()
const programs = ref([])
const departments = ref([])
const academicYears = ref([])
const courses = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showDelete = ref(false)
const editMode = ref(false)
const selected = ref(null)
const filters = ref({ search: '', is_active: '' })
const form = ref({})
const defaultForm = { course_name: '', course_code: '', program: '', department: '', academic_year: '', batch: '', credits: 3, instructor: '', semester: '', is_active: 1, description: '' }

const syncProgramDefaults = () => {
  const program = programs.value.find((item) => item.name === form.value.program)
  if (!program) return
  form.value.department = program.department || form.value.department
}

const fetchCourses = async () => {
  loading.value = true
  try {
    courses.value = await callApi('sms.api.course.get_courses', {
      search: filters.value.search || undefined,
      is_active: filters.value.is_active,
    })
  } finally {
    loading.value = false
  }
}

let timer = null
const debouncedFetch = () => { clearTimeout(timer); timer = setTimeout(fetchCourses, 350) }
const clearFilters = () => { filters.value = { search: '', is_active: '' }; fetchCourses() }
const openCreate = () => { form.value = { ...defaultForm }; editMode.value = false; showModal.value = true }
const openEdit = (course) => {
  selected.value = course
  form.value = { ...defaultForm, ...course }
  syncProgramDefaults()
  editMode.value = true
  showModal.value = true
}
const closeModal = () => { showModal.value = false; selected.value = null }
const confirmDelete = (course) => { selected.value = course; showDelete.value = true }

const saveCourse = async () => {
  saving.value = true
  try {
    if (editMode.value) {
      await callApi('sms.api.course.update_course', { course_name: selected.value.name, data: form.value }, { method: 'POST' })
    } else {
      await callApi('sms.api.course.create_course', { data: form.value }, { method: 'POST' })
    }
    closeModal()
    fetchCourses()
  } finally {
    saving.value = false
  }
}

const deleteCourse = async () => {
  await callApi('sms.api.course.delete_course', { course_name: selected.value.name }, { method: 'POST' })
  showDelete.value = false
  fetchCourses()
}

onMounted(fetchCourses)

onMounted(async () => {
  programs.value = await callApi('sms.api.meta.get_programs')
  departments.value = await callApi('sms.api.meta.get_departments')
  academicYears.value = await callApi('sms.api.meta.get_academic_years')
  syncProgramDefaults()
})
</script>
