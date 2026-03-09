import json
from execution.wcl_api import WarcraftLogsAPI

def test():
    api = WarcraftLogsAPI()
    query = """
    query($reportId: String!, $start: Float!, $end: Float!, $sourceId: Int!) {
        reportData {
            report(code: $reportId) {
                events(startTime: $start, endTime: $end, dataType: CombatantInfo, sourceID: $sourceId, limit: 1) {
                    data
                }
            }
        }
    }
    """
    res = api.query(query, {
        "reportId": "ZXfjwLhaxM1kHRbA",
        "start": 194730,
        "end": 2175693,
        "sourceId": 5
    })
    
    with open("combatant_info_test.json", "w") as f:
        json.dump(res, f, indent=4)

if __name__ == "__main__":
    test()
