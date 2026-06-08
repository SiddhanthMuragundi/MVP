import api from "./client";
import type { ChatResponse } from "@/types/models";

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export const chatApi = {
  async send(message: string, clientId?: number | null, history: ChatTurn[] = []) {
    const { data } = await api.post<ChatResponse>("/chat", {
      message,
      client_id: clientId ?? null,
      history,
    });
    return data;
  },
};
