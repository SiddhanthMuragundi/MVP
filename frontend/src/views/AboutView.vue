<script setup lang="ts">
import MotifMark from "@/components/MotifMark.vue";
import DividerMotif from "@/components/DividerMotif.vue";

const values = [
  {
    title: "Verified profiles",
    body: "Every client is personally verified before they enter the matchmaking pool, so introductions are built on trust.",
  },
  {
    title: "Human matchmakers",
    body: "Real matchmakers guide each journey, supported by tools that surface compatible matches and draft thoughtful introductions.",
  },
  {
    title: "Compatibility first",
    body: "Our matching looks beyond the surface, weighing values, lifestyle, family, and intent to suggest meaningful connections.",
  },
];
</script>

<template>
  <div class="max-w-[820px] mx-auto">
    <section class="text-center py-8">
      <div class="flex justify-center mb-3"><MotifMark :size="42" /></div>
      <div class="eyebrow mb-2">About Us</div>
      <h1 class="font-display text-[32px] sm:text-[42px] text-maroon leading-tight m-0">Saathiya</h1>
      <p class="font-serifItalic italic text-lg text-muted mt-2">Matchmaking, reimagined with care.</p>
    </section>

    <div class="my-2"><DividerMotif /></div>

    <section class="card p-6 sm:p-8 mt-6">
      <p class="font-sans text-[15px] text-maroon-ink/90 leading-relaxed mb-4">
        Saathiya is a concierge matchmaking service that pairs the warmth of a personal matchmaker
        with technology that helps them work at their best. We believe finding a life partner deserves
        more than endless swiping, so we focus on verified profiles, genuine compatibility, and
        introductions made with intention.
      </p>
      <p class="font-sans text-[15px] text-maroon-ink/90 leading-relaxed">
        Behind the scenes, our matchmakers manage each client's journey, review compatible candidates
        from a curated pool, and reach out with personalised introductions, so every connection feels
        considered rather than automated.
      </p>
    </section>

    <section class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
      <div v-for="v in values" :key="v.title" class="card p-5">
        <h3 class="font-display text-lg text-maroon mb-2">{{ v.title }}</h3>
        <p class="font-sans text-[13px] text-maroon-ink/80 leading-relaxed">{{ v.body }}</p>
      </div>
    </section>
  </div>
</template>
