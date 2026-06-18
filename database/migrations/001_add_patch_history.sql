-- =============================================================
-- Migration: Add patch_history table + FK constraints
-- Run this against a database that was seeded BEFORE this table existed.
-- Safe to run once; uses IF NOT EXISTS / ON CONFLICT guards.
-- =============================================================

CREATE TABLE IF NOT EXISTS patch_history (
    id              SERIAL PRIMARY KEY,
    patch_version   VARCHAR(10)     NOT NULL UNIQUE,
    release_date    DATE            NOT NULL,
    codename        VARCHAR(80),
    summary         TEXT,
    heroes_added    TEXT[],
    heroes_reworked TEXT[],
    is_current      BOOLEAN         DEFAULT FALSE,
    created_at      TIMESTAMPTZ     DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patch_current ON patch_history(is_current);

INSERT INTO patch_history (id, patch_version, release_date, codename, summary, heroes_added, heroes_reworked, is_current)
VALUES
    (1, '1.7.0', '2023-08-15', 'Mecha Era',
     'Introduced jungle pathing rework and item economy rebalance.',
     ARRAY['Joy'], ARRAY[]::TEXT[], FALSE),
    (2, '1.7.2', '2023-09-12', 'Storm Surge',
     'Tank emblem rework; nerfs to early-game roam burst combos.',
     ARRAY[]::TEXT[], ARRAY['Khufra','Atlas'], FALSE),
    (3, '1.8.0', '2023-10-20', 'Land of Dawn Anniversary',
     'Major mage itemization changes; Holy Crystal passive scaling adjusted.',
     ARRAY[]::TEXT[], ARRAY['Kagura'], FALSE),
    (4, '1.8.4', '2023-12-05', 'Winter Truncheon Update',
     'Defense item overhaul; Immortality and Athena''s Shield cost reduced.',
     ARRAY[]::TEXT[], ARRAY['Fredrinn'], FALSE),
    (5, '1.9.0', '2024-01-18', 'Reap & Sow',
     'Assassin jungle clear speed buffed across the board; new roam duo meta emerges around Khufra + Mathilda lockdown combos.',
     ARRAY[]::TEXT[], ARRAY['Paquito','Khufra'], TRUE)
ON CONFLICT (patch_version) DO NOTHING;

-- Add FK constraints now that patch_history is populated.
-- Guarded with DO blocks so re-running the migration is safe.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'heroes_release_patch_fkey') THEN
        ALTER TABLE heroes ADD CONSTRAINT heroes_release_patch_fkey
            FOREIGN KEY (release_patch) REFERENCES patch_history(patch_version);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hero_stats_patch_version_fkey') THEN
        ALTER TABLE hero_stats ADD CONSTRAINT hero_stats_patch_version_fkey
            FOREIGN KEY (patch_version) REFERENCES patch_history(patch_version);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'items_patch_version_fkey') THEN
        ALTER TABLE items ADD CONSTRAINT items_patch_version_fkey
            FOREIGN KEY (patch_version) REFERENCES patch_history(patch_version);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'battle_spells_patch_version_fkey') THEN
        ALTER TABLE battle_spells ADD CONSTRAINT battle_spells_patch_version_fkey
            FOREIGN KEY (patch_version) REFERENCES patch_history(patch_version);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hero_counters_patch_version_fkey') THEN
        ALTER TABLE hero_counters ADD CONSTRAINT hero_counters_patch_version_fkey
            FOREIGN KEY (patch_version) REFERENCES patch_history(patch_version);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hero_synergies_patch_version_fkey') THEN
        ALTER TABLE hero_synergies ADD CONSTRAINT hero_synergies_patch_version_fkey
            FOREIGN KEY (patch_version) REFERENCES patch_history(patch_version);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'hero_builds_patch_version_fkey') THEN
        ALTER TABLE hero_builds ADD CONSTRAINT hero_builds_patch_version_fkey
            FOREIGN KEY (patch_version) REFERENCES patch_history(patch_version);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'match_drafts_patch_version_fkey') THEN
        ALTER TABLE match_drafts ADD CONSTRAINT match_drafts_patch_version_fkey
            FOREIGN KEY (patch_version) REFERENCES patch_history(patch_version);
    END IF;
END $$;
