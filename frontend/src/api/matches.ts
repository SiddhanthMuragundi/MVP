import api from "./client";
import type { EmailDraft } from "@/types/models";

export const matchesApi = {
  async draft(customerId: number, candidateId: number) {
    const { data } = await api.post<{ email: EmailDraft }>("/matches/draft", {
      customer_id: customerId,
      candidate_id: candidateId,
    });
    return data.email;
  },
  async send(
    customerId: number,
    candidateId: number,
    edit?: { subject?: string; body?: string; resend?: boolean },
  ) {
    const { data } = await api.post<{ ok: boolean; email: EmailDraft }>("/matches/send", {
      customer_id: customerId,
      candidate_id: candidateId,
      subject: edit?.subject,
      body: edit?.body,
      resend: edit?.resend,
    });
    return data;
  },
};
