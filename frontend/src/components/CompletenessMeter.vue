<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ filled: number; total: number }>();
const pct = computed(() => (props.total ? Math.round((props.filled / props.total) * 100) : 0));
</script>

<template>
  <div class="card !rounded-md px-4 py-3 mb-[18px] flex items-center gap-3.5 flex-wrap">
    <span class="font-sans text-xs tracking-[0.08em] uppercase text-maroon font-semibold">
      Profile completeness
    </span>
    <div class="flex-1 min-w-[120px] h-2 bg-card-warm rounded-full overflow-hidden border border-line">
      <div
        class="h-full"
        :style="{ width: `${pct}%`, background: 'linear-gradient(90deg,#E08A1E,#C8A248)' }"
      />
    </div>
    <span class="font-display text-lg text-maroon">{{ pct }}%</span>
    <span class="font-sans text-xs text-muted">{{ filled }}/{{ total }} fields</span>
  </div>
</template>
