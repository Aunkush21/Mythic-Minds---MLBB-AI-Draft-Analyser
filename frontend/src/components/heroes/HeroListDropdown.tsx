import { useEffect, useLayoutEffect, useRef, useState, type RefObject } from "react";
import { createPortal } from "react-dom";
import { HeroAvatar } from "./HeroAvatar";
import type { HeroSummary } from "@/types/api";

export function HeroListDropdown({
  heroes,
  excludeIds = [],
  onSelect,
  onClose,
  anchorRef,
}: {
  heroes: HeroSummary[];
  excludeIds?: number[];
  onSelect: (heroId: number) => void;
  onClose?: () => void;
  anchorRef: RefObject<HTMLElement | null>;
}) {
  const [search, setSearch] = useState("");
  const panelRef = useRef<HTMLDivElement>(null);
  const [coords, setCoords] = useState<{ top: number; left: number } | null>(null);

  useLayoutEffect(() => {
    const width = 256;
    function updatePosition() {
      const anchor = anchorRef.current;
      if (!anchor) return;
      const rect = anchor.getBoundingClientRect();
      const left = Math.min(rect.left, window.innerWidth - width - 12);
      setCoords({ top: rect.bottom + 8, left: Math.max(12, left) });
    }
    updatePosition();
    window.addEventListener("scroll", updatePosition, true);
    window.addEventListener("resize", updatePosition);
    return () => {
      window.removeEventListener("scroll", updatePosition, true);
      window.removeEventListener("resize", updatePosition);
    };
  }, [anchorRef]);

  useEffect(() => {
    if (!onClose) return;
    const close = onClose;
    function handlePointerDown(e: PointerEvent) {
      const target = e.target as Node;
      if (panelRef.current?.contains(target)) return;
      if (anchorRef.current?.contains(target)) return;
      close();
    }
    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [onClose, anchorRef]);

  const filtered = heroes.filter(
    (h) => !excludeIds.includes(h.id) && h.name.toLowerCase().includes(search.toLowerCase())
  );

  if (!coords) return null;

  return createPortal(
    <div
      ref={panelRef}
      className="glass-panel-solid fixed z-50 w-64 rounded-xl p-3 shadow-xl"
      style={{ top: coords.top, left: coords.left }}
    >
      <input
        autoFocus
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search hero..."
        className="mb-2 w-full rounded-lg bg-glass-fill px-3 py-1.5 text-sm outline-none placeholder:text-muted"
      />
      <div className="max-h-64 space-y-1 overflow-y-auto">
        {filtered.map((hero) => (
          <button
            key={hero.id}
            onClick={() => onSelect(hero.id)}
            className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm hover:bg-glass-fill"
          >
            <HeroAvatar name={hero.name} role={hero.role} size={28} />
            {hero.name}
          </button>
        ))}
        {!filtered.length && <p className="px-2 py-1.5 text-sm text-muted">No heroes found.</p>}
      </div>
    </div>,
    document.body
  );
}
