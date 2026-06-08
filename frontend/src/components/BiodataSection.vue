<script setup lang="ts">
import BiodataField from "./BiodataField.vue";

defineProps<{
  title: string;
  fields: { label: string; value: string | number | null | undefined }[];
}>();
</script>

<template>
  <div class="card p-5">
    <h4 class="font-display text-[17px] text-maroon mb-3.5">{{ title }}</h4>
    <BiodataField v-for="f in fields" :key="f.label" :label="f.label" :value="f.value" />
  </div>
</template>
