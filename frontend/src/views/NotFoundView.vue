<script setup lang="ts">
import { useRouter } from "vue-router";
import StateNotice from "@/components/StateNotice.vue";

const router = useRouter();
</script>

<template>
  <StateNotice
    eyebrow="Error 404"
    title="Page not found"
    message="The page you are looking for doesn’t exist or may have been moved."
    action-label="Back to home"
    secondary-label="Go to matchmaking"
    @action="router.push({ name: 'home' })"
    @secondary="router.push({ name: 'dashboard' })"
  />
</template>
