-- =============================================================
-- Migration: Deduplicate hero_builds + add missing UNIQUE constraint.
-- seed_builds() in seed_all.py was missing an ON CONFLICT guard
-- (every other seed function has one), so re-running the seeder
-- silently duplicated all 24 curated builds into 48 identical rows.
-- =============================================================

-- Keep the lowest id per (hero_id, build_name, patch_version) group,
-- delete the rest.
DELETE FROM hero_builds a
USING hero_builds b
WHERE a.hero_id = b.hero_id
  AND a.build_name = b.build_name
  AND a.patch_version = b.patch_version
  AND a.id > b.id;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'hero_builds_hero_id_build_name_patch_version_key'
    ) THEN
        ALTER TABLE hero_builds
            ADD CONSTRAINT hero_builds_hero_id_build_name_patch_version_key
            UNIQUE (hero_id, build_name, patch_version);
    END IF;
END $$;