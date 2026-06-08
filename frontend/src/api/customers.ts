import api from "./client";
import type {
  CustomerDetail,
  CustomerListItem,
  FilterOptions,
  JourneyStage,
  Match,
  Note,
  Profile,
} from "@/types/models";

export const customersApi = {
  async list(
    filters: {
      search?: string;
      stage?: JourneyStage;
      verified?: boolean;
      state?: string;
      city?: string;
      religion?: string;
      language?: string;
      gender?: string;
      marital_status?: string;
      age_min?: number;
      age_max?: number;
      mine?: boolean;
    } = {},
  ) {
    const { data } = await api.get<CustomerListItem[]>("/customers", { params: filters });
    return data;
  },
  async filterOptions() {
    const { data } = await api.get<FilterOptions>("/customers/filter-options");
    return data;
  },
  async get(id: number) {
    const { data } = await api.get<CustomerDetail>(`/customers/${id}`);
    return data;
  },
  async updateStage(id: number, journey_stage: JourneyStage) {
    const { data } = await api.patch<Profile>(`/customers/${id}/stage`, { journey_stage });
    return data;
  },
  async verify(id: number) {
    const { data } = await api.post<Profile>(`/customers/${id}/verify`);
    return data;
  },
  async assignMatchmaker(id: number, matchmakerId: number | null) {
    const { data } = await api.patch<Profile>(`/customers/${id}/matchmaker`, {
      matchmaker_id: matchmakerId,
    });
    return data;
  },
  async addNote(id: number, body: string) {
    const { data } = await api.post<Note>(`/customers/${id}/notes`, { body });
    return data;
  },
  async matches(id: number, opts: { limit?: number; refresh?: boolean; explain?: boolean } = {}) {
    const { data } = await api.get<Match[]>(`/customers/${id}/matches`, { params: opts });
    return data;
  },
  async shortlist(id: number, candidateId: number) {
    const { data } = await api.post<Match>(`/customers/${id}/matches/${candidateId}/shortlist`);
    return data;
  },
  async unshortlist(id: number, candidateId: number) {
    const { data } = await api.delete<Match>(`/customers/${id}/matches/${candidateId}/shortlist`);
    return data;
  },
  async setOutcome(id: number, candidateId: number, outcome: string) {
    const { data } = await api.post<Match>(`/customers/${id}/matches/${candidateId}/outcome`, { outcome });
    return data;
  },
};
