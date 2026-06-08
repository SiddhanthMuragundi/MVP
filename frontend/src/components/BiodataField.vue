<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ label: string; value: string | number | null | undefined }>();

const isEmpty = computed(
  () => props.value === null || props.value === undefined || props.value === "",
);
</script>

<template>
  <div class="mb-3.5">
    <div class="field-label">{{ label }}</div>
    <div
      class="font-sans text-[15px]"
      :class="isEmpty ? 'text-[#C2B29C] italic' : 'text-maroon-ink'"
    >
      {{ isEmpty ? "Not provided" : value }}
    </div>
  </div>
</template>
