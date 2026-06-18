import { cn } from "@/lib/utils";
import { useCountUp } from "@/lib/useCountUp";

export function StatBar({
  label,
  value,
  max = 100,
  colorClass = "bg-accent",
  suffix = "",
}: {
  label: string;
  value: number;
  max?: number;
  colorClass?: string;
  suffix?: string;
}) {
  const animatedValue = useCountUp(value);
  const pct = Math.max(0, Math.min(100, (animatedValue / max) * 100));

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs text-muted">
        <span>{label}</span>
        <span className="font-display font-semibold text-foreground">
          {Math.round(animatedValue)}
          {suffix}
        </span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-glass-fill-strong">
        <div
          className={cn("h-full rounded-full shadow-[0_0_8px_currentColor] transition-[width]", colorClass)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
