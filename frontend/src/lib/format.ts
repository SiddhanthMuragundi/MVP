import type { JourneyStage, MatchTier, Profile } from "@/types/models";

export function humanize(value: string | null | undefined): string {
  if (!value) return "";
  return value.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

export interface BiodataSection {
  title: string;
  fields: { label: string; value: string | number | null | undefined }[];
}

export function profileSections(c: Profile): BiodataSection[] {
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
}

export const STAGES: { value: JourneyStage; label: string }[] = [
  { value: "new", label: "New" },
  { value: "verified", label: "Profile Verified" },
  { value: "matching", label: "Active / Matching" },
  { value: "matches_sent", label: "Matches Sent" },
  { value: "in_conversation", label: "In Conversation" },
  { value: "meeting", label: "Meeting Scheduled" },
  { value: "on_hold", label: "On Hold" },
  { value: "closed", label: "Matched / Closed" },
];

// Gender is a fixed binary domain (not data-derived); state/city/language/religion/
// marital options are fetched live from the API (see customersApi.filterOptions).
export const GENDERS = [
  { value: "male", label: "Male" },
  { value: "female", label: "Female" },
];

const STAGE_COLORS: Record<JourneyStage, string> = {
  new: "#9A8B7C",
  verified: "#5E7B5A",
  matching: "#C4684E",
  matches_sent: "#C99B46",
  in_conversation: "#5B8BA0",
  meeting: "#8A6BA0",
  on_hold: "#B0A89C",
  closed: "#4A7C59",
};

export function stageLabel(stage: JourneyStage | null | undefined): string {
  if (!stage) return "-";
  return STAGES.find((s) => s.value === stage)?.label ?? humanize(stage);
}

export function stageColor(stage: JourneyStage | null | undefined): string {
  return stage ? STAGE_COLORS[stage] : "#9A7C6A";
}

const TIER_COLORS: Record<MatchTier, string> = {
  high: "#7A1730",
  promising: "#C8A248",
  possible: "#9A7C6A",
};

const TIER_LABELS: Record<MatchTier, string> = {
  high: "High Potential",
  promising: "Promising",
  possible: "Possible",
};

export const tierColor = (tier: MatchTier) => TIER_COLORS[tier];
export const tierLabel = (tier: MatchTier) => TIER_LABELS[tier];
