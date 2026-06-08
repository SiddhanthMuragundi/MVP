<script setup lang="ts">
import { useRouter } from "vue-router";
import type { CustomerListItem } from "@/types/models";
import { humanize } from "@/lib/format";
import AvatarMonogram from "./AvatarMonogram.vue";
import StagePill from "./StagePill.vue";
import VerifiedBadge from "./VerifiedBadge.vue";

const props = defineProps<{ customer: CustomerListItem }>();
const router = useRouter();
</script>

<template>
  <button
    class="card text-left cursor-pointer p-[18px] transition hover:-translate-y-[3px] hover:shadow-cardHover"
    @click="router.push({ name: 'customer', params: { id: props.customer.id } })"
  >
    <div class="flex justify-between items-start gap-2">
      <div class="min-w-0">
        <div class="font-display text-xl text-maroon-ink truncate">
          {{ customer.first_name }} {{ customer.last_name }}
        </div>
        <div class="font-sans text-[13px] text-muted mt-0.5">
          {{ customer.age }} · {{ customer.city }}{{ customer.state ? `, ${customer.state}` : "" }} ·
          {{ humanize(customer.marital_status) }}
        </div>
      </div>
      <AvatarMonogram
        :name="customer.first_name"
        :photo-url="customer.photo_url"
        :size="44"
      />
    </div>
    <div class="mt-3.5 flex items-center gap-2 flex-wrap">
      <StagePill :stage="customer.journey_stage" small />
      <VerifiedBadge :verified="customer.verified" />
      <span
        v-if="customer.mine"
        class="font-sans text-[10.5px] font-semibold tracking-[0.04em] uppercase text-sage bg-sage/10 border border-sage/30 px-2 py-[2px] rounded-full"
      >
        You
      </span>
      <span
        v-else
        class="font-sans text-[10.5px] tracking-[0.02em] text-muted bg-muted/10 border border-muted/25 px-2 py-[2px] rounded-full"
      >
        {{ customer.assigned_matchmaker_name || "Unassigned" }}
      </span>
    </div>
  </button>
</template>
