import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: () => import("@/views/LoginView.vue"), meta: { public: true } },
    { path: "/", name: "home", component: () => import("@/views/HomeView.vue") },
    { path: "/matchmaking", name: "dashboard", component: () => import("@/views/DashboardView.vue") },
    { path: "/about", name: "about", component: () => import("@/views/AboutView.vue") },
    { path: "/customers/:id", name: "customer", component: () => import("@/views/CustomerDetailView.vue"), props: true },
    { path: "/settings", name: "settings", component: () => import("@/views/SettingsView.vue"), meta: { admin: true } },
    { path: "/:pathMatch(.*)*", name: "not-found", component: () => import("@/views/NotFoundView.vue") },
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: "login" };
  }
  if (to.meta.public && auth.isAuthenticated) {
    return { name: "home" };
  }
  if (to.meta.admin && !auth.isAdmin) {
    return { name: "home" };
  }
  return true;
});

export default router;
