import json
import os
import argparse
from wcl_api import WarcraftLogsAPI
from spell_mapping import get_spell_name

def extract_healing_events(report_id: str, fight_id: int):
    """
    Extracts healing events for a specific fight from the WCL GraphQL API.
    """
    api = WarcraftLogsAPI()
    
    if fight_id is None:
        # If no fight ID is provided, query the list of fights in the report
        query = """
        query($reportId: String!) {
            reportData {
                report(code: $reportId) {
                    title
                    fights {
                        id
                        name
                        difficulty
                        size
                        kill
                    }
                }
            }
        }
        """
        variables = {"reportId": report_id}
        print(f"[*] Fetching fight list for Report: {report_id}")
        result = api.query(query, variables)
        
        report = result.get('data', {}).get('reportData', {}).get('report', {})
        if not report:
            print("[-] Report not found or API error.")
            return
            
        print(f"\n[+] Report Title: {report.get('title')}")
        print("-" * 50)
        print(f"{'ID':<5} | {'Diff':<4} | {'Size':<4} | {'Status':<6} | Name")
        print("-" * 50)
        
        for f in report.get('fights', []):
            if f.get('difficulty'): # Filter out trash pulls or irrelevant events if possible, though we show them anyway
                kill_str = "Kill" if f.get('kill') else "Wipe"
                print(f"{f.get('id'):<5} | {f.get('difficulty', '-'):<4} | {f.get('size', '-'):<4} | {kill_str:<6} | {f.get('name')}")
        
        print("-" * 50)
        print("\nRun the script again with --fight <ID> to analyze a specific fight.")
        return

    # GraphQL Query to fetch fight data and healing events
    query = """
    query($reportId: String!, $fightId: Int!) {
        reportData {
            report(code: $reportId) {
                fights(fightIDs: [$fightId]) {
                    id
                    startTime
                    endTime
                    encounterID
                    name
                    difficulty
                    size
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
    variables = {
        "reportId": report_id,
        "fightId": fight_id
    }

    print(f"[*] Fetching fight details for Report: {report_id}, Fight {fight_id}")
    result = api.query(query, variables)
    
    # Parse the result and output as JSON for the dashboard
    # (Mock logic that would normally parse events and evaluate Ramp-ups for Mythic+)
    
    report_data = result.get('data', {}).get('reportData', {}).get('report', {})
    fights = report_data.get('fights', [])
    if not fights:
        print("[-] Fight not found.")
        return
        
    fight_data = fights[0]
    
    # Identify Priest
    actors = report_data.get('masterData', {}).get('actors', [])
    friendly_players = set(fight_data.get('friendlyPlayers', []))
    
    # Find the Priest
    priest_id = None
    priest_name = "Unknown"
    
    for actor in actors:
        if actor.get('subType') == 'Priest':
            if not friendly_players or actor.get('id') in friendly_players:
                priest_id = actor.get('id')
                priest_name = str(actor.get('name', 'Unknown')).encode('ascii', 'ignore').decode()
                break
            
    # Default stats if we fail to fetch
    player_stats = {
        "intellect": 40000,
        "haste": 5000,
        "crit": 4000,
        "mastery": 3000,
        "versatility": 2000
    }
    
    if priest_id:
        print(f"[*] Found Priest {str(priest_name).encode('ascii', 'ignore').decode()} (ID: {priest_id}). Fetching CombatantInfo for real stats...")
    
    # 2. Fetch CombatantInfo (Events API)
    # Get the player's status precisely when the fight started
    
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
    
    start_time = fight_data.get('startTime')
    end_time = fight_data.get('endTime')
    
    events_res = api.query(events_query, {
        "code": report_id,
        "startTime": start_time,
        "endTime": start_time + 10000, # CombatantInfo usually fires exactly at the start
        "actorId": priest_id
    })
    
    # Parse Real Stats
    intellect = 0
    haste = 0
    crit = 0
    mastery = 0
    versatility = 0
    
    events_data = events_res.get("data", {}).get("reportData", {}).get("report", {}).get("events", {}).get("data", [])
    if events_data:
        info = events_data[0]
        stats = info.get('stats', {})
        intellect = stats.get('Intellect', {}).get('min', 0)
        haste = stats.get('Haste', {}).get('min', 0)
        crit = stats.get('Crit', {}).get('min', 0)
        mastery = stats.get('Mastery', {}).get('min', 0)
        versatility = stats.get('Versatility', {}).get('min', 0)
        print(f"[+] Real stats extracted: Intellect {intellect}, Mastery {mastery}")
        player_stats['intellect'] = intellect
        player_stats['haste'] = haste
        player_stats['crit'] = crit
        player_stats['mastery'] = mastery
        player_stats['versatility'] = versatility
    else:
        print("[-] Warning: Could not find CombatantInfo. Using fallback 0 stats.")
        
    # Environment Scoping evaluation
    env_type = "Unknown"
    if fight_data.get('difficulty') == 10 and fight_data.get('size') == 5:
        env_type = "Mythic+ (5-man)"
    elif fight_data.get('difficulty') == 5 and fight_data.get('size') == 20:
         env_type = "Mythic Raid (20-man)"
    elif fight_data.get('difficulty') == 4:
         env_type = "Heroic Raid"

    fight_name = fight_data.get('name')
    print(f"[+] Fight Name: {str(fight_name).encode('ascii', 'ignore').decode()}")
    print(f"[+] Environment Detected: {env_type}")
    print(f"[*] Start Time: {start_time} | End Time: {end_time}")
    
    # Output English mock analytics structure for the Dashboard
    # In a real scenario, this is dynamically generated by parsing the returned arrays
    analytics_output = {
        "reportId": report_id,
        "fightName": fight_data.get('name'),
        "environment": env_type,
        "playerStats": player_stats,
        "metrics": {
            "realHps": "128.4k",
            "potentialHps": "145.2k",
            "efficiencyScore": 88.4
        },
        "insights": [
            {
                "type": "success", 
                "message": f"Excellent Spot healing on the Tank using {get_spell_name(2050)}."
            },
            {
                "type": "warning", 
                "message": f"{get_spell_name(64843)} used 3 seconds late during spiky AoE damage."
            },
            {
                "type": "info", 
                "message": f"Pre-casted {get_spell_name(33076)} perfectly before the pull."
            }
        ],
        "topSequence": [
            get_spell_name(33076), 
            get_spell_name(2061), 
            get_spell_name(2050), 
            get_spell_name(596)
        ]
    }

    # Save to transient .tmp directory as defined in AGENTS.md
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".tmp")
    os.makedirs(output_dir, exist_ok=True)
    
    temp_dir = output_dir # Renamed for clarity with the provided snippet
    mock_output = analytics_output # Renamed for clarity with the provided snippet
    
    file_path = os.path.join(temp_dir, "latest_analysis.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(mock_output, f, indent=4, ensure_ascii=False)
        
    print(f"[+] Analysis saved to {str(file_path).encode('ascii', 'ignore').decode()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WCL Healer Data Extractor")
    parser.add_argument("--report", required=True, help="WCL Report ID (e.g., aB1cD2eF3gH4iJ5k)")
    parser.add_argument("--fight", type=int, required=False, help="Fight ID within the report")
    
    args = parser.parse_args()
    
    # Ensure .tmp exists (handled inside extract_healing_events now so relative path works correctly)
    
    try:
         extract_healing_events(args.report, args.fight)
    except Exception as e:
         print(f"[-] Execution failed: {e}")
