import os
import json
import glob

def calculate_burst_sustain_ratio(damage_events, duration_s):
    if not damage_events or duration_s <= 0:
        return 0, 0
        
    # Group damage into 5-second windows
    windows = {}
    for ev in damage_events:
        # Some damage events might not have 'amount' or 'timestamp' explicitly if malformed,
        # but Warcarft Logs standard events have them.
        pts = ev.get('amount', 0)
        unmitigated = ev.get('unmitigatedAmount', pts) # Use unmitigated if available for true pressure
        
        ts = ev.get('timestamp', 0)
        
        # window index
        w_idx = int(ts / 5000)
        windows[w_idx] = windows.get(w_idx, 0) + unmitigated
        
    if not windows:
        return 0, 0
        
    total_damage = sum(windows.values())
    avg_damage_per_window = total_damage / max(1, len(windows))
    
    # Let's define "Burst" as any 5s window taking > 1.5x the average 5s damage of the run
    burst_threshold = avg_damage_per_window * 1.5
    
    burst_damage = 0
    sustain_damage = 0
    
    for w_dmg in windows.values():
        if w_dmg > burst_threshold:
            burst_damage += w_dmg
        else:
            sustain_damage += w_dmg
            
    # Return percentages
    burst_pct = (burst_damage / total_damage) * 100.0 if total_damage > 0 else 0
    sustain_pct = (sustain_damage / total_damage) * 100.0 if total_damage > 0 else 0
    
    return burst_pct, sustain_pct

def aggregate_datasets():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "..", ".tmp", "mplus_dataset")
    
    if not os.path.exists(dataset_dir):
        print("[-] No dataset directory found. Run extraction first.")
        return
        
    json_files = glob.glob(os.path.join(dataset_dir, "*.json"))
    if not json_files:
        print("[-] No JSON dataset files found.")
        return
        
    print(f"[*] Aggregating data from {len(json_files)} Mythic+ logs...")
    
    total_duration_s = 0
    total_damage_taken = 0
    
    dungeon_stats = {}
    
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        meta = data.get("metadata", {})
        dungeon = meta.get("dungeon", "Unknown")
        duration_ms = meta.get("duration_ms", 0)
        duration_s = duration_ms / 1000.0
        
        dmg_events = data.get("timeline_events", {}).get("damage_taken", [])
        
        run_damage = sum(ev.get('amount', 0) for ev in dmg_events)
        
        total_duration_s += duration_s
        total_damage_taken += run_damage
        
        burst_pct, sustain_pct = calculate_burst_sustain_ratio(dmg_events, duration_s)
        
        if dungeon not in dungeon_stats:
            dungeon_stats[dungeon] = {
                "runs": 0,
                "total_damage": 0,
                "total_duration_s": 0,
                "burst_pct_sum": 0,
                "sustain_pct_sum": 0
            }
            
        dungeon_stats[dungeon]["runs"] += 1
        dungeon_stats[dungeon]["total_damage"] += run_damage
        dungeon_stats[dungeon]["total_duration_s"] += duration_s
        dungeon_stats[dungeon]["burst_pct_sum"] += burst_pct
        dungeon_stats[dungeon]["sustain_pct_sum"] += sustain_pct
        
    # Global Baseline
    global_dtps = total_damage_taken / total_duration_s if total_duration_s > 0 else 0
    
    # Calculate averages per dungeon
    results = {
        "global_baseline_mplus": {
            "average_dtps": global_dtps,
            "total_runs_analyzed": len(json_files),
        },
        "dungeon_profiles": {}
    }
    
    for d, stats in dungeon_stats.items():
        runs = stats["runs"]
        d_dtps = stats["total_damage"] / stats["total_duration_s"] if stats["total_duration_s"] > 0 else 0
        avg_burst = stats["burst_pct_sum"] / runs
        avg_sustain = stats["sustain_pct_sum"] / runs
        
        # Classify the dungeon automatically based on the statistics
        profile_class = "Balanced"
        if avg_burst > 60:
            profile_class = "Burst"
        elif avg_sustain > 60:
            profile_class = "Sustain"
            
        results["dungeon_profiles"][d] = {
            "dtps": d_dtps,
            "burst_damage_pct": round(avg_burst, 2),
            "sustain_damage_pct": round(avg_sustain, 2),
            "auto_classified_profile": profile_class
        }
        
    # Save the aggregated statistical model
    output_path = os.path.join(base_dir, "..", ".tmp", "mplus_baseline.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print("[+] Aggregation Complete! M+ Statistical Baseline generated:")
    print(f"    -> Global DTPS: {global_dtps:.0f}")
    print("    -> Dungeon Profiles mapped:")
    for d, stats in results["dungeon_profiles"].items():
        print(f"       * {d}: {stats['auto_classified_profile']} ({stats['burst_damage_pct']}% Burst / {stats['sustain_damage_pct']}% Sustain)")
        
    print(f"[+] Saved to {output_path}")

if __name__ == "__main__":
    aggregate_datasets()
