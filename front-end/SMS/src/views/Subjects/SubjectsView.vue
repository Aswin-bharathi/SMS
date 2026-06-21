<template>
  <div class="space-y-5">
    <!-- ─── Header ──────────────────────────────────────────────── -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">
          Subjects
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Manage curriculum and faculty assignments
        </p>
      </div>
      <button
        class="inline-flex items-center gap-2 rounded-xl
               bg-gradient-to-r from-primary-500 to-cyan-500
               px-5 py-2.5 text-sm font-semibold text-white
               shadow-lg shadow-primary-500/30 hover:shadow-xl transition-all"
        @click="openCreateModal"
      >
        <Plus class="h-4 w-4" />
        Add Subject
      </button>
    </div>

    <!-- ─── Filters ─────────────────────────────────────────────── -->
    <div class="rounded-xl bg-white dark:bg-slate-800 p-4 ring-1 ring-slate-200 dark:ring-slate-700">
      <div class="flex flex-wrap items-center gap-3">
        <!-- Search -->
        <div class="relative flex-1 min-w-[200px]">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            v-model="searchQ"
            type="text"
            placeholder="Search by code or name…"
            class="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700
                   bg-white dark:bg-slate-900 text-sm
                   text-slate-900 dark:text-white
                   focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <!-- Department -->
        <select
          v-model="filterDept"
          class="rounded-lg border border-slate-200 dark:border-slate-700
                 bg-white dark:bg-slate-900 px-3 py-2 text-sm
                 text-slate-900 dark:text-white
                 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">All Departments</option>
          <option v-for="d in departments" :key="d.name" :value="d.name">
            {{ d.name }}
          </option>
        </select>

        <!-- Year -->
        <select
          v-model="filterYear"
          class="rounded-lg border border-slate-200 dark:border-slate-700
                 bg-white dark:bg-slate-900 px-3 py-2 text-sm
                 text-slate-900 dark:text-white
                 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">All Years</option>
          <option v-for="y in yearLevels" :key="y" :value="y">{{ y }}</option>
        </select>

        <!-- Lab only -->
        <label class="flex items-center gap-2 cursor-pointer px-2">
          <input
            v-model="filterLabOnly"
            type="checkbox"
            class="h-4 w-4 rounded border-slate-300 text-primary-500 focus:ring-primary-500"
          />
          <span class="text-sm text-slate-700 dark:text-slate-200">Labs only</span>
        </label>

        <!-- Count -->
        <span class="ml-auto inline-flex items-center gap-1 rounded-full
                     bg-slate-100 dark:bg-slate-700 px-3 py-1 text-xs font-semibold
                     text-slate-700 dark:text-slate-300">
          {{ filteredSubjects.length }}
          {{ filteredSubjects.length === 1 ? 'subject' : 'subjects' }}
        </span>
      </div>
    </div>

    <!-- ─── Loading ─────────────────────────────────────────────── -->
    <div
      v-if="loading"
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <div
        v-for="i in 6" :key="i"
        class="h-64 rounded-xl bg-white dark:bg-slate-800 animate-pulse
               ring-1 ring-slate-200 dark:ring-slate-700"
      />
    </div>

    <!-- ─── Grid ────────────────────────────────────────────────── -->
    <div
      v-else-if="filteredSubjects.length"
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <SubjectCard
        v-for="s in filteredSubjects"
        :key="s.name"
        :subject="s"
        @edit="openEditModal"
        @manage-faculty="openFacultyModal"
      />
    </div>

    <!-- ─── Empty state ─────────────────────────────────────────── -->
    <div
      v-else
      class="rounded-xl bg-white dark:bg-slate-800 p-12 text-center
             shadow-sm ring-1 ring-slate-200 dark:ring-slate-700"
    >
      <BookMarked class="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
      <h3 class="text-base font-semibold text-slate-700 dark:text-slate-300">
        No subjects found
      </h3>
      <p class="text-sm text-slate-400 mt-1">
        {{ subjects.length
            ? 'Try adjusting your filters.'
            : 'Get started by adding your first subject.' }}
      </p>
    </div>

    <!-- ─── Form modal ──────────────────────────────────────────── -->
    <SubjectFormModal
      :show="showFormModal"
      :subject="editingSubject"
      :departments="departments"
      :saving="saving"
      @close="closeFormModal"
      @save="handleSave"
      @delete="handleDelete"
    />

    <!-- ─── Faculty modal ───────────────────────────────────────── -->
    <FacultyAssignModal
      :show="showFacultyModal"
      :subject="facultySubject"
      :current-mappings="facultyMappings"
      :busy="facultyBusy"
      @close="closeFacultyModal"
      @add="handleAddFaculty"
      @remove="handleRemoveFaculty"
      @set-primary="handleSetPrimary"
    />

    <!-- ─── Toast ───────────────────────────────────────────────── -->
    <transition name="toast">
      <div
        v-if="toast.show"
        :class="[
          'fixed bottom-6 right-6 z-[60] flex items-center gap-3',
          'rounded-xl px-4 py-3 shadow-2xl ring-1',
          toast.type === 'success'
            ? 'bg-emerald-50 ring-emerald-200 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300 dark:ring-emerald-700'
            : 'bg-red-50 ring-red-200 text-red-800 dark:bg-red-500/20 dark:text-red-300 dark:ring-red-700',
        ]"
      >
        <CheckCircle v-if="toast.type === 'success'" class="h-5 w-5 shrink-0" />
        <AlertCircle v-else class="h-5 w-5 shrink-0" />
        <span class="text-sm font-medium">{{ toast.message }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  AlertCircle, BookMarked, CheckCircle, Plus, Search,
} from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'
import SubjectCard         from '@/components/subjects/SubjectCard.vue'
import SubjectFormModal    from '@/components/subjects/SubjectFormModal.vue'
import FacultyAssignModal  from '@/components/subjects/FacultyAssignModal.vue'

const { callApi } = useApi()

// ─── State ─────────────────────────────────────────────────────────────────
const subjects    = ref([])
const departments = ref([])
const loading     = ref(false)
const saving      = ref(false)

const searchQ        = ref('')
const filterDept     = ref('')
const filterYear     = ref('')
const filterLabOnly  = ref(false)

const showFormModal  = ref(false)
const editingSubject = ref(null)

const showFacultyModal = ref(false)
const facultySubject   = ref(null)
const facultyMappings  = ref([])
const facultyBusy      = ref(false)

const toast = ref({ show: false, type: 'success', message: '' })

const yearLevels = ['I UG', 'II UG', 'III UG', 'IV UG', 'I PG', 'II PG']

// ─── Computed ──────────────────────────────────────────────────────────────
const filteredSubjects = computed(() => {
  let list = subjects.value
  if (filterDept.value)    list = list.filter(s => s.department === filterDept.value)
  if (filterYear.value)    list = list.filter(s => s.year_level === filterYear.value)
  if (filterLabOnly.value) list = list.filter(s => s.is_lab)
  if (searchQ.value) {
    const q = searchQ.value.toLowerCase()
    list = list.filter(s =>
      s.subject_code?.toLowerCase().includes(q) ||
      s.subject_name?.toLowerCase().includes(q)
    )
  }
  return list
})

// ─── Data loading ──────────────────────────────────────────────────────────
const loadSubjects = async () => {
  loading.value = true
  try {
    const res = await callApi('sms.api.subject.list_subjects', { is_active: null })
    subjects.value = res || []
  } catch (e) {
    console.error(e)
    showToast('error', 'Failed to load subjects')
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const res = await callApi('sms.api.meta.get_departments', {})
    departments.value = res || []
  } catch (e) {
    console.error(e)
  }
}

const loadFacultyMappings = async () => {
  if (!facultySubject.value?.name) return
  try {
    const res = await callApi('sms.api.subject.get_subject', {
      name: facultySubject.value.name,
    })
    facultyMappings.value = res?.faculty_mappings || []
  } catch (e) {
    console.error(e)
  }
}

// ─── Create / Edit ─────────────────────────────────────────────────────────
const openCreateModal = () => {
  editingSubject.value = null
  showFormModal.value  = true
}

const openEditModal = (subject) => {
  editingSubject.value = { ...subject }
  showFormModal.value  = true
}

const closeFormModal = () => {
  showFormModal.value  = false
  editingSubject.value = null
}

const handleSave = async (formData) => {
  saving.value = true
  try {
    if (formData.name) {
      // Edit
      await callApi('sms.api.subject.update_subject', {
        name: formData.name,
        data: {
          subject_name: formData.subject_name,
          department:   formData.department,
          year_level:   formData.year_level,
          credits:      formData.credits,
          is_lab:       formData.is_lab ? 1 : 0,
          is_active:    formData.is_active ? 1 : 0,
        },
      }, { method: 'POST' })
      showToast('success', 'Subject updated')
    } else {
      // Create
      await callApi('sms.api.subject.create_subject', {
        data: {
          subject_code: formData.subject_code,
          subject_name: formData.subject_name,
          department:   formData.department,
          year_level:   formData.year_level,
          credits:      formData.credits,
          is_lab:       formData.is_lab ? 1 : 0,
          is_active:    formData.is_active ? 1 : 0,
        },
      }, { method: 'POST' })
      showToast('success', 'Subject created')
    }
    closeFormModal()
    await loadSubjects()
  } catch (e) {
    showToast('error', e?.message || 'Failed to save subject')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (formData) => {
  if (!formData.name) return
  if (!confirm(`Delete subject "${formData.subject_name}"? This cannot be undone.`)) {
    return
  }
  saving.value = true
  try {
    await callApi('sms.api.subject.delete_subject', {
      name: formData.name,
    }, { method: 'POST' })
    showToast('success', 'Subject deleted')
    closeFormModal()
    await loadSubjects()
  } catch (e) {
    showToast('error', e?.message || 'Failed to delete subject')
  } finally {
    saving.value = false
  }
}

// ─── Faculty modal ─────────────────────────────────────────────────────────
const openFacultyModal = async (subject) => {
  facultySubject.value = subject
  facultyMappings.value = []
  showFacultyModal.value = true
  await loadFacultyMappings()
}

const closeFacultyModal = () => {
  showFacultyModal.value = false
  facultySubject.value   = null
  facultyMappings.value  = []
  // Refresh list to update faculty counts on cards
  loadSubjects()
}

const handleAddFaculty = async ({ faculty, is_primary }) => {
  facultyBusy.value = true
  try {
    await callApi('sms.api.subject.assign_faculty', {
      subject:    facultySubject.value.name,
      faculty,
      is_primary,
    }, { method: 'POST' })

    // If new one is primary, unset others first
    if (is_primary) {
      const newMappings = await callApi('sms.api.subject.get_subject', {
        name: facultySubject.value.name,
      })
      const newMapping = (newMappings?.faculty_mappings || [])
        .find(m => m.faculty === faculty)
      if (newMapping) {
        await callApi('sms.api.subject.set_primary_faculty', {
          mapping_name: newMapping.name,
        }, { method: 'POST' })
      }
    }

    showToast('success', 'Faculty assigned')
    await loadFacultyMappings()
  } catch (e) {
    showToast('error', e?.message || 'Failed to assign')
  } finally {
    facultyBusy.value = false
  }
}

const handleRemoveFaculty = async (mappingName) => {
  if (!confirm('Remove this faculty from the subject?')) return
  facultyBusy.value = true
  try {
    await callApi('sms.api.subject.remove_faculty', {
      mapping_name: mappingName,
    }, { method: 'POST' })
    showToast('success', 'Faculty removed')
    await loadFacultyMappings()
  } catch (e) {
    showToast('error', e?.message || 'Failed to remove')
  } finally {
    facultyBusy.value = false
  }
}

const handleSetPrimary = async (mappingName) => {
  facultyBusy.value = true
  try {
    await callApi('sms.api.subject.set_primary_faculty', {
      mapping_name: mappingName,
    }, { method: 'POST' })
    showToast('success', 'Primary updated')
    await loadFacultyMappings()
  } catch (e) {
    showToast('error', e?.message || 'Failed')
  } finally {
    facultyBusy.value = false
  }
}

// ─── Toast ─────────────────────────────────────────────────────────────────
const showToast = (type, message) => {
  toast.value = { show: true, type, message }
  setTimeout(() => { toast.value.show = false }, 3500)
}

// ─── Lifecycle ─────────────────────────────────────────────────────────────
onMounted(() => {
  loadSubjects()
  loadDepartments()
})
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from,  .toast-leave-to      { opacity: 0; transform: translateY(20px); }
</style>
