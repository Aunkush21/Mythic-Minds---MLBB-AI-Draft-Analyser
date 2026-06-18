import { cn } from "@/lib/utils";
import { useUiStore } from "@/store/uiStore";

export function ExplainModeToggle() {
  const mode = useUiStore((s) => s.explanationMode);
  const setMode = useUiStore((s) => s.setExplanationMode);

  return (
    <div className="glass-panel inline-flex items-center rounded-full p-1 text-xs">
      {(["beginner", "advanced"] as const).map((option) => (
        <button
          key={option}
          onClick={() => setMode(option)}
          className={cn(
            "rounded-full px-3 py-1 font-medium capitalize transition-colors",
            mode === option ? "bg-accent/20 text-accent" : "text-muted hover:text-foreground"
          )}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
