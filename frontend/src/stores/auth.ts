import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { authApi } from "@/api/auth";
import type { User } from "@/types/models";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(localStorage.getItem("tdc_token"));
  const stored = localStorage.getItem("tdc_user");
  const user = ref<User | null>(stored ? JSON.parse(stored) : null);

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === "admin");

  async function login(username: string, password: string) {
    const res = await authApi.login(username, password);
    token.value = res.access_token;
    user.value = res.user;
    localStorage.setItem("tdc_token", res.access_token);
    localStorage.setItem("tdc_user", JSON.stringify(res.user));
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem("tdc_token");
    localStorage.removeItem("tdc_user");
  }

  return { token, user, isAuthenticated, isAdmin, login, logout };
});
