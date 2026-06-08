<script setup lang="ts">
const year = new Date().getFullYear();
</script>

<template>
  <footer class="border-t border-line bg-card-warm/60">
    <div
      class="max-w-[1100px] mx-auto px-4 sm:px-6 py-3 flex flex-col sm:flex-row items-center justify-center gap-x-2 text-center"
    >
      <p class="font-sans text-xs text-maroon-ink">&copy; {{ year }} Saathiya &middot; Matchmaker Studio</p>
      <span class="hidden sm:inline text-line">&middot;</span>
      <p class="font-sans text-[11px] text-muted">For authorised matchmakers</p>
    </div>
  </footer>
</template>
