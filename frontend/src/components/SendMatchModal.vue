<script setup lang="ts">
import { onMounted, ref } from "vue";
import { matchesApi } from "@/api/matches";
import { useToast } from "@/composables/useToast";
import MotifMark from "./MotifMark.vue";

const props = defineProps<{ customerId: number; candidateId: number; resend?: boolean }>();
const emit = defineEmits<{ close: []; sent: [] }>();
const toast = useToast();

const loading = ref(true);
const sending = ref(false);
const to = ref("");
const subject = ref("");
const body = ref("");

onMounted(async () => {
  try {
    const email = await matchesApi.draft(props.customerId, props.candidateId);
    to.value = email.to;
    subject.value = email.subject;
    body.value = email.body;
  } catch {
    toast.error("Could not draft the email");
    emit("close");
  } finally {
    loading.value = false;
  }
});

async function send() {
  if (sending.value) return;
  sending.value = true;
  try {
    await matchesApi.send(props.customerId, props.candidateId, {
      subject: subject.value,
      body: body.value,
      resend: props.resend,
    });
    toast.success("Match sent to your client");
    emit("sent");
    emit("close");
  } catch {
    toast.error("Could not send match");
  } finally {
    sending.value = false;
  }
}
</script>

<template>
  <div
    class="fixed inset-0 grid place-items-center p-5 z-[80]"
    style="background: rgba(58, 18, 32, 0.6)"
    @click.self="emit('close')"
  >
    <div
      class="w-full max-w-[480px] bg-card-warm rounded-sm border border-gold-soft p-7"
      style="outline: 1px solid #c8a248; outline-offset: 5px"
    >
      <div class="text-center mb-1.5 flex justify-center"><MotifMark :size="30" /></div>
      <h3 class="text-center font-display text-2xl text-maroon mt-0.5 mb-1">Send an introduction</h3>
      <p class="text-center font-serifItalic italic text-[15px] text-muted mb-4">
        Review and edit before sending
      </p>

      <div v-if="loading" class="py-10 text-center font-serifItalic italic text-muted">
        Drafting the email...
      </div>

      <div v-else>
        <div class="mb-3">
          <div class="font-sans text-[11px] uppercase tracking-[0.08em] text-muted mb-1">To (your client)</div>
          <div class="font-sans text-sm text-maroon-ink bg-white border border-line rounded-sm px-3 py-2">
            {{ to }}
          </div>
        </div>
        <div class="mb-3">
          <label class="font-sans text-[11px] uppercase tracking-[0.08em] text-muted mb-1 block">Subject</label>
          <input v-model="subject" class="input" />
        </div>
        <div class="mb-4">
          <label class="font-sans text-[11px] uppercase tracking-[0.08em] text-muted mb-1 block">Message</label>
          <textarea v-model="body" rows="9" class="input resize-y leading-relaxed"></textarea>
        </div>

        <div class="flex gap-2">
          <button
            class="font-sans text-sm text-maroon bg-transparent border border-maroon/30 px-4 py-2.5 rounded-sm cursor-pointer hover:bg-maroon/5"
            @click="emit('close')"
          >
            Cancel
          </button>
          <button class="btn-primary flex-1" :disabled="sending" @click="send">
            {{ sending ? "Sending..." : "Send" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
