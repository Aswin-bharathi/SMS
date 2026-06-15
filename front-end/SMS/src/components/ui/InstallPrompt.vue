<template>
  <Transition name="slide-up">
    <div
      v-if="showPrompt"
      class="fixed inset-x-4 bottom-4 z-50 mx-auto max-w-md rounded-2xl border border-white/70 bg-white/95 p-4 shadow-2xl shadow-slate-900/15 backdrop-blur-xl dark:border-slate-700 dark:bg-slate-900/95 sm:right-5 sm:left-auto"
    >
      <div class="flex gap-3">
        <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-cyan-500 text-white shadow-lg shadow-primary-500/25">
          <Smartphone class="h-5 w-5" />
        </div>
        <div class="min-w-0 flex-1">
          <h2 class="text-sm font-bold text-slate-900 dark:text-white">Install EduManage</h2>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Add this student dashboard to your phone for quick access.
          </p>
          <div class="mt-3 flex items-center gap-2">
            <button class="btn-primary px-3 py-1.5 text-sm" @click="installApp">
              <Download class="h-4 w-4" />
              Install
            </button>
            <button class="btn-secondary px-3 py-1.5 text-sm" @click="dismissPrompt">
              Later
            </button>
          </div>
        </div>
        <button
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
          @click="dismissPrompt"
        >
          <X class="h-4 w-4" />
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { Download, Smartphone, X } from 'lucide-vue-next'

const showPrompt = ref(false)
const deferredPrompt = ref(null)

const dismissPrompt = () => {
  showPrompt.value = false
  localStorage.setItem('pwa-install-dismissed', String(Date.now()))
}

const installApp = async () => {
  if (!deferredPrompt.value) return
  deferredPrompt.value.prompt()
  await deferredPrompt.value.userChoice
  deferredPrompt.value = null
  showPrompt.value = false
}

const onBeforeInstallPrompt = (event) => {
  event.preventDefault()
  const dismissedAt = Number(localStorage.getItem('pwa-install-dismissed') || 0)
  const sevenDays = 7 * 24 * 60 * 60 * 1000
  if (Date.now() - dismissedAt < sevenDays) return
  deferredPrompt.value = event
  showPrompt.value = true
}

onMounted(() => {
  window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt)
})
</script>
