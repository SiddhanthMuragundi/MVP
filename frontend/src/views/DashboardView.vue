<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { customersApi } from "@/api/customers";
import { useAuthStore } from "@/stores/auth";
import type { CustomerListItem, FilterOptions, JourneyStage } from "@/types/models";
import { STAGES, GENDERS, humanize } from "@/lib/format";
import CustomerCard from "@/components/CustomerCard.vue";
import DividerMotif from "@/components/DividerMotif.vue";
import MotifMark from "@/components/MotifMark.vue";

const auth = useAuthStore();

const customers = ref<CustomerListItem[]>([]);
const total = ref(0);
const loading = ref(true);
const error = ref("");

const search = ref("");
const stage = ref<JourneyStage | "">("");
const verifyFilter = ref<"all" | "verified" | "pending">("all");
const stateFilter = ref("");
const cityFilter = ref("");
const religionFilter = ref("");
const languageFilter = ref("");
const genderFilter = ref("");
const maritalFilter = ref("");
const ageMin = ref("");
const ageMax = ref("");
const scope = ref<"all" | "mine">("all");

// Filter option lists are loaded live from the API, never hardcoded.
const options = ref<FilterOptions>({
  states: [],
  cities_by_state: {},
  cities: [],
  languages: [],
  religions: [],
  marital_statuses: [],
});
// Cities cascade from the selected state; with no state, show every city.
const cityOptions = computed(() =>
  stateFilter.value ? options.value.cities_by_state[stateFilter.value] ?? [] : options.value.cities,
);

const hasFilters = computed(
  () =>
    !!search.value || !!stage.value || verifyFilter.value !== "all" || !!stateFilter.value ||
    !!cityFilter.value || !!religionFilter.value || !!languageFilter.value || !!genderFilter.value ||
    !!maritalFilter.value || !!ageMin.value || !!ageMax.value,
);

function resetFilters() {
  search.value = "";
  stage.value = "";
  verifyFilter.value = "all";
  stateFilter.value = "";
  cityFilter.value = "";
  religionFilter.value = "";
  languageFilter.value = "";
  genderFilter.value = "";
  maritalFilter.value = "";
  ageMin.value = "";
  ageMax.value = "";
}

const PAGE_SIZE = 12;
const page = ref(1);
const pageCount = computed(() => Math.max(1, Math.ceil(customers.value.length / PAGE_SIZE)));
const paged = computed(() => customers.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE));

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const data = await customersApi.list({
      search: search.value || undefined,
      stage: stage.value || undefined,
      verified: verifyFilter.value === "all" ? undefined : verifyFilter.value === "verified",
      state: stateFilter.value || undefined,
      city: cityFilter.value || undefined,
      religion: religionFilter.value || undefined,
      language: languageFilter.value || undefined,
      gender: genderFilter.value || undefined,
      marital_status: maritalFilter.value || undefined,
      age_min: ageMin.value ? Number(ageMin.value) : undefined,
      age_max: ageMax.value ? Number(ageMax.value) : undefined,
      mine: !auth.isAdmin && scope.value === "mine" ? true : undefined,
    });
    customers.value = data;
    page.value = 1;
    if (!hasFilters.value) total.value = data.length;
  } catch {
    error.value = "Could not load clients.";
  } finally {
    loading.value = false;
  }
}

let timer: number | undefined;
watch(
  [search, stage, verifyFilter, stateFilter, cityFilter, religionFilter, languageFilter, genderFilter, maritalFilter, ageMin, ageMax, scope],
  () => {
    window.clearTimeout(timer);
    timer = window.setTimeout(load, 250);
  },
);

// When the state changes, drop a city that no longer belongs to it.
watch(stateFilter, () => {
  if (cityFilter.value && !cityOptions.value.includes(cityFilter.value)) cityFilter.value = "";
});

onMounted(async () => {
  try {
    options.value = await customersApi.filterOptions();
  } catch {
    /* filters still work; dropdowns just stay empty */
  }
  await load();
});
</script>

<template>
  <div>
    <div class="flex flex-wrap gap-3 items-end mb-2">
      <div class="flex-1 min-w-[240px]">
        <div class="eyebrow mb-0.5">The Roster</div>
        <h2 class="font-display text-[28px] sm:text-[34px] text-maroon leading-none m-0">
          {{ !auth.isAdmin && scope === "mine" ? "Your Clients" : "Client Roster" }}
        </h2>
        <p class="font-serifItalic italic text-base text-muted mt-1">
          {{ customers.length }}<span v-if="total"> of {{ total }}</span>
          {{ !auth.isAdmin && scope === "mine" ? "profiles in your care" : "profiles across the studio" }}
        </p>
      </div>

      <div v-if="!auth.isAdmin" class="inline-flex rounded-sm border border-line overflow-hidden self-end">
        <button
          v-for="opt in (['all', 'mine'] as const)"
          :key="opt"
          class="font-sans text-[13px] px-3 py-2 cursor-pointer"
          :class="scope === opt ? 'bg-maroon text-white' : 'bg-card text-maroon hover:bg-maroon/5'"
          @click="scope = opt"
        >
          {{ opt === "all" ? "All clients" : "My clients" }}
        </button>
      </div>
      <input
        v-model="search"
        placeholder="Search name, city, religion, community, profession…"
        class="input !w-auto flex-1 sm:flex-none min-w-[220px]"
      />
    </div>

    <div class="flex flex-wrap gap-2 mt-2.5">
      <select v-model="genderFilter" class="input !w-auto">
        <option value="">Any gender</option>
        <option v-for="g in GENDERS" :key="g.value" :value="g.value">{{ g.label }}</option>
      </select>
      <select v-model="stateFilter" class="input !w-auto">
        <option value="">All states</option>
        <option v-for="st in options.states" :key="st" :value="st">{{ st }}</option>
      </select>
      <select v-model="cityFilter" class="input !w-auto">
        <option value="">{{ stateFilter ? `All cities in ${stateFilter}` : "All cities" }}</option>
        <option v-for="ct in cityOptions" :key="ct" :value="ct">{{ ct }}</option>
      </select>
      <select v-model="languageFilter" class="input !w-auto">
        <option value="">Any language</option>
        <option v-for="l in options.languages" :key="l" :value="l">{{ l }}</option>
      </select>
      <select v-model="religionFilter" class="input !w-auto">
        <option value="">All religions</option>
        <option v-for="r in options.religions" :key="r" :value="r">{{ r }}</option>
      </select>
      <select v-model="maritalFilter" class="input !w-auto">
        <option value="">Any marital status</option>
        <option v-for="m in options.marital_statuses" :key="m" :value="m">{{ humanize(m) }}</option>
      </select>
      <select v-model="stage" class="input !w-auto">
        <option value="">All stages</option>
        <option v-for="s in STAGES" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
      <select v-model="verifyFilter" class="input !w-auto">
        <option value="all">All profiles</option>
        <option value="verified">Verified</option>
        <option value="pending">Pending verification</option>
      </select>
      <div class="inline-flex items-center gap-1.5 border border-line rounded-sm px-2.5 bg-white">
        <span class="font-sans text-[11px] uppercase tracking-[0.06em] text-muted">Age</span>
        <input v-model="ageMin" type="number" min="18" max="99" placeholder="min" class="w-12 border-none outline-none bg-transparent text-[14px] text-maroon-ink" />
        <span class="text-muted">–</span>
        <input v-model="ageMax" type="number" min="18" max="99" placeholder="max" class="w-12 border-none outline-none bg-transparent text-[14px] text-maroon-ink" />
      </div>
      <button
        v-if="hasFilters"
        class="font-sans text-[13px] text-maroon border border-line rounded-sm px-3 cursor-pointer hover:bg-maroon/5"
        @click="resetFilters"
      >
        ✕ Clear
      </button>
    </div>

    <div class="my-[18px]"><DividerMotif /></div>

    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-3.5">
      <div v-for="n in 6" :key="n" class="card p-[18px] animate-pulse h-[120px]" />
    </div>

    <p v-else-if="error" class="font-sans text-maroon text-center py-10">{{ error }}</p>

    <div v-else-if="customers.length === 0" class="text-center py-16">
      <div class="flex justify-center mb-3"><MotifMark :size="34" /></div>
      <p class="font-serifItalic italic text-lg text-muted">No clients match your filters.</p>
    </div>

    <template v-else>
      <div class="grid grid-cols-1 sm:grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-3.5">
        <CustomerCard v-for="c in paged" :key="c.id" :customer="c" />
      </div>

      <div v-if="pageCount > 1" class="flex items-center justify-center gap-4 mt-8">
        <button
          class="font-sans text-[13px] text-maroon border border-line rounded-sm px-3 py-1.5 cursor-pointer disabled:opacity-40 disabled:cursor-default hover:bg-maroon/5"
          :disabled="page === 1"
          @click="page--"
        >
          ‹ Prev
        </button>
        <span class="font-sans text-[13px] text-muted">Page {{ page }} of {{ pageCount }}</span>
        <button
          class="font-sans text-[13px] text-maroon border border-line rounded-sm px-3 py-1.5 cursor-pointer disabled:opacity-40 disabled:cursor-default hover:bg-maroon/5"
          :disabled="page === pageCount"
          @click="page++"
        >
          Next ›
        </button>
      </div>
    </template>
  </div>
</template>
