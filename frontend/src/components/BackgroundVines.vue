<script setup lang="ts">
/**
 * Decorative corner vine flourishes for background beautification only.
 * Gold vines, marigold flower buds and soft leaves — a traditional Indian
 * matrimonial-invite feel. Purely ornamental: sits behind content, never
 * intercepts clicks, and is clipped to its container so cards stay untouched.
 */
withDefaults(
  defineProps<{
    corners?: ("tl" | "tr" | "bl" | "br")[];
    opacity?: number;
    size?: number;
    stroke?: string;
    leafFill?: string;
    petal?: string;
    bud?: string;
  }>(),
  {
    corners: () => ["tl", "br"],
    opacity: 0.4,
    size: 240,
    stroke: "#C8A248",
    leafFill: "rgba(200,162,72,0.16)",
    petal: "#E8D49A",
    bud: "#E08A1E",
  },
);

// Main stem sweeps from the corner; two side branches each end in a flower.
// Leaves and buds below sit on points computed to lie exactly on these curves.
const STEMS = [
  "M-4 14 C64 28 100 72 92 146 C86 196 116 218 172 232",
  "M90 97 C68 102 56 120 54 144",
  "M72 59 C80 45 92 41 104 40",
];

const LEAVES = [
  { x: 41, y: 32, r: -52, s: 1.0 }, // main stem
  { x: 61, y: 47, r: -26, s: 1.05 },
  { x: 93, y: 116, r: 34, s: 1.05 },
  { x: 94, y: 178, r: 72, s: 1.0 },
  { x: 109, y: 202, r: 104, s: 0.92 },
  { x: 132, y: 217, r: 88, s: 0.95 },
  { x: 64, y: 113, r: 158, s: 0.9 }, // on branch 1
  { x: 86, y: 45, r: -8, s: 0.85 }, // on branch 2
];

const BUDS = [
  { x: 54, y: 144, s: 0.95 }, // branch 1 tip
  { x: 104, y: 40, s: 0.9 }, // branch 2 tip
  { x: 5, y: 15, s: 1.0 }, // corner anchor
];

const PETAL_ANGLES = [0, 72, 144, 216, 288];
const LEAF_D = "M0 0 C6 -5 7.5 -15 0 -25 C-7.5 -15 -6 -5 0 0Z";
const PETAL_D = "M0 -2 C3.2 -4 3.2 -9.5 0 -12 C-3.2 -9.5 -3.2 -4 0 -2Z";

const POS: Record<string, string> = {
  tl: "top-0 left-0",
  tr: "top-0 right-0",
  bl: "bottom-0 left-0",
  br: "bottom-0 right-0",
};
const FLIP: Record<string, string> = {
  tl: "none",
  tr: "scaleX(-1)",
  bl: "scaleY(-1)",
  br: "scale(-1,-1)",
};
</script>

<template>
  <div
    class="pointer-events-none absolute inset-0 overflow-hidden"
    aria-hidden="true"
    :style="{ opacity }"
  >
    <svg
      v-for="c in corners"
      :key="c"
      :class="['absolute', POS[c]]"
      :width="size"
      :height="size"
      viewBox="0 0 240 240"
      fill="none"
      :style="{ transform: FLIP[c] }"
    >
      <g :stroke="stroke" stroke-width="1.3" stroke-linecap="round" fill="none">
        <path v-for="(d, i) in STEMS" :key="i" :d="d" />
      </g>
      <g :fill="leafFill" :stroke="stroke" stroke-width="0.8">
        <path
          v-for="(l, i) in LEAVES"
          :key="i"
          :d="LEAF_D"
          :transform="`translate(${l.x} ${l.y}) rotate(${l.r}) scale(${l.s})`"
        />
      </g>
      <g v-for="(b, i) in BUDS" :key="i" :transform="`translate(${b.x} ${b.y}) scale(${b.s})`">
        <path
          v-for="a in PETAL_ANGLES"
          :key="a"
          :d="PETAL_D"
          :fill="petal"
          :transform="`rotate(${a})`"
        />
        <circle cx="0" cy="0" r="2.4" :fill="bud" />
      </g>
    </svg>
  </div>
</template>
