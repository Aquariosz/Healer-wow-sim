# Mapping of Warcraft Logs AbilityGameIDs to English Spell Names for Holy Priests

HOLY_PRIEST_SPELLS = {
    14914: "Holy Fire",
    2061: "Flash Heal",
    596: "Prayer of Healing",
    2050: "Holy Word: Serenity",
    34861: "Holy Word: Sanctify",
    33076: "Prayer of Mending",
    121536: "Angelic Feather",
    139: "Renew",
    73325: "Leap of Faith",
    64843: "Divine Hymn",
    265202: "Holy Word: Salvation",
    10060: "Power Infusion",
    32546: "Binding Heal",
    204883: "Circle of Healing",
    88625: "Holy Word: Chastise",
    120517: "Halo",
    110744: "Divine Star",
    47540: "Penance",               # Disc overlap, but sometimes present
    200183: "Apotheosis",
    132157: "Holy Nova",
    1262763: "Power Word: Life",
    17: "Power Word: Shield",
    1236616: "Symbol of Hope"
    # This list can be dynamically expanded via WoWhead API in the future
}

def get_spell_name(ability_id: int) -> str:
    """Returns the English spell name for a given abilityGameID, or 'Unknown Spell (ID)' if not found."""
    return HOLY_PRIEST_SPELLS.get(ability_id, f"Unknown Spell ({ability_id})")
