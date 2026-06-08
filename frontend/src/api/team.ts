import api from "./client";
import type { Matchmaker } from "@/types/models";

export const teamApi = {
  async listMatchmakers() {
    const { data } = await api.get<Matchmaker[]>("/matchmakers");
    return data;
  },
};
