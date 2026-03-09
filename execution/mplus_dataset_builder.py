import os
import json
import argparse
from wcl_api import WarcraftLogsAPI

def build_dataset_for_fight(report_id: str, fight_id: int):
    """
    Extracts high-fidelity M+ healing patterns (Casts & Damage Taken) to build
    a scalable dataset for the WoW Healer Simulator.
    """
    api = WarcraftLogsAPI()
    
    # 1. First query: Get the fight timestamps and composition
    meta_query = """
    query($reportId: String!, $fightId: Int!) {
        reportData {
            report(code: $reportId) {
                fights(fightIDs: [$fightId]) {
                    id
                    startTime
                    endTime
                    difficulty
                    size
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
    """
    
    print(f"[*] Fetching metadata for Report: {report_id}, Fight: {fight_id}...")
    meta_result = api.query(meta_query, {"reportId": report_id, "fightId": fight_id})
    report = meta_result.get('data', {}).get('reportData', {}).get('report', {})
    
    fights = report.get('fights', [])
    if not fights:
        print("[-] Fight not found.")
        return
        
    fight = fights[0]
    start_time = fight.get('startTime')
    end_time = fight.get('endTime')
    
    if fight.get('difficulty') != 10:
        print(f"[!] Warning: This fight (Difficulty: {fight.get('difficulty')}) is not a Mythic+ Dungeon.")
    
    # 2. Find the Holy Priest in the log
    actors = report.get('masterData', {}).get('actors', [])
    friendly_players = set(fight.get('friendlyPlayers', []))
    
    priest_id = None
    priest_name = None
    
    # Find the Priest
    priest_id = None
    priest_name = "Unknown"
    
    for actor in actors:
        if actor.get('subType') == 'Priest':
            if not friendly_players or actor.get('id') in friendly_players:
                priest_id = actor.get('id')
                priest_name = str(actor.get('name', 'Unknown')).encode('ascii', 'ignore').decode()
                break
            
    if not priest_id:
        print("[-] Could not find the Priest in the friendly composition for this fight.")
        return
        
    print(f"[+] Found Priest: {priest_name} (Actor ID: {priest_id}). Fetching events...")

    # 3. Second query: Fetch Casts by the Priest
    # (Note: In WCL API v2, fetching events might require pagination if limits are hit.
    # We use a basic query here for the MVP architecture).
    events_query = """
    query($reportId: String!, $start: Float!, $end: Float!, $sourceId: Int!) {
        reportData {
            report(code: $reportId) {
                casts: events(startTime: $start, endTime: $end, dataType: Casts, sourceID: $sourceId, limit: 10000) {
                    data
                    nextPageTimestamp
                }
                damageTaken: events(startTime: $start, endTime: $end, dataType: DamageTaken, limit: 10000) {
                    data
                    nextPageTimestamp
                }
            }
        }
    }
    """
    
    events_variables = {
        "reportId": report_id,
        "start": start_time,
        "end": end_time,
        "sourceId": priest_id
    }
    
    events_result = api.query(events_query, events_variables)
    
    report_events = events_result.get('data', {}).get('reportData', {}).get('report', {})
    casts_data = report_events.get('casts', {}).get('data', [])
    damage_taken_data = report_events.get('damageTaken', {}).get('data', [])
    
    print(f"[+] Extracted {len(casts_data)} Priest Casts and {len(damage_taken_data)} Damage Taken events.")
    
    # 4. Compile into a Training Simulator Object
    dataset_object = {
        "metadata": {
            "report_id": report_id,
            "fight_id": fight_id,
            "dungeon": fight.get('name'),
            "healer_name": priest_name,
            "duration_ms": end_time - start_time
        },
        "timeline_events": {
            "casts": casts_data,
            "damage_taken": damage_taken_data
        }
    }
    
    # 5. Save to dataset directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "..", ".tmp", "mplus_dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    
    dataset_path = os.path.join(dataset_dir, f"{report_id}_fight_{fight_id}.json")
    with open(dataset_path, "w", encoding='utf-8') as f:
        json.dump(dataset_object, f, indent=4, ensure_ascii=False)
        
    print("[+] Dataset fragment correctly built and stored for Machine Learning / Simulation at:")
    print(f"    -> {str(dataset_path).encode('ascii', 'ignore').decode()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M+ Dataset Builder for WoW Healer Simulator")
    parser.add_argument("--report", required=True, help="WCL Report ID")
    parser.add_argument("--fight", type=int, required=True, help="Fight ID within the report")
    
    args = parser.parse_args()
    
    try:
         build_dataset_for_fight(args.report, args.fight)
    except Exception as e:
         print(f"[-] Execution failed: {e}")
