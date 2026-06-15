import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/student-app/'),
  routes: [
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: 'Dashboard' }
        },
        {
          path: 'students',
          name: 'Students',
          component: () => import('@/views/Students/StudentList.vue'),
          meta: { title: 'Students' }
        },
        {
          path: 'students/:id',
          name: 'StudentDetail',
          component: () => import('@/views/Students/StudentDetail.vue'),
          meta: { title: 'Student Detail' }
        },
        {
          path: 'attendance',
          name: 'Attendance',
          component: () => import('@/views/Attendance/AttendanceView.vue'),
          meta: { title: 'Attendance' }
        },
        {
          path: 'fees',
          name: 'Fees',
          component: () => import('@/views/Fees/FeeView.vue'),
          meta: { title: 'Fees' }
        },
        {
          path: 'fee-structures',
          name: 'FeeStructures',
          component: () => import('@/views/Fees/FeeStructureView.vue'),
          meta: { title: 'Fee Structures' }
        },
        {
          path: 'results',
          name: 'Results',
          component: () => import('@/views/Results/ResultView.vue'),
          meta: { title: 'Results' }
        },
        {
          path: 'courses',
          name: 'Courses',
          component: () => import('@/views/Courses/CourseView.vue'),
          meta: { title: 'Courses' }
        },
        {
          path: 'departments',
          name: 'Departments',
          component: () => import('@/views/Masters/DepartmentView.vue'),
          meta: { title: 'Departments' }
        },
        {
          path: 'programs',
          name: 'Programs',
          component: () => import('@/views/Masters/ProgramView.vue'),
          meta: { title: 'Programs' }
        },
        {
          path: 'academic-years',
          name: 'AcademicYears',
          component: () => import('@/views/Masters/AcademicYearView.vue'),
          meta: { title: 'Academic Years' }
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings/SettingsView.vue'),
          meta: { title: 'Settings' }
        },
      ]
    }
  ]
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'Home'} | Student Management`
})

export default router
