"""
Content-based hero similarity (cosine, over a one-hot + normalized-stat
feature vector) — used for (a) "similar hero" substitution suggestions
and (b) MMR diversity penalties when re-ranking the Best Picks list.
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

ROLES = ["Tank", "Fighter", "Assassin", "Mage", "Marksman", "Support"]
SPECIALTIES = ["Crowd Control", "Damage", "Initiator", "Pusher", "Reap",
               "Poke", "Guard", "Heal", "Support"]
DAMAGE_TYPES = ["Physical", "Magic", "Hybrid"]


def build_similarity_matrix(heroes_df: pd.DataFrame, hero_stats_df: pd.DataFrame):
    """Returns (NxN similarity matrix, list of hero_ids in matrix row/col order)."""
    latest_patch = hero_stats_df["patch_version"].max()
    stats = hero_stats_df[hero_stats_df["patch_version"] == latest_patch].set_index("hero_id")

    hero_ids = list(heroes_df.index)
    rows = []
    for hid in hero_ids:
        h = heroes_df.loc[hid]
        role_vec = [1.0 if h["role"] == r else 0.0 for r in ROLES]
        spec_vec = [1.0 if h["specialty"] == s else 0.0 for s in SPECIALTIES]
        dmg_vec = [1.0 if h["damage_type"] == d else 0.0 for d in DAMAGE_TYPES]

        s = stats.loc[hid] if hid in stats.index else None
        win_rate = float(s["win_rate"]) if s is not None else 50.0
        pick_rate = float(s["pick_rate"]) if s is not None else 5.0
        ban_rate = float(s["ban_rate"]) if s is not None else 5.0

        rows.append({
            **{f"role_{r}": v for r, v in zip(ROLES, role_vec)},
            **{f"spec_{s_}": v for s_, v in zip(SPECIALTIES, spec_vec)},
            **{f"dmg_{d}": v for d, v in zip(DAMAGE_TYPES, dmg_vec)},
            "difficulty": float(h["difficulty"]),
            "win_rate": win_rate,
            "pick_rate": pick_rate,
            "ban_rate": ban_rate,
            "is_meta": float(h["is_meta"]),
            "is_op": float(h["is_op"]),
        })

    feature_df = pd.DataFrame(rows, index=hero_ids)

    # Categorical identity (role/specialty/damage type) should dominate
    # "similar hero" similarity — continuous meta stats are a fine-grained
    # tiebreaker only, not an equal partner. Without this down-weighting,
    # a Marksman with matching win/pick/ban rates can outrank a same-role
    # Assassin, which defeats the point of a substitution suggestion.
    continuous_cols = ["difficulty", "win_rate", "pick_rate", "ban_rate"]
    feature_df[continuous_cols] = MinMaxScaler().fit_transform(feature_df[continuous_cols])
    feature_df[continuous_cols] *= 0.3
    feature_df[["is_meta", "is_op"]] *= 0.3

    sim_matrix = cosine_similarity(feature_df.values)
    return sim_matrix, hero_ids


def similar_heroes(hero_id: int, sim_matrix: np.ndarray, hero_ids: list[int],
                    exclude_ids: set[int], limit: int = 5) -> list[tuple[int, float]]:
    idx = hero_ids.index(hero_id)
    scores = [(hid, sim_matrix[idx][j]) for j, hid in enumerate(hero_ids)
              if hid != hero_id and hid not in exclude_ids]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:limit]


def mmr_rerank(candidates: list[dict], sim_matrix: np.ndarray, hero_ids: list[int],
               lam: float = 0.7, k: int = 5) -> list[dict]:
    """
    candidates: list of dicts with at least {'hero_id': int, 'composite_score': float},
    pre-sorted by relevance descending. Returns a re-ordered top-k balancing
    relevance against redundancy with already-selected picks.
    """
    pool = candidates.copy()
    selected: list[dict] = []

    if not pool:
        return selected

    max_score = max(c["composite_score"] for c in pool) or 1.0

    while pool and len(selected) < k:
        best, best_mmr = None, -float("inf")
        for c in pool:
            relevance = c["composite_score"] / max_score
            if selected:
                idx_c = hero_ids.index(c["hero_id"])
                max_sim = max(
                    sim_matrix[idx_c][hero_ids.index(s["hero_id"])] for s in selected
                )
            else:
                max_sim = 0.0
            mmr = lam * relevance - (1 - lam) * max_sim
            if mmr > best_mmr:
                best, best_mmr = c, mmr
        selected.append(best)
        pool.remove(best)

    return selected
