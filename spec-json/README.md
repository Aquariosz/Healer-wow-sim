# Spec JSON Reference Data

Normalized per-spec ability reference files for RaidAudit tracking systems.

## Schema

```json
{
  "class": "string",       // Matches CLASS_MAP in wow-classes.ts (e.g. "DeathKnight")
  "spec": "string",        // Matches CLASS_SPECS names (e.g. "Blood", "Frost")
  "role": "string",        // TANK | HEALER | MELEE_DPS | RANGED_DPS
  "expansion": "Midnight", // Current expansion target
  "version": 1,            // Bump when data is updated
  "abilities": {
    "personalDefensives": [],    // Active personal DR, shields, heals
    "immunities": [],            // Full damage immunities
    "raidCooldowns": [],         // Raid-wide CDs (healing, DR, movement)
    "externals": [],             // CDs castable on other players
    "interrupts": [],            // Active interrupt abilities
    "dispels": [],               // Purge, soothe, cleanse, mass dispel
    "movementCooldowns": [],     // Dashes, blinks, speed boosts
    "offensiveCooldowns": [],    // DPS CDs tracked for timeline
    "utility": [],               // Buffs, battle rez, misc
    "crowdControl": []           // Stuns, roots, incaps, fears, knockbacks
  },
  "removedAbilities": [],   // Spells removed/made passive in Midnight
  "replacementMap": {},      // Old spell ID -> new spell ID mapping
  "notes": []                // Uncertainty, caveats, special behavior
}
```

## Ability Entry Shape

```json
{
  "id": 48707,                          // WoW spell ID (numeric)
  "name": "Anti-Magic Shell",           // Exact spell name
  "cooldown": 60,                       // Base cooldown in seconds (0 = no CD)
  "notes": "Magic absorb for 5-7s"     // Talent variations, hero talent effects
}
```

## File Naming Convention

- **Class-level:** `{class}.json` — shared abilities across all specs of a class
- **Spec-level:** `{class}-{spec}.json` — spec-specific additions only

Examples: `evoker.json` (class), `evoker-devastation.json` (spec), `death-knight-blood.json` (spec)

## Class + Spec Inheritance

Every class has a class-level JSON file containing abilities shared across all its specs.
Spec files use `"inherits": "{class}.json"` and contain **only spec-specific abilities**.

To get the full ability list for a spec, merge the class file + spec file:
- `warrior.json` (base) + `warrior-fury.json` (additions) = full Fury Warrior

Spec files may also include `specOverrides` to modify base class ability notes:
```json
"specOverrides": {
  "dispels": {
    "365585": { "notes": "Poison + Magic. Preservation adds Magic" }
  }
}
```

**Class-level files (13):** `death-knight.json`, `demon-hunter.json`, `druid.json`, `evoker.json`, `hunter.json`, `mage.json`, `monk.json`, `paladin.json`, `priest.json`, `rogue.json`, `shaman.json`, `warlock.json`, `warrior.json`

## Intended Usage

These files power:
- **Defensive detection** — `personalDefensives` + `immunities`
- **Raid cooldown tracking** — `raidCooldowns` + `externals`
- **Interrupt tracking** — `interrupts`
- **Dispel tracking** — `dispels`
- **Movement CD tracking** — `movementCooldowns`
- **Player recommendations** — all categories
- **Timeline categorization** — `offensiveCooldowns` for DPS timeline overlay

## Key Design Decisions

1. **Passive abilities are excluded** from active tracking categories (Cheat Death, Purgatory, etc.) but noted in `notes[]`
2. **Hero talent variants** are noted in ability `notes` field, not as separate entries
3. **Choice nodes** (e.g., HTT vs Ascendance) are listed as separate entries — app logic should handle mutual exclusion
4. **Talented abilities** are included with "Talented" noted — most raid builds take these
5. **Dual-purpose abilities** may appear in multiple categories (e.g., Netherwalk in both defensives and immunities)
6. **Cooldowns are base values** — talent/hero talent CDR is noted but not applied

## Coverage

All 13 classes, all 39 specs (13 × 3 = 39, except DH at 2 and Evoker at 3).

| Class | Specs | Files |
|-------|-------|-------|
| Death Knight | Blood, Frost, Unholy | 1 class + 3 spec |
| Demon Hunter | Havoc, Vengeance | 1 class + 2 spec |
| Druid | Balance, Feral, Guardian, Restoration | 1 class + 4 spec |
| Evoker | Augmentation, Devastation, Preservation | 1 class + 3 spec |
| Hunter | Beast Mastery, Marksmanship, Survival | 1 class + 3 spec |
| Mage | Arcane, Fire, Frost | 1 class + 3 spec |
| Monk | Brewmaster, Mistweaver, Windwalker | 1 class + 3 spec |
| Paladin | Holy, Protection, Retribution | 1 class + 3 spec |
| Priest | Discipline, Holy, Shadow | 1 class + 3 spec |
| Rogue | Assassination, Outlaw, Subtlety | 1 class + 3 spec |
| Shaman | Elemental, Enhancement, Restoration | 1 class + 3 spec |
| Warlock | Affliction, Demonology, Destruction | 1 class + 3 spec |
| Warrior | Arms, Fury, Protection | 1 class + 3 spec |
| **Total** | | **13 class + 39 spec = 52 files** |

## Sources

- Primary: `Copy of Class Info - Wow - Copy of Class Info - Midnight Edit.csv` (community spreadsheet by @Baratus)
- Secondary: `Copy of Logs and Queries Sheet - Queries.csv` (WCL query spell ID groups)
- Validation: Wowhead Midnight class/spec guides (cross-referenced for removed/new abilities)
- Existing: `packages/analysis/src/metrics/definitions.ts` (current DEFENSIVE_ABILITY_IDS)

## Not Wired Into App Code

This is reference data only. Integration into RaidAudit tracking requires a separate implementation pass.
