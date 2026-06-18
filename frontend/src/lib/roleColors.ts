export const ROLE_COLORS: Record<string, { text: string; bg: string; border: string }> = {
  Tank: { text: "text-ally", bg: "bg-ally/15", border: "border-ally/40" },
  Fighter: { text: "text-orange-400", bg: "bg-orange-400/15", border: "border-orange-400/40" },
  Assassin: { text: "text-enemy", bg: "bg-enemy/15", border: "border-enemy/40" },
  Mage: { text: "text-purple-400", bg: "bg-purple-400/15", border: "border-purple-400/40" },
  Marksman: { text: "text-gold", bg: "bg-gold/15", border: "border-gold/40" },
  Support: { text: "text-positive", bg: "bg-positive/15", border: "border-positive/40" },
};

export function roleColor(role: string) {
  return ROLE_COLORS[role] ?? { text: "text-accent", bg: "bg-accent/15", border: "border-accent/40" };
}

export function heroSlug(name: string) {
  return name
    .toLowerCase()
    .replace(/[.'%]/g, "")
    .replace(/\s+/g, "-");
}

// Some source portraits are cropped tighter than the rest of the roster (e.g. Yve's
// is a close-up of her visor instead of a head-and-shoulders shot). Scale those down
// inside their frame so they read at a similar size to everyone else's avatar.
export const AVATAR_SCALE_OVERRIDES: Record<string, number> = {
  Yve: 0.78,
};
