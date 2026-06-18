import { AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

export function ErrorBanner({ message, className }: { message: string; className?: string }) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-xl border border-enemy/30 bg-enemy/10 px-4 py-3 text-sm text-enemy",
        className
      )}
    >
      <AlertTriangle size={16} className="shrink-0" />
      <span>{message}</span>
    </div>
  );
}
