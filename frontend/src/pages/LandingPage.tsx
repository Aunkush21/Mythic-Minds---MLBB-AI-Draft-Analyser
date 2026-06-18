import { Link } from "react-router-dom";
import { AlertTriangle, ArrowRight, Brain, Hammer, Sparkles } from "lucide-react";
import { GlassCard } from "@/components/common/GlassCard";
import { HeroAvatar } from "@/components/heroes/HeroAvatar";
import { useHeroes } from "@/api/referenceData";

const SECTIONS = [
  {
    icon: Brain,
    title: "Hero Intelligence",
    description:
      "Tier-cascaded hero recommendations with counter-pick and team-synergy analysis built directly into the same engine — no separate modules needed.",
  },
  {
    icon: Hammer,
    title: "Build Generation",
    description:
      "Curated and similarity-transferred item, emblem, and battle-spell builds, adapted to the enemy team's threat profile.",
  },
  {
    icon: Sparkles,
    title: "Explainability",
    description:
      "Every prediction ships with a unified explanation: SHAP-derived factors, confidence level, and the reasoning basis behind it.",
  },
];

export function LandingPage() {
  const { data: heroes } = useHeroes();

  return (
    <div className="space-y-20">
      <section className="relative grid items-center gap-10 overflow-hidden rounded-3xl py-12 lg:grid-cols-2">
        <div
          className="pointer-events-none absolute -right-20 -top-20 h-72 w-72 rounded-full bg-accent/20 blur-3xl"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute -bottom-24 right-32 h-56 w-56 rounded-full bg-gold/10 blur-3xl"
          aria-hidden
        />

        <div className="relative z-10 space-y-6">
          <p className="font-display text-sm font-semibold uppercase tracking-[0.3em] text-accent">
            MLBB AI Draft Intelligence
          </p>
          <h1 className="font-display text-5xl font-bold leading-tight">
            Draft smarter.
            <br />
            <span className="text-accent">See the why.</span>
          </h1>
          <p className="max-w-md text-muted">
            Win-probability prediction, hero recommendation, and build optimization for Mobile
            Legends: Bang Bang — every output explained, not just predicted.
          </p>
          <Link
            to="/draft"
            className="inline-flex items-center gap-2 rounded-full bg-accent px-6 py-3 font-display font-semibold text-background shadow-[0_0_24px_-6px_var(--color-accent)] transition-transform hover:scale-105 active:scale-95"
          >
            Enter the Draft Room <ArrowRight size={18} />
          </Link>
        </div>

        <div className="relative z-10 flex justify-center lg:justify-end">
          <img
            src="/assets/mascot/yss-full-body.png"
            alt="Yss"
            className="pointer-events-none max-h-96 w-auto select-none drop-shadow-2xl"
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
        </div>
      </section>

      <GlassCard className="flex items-start gap-3 border-gold/30">
        <AlertTriangle size={20} className="mt-0.5 shrink-0 text-gold" />
        <p className="text-sm text-muted">
          <span className="font-semibold text-gold">Data disclosure: </span>
          This platform is trained on synthetically generated matches, not real MLBB telemetry. Win
          labels are a direct function of hero meta/OP flags, so held-out model metrics (AUC ~0.97)
          reflect recovery of that synthetic rule rather than real-world draft prediction accuracy.
          Every prediction's confidence basis says this explicitly — nothing here overstates its own
          certainty.
        </p>
      </GlassCard>

      <section className="grid gap-6 md:grid-cols-3">
        {SECTIONS.map((section) => (
          <GlassCard key={section.title} interactive className="relative">
            <section.icon size={24} className="text-accent" />
            <h3 className="mt-4 font-display text-lg font-semibold">{section.title}</h3>
            <p className="mt-2 text-sm text-muted">{section.description}</p>
          </GlassCard>
        ))}
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-xl font-semibold">Meet the Heroes</h2>
          <Link to="/heroes" className="text-sm text-accent hover:underline">
            View compendium →
          </Link>
        </div>
        <div className="flex gap-4 overflow-x-auto pb-2">
          {heroes?.slice(0, 14).map((hero) => (
            <Link
              key={hero.id}
              to={`/heroes/${hero.id}`}
              className="flex shrink-0 flex-col items-center gap-2 transition-transform hover:scale-110 active:scale-95"
            >
              <HeroAvatar name={hero.name} role={hero.role} size={64} />
              <span className="text-xs text-muted">{hero.name}</span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
