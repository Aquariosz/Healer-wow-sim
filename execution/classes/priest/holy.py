class HolyPriest:
    def __init__(self, stats, talents, fight_style, fight_length, healing_req, stat_pcts):
        self.stats = stats
        self.talents = talents
        self.fight_style = fight_style
        self.fight_length = fight_length
        self.healing_req = healing_req
        self.pct = stat_pcts

    def calculate_modifiers(self, base_hps, efficiency):
        simulated_hps = base_hps
        insights = []
        
        # Stat Base Multiplier (crit/vers/mastery/haste)
        stat_multiplier = (1 + self.pct['crit']) * (1 + self.pct['versatility']) * (1 + self.pct['mastery']) * (1 + self.pct['haste'])
        simulated_hps *= stat_multiplier

        # Hero Talents
        hero = self.talents.get('heroTalent', 'none').lower()
        if hero == 'archon':
            if self.fight_style == "Raid":
                simulated_hps *= 1.12 # Massive in Raid
                insights.append({"type": "success", "message": "Archon Halo execution scales incredibly well in massive Raid AoE."})
            else:
                simulated_hps *= 1.05 # Good in M+ but less targets
                insights.append({"type": "success", "message": "Archon provides solid burst healing for M+ trash packs."})
        elif hero == 'oracle':
            simulated_hps *= 1.02
            efficiency += 5.0 # Oracle greatly improves survivability via Premonition
            if self.fight_style == "Dungeon":
                 insights.append({"type": "info", "message": "Oracle's Premonition is preventing fatal damage, showing low HPS but high survival efficiency in M+."})

        # Base Talents
        if self.talents.get('apotheosis'):
            if self.fight_style == "Dungeon":
                simulated_hps *= 1.08
                efficiency += 4.0
                if self.healing_req == "Burst":
                    insights.append({"type": "success", "message": "Apotheosis perfectly matches Burst Healing requirements, allowing rapid Holy Word recovery."})
                    simulated_hps *= 1.05
            else:
                simulated_hps *= 1.03
        
        if self.talents.get('lightweaver'):
            if self.healing_req == "Spot":
                simulated_hps *= 1.08
                efficiency += 5.0
                insights.append({"type": "success", "message": "Lightweaver thrives in Spot Healing scenarios (saving Tanks and focused targets)."})
            elif self.fight_style == "Dungeon":
                simulated_hps *= 1.04
                insights.append({"type": "info", "message": "Lightweaver synergizes well with Flash Heal spot healing."})
            else:
                simulated_hps *= 1.01

        # Damage Profile specific class interactions (Holy Priest Base)
        if self.healing_req == "Ramp":
            # Holy Priest is reactive, not proactive. Ramp damage profiles are inherently inefficient.
            efficiency -= 15.0
            insights.append({"type": "warning", "message": "Holy Priest is reactive. Pure Ramp/setup profiles may cause efficiency loss compared to Druid or Discipline."})
        elif self.healing_req == "Burst":
             efficiency += 5.0 # Naturally good at burst
        elif self.healing_req == "Sustain":
            # Sustained rot / heavy aura damage.
            # Boost HPS from Mastery scaling in sustain environments.
            simulated_hps *= (1 + (self.pct['mastery'] * 0.5)) 
            insights.append({"type": "info", "message": "Sustained Aura damage heavily boosts Echo of Light (Mastery) value."})
            
            # Massive mana penalty if fight is long and it's a sustain fight
            if self.fight_length > 180:
                efficiency -= 12.0
                insights.append({"type": "warning", "message": "Heavy Sustained damage over a long duration causes massive OOM (Out of Mana) risk for Holy."})
            else:
                efficiency += 2.0
                
        # Versatility Survival Modifier (High Key Theorycrafting)
        if self.pct.get('versatility', 0) > 0.08: # If user has more than 8% vers
             efficiency += 8.0 # Huge consistency bonus
             insights.append({"type": "info", "message": "High Versatility (>8%) detected. This drastically improves Holy Priest (Cloth) survival in +15 keys against one-shots."})
        elif self.pct.get('versatility', 0) < 0.03:
             insights.append({"type": "warning", "message": "Low Versatility (<3%) may result in lethal one-shots in keys +15 or higher, regardless of your throughput."})

        return simulated_hps, efficiency, insights
