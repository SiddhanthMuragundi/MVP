<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import MotifMark from "@/components/MotifMark.vue";
import DividerMotif from "@/components/DividerMotif.vue";
import BackgroundVines from "@/components/BackgroundVines.vue";

const auth = useAuthStore();
const router = useRouter();

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);
const year = new Date().getFullYear();

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    await auth.login(username.value, password.value);
    router.push({ name: "home" });
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? "Unable to sign in. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div
    class="relative min-h-screen grid place-items-center overflow-hidden p-5"
    style="background: radial-gradient(circle at 50% 0%, #6e1530 0%, #5a1126 55%, #420d1c 100%)"
  >
    <BackgroundVines
      :corners="['tl', 'tr', 'bl', 'br']"
      :size="280"
      :opacity="0.5"
      leaf-fill="rgba(232,212,154,0.12)"
      petal="#E8D49A"
      bud="#E08A1E"
    />
    <div class="relative z-10 w-full max-w-[400px]">
      <div
        class="bg-card-warm rounded-sm px-9 sm:px-10 pt-11 pb-9 shadow-modal border border-gold-soft"
        style="outline: 1px solid #c8a248; outline-offset: 6px"
      >
        <div class="text-center">
          <div class="flex justify-center"><MotifMark :size="38" /></div>
          <h1 class="font-display text-[34px] text-maroon leading-none mt-3 mb-1.5">Saathiya</h1>
          <div class="font-sans text-[11px] tracking-[0.28em] uppercase text-marigold">Matchmaker Studio</div>
        </div>

        <div class="my-6"><DividerMotif /></div>

        <form @submit.prevent="submit">
          <div class="mb-3.5">
            <label class="font-sans text-[11px] font-medium tracking-[0.08em] uppercase text-maroon block mb-1.5">
              Username
            </label>
            <input v-model="username" type="text" class="input" autocomplete="username" />
          </div>
          <div class="mb-3.5">
            <label class="font-sans text-[11px] font-medium tracking-[0.08em] uppercase text-maroon block mb-1.5">
              Password
            </label>
            <input v-model="password" type="password" class="input" autocomplete="current-password" />
          </div>

          <p v-if="error" class="font-sans text-[13px] text-maroon bg-maroon/5 border border-maroon/20 rounded-sm px-3 py-2 my-2">
            {{ error }}
          </p>

          <button type="submit" class="btn-primary w-full mt-2.5" :disabled="loading">
            {{ loading ? "Signing in..." : "Sign in" }}
          </button>
        </form>

        <p class="font-sans text-xs text-muted mt-5 text-center">Authorised matchmakers only</p>
      </div>
    </div>

    <p class="absolute bottom-5 inset-x-0 z-10 text-center font-sans text-[11px] tracking-wide text-gold-soft/70">
      &copy; {{ year }} Saathiya &middot; Matchmaker Studio
    </p>
  </div>
</template>
