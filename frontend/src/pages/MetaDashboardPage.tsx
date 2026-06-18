import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip as RechartsTooltip, XAxis, YAxis } from "recharts";
import { ArrowDown, ArrowUp, Flame, Star } from "lucide-react";
import { useAllHeroDetails, useHeroes } from "@/api/referenceData";
import { GlassCard } from "@/components/common/GlassCard";
import { Skeleton } from "@/components/common/Skeleton";
import { HeroAvatar } from "@/components/heroes/HeroAvatar";
import { roleColor } from "@/lib/roleColors";
import { cn } from "@/lib/utils";

type SortKey = "win_rate" | "pick_rate" | "ban_rate" | "name";

interface Row {
  id: number;
  name: string;
  role: string;
  is_meta: boolean;
  is_op: boolean;
  win_rate: number | null;
  pick_rate: number | null;
  ban_rate: number | null;
}

export function MetaDashboardPage() {
  const { data: heroes, isLoading: heroesLoading } = useHeroes();
  const heroIds = useMemo(() => heroes?.map((h) => h.id), [heroes]);
  const detailQueries = useAllHeroDetails(heroIds);

  const [roleFilter, setRoleFilter] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("win_rate");
  const [sortDesc, setSortDesc] = useState(true);

  const detailsLoading = detailQueries.some((q) => q.isLoading);

  const rows: Row[] = useMemo(() => {
    if (!heroes) return [];
    return heroes.map((hero, i) => {
      const stats = detailQueries[i]?.data?.stats[0];
      return {
        id: hero.id,
        name: hero.name,
        role: hero.role,
        is_meta: hero.is_meta,
        is_op: hero.is_op,
        win_rate: stats?.win_rate ?? null,
        pick_rate: stats?.pick_rate ?? null,
        ban_rate: stats?.ban_rate ?? null,
      };
    });
  }, [heroes, detailQueries]);

  const roles = useMemo(() => Array.from(new Set(heroes?.map((h) => h.role) ?? [])).sort(), [heroes]);

  const filtered = useMemo(() => {
    const base = roleFilter ? rows.filter((r) => r.role === roleFilter) : rows;
    return [...base].sort((a, b) => {
      if (sortKey === "name") {
        return sortDesc ? b.name.localeCompare(a.name) : a.name.localeCompare(b.name);
      }
      const av = a[sortKey] ?? -Infinity;
      const bv = b[sortKey] ?? -Infinity;
      return sortDesc ? bv - av : av - bv;
    });
  }, [rows, roleFilter, sortKey, sortDesc]);

  const chartData = useMemo(
    () =>
      [...rows]
        .filter((r) => r.win_rate !== null)
        .sort((a, b) => (b.win_rate ?? 0) - (a.win_rate ?? 0))
        .slice(0, 10)
        .map((r) => ({ name: r.name, win_rate: r.win_rate })),
    [rows]
  );

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDesc((d) => !d);
    } else {
      setSortKey(key);
      setSortDesc(true);
    }
  }

  const SortHeader = ({ label, sortKeyValue }: { label: string; sortKeyValue: SortKey }) => (
    <button
      onClick={() => toggleSort(sortKeyValue)}
      className={cn(
        "flex items-center gap-1 text-xs font-medium uppercase tracking-wider",
        sortKey === sortKeyValue ? "text-accent" : "text-muted hover:text-foreground"
      )}
    >
      {label}
      {sortKey === sortKeyValue && (sortDesc ? <ArrowDown size={12} /> : <ArrowUp size={12} />)}
    </button>
  );

  const isLoading = heroesLoading || detailsLoading;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-3xl font-bold">Meta Dashboard</h1>
        <p className="text-muted">Win rate, pick rate, and ban rate across all modeled heroes.</p>
      </div>

      <GlassCard>
        <h2 className="mb-4 font-display text-lg font-semibold">Top 10 by Win Rate</h2>
        {isLoading ? (
          <Skeleton className="h-72" />
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" horizontal={false} />
                <XAxis
                  type="number"
                  stroke="var(--muted)"
                  fontSize={12}
                  domain={[(min: number) => Math.floor(min - 1), (max: number) => Math.ceil(max + 1)]}
                />
                <YAxis type="category" dataKey="name" stroke="var(--muted)" fontSize={12} width={110} />
                <RechartsTooltip
                  contentStyle={{
                    background: "var(--background)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="win_rate" fill="var(--accent)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </GlassCard>

      <div className="flex flex-wrap items-center gap-3">
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

      <GlassCard className="overflow-x-auto">
        {isLoading ? (
          <Skeleton className="h-96" />
        ) : (
          <table className="w-full min-w-[600px] text-sm">
            <thead>
              <tr className="border-b border-glass-border text-left">
                <th className="pb-3 pr-4">
                  <SortHeader label="Hero" sortKeyValue="name" />
                </th>
                <th className="pb-3 pr-4">
                  <SortHeader label="Win Rate" sortKeyValue="win_rate" />
                </th>
                <th className="pb-3 pr-4">
                  <SortHeader label="Pick Rate" sortKeyValue="pick_rate" />
                </th>
                <th className="pb-3 pr-4">
                  <SortHeader label="Ban Rate" sortKeyValue="ban_rate" />
                </th>
                <th className="pb-3">Flags</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row) => {
                const colors = roleColor(row.role);
                return (
                  <tr key={row.id} className="border-b border-glass-border/50 last:border-0">
                    <td className="py-2.5 pr-4">
                      <Link to={`/heroes/${row.id}`} className="flex items-center gap-2.5 hover:text-accent">
                        <HeroAvatar name={row.name} role={row.role} size={28} />
                        <span className="font-medium">{row.name}</span>
                        <span className={cn("rounded-full px-2 py-0.5 text-xs", colors.bg, colors.text)}>
                          {row.role}
                        </span>
                      </Link>
                    </td>
                    <td className="py-2.5 pr-4 font-display font-semibold text-foreground">
                      {row.win_rate !== null ? `${row.win_rate}%` : "—"}
                    </td>
                    <td className="py-2.5 pr-4 text-muted">
                      {row.pick_rate !== null ? `${row.pick_rate}%` : "—"}
                    </td>
                    <td className="py-2.5 pr-4 text-muted">
                      {row.ban_rate !== null ? `${row.ban_rate}%` : "—"}
                    </td>
                    <td className="py-2.5">
                      <div className="flex gap-1.5">
                        {row.is_meta && <Flame size={14} className="text-enemy" />}
                        {row.is_op && <Star size={14} className="text-gold" />}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </GlassCard>
    </div>
  );
}
