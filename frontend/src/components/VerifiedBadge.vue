<script setup lang="ts">
defineProps<{ verified: boolean }>();
</script>

<template>
  <span
    v-if="verified"
    class="inline-flex items-center gap-1 font-sans text-[11px] font-semibold tracking-[0.04em] text-white bg-sage px-2 py-[2px] rounded-full align-middle"
  >
    ✓ Verified
  </span>
</template>
