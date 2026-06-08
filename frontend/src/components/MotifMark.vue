<script setup lang="ts">
withDefaults(defineProps<{ size?: number; color?: string }>(), {
  size: 26,
  color: "#C8A248",
});
const angles = [0, 45, 90, 135, 180, 225, 270, 315];
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 40 40" aria-hidden="true">
    <g fill="none" :stroke="color" stroke-width="1.2">
      <circle cx="20" cy="20" r="3.2" :fill="color" stroke="none" />
      <path
        v-for="a in angles"
        :key="a"
        d="M20 16 C23 11 23 6 20 2 C17 6 17 11 20 16Z"
        :transform="`rotate(${a} 20 20)`"
      />
      <circle cx="20" cy="20" r="12.5" stroke-dasharray="1.5 3" />
    </g>
  </svg>
</template>
