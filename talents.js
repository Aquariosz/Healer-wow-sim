// We map the Core MVP Talents that impact the Python HPS Engine
// The Grid is 10x10.
// x = column (1 to 10), y = row (1 to 10)

const allTalents = [
    // --- CLASS TREE ---
    {
        id: "pw_life",
        name: "Power Word: Life",
        tree: "class",
        icon: "https://wow.zamimg.com/images/wow/icons/large/spell_holy_powerwordlife.jpg",
        type: "active",
        maxPoints: 1,
        x: 5,
        y: 5,
        description: "Heals a target heavily if below 35% health.",
        linksTo: []
    },
    {
        id: "protective_light",
        name: "Protective Light",
        tree: "class",
        icon: "https://wow.zamimg.com/images/wow/icons/large/spell_holy_holyprotection.jpg",
        type: "passive",
        maxPoints: 1,
        x: 5,
        y: 7,
        description: "Flash Heal reduces damage you take by 10%.",
        linksTo: ["pw_life"]
    },

    // --- HERO TREE (Archon) ---
    {
        id: "power_surge",
        name: "Power Surge",
        tree: "hero",
        icon: "https://wow.zamimg.com/images/wow/icons/large/spell_holy_halo.jpg",
        type: "passive",
        maxPoints: 1,
        x: 3,
        y: 2,
        description: "Halo creates additional surges.",
        linksTo: []
    },
    {
        id: "manifested_power",
        name: "Manifested Power",
        tree: "hero",
        icon: "https://wow.zamimg.com/images/wow/icons/large/achievement_boss_algalon_01.jpg",
        type: "passive",
        maxPoints: 1,
        x: 3,
        y: 4,
        description: "Surges of Halo increase your healing done.",
        linksTo: ["power_surge"]
    },

    // --- SPEC TREE (Holy) ---
    {
        id: "lightweaver",
        name: "Lightweaver",
        tree: "spec",
        icon: "https://wow.zamimg.com/images/wow/icons/large/spell_holy_lightweaver.jpg",
        type: "passive",
        maxPoints: 2,
        x: 3,
        y: 8,
        description: "Flash Heal reduces the cast time of your next Heal and increases its healing.",
        linksTo: []
    },
    {
        id: "apotheosis",
        name: "Apotheosis",
        tree: "spec",
        icon: "https://wow.zamimg.com/images/wow/icons/large/spell_holy_apotheosis.jpg",
        type: "active",
        maxPoints: 1,
        x: 5,
        y: 9,
        description: "Reset the cooldowns of your Holy Words, and enter a pure Holy form.",
        linksTo: ["lightweaver", "pontifex"] // Visual connection lines
    },
    {
        id: "pontifex",
        name: "Pontifex",
        tree: "spec",
        icon: "https://wow.zamimg.com/images/wow/icons/large/spell_holy_divineprovidence.jpg",
        type: "passive",
        maxPoints: 1,
        x: 7,
        y: 8,
        description: "Holy Words increase the healing of your next specific spell.",
        linksTo: []
    },
    {
        id: "divine_image",
        name: "Divine Image",
        tree: "spec",
        icon: "https://wow.zamimg.com/images/wow/icons/large/spell_holy_divineimage.jpg",
        type: "passive",
        maxPoints: 1,
        x: 5,
        y: 6,
        description: "Using a Holy Word has a chance to summon a Naaru image.",
        linksTo: ["apotheosis"]
    },
    {
        id: "miracle_worker",
        name: "Miracle Worker",
        tree: "spec",
        icon: "https://wow.zamimg.com/images/wow/icons/large/ability_priest_miracleworker.jpg",
        type: "passive",
        maxPoints: 1,
        x: 5,
        y: 3,
        description: "Holy Word: Serenity and Holy Word: Sanctify gain 1 additional charge.",
        linksTo: ["divine_image"]
    }
];

let talentState = {};
const MAX_POINTS = {
    class: 31,
    hero: 10,
    spec: 30
};

function initTalentState() {
    if (Object.keys(talentState).length === 0) {
        allTalents.forEach(t => {
            talentState[t.id] = 0; // 0 points spent
        });
    }
}

function renderTalentTree() {
    initTalentState();

    // Render each panel independently
    renderPanel('class', 'priest-class-tree', 'class-links-svg', 'class-points-spent');
    renderPanel('hero', 'hero-talent-tree', 'hero-links-svg', null); // Hero has no explicit pt tracker normally, but we have 10 max
    renderPanel('spec', 'holy-spec-tree', 'spec-links-svg', 'spec-points-spent');
}

function renderPanel(treeType, gridId, svgId, pointsCounterId) {
    const grid = document.getElementById(gridId);
    const svgLayer = document.getElementById(svgId);

    if (!grid || !svgLayer) return;

    grid.innerHTML = '';
    svgLayer.innerHTML = '';

    const panelTalents = allTalents.filter(t => t.tree === treeType);
    let pointsSpentInTree = 0;

    // 1. Render Lines First (Delayed for layout)
    setTimeout(() => {
        panelTalents.forEach(sourceTalent => {
            if (sourceTalent.linksTo && sourceTalent.linksTo.length > 0) {
                sourceTalent.linksTo.forEach(targetId => {
                    const targetTalent = panelTalents.find(t => t.id === targetId);
                    if (targetTalent) {
                        drawSvgLine(sourceTalent, targetTalent, svgLayer, grid.parentElement);
                    }
                });
            }
        });
    }, 100);

    // 2. Render Nodes
    panelTalents.forEach(talent => {
        const wrapper = document.createElement('div');
        wrapper.className = `talent-node-wrapper talent-type-${talent.type}`;
        wrapper.style.gridColumn = talent.x;
        wrapper.style.gridRow = talent.y;
        wrapper.id = `node-${talent.id}`;

        const currentPoints = talentState[talent.id];
        pointsSpentInTree += currentPoints;

        if (currentPoints > 0) {
            wrapper.classList.add('active');
            if (currentPoints === talent.maxPoints) {
                wrapper.classList.add('maxed');
            }
        }

        wrapper.innerHTML = `
            <a href="https://www.wowhead.com/spell=${encodeURIComponent(talent.name)}" data-wh-rename-link="false" data-wh-icon-size="none" style="text-decoration:none; color:inherit; display:flex; flex-direction:column; align-items:center; justify-content:center; width:100%; height:100%;">
                <img src="${talent.icon}" class="talent-icon" alt="${talent.name}">
                <div class="talent-points">${currentPoints}/${talent.maxPoints}</div>
            </a>
        `;

        // Interaction (Left Click = Add, Right Click = Remove)
        wrapper.addEventListener('click', (e) => handleTalentClick(e, talent, 1));
        wrapper.addEventListener('contextmenu', (e) => handleTalentClick(e, talent, -1));

        grid.appendChild(wrapper);
    });

    if (pointsCounterId) {
        document.getElementById(pointsCounterId).textContent = pointsSpentInTree;
    }
}

function drawSvgLine(source, target, svgLayer, parentContainer) {
    const sourceEl = document.getElementById(`node-${source.id}`);
    const targetEl = document.getElementById(`node-${target.id}`);

    if (!sourceEl || !targetEl) return;

    // Get position relative to the panel container (parentContainer)
    const containerRect = parentContainer.getBoundingClientRect();
    const sRect = sourceEl.getBoundingClientRect();
    const tRect = targetEl.getBoundingClientRect();

    const sX = sRect.left - containerRect.left + (sRect.width / 2);
    const sY = sRect.top - containerRect.top + (sRect.height / 2);
    const tX = tRect.left - containerRect.left + (tRect.width / 2);
    const tY = tRect.top - containerRect.top + (tRect.height / 2);

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', sX);
    line.setAttribute('y1', sY);
    line.setAttribute('x2', tX);
    line.setAttribute('y2', tY);
    line.setAttribute('class', 'talent-link-line');
    line.id = `link-${source.id}-${target.id}`;

    // Active path
    if (talentState[target.id] > 0) {
        line.classList.add('active');
    }

    svgLayer.appendChild(line);
}

function handleTalentClick(e, talent, delta) {
    e.preventDefault(); // Prevent right-click menu

    const current = talentState[talent.id];
    let newVal = current + delta;

    if (newVal < 0) newVal = 0;
    if (newVal > talent.maxPoints) newVal = talent.maxPoints;

    // Check tree limits
    const treePointsSpent = allTalents.filter(t => t.tree === talent.tree).reduce((sum, t) => sum + talentState[t.id], 0);
    if (delta > 0 && treePointsSpent >= MAX_POINTS[talent.tree] && current === newVal) {
        return; // Max points reached for this tree
    }

    if (current !== newVal) {
        talentState[talent.id] = newVal;
        renderTalentTree();
    }
}

// Ensure load
window.addEventListener('DOMContentLoaded', () => {
    // Fire it up if at least one grid exists
    if (document.getElementById('priest-class-tree')) {
        renderTalentTree();
    }
});
