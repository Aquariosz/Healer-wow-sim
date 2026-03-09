import requests
import re
import json
import time
import os

class WowheadItemScraper:
    def __init__(self, db_path="../item_db.json"):
        self.db_path = db_path
        self.db = self._load_db()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _load_db(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_db(self):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=4)

    def scrape_item(self, item_id, ilvl=None):
        """
        Scrapes a specific item from Wowhead XML tooltip endpoint.
        Mimics the BreakBB/wowhead_scraper logic for local caching.
        """
        dict_key = f"{item_id}_{ilvl}" if ilvl else str(item_id)
        if dict_key in self.db:
            print(f"[{item_id}] Already in local database cache.")
            return self.db[dict_key]

        print(f"[{item_id}] Scraping from Wowhead Database (ilvl: {ilvl})...")
        
        # We use the xml endpoint. For accurate scaling, bonus IDs are needed in reality.
        # This is an MVP implementation that grabs base stats or tooltip HTML.
        url = f"https://www.wowhead.com/item={item_id}&xml"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                html_tooltip = response.text
                
                # Extract Name
                name_match = re.search(r'<name><!\[CDATA\[(.*?)\]\]></name>', html_tooltip)
                name = name_match.group(1) if name_match else "Unknown"

                # Extract Stats from Tooltip
                # In wowhead tooltips: 
                # Intellect/Stamina/Strength/Agility are mapped via: <!--stat4-->+X Strength
                stats = {}
                
                # Primary Stats
                int_match = re.search(r'\+<!--stat(5|3|4)-->(\d+) (Intellect|Agility|Strength)', html_tooltip)
                if int_match:
                    stats["intellect"] = int_match.group(2) # We collapse primary to intellect for Healer Sim

                # Secondary Stats mapping:
                # 32 = Crit, 36 = Haste, 49 = Mastery, 40 = Versatility
                rtg_map = {"32": "crit", "36": "haste", "49": "mastery", "40": "versatility"}
                for rtg_code, stat_name in rtg_map.items():
                    val = re.search(r'\+<!--rtg' + rtg_code + r'-->(\d+)', html_tooltip)
                    if val:
                        stats[stat_name] = int(val.group(1))

                item_data = {
                    "id": item_id,
                    "name": name,
                    "stats": stats,
                    "ilvl_base": ilvl if ilvl else "Base",
                    "source": "wowhead_scraper"
                }
                
                self.db[dict_key] = item_data
                self.save_db()
                return item_data
            else:
                print(f"Failed to fetch {item_id}. HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Scraper Error on {item_id}: {str(e)}")
            return None

if __name__ == "__main__":
    scraper = WowheadItemScraper("item_db.json")
    
    # Test batch extraction (mimicking the github repo behavior)
    test_items = [212401, 193000, 201111]
    
    print("Initiating Local Item Database Build...")
    for item in test_items:
        scraper.scrape_item(item)
        time.sleep(1) # Be gentle to Wowhead
    
    print(f"Database sync complete. {len(scraper.db)} items cached.")
