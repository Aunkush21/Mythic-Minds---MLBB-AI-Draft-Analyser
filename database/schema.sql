-- =============================================================
-- MLBB AI Draft Intelligence Platform
-- PostgreSQL Database Schema
-- =============================================================

-- ENUM TYPES
CREATE TYPE hero_role AS ENUM ('Tank', 'Fighter', 'Assassin', 'Mage', 'Marksman', 'Support');
CREATE TYPE hero_specialty AS ENUM ('Crowd Control', 'Damage', 'Initiator', 'Pusher', 'Reap', 'Poke', 'Guard', 'Heal', 'Support');
CREATE TYPE damage_type AS ENUM ('Physical', 'Magic', 'Hybrid');
CREATE TYPE item_type AS ENUM ('Attack', 'Magic', 'Defense', 'Movement', 'Jungle', 'Roam');
CREATE TYPE emblem_type AS ENUM ('Assassin', 'Fighter', 'Mage', 'Marksman', 'Support', 'Tank', 'Common');
CREATE TYPE lane_type AS ENUM ('EXP', 'Gold', 'Mid', 'Jungle', 'Roam');
CREATE TYPE match_rank AS ENUM ('Warrior', 'Elite', 'Master', 'Grandmaster', 'Epic', 'Legend', 'Mythic', 'Mythical Glory');
CREATE TYPE match_side AS ENUM ('Blue', 'Red');

-- =============================================================
-- TABLE 0: patch_history
-- Purpose: Source of truth for game patches. Every other table's
--          patch_version FK's into this — prevents orphaned/invalid
--          patch strings and lets the API answer "what changed".
-- =============================================================
CREATE TABLE patch_history (
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

-- =============================================================
-- TABLE 1: heroes
-- Purpose: Master hero entity — all 9 modules reference this
-- =============================================================
CREATE TABLE heroes (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(60)     NOT NULL UNIQUE,
    role            hero_role       NOT NULL,
    secondary_role  hero_role,
    specialty       hero_specialty  NOT NULL,
    damage_type     damage_type     NOT NULL,
    preferred_lane  lane_type       NOT NULL,
    difficulty      SMALLINT        NOT NULL CHECK (difficulty BETWEEN 1 AND 10),
    release_patch   VARCHAR(10)     REFERENCES patch_history(patch_version),
    is_meta         BOOLEAN         DEFAULT FALSE,
    is_op           BOOLEAN         DEFAULT FALSE,
    portrait_url    TEXT,
    created_at      TIMESTAMPTZ     DEFAULT NOW()
);

-- =============================================================
-- TABLE 2: hero_stats
-- Purpose: Base stats per hero — used in win prediction features
-- =============================================================
CREATE TABLE hero_stats (
    id              SERIAL PRIMARY KEY,
    hero_id         INT             NOT NULL REFERENCES heroes(id) ON DELETE CASCADE,
    patch_version   VARCHAR(10)     NOT NULL REFERENCES patch_history(patch_version),
    -- Base Stats
    base_hp         INT             NOT NULL,
    base_mana       INT,
    base_armor      NUMERIC(5,1)    NOT NULL,
    base_magic_res  NUMERIC(5,1)    NOT NULL,
    base_atk_spd    NUMERIC(4,2)    NOT NULL,
    base_phys_atk   INT             NOT NULL,
    base_magic_pwr  INT             DEFAULT 0,
    movement_spd    INT             NOT NULL,
    -- Scaling per level
    hp_growth       NUMERIC(6,1),
    armor_growth    NUMERIC(4,2),
    atk_growth      NUMERIC(4,1),
    -- Meta metrics (updated per patch)
    win_rate        NUMERIC(5,2)    CHECK (win_rate BETWEEN 0 AND 100),
    pick_rate       NUMERIC(5,2)    CHECK (pick_rate BETWEEN 0 AND 100),
    ban_rate        NUMERIC(5,2)    CHECK (ban_rate BETWEEN 0 AND 100),
    -- Timestamps
    updated_at      TIMESTAMPTZ     DEFAULT NOW(),
    UNIQUE(hero_id, patch_version)
);

-- =============================================================
-- TABLE 3: items
-- Purpose: All MLBB items — used in build recommendation
-- =============================================================
CREATE TABLE items (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(80)     NOT NULL UNIQUE,
    type            item_type       NOT NULL,
    tier            SMALLINT        NOT NULL CHECK (tier BETWEEN 1 AND 3),
    cost            INT             NOT NULL,
    -- Stat bonuses
    phys_atk        INT             DEFAULT 0,
    magic_pwr       INT             DEFAULT 0,
    phys_def        INT             DEFAULT 0,
    magic_def       INT             DEFAULT 0,
    max_hp          INT             DEFAULT 0,
    hp_regen        INT             DEFAULT 0,
    mana            INT             DEFAULT 0,
    mana_regen      INT             DEFAULT 0,
    crit_chance     NUMERIC(4,1)    DEFAULT 0,
    atk_speed       NUMERIC(4,2)    DEFAULT 0,
    lifesteal       NUMERIC(4,1)    DEFAULT 0,
    movement_spd    INT             DEFAULT 0,
    phys_pen        NUMERIC(4,1)    DEFAULT 0,
    magic_pen       NUMERIC(4,1)    DEFAULT 0,
    cooldown_red    NUMERIC(4,1)    DEFAULT 0,
    -- Passive description
    passive_name    VARCHAR(60),
    passive_desc    TEXT,
    is_active       BOOLEAN         DEFAULT FALSE,
    active_desc     TEXT,
    patch_version   VARCHAR(10)     NOT NULL DEFAULT '1.9.0' REFERENCES patch_history(patch_version),
    created_at      TIMESTAMPTZ     DEFAULT NOW()
);

-- =============================================================
-- TABLE 4: emblems
-- Purpose: Emblem sets and their stat bonuses
-- =============================================================
CREATE TABLE emblems (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(60)     NOT NULL UNIQUE,
    type            emblem_type     NOT NULL,
    -- Core stats boosted
    phys_atk_bonus  NUMERIC(5,1)    DEFAULT 0,
    magic_pwr_bonus NUMERIC(5,1)    DEFAULT 0,
    hp_bonus        INT             DEFAULT 0,
    armor_bonus     NUMERIC(4,1)    DEFAULT 0,
    magic_res_bonus NUMERIC(4,1)    DEFAULT 0,
    cdr_bonus       NUMERIC(4,1)    DEFAULT 0,
    movement_bonus  INT             DEFAULT 0,
    -- Talent descriptions (3 talent slots)
    talent_1        VARCHAR(60),
    talent_2        VARCHAR(60),
    talent_3        VARCHAR(60),
    -- Recommended for roles
    recommended_roles  hero_role[],
    created_at      TIMESTAMPTZ     DEFAULT NOW()
);

-- =============================================================
-- TABLE 5: battle_spells
-- Purpose: All battle spells — used in build recommendation
-- =============================================================
CREATE TABLE battle_spells (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(40)     NOT NULL UNIQUE,
    description     TEXT            NOT NULL,
    cooldown        INT             NOT NULL,
    unlock_level    INT             NOT NULL DEFAULT 1,
    -- Which roles typically use this
    recommended_roles  hero_role[],
    recommended_lanes  lane_type[],
    -- Usage context
    use_case        TEXT,
    patch_version   VARCHAR(10)     DEFAULT '1.9.0' REFERENCES patch_history(patch_version),
    created_at      TIMESTAMPTZ     DEFAULT NOW()
);

-- =============================================================
-- TABLE 6: hero_counters
-- Purpose: Counter-pick relationships — Counter Analysis module
-- =============================================================
CREATE TABLE hero_counters (
    id              SERIAL PRIMARY KEY,
    hero_id         INT             NOT NULL REFERENCES heroes(id) ON DELETE CASCADE,
    countered_by_id INT             NOT NULL REFERENCES heroes(id) ON DELETE CASCADE,
    -- Strength of counter (1-10)
    counter_score   NUMERIC(3,1)    NOT NULL CHECK (counter_score BETWEEN 1 AND 10),
    -- Why this counter works
    reason          TEXT,
    patch_version   VARCHAR(10)     NOT NULL DEFAULT '1.9.0' REFERENCES patch_history(patch_version),
    created_at      TIMESTAMPTZ     DEFAULT NOW(),
    UNIQUE(hero_id, countered_by_id, patch_version),
    CHECK(hero_id != countered_by_id)
);

-- =============================================================
-- TABLE 7: hero_synergies
-- Purpose: Hero synergy pairs — Synergy Analysis module
-- =============================================================
CREATE TABLE hero_synergies (
    id              SERIAL PRIMARY KEY,
    hero_a_id       INT             NOT NULL REFERENCES heroes(id) ON DELETE CASCADE,
    hero_b_id       INT             NOT NULL REFERENCES heroes(id) ON DELETE CASCADE,
    -- Synergy score (1-10)
    synergy_score   NUMERIC(3,1)    NOT NULL CHECK (synergy_score BETWEEN 1 AND 10),
    combo_name      VARCHAR(60),
    reason          TEXT,
    patch_version   VARCHAR(10)     NOT NULL DEFAULT '1.9.0' REFERENCES patch_history(patch_version),
    created_at      TIMESTAMPTZ     DEFAULT NOW(),
    UNIQUE(hero_a_id, hero_b_id, patch_version),
    CHECK(hero_a_id < hero_b_id)
);

-- =============================================================
-- TABLE 8: hero_builds
-- Purpose: Recommended item builds per hero per meta context
-- =============================================================
CREATE TABLE hero_builds (
    id              SERIAL PRIMARY KEY,
    hero_id         INT             NOT NULL REFERENCES heroes(id) ON DELETE CASCADE,
    build_name      VARCHAR(80)     NOT NULL,
    -- Ordered item slots (item IDs)
    item_1          INT             REFERENCES items(id),
    item_2          INT             REFERENCES items(id),
    item_3          INT             REFERENCES items(id),
    item_4          INT             REFERENCES items(id),
    item_5          INT             REFERENCES items(id),
    item_6          INT             REFERENCES items(id),
    -- Emblem & spell
    emblem_id       INT             REFERENCES emblems(id),
    spell_id        INT             REFERENCES battle_spells(id),
    -- Context
    is_core         BOOLEAN         DEFAULT TRUE,
    situation       VARCHAR(40),    -- 'Standard', 'Anti-Tank', 'Anti-Burst', etc.
    patch_version   VARCHAR(10)     NOT NULL DEFAULT '1.9.0' REFERENCES patch_history(patch_version),
    win_rate        NUMERIC(5,2),
    games_played    INT             DEFAULT 0,
    created_at      TIMESTAMPTZ     DEFAULT NOW(),
    UNIQUE(hero_id, build_name, patch_version)
);

-- =============================================================
-- TABLE 9: match_drafts
-- Purpose: Full draft data per match — Win Prediction & Hero Rec
-- =============================================================
CREATE TABLE match_drafts (
    id              SERIAL PRIMARY KEY,
    match_id        VARCHAR(40)     NOT NULL UNIQUE,
    patch_version   VARCHAR(10)     NOT NULL REFERENCES patch_history(patch_version),
    rank            match_rank      NOT NULL,
    -- Blue team picks (by lane)
    blue_exp        INT             REFERENCES heroes(id),
    blue_gold       INT             REFERENCES heroes(id),
    blue_mid        INT             REFERENCES heroes(id),
    blue_jungle     INT             REFERENCES heroes(id),
    blue_roam       INT             REFERENCES heroes(id),
    -- Red team picks (by lane)
    red_exp         INT             REFERENCES heroes(id),
    red_gold        INT             REFERENCES heroes(id),
    red_mid         INT             REFERENCES heroes(id),
    red_jungle      INT             REFERENCES heroes(id),
    red_roam        INT             REFERENCES heroes(id),
    -- Bans (up to 6 per side)
    blue_bans       INT[],
    red_bans        INT[],
    created_at      TIMESTAMPTZ     DEFAULT NOW()
);

-- =============================================================
-- TABLE 10: match_results
-- Purpose: Outcome of each draft — target variable for ML models
-- =============================================================
CREATE TABLE match_results (
    id              SERIAL PRIMARY KEY,
    match_id        VARCHAR(40)     NOT NULL REFERENCES match_drafts(match_id) ON DELETE CASCADE,
    winner          match_side      NOT NULL,
    -- Duration
    match_duration  INT             NOT NULL,  -- seconds
    -- Blue team performance
    blue_kills      SMALLINT,
    blue_deaths     SMALLINT,
    blue_assists    SMALLINT,
    blue_turrets    SMALLINT,
    blue_lords      SMALLINT,
    blue_turtles    SMALLINT,
    blue_gold_total INT,
    -- Red team performance
    red_kills       SMALLINT,
    red_deaths      SMALLINT,
    red_assists     SMALLINT,
    red_turrets     SMALLINT,
    red_lords       SMALLINT,
    red_turtles     SMALLINT,
    red_gold_total  INT,
    -- ML feature: first objectives
    first_blood_side    match_side,
    first_turret_side   match_side,
    first_lord_side     match_side,
    first_turtle_side   match_side,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================
-- INDEXES — for query performance
-- =============================================================
CREATE INDEX idx_patch_current       ON patch_history(is_current);
CREATE INDEX idx_hero_stats_hero     ON hero_stats(hero_id);
CREATE INDEX idx_hero_stats_patch    ON hero_stats(patch_version);
CREATE INDEX idx_counters_hero       ON hero_counters(hero_id);
CREATE INDEX idx_counters_by         ON hero_counters(countered_by_id);
CREATE INDEX idx_synergies_a         ON hero_synergies(hero_a_id);
CREATE INDEX idx_synergies_b         ON hero_synergies(hero_b_id);
CREATE INDEX idx_builds_hero         ON hero_builds(hero_id);
CREATE INDEX idx_drafts_patch        ON match_drafts(patch_version);
CREATE INDEX idx_drafts_rank         ON match_drafts(rank);
CREATE INDEX idx_results_match       ON match_results(match_id);
CREATE INDEX idx_results_winner      ON match_results(winner);

-- =============================================================
-- VIEWS — pre-built for API queries
-- =============================================================

-- Hero full profile view
CREATE VIEW v_hero_profile AS
SELECT
    h.id, h.name, h.role, h.secondary_role, h.specialty,
    h.damage_type, h.preferred_lane, h.difficulty, h.is_meta, h.is_op,
    hs.patch_version, hs.win_rate, hs.pick_rate, hs.ban_rate,
    hs.base_hp, hs.base_phys_atk, hs.movement_spd
FROM heroes h
LEFT JOIN hero_stats hs ON h.id = hs.hero_id
WHERE hs.patch_version = '1.9.0' OR hs.patch_version IS NULL;

-- Top counter picks view
CREATE VIEW v_top_counters AS
SELECT
    h.name AS hero_name,
    c.name AS countered_by,
    hc.counter_score,
    hc.reason,
    hc.patch_version
FROM hero_counters hc
JOIN heroes h  ON hc.hero_id         = h.id
JOIN heroes c  ON hc.countered_by_id = c.id
ORDER BY hc.counter_score DESC;

-- Top synergy pairs view
CREATE VIEW v_top_synergies AS
SELECT
    ha.name AS hero_a,
    hb.name AS hero_b,
    hs.synergy_score,
    hs.combo_name,
    hs.reason,
    hs.patch_version
FROM hero_synergies hs
JOIN heroes ha ON hs.hero_a_id = ha.id
JOIN heroes hb ON hs.hero_b_id = hb.id
ORDER BY hs.synergy_score DESC;

-- Match win rate by hero view
CREATE VIEW v_hero_win_rate AS
SELECT
    h.name,
    h.role,
    COUNT(*) AS total_matches,
    SUM(CASE
        WHEN (md.blue_exp = h.id OR md.blue_gold = h.id OR md.blue_mid = h.id
              OR md.blue_jungle = h.id OR md.blue_roam = h.id) AND mr.winner = 'Blue' THEN 1
        WHEN (md.red_exp  = h.id OR md.red_gold  = h.id OR md.red_mid  = h.id
              OR md.red_jungle  = h.id OR md.red_roam  = h.id) AND mr.winner = 'Red'  THEN 1
        ELSE 0
    END) AS wins,
    ROUND(
        100.0 * SUM(CASE
            WHEN (md.blue_exp = h.id OR md.blue_gold = h.id OR md.blue_mid = h.id
                  OR md.blue_jungle = h.id OR md.blue_roam = h.id) AND mr.winner = 'Blue' THEN 1
            WHEN (md.red_exp  = h.id OR md.red_gold  = h.id OR md.red_mid  = h.id
                  OR md.red_jungle  = h.id OR md.red_roam  = h.id) AND mr.winner = 'Red'  THEN 1
            ELSE 0
        END) / NULLIF(COUNT(*), 0), 2
    ) AS calculated_win_rate
FROM heroes h
JOIN match_drafts md ON (
    md.blue_exp = h.id OR md.blue_gold = h.id OR md.blue_mid = h.id OR
    md.blue_jungle = h.id OR md.blue_roam = h.id OR
    md.red_exp  = h.id OR md.red_gold  = h.id OR md.red_mid  = h.id OR
    md.red_jungle  = h.id OR md.red_roam  = h.id
)
JOIN match_results mr ON md.match_id = mr.match_id
GROUP BY h.id, h.name, h.role;
