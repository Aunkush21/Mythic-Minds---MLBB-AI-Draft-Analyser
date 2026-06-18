-- =============================================================
-- Migration: Fix movement_spd for Movement-type items.
-- Original seed data (database/seed/items.py) never set a base
-- movement_spd for any boots item (all defaulted to 0), and Rapid
-- Boots' intended +50 value was off-by-one shifted into phys_pen
-- instead. Caught by the Build Recommendation engine's Tier 3
-- role-default boots selection, which picks the highest movement_spd
-- Movement item and was getting a meaningless 0-way tie.
-- =============================================================

UPDATE items SET movement_spd = 40 WHERE name IN
    ('Warrior Boots', 'Tough Boots', 'Magic Shoes', 'Arcane Boots', 'Swift Boots', 'Demon Shoes');

UPDATE items SET movement_spd = 60, phys_pen = 0.0 WHERE name = 'Rapid Boots';
