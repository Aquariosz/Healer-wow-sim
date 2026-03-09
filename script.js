document.addEventListener('DOMContentLoaded', () => {
    // Class selection logic
    const classBtns = document.querySelectorAll('.class-btn');
    classBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            classBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Minimal simulated update
            document.querySelector('.real-fill').style.width = '0%';
            document.querySelector('.potential-fill').style.width = '0%';

            setTimeout(() => {
                const isEvoker = btn.id === 'btn-evoker';
                const realVal = isEvoker ? '135.2k' : '124.5k';
                const potVal = isEvoker ? '154.0k' : '142.8k';
                const eff = isEvoker ? '87.8%' : '87.1%';
                const realPct = isEvoker ? '87.8%' : '87.1%';

                document.querySelector('.real-value').textContent = realVal;
                document.querySelector('.potential-value').textContent = potVal;
                document.querySelector('.score-value').textContent = eff;

                document.querySelector('.real-fill').style.width = realPct;
                document.querySelector('.potential-fill').style.width = '100%';
            }, 300);
        });
    });

    // Environment card selection
    const envCards = document.querySelectorAll('.env-card');
    envCards.forEach(card => {
        card.addEventListener('click', () => {
            envCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
        });
    });

    // SimC Import Logic
    const btnImportSimc = document.getElementById('btn-import-simc');
    if (btnImportSimc) {
        btnImportSimc.addEventListener('click', () => {
            const rawText = document.getElementById('simc-input-text').value;
            if (!rawText.trim()) return;

            try {
                const parsedData = window.SimCParser.parse(rawText);
                console.log("Parsed SimC Data:", parsedData);

                // Show Top Gear Section
                document.getElementById('top-gear-section').style.display = 'block';

                // Render List
                const container = document.getElementById('gear-list-container');
                container.innerHTML = '';

                // Combine all items into a list to be grouped
                const allItems = [
                    ...parsedData.equipped.map(i => ({ ...i, source: 'equipped', selected: true })),
                    ...parsedData.bags.map(i => ({ ...i, source: 'bag', selected: false })),
                    ...parsedData.vault.map(i => ({ ...i, source: 'vault', selected: false }))
                ];

                // Remove Unknown Items
                const validItems = allItems.filter(i => i.id !== null && i.slot);

                // Group by Slot
                const groupedBySlot = {};

                // Define rendering order
                const slotOrder = ['head', 'neck', 'shoulder', 'back', 'chest', 'wrist', 'hands', 'waist', 'legs', 'feet', 'finger1', 'finger2', 'trinket1', 'trinket2', 'main_hand', 'off_hand', 'two_hand'];

                validItems.forEach(item => {
                    // sometimes simc produces strange slot names or prefixes
                    let trueSlot = item.slot.replace(/^(bag_|vault_)/, '');
                    if (!groupedBySlot[trueSlot]) groupedBySlot[trueSlot] = [];
                    groupedBySlot[trueSlot].push(item);
                });

                // Render Slot Columns
                slotOrder.forEach(slot => {
                    const itemsInSlot = groupedBySlot[slot];
                    if (!itemsInSlot || itemsInSlot.length === 0) return;

                    const slotGroup = document.createElement('div');
                    slotGroup.className = 'gear-slot-group';

                    const slotTitle = document.createElement('h3');
                    slotTitle.className = 'gear-slot-title';
                    slotTitle.textContent = slot.replace('_', ' ').toUpperCase();
                    slotGroup.appendChild(slotTitle);

                    itemsInSlot.forEach(item => {
                        // Create a card for each item
                        const card = document.createElement('label');
                        card.className = `gear-card ${item.selected ? 'selected' : ''}`;
                        card.style.cursor = 'pointer'; // Make it clickable

                        // Checkbox (hidden for styling, or visible but seamlessly integrated)
                        const cb = document.createElement('input');
                        cb.type = 'checkbox';
                        cb.checked = item.selected;
                        cb.className = 'gear-checkbox';
                        cb.style.display = 'none'; // we will use the card's visual state instead
                        cb.dataset.raw = item.rawLine;
                        cb.dataset.slot = item.slot;

                        // 1. Build Wowhead Query string for both text and icon
                        let whParams = [];
                        if (item.bonus_ids && item.bonus_ids.length > 0) whParams.push(`bonus=${item.bonus_ids.join(':')}`);
                        if (item.enchant) whParams.push(`ench=${item.enchant}`);
                        if (item.gem_id && item.gem_id.length > 0) whParams.push(`gems=${item.gem_id.join(':')}`);
                        if (item.ilevel) whParams.push(`ilvl=${item.ilevel}`);

                        let whUrl = `https://www.wowhead.com/item=${item.id}`;
                        if (whParams.length > 0) whUrl += `?${whParams.join('&')}`;

                        // Visual elements
                        const iconPlaceholder = document.createElement('a');
                        iconPlaceholder.href = whUrl;
                        iconPlaceholder.dataset.whRenameLink = 'false';
                        iconPlaceholder.dataset.whIconSize = 'medium';
                        iconPlaceholder.className = `gear-icon-placeholder quality-${item.ilevel >= 610 ? 'epic' : 'rare'}`;
                        iconPlaceholder.style.display = 'block';

                        const detailsContent = document.createElement('div');
                        detailsContent.className = 'gear-details';

                        const itemName = document.createElement('a');
                        itemName.className = 'gear-name';
                        itemName.style.textDecoration = 'none';
                        itemName.style.color = 'inherit';
                        itemName.href = whUrl;
                        itemName.dataset.whIconSize = 'none'; // text only
                        itemName.textContent = item.name;

                        const itemLevel = document.createElement('div');
                        itemLevel.className = 'gear-ilvl';
                        itemLevel.innerHTML = `<span style="color:var(--text-muted); font-size: 0.8em; margin-right:4px;">ILVL</span>${item.ilevel || '?'}`;

                        if (item.source !== 'equipped') {
                            const sourceTag = document.createElement('span');
                            sourceTag.style.fontSize = '0.7em';
                            sourceTag.style.marginLeft = '6px';
                            sourceTag.style.padding = '2px 4px';
                            sourceTag.style.borderRadius = '3px';
                            sourceTag.style.background = 'rgba(255,255,255,0.1)';
                            sourceTag.style.color = '#ccc';
                            sourceTag.textContent = item.source === 'bag' ? 'BAG' : 'VAULT';
                            itemLevel.appendChild(sourceTag);
                        }

                        detailsContent.appendChild(itemName);
                        detailsContent.appendChild(itemLevel);

                        card.appendChild(cb);
                        card.appendChild(iconPlaceholder);
                        card.appendChild(detailsContent);

                        // Card Selection Logic
                        cb.addEventListener('change', (e) => {
                            if (e.target.checked) card.classList.add('selected');
                            else card.classList.remove('selected');
                        });

                        slotGroup.appendChild(card);
                    });

                    container.appendChild(slotGroup);
                });

                // Trigger Wowhead power.js to scan new DOM for icon injection
                setTimeout(() => {
                    if (typeof $WH !== 'undefined') {
                        if ($WH.Tooltip && $WH.Tooltip.refreshLinks) $WH.Tooltip.refreshLinks();
                        else if ($WH.powerTooltips && $WH.powerTooltips.refreshLinks) $WH.powerTooltips.refreshLinks();
                    }
                }, 100);

                btnImportSimc.innerText = '✔ Imported Successfully';
                setTimeout(() => btnImportSimc.innerText = 'Import Gear & Talents', 2000);
            } catch (e) {
                console.error("Failed to parse SimC", e);
                alert("Error parsing SimC data. Make sure you copied the entire addon output.");
            }
        });
    }

    // Load Real Stats from WCL Extractor
    const btnLoadStats = document.getElementById('btn-load-stats');
    if (btnLoadStats) {
        btnLoadStats.addEventListener('click', async () => {
            const originalText = btnLoadStats.innerHTML;
            btnLoadStats.innerHTML = 'Loading...';

            try {
                const response = await fetch('.tmp/latest_analysis.json');
                if (!response.ok) throw new Error("Data not found");

                const data = await response.json();

                if (data.playerStats) {
                    document.getElementById('stat-intellect').value = data.playerStats.intellect || 0;
                    document.getElementById('stat-haste').value = data.playerStats.haste || 0;
                    document.getElementById('stat-crit').value = data.playerStats.crit || 0;
                    document.getElementById('stat-mastery').value = data.playerStats.mastery || 0;
                    document.getElementById('stat-versatility').value = data.playerStats.versatility || 0;

                    btnLoadStats.innerHTML = '✔ Stats Loaded!';
                    btnLoadStats.style.color = '#4ade80';
                    btnLoadStats.style.borderColor = '#4ade80';
                }
            } catch (err) {
                console.error(err);
                btnLoadStats.innerHTML = '✖ Error Loading';
                btnLoadStats.style.color = '#f87171';
            }

            setTimeout(() => {
                btnLoadStats.innerHTML = originalText;
                btnLoadStats.style.color = '';
                btnLoadStats.style.borderColor = '';
            }, 3000);
        });
    }

    // Analyze button effect (now Run Simulation)
    const btnSimulate = document.getElementById('btn-simulate');

    btnSimulate.addEventListener('click', async () => {
        // Collect Stats
        const baseStats = {
            intellect: parseInt(document.getElementById('base-intellect').value) || 0,
            haste: parseInt(document.getElementById('base-haste').value) || 0,
            crit: parseInt(document.getElementById('base-crit').value) || 0,
            mastery: parseInt(document.getElementById('base-mastery').value) || 0,
            versatility: parseInt(document.getElementById('base-versatility').value) || 0
        };
        const upgStats = {
            intellect: parseInt(document.getElementById('upg-intellect').value) || 0,
            haste: parseInt(document.getElementById('upg-haste').value) || 0,
            crit: parseInt(document.getElementById('upg-crit').value) || 0,
            mastery: parseInt(document.getElementById('upg-mastery').value) || 0,
            versatility: parseInt(document.getElementById('upg-versatility').value) || 0
        };
        // 2. Fetch Talents directly from the interactive WoWhead tree state
        // If the user hasn't clicked anything, talentState might be empty.
        const talents = typeof talentState !== 'undefined' ? {
            apotheosis: talentState['apotheosis'] > 0,
            lightweaver: talentState['lightweaver'] > 0,
            divine_image: talentState['divine_image'] > 0,
            miracle_worker: talentState['miracle_worker'] > 0,
            pontifex: talentState['pontifex'] > 0,
            heroTalent: document.getElementById('hero-talent-select').value
        } : { heroTalent: document.getElementById('hero-talent-select').value };
        const originalText = btnSimulate.innerHTML;
        btnSimulate.innerHTML = `
            <svg class="animate-spin" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="animation: spin 1s linear infinite;"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
            Simulating...
            <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
        `;

        // Reset bars
        document.querySelector('.real-fill').style.width = '0%';

        const fightStyle = document.getElementById('fight-style').value;
        const fightLength = parseInt(document.getElementById('fight-length').value, 10);
        const healingReq = document.getElementById('healing-requirement').value;

        try {
            // Call the Python Simulation Engine natively
            const response = await fetch('/api/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    base_stats: baseStats,
                    upg_stats: upgStats,
                    talents: talents,
                    fight_style: fightStyle,
                    fight_length: fightLength,
                    healing_requirement: healingReq
                })
            });

            if (!response.ok) {
                throw new Error("Simulation Engine Offline. Backend not responding.");
            }

            const engineData = await response.json();

            if (engineData.error) {
                throw new Error(engineData.error);
            }

            // Extract actual python simulated numbers
            const simulatedRealHps = engineData.metrics.realHps;
            const simulatedPotHps = engineData.metrics.potentialHps;
            const simEfficiency = engineData.metrics.efficiencyScore + "%";

            setTimeout(() => {
                btnSimulate.innerHTML = originalText;

                // Update interface
                document.querySelector('.real-value').textContent = simulatedRealHps;
                document.querySelector('.potential-value').textContent = simulatedPotHps;

                // Update Efficiency purely based on engine returns
                document.querySelector('.score-value').innerText = simEfficiency;
                document.querySelector('.real-fill').style.width = simEfficiency;

                // Handle the UI difference label
                const increaseHps = engineData.metrics.increase_hps || 0;
                const increasePct = engineData.metrics.increase_pct || 0;
                const diffEl = document.getElementById('upgrade-diff-text');

                if (increasePct > 0) {
                    diffEl.innerText = `(+${(increaseHps / 1000).toFixed(1)}k | +${increasePct.toFixed(1)}%)`;
                    diffEl.style.color = '#4ade80'; // Green
                } else if (increasePct < 0) {
                    diffEl.innerText = `(${(increaseHps / 1000).toFixed(1)}k | ${increasePct.toFixed(1)}%)`;
                    diffEl.style.color = '#ef4444'; // Red
                } else {
                    diffEl.innerText = '';
                }

                // Update Insights from Engine
                const insightsList = document.querySelector('.insights-list');
                insightsList.innerHTML = ''; // Clear previous

                engineData.insights.forEach(insight => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <div class="insight-icon ${insight.type}"></div>
                        <div class="insight-text">${insight.message}</div>
                    `;
                    insightsList.appendChild(li);
                });

            }, 1200);

        } catch (error) {
            console.error(error);
            setTimeout(() => {
                btnSimulate.innerHTML = originalText;
                alert("Simulation Engine Error: Could not connect to Dataset.");
            }, 500);
        }
    });

    // Initial animation for progress bars
    setTimeout(() => {
        document.querySelector('.real-fill').style.width = '87.1%';
        document.querySelector('.potential-fill').style.width = '100%';
    }, 500);
});

// Layout interaction
