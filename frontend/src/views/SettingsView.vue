<script setup lang="ts">
import { onMounted, ref } from "vue";
import { settingsApi } from "@/api/settings";
import { useToast } from "@/composables/useToast";
import type { LLMProvider, LLMSettings } from "@/types/models";
import DividerMotif from "@/components/DividerMotif.vue";
import MotifMark from "@/components/MotifMark.vue";

const toast = useToast();

const current = ref<LLMSettings | null>(null);
const provider = ref<LLMProvider>("openai");
const apiKey = ref("");
const model = ref("");
const models = ref<string[]>([]);
const loadingModels = ref(false);
const saving = ref(false);
const removing = ref(false);
const removeModal = ref<null | "confirm" | "done">(null);

const PROVIDERS: LLMProvider[] = ["openai", "anthropic", "gemini"];

onMounted(async () => {
  try {
    current.value = await settingsApi.getLLM();
    if (current.value.provider) provider.value = current.value.provider;
    if (current.value.model) model.value = current.value.model;
  } catch {
    toast.error("Could not load settings");
  }
});

async function loadModels() {
  loadingModels.value = true;
  try {
    models.value = await settingsApi.models(provider.value, apiKey.value || undefined);
    if (models.value.length && !models.value.includes(model.value)) model.value = models.value[0];
    toast.success("Models loaded");
  } catch {
    toast.error("Could not load models. Check the provider and key");
  } finally {
    loadingModels.value = false;
  }
}

async function save() {
  saving.value = true;
  try {
    current.value = await settingsApi.updateLLM({
      provider: provider.value,
      api_key: apiKey.value || null,
      model: model.value || null,
    });
    apiKey.value = "";
    toast.success("LLM settings saved");
  } catch (e: any) {
    toast.error(e?.response?.data?.detail ?? "Could not save settings");
  } finally {
    saving.value = false;
  }
}

async function confirmRemove() {
  removing.value = true;
  try {
    current.value = await settingsApi.removeLLM();
    apiKey.value = "";
    model.value = "";
    models.value = [];
    removeModal.value = "done";
  } catch {
    toast.error("Could not remove the key");
    removeModal.value = null;
  } finally {
    removing.value = false;
  }
}
</script>

<template>
  <div class="max-w-[560px] mx-auto">
    <div class="text-center">
      <div class="eyebrow">Admin</div>
      <h2 class="font-display text-[30px] text-maroon m-0">AI Settings</h2>
      <p class="font-serifItalic italic text-muted mt-1">Configure the language model that powers explanations, intros, and chat.</p>
    </div>
    <div class="my-5"><DividerMotif /></div>

    <div
      class="card p-3.5 mb-5 text-center font-sans text-sm"
      :class="current?.configured ? 'text-sage' : 'text-muted'"
    >
      <template v-if="current?.configured">
        AI is active: {{ current.provider }} · {{ current.model }}
        <span v-if="current.masked_key">· key {{ current.masked_key }}</span>
      </template>
      <template v-else>AI is not configured. The app uses built-in templates until a key is added.</template>
    </div>

    <div class="card p-6">
      <label class="field-label !text-maroon">Provider</label>
      <select v-model="provider" class="input mb-4">
        <option v-for="p in PROVIDERS" :key="p" :value="p">{{ p }}</option>
      </select>

      <label class="field-label !text-maroon">API key</label>
      <input
        v-model="apiKey"
        type="password"
        class="input mb-1 disabled:bg-line/30 disabled:text-muted disabled:cursor-not-allowed"
        :disabled="!!current?.configured"
        :placeholder="current?.masked_key ? `Saved: ${current.masked_key} (remove key to change)` : 'Paste provider API key'"
      />
      <p class="font-sans text-[11px] text-muted mb-4">
        {{
          current?.configured
            ? "Key is locked. You can still change the model below; remove the key to replace it."
            : "Stored encrypted (AES-256-GCM). Never shown again after saving."
        }}
      </p>

      <button class="font-sans text-sm text-maroon border border-maroon/30 rounded-sm block w-fit px-3 py-2 cursor-pointer hover:bg-maroon/5 mb-4 disabled:opacity-60" :disabled="loadingModels" @click="loadModels">
        {{ loadingModels ? "Loading…" : "Load models" }}
      </button>

      <template v-if="models.length">
        <label class="field-label !text-maroon block">Model</label>
        <select v-model="model" class="input mb-4">
          <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
        </select>
      </template>

      <button class="btn-primary w-full" :disabled="saving" @click="save">
        {{ saving ? "Saving…" : "Save settings" }}
      </button>

      <button
        v-if="current?.configured"
        class="font-sans text-sm text-maroon border border-maroon/30 rounded-sm w-full px-3 py-2.5 mt-3 cursor-pointer hover:bg-maroon/5"
        @click="removeModal = 'confirm'"
      >
        Remove API key
      </button>
    </div>

    <!-- Remove-key modal (confirm, then confirmation that it's gone). -->
    <div
      v-if="removeModal"
      class="fixed inset-0 grid place-items-center p-5 z-[80]"
      style="background: rgba(58, 18, 32, 0.6)"
      @click.self="removeModal === 'done' && (removeModal = null)"
    >
      <div
        class="w-full max-w-[420px] bg-card-warm rounded-sm border border-gold-soft p-7 text-center"
        style="outline: 1px solid #c8a248; outline-offset: 5px"
      >
        <div class="flex justify-center mb-1.5"><MotifMark :size="28" /></div>
        <template v-if="removeModal === 'confirm'">
          <h3 class="font-display text-2xl text-maroon mb-1">Remove API key?</h3>
          <p class="font-serifItalic italic text-muted mb-5">
            The saved key will be permanently deleted. The app falls back to built-in templates until you add a new one.
          </p>
          <div class="flex gap-2">
            <button
              class="font-sans text-sm text-maroon bg-transparent border border-maroon/30 px-4 py-2.5 rounded-sm cursor-pointer hover:bg-maroon/5"
              @click="removeModal = null"
            >
              Cancel
            </button>
            <button class="btn-primary flex-1" :disabled="removing" @click="confirmRemove">
              {{ removing ? "Removing…" : "Remove key" }}
            </button>
          </div>
        </template>
        <template v-else>
          <h3 class="font-display text-2xl text-maroon mb-1">API key removed</h3>
          <p class="font-serifItalic italic text-muted mb-5">
            The app now uses built-in templates. You can add a new key anytime.
          </p>
          <button class="btn-primary w-full" @click="removeModal = null">Done</button>
        </template>
      </div>
    </div>
  </div>
</template>
