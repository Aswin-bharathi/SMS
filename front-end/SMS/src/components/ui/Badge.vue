<template>
  <span :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', colorClass]">
    <slot />
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'default'
  }
})

const colorMap = {
  'Active':         'bg-green-100  dark:bg-green-900/30  text-green-700  dark:text-green-400',
  'Inactive':       'bg-gray-100   dark:bg-gray-700      text-gray-600   dark:text-gray-400',
  'Graduated':      'bg-blue-100   dark:bg-blue-900/30   text-blue-700   dark:text-blue-400',
  'Dropped':        'bg-red-100    dark:bg-red-900/30    text-red-700    dark:text-red-400',
  'Present':        'bg-green-100  dark:bg-green-900/30  text-green-700  dark:text-green-400',
  'Absent':         'bg-red-100    dark:bg-red-900/30    text-red-700    dark:text-red-400',
  'Late':           'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
  'Excused':        'bg-blue-100   dark:bg-blue-900/30   text-blue-700   dark:text-blue-400',
  'Paid':           'bg-green-100  dark:bg-green-900/30  text-green-700  dark:text-green-400',
  'Unpaid':         'bg-red-100    dark:bg-red-900/30    text-red-700    dark:text-red-400',
  'Overdue':        'bg-red-100    dark:bg-red-900/30    text-red-700    dark:text-red-400',
  'Partially Paid': 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
  'Pass':           'bg-green-100  dark:bg-green-900/30  text-green-700  dark:text-green-400',
  'Fail':           'bg-red-100    dark:bg-red-900/30    text-red-700    dark:text-red-400',
  'default':        'bg-gray-100   dark:bg-gray-700      text-gray-600   dark:text-gray-400',
}

const colorClass = computed(() => {
  return colorMap[props.variant] || colorMap['default']
})
</script>
