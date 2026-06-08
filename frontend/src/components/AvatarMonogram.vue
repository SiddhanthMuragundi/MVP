<script setup lang="ts">
import { ref } from "vue";

const props = withDefaults(
  defineProps<{ name: string; photoUrl?: string; size?: number }>(),
  { size: 46, photoUrl: "" },
);

const failed = ref(false);
const initial = props.name?.trim()?.[0]?.toUpperCase() ?? "?";
</script>

<template>
  <div
    class="rounded-full bg-gradient-to-b from-maroon to-maroon-deep border-2 border-gold grid place-items-center overflow-hidden shrink-0"
    :style="{ width: `${size}px`, height: `${size}px` }"
  >
    <img
      v-if="photoUrl && !failed"
      :src="photoUrl"
      :alt="name"
      class="w-full h-full object-cover"
      @error="failed = true"
    />
    <span
      v-else
      class="font-display text-gold-soft"
      :style="{ fontSize: `${Math.round(size * 0.42)}px` }"
      >{{ initial }}</span
    >
  </div>
</template>
