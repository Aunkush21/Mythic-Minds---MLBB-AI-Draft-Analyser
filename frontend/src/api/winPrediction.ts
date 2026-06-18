import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { WinPredictionRequest, WinPredictionResponse } from "@/types/api";

export function useWinPrediction(request: WinPredictionRequest | null) {
  return useQuery({
    queryKey: ["predict", "win-probability", request],
    queryFn: async () =>
      (await apiClient.post<WinPredictionResponse>("/predict/win-probability", request)).data,
    enabled: request !== null,
    retry: false,
  });
}
