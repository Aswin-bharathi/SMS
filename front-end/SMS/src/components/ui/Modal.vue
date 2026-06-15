<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="$emit('close')"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />

        <!-- Modal Panel -->
        <div
          :class="[
            'relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl',
            'border border-gray-100 dark:border-gray-700 w-full',
            sizeClass, 'max-h-[90vh] flex flex-col'
          ]"
        >
          <!-- Header -->
          <div class="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-800 dark:text-white">{{ title }}</h3>
            <button
              @click="$emit('close')"
              class="w-8 h-8 flex items-center justify-center rounded-xl
                     hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <X class="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </button>
          </div>

          <!-- Body -->
          <div class="flex-1 overflow-y-auto p-6">
            <slot />
          </div>

          <!-- Footer -->
          <div
            v-if="$slots.footer"
            class="p-6 border-t border-gray-100 dark:border-gray-700 flex items-center justify-end gap-3"
          >
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  title: String,
  size: { type: String, default: 'md' }
})

defineEmits(['close'])

const sizeClass = computed(() => ({
  sm: 'max-w-md',
  md: 'max-w-xl',
  lg: 'max-w-3xl',
  xl: 'max-w-5xl',
}[props.size]))
</script>

<style scoped>
.modal-enter-active, .modal-leave-active {
  transition: all 0.3s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
