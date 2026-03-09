import os
import json
import sys
sys.path.append('execution')
from wcl_api import WarcraftLogsAPI

api = WarcraftLogsAPI()

# A map of all 10 fights we processed in mplus_dataset_builder
fights = [
    {"report": "3h6n2KJrC7VMWXGD", "fight": 8},
    {"report": "QTGZ3dM94ry2nkKX", "fight": 3},
    {"report": "RNVqmCGyXgdY7hQ6", "fight": 8},
    {"report": "ZXfjwLhaxM1kHRbA", "fight": 2},
    {"report": "k7zbVXAdtYM1FNxg", "fight": 2},
    {"report": "ALm1gc3HpCWvwtZy", "fight": 2},
    # Mega log qcbMkLR3D7HvPGxf
    {"report": "qcbMkLR3D7HvPGxf", "fight": 2}, # The Seat of the Triumvirate
    {"report": "qcbMkLR3D7HvPGxf", "fight": 5}, # Nexus-Point Xenas
    {"report": "qcbMkLR3D7HvPGxf", "fight": 7}, # Windrunner Spire
    {"report": "qcbMkLR3D7HvPGxf", "fight": 8}, # Pit of Saron
]

def analyze_talents():
    print("[*] Fetching CombatantInfo for all 10 M+ logs to identify Priest Talents...")
    
    # We will track talent occurrences
    talent_frequency = {}
    
    # We will map "Build Archetypes"
    builds = []
    
    for entry in fights:
        report_id = entry['report']
        fight_id = entry['fight']
        
        # 1. Get fight and actors
        report_query = """
        query($code: String!) {
            reportData {
                report(code: $code) {
                    fights(fightIDs: [%s]) {
                        startTime
                        endTime
                        name
                        friendlyPlayers
                    }
                    masterData {
                        actors {
                            id
                            name
                            subType
                        }
                    }
                }
            }
        }
        """ % str(fight_id)
        
        res = api.query(report_query, {"code": report_id})
        report_data = res.get('data', {}).get('reportData', {}).get('report', {})
        fight_arr = report_data.get('fights', [])
        if not fight_arr:
            continue
            
        f_data = fight_arr[0]
        start_time = f_data.get('startTime')
        end_time = f_data.get('endTime')
        friendly_players = set(f_data.get('friendlyPlayers', []))
        actors = report_data.get('masterData', {}).get('actors', [])
        
        priest_id = None
        priest_name = "Unknown"
        for actor in actors:
            if actor.get('subType') == 'Priest':
                if not friendly_players or actor.get('id') in friendly_players:
                    priest_id = actor.get('id')
                    priest_name = str(actor.get('name')).encode('ascii', 'ignore').decode()
                    break
                    
        if not priest_id:
            continue
            
        # 2. Extract CombatantInfo to get Talents
        events_query = """
        query($code: String!, $startTime: Float!, $endTime: Float!, $actorId: Int!) {
            reportData {
                report(code: $code) {
                    events(startTime: $startTime, endTime: $endTime, sourceID: $actorId, dataType: CombatantInfo) {
                        data
                    }
                }
            }
        }
        """
        
        events_res = api.query(events_query, {
            "code": report_id,
            "startTime": start_time,
            "endTime": start_time + 10000,
            "actorId": priest_id
        })
        
        events_data = events_res.get("data", {}).get("reportData", {}).get("report", {}).get("events", {}).get("data", [])
        if events_data:
            info = events_data[0]
            talents_list = info.get('talents', [])
            
            # Since we only get IDs, let's track the array sizes and hashes to see if they differ
            talent_ids = tuple(sorted([t.get('id') for t in talents_list]))
            
            # Determine Archetype via known spell IDs (simplified mock detection)
            # You would normally map these IDs precisely to wowhead spells.
            # E.g. 372616 refers to Lightweaver, etc.
            
            archetype = "Standard Holy"
            # Just tracking frequency
            for t in talents_list:
                tid = t.get('id')
                if tid not in talent_frequency:
                    talent_frequency[tid] = 0
                talent_frequency[tid] += 1
                
            builds.append({
                "priest": priest_name,
                "dungeon": f_data.get('name'),
                "talent_hash": str(hash(talent_ids))[-6:],
                "count": len(talent_ids)
            })
            
    # Print logic
    print("-" * 50)
    print("Priest Builds Extracted across M+ Runs:")
    print("-" * 50)
    for b in builds:
        print(f"[{b['dungeon']}] {b['priest']} | Unique Talent Hash: {b['talent_hash']} | Skills Total: {b['count']}")
        
    print("-" * 50)
    # Check if they are all using the EXACT same build
    hashes = set([b['talent_hash'] for b in builds])
    if len(hashes) == 1:
        print("[+] CONCLUSION: All Top M+ Priests analyzed are running the EXACT SAME meta talent build.")
    else:
        print(f"[!] CONCLUSION: There are {len(hashes)} different talent builds being used, suggesting competitive variety in M+.")

if __name__ == "__main__":
    analyze_talents()
