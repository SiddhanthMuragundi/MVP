export type Role = "admin" | "matchmaker";

export type JourneyStage =
  | "new"
  | "verified"
  | "matching"
  | "matches_sent"
  | "in_conversation"
  | "meeting"
  | "on_hold"
  | "closed";

export type MatchTier = "high" | "promising" | "possible";
export type MatchStatus =
  | "suggested"
  | "shortlisted"
  | "sent"
  | "accepted"
  | "declined"
  | "no_response"
  | "withdrawn";
export type LLMProvider = "openai" | "anthropic" | "gemini";
export type ChatIntent = "search" | "ask" | "draft" | "unknown";

export interface User {
  id: number;
  username: string;
  display_name: string;
  role: Role;
}

export interface FilterOptions {
  states: string[];
  cities_by_state: Record<string, string[]>;
  cities: string[];
  languages: string[];
  religions: string[];
  marital_statuses: string[];
}

export interface CustomerListItem {
  id: number;
  first_name: string;
  last_name: string;
  age: number;
  city: string;
  state: string | null;
  marital_status: string;
  journey_stage: JourneyStage | null;
  verified: boolean;
  photo_url: string;
  assigned_matchmaker_id: number | null;
  assigned_matchmaker_name: string | null;
  mine: boolean;
}

export interface Profile {
  id: number;
  first_name: string;
  last_name: string;
  gender: string;
  dob: string;
  age: number;
  country: string;
  city: string;
  height_cm: number;
  email: string;
  phone: string;
  ug_college: string;
  degree: string;
  income_lpa: number;
  company: string;
  designation: string;
  marital_status: string;
  languages_known: string[];
  siblings: number;
  caste: string;
  religion: string;
  mother_tongue: string;
  manglik: string;
  want_kids: string;
  open_to_relocate: string;
  open_to_pets: string;
  diet: string;
  smoking: string;
  drinking: string;
  family_type: string;
  hobbies: string[];
  bio: string;
  photo_url: string;
  verified: boolean;
  journey_stage: JourneyStage | null;
}

export interface Note {
  id: number;
  body: string;
  author_name: string;
  created_at: string;
}

export interface Matchmaker {
  id: number;
  display_name: string;
  client_count: number;
}

export interface Activity {
  id: number;
  actor_user_id: number | null;
  actor_name: string;
  target_user_id: number | null;
  target_name: string | null;
  customer_id: number | null;
  action: string;
  message: string;
  created_at: string;
}

export interface NotificationsResponse {
  items: Activity[];
  unread_count: number;
  has_more: boolean;
}

export interface CustomerDetail extends Profile {
  notes: Note[];
  mine: boolean;
  editable: boolean;
  assigned_matchmaker_id: number | null;
  assigned_matchmaker_name: string | null;
}

export interface Match {
  id: number | null;
  candidate: Profile;
  score: number;
  tier: MatchTier;
  reasons: string[];
  ai_explanation: string | null;
  status: MatchStatus;
}

export interface EmailDraft {
  to: string;
  subject: string;
  body: string;
  candidate_summary: {
    name: string;
    age: number;
    city: string;
    designation: string;
    company: string;
    marital_status: string;
    photo_url: string;
  };
}

export interface LLMSettings {
  provider: LLMProvider | null;
  model: string | null;
  configured: boolean;
  masked_key: string | null;
  updated_at: string | null;
}

export interface ChatResponse {
  reply: string;
  intent: ChatIntent;
  matches: Match[] | null;
  ai_used: boolean;
  ai_error: string | null;
}
