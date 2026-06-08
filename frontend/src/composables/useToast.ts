import { reactive } from "vue";

export interface Toast {
  id: number;
  message: string;
  kind: "success" | "error";
}

const state = reactive<{ toasts: Toast[] }>({ toasts: [] });
let counter = 0;

export function useToast() {
  function push(message: string, kind: Toast["kind"] = "success") {
    const id = ++counter;
    state.toasts.push({ id, message, kind });
    setTimeout(() => dismiss(id), 3200);
  }
  function dismiss(id: number) {
    const i = state.toasts.findIndex((t) => t.id === id);
    if (i !== -1) state.toasts.splice(i, 1);
  }
  return { toasts: state.toasts, success: (m: string) => push(m, "success"), error: (m: string) => push(m, "error"), dismiss };
}
