import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip } from "@/components/ui/Tooltip";
import type { ConfidenceSchema } from "@/types/api";

const LEVEL_CLASS: Record<string, string> = {
  high: "text-positive border-positive/40",
  medium: "text-gold border-gold/40",
  low: "text-neutral border-neutral/40",
};

export function ConfidenceBadge({ confidence }: { confidence: ConfidenceSchema }) {
  return (
    <Tooltip content={confidence.basis}>
      <span
        className={cn(
          "inline-flex cursor-help items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium",
          LEVEL_CLASS[confidence.level] ?? LEVEL_CLASS.medium
        )}
      >
        <ShieldCheck size={12} />
        {confidence.level} confidence
      </span>
    </Tooltip>
  );
}
