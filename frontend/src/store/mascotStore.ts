import { create } from "zustand";

export type MascotEmotion =
  | "idle"
  | "happy"
  | "angry"
  | "confused"
  | "thinking"
  | "lowHealth"
  | "recalling";

interface MascotState {
  emotion: MascotEmotion;
  message: string | null;
  react: (emotion: MascotEmotion, message?: string, durationMs?: number) => void;
  setThinking: (active: boolean) => void;
  goLowHealth: () => void;
  recall: () => void;
}

const RECALL_DURATION_MS = 5000;

const RECALL_LINES = [
  "Full HP! Let's clutch this!",
  "Back in the fight — recall complete!",
  "Healed up and ready to carry!",
  "Like nothing happened. Let's go!",
];

let revertTimer: ReturnType<typeof setTimeout> | null = null;

export const useMascotStore = create<MascotState>((set, get) => ({
  emotion: "idle",
  message: null,

  react: (emotion, message, durationMs = 4500) => {
    if (revertTimer) clearTimeout(revertTimer);
    set({ emotion, message: message ?? null });
    if (emotion !== "idle") {
      revertTimer = setTimeout(() => set({ emotion: "idle", message: null }), durationMs);
    }
  },

  setThinking: (active) => {
    if (active) {
      if (revertTimer) clearTimeout(revertTimer);
      set({ emotion: "thinking", message: null });
    } else {
      set((state) => (state.emotion === "thinking" ? { emotion: "idle" } : state));
    }
  },

  goLowHealth: () => {
    if (revertTimer) clearTimeout(revertTimer);
    set({ emotion: "lowHealth", message: "I'm low on health... tap to recall!" });
  },

  recall: () => {
    if (get().emotion !== "lowHealth") return;
    if (revertTimer) clearTimeout(revertTimer);
    set({ emotion: "recalling", message: null });
    revertTimer = setTimeout(() => {
      const line = RECALL_LINES[Math.floor(Math.random() * RECALL_LINES.length)];
      set({ emotion: "happy", message: line });
      revertTimer = setTimeout(() => set({ emotion: "idle", message: null }), 4500);
    }, RECALL_DURATION_MS);
  },
}));
