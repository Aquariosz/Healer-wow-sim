import json
import sys
from execution.wcl_api import WarcraftLogsAPI

def list_composition(report_id, fight_id):
    api = WarcraftLogsAPI()
    query = """
    query($reportId: String!, $fightId: Int!) {
        reportData {
            report(code: $reportId) {
                fights(fightIDs: [$fightId]) {
                    friendlyPlayers
                }
                masterData {
                    actors {
                        id
                        name
                        type
                        subType
                    }
                }
            }
        }
    }
    """
    res = api.query(query, {"reportId": report_id, "fightId": fight_id})
    report = res.get("data", {}).get("reportData", {}).get("report", {})
    actors = report.get("masterData", {}).get("actors", [])
    fight = report.get("fights", [])[0]
    
    friendly = set(fight.get("friendlyPlayers", []))
    
    print(f"Group Composition for Fight {fight_id}:")
    for a in actors:
        if a.get('id') in friendly:
            name = a.get('name', '').encode('ascii', 'ignore').decode()
            print(f"ID: {a['id']}, Name: {name}, Class: {a['subType']}")

if __name__ == "__main__":
    list_composition("RNVqmCGyXgdY7hQ6", 8)
