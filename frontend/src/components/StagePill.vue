<script setup lang="ts">
import type { JourneyStage } from "@/types/models";
import { stageColor, stageLabel } from "@/lib/format";

withDefaults(defineProps<{ stage: JourneyStage | null; small?: boolean }>(), {
  small: false,
});
</script>

<template>
  <span
    class="pill"
    :class="small ? 'text-[11px] px-2.5 py-[3px]' : 'text-xs'"
    :style="{ background: stageColor(stage) }"
  >
    <span class="w-[5px] h-[5px] rounded-full bg-white/80" />
    {{ stageLabel(stage) }}
  </span>
</template>
