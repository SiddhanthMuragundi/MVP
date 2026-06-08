import api from "./client";
import type { User } from "@/types/models";

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  async login(username: string, password: string) {
    const { data } = await api.post<LoginResponse>("/auth/login", { username, password });
    return data;
  },
  async me() {
    const { data } = await api.get<User>("/auth/me");
    return data;
  },
};
