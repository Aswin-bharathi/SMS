<template>
  <div :class="['card', className]">
    <slot />
  </div>
</template>

<script setup>
defineProps({ className: String })
</script>
