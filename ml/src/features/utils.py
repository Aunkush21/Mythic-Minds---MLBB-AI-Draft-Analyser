"""Shared helpers for patch-aware feature lookups."""


def patch_key(version: str) -> tuple[int, ...]:
    """'1.9.0' -> (1, 9, 0). Enables correct numeric ordering of patch strings."""
    return tuple(int(p) for p in version.split("."))


def nearest_patch_leq(target: str, available: list[str]) -> str:
    """
    Return the latest available patch <= target. Falls back to the latest
    available patch overall if none qualify (e.g. target predates all data).
    """
    target_key = patch_key(target)
    candidates = sorted(available, key=patch_key)
    leq = [p for p in candidates if patch_key(p) <= target_key]
    return leq[-1] if leq else candidates[-1]
