import { Compass, Footprints, Shield, Sword, Trees, Wand2, type LucideIcon } from "lucide-react";

export const ITEM_TYPE_ICON: Record<string, LucideIcon> = {
  Attack: Sword,
  Magic: Wand2,
  Defense: Shield,
  Movement: Footprints,
  Jungle: Trees,
  Roam: Compass,
};

export function itemTypeIcon(type: string): LucideIcon {
  return ITEM_TYPE_ICON[type] ?? Sword;
}
