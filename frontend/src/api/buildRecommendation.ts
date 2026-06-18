import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { BuildRequest, BuildResponse } from "@/types/api";

export function useBuildRecommendation(request: BuildRequest | null) {
  return useQuery({
    queryKey: ["recommendations", "build", request],
    queryFn: async () =>
      (await apiClient.post<BuildResponse>("/recommendations/build", request)).data,
    enabled: request !== null,
    retry: false,
  });
}
