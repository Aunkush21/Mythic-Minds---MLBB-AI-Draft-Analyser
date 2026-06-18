import { useQueries, useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";
import type {
  BattleSpellSummary,
  EmblemSummary,
  HeroCounterEntry,
  HeroDetail,
  HeroSummary,
  ItemSummary,
  PatchSummary,
  SimilarHeroEntry,
} from "@/types/api";

const STATIC_STALE_TIME = Infinity;

export function useHeroes() {
  return useQuery({
    queryKey: ["heroes"],
    queryFn: async () => (await apiClient.get<HeroSummary[]>("/heroes")).data,
    staleTime: STATIC_STALE_TIME,
  });
}

export function useHero(heroId: number | undefined) {
  return useQuery({
    queryKey: ["heroes", heroId],
    queryFn: async () => (await apiClient.get<HeroDetail>(`/heroes/${heroId}`)).data,
    enabled: heroId !== undefined,
    staleTime: STATIC_STALE_TIME,
  });
}

export function useAllHeroDetails(heroIds: number[] | undefined) {
  return useQueries({
    queries: (heroIds ?? []).map((heroId) => ({
      queryKey: ["heroes", heroId],
      queryFn: async () => (await apiClient.get<HeroDetail>(`/heroes/${heroId}`)).data,
      staleTime: STATIC_STALE_TIME,
    })),
  });
}

export function useSimilarHeroes(heroId: number | undefined, limit = 5) {
  return useQuery({
    queryKey: ["heroes", heroId, "similar", limit],
    queryFn: async () =>
      (await apiClient.get<SimilarHeroEntry[]>(`/heroes/${heroId}/similar`, { params: { limit } })).data,
    enabled: heroId !== undefined,
    staleTime: STATIC_STALE_TIME,
  });
}

export function useItems() {
  return useQuery({
    queryKey: ["items"],
    queryFn: async () => (await apiClient.get<ItemSummary[]>("/items")).data,
    staleTime: STATIC_STALE_TIME,
  });
}

export function useEmblems() {
  return useQuery({
    queryKey: ["emblems"],
    queryFn: async () => (await apiClient.get<EmblemSummary[]>("/emblems")).data,
    staleTime: STATIC_STALE_TIME,
  });
}

export function useBattleSpells() {
  return useQuery({
    queryKey: ["battle-spells"],
    queryFn: async () => (await apiClient.get<BattleSpellSummary[]>("/battle-spells")).data,
    staleTime: STATIC_STALE_TIME,
  });
}

export function usePatches() {
  return useQuery({
    queryKey: ["patches"],
    queryFn: async () => (await apiClient.get<PatchSummary[]>("/patches")).data,
    staleTime: STATIC_STALE_TIME,
  });
}

export function useCurrentPatch() {
  return useQuery({
    queryKey: ["patches", "current"],
    queryFn: async () => (await apiClient.get<PatchSummary>("/patches/current")).data,
    staleTime: STATIC_STALE_TIME,
  });
}

export function useCounters() {
  return useQuery({
    queryKey: ["counters"],
    queryFn: async () => (await apiClient.get<HeroCounterEntry[]>("/counters")).data,
    staleTime: STATIC_STALE_TIME,
  });
}
