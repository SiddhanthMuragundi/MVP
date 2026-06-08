<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import { notificationsApi } from "@/api/notifications";
import { useAuthStore } from "@/stores/auth";
import type { Activity } from "@/types/models";

const auth = useAuthStore();
const router = useRouter();
const me = auth.user?.id;

function openActivity(a: Activity) {
  if (!a.customer_id) return;
  open.value = false;
  router.push({ name: "customer", params: { id: a.customer_id } });
}

// Personalise: show the viewer's own actions as "You ..." and "... to you".
function display(a: Activity) {
  let msg = a.message;
  if (a.actor_user_id === me && msg.startsWith(a.actor_name)) {
    msg = "You" + msg.slice(a.actor_name.length);
  }
  if (a.target_user_id === me && a.target_name) {
    msg = msg.split(a.target_name).join("you");
  }
  return msg;
}

const open = ref(false);
const items = ref<Activity[]>([]);
const unread = ref(0);
const hasMore = ref(false);
const loading = ref(false);

async function refresh() {
  try {
    const res = await notificationsApi.list();
    items.value = res.items;
    unread.value = res.unread_count;
    hasMore.value = res.has_more;
  } catch {
    /* ignore polling errors */
  }
}

async function loadMore() {
  if (!items.value.length || loading.value) return;
  loading.value = true;
  try {
    const last = items.value[items.value.length - 1].id;
    const res = await notificationsApi.list(last);
    items.value.push(...res.items);
    hasMore.value = res.has_more;
  } finally {
    loading.value = false;
  }
}

async function clearAll() {
  await notificationsApi.clear();
  items.value = [];
  unread.value = 0;
  hasMore.value = false;
}

function toggle() {
  open.value = !open.value;
  if (open.value) refresh();
}

function timeAgo(ts: string) {
  const s = (Date.now() - new Date(ts).getTime()) / 1000;
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}

let timer: number;
onMounted(() => {
  refresh();
  // Refresh the badge periodically, but not while the panel is open (keeps "load more").
  timer = window.setInterval(() => {
    if (!open.value) refresh();
  }, 30000);
});
onUnmounted(() => window.clearInterval(timer));
</script>

<template>
  <div class="relative">
    <button
      class="relative text-gold-soft hover:text-white w-9 h-9 grid place-items-center cursor-pointer"
      aria-label="Notifications"
      @click="toggle"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.7 21a2 2 0 0 1-3.4 0" />
      </svg>
      <span
        v-if="unread"
        class="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 grid place-items-center font-sans text-[10px] font-bold text-white bg-marigold rounded-full"
      >
        {{ unread > 9 ? "9+" : unread }}
      </span>
    </button>

    <div
      v-if="open"
      class="absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] bg-card rounded-sm border border-line shadow-modal overflow-hidden z-[60]"
    >
      <div class="flex items-center justify-between px-4 py-2.5 border-b border-line">
        <span class="font-display text-[15px] text-maroon">Notifications</span>
        <button v-if="items.length" class="font-sans text-[12px] text-muted hover:text-maroon cursor-pointer" @click="clearAll">
          Clear all
        </button>
      </div>

      <div class="max-h-[360px] overflow-y-auto">
        <p v-if="!items.length" class="font-sans text-[13px] text-muted text-center py-8">You're all caught up.</p>

        <button
          v-for="a in items"
          :key="a.id"
          class="w-full text-left px-4 py-2.5 border-b border-line/60 last:border-0 disabled:cursor-default"
          :class="a.customer_id ? 'cursor-pointer hover:bg-card-warm' : ''"
          :disabled="!a.customer_id"
          @click="openActivity(a)"
        >
          <p class="font-sans text-[13px] text-maroon-ink leading-snug">{{ display(a) }}</p>
          <div class="font-sans text-[11px] text-muted mt-0.5">{{ timeAgo(a.created_at) }}</div>
        </button>

        <button
          v-if="hasMore"
          class="w-full font-sans text-[12.5px] text-maroon py-2.5 hover:bg-maroon/5 cursor-pointer disabled:opacity-50"
          :disabled="loading"
          @click="loadMore"
        >
          {{ loading ? "Loading..." : "Load more" }}
        </button>
      </div>
    </div>

    <div v-if="open" class="fixed inset-0 z-[55]" @click="open = false" />
  </div>
</template>
