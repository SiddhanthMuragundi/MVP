<script setup lang="ts">
import { computed, ref } from "vue";
import type { Match } from "@/types/models";
import { tierColor } from "@/lib/format";
import AvatarMonogram from "./AvatarMonogram.vue";
import TierBadge from "./TierBadge.vue";
import ProfileModal from "./ProfileModal.vue";

const props = defineProps<{ match: Match }>();
const emit = defineEmits<{
  send: [match: Match];
  shortlist: [match: Match];
  unshortlist: [match: Match];
  outcome: [payload: { match: Match; outcome: string }];
}>();
const c = props.match.candidate;
const showProfile = ref(false);

const SENT = ["sent", "accepted", "declined", "no_response", "withdrawn"];
const isSent = computed(() => SENT.includes(props.match.status));
const isShortlisted = computed(() => props.match.status === "shortlisted");
const outcomeValue = computed(() =>
  ["accepted", "declined", "no_response"].includes(props.match.status) ? props.match.status : "",
);
function onOutcome(e: Event) {
  const v = (e.target as HTMLSelectElement).value;
  if (v) emit("outcome", { match: props.match, outcome: v });
}
function toggleShortlist() {
  if (isShortlisted.value) emit("unshortlist", props.match);
  else emit("shortlist", props.match);
}
</script>

<template>
  <div
    class="bg-card border border-line rounded-card p-[18px] flex flex-col shadow-card"
    :style="{ borderTopColor: tierColor(match.tier), borderTopWidth: '3px' }"
  >
    <div class="flex justify-between items-start gap-2.5">
      <div class="flex gap-[11px] items-center min-w-0">
        <AvatarMonogram :name="c.first_name" :photo-url="c.photo_url" :size="46" />
        <div class="min-w-0">
          <button
            class="font-display text-[18px] text-maroon-ink leading-tight truncate text-left hover:text-maroon hover:underline cursor-pointer bg-transparent border-none p-0"
            @click="showProfile = true"
          >
            {{ c.first_name }} {{ c.last_name }}
          </button>
          <div class="font-sans text-[12.5px] text-muted">{{ c.age }} · {{ c.city }}</div>
          <div class="font-sans text-[12.5px] text-muted truncate">{{ c.designation }}</div>
        </div>
      </div>
      <div
        class="w-[50px] h-[50px] rounded-full grid place-items-center shrink-0 bg-card-warm"
        :style="{ border: `2px solid ${tierColor(match.tier)}` }"
      >
        <div class="font-display text-xl leading-none" :style="{ color: tierColor(match.tier) }">
          {{ Math.round(match.score) }}
        </div>
        <div class="font-sans text-[8px] tracking-[0.1em] text-muted">SCORE</div>
      </div>
    </div>

    <div class="mt-3"><TierBadge :tier="match.tier" /></div>

    <div class="my-3 flex flex-wrap gap-1.5">
      <span
        v-for="r in match.reasons"
        :key="r"
        class="font-sans text-[11.5px] text-maroon bg-card-warm border border-gold-soft px-2.5 py-[3px] rounded-sm"
        >{{ r }}</span
      >
    </div>

    <div
      v-if="match.ai_explanation"
      class="bg-card-warm rounded-r-sm px-3 py-2.5 mb-3.5 flex-1"
      style="border-left: 3px solid #e08a1e"
    >
      <div class="font-sans text-[9.5px] tracking-[0.14em] uppercase text-marigold mb-0.5">
        Matchmaker's note
      </div>
      <p class="font-serifItalic italic text-[15px] text-maroon-ink leading-snug m-0">
        {{ match.ai_explanation }}
      </p>
    </div>

    <button class="btn-ghost text-left text-[12.5px] mb-2.5" @click="showProfile = true">View full profile ›</button>

    <!-- Before sending: shortlist (reversible) + send. After sending: outcome tracking. -->
    <div v-if="!isSent" class="flex gap-2 mt-auto">
      <button
        class="font-sans text-[13px] font-medium px-3 py-2.5 rounded-sm cursor-pointer border"
        :class="isShortlisted
          ? 'text-gold border-gold bg-gold/10'
          : 'text-maroon border-maroon/30 bg-transparent hover:bg-maroon/5'"
        @click="toggleShortlist"
      >
        {{ isShortlisted ? "★ Shortlisted" : "☆ Shortlist" }}
      </button>
      <button class="btn-primary flex-1 !py-2.5" @click="emit('send', match)">Send Match ❯</button>
    </div>

    <div v-else class="mt-auto">
      <div class="flex items-center gap-2">
        <span class="font-sans text-[11.5px] font-semibold uppercase tracking-[0.06em] text-sage bg-sage/10 border border-sage/30 px-2.5 py-[7px] rounded-sm whitespace-nowrap">
          ✓ Sent
        </span>
        <select
          :value="outcomeValue"
          class="input !w-auto flex-1 !py-2 text-[13px]"
          @change="onOutcome"
        >
          <option value="">Awaiting response…</option>
          <option value="accepted">Interested</option>
          <option value="declined">Not interested</option>
          <option value="no_response">No response</option>
        </select>
        <button class="btn-ghost text-[12px] shrink-0" @click="emit('send', match)">Resend</button>
      </div>
    </div>

    <ProfileModal v-if="showProfile" :profile="c" @close="showProfile = false" />
  </div>
</template>
