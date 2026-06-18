"""
Slot-level refinement applied on top of whichever tier produced the
backbone build. Swaps up to 2 of the more "situational" slots (the
later slots, by MLBB build-order convention) when a specific enemy
threat is strong and not already covered by the existing build.
"""
import pandas as pd

MAX_SWAPS = 2


def _best_tagged_item(items_df: pd.DataFrame, tag_col: str, exclude: set[int], sort_col: str) -> int | None:
    pool = items_df[items_df[tag_col] & (~items_df.index.isin(exclude))]
    if pool.empty:
        return None
    return pool.sort_values(sort_col, ascending=False).index[0]


def apply_threat_substitution(item_ids: list[int], threat: dict, items_df: pd.DataFrame) -> tuple[list[int], list[dict]]:
    items = list(item_ids)
    existing = set(items)
    needs = []

    if threat["magic_count"] >= 3 and not any(items_df.loc[i, "is_anti_magic"] for i in items):
        needs.append(("anti_magic", "is_anti_magic", "magic_def",
                       f"enemy has {threat['magic_count']} magic damage heroes"))
    if threat["physical_count"] >= 3 and not any(items_df.loc[i, "is_anti_physical"] for i in items):
        needs.append(("anti_physical", "is_anti_physical", "phys_def",
                       f"enemy has {threat['physical_count']} physical damage heroes"))
    if threat["sustain_threat"] >= 2 and not any(items_df.loc[i, "is_anti_heal"] for i in items):
        needs.append(("anti_heal", "is_anti_heal", "cost",
                       f"enemy has {threat['sustain_threat']} sustain-oriented heroes"))
    if threat["burst_threat_score"] >= 3 and not any(
        items_df.loc[i, "is_revive"] or items_df.loc[i, "is_shield"] for i in items
    ):
        needs.append(("anti_burst", "is_revive", "cost",
                       f"enemy has {threat['burst_threat_score']} high-burst meta picks"))

    needs.sort(key=lambda n: {
        "anti_magic": threat["magic_count"], "anti_physical": threat["physical_count"],
        "anti_heal": threat["sustain_threat"], "anti_burst": threat["burst_threat_score"],
    }[n[0]], reverse=True)

    swap_log = []
    for label, tag_col, sort_col, reason in needs[:MAX_SWAPS]:
        replacement = _best_tagged_item(items_df, tag_col, existing, sort_col)
        if replacement is None:
            continue
        # Replace the latest situational slot (last item not already flagged as a swap target).
        slot_idx = len(items) - 1 - swap_log.__len__()
        removed = items[slot_idx]
        items[slot_idx] = replacement
        existing.discard(removed)
        existing.add(replacement)
        swap_log.append({
            "slot": slot_idx + 1,
            "removed_item": items_df.loc[removed, "name"],
            "added_item": items_df.loc[replacement, "name"],
            "reason": reason,
        })

    return items, swap_log
