<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import MotifMark from "@/components/MotifMark.vue";
import DividerMotif from "@/components/DividerMotif.vue";

const auth = useAuthStore();
const router = useRouter();

const cards = [
  {
    title: "Matchmaking",
    body: "Manage your clients, review verified profiles, and send curated introductions.",
    to: "dashboard",
    cta: "Open the studio",
  },
  {
    title: "About Us",
    body: "Learn how Saathiya blends human matchmaking with thoughtful technology.",
    to: "about",
    cta: "Read more",
  },
];
</script>

<template>
  <div class="max-w-[900px] mx-auto">
    <section class="text-center py-8 sm:py-12">
      <div class="flex justify-center mb-3"><MotifMark :size="46" /></div>
      <div class="eyebrow mb-2">Saathiya</div>
      <h1 class="font-display text-[34px] sm:text-[46px] text-maroon leading-tight m-0">
        Welcome back, {{ auth.user?.display_name }}
      </h1>
      <p class="font-serifItalic italic text-lg sm:text-xl text-muted mt-2">
        Where thoughtful journeys to companionship begin.
      </p>
      <button class="btn-primary mt-6 px-8" @click="router.push({ name: 'dashboard' })">
        Go to Matchmaking
      </button>
    </section>

    <div class="my-4"><DividerMotif /></div>

    <section class="grid grid-cols-1 sm:grid-cols-2 gap-5 mt-6">
      <button
        v-for="c in cards"
        :key="c.to"
        class="card text-left p-6 cursor-pointer transition hover:-translate-y-[3px] hover:shadow-cardHover"
        @click="router.push({ name: c.to })"
      >
        <h3 class="font-display text-2xl text-maroon mb-2">{{ c.title }}</h3>
        <p class="font-sans text-sm text-maroon-ink/80 leading-relaxed mb-4">{{ c.body }}</p>
        <span class="font-sans text-[13px] font-semibold text-marigold">{{ c.cta }} ›</span>
      </button>
    </section>
  </div>
</template>
