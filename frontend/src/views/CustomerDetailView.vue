<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { customersApi } from "@/api/customers";
import { teamApi } from "@/api/team";
import { useAuthStore } from "@/stores/auth";
import { useToast } from "@/composables/useToast";
import { STAGES, humanize } from "@/lib/format";
import type { CustomerDetail, JourneyStage, Match, Matchmaker, Note } from "@/types/models";
import AvatarMonogram from "@/components/AvatarMonogram.vue";
import StagePill from "@/components/StagePill.vue";
import VerifiedBadge from "@/components/VerifiedBadge.vue";
import BiodataSection from "@/components/BiodataSection.vue";
import CompletenessMeter from "@/components/CompletenessMeter.vue";
import NotesPanel from "@/components/NotesPanel.vue";
import MatchCard from "@/components/MatchCard.vue";
import SendMatchModal from "@/components/SendMatchModal.vue";
import MotifMark from "@/components/MotifMark.vue";
import StateNotice from "@/components/StateNotice.vue";

const props = defineProps<{ id: string }>();
const router = useRouter();
const toast = useToast();
const auth = useAuthStore();
const customerId = Number(props.id);

const client = ref<CustomerDetail | null>(null);
const loading = ref(true);
const loadError = ref<"notfound" | "forbidden" | "generic" | null>(null);
const tab = ref<"bio" | "matches" | "notes">("bio");
const stage = ref<JourneyStage | null>(null);
const mine = computed(() => client.value?.editable ?? false);

const matchable = computed(() => {
  const c = client.value;
  return !!c && c.verified && c.journey_stage !== "on_hold" && c.journey_stage !== "closed";
});
const matchHint = computed(() => {
  const c = client.value;
  if (!c) return "";
  if (!c.verified) return "Verify this client to start finding matches.";
  if (c.journey_stage === "on_hold") return "This client is on hold, so matching is paused.";
  if (c.journey_stage === "closed") return "This client is closed. Their matchmaking journey is complete.";
  return "";
});

const matches = ref<Match[]>([]);
const matchesLoaded = ref(false);
const matchesLoading = ref(false);
const composing = ref<Match | null>(null);

// Admin-only client assignment
const matchmakers = ref<Matchmaker[]>([]);
const assignSel = ref<number>(0); // 0 = auto (least-loaded)

onMounted(async () => {
  try {
    client.value = await customersApi.get(customerId);
    stage.value = client.value.journey_stage;
    assignSel.value = client.value.assigned_matchmaker_id ?? 0;
    if (auth.isAdmin) matchmakers.value = await teamApi.listMatchmakers();
  } catch (e: any) {
    const status = e?.response?.status;
    loadError.value = status === 404 ? "notfound" : status === 403 ? "forbidden" : "generic";
  } finally {
    loading.value = false;
  }
});

async function assignMatchmaker() {
  try {
    await customersApi.assignMatchmaker(customerId, assignSel.value === 0 ? null : assignSel.value);
    client.value = await customersApi.get(customerId);
    assignSel.value = client.value.assigned_matchmaker_id ?? 0;
    matchmakers.value = await teamApi.listMatchmakers();
    toast.success("Client assigned");
  } catch {
    toast.error("Could not assign client");
  }
}

const sections = computed(() => {
  const c = client.value;
  if (!c) return [];
  return [
    {
      title: "Basics",
      fields: [
        { label: "Gender", value: humanize(c.gender) },
        { label: "Age", value: c.age },
        { label: "Height", value: c.height_cm ? `${c.height_cm} cm` : null },
        { label: "City", value: c.city },
        { label: "Country", value: c.country },
        { label: "Marital status", value: humanize(c.marital_status) },
      ],
    },
    {
      title: "Education & Career",
      fields: [
        { label: "College", value: c.ug_college },
        { label: "Degree", value: c.degree },
        { label: "Company", value: c.company },
        { label: "Designation", value: c.designation },
        { label: "Income", value: c.income_lpa ? `₹${c.income_lpa} LPA` : null },
      ],
    },
    {
      title: "Community & Family",
      fields: [
        { label: "Religion", value: c.religion },
        { label: "Caste", value: c.caste },
        { label: "Mother tongue", value: c.mother_tongue },
        { label: "Manglik", value: humanize(c.manglik) },
        { label: "Family type", value: humanize(c.family_type) },
        { label: "Siblings", value: c.siblings },
      ],
    },
    {
      title: "Lifestyle & Intent",
      fields: [
        { label: "Diet", value: humanize(c.diet) },
        { label: "Smoking", value: humanize(c.smoking) },
        { label: "Drinking", value: humanize(c.drinking) },
        { label: "Want kids", value: humanize(c.want_kids) },
        { label: "Open to relocate", value: humanize(c.open_to_relocate) },
        { label: "Open to pets", value: humanize(c.open_to_pets) },
        { label: "Languages", value: c.languages_known?.join(", ") },
        { label: "Hobbies", value: c.hobbies?.join(", ") },
      ],
    },
  ];
});

const completeness = computed(() => {
  const all = sections.value.flatMap((s) => s.fields);
  const filled = all.filter((f) => f.value !== null && f.value !== undefined && f.value !== "").length;
  return { filled, total: all.length };
});

async function changeStage() {
  if (!stage.value) return;
  try {
    const updated = await customersApi.updateStage(customerId, stage.value);
    if (client.value) {
      // verified is derived from the stage, so sync both to keep the UI reactive.
      client.value.journey_stage = updated.journey_stage;
      client.value.verified = updated.verified;
    }
    stage.value = updated.journey_stage;
    toast.success("Stage updated");
  } catch {
    toast.error("Could not update stage");
  }
}

async function loadMatches(refresh = false) {
  matchesLoading.value = true;
  try {
    matches.value = await customersApi.matches(customerId, { limit: 12, refresh, explain: true });
    matchesLoaded.value = true;
  } catch {
    toast.error("Could not load matches");
  } finally {
    matchesLoading.value = false;
  }
}

function openMatches() {
  tab.value = "matches";
  if (matchable.value && !matchesLoaded.value) loadMatches();
}

function replaceMatch(updated: Match) {
  const i = matches.value.findIndex((x) => x.candidate.id === updated.candidate.id);
  if (i !== -1) matches.value[i] = updated;
}

async function shortlist(m: Match) {
  try {
    replaceMatch(await customersApi.shortlist(customerId, m.candidate.id));
  } catch {
    toast.error("Could not shortlist match");
  }
}

async function unshortlist(m: Match) {
  try {
    replaceMatch(await customersApi.unshortlist(customerId, m.candidate.id));
  } catch {
    toast.error("Could not remove from shortlist");
  }
}

async function setOutcome({ match: m, outcome }: { match: Match; outcome: string }) {
  try {
    replaceMatch(await customersApi.setOutcome(customerId, m.candidate.id, outcome));
    toast.success("Outcome updated");
  } catch {
    toast.error("Could not update outcome");
  }
}

function send(m: Match) {
  composing.value = m;
}

function onSent() {
  if (composing.value) composing.value.status = "sent";
  // Sending the first match advances the client's journey.
  if (client.value && ["new", "verified", "matching"].includes(client.value.journey_stage ?? "")) {
    client.value.journey_stage = "matches_sent";
    stage.value = "matches_sent";
  }
}

async function verify() {
  try {
    const updated = await customersApi.verify(customerId);
    if (client.value) {
      client.value.verified = updated.verified;
      client.value.journey_stage = updated.journey_stage;
      stage.value = updated.journey_stage;
    }
    toast.success("Profile verified");
  } catch {
    toast.error("Could not verify profile");
  }
}

function onNoteAdded(note: Note) {
  client.value?.notes.unshift(note);
}

const subtitle = computed(() => {
  const c = client.value;
  if (!c) return "";
  return [c.age, c.height_cm ? `${c.height_cm} cm` : null, c.city].filter(Boolean).join(" · ");
});

const tabs = computed<[string, string][]>(() => {
  const t: [string, string][] = [["bio", "Biodata"]];
  // Matches and Notes are the owning matchmaker's workspace. A non-owner (admin overseer
  // or another matchmaker) only needs the biodata, so we hide the unusable empty tabs.
  if (mine.value) {
    t.push(["matches", "Matches"]);
    t.push(["notes", `Notes · ${client.value?.notes.length ?? 0}`]);
  }
  return t;
});
</script>

<template>
  <div v-if="loading" class="py-16 text-center font-serifItalic italic text-muted text-lg">
    Loading profile…
  </div>

  <div v-else-if="client">
    <button class="btn-ghost mb-4" @click="router.push({ name: 'dashboard' })">← Back to roster</button>

    <div class="flex flex-wrap gap-4 items-center justify-between mb-[18px]">
      <div class="flex gap-3.5 items-center">
        <AvatarMonogram :name="client.first_name" :photo-url="client.photo_url" :size="58" />
        <div>
          <h2 class="font-display text-2xl sm:text-3xl text-maroon-ink m-0 flex items-center gap-2 flex-wrap">
            {{ client.first_name }} {{ client.last_name }}
            <VerifiedBadge :verified="client.verified" />
            <span
              v-if="!client.verified"
              class="font-sans text-[10.5px] font-semibold tracking-[0.04em] uppercase text-marigold bg-marigold/10 border border-marigold/30 px-2 py-[2px] rounded-full"
            >
              Pending verification
            </span>
          </h2>
          <div class="font-sans text-sm text-muted">{{ subtitle }}</div>
        </div>
      </div>
      <div class="flex gap-2 items-center flex-wrap">
        <template v-if="mine">
          <button
            v-if="!client.verified"
            class="font-sans text-[13px] font-semibold text-white bg-sage px-3 py-2 rounded-sm cursor-pointer hover:brightness-110"
            @click="verify"
          >
            ✓ Verify profile
          </button>
          <span class="font-sans text-xs text-muted">Stage</span>
          <select v-model="stage" class="input !w-auto !rounded-[10px] !py-2" @change="changeStage">
            <option v-for="s in STAGES" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
        </template>
        <template v-else-if="auth.isAdmin">
          <span class="font-sans text-xs text-muted">Matchmaker</span>
          <select v-model.number="assignSel" class="input !w-auto !rounded-[10px] !py-2" @change="assignMatchmaker">
            <option :value="0">Auto-assign (least-loaded)</option>
            <option v-for="m in matchmakers" :key="m.id" :value="m.id">
              {{ m.display_name }} · {{ m.client_count }} clients
            </option>
          </select>
        </template>
        <StagePill :stage="client.journey_stage" />
      </div>
    </div>

    <div class="flex gap-1 border-b border-line mb-5 overflow-x-auto">
      <button
        v-for="t in tabs"
        :key="t[0]"
        class="font-sans text-sm px-3.5 py-2.5 cursor-pointer border-b-2 -mb-px whitespace-nowrap"
        :class="tab === t[0] ? 'font-semibold text-maroon-ink border-maroon' : 'text-muted border-transparent'"
        @click="t[0] === 'matches' ? openMatches() : (tab = t[0] as any)"
      >
        {{ t[1] }}
      </button>
    </div>

    <!-- Biodata -->
    <div v-if="tab === 'bio'">
      <CompletenessMeter :filled="completeness.filled" :total="completeness.total" />
      <div class="grid grid-cols-1 sm:grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-5">
        <BiodataSection v-for="s in sections" :key="s.title" :title="s.title" :fields="s.fields" />
      </div>
    </div>

    <!-- Matches -->
    <div v-else-if="tab === 'matches'">
      <div v-if="!matchable" class="py-12 text-center">
        <div class="flex justify-center mb-3"><MotifMark :size="32" /></div>
        <p class="font-serifItalic italic text-lg text-muted">{{ matchHint }}</p>
        <button
          v-if="mine && !client.verified"
          class="font-sans text-[13px] font-semibold text-white bg-sage px-4 py-2 rounded-sm cursor-pointer hover:brightness-110 mt-4"
          @click="verify"
        >
          ✓ Verify profile
        </button>
      </div>

      <template v-else>
      <div class="flex justify-between items-start gap-3 mb-4">
        <p class="font-serifItalic italic text-muted m-0">Suggested partners, ranked by compatibility.</p>
        <button class="btn-ghost shrink-0" :disabled="matchesLoading" @click="loadMatches(true)">↻ Regenerate</button>
      </div>

      <div v-if="matchesLoading" class="py-12 text-center font-serifItalic italic text-muted">
        Finding matches…
      </div>
      <div v-else-if="matches.length === 0" class="py-12 text-center">
        <div class="flex justify-center mb-3"><MotifMark :size="32" /></div>
        <p class="font-serifItalic italic text-muted">No suitable matches yet.</p>
      </div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-[repeat(auto-fill,minmax(300px,1fr))] gap-4">
        <MatchCard
          v-for="m in matches"
          :key="m.candidate.id"
          :match="m"
          @shortlist="shortlist"
          @unshortlist="unshortlist"
          @outcome="setOutcome"
          @send="send"
        />
      </div>
      </template>
    </div>

    <!-- Notes -->
    <div v-else-if="tab === 'notes'">
      <NotesPanel :customer-id="customerId" :notes="client.notes" :readonly="!mine" @added="onNoteAdded" />
    </div>

    <SendMatchModal
      v-if="composing"
      :customer-id="customerId"
      :candidate-id="composing.candidate.id"
      :resend="['sent', 'accepted', 'declined', 'no_response', 'withdrawn'].includes(composing.status)"
      @sent="onSent"
      @close="composing = null"
    />
  </div>

  <StateNotice
    v-else
    :eyebrow="loadError === 'forbidden' ? 'No access' : 'Not found'"
    :title="loadError === 'forbidden' ? 'You don’t have access to this profile' : 'Profile not found'"
    :message="
      loadError === 'forbidden'
        ? 'This client belongs to another matchmaker, so their profile isn’t available to you.'
        : 'We couldn’t open this profile. It may have been removed or the link is incorrect.'
    "
    action-label="Back to roster"
    @action="router.push({ name: 'dashboard' })"
  />
</template>
