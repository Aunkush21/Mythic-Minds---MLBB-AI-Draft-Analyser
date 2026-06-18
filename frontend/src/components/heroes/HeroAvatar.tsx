import { useState } from "react";
import { cn } from "@/lib/utils";
import { AVATAR_SCALE_OVERRIDES, heroSlug, roleColor } from "@/lib/roleColors";

export function HeroAvatar({
  name,
  role,
  size = 48,
  className,
}: {
  name: string;
  role: string;
  size?: number;
  className?: string;
}) {
  const [errored, setErrored] = useState(false);
  const colors = roleColor(role);
  const initials = name
    .split(/\s+/)
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  if (errored) {
    return (
      <div
        className={cn(
          "flex items-center justify-center rounded-full border font-display font-semibold",
          colors.bg,
          colors.border,
          colors.text,
          className
        )}
        style={{ width: size, height: size, fontSize: size * 0.36 }}
      >
        {initials}
      </div>
    );
  }

  const scale = AVATAR_SCALE_OVERRIDES[name] ?? 1;

  return (
    <img
      src={`/assets/heroes/${heroSlug(name)}.webp`}
      alt={name}
      width={size}
      height={size}
      onError={() => setErrored(true)}
      className={cn("rounded-full border object-cover", colors.border, className)}
      style={{ width: size, height: size, transform: scale !== 1 ? `scale(${scale})` : undefined }}
    />
  );
}
