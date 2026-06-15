<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Personal Info -->
    <div>
      <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        Personal Information
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="label">Roll Number</label>
          <input v-model="form.student_id" :disabled="editMode" class="input-field" placeholder="Auto generated" />
        </div>
        <div>
          <label class="label">Gender *</label>
          <select v-model="form.gender" class="input-field" required>
            <option value="">Select Gender</option>
            <option>Male</option>
            <option>Female</option>
            <option>Other</option>
          </select>
        </div>
        <div>
          <label class="label">First Name *</label>
          <input v-model="form.first_name" class="input-field" required placeholder="John" />
        </div>
        <div>
          <label class="label">Last Name *</label>
          <input v-model="form.last_name" class="input-field" required placeholder="Doe" />
        </div>
        <div>
          <label class="label">Date of Birth *</label>
          <input v-model="form.date_of_birth" type="date" class="input-field" required />
        </div>
        <div>
          <label class="label">Blood Group</label>
          <select v-model="form.blood_group" class="input-field">
            <option value="">Select Blood Group</option>
            <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Contact Info -->
    <div>
      <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        Contact Information
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="label">Email</label>
          <input v-model="form.email" type="email" class="input-field" placeholder="john@example.com" />
        </div>
        <div>
          <label class="label">Phone</label>
          <input v-model="form.phone" class="input-field" placeholder="+91 9999999999" />
        </div>
        <div class="sm:col-span-2">
          <label class="label">Address</label>
          <textarea v-model="form.address" class="input-field" rows="2" placeholder="Full address..." />
        </div>
      </div>
    </div>

    <!-- Academic Info -->
    <div>
      <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        Academic Information
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="label">Program Level *</label>
          <select v-model="form.program_level" class="input-field" required>
            <option>UG</option>
            <option>PG</option>
          </select>
        </div>
        <div>
          <label class="label">Program *</label>
          <select v-model="form.program" class="input-field" required @change="syncDepartmentFromProgram">
            <option value="">Select Program</option>
            <option v-for="p in programs" :key="p.name" :value="p.name">{{ p.program_name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Department *</label>
          <select v-model="form.department" class="input-field" required>
            <option value="">Select Department</option>
            <option v-for="d in departments" :key="d.name" :value="d.name">{{ d.department_name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Academic Year</label>
          <select v-model="form.academic_year" class="input-field" @change="syncBatchFromYear">
            <option value="">Select Year</option>
            <option v-for="y in academicYears" :key="y.name" :value="y.name">{{ y.year_name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Batch</label>
          <input v-model="form.batch" class="input-field" placeholder="2026-27" />
        </div>
        <div>
          <label class="label">Current Semester</label>
          <select v-model="form.current_semester" class="input-field">
            <option value="">Select Semester</option>
            <option v-for="s in 8" :key="s" :value="s">Semester {{ s }}</option>
          </select>
        </div>
        <div>
          <label class="label">Status</label>
          <select v-model="form.status" class="input-field">
            <option>Active</option>
            <option>Inactive</option>
            <option>Graduated</option>
            <option>Dropped</option>
          </select>
        </div>
        <div>
          <label class="label">Enrollment Date</label>
          <input v-model="form.enrollment_date" type="date" class="input-field" />
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20
                             border border-red-200 dark:border-red-800 rounded-xl text-red-600
                             dark:text-red-400 text-sm">
      <AlertCircle class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Form Actions -->
    <div class="flex items-center justify-end gap-3 pt-2">
      <button type="button" @click="$emit('cancel')" class="btn-secondary">Cancel</button>
      <button type="submit" :disabled="saving" class="btn-primary">
        <Save class="w-4 h-4" />
        {{ saving ? 'Saving...' : (editMode ? 'Update Student' : 'Create Student') }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Save, AlertCircle } from 'lucide-vue-next'
import { useStudentStore } from '@/stores/student'
import { useApi } from '@/composables/useApi'

const props = defineProps({
  initialData: Object,
  editMode: Boolean
})
const emit = defineEmits(['saved', 'cancel'])

const studentStore = useStudentStore()
const { callApi } = useApi()

const saving = ref(false)
const error = ref('')
const programs = ref([])
const departments = ref([])
const academicYears = ref([])

const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']

const defaultForm = {
  student_id: '', first_name: '', last_name: '',
  date_of_birth: '', gender: '', blood_group: '',
  email: '', phone: '', address: '',
  program_level: 'UG', program: '', department: '',
  academic_year: '', batch: '',
  current_semester: '', enrollment_date: '',
  status: 'Active'
}

const form = ref({ ...defaultForm })

watch(() => props.initialData, (val) => {
  if (val) form.value = { ...defaultForm, ...val, student_id: val.student_id || val.name }
  else form.value = { ...defaultForm }
}, { immediate: true })

watch(
  () => [form.value.program, form.value.academic_year, programs.value.length, academicYears.value.length],
  () => {
    syncDepartmentFromProgram()
    syncBatchFromYear()
  }
)

const handleSubmit = async () => {
  saving.value = true
  error.value = ''
  try {
    if (props.editMode) {
      await studentStore.updateStudent(form.value.student_id, form.value)
    } else {
      await studentStore.createStudent(form.value)
    }
    emit('saved')
  } catch (err) {
    error.value = err || 'Failed to save student.'
  } finally {
    saving.value = false
  }
}

const syncDepartmentFromProgram = () => {
  const program = programs.value.find((p) => p.name === form.value.program)
  if (program?.department) form.value.department = program.department
}

const syncBatchFromYear = () => {
  if (!form.value.batch && form.value.academic_year) {
    form.value.batch = form.value.academic_year
  }
}

onMounted(async () => {
  programs.value = await callApi('sms.api.meta.get_programs')
  departments.value = await callApi('sms.api.meta.get_departments')
  academicYears.value = await callApi('sms.api.meta.get_academic_years')
  syncDepartmentFromProgram()
  syncBatchFromYear()
})
</script>
