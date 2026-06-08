<script setup lang="ts">
import MotifMark from "./MotifMark.vue";
withDefaults(defineProps<{ light?: boolean }>(), { light: false });
</script>

<template>
  <div class="flex items-center gap-3 justify-center my-1">
    <span
      class="h-px flex-1"
      :style="{
        background: light
          ? 'rgba(232,212,154,.4)'
          : 'linear-gradient(90deg,transparent,#E8D49A)',
      }"
    />
    <MotifMark :size="22" :color="light ? '#E8D49A' : '#C8A248'" />
    <span
      class="h-px flex-1"
      :style="{
        background: light
          ? 'rgba(232,212,154,.4)'
          : 'linear-gradient(270deg,transparent,#E8D49A)',
      }"
    />
  </div>
</template>
