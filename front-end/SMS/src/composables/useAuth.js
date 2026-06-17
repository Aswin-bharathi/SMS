import { ref, computed } from 'vue'

// ════════════════════════════════════════════════════════════════════════════
// Global reactive auth state (singleton — shared across all components)
// ════════════════════════════════════════════════════════════════════════════
const user        = ref(null)
const loading     = ref(false)
const initialized = ref(false)

export function useAuth() {
  // ─── Computed flags ──────────────────────────────────────────────────────
  const isLoggedIn = computed(() => user.value?.logged_in === true)
  const isAdmin    = computed(() => user.value?.is_admin === true)
  const isStaff    = computed(() => user.value?.is_staff === true)
  const isStudent  = computed(() => user.value?.is_student === true)
  const fullName   = computed(() => user.value?.full_name || 'Guest')
  const email      = computed(() => user.value?.email || '')
  const roles      = computed(() => user.value?.roles || [])
  const studentId  = computed(() => user.value?.student_id || null)
  const myBatches  = computed(() => user.value?.batches || [])

  const roleLabel = computed(() => {
    if (isAdmin.value)   return 'System Manager'
    if (isStaff.value)   return 'Class In-Charge'
    if (isStudent.value) return 'Student'
    return 'Guest'
  })

  // ─── Fetch current user info from backend ────────────────────────────────
  const fetchMe = async () => {
    loading.value = true
    try {
      const res = await fetch('/api/method/sms.api.auth.whoami', {
        credentials: 'include',
      })
      const data = await res.json()
      user.value = data.message || { logged_in: false }
    } catch (e) {
      console.error('whoami failed:', e)
      user.value = { logged_in: false }
    } finally {
      loading.value = false
      initialized.value = true
    }
    return user.value
  }

  // ─── Login ───────────────────────────────────────────────────────────────
  const login = async (emailInput, password) => {
    loading.value = true
    try {
      const res = await fetch('/api/method/login', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          usr: emailInput,
          pwd: password,
        }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.message || 'Invalid email or password')
      }

      // After successful login, fetch user details
      await fetchMe()
      return { success: true, user: user.value }
    } catch (e) {
      return { success: false, message: e.message }
    } finally {
      loading.value = false
    }
  }

  // ─── Logout ──────────────────────────────────────────────────────────────
  const logout = async () => {
    try {
      await fetch('/api/method/logout', { credentials: 'include' })
    } catch (e) {
      console.error('logout failed:', e)
    }
    user.value        = { logged_in: false }
    initialized.value = false
    window.location.href = '/student-app/login'
  }

  return {
    // state
    user, loading, initialized,
    // flags
    isLoggedIn, isAdmin, isStaff, isStudent,
    fullName, email, roles, roleLabel,
    studentId, myBatches,
    // actions
    fetchMe, login, logout,
  }
}
