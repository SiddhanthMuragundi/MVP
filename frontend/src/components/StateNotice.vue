<script setup lang="ts">
/**
 * Branded, centered notice for empty / error / not-found states.
 * Keeps "nothing to show" moments on-brand instead of leaving a blank screen.
 */
defineProps<{
  eyebrow?: string;
  title: string;
  message?: string;
  actionLabel?: string;
  secondaryLabel?: string;
}>();

defineEmits<{ (e: "action"): void; (e: "secondary"): void }>();

import MotifMark from "@/components/MotifMark.vue";
</script>

<template>
  <div class="py-16 sm:py-20 text-center">
    <div class="flex justify-center mb-4"><MotifMark :size="40" /></div>
    <div v-if="eyebrow" class="eyebrow mb-2">{{ eyebrow }}</div>
    <h2 class="font-display text-2xl sm:text-[28px] text-maroon mb-2">{{ title }}</h2>
    <p v-if="message" class="font-serifItalic italic text-muted text-lg max-w-md mx-auto mb-6">
      {{ message }}
    </p>
    <div class="flex flex-wrap gap-3 justify-center">
      <button v-if="actionLabel" class="btn-primary" @click="$emit('action')">{{ actionLabel }}</button>
      <button v-if="secondaryLabel" class="btn-ghost" @click="$emit('secondary')">{{ secondaryLabel }}</button>
    </div>
  </div>
</template>
