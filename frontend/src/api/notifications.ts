import api from "./client";
import type { NotificationsResponse } from "@/types/models";

export const notificationsApi = {
  async list(beforeId?: number, limit = 5) {
    const { data } = await api.get<NotificationsResponse>("/notifications", {
      params: { before_id: beforeId, limit },
    });
    return data;
  },
  async clear() {
    await api.post("/notifications/clear");
  },
};
