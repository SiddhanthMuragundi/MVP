import api from "./client";
import type { LLMProvider, LLMSettings } from "@/types/models";

export const settingsApi = {
  async getLLM() {
    const { data } = await api.get<LLMSettings>("/settings/llm");
    return data;
  },
  async updateLLM(payload: { provider: LLMProvider; api_key?: string | null; model?: string | null }) {
    const { data } = await api.put<LLMSettings>("/settings/llm", payload);
    return data;
  },
  async removeLLM() {
    const { data } = await api.delete<LLMSettings>("/settings/llm");
    return data;
  },
  async models(provider: LLMProvider, apiKey?: string) {
    const { data } = await api.get<{ models: string[] }>("/settings/llm/models", {
      params: { provider, api_key: apiKey },
    });
    return data.models;
  },
};
