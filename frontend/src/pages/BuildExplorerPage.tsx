import { useMemo, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { Hammer, Plus, Wand2, X } from "lucide-react";
import { useBuildRecommendation } from "@/api/buildRecommendation";
import { useHeroes, useItems } from "@/api/referenceData";
import { GlassCard } from "@/components/common/GlassCard";
import { Skeleton } from "@/components/common/Skeleton";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { StatBar } from "@/components/common/StatBar";
import { ExplainModeToggle } from "@/components/common/ExplainModeToggle";
import { ExplanationFactorsList } from "@/components/common/ExplanationFactorsList";
import { HeroAvatar } from "@/components/heroes/HeroAvatar";
import { HeroListDropdown } from "@/components/heroes/HeroListDropdown";
import { itemTypeIcon } from "@/lib/itemIcons";
import { getApiErrorMessage } from "@/api/client";
import type { BuildRequest } from "@/types/api";

const MAX_ENEMY_PICKS = 5;

export function BuildExplorerPage() {
  const location = useLocation();
  const preselectedHeroId = (location.state as { heroId?: number } | null)?.heroId;

  const { data: heroes } = useHeroes();
  const { data: items } = useItems();

  const [heroId, setHeroId] = useState<number | null>(preselectedHeroId ?? null);
  const [enemyPicks, setEnemyPicks] = useState<number[]>([]);
  const [heroPickerOpen, setHeroPickerOpen] = useState(false);
  const [enemyPickerOpen, setEnemyPickerOpen] = useState(false);
  const heroPickerButtonRef = useRef<HTMLButtonElement>(null);
  const enemyPickerButtonRef = useRef<HTMLButtonElement>(null);

  const heroById = useMemo(() => new Map(heroes?.map((h) => [h.id, h])), [heroes]);
  const itemTypeByName = useMemo(() => new Map(items?.map((i) => [i.name, i.type])), [items]);

  const request: BuildRequest | null = heroId
    ? { hero_id: heroId, enemy_picks: enemyPicks }
    : null;

  const { data: build, isLoading, isError, error } = useBuildRecommendation(request);

  const selectedHero = heroId ? heroById.get(heroId) : undefined;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold">Build Explorer</h1>
          <p className="text-muted">Item, emblem, and battle-spell builds adapted to the enemy threat profile.</p>
        </div>
        <ExplainModeToggle />
      </div>

      <GlassCard className="space-y-5">
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <p className="mb-2 text-sm font-medium text-muted">Hero</p>
            <div className="relative inline-block">
              <button
                ref={heroPickerButtonRef}
                onClick={() => setHeroPickerOpen((v) => !v)}
                className="glass-panel flex items-center gap-3 rounded-xl px-3 py-2 hover:bg-glass-fill"
              >
                {selectedHero ? (
                  <>
                    <HeroAvatar name={selectedHero.name} role={selectedHero.role} size={32} />
                    <span className="text-sm font-medium">{selectedHero.name}</span>
                  </>
                ) : (
                  <span className="text-sm text-muted">Select a hero...</span>
                )}
              </button>
              {heroPickerOpen && (
                <HeroListDropdown
                  heroes={heroes ?? []}
                  excludeIds={heroId ? [heroId] : []}
                  onSelect={(id) => {
                    setHeroId(id);
                    setHeroPickerOpen(false);
                  }}
                  onClose={() => setHeroPickerOpen(false)}
                  anchorRef={heroPickerButtonRef}
                />
              )}
            </div>
          </div>

          <div>
            <p className="mb-2 text-sm font-medium text-muted">
              Enemy Picks <span className="text-xs">({enemyPicks.length}/{MAX_ENEMY_PICKS})</span>
            </p>
            <div className="flex flex-wrap items-center gap-2">
              {enemyPicks.map((id) => {
                const hero = heroById.get(id);
                if (!hero) return null;
                return (
                  <span
                    key={id}
                    className="glass-panel flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs"
                  >
                    <HeroAvatar name={hero.name} role={hero.role} size={18} />
                    {hero.name}
                    <button
                      onClick={() => setEnemyPicks((prev) => prev.filter((p) => p !== id))}
                      className="ml-0.5 text-muted hover:text-enemy"
                    >
                      <X size={12} />
                    </button>
                  </span>
                );
              })}
              {enemyPicks.length < MAX_ENEMY_PICKS && (
                <div className="relative inline-block">
                  <button
                    ref={enemyPickerButtonRef}
                    onClick={() => setEnemyPickerOpen((v) => !v)}
                    className="glass-panel flex items-center gap-1 rounded-full px-2.5 py-1 text-xs text-muted hover:text-foreground"
                  >
                    <Plus size={12} /> Add
                  </button>
                  {enemyPickerOpen && (
                    <HeroListDropdown
                      heroes={heroes ?? []}
                      excludeIds={[...enemyPicks, ...(heroId ? [heroId] : [])]}
                      onSelect={(id) => {
                        setEnemyPicks((prev) => [...prev, id]);
                        setEnemyPickerOpen(false);
                      }}
                      onClose={() => setEnemyPickerOpen(false)}
                      anchorRef={enemyPickerButtonRef}
                    />
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </GlassCard>

      {!heroId && (
        <GlassCard className="flex items-center gap-3 text-muted">
          <Wand2 size={20} className="text-accent" />
          <p className="text-sm">Select a hero to generate a build recommendation.</p>
        </GlassCard>
      )}

      {isLoading && (
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      )}

      {isError && <ErrorBanner message={getApiErrorMessage(error)} />}

      {build && (
        <div className="grid gap-6 md:grid-cols-2">
          <GlassCard>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="flex items-center gap-2 font-display text-lg font-semibold">
                <Hammer size={16} className="text-accent" /> {build.hero_name}'s Build
              </h2>
              <span className="glass-panel rounded-full px-3 py-1 text-xs font-medium text-gold">
                {build.tier}
              </span>
            </div>

            <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted">Items</p>
            <div className="mb-4 grid grid-cols-2 gap-2">
              {build.items.map((itemName) => {
                const Icon = itemTypeIcon(itemTypeByName.get(itemName) ?? "Attack");
                return (
                  <div
                    key={itemName}
                    className="glass-panel flex items-center gap-2 rounded-lg px-3 py-2 text-sm"
                  >
                    <Icon size={16} className="shrink-0 text-accent" />
                    {itemName}
                  </div>
                );
              })}
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="glass-panel rounded-lg px-3 py-2">
                <p className="text-xs text-muted">Emblem</p>
                <p className="font-medium">{build.emblem}</p>
              </div>
              <div className="glass-panel rounded-lg px-3 py-2">
                <p className="text-xs text-muted">Battle Spell</p>
                <p className="font-medium">{build.battle_spell}</p>
              </div>
            </div>
          </GlassCard>

          <div className="space-y-6">
            <GlassCard>
              <h2 className="mb-4 font-display text-lg font-semibold">Enemy Threat Profile</h2>
              <div className="space-y-3">
                <StatBar label="Physical Damage" value={build.threat_profile.physical_count} max={5} colorClass="bg-enemy" />
                <StatBar label="Magic Damage" value={build.threat_profile.magic_count} max={5} colorClass="bg-purple-400" />
                <StatBar label="Tankiness" value={build.threat_profile.tank_count} max={5} colorClass="bg-ally" />
                <StatBar label="Burst Threat" value={build.threat_profile.burst_threat_score} max={5} colorClass="bg-gold" />
                <StatBar label="CC Density" value={build.threat_profile.cc_density} max={5} colorClass="bg-accent" />
                <StatBar label="Sustain Threat" value={build.threat_profile.sustain_threat} max={5} colorClass="bg-positive" />
              </div>
            </GlassCard>

            <GlassCard>
              <h2 className="mb-3 font-display text-lg font-semibold">Why this build?</h2>
              <ExplanationFactorsList explanation={build.unified_explanation} />
            </GlassCard>
          </div>
        </div>
      )}
    </div>
  );
}
