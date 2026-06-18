"""Computes the enemy team's threat profile from their drafted heroes."""
import pandas as pd


def compute_enemy_threat_profile(enemy_ids: list[int], heroes_df: pd.DataFrame) -> dict:
    if not enemy_ids:
        return {
            "physical_count": 0, "magic_count": 0, "tank_count": 0,
            "burst_threat_score": 0, "cc_density": 0, "sustain_threat": 0,
        }

    enemy = heroes_df.loc[enemy_ids]

    physical_count = int((enemy["damage_type"] == "Physical").sum())
    magic_count = int((enemy["damage_type"] == "Magic").sum())
    tank_count = int((enemy["role"] == "Tank").sum())

    burst_roles = enemy["role"].isin(["Assassin", "Mage"])
    burst_threat_score = int((burst_roles & (enemy["is_op"] | enemy["is_meta"])).sum())

    cc_density = int((enemy["specialty"] == "Crowd Control").sum())
    sustain_threat = int((enemy["specialty"] == "Heal").sum())

    return {
        "physical_count": physical_count,
        "magic_count": magic_count,
        "tank_count": tank_count,
        "burst_threat_score": burst_threat_score,
        "cc_density": cc_density,
        "sustain_threat": sustain_threat,
    }