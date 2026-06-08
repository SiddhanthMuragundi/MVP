<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import MotifMark from "./MotifMark.vue";
import NotificationBell from "./NotificationBell.vue";

const auth = useAuthStore();
const router = useRouter();
const menuOpen = ref(false);

const initial = (auth.user?.display_name || "?").charAt(0).toUpperCase();

const navLinks = [
  { name: "home", label: "Home" },
  { name: "dashboard", label: "Matchmaking" },
  { name: "about", label: "About Us" },
];

function signOut() {
  menuOpen.value = false;
  auth.logout();
  router.push({ name: "login" });
}

function closeMenu() {
  menuOpen.value = false;
}
</script>

<template>
  <header class="sticky top-0 z-30 bg-gradient-to-b from-maroon to-maroon-deep border-b-[3px] border-gold shadow-card">
    <div class="max-w-[1100px] mx-auto px-4 sm:px-6 py-3 sm:py-4 flex justify-between items-center gap-3">
      <RouterLink :to="{ name: 'home' }" class="flex items-center gap-2.5 min-w-0">
        <MotifMark :size="28" color="#C8A248" />
        <div class="leading-none">
          <div class="font-display text-[17px] sm:text-xl text-white tracking-[0.02em]">Saathiya</div>
          <div class="hidden sm:block font-sans text-[11px] tracking-[0.22em] uppercase text-gold-soft mt-[3px]">
            Matchmaker Studio
          </div>
        </div>
      </RouterLink>

      <nav class="flex items-center gap-1 sm:gap-2">
        <RouterLink
          v-for="link in navLinks"
          :key="link.name"
          :to="{ name: link.name }"
          class="font-sans text-[13px] text-gold-soft hover:text-white px-2.5 py-1.5 rounded-sm transition"
          active-class="text-white"
        >
          {{ link.label }}
        </RouterLink>

        <NotificationBell />

        <div class="relative ml-1">
          <button
            class="w-9 h-9 rounded-full bg-card-warm border-2 border-gold grid place-items-center font-display text-maroon text-[15px] cursor-pointer hover:brightness-105"
            aria-label="Account menu"
            @click="menuOpen = !menuOpen"
          >
            {{ initial }}
          </button>

          <div
            v-if="menuOpen"
            class="absolute right-0 mt-2 w-52 bg-card rounded-sm border border-line shadow-modal overflow-hidden z-[60]"
          >
            <div class="px-4 py-3 border-b border-line">
              <div class="font-sans text-sm text-maroon-ink font-medium">{{ auth.user?.display_name }}</div>
              <div class="font-sans text-[12px] text-muted capitalize">{{ auth.user?.role }}</div>
            </div>
            <RouterLink
              v-if="auth.isAdmin"
              :to="{ name: 'settings' }"
              class="block px-4 py-2.5 font-sans text-[13px] text-maroon-ink hover:bg-card-warm"
              @click="closeMenu"
            >
              AI Settings
            </RouterLink>
            <button
              class="w-full text-left px-4 py-2.5 font-sans text-[13px] text-maroon hover:bg-maroon/5 cursor-pointer"
              @click="signOut"
            >
              Sign out
            </button>
          </div>
        </div>
      </nav>
    </div>

    <!-- click-away overlay for the dropdown -->
    <div v-if="menuOpen" class="fixed inset-0 z-[55]" @click="closeMenu" />
  </header>
</template>
