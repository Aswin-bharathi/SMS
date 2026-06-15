import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

export const useStudentStore = defineStore('student', () => {
  const students = ref([])
  const currentStudent = ref(null)
  const loading = ref(false)
  const total = ref(0)
  const { callApi } = useApi()

 const fetchStudents = async (params = {}) => {
    loading.value = true
    try {
      const res = await callApi('sms.api.student.get_all_students', params)
      // The backend specifically returns "data" and "pagination"
      students.value = res.data || []
      total.value = res.pagination?.total || 0
    } finally {
      loading.value = false
    }
  }

  const fetchStudent = async (id) => {
    loading.value = true
    try {
      const res = await callApi('sms.api.student.get_student', { student_id: id })
      currentStudent.value = res
    } finally {
      loading.value = false
    }
  }

  const createStudent = async (data) => {
    return await callApi('sms.api.student.create_student', { data }, { method: 'POST' })
  }

  const updateStudent = async (id, data) => {
    return await callApi('sms.api.student.update_student', {
      student_id: id, data
    }, { method: 'POST' })
  }

  const deleteStudent = async (id) => {
    return await callApi('sms.api.student.delete_student', { student_id: id }, { method: 'POST' })
  }

  return {
    students, currentStudent, loading, total,
    fetchStudents, fetchStudent, createStudent,
    updateStudent, deleteStudent
  }
})
