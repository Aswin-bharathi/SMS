<template>
  <div class="space-y-5">
    <!-- Breadcrumb -->
    <nav class="flex flex-wrap items-center gap-2 text-sm">
      <router-link to="/academics" class="text-primary-500 hover:underline">
        Academics
      </router-link>
      <ChevronRight class="h-4 w-4 text-slate-400" />
      <router-link
        v-if="batch.department"
        :to="`/academics/${encodeURIComponent(batch.department)}/batches`"
        class="text-primary-500 hover:underline"
      >
        {{ batch.department }}
      </router-link>
      <ChevronRight v-if="batch.department" class="h-4 w-4 text-slate-400" />
      <span class="font-semibold text-slate-700 dark:text-slate-200">
        {{ batch.batch_year || batchId }}
      </span>
    </nav>

    <!-- Loading -->
    <div v-if="loading" class="rounded-xl bg-white dark:bg-slate-800 p-12 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 animate-pulse">
      <div class="h-8 w-1/3 bg-slate-200 dark:bg-slate-700 rounded" />
      <div class="mt-6 grid grid-cols-4 gap-3">
        <div v-for="i in 4" :key="i" class="h-20 bg-slate-100 dark:bg-slate-700/50 rounded" />
      </div>
    </div>

    <template v-else>
      <!-- Header card -->
      <div class="rounded-xl bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-800/50 p-6 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 class="text-3xl font-bold text-slate-900 dark:text-white">
              {{ batch.batch_year }}
            </h1>
            <p class="mt-1 text-sm text-slate-500">
              {{ batch.department }} · {{ batch.program || 'No program' }}
            </p>
            <div class="mt-3 flex flex-wrap items-center gap-2">
              <span class="inline-flex items-center rounded-full bg-primary-50 dark:bg-primary-500/20 px-3 py-1 text-xs font-semibold text-primary-700 dark:text-primary-300">
                {{ batch.current_semester || 'Sem 1' }}
              </span>
              <span class="text-xs text-slate-500">
                of {{ batch.total_semesters || 8 }} semesters
              </span>
            </div>
          </div>
          <div class="flex items-center gap-3 rounded-xl bg-white dark:bg-slate-700/50 px-4 py-3 ring-1 ring-slate-200 dark:ring-slate-700">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-500 text-white">
              <UserCheck class="h-5 w-5" />
            </div>
            <div>
              <p class="text-xs text-slate-400">Class In-Charge</p>
              <p class="text-sm font-semibold text-slate-900 dark:text-white">
                {{ batch.class_in_charge_name || batch.class_in_charge || 'Not assigned' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
          <div class="rounded-xl bg-white dark:bg-slate-700/40 p-4 ring-1 ring-slate-100 dark:ring-slate-700">
            <div class="flex items-center gap-2 text-xs text-slate-500">
              <Users class="h-3.5 w-3.5" />
              Students
            </div>
            <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
              {{ batch.student_count || 0 }}
            </p>
          </div>
          <div class="rounded-xl bg-white dark:bg-slate-700/40 p-4 ring-1 ring-slate-100 dark:ring-slate-700">
            <div class="flex items-center gap-2 text-xs text-slate-500">
              <IndianRupee class="h-3.5 w-3.5" />
              Billed
            </div>
            <p class="text-xl font-bold text-slate-900 dark:text-white mt-1">
              ₹{{ formatMoney(batch.fee_summary?.total) }}
            </p>
          </div>
          <div class="rounded-xl bg-white dark:bg-slate-700/40 p-4 ring-1 ring-slate-100 dark:ring-slate-700">
            <div class="flex items-center gap-2 text-xs text-slate-500">
              <CheckCircle class="h-3.5 w-3.5" />
              Collected
            </div>
            <p class="text-xl font-bold text-emerald-600 mt-1">
              ₹{{ formatMoney(batch.fee_summary?.paid) }}
            </p>
          </div>
          <div class="rounded-xl bg-white dark:bg-slate-700/40 p-4 ring-1 ring-slate-100 dark:ring-slate-700">
            <div class="flex items-center gap-2 text-xs text-slate-500">
              <Clock class="h-3.5 w-3.5" />
              Outstanding
            </div>
            <p class="text-xl font-bold text-amber-600 mt-1">
              ₹{{ formatMoney(batch.fee_summary?.outstanding) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="rounded-xl bg-white dark:bg-slate-800 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700 overflow-hidden">
        <div class="flex border-b border-slate-200 dark:border-slate-700 overflow-x-auto">
          <button
            v-for="t in tabs"
            :key="t.key"
            :class="[
              'flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 -mb-px whitespace-nowrap transition-colors',
              active === t.key
                ? 'border-primary-500 text-primary-500 bg-primary-50/30 dark:bg-primary-500/5'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300',
            ]"
            @click="active = t.key"
          >
            <component :is="t.icon" class="h-4 w-4" />
            {{ t.label }}
            <span
              v-if="t.count !== null"
              :class="[
                'text-xs px-2 py-0.5 rounded-full font-semibold',
                active === t.key
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-300'
                  : 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400',
              ]"
            >{{ t.count }}</span>
          </button>
        </div>

        <div class="p-5">
          <!-- Students Tab -->
          <div v-if="active === 'students'" class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-slate-100 dark:border-slate-700">
                  <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Roll</th>
                  <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Student</th>
                  <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Email</th>
                  <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Gender</th>
                  <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Semester</th>
                  <th class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
                <tr
                  v-for="s in batch.students"
                  :key="s.name"
                  class="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
                >
                  <td class="px-3 py-3 text-sm font-mono font-semibold text-slate-700 dark:text-slate-200">
                    {{ s.roll_number || '—' }}
                  </td>
                  <td class="px-3 py-3">
                    <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ s.full_name }}</p>
                    <p class="text-xs text-slate-400">{{ s.student_id || s.name }}</p>
                  </td>
                  <td class="px-3 py-3 text-sm text-slate-600 dark:text-slate-300">{{ s.email || '—' }}</td>
                  <td class="px-3 py-3 text-sm text-slate-600 dark:text-slate-300">{{ s.gender || '—' }}</td>
                  <td class="px-3 py-3 text-sm text-slate-600 dark:text-slate-300">{{ s.semester || '—' }}</td>
                  <td class="px-3 py-3">
                    <span class="inline-flex items-center rounded-full bg-emerald-50 dark:bg-emerald-500/20 px-2.5 py-0.5 text-xs font-medium text-emerald-700 dark:text-emerald-300">
                      {{ s.status }}
                    </span>
                  </td>
                </tr>
                <tr v-if="!batch.students?.length">
                  <td colspan="6" class="px-3 py-12 text-center text-sm text-slate-400">
                    No students in this batch yet.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Attendance Tab -->
          <BatchAttendance
            v-else-if="active === 'attendance'"
            :batch="batchId"
            @saved="loadBatch"
          />

          <!-- Fees Tab -->
          <BatchFees
            v-else-if="active === 'fees'"
            :batch="batchId"
            @changed="loadBatch"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { plural } from '@/composables/usePlural'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  Calendar, CheckCircle, ChevronRight, Clock, IndianRupee,
  UserCheck, Users,
} from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'
import BatchAttendance from './BatchAttendance.vue'
import BatchFees from './BatchFees.vue'

const route       = useRoute()
const { callApi } = useApi()
const batchId     = decodeURIComponent(route.params.batch)

const batch   = ref({})
const loading = ref(true)
const active  = ref('students')

const formatMoney = (v) => Number(v || 0).toLocaleString('en-IN')

const tabs = computed(() => [
  { key: 'students',   label: 'Students',   icon: Users,       count: batch.value.student_count || 0 },
  { key: 'attendance', label: 'Attendance', icon: Calendar,    count: null },
  { key: 'fees',       label: 'Fees',       icon: IndianRupee, count: batch.value.fee_summary?.count || 0 },
])

const loadBatch = async () => {
  loading.value = true
  try {
    batch.value = (await callApi('sms.api.hierarchy.get_batch_detail', { batch: batchId })) ?? {}
  } catch (e) {
    console.error('Failed to load batch:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadBatch)
</script>
