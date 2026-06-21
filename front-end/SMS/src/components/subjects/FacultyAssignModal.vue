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
          <div>
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">
              Manage Faculty
            </h2>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {{ subject?.subject_code }} · {{ subject?.subject_name }}
            </p>
          </div>
          <button
            class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
            @click="$emit('close')"
          >
            <X class="h-5 w-5" />
          </button>
        </div>

        <!-- Body -->
        <div class="px-6 py-5 space-y-4">
          <!-- Current assignments -->
          <div>
            <p class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Currently assigned ({{ currentMappings.length }}/2)
            </p>
            <div v-if="currentMappings.length" class="space-y-2">
              <div
                v-for="m in currentMappings"
                :key="m.name"
                class="flex items-center gap-2 rounded-lg bg-slate-50 dark:bg-slate-700/50
                       px-3 py-2"
              >
                <div
                  :class="[
                    'h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0',
                    m.is_primary
                      ? 'bg-gradient-to-br from-primary-500 to-cyan-500 text-white'
                      : 'bg-slate-200 dark:bg-slate-600 text-slate-700 dark:text-slate-200',
                  ]"
                >
                  {{ initials(m.faculty_name) }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-semibold text-slate-900 dark:text-white truncate">
                    {{ m.faculty_name }}
                  </p>
                  <p class="text-xs text-slate-500 truncate">{{ m.faculty }}</p>
                </div>
                <span
                  v-if="m.is_primary"
                  class="inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-[10px] font-bold
                         bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-300"
                >
                  PRIMARY
                </span>
                <button
                  v-else
                  :disabled="busy"
                  class="text-[10px] font-bold text-slate-500 hover:text-primary-600 px-2"
                  @click="$emit('set-primary', m.name)"
                >
                  Make Primary
                </button>
                <button
                  :disabled="busy"
                  class="rounded-lg p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10"
                  @click="$emit('remove', m.name)"
                >
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
            </div>
            <p v-else class="text-sm text-slate-400 italic py-2">
              No faculty assigned yet.
            </p>
          </div>

          <!-- Add new (if under limit) -->
          <div
            v-if="currentMappings.length < 2"
            class="rounded-lg border border-dashed border-slate-300 dark:border-slate-600 p-4"
          >
            <p class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Add Faculty
            </p>

            <div v-if="loadingFaculty"
                 class="flex items-center gap-2 text-sm text-slate-400 py-2">
              <Loader2 class="h-4 w-4 animate-spin" />
              Loading available faculty…
            </div>

            <div v-else class="space-y-2">
              <select
                v-model="selectedFaculty"
                class="w-full rounded-lg border border-slate-200 dark:border-slate-700
                       bg-white dark:bg-slate-900 px-3 py-2.5 text-sm
                       text-slate-900 dark:text-white
                       focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">— Select faculty —</option>
                <option v-for="f in assignableFaculty" :key="f.email" :value="f.email">
                  {{ f.full_name || f.email }}
                </option>
              </select>

              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="addAsPrimary"
                  type="checkbox"
                  class="h-4 w-4 rounded border-slate-300 text-primary-500 focus:ring-primary-500"
                />
                <span class="text-xs text-slate-700 dark:text-slate-200">
                  Set as Primary
                  <span v-if="hasPrimary" class="text-amber-600 dark:text-amber-400 ml-1">
                    (will replace current primary)
                  </span>
                </span>
              </label>

              <button
                :disabled="!selectedFaculty || busy"
                class="w-full inline-flex items-center justify-center gap-2 rounded-lg
                       bg-gradient-to-r from-primary-500 to-cyan-500 px-4 py-2
                       text-sm font-semibold text-white shadow-md
                       disabled:opacity-50 disabled:cursor-not-allowed"
                @click="handleAdd"
              >
                <Loader2 v-if="busy" class="h-4 w-4 animate-spin" />
                <Plus v-else class="h-4 w-4" />
                Add Faculty
              </button>
            </div>
          </div>

          <div
            v-else
            class="rounded-lg bg-amber-50 dark:bg-amber-500/10 border border-amber-200
                   dark:border-amber-700/50 p-3 text-xs text-amber-700 dark:text-amber-300
                   flex items-center gap-2"
          >
            <AlertCircle class="h-4 w-4 shrink-0" />
            Maximum 2 faculty per subject. Remove one to add another.
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-end border-t
                    border-slate-100 dark:border-slate-700 px-6 py-4">
          <button
            class="rounded-lg border border-slate-200 dark:border-slate-700
                   px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300
                   hover:bg-slate-50 dark:hover:bg-slate-700"
            @click="$emit('close')"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { AlertCircle, Loader2, Plus, Trash2, X } from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

const props = defineProps({
  show:            { type: Boolean, default: false },
  subject:         { type: Object,  default: null },
  currentMappings: { type: Array,   default: () => [] },
  busy:            { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'add', 'remove', 'set-primary'])

const { callApi } = useApi()

const assignableFaculty = ref([])
const loadingFaculty    = ref(false)
const selectedFaculty   = ref('')
const addAsPrimary      = ref(false)

const hasPrimary = computed(() => props.currentMappings.some(m => m.is_primary))

const loadAssignable = async () => {
  if (!props.subject?.name) return
  loadingFaculty.value = true
  try {
    const res = await callApi('sms.api.subject.get_assignable_faculty', {
      exclude_subject: props.subject.name,
    })
    assignableFaculty.value = res || []
  } catch (e) {
    console.error(e)
  } finally {
    loadingFaculty.value = false
  }
}

const initials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

const handleAdd = () => {
  if (!selectedFaculty.value) return
  emit('add', {
    faculty:    selectedFaculty.value,
    is_primary: addAsPrimary.value ? 1 : 0,
  })
  // Reset
  selectedFaculty.value = ''
  addAsPrimary.value    = false
}

// Reload when subject or mappings change
watch(() => [props.show, props.subject?.name, props.currentMappings.length],
  ([show]) => {
    if (show) loadAssignable()
  }
)

onMounted(loadAssignable)
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from,  .modal-leave-to      { opacity: 0; transform: scale(0.97); }
</style>
