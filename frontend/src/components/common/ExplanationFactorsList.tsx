import { Minus, TrendingDown, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { useUiStore } from "@/store/uiStore";
import { ConfidenceBadge } from "./ConfidenceBadge";
import type { ExplanationSchema } from "@/types/api";

const DIRECTION_ICON = {
  positive: TrendingUp,
  negative: TrendingDown,
  neutral: Minus,
};

const DIRECTION_CLASS = {
  positive: "text-positive",
  negative: "text-negative",
  neutral: "text-neutral",
};

export function ExplanationFactorsList({ explanation }: { explanation: ExplanationSchema }) {
  const mode = useUiStore((s) => s.explanationMode);

  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm text-foreground">{explanation.summary}</p>
        <ConfidenceBadge confidence={explanation.confidence} />
      </div>

      {mode === "advanced" && (
        <ul className="space-y-2 border-t border-glass-border pt-3">
          {(explanation.factors ?? []).map((factor) => {
            const Icon = DIRECTION_ICON[factor.direction as keyof typeof DIRECTION_ICON] ?? Minus;
            const colorClass =
              DIRECTION_CLASS[factor.direction as keyof typeof DIRECTION_CLASS] ?? "text-neutral";
            return (
              <li key={factor.label} className="flex items-start gap-2 text-xs">
                <Icon size={14} className={cn("mt-0.5 shrink-0", colorClass)} />
                <span className="text-muted">{factor.description}</span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
