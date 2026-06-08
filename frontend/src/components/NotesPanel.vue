<script setup lang="ts">
import { ref } from "vue";
import { customersApi } from "@/api/customers";
import { useToast } from "@/composables/useToast";
import type { Note } from "@/types/models";

const props = defineProps<{ customerId: number; notes: Note[]; readonly?: boolean }>();
const emit = defineEmits<{ added: [note: Note] }>();
const toast = useToast();

const draft = ref("");
const saving = ref(false);

async function add() {
  const body = draft.value.trim();
  if (!body || saving.value) return;
  saving.value = true;
  try {
    const note = await customersApi.addNote(props.customerId, body);
    emit("added", note);
    draft.value = "";
    toast.success("Note added");
  } catch {
    toast.error("Could not save note");
  } finally {
    saving.value = false;
  }
}

function fmt(ts: string) {
  return new Date(ts).toLocaleString();
}
</script>

<template>
  <div class="max-w-[600px]">
    <div v-if="!readonly" class="flex gap-2 mb-[18px]">
      <input
        v-model="draft"
        class="input !rounded-xl"
        placeholder="Add a note from your last call…"
        @keydown.enter="add"
      />
      <button class="font-sans font-medium text-sm text-white bg-maroon border-none px-[18px] rounded-xl cursor-pointer disabled:opacity-60" :disabled="saving" @click="add">
        Add
      </button>
    </div>

    <p v-if="notes.length === 0" class="font-sans text-sm text-muted">No notes yet.</p>

    <div v-for="n in notes" :key="n.id" class="bg-card border border-line rounded-xl p-3.5 mb-2.5">
      <p class="font-sans text-sm text-maroon-ink m-0 leading-relaxed">{{ n.body }}</p>
      <div class="font-sans text-[11px] text-muted mt-1.5">{{ n.author_name }} · {{ fmt(n.created_at) }}</div>
    </div>
  </div>
</template>
