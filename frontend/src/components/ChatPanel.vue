<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import { useRoute } from "vue-router";
import { chatApi } from "@/api/chat";
import type { Match } from "@/types/models";
import { tierLabel } from "@/lib/format";
import MotifMark from "./MotifMark.vue";
import SendMatchModal from "./SendMatchModal.vue";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  matches?: Match[];
}

const route = useRoute();

const open = ref(false);
const input = ref("");
const sending = ref(false);
const aiNoticeShown = ref(false);
const composing = ref<Match | null>(null);
const body = ref<HTMLElement | null>(null);
const messages = ref<ChatMessage[]>([
  { role: "assistant", text: "Hi! I can find matches, summarise a client, or draft an intro. Open a client first for the best results." },
]);

const clientId = computed(() => {
  const id = route.params.id;
  return id ? Number(id) : null;
});

async function send() {
  const text = input.value.trim();
  if (!text || sending.value) return;
  // Capture prior turns as history before adding the new message.
  const history = messages.value
    .filter((m) => m.text)
    .slice(-8)
    .map((m) => ({ role: m.role, content: m.text }));
  messages.value.push({ role: "user", text });
  input.value = "";
  sending.value = true;
  await scroll();
  try {
    const res = await chatApi.send(text, clientId.value, history);
    messages.value.push({ role: "assistant", text: res.reply, matches: res.matches ?? undefined });
    // AI not configured OR the provider call failed (e.g. credits exhausted): show a
    // calm, matchmaker-facing note rather than a technical error.
    if ((res.ai_error || !res.ai_used) && !aiNoticeShown.value) {
      aiNoticeShown.value = true;
      messages.value.push({
        role: "assistant",
        text: "Smart AI replies aren't available right now. Please ask your admin to set up AI. In the meantime, I'm using basic search.",
      });
    }
  } catch (e: any) {
    const text =
      e?.response?.status === 403
        ? "You can view this client, but only their assigned matchmaker can run matches or send an introduction."
        : "Something went wrong. Please try again.";
    messages.value.push({ role: "assistant", text });
  } finally {
    sending.value = false;
    await scroll();
  }
}

async function scroll() {
  await nextTick();
  if (body.value) body.value.scrollTop = body.value.scrollHeight;
}

function sendMatch(m: Match) {
  if (!clientId.value) return;
  composing.value = m;
}

function onSent() {
  if (composing.value) composing.value.status = "sent";
}
</script>

<template>
  <div>
    <button
      v-if="!open"
      class="fixed bottom-5 right-5 z-[70] w-14 h-14 rounded-full bg-gradient-to-b from-maroon to-maroon-deep border-2 border-gold grid place-items-center shadow-modal cursor-pointer"
      aria-label="Open Match Assistant"
      @click="open = true"
    >
      <MotifMark :size="26" color="#E8D49A" />
    </button>

    <div
      v-if="open"
      class="fixed bottom-5 right-5 z-[70] w-[min(380px,calc(100vw-2.5rem))] h-[min(560px,calc(100vh-2.5rem))] bg-card-warm rounded-lg border border-gold-soft shadow-modal flex flex-col overflow-hidden"
    >
      <div class="bg-gradient-to-b from-maroon to-maroon-deep px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <MotifMark :size="22" color="#C8A248" />
          <div class="font-display text-white text-[15px] leading-none">
            Match Assistant
            <div class="font-sans text-[10px] tracking-[0.15em] uppercase text-gold-soft mt-1">
              {{ clientId ? "client in context" : "open a client for matches" }}
            </div>
          </div>
        </div>
        <button class="text-gold-soft hover:text-white text-lg leading-none" @click="open = false">✕</button>
      </div>

      <div ref="body" class="flex-1 overflow-y-auto p-3 flex flex-col gap-2.5">
        <template v-for="(m, i) in messages" :key="i">
          <div
            class="max-w-[85%] font-sans text-[13.5px] leading-relaxed px-3 py-2 rounded-xl"
            :class="m.role === 'user'
              ? 'self-end bg-maroon text-white rounded-br-sm'
              : 'self-start bg-white border border-line text-maroon-ink rounded-bl-sm'"
          >
            {{ m.text }}
          </div>
          <div v-if="m.matches?.length" class="self-start w-full flex flex-col gap-2">
            <div
              v-for="mm in m.matches"
              :key="mm.candidate.id"
              class="bg-white border border-line rounded-lg p-2.5 flex items-center justify-between gap-2"
            >
              <div class="min-w-0">
                <div class="font-display text-[15px] text-maroon-ink truncate">
                  {{ mm.candidate.first_name }} {{ mm.candidate.last_name }}
                </div>
                <div class="font-sans text-[11.5px] text-muted">
                  {{ mm.candidate.age }} · {{ mm.candidate.city }} · {{ tierLabel(mm.tier) }} ({{ Math.round(mm.score) }})
                </div>
              </div>
              <button
                class="font-sans text-[12px] text-white bg-maroon px-2.5 py-1.5 rounded-md cursor-pointer shrink-0 disabled:opacity-60"
                :disabled="!clientId || mm.status === 'sent'"
                @click="sendMatch(mm)"
              >
                {{ mm.status === "sent" ? "Sent ✓" : "Send" }}
              </button>
            </div>
          </div>
        </template>
        <div v-if="sending" class="self-start font-serifItalic italic text-muted text-sm px-1">thinking…</div>
      </div>

      <div class="p-3 border-t border-line flex gap-2">
        <input
          v-model="input"
          class="input !py-2"
          placeholder="Ask me to find matches…"
          @keydown.enter="send"
        />
        <button class="font-sans text-sm text-white bg-maroon px-3 rounded-sm cursor-pointer disabled:opacity-60" :disabled="sending" @click="send">
          Send
        </button>
      </div>
    </div>

    <SendMatchModal
      v-if="composing && clientId"
      :customer-id="clientId"
      :candidate-id="composing.candidate.id"
      @sent="onSent"
      @close="composing = null"
    />
  </div>
</template>
