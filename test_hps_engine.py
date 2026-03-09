from execution.hps_engine import HPSEngine
import json

stats = {"intellect": 14500, "haste": 4200, "crit": 3800, "mastery": 2100, "versatility": 1500}
talents = {"heroTalent": "archon", "apotheosis": True}

print("--- MYTHIC+ ---")
engine_mplus = HPSEngine(stats, talents, "Dungeon", 180)
print(json.dumps(engine_mplus.simulate(), indent=2))

print("\n--- RAID ---")
engine_raid = HPSEngine(stats, talents, "Raid", 400) # 6.6 min fight
print(json.dumps(engine_raid.simulate(), indent=2))
