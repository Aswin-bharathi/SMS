import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = createRouter({
  history: createWebHistory('/student-app/'),
  routes: [
    // ─── Public route: login ─────────────────────────────────────────────
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Auth/LoginView.vue'),
      meta: { public: true, title: 'Sign In' },
    },

    // ─── Protected routes (require login) ────────────────────────────────
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: 'Dashboard' },
        },
        // Hierarchy navigation
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
        // Existing routes
        {
          path: 'students',
          name: 'Students',
          component: () => import('@/views/Students/StudentList.vue'),
          meta: { title: 'Students' },
        },
        {
          path: 'students/:id',
          name: 'StudentDetail',
          component: () => import('@/views/Students/StudentDetail.vue'),
          meta: { title: 'Student Detail' },
        },
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
        {
          path: 'results',
          name: 'Results',
          component: () => import('@/views/Results/ResultView.vue'),
          meta: { title: 'Results' },
        },
        {
          path: 'courses',
          name: 'Courses',
          component: () => import('@/views/Courses/CourseView.vue'),
          meta: { title: 'Courses' },
        },
        {
          path: 'departments',
          name: 'Departments',
          component: () => import('@/views/Masters/DepartmentView.vue'),
          meta: { title: 'Departments' },
        },
        {
          path: 'programs',
          name: 'Programs',
          component: () => import('@/views/Masters/ProgramView.vue'),
          meta: { title: 'Programs' },
        },
        {
          path: 'academic-years',
          name: 'AcademicYears',
          component: () => import('@/views/Masters/AcademicYearView.vue'),
          meta: { title: 'Academic Years' },
        },
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
// Auth Guard: runs before every navigation
// ════════════════════════════════════════════════════════════════════════════
router.beforeEach(async (to, from, next) => {
  const { isLoggedIn, initialized, fetchMe } = useAuth()

  // Initialize auth on first load
  if (!initialized.value) {
    await fetchMe()
  }

  // Public route → let through
  if (to.meta.public) {
    return next()
  }

  // Protected route + not logged in → redirect to login
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
