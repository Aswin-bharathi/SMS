<template>
  <div
    :class="[
      'rounded-xl bg-white dark:bg-slate-800 shadow-sm ring-1 overflow-hidden transition-all',
      subject.is_active
        ? 'ring-slate-200 dark:ring-slate-700 hover:shadow-md hover:ring-primary-300'
        : 'ring-slate-200 dark:ring-slate-700/50 opacity-60',
    ]"
  >
    <!-- Top accent bar -->
    <div
      :class="[
        'h-1 w-full',
        subject.is_lab
          ? 'bg-gradient-to-r from-purple-400 to-pink-400'
          : 'bg-gradient-to-r from-primary-400 to-cyan-400',
      ]"
    />

    <div class="p-5 space-y-3">
      <!-- Header: code + name -->
      <div>
        <div class="flex items-start justify-between gap-2">
          <p class="text-xs font-mono font-bold text-slate-400 dark:text-slate-500 tracking-wider">
            {{ subject.subject_code }}
          </p>
          <span
            v-if="subject.is_lab"
            class="inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-[10px] font-bold
                   bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-300"
          >
            🧪 LAB
          </span>
          <span
            v-if="!subject.is_active"
            class="inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-[10px] font-bold
                   bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
          >
            INACTIVE
          </span>
        </div>
        <h3 class="text-base font-bold text-slate-900 dark:text-white mt-1 leading-tight">
          {{ subject.subject_name }}
        </h3>
      </div>

      <!-- Meta -->
      <div class="flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <span v-if="subject.department" class="inline-flex items-center gap-1">
          <Building2 class="h-3 w-3" />
          {{ shortDept(subject.department) }}
        </span>
        <span v-if="subject.year_level" class="inline-flex items-center gap-1">
          <GraduationCap class="h-3 w-3" />
          {{ subject.year_level }}
        </span>
        <span class="inline-flex items-center gap-1">
          <Award class="h-3 w-3" />
          {{ subject.credits || 0 }} cr
        </span>
      </div>

      <!-- Faculty list -->
      <div class="space-y-1.5 min-h-[3rem]">
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
          Faculty ({{ subject.faculty_list?.length || 0 }}/2)
        </p>
        <template v-if="subject.faculty_list?.length">
          <div
            v-for="f in subject.faculty_list"
            :key="f.email"
            class="flex items-center gap-1.5 text-xs"
          >
            <div
              :class="[
                'h-5 w-5 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0',
                f.is_primary
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-300'
                  : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
              ]"
            >
              {{ initials(f.name) }}
            </div>
            <span class="text-slate-700 dark:text-slate-200 truncate flex-1">
              {{ f.name }}
            </span>
            <span
              v-if="f.is_primary"
              class="text-[9px] font-bold text-primary-500 dark:text-primary-400"
            >
              PRIMARY
            </span>
          </div>
        </template>
        <p v-else class="text-xs text-amber-600 dark:text-amber-400 italic">
          ⚠ No faculty assigned
        </p>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-700">
        <button
          class="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg
                 border border-slate-200 dark:border-slate-700 px-3 py-1.5 text-xs font-semibold
                 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700"
          @click="$emit('edit', subject)"
        >
          <Edit3 class="h-3.5 w-3.5" />
          Edit
        </button>
        <button
          class="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg
                 bg-primary-50 dark:bg-primary-500/10 px-3 py-1.5 text-xs font-semibold
                 text-primary-700 dark:text-primary-300
                 hover:bg-primary-100 dark:hover:bg-primary-500/20"
          @click="$emit('manage-faculty', subject)"
        >
          <Users class="h-3.5 w-3.5" />
          Faculty
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Award, Building2, Edit3, GraduationCap, Users,
} from 'lucide-vue-next'

defineProps({
  subject: { type: Object, required: true },
})
defineEmits(['edit', 'manage-faculty'])

const initials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

const shortDept = (d) => {
  if (!d) return ''
  return d.replace('Computer Science', 'CS')
          .replace('Mechanical Engineering', 'ME')
          .replace('Electrical Engineering', 'EE')
          .replace('Civil Engineering', 'CE')
          .replace('Business Administration', 'BBA')
          .replace('Commerce', 'COM')
          .replace('Mathematics', 'MATH')
}
</script>
