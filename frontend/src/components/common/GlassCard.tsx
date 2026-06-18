import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function GlassCard({
  children,
  className,
  strong = false,
  interactive = false,
}: {
  children: ReactNode;
  className?: string;
  strong?: boolean;
  interactive?: boolean;
}) {
  return (
    <div
      className={cn(
        strong ? "glass-panel-strong" : "glass-panel",
        interactive && "glass-panel-interactive",
        "rounded-2xl p-5",
        className
      )}
    >
      {children}
    </div>
  );
}
