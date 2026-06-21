<template>
  <div
    :class="[
      'rounded-xl bg-white dark:bg-slate-800 shadow-sm',
      'ring-1 transition-all overflow-hidden',
      statusRing,
    ]"
  >
    <!-- Status bar -->
    <div :class="['h-1 w-full', statusBar]" />

    <div class="p-5">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <!-- Left: info -->
        <div class="flex-1 min-w-0 space-y-3">
          <!-- Top row: status + date -->
          <div class="flex flex-wrap items-center gap-2">
            <span :class="['inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold', statusBadge]">
              <component :is="statusIcon" class="h-3 w-3" />
              {{ sub.status }}
            </span>
            <span class="text-xs text-slate-400">
              {{ formatDate(sub.date) }}
            </span>
            <span class="text-xs text-slate-400">·</span>
            <span class="text-xs font-medium text-slate-500">
              {{ sub.hour }}
            </span>
          </div>

          <!-- Subject + batch -->
          <div>
            <p class="text-base font-bold text-slate-900 dark:text-white">
              {{ sub.subject_name || sub.subject || 'Unknown Subject' }}
            </p>
            <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
              {{ sub.batch }}
            </p>
          </div>

          <!-- Faculty swap -->
          <div class="flex items-center gap-2 text-sm">
            <div class="flex items-center gap-1.5">
              <div class="h-7 w-7 rounded-full bg-slate-200 dark:bg-slate-700
                          flex items-center justify-center text-xs font-bold
                          text-slate-600 dark:text-slate-300">
                {{ initials(sub.original_faculty_name || sub.original_faculty) }}
              </div>
              <div>
                <p class="text-xs text-slate-400 leading-none">Original</p>
                <p class="font-semibold text-slate-700 dark:text-slate-200 leading-tight">
                  {{ sub.original_faculty_name || sub.original_faculty }}
                </p>
              </div>
            </div>

            <ArrowRight class="h-4 w-4 text-slate-400 shrink-0" />

            <div class="flex items-center gap-1.5">
              <div class="h-7 w-7 rounded-full bg-primary-100 dark:bg-primary-500/20
                          flex items-center justify-center text-xs font-bold
                          text-primary-600 dark:text-primary-300">
                {{ initials(sub.substitute_faculty_name || sub.substitute_faculty) }}
              </div>
              <div>
                <p class="text-xs text-slate-400 leading-none">Substitute</p>
                <p class="font-semibold text-slate-700 dark:text-slate-200 leading-tight">
                  {{ sub.substitute_faculty_name || sub.substitute_faculty }}
                </p>
              </div>
            </div>
          </div>

          <!-- Reason -->
          <p v-if="sub.reason" class="text-xs text-slate-500 dark:text-slate-400 italic">
            "{{ sub.reason }}"
          </p>

          <!-- Requested by -->
          <p class="text-xs text-slate-400">
            Requested by
            <strong>{{ sub.requested_by_name || sub.requested_by }}</strong>
            · {{ formatDateTime(sub.creation) }}
          </p>
        </div>

        <!-- Right: actions -->
        <div
          v-if="showActions && isAdminOrHod && sub.status === 'Pending'"
          class="flex flex-col gap-2 sm:items-end"
        >
          <button
            class="inline-flex items-center gap-2 rounded-lg
                   bg-emerald-500 hover:bg-emerald-600
                   px-4 py-2 text-sm font-semibold text-white
                   shadow-sm transition-colors"
            @click="$emit('approve', sub.name)"
          >
            <Check class="h-4 w-4" />
            Approve
          </button>
          <button
            class="inline-flex items-center gap-2 rounded-lg
                   border border-red-200 dark:border-red-700
                   text-red-600 dark:text-red-400 hover:bg-red-50
                   dark:hover:bg-red-500/10
                   px-4 py-2 text-sm font-semibold transition-colors"
            @click="$emit('reject', sub.name)"
          >
            <X class="h-4 w-4" />
            Reject
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  ArrowRight, Check, CheckCircle, Clock,
  X, XCircle,
} from 'lucide-vue-next'

const props = defineProps({
  sub:          { type: Object,  required: true },
  isAdminOrHod: { type: Boolean, default: false },
  showActions:  { type: Boolean, default: true },
})

defineEmits(['approve', 'reject'])

const statusConfig = {
  Pending:  {
    ring:   'ring-amber-200 dark:ring-amber-700/50',
    bar:    'bg-amber-400',
    badge:  'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300',
    icon:   Clock,
  },
  Approved: {
    ring:   'ring-emerald-200 dark:ring-emerald-700/50',
    bar:    'bg-emerald-400',
    badge:  'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300',
    icon:   CheckCircle,
  },
  Rejected: {
    ring:   'ring-red-200 dark:ring-red-700/50',
    bar:    'bg-red-400',
    badge:  'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300',
    icon:   XCircle,
  },
}

const cfg        = computed(() => statusConfig[props.sub.status] || statusConfig.Pending)
const statusRing = computed(() => cfg.value.ring)
const statusBar  = computed(() => cfg.value.bar)
const statusBadge = computed(() => cfg.value.badge)
const statusIcon  = computed(() => cfg.value.icon)

const initials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

const formatDate = (d) => {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('en-IN', {
    weekday: 'short', day: 'numeric', month: 'short',
  })
}

const formatDateTime = (dt) => {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}
</script>
