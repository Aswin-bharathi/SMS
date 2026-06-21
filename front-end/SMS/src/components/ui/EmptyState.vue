<template>
  <div class="rounded-xl bg-white dark:bg-slate-800 p-12 text-center
              shadow-sm ring-1 ring-slate-200 dark:ring-slate-700">
    <component
      :is="iconComponent"
      class="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-3"
    />
    <h3 class="text-base font-semibold text-slate-700 dark:text-slate-300">
      {{ title }}
    </h3>
    <p class="text-sm text-slate-400 mt-1">{{ message }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  CalendarOff, CheckCircle, RefreshCcw, AlertCircle,
} from 'lucide-vue-next'

const props = defineProps({
  icon:    { type: String, default: 'CalendarOff' },
  title:   { type: String, required: true },
  message: { type: String, default: '' },
})

const iconMap = { CalendarOff, CheckCircle, RefreshCcw, AlertCircle }
const iconComponent = computed(() => iconMap[props.icon] || CalendarOff)
</script>
