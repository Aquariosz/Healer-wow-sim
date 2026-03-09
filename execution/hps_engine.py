import json
import math
import argparse

class HPSEngine:
    def __init__(self, stats, talents, fight_style, fight_length_seconds, healing_req="Balanced", dungeon_name=None):
        self.stats = stats
        self.talents = talents
        self.fight_style = fight_style
        self.fight_length = fight_length_seconds
        
        # Override requirement if a specific dungeon is known
        self.dungeon_name = dungeon_name
        self.healing_req = healing_req
        self.dungeon_insight = None
        
        self._apply_dungeon_profile()
        
        # Base conversion rates for Midnight (Level 90)
        # Note: At level 90, rating conversions are much steeper than level 80
        self.rating_conversions = {
            'haste': 115, # Example scaled conversions for Lvl 90
            'crit': 120,
            'mastery': 120, 
            'versatility': 130
        }
        
        # Base stats (% before ratings are applied)
        self.base_stats = {
            'haste': 0.0,
            'crit': 0.05,
            'mastery': 0.10, # Base Mastery % for Holy
            'versatility': 0.0
        }

    def _apply_dungeon_profile(self):
        if self.fight_style != "Dungeon" or not self.dungeon_name or self.dungeon_name == "Generic":
            return
            
        # Midnight Season 1 Expected Damage Profiles based on M+ Dataset
        profiles = {
            "Pit of Saron": "Sustain",          # Heavy continuous rot damage and environmental ticking auras
            "Maisara Caverns": "Balanced",      # Good mix of spot healing and sudden bursts
            "Skyreach": "Burst",                # Sudden huge targeted drops and phase transitions
            "Nexus-Point Xenas": "Spot",        # High tank damage and random single target dots
            "Magisters' Terrace": "Spot",       # Tons of dangerous trash casts requiring spot patching
        }
        
        if self.dungeon_name in profiles:
            self.healing_req = profiles[self.dungeon_name]
            self.dungeon_insight = f"Auto-applied '{self.healing_req}' profile based on dataset patterns for {self.dungeon_name}."

    def _calculate_stat_percentages(self):
        # Calculate actual percentages from rating
        # Note: In a real sim, diminishing returns (DR) are applied here.
        # For our MVP engine, we use direct linear scaling before DR caps.
        pct = {
            'haste': self.base_stats['haste'] + (self.stats.get('haste', 0) / self.rating_conversions['haste']) / 100,
            'crit': self.base_stats['crit'] + (self.stats.get('crit', 0) / self.rating_conversions['crit']) / 100,
            'mastery': self.base_stats['mastery'] + (self.stats.get('mastery', 0) / self.rating_conversions['mastery']) / 100,
            'versatility': self.base_stats['versatility'] + (self.stats.get('versatility', 0) / self.rating_conversions['versatility']) / 100
        }
        return pct

    def simulate(self):
        pct = self._calculate_stat_percentages()
        intellect = self.stats.get('intellect', 0)
        
        # 1. Base Spell Power Calculation
        # Intellect provides 1 Spell Power per point
        spell_power = intellect
        
        # 2. Base HPS based on standard rotation mapping
        # We assume a fixed "baseline HPS multiplier" that scales with SP
        # This multiplier varies heavily based on Environment.
        if self.fight_style == "Dungeon":
            # Baseline is spikier, more spot healing, lower overall raw throughput compared to raid
            base_multiplier = 14.5 
        elif self.fight_style == "Raid":
            # Constant AoE damage, higher raw throughput possible
            base_multiplier = 22.0
        else:
             base_multiplier = 15.0

        raw_hps = spell_power * base_multiplier
        
        # 3. Apply Class Specific Modifiers
        # To make the engine robust, each class has its own specific scaling, talents, and profile reactions.
        insights = []
        if self.dungeon_insight:
            insights.append({"type": "info", "message": self.dungeon_insight})
            
        efficiency = 85.0 # Base efficiency assumptions
        
        simulated_hps = raw_hps
        
        # We currently hardcode to Holy Priest as it's our first MVP class
        try:
            from execution.classes.priest.holy import HolyPriest
            holy_calc = HolyPriest(self.stats, self.talents, self.fight_style, self.fight_length, self.healing_req, pct)
            simulated_hps, efficiency, class_insights = holy_calc.calculate_modifiers(simulated_hps, efficiency)
            insights.extend(class_insights)
        except ImportError:
            insights.append({"type": "warning", "message": "Could not load Holy Priest specific calculations."})


        # 6. Fight Length adjustments (Mana considerations)
        # If the fight is very long (e.g. > 6 minutes), Haste becomes less valuable and Intellect/Crit more valuable due to Mana constraints.
        if self.fight_length > 360: # 6 minutes
            efficiency -= 10.0 # OOM risk
            simulated_hps *= 0.90 # Forced downtime
            insights.append({"type": "warning", "message": f"Fight length ({self.fight_length // 60}m) causing severe Mana constraints. HPS scaled down to reflect conservative casting."})

        # Cap efficiency
        efficiency = min(100.0, max(0.0, efficiency))

        return {
            "metrics": {
                "realHpsRaw": simulated_hps,
                "realHps": f"{simulated_hps / 1000:.1f}k",
                "potentialHps": f"{(simulated_hps * 1.15) / 1000:.1f}k", # Legacy mock, overwritten by server.py now
                "efficiencyScore": round(efficiency, 1)
            },
            "insights": insights,
            "sim_details": {
                "fight_style": self.fight_style,
                "length_seconds": self.fight_length,
                "stat_percentages": {k: f"{v*100:.1f}%" for k,v in pct.items()}
            }
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HPS Simulation Engine")
    parser.add_argument('--stats', type=str, required=True, help='JSON string of stats')
    parser.add_argument('--talents', type=str, required=True, help='JSON string of talents')
    parser.add_argument('--style', type=str, default="Dungeon", choices=["Dungeon", "Raid"], help='Fight style')
    parser.add_argument('--length', type=int, default=180, help='Fight length in seconds')
    
    args = parser.parse_args()
    
    try:
        stats_dict = json.loads(args.stats)
        talents_dict = json.loads(args.talents)
        
        engine = HPSEngine(stats_dict, talents_dict, args.style, args.length)
        result = engine.simulate()
        print(json.dumps(result, indent=4))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
