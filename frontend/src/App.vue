<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import AppHeader from "@/components/AppHeader.vue";
import ChatPanel from "@/components/ChatPanel.vue";
import ToastHost from "@/components/ToastHost.vue";
import BackgroundVines from "@/components/BackgroundVines.vue";
import AppFooter from "@/components/AppFooter.vue";

const route = useRoute();
const isBare = computed(() => route.meta.public === true);
</script>

<template>
  <RouterView v-if="isBare" />
  <div v-else class="relative min-h-screen bg-ivory bg-dotted">
    <div class="relative z-10 flex min-h-screen flex-col">
      <AppHeader />
      <!-- Body region: vines are scoped here so they never touch the header or footer. -->
      <div class="relative flex-1">
        <BackgroundVines :corners="['tl', 'br']" :size="220" :opacity="0.22" />
        <main class="relative z-10 w-full max-w-[1100px] mx-auto px-4 sm:px-6 py-5 sm:py-7 pb-12">
          <RouterView />
        </main>
      </div>
      <AppFooter />
    </div>
    <ChatPanel />
  </div>
  <ToastHost />
</template>
