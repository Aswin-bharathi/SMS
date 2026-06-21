<template>
  <transition name="modal">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="$emit('close')"
    >
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" />

      <div class="relative w-full max-w-lg rounded-2xl bg-white dark:bg-slate-800
                  shadow-2xl ring-1 ring-slate-200 dark:ring-slate-700">
        <!-- Header -->
        <div class="flex items-center justify-between border-b
                    border-slate-100 dark:border-slate-700 px-6 py-4">
          <h2 class="text-lg font-bold text-slate-900 dark:text-white">
            {{ isEdit ? 'Edit Subject' : 'Add New Subject' }}
          </h2>
          <button
            class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
            @click="$emit('close')"
          >
            <X class="h-5 w-5" />
          </button>
        </div>

        <!-- Body -->
        <div class="px-6 py-5 space-y-4">
          <!-- Subject code -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Subject Code *
              <span class="text-xs font-normal text-slate-400">(e.g. ADA, DBMS-LAB)</span>
            </label>
            <input
              v-model="form.subject_code"
              type="text"
              :disabled="isEdit"
              placeholder="ADA"
              class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                     bg-white dark:bg-slate-900 px-3 py-2.5 text-sm uppercase font-mono
                     text-slate-900 dark:text-white
                     focus:outline-none focus:ring-2 focus:ring-primary-500
                     disabled:opacity-60 disabled:cursor-not-allowed"
            />
          </div>

          <!-- Subject name -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Subject Name *
            </label>
            <input
              v-model="form.subject_name"
              type="text"
              placeholder="Algorithm Design & Analysis"
              class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                     bg-white dark:bg-slate-900 px-3 py-2.5 text-sm
                     text-slate-900 dark:text-white
                     focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <!-- Dept + Year -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Department
              </label>
              <select
                v-model="form.department"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                       bg-white dark:bg-slate-900 px-3 py-2.5 text-sm
                       text-slate-900 dark:text-white
                       focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">— Select —</option>
                <option v-for="d in departments" :key="d.name" :value="d.name">
                  {{ d.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Year Level
              </label>
              <select
                v-model="form.year_level"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                       bg-white dark:bg-slate-900 px-3 py-2.5 text-sm
                       text-slate-900 dark:text-white
                       focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">— Any —</option>
                <option v-for="y in yearLevels" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
          </div>

          <!-- Credits + flags -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Credits
              </label>
              <input
                v-model.number="form.credits"
                type="number"
                min="0"
                max="10"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                       bg-white dark:bg-slate-900 px-3 py-2.5 text-sm
                       text-slate-900 dark:text-white
                       focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div class="space-y-2 pt-6">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="form.is_lab"
                  type="checkbox"
                  class="h-4 w-4 rounded border-slate-300 text-primary-500
                         focus:ring-primary-500"
                />
                <span class="text-sm text-slate-700 dark:text-slate-200">
                  This is a Lab subject
                </span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="form.is_active"
                  type="checkbox"
                  class="h-4 w-4 rounded border-slate-300 text-primary-500
                         focus:ring-primary-500"
                />
                <span class="text-sm text-slate-700 dark:text-slate-200">
                  Active
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between gap-3 border-t
                    border-slate-100 dark:border-slate-700 px-6 py-4">
          <!-- Delete button (edit mode only) -->
          <button
            v-if="isEdit"
            class="inline-flex items-center gap-1.5 rounded-lg text-red-600 dark:text-red-400
                   hover:bg-red-50 dark:hover:bg-red-500/10 px-3 py-2 text-sm font-medium"
            @click="$emit('delete', form)"
          >
            <Trash2 class="h-4 w-4" />
            Delete
          </button>
          <div v-else></div>

          <div class="flex items-center gap-2">
            <button
              class="rounded-lg border border-slate-200 dark:border-slate-700
                     px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300
                     hover:bg-slate-50 dark:hover:bg-slate-700"
              @click="$emit('close')"
            >
              Cancel
            </button>
            <button
              :disabled="!canSubmit || saving"
              class="inline-flex items-center gap-2 rounded-lg
                     bg-gradient-to-r from-primary-500 to-cyan-500 px-5 py-2
                     text-sm font-semibold text-white shadow-md
                     disabled:opacity-50 disabled:cursor-not-allowed"
              @click="$emit('save', form)"
            >
              <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
              <Save v-else class="h-4 w-4" />
              {{ saving ? 'Saving…' : (isEdit ? 'Update' : 'Create') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Loader2, Save, Trash2, X } from 'lucide-vue-next'

const props = defineProps({
  show:        { type: Boolean, default: false },
  subject:     { type: Object,  default: null },   // null = create mode
  departments: { type: Array,   default: () => [] },
  saving:      { type: Boolean, default: false },
})
defineEmits(['close', 'save', 'delete'])

const yearLevels = ['I UG', 'II UG', 'III UG', 'IV UG', 'I PG', 'II PG']

const blank = {
  name:         null,
  subject_code: '',
  subject_name: '',
  department:   '',
  year_level:   '',
  credits:      3,
  is_lab:       false,
  is_active:    true,
}

const form = ref({ ...blank })

const isEdit = computed(() => !!props.subject?.name)

const canSubmit = computed(() =>
  form.value.subject_code?.trim() && form.value.subject_name?.trim()
)

// Reset / populate form when subject changes
watch(() => props.subject, (newSub) => {
  if (newSub) {
    form.value = {
      ...blank,
      ...newSub,
      is_lab:    !!newSub.is_lab,
      is_active: !!newSub.is_active,
    }
  } else {
    form.value = { ...blank }
  }
}, { immediate: true })

watch(() => props.show, (s) => {
  if (!s) form.value = { ...blank }
})
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from,  .modal-leave-to      { opacity: 0; transform: scale(0.97); }
</style>
