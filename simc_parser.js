/**
 * SimC Parser Engine
 * Parses raw text from the SimulationCraft addon and extracts equipped gear, bags, and vault items.
 */

class SimCParser {
    static parse(rawText) {
        const lines = rawText.split('\n').map(line => line.trim());
        const data = {
            character: {},
            equipped: [],
            bags: [],
            vault: [],
            rawStats: {} // Optional: if we want to parse the comment block of stats
        };
        // 1. Identify Sections
        let currentMode = 'equipped'; // 'equipped', 'bags', 'vault'
        let lastCommentName = "Unknown Item";

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i].trim();
            if (!line) continue;

            // Section Headers
            if (line.includes('### Gear from Bags')) {
                currentMode = 'bags';
                continue;
            } else if (line.includes('### Weekly Reward Choices')) {
                currentMode = 'vault';
                continue;
            } else if (line.includes('### End of Weekly Reward Choices')) {
                currentMode = 'equipped'; // reset or whatever
                continue;
            }

            // Character parsing (only when not in bags/vault)
            if (currentMode === 'equipped' && !line.startsWith('#')) {
                if (line.startsWith('level=')) data.character.level = parseInt(line.split('=')[1]);
                else if (line.startsWith('race=')) data.character.race = line.split('=')[1];
                else if (line.startsWith('role=')) data.character.role = line.split('=')[1];
                else if (line.startsWith('spec=')) data.character.spec = line.split('=')[1];
                else if (line.startsWith('talents=')) data.character.talents = line.split('=')[1];
            }

            // The actual SimC Addon outputs the item name as a comment right before the slot line
            // Example:
            // # Hood of the Cleared Mind (610)
            // head=,id=12345,bonus_id=...
            // Or for bags:
            // #
            // # Hood of the Cleared Mind (610)
            // # head=,id=12345

            if (line.startsWith('#')) {
                let text = line.replace(/^#\s*/, '').trim();
                // If the comment doesn't look like a slot assignment, it might be the name
                if (text && !text.includes('=')) {
                    lastCommentName = text; // Usually looks like "Item Name (610)"
                }
            }

            // Now, check if this line is a gear assignment
            // For equipped: "head=,id=..." or "head=item_name,id=..."
            // For bags/vault: "# head=,id=..."
            let isGearLine = false;
            let gearVal = "";
            let gearSlot = "";

            // List of valid slots from simc
            const validSlots = ["head", "neck", "shoulder", "shirt", "chest", "waist", "legs", "feet", "wrist", "hands", "finger1", "finger2", "trinket1", "trinket2", "back", "main_hand", "off_hand", "two_hand"];

            // Check if line contains a valid slot
            for (let slot of validSlots) {
                // regex to match "slot=" either at start of line or after "# "
                // e.g. "^head=" or "^# head="
                const re = new RegExp(`^(?:#\\s*)?(${slot})=([^\\s]*)`);
                const match = line.match(re);
                if (match) {
                    isGearLine = true;
                    gearSlot = match[1];
                    gearVal = match[2]; // the rest of the string ",id=123..."
                    break;
                }
            }

            if (isGearLine) {
                // Found gear
                const itemData = this._parseItemString(`slot=${gearVal}`, gearSlot, lastCommentName, line);

                if (currentMode === 'equipped') {
                    data.equipped.push(itemData);
                } else if (currentMode === 'bags') {
                    data.bags.push(itemData);
                } else if (currentMode === 'vault') {
                    data.vault.push(itemData);
                }

                // reset last name
                lastCommentName = "Unknown Item";
            }
        }

        return data;
    }

    static _parseItemString(rawConfig, slot, commentName, rawFullLine) {
        // rawConfig looks like "slot=,id=12345,bonus_id=1/2/3" or "slot=item_name,id=12345"
        const parts = rawConfig.split(',');
        const itemObj = {
            slot: slot,
            name: commentName || "Unknown",
            id: null,
            bonus_ids: [],
            enchant: null,
            ilevel: null,
            rawLine: rawFullLine
        };

        // If the commentName has item level inside it e.g. "Hood (610)" extract it
        const lvlMatch = itemObj.name.match(/\((\d+)\)$/);
        if (lvlMatch) {
            itemObj.ilevel = parseInt(lvlMatch[1], 10);
            itemObj.name = itemObj.name.replace(/\s*\(\d+\)$/, '').trim();
        }
        for (let i = 1; i < parts.length; i++) {
            const pair = parts[i].split('=');
            if (pair.length !== 2) continue;

            const key = pair[0];
            const val = pair[1];

            if (key === 'id') itemObj.id = parseInt(val);
            if (key === 'bonus_id') itemObj.bonus_ids = val.split('/').map(v => parseInt(v));
            if (key === 'enchant_id' || key === 'enchant') itemObj.enchant = parseInt(val);
            if (key === 'gem_id') itemObj.gem_id = val.split('/').map(v => parseInt(v));
            if (key === 'ilevel') itemObj.ilevel = parseInt(val);
        }

        return itemObj;
    }

    static _prettyName(rawName) {
        return rawName.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
}

// Export for browser
window.SimCParser = SimCParser;
