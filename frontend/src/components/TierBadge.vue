<script setup lang="ts">
import type { MatchTier } from "@/types/models";
import { tierColor, tierLabel } from "@/lib/format";

defineProps<{ tier: MatchTier }>();
</script>

<template>
  <span
    class="inline-flex font-sans text-[11px] font-semibold tracking-[0.05em] uppercase text-white px-2.5 py-[3px] rounded-full"
    :style="{ background: tierColor(tier) }"
  >
    {{ tierLabel(tier) }}
  </span>
</template>
