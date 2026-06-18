"""
Lightweight threat-tagging for items, derived from existing stat columns
and passive_desc text. This is a documented stopgap — the architecture
doc flags that items should eventually carry structured boolean tags
(is_anti_heal, counters_burst, etc.) instead of requiring text parsing
at runtime. Until that schema change happens, this is the bridge.
"""
import pandas as pd


def tag_items(items_df: pd.DataFrame) -> pd.DataFrame:
    df = items_df.copy()

    is_defense = df["type"] == "Defense"
    df["is_anti_magic"] = is_defense & (df["magic_def"] > df["phys_def"])
    df["is_anti_physical"] = is_defense & (df["phys_def"] > df["magic_def"])

    desc = df["passive_desc"].fillna("").str.lower()
    df["is_anti_heal"] = desc.str.contains("regen") & desc.str.contains("reduc")

    df["is_revive"] = desc.str.contains("revive")
    df["is_shield"] = desc.str.contains("shield")

    return df