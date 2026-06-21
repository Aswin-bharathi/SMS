import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = createRouter({
  history: createWebHistory('/student-app/'),
  routes: [
    // ─── Public: login ───────────────────────────────────────────────────
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Auth/LoginView.vue'),
      meta: { public: true, title: 'Sign In' },
    },

    // ─── Protected (auth required) ───────────────────────────────────────
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        // Dashboard
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: 'Dashboard' },
        },

        // ─── Academics hierarchy ──────────────────────────────────────
        {
          path: 'academics',
          name: 'Academics',
          component: () => import('@/views/Hierarchy/DepartmentsView.vue'),
          meta: { title: 'Academics' },
        },
        {
          path: 'academics/:dept/batches',
          name: 'DeptBatches',
          component: () => import('@/views/Hierarchy/BatchesView.vue'),
          meta: { title: 'Batches' },
        },
        {
          path: 'batches/:batch',
          name: 'BatchDetail',
          component: () => import('@/views/Hierarchy/BatchDetailView.vue'),
          meta: { title: 'Batch Detail' },
        },

        // ─── Student detail (no list — list lives inside Academics) ──
        {
          path: 'students/:id',
          name: 'StudentDetail',
          component: () => import('@/views/Students/StudentDetail.vue'),
          meta: { title: 'Student Detail' },
        },

        // ─── Attendance ─────────────────────────────────────────────
        {
          path: 'attendance',
          name: 'Attendance',
          component: () => import('@/views/Attendance/MyClassesView.vue'),
          meta: { title: 'My Classes' },
        },
        {
          path: 'attendance/:slot/:date',
          name: 'MarkAttendance',
          component: () => import('@/views/Attendance/MarkAttendanceView.vue'),
          meta: { title: 'Mark Attendance' },
        },
        {
          path: 'substitutions',
          name: 'Substitutions',
          component: () => import('@/views/Attendance/SubstitutionsView.vue'),
          meta: { title: 'Substitutions' },
        },

        // ─── Curriculum ─────────────────────────────────────────────
        {
          path: 'subjects',
          name: 'Subjects',
          component: () => import('@/views/Subjects/SubjectsView.vue'),
          meta: { title: 'Subjects' },
        },

        // ─── Fees ───────────────────────────────────────────────────
        {
          path: 'fees',
          name: 'Fees',
          component: () => import('@/views/Fees/FeeView.vue'),
          meta: { title: 'Fees' },
        },
        {
          path: 'fee-structures',
          name: 'FeeStructures',
          component: () => import('@/views/Fees/FeeStructureView.vue'),
          meta: { title: 'Fee Structures' },
        },

        // ─── Settings ───────────────────────────────────────────────
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings/SettingsView.vue'),
          meta: { title: 'Settings' },
        },
      ],
    },

    // Catch-all → login
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login',
    },
  ],
})

// ════════════════════════════════════════════════════════════════════════════
// Auth Guard
// ════════════════════════════════════════════════════════════════════════════
router.beforeEach(async (to, from, next) => {
  const { isLoggedIn, initialized, fetchMe } = useAuth()

  if (!initialized.value) {
    await fetchMe()
  }

  if (to.meta.public) {
    return next()
  }

  if (to.meta.requiresAuth && !isLoggedIn.value) {
    return next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
  }

  next()
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'Home'} | EduManage`
})

export default router
