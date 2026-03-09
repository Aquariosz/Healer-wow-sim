import sys
sys.path.append('execution')
from wcl_api import WarcraftLogsAPI
import json

api = WarcraftLogsAPI()
res = api.query('query { reportData { report(code: "qcbMkLR3D7HvPGxf") { masterData { actors { id name subType } } } } }')
actors = res.get('data', {}).get('reportData', {}).get('report', {}).get('masterData', {}).get('actors', [])
for a in actors:
    if a.get('subType') in ('Priest', 'Paladin', 'Monk', 'Druid', 'Shaman', 'Evoker'):
        print(f"Actor: {str(a['name']).encode('ascii', 'ignore').decode()} ID: {a['id']} SubType: {a['subType']}")
