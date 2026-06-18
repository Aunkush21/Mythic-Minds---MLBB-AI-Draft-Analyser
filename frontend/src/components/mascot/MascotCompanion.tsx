import { useEffect, useRef, useState } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMascotStore } from "@/store/mascotStore";
import { MASCOT_FAQ, type MascotFaqItem } from "@/data/mascotFaq";

const ANIMATION_CLASS: Record<string, string> = {
  idle: "animate-mascot-idle",
  happy: "animate-mascot-happy",
  angry: "animate-mascot-angry",
  confused: "animate-mascot-confused",
  thinking: "animate-mascot-idle",
  lowHealth: "animate-mascot-idle animate-pulse-low-health",
  recalling: "animate-mascot-recall",
};

const RING_CLASS: Record<string, string> = {
  idle: "ring-glass-border",
  happy: "ring-gold/60",
  angry: "ring-enemy/60",
  confused: "ring-neutral/50",
  thinking: "ring-accent/60",
  lowHealth: "ring-enemy/70",
  recalling: "ring-accent/80",
};

const LOW_HEALTH_MIN_DELAY_MS = 90_000;
const LOW_HEALTH_MAX_DELAY_MS = 180_000;

interface ChatThreadEntry {
  key: string;
  question: string;
  answer: string;
}

export function MascotCompanion() {
  const emotion = useMascotStore((s) => s.emotion);
  const message = useMascotStore((s) => s.message);
  const recall = useMascotStore((s) => s.recall);

  const [chatOpen, setChatOpen] = useState(false);
  const [thread, setThread] = useState<ChatThreadEntry[]>([]);
  const threadRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: "smooth" });
  }, [thread]);

  const askQuestion = (item: MascotFaqItem) => {
    setThread((prev) => [...prev, { key: `${item.id}-${prev.length}`, question: item.question, answer: item.answer }]);
  };

  const closeChat = () => {
    setChatOpen(false);
    setThread([]);
  };

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;

    const scheduleNext = () => {
      const delay = LOW_HEALTH_MIN_DELAY_MS + Math.random() * (LOW_HEALTH_MAX_DELAY_MS - LOW_HEALTH_MIN_DELAY_MS);
      timer = setTimeout(() => {
        if (useMascotStore.getState().emotion === "idle") {
          useMascotStore.getState().goLowHealth();
        }
        scheduleNext();
      }, delay);
    };

    scheduleNext();
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="pointer-events-none fixed bottom-6 right-6 z-40 flex flex-col items-end gap-2">
      {chatOpen ? (
        <div className="glass-panel-strong pointer-events-auto flex max-h-96 w-72 max-w-[90vw] flex-col overflow-hidden rounded-2xl shadow-lg">
          <div className="flex shrink-0 items-center justify-between border-b border-glass-border px-4 py-2">
            <span className="font-display text-sm font-semibold text-foreground">Ask Yss</span>
            <button
              onClick={closeChat}
              aria-label="Close chat"
              className="text-muted transition-colors hover:text-accent"
            >
              <X size={14} />
            </button>
          </div>
          <div ref={threadRef} className="min-h-0 flex-1 space-y-2 overflow-y-auto px-3 py-2">
            {thread.length === 0 && (
              <p className="text-xs text-muted">Tap a question below and I'll answer!</p>
            )}
            {thread.map((entry) => (
              <div key={entry.key} className="space-y-1">
                <div className="ml-auto max-w-[85%] rounded-xl rounded-br-sm bg-accent/20 px-3 py-1.5 text-xs text-foreground">
                  {entry.question}
                </div>
                <div className="mr-auto max-w-[85%] rounded-xl rounded-bl-sm bg-glass-fill px-3 py-1.5 text-xs text-foreground">
                  {entry.answer}
                </div>
              </div>
            ))}
            <div className="flex flex-wrap gap-1.5 border-t border-glass-border pt-2">
              {MASCOT_FAQ.map((item) => (
                <button
                  key={item.id}
                  onClick={() => askQuestion(item)}
                  className="rounded-full border border-glass-border bg-glass-fill px-2.5 py-1 text-[11px] text-muted transition-colors hover:border-accent/50 hover:text-accent"
                >
                  {item.question}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        message && (
          <div className="glass-panel-strong pointer-events-auto max-w-56 rounded-2xl rounded-br-sm px-4 py-2 text-sm text-foreground shadow-lg">
            {message}
          </div>
        )
      )}
      <div
        onClick={() => {
          if (emotion === "lowHealth") {
            recall();
            return;
          }
          if (chatOpen) {
            closeChat();
          } else {
            setChatOpen(true);
          }
        }}
        className={cn(
          "glass-panel-strong pointer-events-auto relative flex h-20 w-20 cursor-pointer items-center justify-center rounded-full shadow-lg ring-2 transition-shadow duration-300",
          RING_CLASS[emotion],
          ANIMATION_CLASS[emotion]
        )}
      >
        <img src="/assets/mascot/yss-chibi.png" alt="Yss" className="h-16 w-16 object-contain" draggable={false} />
        {emotion === "thinking" && (
          <div className="absolute -right-1 -top-1 h-5 w-5 animate-[mascot-spin-slow_1s_linear_infinite] rounded-full border-2 border-accent border-t-transparent bg-background" />
        )}
        {emotion === "lowHealth" && (
          <div className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-enemy text-[10px] font-bold text-background shadow-md">
            !
          </div>
        )}
      </div>
    </div>
  );
}
