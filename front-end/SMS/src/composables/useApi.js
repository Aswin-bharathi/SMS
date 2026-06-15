import axios from 'axios'
import { ref } from 'vue'

const BASE_URL = '/api/method/'

const getCsrfToken = () => {
  if (typeof window === 'undefined') return ''

  if (window.csrf_token) return window.csrf_token
  if (window.frappe?.csrf_token) return window.frappe.csrf_token

  const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : ''
}

const encodeParams = (params = {}) => {
  const body = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    body.append(key, typeof value === 'object' ? JSON.stringify(value) : String(value))
  })

  return body
}

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const callApi = async (method, params = {}, options = {}) => {
    loading.value = true
    error.value = null

    try {
      const requestMethod = (options.method || 'GET').toUpperCase()
      const config = {
        method: requestMethod,
        url: `${BASE_URL}${method}`,
        withCredentials: true,
        headers: {},
      }

      const csrfToken = getCsrfToken()
      if (csrfToken) {
        config.headers['X-Frappe-CSRF-Token'] = csrfToken
      }

      if (requestMethod === 'POST' || requestMethod === 'PUT' || requestMethod === 'PATCH' || requestMethod === 'DELETE') {
        config.data = encodeParams(params)
        config.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
      } else {
        config.params = params
      }

      const response = await axios(config)
      return response.data?.message !== undefined ? response.data.message : response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.response?.data?.exception || err.response?.data?.exc || err.message || 'Something went wrong'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return { callApi, loading, error }
}
