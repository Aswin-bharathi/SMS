<template>
  <div class="space-y-5">
    <!-- ─── Header ──────────────────────────────────────────────── -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">
          Substitutions
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Manage class substitution requests
        </p>
      </div>
      <button
        class="inline-flex items-center gap-2 rounded-xl
               bg-gradient-to-r from-primary-500 to-cyan-500
               px-5 py-2.5 text-sm font-semibold text-white
               shadow-lg shadow-primary-500/30 hover:shadow-xl transition-all"
        @click="openRequestModal"
      >
        <Plus class="h-4 w-4" />
        Request Substitution
      </button>
    </div>

    <!-- ─── Tabs ────────────────────────────────────────────────── -->
    <div class="flex gap-1 rounded-xl bg-slate-100 dark:bg-slate-800 p-1">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="[
          'flex-1 rounded-lg px-4 py-2 text-sm font-semibold transition-all',
          activeTab === tab.key
            ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
            : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200',
        ]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span
          v-if="tabCount(tab.key)"
          :class="[
            'ml-1.5 inline-flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold',
            tab.key === 'pending'
              ? 'bg-amber-500 text-white'
              : 'bg-slate-200 dark:bg-slate-600 text-slate-700 dark:text-slate-200',
          ]"
        >
          {{ tabCount(tab.key) }}
        </span>
      </button>
    </div>

    <!-- ─── Loading ─────────────────────────────────────────────── -->
    <div v-if="loading" class="space-y-3">
      <div
        v-for="i in 3" :key="i"
        class="h-32 rounded-xl bg-white dark:bg-slate-800 animate-pulse
               ring-1 ring-slate-200 dark:ring-slate-700"
      />
    </div>

    <!-- ─── Pending ─────────────────────────────────────────────── -->
    <template v-else-if="activeTab === 'pending'">
      <div
        v-if="isAdminOrHod && pendingList.length"
        class="rounded-xl bg-amber-50 dark:bg-amber-500/10
               border border-amber-200 dark:border-amber-700/50 p-4
               flex items-center gap-3 text-sm text-amber-800 dark:text-amber-300"
      >
        <AlertCircle class="h-5 w-5 shrink-0" />
        <span>
          <strong>{{ pendingList.length }}</strong>
          substitution request{{ pendingList.length !== 1 ? 's' : '' }}
          awaiting your approval.
        </span>
      </div>

      <div v-if="filteredList.length" class="space-y-3">
        <SubstitutionCard
          v-for="sub in filteredList"
          :key="sub.name"
          :sub="sub"
          :is-admin-or-hod="isAdminOrHod"
          @approve="handleApprove"
          @reject="openRejectModal"
        />
      </div>
      <EmptyState
        v-else
        icon="CheckCircle"
        title="No pending requests"
        message="All substitution requests have been handled."
      />
    </template>

    <!-- ─── Mine ─────────────────────────────────────────────────── -->
    <template v-else-if="activeTab === 'mine'">
      <div v-if="filteredList.length" class="space-y-3">
        <SubstitutionCard
          v-for="sub in filteredList"
          :key="sub.name"
          :sub="sub"
          :is-admin-or-hod="isAdminOrHod"
          :show-actions="false"
        />
      </div>
      <EmptyState
        v-else
        icon="RefreshCcw"
        title="No substitutions yet"
        message="You haven't requested or covered any substitutions."
      />
    </template>

    <!-- ─── All ───────────────────────────────────────────────────── -->
    <template v-else-if="activeTab === 'all'">
      <div v-if="filteredList.length" class="space-y-3">
        <SubstitutionCard
          v-for="sub in filteredList"
          :key="sub.name"
          :sub="sub"
          :is-admin-or-hod="isAdminOrHod"
          @approve="handleApprove"
          @reject="openRejectModal"
        />
      </div>
      <EmptyState
        v-else
        icon="CalendarOff"
        title="No substitutions found"
        message="No substitution records match the current filter."
      />
    </template>

    <!-- ════════════════════════════════════════════════════════════
         REQUEST MODAL — calendar-based class picker
    ════════════════════════════════════════════════════════════ -->
    <transition name="modal">
      <div
        v-if="showRequestModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="closeRequestModal"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" />

        <!-- Modal panel: bigger + uses flex column for sticky header/footer -->
        <div class="relative w-full max-w-2xl max-h-[90vh]
                    rounded-2xl bg-white dark:bg-slate-800
                    shadow-2xl ring-1 ring-slate-200 dark:ring-slate-700
                    flex flex-col">
          <!-- Modal HEADER (sticky) -->
          <div class="flex items-center justify-between border-b
                      border-slate-100 dark:border-slate-700 px-6 py-4
                      shrink-0">
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">
              Request Substitution
            </h2>
            <button
              class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100
                     dark:hover:bg-slate-700"
              @click="closeRequestModal"
            >
              <X class="h-5 w-5" />
            </button>
          </div>

          <!-- Modal BODY (scrolls if too tall) -->
          <div class="px-6 py-5 space-y-5 overflow-y-auto flex-1">
            <!-- Calendar + class picker (handles BOTH date AND slot selection) -->
            <MyCalendarPicker
              ref="pickerRef"
              :user-email="email || ''"
              @select="onClassPicked"
            />

            <!-- Substitute faculty (shown only after a class is picked) -->
            <div v-if="form.timetable_slot">
              <label class="block text-sm font-semibold text-slate-700
                            dark:text-slate-300 mb-1.5">
                Substitute Faculty *
              </label>
              <div
                v-if="loadingFaculty"
                class="flex items-center gap-2 text-sm text-slate-400 py-2"
              >
                <Loader2 class="h-4 w-4 animate-spin" />
                Finding available faculty…
              </div>
              <select
                v-else
                v-model="form.substitute_faculty"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                       bg-white dark:bg-slate-900 px-3 py-2.5 text-sm
                       text-slate-900 dark:text-white
                       focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">
                  {{ availableFaculty.length
                      ? '— Select substitute —'
                      : '— No faculty available —' }}
                </option>
                <option
                  v-for="f in availableFaculty"
                  :key="f.name"
                  :value="f.name"
                >
                  {{ f.full_name || f.name }}
                </option>
              </select>
              <p
                v-if="!loadingFaculty && availableFaculty.length === 0"
                class="mt-1 text-xs text-amber-600 dark:text-amber-400"
              >
                No faculty are free at this hour. Contact admin.
              </p>
            </div>

            <!-- Reason -->
            <div v-if="form.timetable_slot">
              <label class="block text-sm font-semibold text-slate-700
                            dark:text-slate-300 mb-1.5">
                Reason
                <span class="font-normal text-slate-400">(optional)</span>
              </label>
              <textarea
                v-model="form.reason"
                rows="2"
                placeholder="e.g. Medical appointment, Conference…"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                       bg-white dark:bg-slate-900 px-3 py-2.5 text-sm
                       text-slate-900 dark:text-white resize-none
                       focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <!-- Auto-approve note for admin -->
            <div
              v-if="form.timetable_slot && isAdminOrHod"
              class="flex items-center gap-2 rounded-lg bg-emerald-50
                     dark:bg-emerald-500/10 px-3 py-2 text-xs
                     text-emerald-700 dark:text-emerald-300"
            >
              <CheckCircle class="h-4 w-4 shrink-0" />
              As HOD/Admin, your request will be auto-approved.
            </div>
          </div>

          <!-- Modal FOOTER (sticky) -->
          <div class="flex items-center justify-end gap-3 border-t
                      border-slate-100 dark:border-slate-700 px-6 py-4
                      shrink-0">
            <button
              class="rounded-lg border border-slate-200 dark:border-slate-700
                     px-4 py-2 text-sm font-medium text-slate-700
                     dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
              @click="closeRequestModal"
            >
              Cancel
            </button>
            <button
              :disabled="!canSubmitRequest || submitting"
              class="inline-flex items-center gap-2 rounded-lg
                     bg-gradient-to-r from-primary-500 to-cyan-500
                     px-5 py-2 text-sm font-semibold text-white shadow-md
                     disabled:opacity-50 disabled:cursor-not-allowed"
              @click="submitRequest"
            >
              <Loader2 v-if="submitting" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
              {{ submitting
                  ? 'Submitting…'
                  : isAdminOrHod ? 'Assign & Approve' : 'Submit Request' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ════════════════════════════════════════════════════════════
         REJECT MODAL
    ════════════════════════════════════════════════════════════ -->
    <transition name="modal">
      <div
        v-if="showRejectModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="showRejectModal = false"
      >
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" />
        <div class="relative w-full max-w-md rounded-2xl bg-white dark:bg-slate-800
                    shadow-2xl ring-1 ring-slate-200 dark:ring-slate-700">
          <div class="flex items-center justify-between border-b
                      border-slate-100 dark:border-slate-700 px-6 py-4">
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">
              Reject Substitution
            </h2>
            <button
              class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100
                     dark:hover:bg-slate-700"
              @click="showRejectModal = false"
            >
              <X class="h-5 w-5" />
            </button>
          </div>
          <div class="px-6 py-5 space-y-4">
            <p class="text-sm text-slate-600 dark:text-slate-300">
              Provide a reason for rejection (optional but recommended):
            </p>
            <textarea
              v-model="rejectReason"
              rows="3"
              placeholder="e.g. Substitute faculty also has a class…"
              class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                     bg-white dark:bg-slate-900 px-3 py-2.5 text-sm
                     text-slate-900 dark:text-white resize-none
                     focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div class="flex items-center justify-end gap-3 border-t
                      border-slate-100 dark:border-slate-700 px-6 py-4">
            <button
              class="rounded-lg border border-slate-200 dark:border-slate-700
                     px-4 py-2 text-sm font-medium text-slate-700
                     dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
              @click="showRejectModal = false"
            >
              Cancel
            </button>
            <button
              :disabled="submitting"
              class="inline-flex items-center gap-2 rounded-lg bg-red-500
                     px-5 py-2 text-sm font-semibold text-white shadow-md
                     disabled:opacity-50"
              @click="submitReject"
            >
              <Loader2 v-if="submitting" class="h-4 w-4 animate-spin" />
              <XCircle v-else class="h-4 w-4" />
              {{ submitting ? 'Rejecting…' : 'Confirm Reject' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ─── Toast ────────────────────────────────────────────────── -->
    <transition name="toast">
      <div
        v-if="toast.show"
        :class="[
          'fixed bottom-6 right-6 z-50 flex items-center gap-3',
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
  AlertCircle, CheckCircle, Loader2, Plus,
  Send, X, XCircle,
} from 'lucide-vue-next'
import { useApi }       from '@/composables/useApi'
import { useAuth }      from '@/composables/useAuth'
import SubstitutionCard from '@/components/ui/SubstitutionCard.vue'
import EmptyState       from '@/components/ui/EmptyState.vue'
import MyCalendarPicker from '@/components/ui/MyCalendarPicker.vue'

const { callApi }      = useApi()
const { email, roles } = useAuth()

// ─── Auth ──────────────────────────────────────────────────────────────────
const isAdminOrHod = computed(() =>
  roles.value?.some(r =>
    ['System Manager', 'SMS Admin', 'SMS HOD', 'Administrator'].includes(r)
  )
)

// ─── State ─────────────────────────────────────────────────────────────────
const allSubs    = ref([])
const loading    = ref(false)
const submitting = ref(false)
const activeTab  = ref('pending')

const showRequestModal = ref(false)
const showRejectModal  = ref(false)
const rejectTarget     = ref(null)
const rejectReason     = ref('')

const availableFaculty = ref([])
const loadingFaculty   = ref(false)

const pickerRef = ref(null)

const today = new Date().toISOString().slice(0, 10)

const form = ref({
  timetable_slot:     '',
  date:               today,
  substitute_faculty: '',
  reason:             '',
  hour:               '',
  department:         '',
})

const toast = ref({ show: false, type: 'success', message: '' })

// ─── Tabs ──────────────────────────────────────────────────────────────────
const tabs = computed(() => {
  const t = [
    { key: 'pending', label: 'Pending' },
    { key: 'mine',    label: 'My Substitutions' },
  ]
  if (isAdminOrHod.value) t.push({ key: 'all', label: 'All' })
  return t
})

const pendingList = computed(() =>
  allSubs.value.filter(s => s.status === 'Pending')
)

const filteredList = computed(() => {
  if (activeTab.value === 'pending') return pendingList.value
  if (activeTab.value === 'mine') {
    const me = email.value
    return allSubs.value.filter(s =>
      s.original_faculty === me || s.substitute_faculty === me
    )
  }
  return allSubs.value
})

const tabCount = (key) => {
  if (key === 'pending') return pendingList.value.length  || null
  if (key === 'mine')    return filteredList.value.length || null
  return null
}

// ─── Loaders ───────────────────────────────────────────────────────────────
const loadSubs = async () => {
  loading.value = true
  try {
    const res = await callApi('sms.api.substitution.list_substitutions', {})
    allSubs.value = res || []
  } catch (e) {
    console.error('[Substitutions] loadSubs:', e)
  } finally {
    loading.value = false
  }
}

const loadAvailableFaculty = async () => {
  if (!form.value.timetable_slot || !form.value.date) return
  loadingFaculty.value   = true
  availableFaculty.value = []
  try {
    const res = await callApi('sms.api.substitution.get_available_faculty', {
      date:       form.value.date,
      hour:       form.value.hour,
      department: form.value.department,
      exclude:    email.value,
    })
    availableFaculty.value = res?.available || []
  } catch (e) {
    console.error('[Substitutions] loadAvailableFaculty:', e)
  } finally {
    loadingFaculty.value = false
  }
}

// ─── Calendar picker callback ─────────────────────────────────────────────
const onClassPicked = (payload) => {
  if (!payload) {
    form.value.timetable_slot = ''
    form.value.hour           = ''
    form.value.department     = ''
    form.value.date           = today
    form.value.substitute_faculty = ''
    availableFaculty.value    = []
    return
  }
  form.value.timetable_slot     = payload.slot_id
  form.value.hour               = payload.hour
  form.value.department         = payload.department || ''
  form.value.date               = payload.date
  form.value.substitute_faculty = ''   // reset on new selection
  loadAvailableFaculty()
}

// ─── Form actions ──────────────────────────────────────────────────────────
const canSubmitRequest = computed(() =>
  form.value.timetable_slot &&
  form.value.date &&
  form.value.substitute_faculty
)

const openRequestModal = () => {
  resetForm()
  showRequestModal.value = true
}

const closeRequestModal = () => {
  showRequestModal.value = false
  resetForm()
  pickerRef.value?.clearSelection()
}

const resetForm = () => {
  form.value = {
    timetable_slot: '', date: today,
    substitute_faculty: '', reason: '', hour: '', department: '',
  }
  availableFaculty.value = []
}

const submitRequest = async () => {
  if (!canSubmitRequest.value || submitting.value) return
  submitting.value = true
  try {
    await callApi(
      'sms.api.substitution.request_substitution',
      { data: form.value },
      { method: 'POST' },
    )
    showToast('success',
      isAdminOrHod.value
        ? 'Substitution assigned and approved!'
        : 'Request submitted — awaiting HOD approval.'
    )
    closeRequestModal()
    await loadSubs()
  } catch (e) {
    showToast('error', e?.message || 'Failed to submit request')
  } finally {
    submitting.value = false
  }
}

// ─── Approve / Reject ──────────────────────────────────────────────────────
const handleApprove = async (name) => {
  submitting.value = true
  try {
    await callApi(
      'sms.api.substitution.approve_substitution',
      { name },
      { method: 'POST' },
    )
    showToast('success', 'Substitution approved!')
    await loadSubs()
  } catch (e) {
    showToast('error', e?.message || 'Failed to approve')
  } finally {
    submitting.value = false
  }
}

const openRejectModal = (name) => {
  rejectTarget.value    = name
  rejectReason.value    = ''
  showRejectModal.value = true
}

const submitReject = async () => {
  if (submitting.value) return
  submitting.value = true
  try {
    await callApi(
      'sms.api.substitution.reject_substitution',
      { name: rejectTarget.value, reason: rejectReason.value },
      { method: 'POST' },
    )
    showToast('success', 'Request rejected.')
    showRejectModal.value = false
    await loadSubs()
  } catch (e) {
    showToast('error', e?.message || 'Failed to reject')
  } finally {
    submitting.value = false
  }
}

// ─── Toast ─────────────────────────────────────────────────────────────────
const showToast = (type, message) => {
  toast.value = { show: true, type, message }
  setTimeout(() => { toast.value.show = false }, 3500)
}

// ─── Lifecycle ─────────────────────────────────────────────────────────────
onMounted(loadSubs)
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from,  .modal-leave-to      { opacity: 0; transform: scale(0.97); }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from,  .toast-leave-to      { opacity: 0; transform: translateY(20px); }
</style>
