<script setup lang="ts">
import { useToast } from "@/composables/useToast";
const { toasts, dismiss } = useToast();
</script>

<template>
  <div class="fixed bottom-5 left-1/2 -translate-x-1/2 z-[100] flex flex-col gap-2 items-center">
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="font-sans text-sm text-white px-4 py-2.5 rounded-md shadow-modal cursor-pointer"
        :class="t.kind === 'error' ? 'bg-maroon' : 'bg-sage'"
        @click="dismiss(t.id)"
      >
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
