"""
Battle spell override rules, triggered by the enemy threat profile.

Emblems are deliberately NOT threat-adjusted here: in actual MLBB,
emblem choice is a slow, role-level commitment (the schema also has no
selectable-talent granularity, just a fixed type + bonus block), while
battle spells are explicitly designed as the reactive, situational
choice. Overriding emblems per-matchup would be both unrealistic and
unsupported by the current data model — so the cascade leaves the
backbone's emblem untouched and only adjusts the spell.
"""
import pandas as pd


def apply_spell_override(spell_id: int, threat: dict, hero_role: str, spells_df: pd.DataFrame) -> tuple[int, str | None]:
    by_name = {row["name"]: idx for idx, row in spells_df.iterrows()}

    if threat["cc_density"] >= 2 and hero_role in ("Marksman", "Mage") and "Purify" in by_name:
        if spell_id != by_name["Purify"]:
            return by_name["Purify"], f"enemy has {threat['cc_density']} crowd-control heroes"

    if threat["cc_density"] >= 2 and hero_role in ("Tank", "Fighter") and "Vengeance" in by_name:
        if spell_id != by_name["Vengeance"]:
            return by_name["Vengeance"], f"enemy has {threat['cc_density']} crowd-control heroes"

    if threat["burst_threat_score"] >= 3 and hero_role in ("Support", "Tank") and "Aegis" in by_name:
        if spell_id != by_name["Aegis"]:
            return by_name["Aegis"], f"enemy has {threat['burst_threat_score']} high-burst meta picks"

    return spell_id, None