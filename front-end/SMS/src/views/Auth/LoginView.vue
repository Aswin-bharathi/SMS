<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800 p-4">
    <div class="w-full max-w-md">
      <!-- Logo / Brand -->
      <div class="text-center mb-8">
        <div class="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-500 to-cyan-500 shadow-xl shadow-primary-500/30 mb-4">
          <GraduationCap class="h-9 w-9 text-white" />
        </div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white">EduManage</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Student Management System
        </p>
      </div>

      <!-- Card -->
      <div class="rounded-2xl bg-white dark:bg-slate-800 p-8 shadow-2xl ring-1 ring-slate-200 dark:ring-slate-700">
        <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-1">
          Welcome back
        </h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mb-6">
          Sign in to your account
        </p>

        <form class="space-y-4" @submit.prevent="handleLogin">
          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Email or Username
            </label>
            <div class="relative">
              <Mail class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                v-model="emailInput"
                type="text"
                required
                autocomplete="username"
                placeholder="you@example.com"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 pl-10 pr-3 py-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Password
            </label>
            <div class="relative">
              <Lock class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                placeholder="••••••••"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 pl-10 pr-10 py-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                @click="showPassword = !showPassword"
              >
                <Eye v-if="!showPassword" class="h-4 w-4" />
                <EyeOff v-else class="h-4 w-4" />
              </button>
            </div>
          </div>

          <!-- Error message -->
          <div
            v-if="error"
            class="rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-700 px-3 py-2.5 text-sm text-red-700 dark:text-red-300 flex items-start gap-2"
          >
            <AlertCircle class="h-4 w-4 shrink-0 mt-0.5" />
            <span>{{ error }}</span>
          </div>

          <!-- Submit button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full rounded-lg bg-gradient-to-r from-primary-500 to-cyan-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-primary-500/30 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <span v-if="loading" class="inline-flex items-center gap-2 justify-center w-full">
              <Loader2 class="h-4 w-4 animate-spin" />
              Signing in…
            </span>
            <span v-else class="inline-flex items-center gap-2 justify-center w-full">
              Sign In
              <ArrowRight class="h-4 w-4" />
            </span>
          </button>
        </form>

        <!-- Dev quick-fill helper -->
        <div class="mt-6 pt-6 border-t border-slate-100 dark:border-slate-700">
          <p class="text-xs text-slate-400 mb-2 text-center">Quick fill (dev only):</p>
          <div class="grid grid-cols-3 gap-2">
            <button
              type="button"
              class="rounded-lg bg-slate-100 dark:bg-slate-700 px-2 py-2 text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
              @click="quickFill('admin')"
            >
              <Shield class="h-3 w-3 mx-auto mb-0.5" />
              Admin
            </button>
            <button
              type="button"
              class="rounded-lg bg-slate-100 dark:bg-slate-700 px-2 py-2 text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
              @click="quickFill('staff')"
            >
              <UserCheck class="h-3 w-3 mx-auto mb-0.5" />
              Staff
            </button>
            <button
              type="button"
              class="rounded-lg bg-slate-100 dark:bg-slate-700 px-2 py-2 text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
              @click="quickFill('student')"
            >
              <GraduationCap class="h-3 w-3 mx-auto mb-0.5" />
              Student
            </button>
          </div>
        </div>
      </div>

      <p class="text-center text-xs text-slate-400 mt-6">
        © 2026 EduManage · Student Management System
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  AlertCircle, ArrowRight, Eye, EyeOff,
  GraduationCap, Loader2, Lock, Mail, Shield, UserCheck,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route  = useRoute()
const { login, fetchMe, isLoggedIn } = useAuth()

const emailInput   = ref('')
const password     = ref('')
const showPassword = ref(false)
const loading      = ref(false)
const error        = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value   = ''
  try {
    const result = await login(emailInput.value, password.value)

    if (result.success) {
      // Route based on role
      const redirectPath = route.query.redirect
      if (redirectPath) {
        router.push(redirectPath)
      } else if (result.user.is_student) {
        router.push('/me/profile')
      } else {
        router.push('/')
      }
    } else {
      error.value = result.message || 'Login failed. Please check your credentials.'
    }
  } catch (e) {
    error.value = e.message || 'Unexpected error occurred'
  } finally {
    loading.value = false
  }
}

// Dev helper: pre-fill credentials for testing
const quickFill = (role) => {
  if (role === 'admin') {
    emailInput.value = 'Administrator'
    password.value   = ''
  } else if (role === 'staff') {
    emailInput.value = 'subi83.k@gmail.com'
    password.value   = ''
  } else if (role === 'student') {
    emailInput.value = 'asanth2712@gmail.com'
    password.value   = 'Student@123'
  }
}

// If already logged in, skip the login page
onMounted(async () => {
  await fetchMe()
  if (isLoggedIn.value) {
    router.push('/')
  }
})
</script>
