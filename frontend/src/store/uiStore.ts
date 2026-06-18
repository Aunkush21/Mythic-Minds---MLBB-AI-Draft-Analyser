import { create } from "zustand";

export type Theme = "dark" | "light";
export type ExplanationMode = "beginner" | "advanced";

const THEME_KEY = "nexus-theme";
const EXPLAIN_KEY = "nexus-explain-mode";

function readStoredTheme(): Theme {
  const stored = localStorage.getItem(THEME_KEY);
  return stored === "light" || stored === "dark" ? stored : "dark";
}

function readStoredExplainMode(): ExplanationMode {
  const stored = localStorage.getItem(EXPLAIN_KEY);
  return stored === "advanced" || stored === "beginner" ? stored : "beginner";
}

interface UiState {
  theme: Theme;
  explanationMode: ExplanationMode;
  toggleTheme: () => void;
  setExplanationMode: (mode: ExplanationMode) => void;
}

export const useUiStore = create<UiState>((set, get) => ({
  theme: readStoredTheme(),
  explanationMode: readStoredExplainMode(),

  toggleTheme: () => {
    const next: Theme = get().theme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem(THEME_KEY, next);
    set({ theme: next });
  },

  setExplanationMode: (mode) => {
    localStorage.setItem(EXPLAIN_KEY, mode);
    set({ explanationMode: mode });
  },
}));
