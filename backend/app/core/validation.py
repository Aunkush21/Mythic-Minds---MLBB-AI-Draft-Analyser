"""Shared request-validation helpers used across the ML service layers."""
from app.core.exceptions import HeroNotFoundError, InvalidDraftError


def assert_heroes_exist(hero_ids: list[int], valid_ids: set[int]) -> None:
    unknown = [h for h in hero_ids if h not in valid_ids]
    if unknown:
        raise HeroNotFoundError(f"Unknown hero id(s): {unknown}")


def assert_no_duplicate_picks(*groups: list[int]) -> None:
    """
    MLBB disallows mirror picks — the same hero cannot appear twice across
    ally picks, enemy picks, and bans combined.
    """
    seen: dict[int, int] = {}
    for hero_id in [h for group in groups for h in group]:
        seen[hero_id] = seen.get(hero_id, 0) + 1
    duplicates = [h for h, count in seen.items() if count > 1]
    if duplicates:
        raise InvalidDraftError(
            f"Hero id(s) {duplicates} appear more than once across ally picks, "
            f"enemy picks, and bans — MLBB does not allow mirror picks."
        )
