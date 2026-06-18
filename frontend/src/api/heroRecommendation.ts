import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { HeroPickRequest, HeroPickResponse } from "@/types/api";

export function useHeroRecommendation(request: HeroPickRequest | null) {
  return useQuery({
    queryKey: ["recommendations", "hero-pick", request],
    queryFn: async () =>
      (await apiClient.post<HeroPickResponse>("/recommendations/hero-pick", request)).data,
    enabled: request !== null,
    retry: false,
  });
}
