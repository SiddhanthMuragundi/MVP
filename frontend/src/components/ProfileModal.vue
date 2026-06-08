<script setup lang="ts">
import { computed } from "vue";
import type { Profile } from "@/types/models";
import { profileSections } from "@/lib/format";
import AvatarMonogram from "./AvatarMonogram.vue";
import VerifiedBadge from "./VerifiedBadge.vue";
import BiodataSection from "./BiodataSection.vue";

const props = defineProps<{ profile: Profile }>();
const emit = defineEmits<{ close: [] }>();

const sections = computed(() => profileSections(props.profile));
const subtitle = computed(() => {
  const c = props.profile;
  return [c.age, c.height_cm ? `${c.height_cm} cm` : null, c.city].filter(Boolean).join(" · ");
});
</script>

<template>
  <div
    class="fixed inset-0 z-[80] grid place-items-center p-4"
    style="background: rgba(58, 18, 32, 0.6)"
    @click.self="emit('close')"
  >
    <div class="w-full max-w-[760px] max-h-[90vh] overflow-y-auto bg-card-warm rounded-sm border border-gold-soft shadow-modal">
      <div class="flex items-start justify-between gap-3 p-5 sm:p-6 border-b border-line sticky top-0 bg-card-warm">
        <div class="flex gap-3.5 items-center">
          <AvatarMonogram :name="profile.first_name" :photo-url="profile.photo_url" :size="56" />
          <div>
            <h3 class="font-display text-2xl text-maroon-ink m-0 flex items-center gap-2 flex-wrap">
              {{ profile.first_name }} {{ profile.last_name }}
              <VerifiedBadge :verified="profile.verified" />
            </h3>
            <div class="font-sans text-sm text-muted">{{ subtitle }}</div>
          </div>
        </div>
        <button class="text-muted hover:text-maroon text-xl leading-none" aria-label="Close" @click="emit('close')">✕</button>
      </div>

      <div class="p-5 sm:p-6">
        <p v-if="profile.bio" class="font-serifItalic italic text-[15px] text-maroon-ink mb-5 leading-relaxed">
          “{{ profile.bio }}”
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <BiodataSection v-for="s in sections" :key="s.title" :title="s.title" :fields="s.fields" />
        </div>
      </div>
    </div>
  </div>
</template>
