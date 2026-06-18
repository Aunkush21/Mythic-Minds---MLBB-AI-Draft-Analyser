import { useMemo } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Swords } from "lucide-react";
import { useCounters, useHero, useHeroes, useSimilarHeroes } from "@/api/referenceData";
import { GlassCard } from "@/components/common/GlassCard";
import { Skeleton } from "@/components/common/Skeleton";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { StatBar } from "@/components/common/StatBar";
import { HeroAvatar } from "@/components/heroes/HeroAvatar";
import { roleColor } from "@/lib/roleColors";
import { cn } from "@/lib/utils";
import { getApiErrorMessage } from "@/api/client";

export function HeroDetailPage() {
  const { heroId } = useParams();
  const id = heroId ? Number(heroId) : undefined;

  const { data: hero, isLoading, isError, error } = useHero(id);
  const { data: similar } = useSimilarHeroes(id, 5);
  const { data: counters } = useCounters();
  const { data: allHeroes } = useHeroes();

  const heroName = useMemo(() => {
    const map = new Map(allHeroes?.map((h) => [h.id, h.name]));
    return (heroId: number) => map.get(heroId) ?? `Hero #${heroId}`;
  }, [allHeroes]);

  const latestStats = hero?.stats[0];

  const counteredBy = useMemo(
    () => counters?.filter((c) => c.hero_id === id) ?? [],
    [counters, id]
  );
  const countersTargets = useMemo(
    () => counters?.filter((c) => c.countered_by_id === id) ?? [],
    [counters, id]
  );

  if (isLoading) return <Skeleton className="h-96" />;
  if (isError) return <ErrorBanner message={getApiErrorMessage(error)} />;
  if (!hero) return null;

  const colors = roleColor(hero.role);

  return (
    <div className="space-y-8">
      <Link to="/heroes" className="inline-flex items-center gap-1 text-sm text-muted hover:text-foreground">
        <ArrowLeft size={14} /> Back to Compendium
      </Link>

      <div className="flex flex-wrap items-center gap-6">
        <HeroAvatar name={hero.name} role={hero.role} size={96} />
        <div>
          <h1 className="font-display text-4xl font-bold">{hero.name}</h1>
          <div className="mt-2 flex flex-wrap gap-2 text-sm">
            <span className={cn("rounded-full px-3 py-1", colors.bg, colors.text)}>{hero.role}</span>
            {hero.secondary_role && (
              <span className="glass-panel rounded-full px-3 py-1 text-muted">{hero.secondary_role}</span>
            )}
            <span className="glass-panel rounded-full px-3 py-1 text-muted">{hero.specialty}</span>
            <span className="glass-panel rounded-full px-3 py-1 text-muted">{hero.damage_type}</span>
            <span className="glass-panel rounded-full px-3 py-1 text-muted">{hero.preferred_lane}</span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <GlassCard>
          <h2 className="mb-4 font-display text-lg font-semibold">
            Patch {latestStats?.patch_version ?? "—"} Stats
          </h2>
          {latestStats ? (
            <div className="space-y-4">
              <StatBar label="Win Rate" value={latestStats.win_rate ?? 0} suffix="%" colorClass="bg-positive" />
              <StatBar label="Pick Rate" value={latestStats.pick_rate ?? 0} suffix="%" colorClass="bg-accent" />
              <StatBar label="Ban Rate" value={latestStats.ban_rate ?? 0} suffix="%" colorClass="bg-enemy" />
            </div>
          ) : (
            <p className="text-sm text-muted">No stats recorded.</p>
          )}
          <Link
            to="/builds"
            state={{ heroId: hero.id }}
            className="mt-5 inline-flex items-center gap-2 text-sm text-accent hover:underline"
          >
            View build recommendations →
          </Link>
        </GlassCard>

        <GlassCard>
          <h2 className="mb-4 font-display text-lg font-semibold">Similar Heroes</h2>
          <div className="space-y-3">
            {similar?.map((s) => (
              <Link
                key={s.hero_id}
                to={`/heroes/${s.hero_id}`}
                className="flex items-center justify-between rounded-lg px-2 py-1.5 hover:bg-glass-fill"
              >
                <span className="text-sm">{s.hero_name}</span>
                <span className="font-display text-sm text-accent">{(s.similarity * 100).toFixed(0)}%</span>
              </Link>
            ))}
            {!similar?.length && <p className="text-sm text-muted">No similar heroes found.</p>}
          </div>
        </GlassCard>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <GlassCard>
          <h2 className="mb-4 flex items-center gap-2 font-display text-lg font-semibold text-enemy">
            <Swords size={16} /> Countered By
          </h2>
          <ul className="space-y-2">
            {counteredBy.map((c) => (
              <li key={c.countered_by_id} className="text-sm">
                <Link to={`/heroes/${c.countered_by_id}`} className="font-medium hover:text-accent">
                  {heroName(c.countered_by_id)}
                </Link>{" "}
                <span className="text-muted">— {c.reason ?? `score ${c.counter_score}`}</span>
              </li>
            ))}
            {!counteredBy.length && <p className="text-sm text-muted">No recorded hard counters.</p>}
          </ul>
        </GlassCard>

        <GlassCard>
          <h2 className="mb-4 flex items-center gap-2 font-display text-lg font-semibold text-positive">
            <Swords size={16} /> Counters
          </h2>
          <ul className="space-y-2">
            {countersTargets.map((c) => (
              <li key={c.hero_id} className="text-sm">
                <Link to={`/heroes/${c.hero_id}`} className="font-medium hover:text-accent">
                  {heroName(c.hero_id)}
                </Link>{" "}
                <span className="text-muted">— {c.reason ?? `score ${c.counter_score}`}</span>
              </li>
            ))}
            {!countersTargets.length && <p className="text-sm text-muted">No recorded favorable matchups.</p>}
          </ul>
        </GlassCard>
      </div>
    </div>
  );
}
