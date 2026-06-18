import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Flame, Star } from "lucide-react";
import { useHeroes } from "@/api/referenceData";
import { GlassCard } from "@/components/common/GlassCard";
import { Skeleton } from "@/components/common/Skeleton";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { HeroAvatar } from "@/components/heroes/HeroAvatar";
import { roleColor } from "@/lib/roleColors";
import { cn } from "@/lib/utils";
import { getApiErrorMessage } from "@/api/client";

export function HeroCompendiumPage() {
  const { data: heroes, isLoading, isError, error } = useHeroes();
  const [roleFilter, setRoleFilter] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const roles = useMemo(
    () => Array.from(new Set(heroes?.map((h) => h.role) ?? [])).sort(),
    [heroes]
  );

  const filtered = useMemo(() => {
    if (!heroes) return [];
    return heroes.filter((hero) => {
      if (roleFilter && hero.role !== roleFilter) return false;
      if (search && !hero.name.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [heroes, roleFilter, search]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl font-bold">Hero Compendium</h1>
        <p className="text-muted">Browse all modeled heroes, stats, and similar-hero mappings.</p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search heroes..."
          className="glass-panel rounded-full px-4 py-2 text-sm outline-none placeholder:text-muted"
        />
        <button
          onClick={() => setRoleFilter(null)}
          className={cn(
            "rounded-full px-3 py-1.5 text-sm font-medium transition-colors",
            roleFilter === null ? "bg-accent/20 text-accent" : "glass-panel text-muted hover:text-foreground"
          )}
        >
          All
        </button>
        {roles.map((role) => (
          <button
            key={role}
            onClick={() => setRoleFilter(role)}
            className={cn(
              "rounded-full px-3 py-1.5 text-sm font-medium transition-colors",
              roleFilter === role
                ? cn(roleColor(role).bg, roleColor(role).text)
                : "glass-panel text-muted hover:text-foreground"
            )}
          >
            {role}
          </button>
        ))}
      </div>

      {isError && <ErrorBanner message={getApiErrorMessage(error)} />}

      {isLoading && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} className="h-36" />
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {filtered.map((hero) => {
          const colors = roleColor(hero.role);
          return (
            <Link key={hero.id} to={`/heroes/${hero.id}`} className="transition-transform active:scale-95">
              <GlassCard interactive className="flex flex-col items-center gap-2 text-center">
                <HeroAvatar name={hero.name} role={hero.role} size={56} />
                <p className="font-display font-semibold">{hero.name}</p>
                <span className={cn("rounded-full px-2 py-0.5 text-xs", colors.bg, colors.text)}>
                  {hero.role}
                </span>
                <div className="flex gap-1.5 text-muted">
                  {hero.is_meta && <Flame size={13} className="text-enemy" />}
                  {hero.is_op && <Star size={13} className="text-gold" />}
                </div>
              </GlassCard>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
