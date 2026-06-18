import { create } from "zustand";
import type { LanePicks } from "@/types/api";

export type Lane = keyof LanePicks;
export type Side = "ally" | "enemy";

const EMPTY_LANES: LanePicks = { exp: null, gold: null, mid: null, jungle: null, roam: null };

interface DraftState {
  allyPicks: LanePicks;
  enemyPicks: LanePicks;
  allyBans: number[];
  enemyBans: number[];
  patchVersion: string;
  rank: string;

  setPick: (side: Side, lane: Lane, heroId: number) => void;
  clearPick: (side: Side, lane: Lane) => void;
  toggleBan: (side: Side, heroId: number) => void;
  setPatchVersion: (patch: string) => void;
  setRank: (rank: string) => void;
  resetDraft: () => void;
}

export const useDraftStore = create<DraftState>((set, get) => ({
  allyPicks: { ...EMPTY_LANES },
  enemyPicks: { ...EMPTY_LANES },
  allyBans: [],
  enemyBans: [],
  patchVersion: "1.9.0",
  rank: "Mythic",

  setPick: (side, lane, heroId) =>
    set((state) =>
      side === "ally"
        ? { allyPicks: { ...state.allyPicks, [lane]: heroId } }
        : { enemyPicks: { ...state.enemyPicks, [lane]: heroId } }
    ),

  clearPick: (side, lane) =>
    set((state) =>
      side === "ally"
        ? { allyPicks: { ...state.allyPicks, [lane]: null } }
        : { enemyPicks: { ...state.enemyPicks, [lane]: null } }
    ),

  toggleBan: (side, heroId) => {
    const key = side === "ally" ? "allyBans" : "enemyBans";
    const current = get()[key];
    set({
      [key]: current.includes(heroId) ? current.filter((id) => id !== heroId) : [...current, heroId],
    });
  },

  setPatchVersion: (patchVersion) => set({ patchVersion }),
  setRank: (rank) => set({ rank }),

  resetDraft: () =>
    set({
      allyPicks: { ...EMPTY_LANES },
      enemyPicks: { ...EMPTY_LANES },
      allyBans: [],
      enemyBans: [],
    }),
}));

export function filledHeroIds(state: Pick<DraftState, "allyPicks" | "enemyPicks" | "allyBans" | "enemyBans">) {
  return [
    ...Object.values(state.allyPicks),
    ...Object.values(state.enemyPicks),
    ...state.allyBans,
    ...state.enemyBans,
  ].filter((id): id is number => id !== null && id !== undefined);
}

export function isDraftComplete(picks: LanePicks) {
  return Object.values(picks).every((id) => id !== null && id !== undefined);
}
