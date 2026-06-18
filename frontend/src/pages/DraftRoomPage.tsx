import { useEffect, useMemo, useRef, useState } from "react";
import { Ban, Plus, RotateCcw, Sparkles, Swords, X } from "lucide-react";
import { useCounters, useHeroes, usePatches } from "@/api/referenceData";
import { useHeroRecommendation } from "@/api/heroRecommendation";
import { useWinPrediction } from "@/api/winPrediction";
import { useDraftStore, filledHeroIds, isDraftComplete, type Lane, type Side } from "@/store/draftStore";
import { useMascotStore } from "@/store/mascotStore";
import { useCountUp } from "@/lib/useCountUp";
import { GlassCard } from "@/components/common/GlassCard";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { ExplainModeToggle } from "@/components/common/ExplainModeToggle";
import { ExplanationFactorsList } from "@/components/common/ExplanationFactorsList";
import { HeroAvatar } from "@/components/heroes/HeroAvatar";
import { HeroListDropdown } from "@/components/heroes/HeroListDropdown";
import { cn } from "@/lib/utils";
import { getApiErrorMessage } from "@/api/client";
import type { BestPickEntry, CounterPickEntry, HeroSummary, SynergyPickEntry } from "@/types/api";

const LANES: { key: Lane; label: string }[] = [
  { key: "exp", label: "EXP" },
  { key: "jungle", label: "Jungle" },
  { key: "mid", label: "Mid" },
  { key: "gold", label: "Gold" },
  { key: "roam", label: "Roam" },
];

const RANKS = ["Warrior", "Elite", "Master", "Grandmaster", "Epic", "Legend", "Mythic", "Mythical Glory"];

interface SlotKey {
  side: Side;
  lane: Lane;
}

function LaneSlot({
  side,
  hero,
  isOpen,
  onToggle,
  onClear,
  heatmap,
  heroes,
  excludeIds,
  onSelect,
  onClose,
  pulse = false,
}: {
  side: Side;
  hero: HeroSummary | undefined;
  isOpen: boolean;
  onToggle: () => void;
  onClear: () => void;
  heatmap: { counters: boolean; counteredBy: boolean };
  heroes: HeroSummary[];
  excludeIds: number[];
  onSelect: (heroId: number) => void;
  onClose: () => void;
  pulse?: boolean;
}) {
  const tint = side === "ally" ? "border-ally/40 hover:border-ally" : "border-enemy/40 hover:border-enemy";
  const buttonRef = useRef<HTMLButtonElement>(null);

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={onToggle}
        className={cn(
          "glass-panel flex h-24 w-full flex-col items-center justify-center gap-1 rounded-xl border p-2 transition-all hover:scale-[1.03] active:scale-95",
          tint,
          pulse && "animate-pulse-ready border-accent"
        )}
      >
        {hero ? (
          <>
            <HeroAvatar name={hero.name} role={hero.role} size={40} />
            <span className="truncate text-xs font-medium">{hero.name}</span>
            <div className="flex gap-1">
              {heatmap.counteredBy && (
                <span title="Countered by enemy pick">
                  <Swords size={11} className="text-enemy" />
                </span>
              )}
              {heatmap.counters && (
                <span title="Counters an enemy pick">
                  <Swords size={11} className="text-positive" />
                </span>
              )}
            </div>
          </>
        ) : (
          <Plus size={20} className="text-muted" />
        )}
      </button>

      {hero && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onClear();
          }}
          className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-background text-muted shadow hover:text-enemy"
        >
          <X size={12} />
        </button>
      )}

      {isOpen && (
        <HeroListDropdown
          heroes={heroes}
          excludeIds={excludeIds}
          onSelect={onSelect}
          onClose={onClose}
          anchorRef={buttonRef}
        />
      )}
    </div>
  );
}

function BestPickRow({ entry, onPick }: { entry: BestPickEntry; onPick: (id: number) => void }) {
  return (
    <li className="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 hover:bg-glass-fill">
      <div className="min-w-0">
        <p className="truncate text-sm font-medium">{entry.hero_name}</p>
        <p className="truncate text-xs text-muted">{entry.explanation}</p>
      </div>
      <button
        onClick={() => onPick(entry.hero_id)}
        className="shrink-0 rounded-full bg-accent/20 px-3 py-1 text-xs font-medium text-accent transition-transform hover:scale-105 hover:bg-accent/30 active:scale-95"
      >
        Pick
      </button>
    </li>
  );
}

export function DraftRoomPage() {
  const { data: heroes } = useHeroes();
  const { data: counters } = useCounters();
  const { data: patches } = usePatches();

  const allyPicks = useDraftStore((s) => s.allyPicks);
  const enemyPicks = useDraftStore((s) => s.enemyPicks);
  const allyBans = useDraftStore((s) => s.allyBans);
  const enemyBans = useDraftStore((s) => s.enemyBans);
  const patchVersion = useDraftStore((s) => s.patchVersion);
  const rank = useDraftStore((s) => s.rank);
  const setPick = useDraftStore((s) => s.setPick);
  const clearPick = useDraftStore((s) => s.clearPick);
  const toggleBan = useDraftStore((s) => s.toggleBan);
  const setPatchVersion = useDraftStore((s) => s.setPatchVersion);
  const setRank = useDraftStore((s) => s.setRank);
  const resetDraft = useDraftStore((s) => s.resetDraft);

  const react = useMascotStore((s) => s.react);
  const setThinking = useMascotStore((s) => s.setThinking);

  const [openSlot, setOpenSlot] = useState<SlotKey | null>(null);
  const [openBanSide, setOpenBanSide] = useState<Side | null>(null);
  const [activeLane, setActiveLane] = useState<Lane>("exp");
  const allyBanButtonRef = useRef<HTMLButtonElement>(null);
  const enemyBanButtonRef = useRef<HTMLButtonElement>(null);

  const heroById = useMemo(() => new Map(heroes?.map((h) => [h.id, h])), [heroes]);
  const usedIds = useMemo(
    () => filledHeroIds({ allyPicks, enemyPicks, allyBans, enemyBans }),
    [allyPicks, enemyPicks, allyBans, enemyBans]
  );

  const allyComplete = isDraftComplete(allyPicks);
  const enemyComplete = isDraftComplete(enemyPicks);

  const heroPickRequest = {
    ally_picks: allyPicks,
    enemy_picks: enemyPicks,
    banned_heroes: [...allyBans, ...enemyBans],
    target_lane: activeLane,
    patch_version: patchVersion || null,
    rank_tier: rank || null,
    top_k: 5,
  };

  const {
    data: recommendation,
    isLoading: recLoading,
    isError: recIsError,
    error: recError,
  } = useHeroRecommendation(heroPickRequest);

  const winRequest =
    allyComplete && enemyComplete
      ? {
          ally_picks: allyPicks,
          enemy_picks: enemyPicks,
          ally_bans: allyBans,
          enemy_bans: enemyBans,
          patch_version: patchVersion || null,
          rank,
        }
      : null;

  const {
    data: winPrediction,
    isLoading: winLoading,
    isError: winIsError,
    error: winError,
  } = useWinPrediction(winRequest);

  const animatedWinPct = useCountUp(winPrediction ? winPrediction.win_probability * 100 : 0);

  useEffect(() => {
    setThinking(recLoading || winLoading);
  }, [recLoading, winLoading, setThinking]);

  useEffect(() => {
    if (!winPrediction) return;
    const pct = winPrediction.win_probability;
    if (pct >= 0.55) react("happy", `${Math.round(pct * 100)}% win chance — looking strong!`);
    else if (pct <= 0.45) react("angry", `${Math.round(pct * 100)}% win chance — this draft is rough.`);
  }, [winPrediction, react]);

  useEffect(() => {
    if (winIsError || recIsError) react("confused", "I don't recognize this draft combination...");
  }, [winIsError, recIsError, react]);

  function heatmapStatus(heroId: number, side: Side) {
    const opposing = Object.values(side === "ally" ? enemyPicks : allyPicks).filter(
      (id): id is number => id !== null && id !== undefined
    );
    const counteredBy = !!counters?.some(
      (c) => c.hero_id === heroId && opposing.includes(c.countered_by_id)
    );
    const countersOpp = !!counters?.some(
      (c) => opposing.includes(c.hero_id) && c.countered_by_id === heroId
    );
    return { counters: countersOpp, counteredBy };
  }

  function renderBanTray(side: Side) {
    const bans = side === "ally" ? allyBans : enemyBans;
    const banButtonRef = side === "ally" ? allyBanButtonRef : enemyBanButtonRef;
    return (
      <div className="flex flex-wrap items-center gap-2">
        {bans.map((id) => {
          const hero = heroById.get(id);
          if (!hero) return null;
          return (
            <span key={id} className="glass-panel flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs">
              <Ban size={11} className="text-enemy" />
              {hero.name}
              <button onClick={() => toggleBan(side, id)} className="text-muted hover:text-enemy">
                <X size={11} />
              </button>
            </span>
          );
        })}
        <div className="relative inline-block">
          <button
            ref={banButtonRef}
            onClick={() => setOpenBanSide(openBanSide === side ? null : side)}
            className="glass-panel flex items-center gap-1 rounded-full px-2.5 py-1 text-xs text-muted hover:text-foreground"
          >
            <Plus size={12} /> Ban
          </button>
          {openBanSide === side && (
            <HeroListDropdown
              heroes={heroes ?? []}
              excludeIds={usedIds}
              onSelect={(id) => {
                toggleBan(side, id);
                setOpenBanSide(null);
              }}
              onClose={() => setOpenBanSide(null)}
              anchorRef={banButtonRef}
            />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold">Draft Room</h1>
          <p className="text-muted">Build a full draft to get win-probability, pick, and build insights.</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={patchVersion}
            onChange={(e) => setPatchVersion(e.target.value)}
            className="glass-panel rounded-full px-3 py-1.5 text-sm outline-none"
          >
            {(patches ?? [{ patch_version: patchVersion }]).map((p) => (
              <option key={p.patch_version} value={p.patch_version}>
                {p.patch_version}
              </option>
            ))}
          </select>
          <select
            value={rank}
            onChange={(e) => setRank(e.target.value)}
            className="glass-panel rounded-full px-3 py-1.5 text-sm outline-none"
          >
            {RANKS.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
          <ExplainModeToggle />
          <button
            onClick={resetDraft}
            className="glass-panel flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm text-muted transition-transform hover:scale-105 hover:text-enemy active:scale-95"
          >
            <RotateCcw size={14} /> Reset
          </button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <GlassCard className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider text-ally">Ally Team</h2>
              {renderBanTray("ally")}
            </div>
            <div className="grid grid-cols-5 gap-3">
              {LANES.map(({ key, label }) => {
                const heroId = allyPicks[key];
                return (
                  <div key={key} className="space-y-1.5">
                    <p className="text-center text-[10px] uppercase tracking-wider text-muted">{label}</p>
                    <LaneSlot
                      side="ally"
                      hero={heroId ? heroById.get(heroId) : undefined}
                      isOpen={openSlot?.side === "ally" && openSlot.lane === key}
                      onToggle={() =>
                        setOpenSlot(openSlot?.side === "ally" && openSlot.lane === key ? null : { side: "ally", lane: key })
                      }
                      onClear={() => clearPick("ally", key)}
                      heatmap={heroId ? heatmapStatus(heroId, "ally") : { counters: false, counteredBy: false }}
                      heroes={heroes ?? []}
                      excludeIds={usedIds}
                      onSelect={(id) => {
                        setPick("ally", key, id);
                        setOpenSlot(null);
                      }}
                      onClose={() => setOpenSlot(null)}
                      pulse={!heroId && key === activeLane && !!recommendation?.best_picks.length}
                    />
                  </div>
                );
              })}
            </div>
          </GlassCard>

          <GlassCard className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-sm font-semibold uppercase tracking-wider text-enemy">Enemy Team</h2>
              {renderBanTray("enemy")}
            </div>
            <div className="grid grid-cols-5 gap-3">
              {LANES.map(({ key, label }) => {
                const heroId = enemyPicks[key];
                return (
                  <div key={key} className="space-y-1.5">
                    <p className="text-center text-[10px] uppercase tracking-wider text-muted">{label}</p>
                    <LaneSlot
                      side="enemy"
                      hero={heroId ? heroById.get(heroId) : undefined}
                      isOpen={openSlot?.side === "enemy" && openSlot.lane === key}
                      onToggle={() =>
                        setOpenSlot(openSlot?.side === "enemy" && openSlot.lane === key ? null : { side: "enemy", lane: key })
                      }
                      onClear={() => clearPick("enemy", key)}
                      heatmap={heroId ? heatmapStatus(heroId, "enemy") : { counters: false, counteredBy: false }}
                      heroes={heroes ?? []}
                      excludeIds={usedIds}
                      onSelect={(id) => {
                        setPick("enemy", key, id);
                        setOpenSlot(null);
                      }}
                      onClose={() => setOpenSlot(null)}
                    />
                  </div>
                );
              })}
            </div>
          </GlassCard>

          {winRequest && (
            <GlassCard>
              <h2 className="mb-4 font-display text-lg font-semibold">Win Probability</h2>
              {winLoading && <p className="text-sm text-muted">Calculating...</p>}
              {winIsError && <ErrorBanner message={getApiErrorMessage(winError)} />}
              {winPrediction && (
                <div className="flex flex-wrap items-center gap-6">
                  <div
                    className="relative flex h-32 w-32 items-center justify-center rounded-full transition-[background] duration-300"
                    style={{
                      background: `conic-gradient(${
                        winPrediction.win_probability >= 0.55
                          ? "var(--positive)"
                          : winPrediction.win_probability <= 0.45
                            ? "var(--enemy)"
                            : "var(--gold)"
                      } ${animatedWinPct}%, var(--glass-fill-strong) 0)`,
                    }}
                  >
                    <div className="absolute inset-2 flex items-center justify-center rounded-full bg-background">
                      <span className="font-display text-2xl font-bold">{Math.round(animatedWinPct)}%</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <ExplanationFactorsList explanation={winPrediction.explanation} />
                  </div>
                </div>
              )}
            </GlassCard>
          )}
        </div>

        <div className="space-y-6">
          <GlassCard>
            <div className="mb-3 flex items-center gap-2">
              <Sparkles size={16} className="text-accent" />
              <h2 className="font-display text-lg font-semibold">Hero Recommendations</h2>
            </div>
            <div className="mb-4 flex flex-wrap gap-1.5">
              {LANES.map(({ key, label }) => (
                <button
                  key={key}
                  onClick={() => setActiveLane(key)}
                  className={cn(
                    "rounded-full px-2.5 py-1 text-xs font-medium transition-colors",
                    activeLane === key ? "bg-accent/20 text-accent" : "glass-panel text-muted hover:text-foreground"
                  )}
                >
                  {label}
                </button>
              ))}
            </div>

            {recIsError && <ErrorBanner message={getApiErrorMessage(recError)} />}
            {recLoading && <p className="text-sm text-muted">Thinking...</p>}

            {recommendation && (
              <div className="space-y-5">
                <div>
                  <p className="mb-1.5 text-xs font-medium uppercase tracking-wider text-muted">Best Picks</p>
                  <ul className="space-y-0.5">
                    {recommendation.best_picks.map((entry) => (
                      <BestPickRow
                        key={entry.hero_id}
                        entry={entry}
                        onPick={(id) => setPick("ally", activeLane, id)}
                      />
                    ))}
                    {!recommendation.best_picks.length && (
                      <p className="text-sm text-muted">No candidates available.</p>
                    )}
                  </ul>
                </div>

                {recommendation.best_picks[0] && (
                  <div className="border-t border-glass-border pt-3">
                    <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted">
                      Why {recommendation.best_picks[0].hero_name}?
                    </p>
                    <ExplanationFactorsList explanation={recommendation.best_picks[0].unified_explanation} />
                  </div>
                )}

                {!!recommendation.counter_picks.length && (
                  <div className="border-t border-glass-border pt-3">
                    <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wider text-muted">
                      <Swords size={12} /> Counter Picks
                    </p>
                    <ul className="space-y-0.5">
                      {recommendation.counter_picks.map((entry: CounterPickEntry) => (
                        <li key={entry.hero_id} className="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 hover:bg-glass-fill">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium">{entry.hero_name}</p>
                            <p className="truncate text-xs text-muted">
                              counters {entry.countered_enemy_heroes.join(", ")}
                            </p>
                          </div>
                          <button
                            onClick={() => setPick("ally", activeLane, entry.hero_id)}
                            className="shrink-0 rounded-full bg-accent/20 px-3 py-1 text-xs font-medium text-accent transition-transform hover:scale-105 hover:bg-accent/30 active:scale-95"
                          >
                            Pick
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {!!recommendation.synergy_picks.length && (
                  <div className="border-t border-glass-border pt-3">
                    <p className="mb-1.5 text-xs font-medium uppercase tracking-wider text-muted">Synergy Picks</p>
                    <ul className="space-y-0.5">
                      {recommendation.synergy_picks.map((entry: SynergyPickEntry) => (
                        <li key={entry.hero_id} className="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 hover:bg-glass-fill">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium">{entry.hero_name}</p>
                            <p className="truncate text-xs text-muted">
                              synergizes with {entry.synergized_ally_heroes.join(", ")}
                            </p>
                          </div>
                          <button
                            onClick={() => setPick("ally", activeLane, entry.hero_id)}
                            className="shrink-0 rounded-full bg-accent/20 px-3 py-1 text-xs font-medium text-accent transition-transform hover:scale-105 hover:bg-accent/30 active:scale-95"
                          >
                            Pick
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
