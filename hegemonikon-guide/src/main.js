import hubsData from './data/hubs.json';
import workflowsData from './data/workflows.json';
import xSeriesData from './data/x-series.json';

// State
const state = {
  hubs: hubsData.hubs,
  workflows: workflowsData.workflows,
  xRelations: xSeriesData.relations,
  currentView: 'home'
};

// DOM Elements
const el = {
  hubGrid: document.getElementById('hub-grid'),
  cmdInput: document.getElementById('cmd-input'),
  suggestionBox: document.getElementById('suggestion-box'),
  homeView: document.getElementById('home-view'),
  detailView: document.getElementById('detail-view'),
  detailContent: document.getElementById('detail-content'),
  backBtn: document.getElementById('back-btn'),
  // X-Series Elements
  xSeriesView: document.getElementById('x-series-view'),
  xBackBtn: document.getElementById('x-back-btn'),
  navXSeries: document.getElementById('nav-x-series'),
  xSvg: document.getElementById('x-svg'),
  xNodesLayer: document.getElementById('x-nodes-layer'),
  xInfoPanel: document.getElementById('x-info-panel')
};

// --- Initialization ---
function init() {
  renderHubs();
  setupInputListeners();
  setupNavigation();
  renderXSeries(); // Pre-render X-Series
}

// --- Rendering ---
function renderHubs() {
  el.hubGrid.innerHTML = state.hubs.map(hub => `
    <div class="glass-card hub-card ${hub.color_var}" data-id="${hub.id}" role="button" tabindex="0" aria-label="${hub.name} Hub">
      <div class="hub-icon">${hub.symbol}</div>
      <h3 class="font-lg">${hub.name}</h3>
      <p class="font-sm">${hub.meaning}</p>
    </div>
  `).join('');

  // Add Listeners
  document.querySelectorAll('.hub-card').forEach(card => {
    card.addEventListener('click', () => showHubDetail(card.dataset.id));
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        showHubDetail(card.dataset.id);
      }
    });
  });
}

function showHubDetail(hubId) {
  const hub = state.hubs.find(h => h.id === hubId);
  if (!hub) return;

  const content = `
    <div class="glass-panel hub-detail ${hub.color_var}" style="padding: var(--space-xl);">
      <div class="flex-center" style="justify-content: flex-start; gap: var(--space-md); margin-bottom: var(--space-lg);">
        <div class="hub-icon" style="margin:0;">${hub.symbol}</div>
        <div>
          <h2 class="font-xl">${hub.name}</h2>
          <p class="text-accent">${hub.meaning}</p>
        </div>
      </div>
      
      <p class="font-lg" style="margin-bottom: var(--space-lg);">${hub.description}</p>
      
      <h3 class="font-lg" style="margin-bottom: var(--space-md);">Included Modules</h3>
      <div class="grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));">
        ${hub.modules.map(mod => `
          <div class="glass-card">
            <span class="font-bold">${mod}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  el.detailContent.innerHTML = content;
  switchView('detail');
}

// --- X-Series Rendering ---
function renderXSeries() {
  const centerX = 300;
  const centerY = 300;
  const radius = 200;
  const nodeRadius = 30;

  // 1. Calculate Node Positions (Hexagonal/Circular)
  // O is top (actually O-S-H-P-K-A order?)
  // Let's use the layout from spec: O (top), S(top-right), etc?
  // Spec: O (Top), S (Right Top), H (Right Bottom), P (Bottom), K (Left Bottom), A (Left Top)
  // Indices: 0:O, 1:S, 2:H, 3:P, 4:K, 5:A
  const hubOrder = ['o', 's', 'h', 'p', 'k', 'a']; // Clockwise starting from top?
  // Angle: -90 deg (Top) is start.

  const nodePositions = {};

  // Render Nodes
  el.xNodesLayer.innerHTML = hubOrder.map((hubId, i) => {
    const angleDeg = (i * 60) - 90;
    const angleRad = angleDeg * (Math.PI / 180);
    const x = centerX + radius * Math.cos(angleRad);
    const y = centerY + radius * Math.sin(angleRad);

    nodePositions[hubId] = { x, y };

    const hub = state.hubs.find(h => h.id === hubId);

    // Position absolute, centered at x,y
    return `
      <div class="x-node ${hub.color_var}" data-id="${hubId}"
           style="position: absolute; left: ${x - nodeRadius}px; top: ${y - nodeRadius}px;
                  width: ${nodeRadius * 2}px; height: ${nodeRadius * 2}px;
                  border-radius: 50%; display: flex; align-items: center; justify-content: center;
                  background: var(--bg-secondary); border: 2px solid var(--hub-color);
                  box-shadow: 0 0 15px rgba(0,0,0,0.5); cursor: pointer; z-index: 10;
                  transition: transform 0.2s;">
        <span style="font-weight: 800; color: var(--text-primary);">${hub.symbol}</span>
      </div>
    `;
  }).join('');

  // Render Lines (SVG)
  // Generate lines for all 36 relations, hidden by default (opacity 0.1)
  // We will highlight them on hover

  el.xSvg.innerHTML = state.xRelations.map(rel => {
    const from = nodePositions[rel.from];
    const to = nodePositions[rel.to];

    // Skip self-loops for simple line drawing (or handle them differently)
    if (rel.from === rel.to) return ''; // Visualizing self-loops is tricky in this simple view

    return `
      <line class="x-line" data-from="${rel.from}" data-to="${rel.to}"
            x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}"
            stroke="var(--text-secondary)" stroke-width="1" opacity="0.1"
            style="transition: opacity 0.3s, stroke 0.3s, stroke-width 0.3s;" />
      
      <!-- Arrow marker could be added here ideally -->
    `;
  }).join('');

  // Add Interactions
  document.querySelectorAll('.x-node').forEach(node => {
    node.addEventListener('mouseenter', () => highlightRelations(node.dataset.id));
    node.addEventListener('mouseleave', () => resetHighlights());
    node.addEventListener('click', () => highlightRelations(node.dataset.id, true)); // Persistent on click?
  });
}

function highlightRelations(sourceHubId, isPersistent = false) {
  // 1. Dim all lines
  document.querySelectorAll('.x-line').forEach(line => {
    line.style.opacity = '0.05';
    line.style.stroke = 'var(--text-secondary)';
    line.style.strokeWidth = '1';
  });

  // 2. Highlight outgoing lines
  const outgoing = state.xRelations.filter(r => r.from === sourceHubId);
  const outgoingHtml = outgoing.map(r => {
    // Determine priority style
    const isPriority = r.priority === 1;
    const color = isPriority ? 'var(--text-accent)' : 'var(--text-primary)';

    // Highlight SVG Line
    const lineEl = document.querySelector(`.x-line[data-from="${r.from}"][data-to="${r.to}"]`);
    if (lineEl) {
      lineEl.style.opacity = '1';
      lineEl.style.stroke = isPriority ? 'var(--border-accent)' : 'var(--text-primary)';
      lineEl.style.strokeWidth = isPriority ? '3' : '1.5';
      // Bring to front in SVG z-order? (DOM order) - hard in SVG without re-appending
    }

    return `
      <div class="glass-card" style="border-left: 3px solid ${isPriority ? 'var(--border-accent)' : 'var(--text-secondary)'};">
        <div class="flex-center" style="justify-content: space-between;">
          <strong class="font-lg">${r.to.toUpperCase()}</strong>
          <span class="font-sm">${r.path}</span>
        </div>
        <div class="font-sm" style="color: ${color};">${r.meaning}</div>
      </div>
    `;
  }).join('');

  // Update Info Panel
  const hub = state.hubs.find(h => h.id === sourceHubId);
  el.xInfoPanel.innerHTML = `
    <h3 class="font-lg" style="margin-bottom: var(--space-sm); color: var(--hub-${sourceHubId});">${hub.name} (${hub.meaning})</h3>
    <div class="grid" style="grid-template-columns: 1fr 1fr; gap: var(--space-xs); text-align: left;">
      ${outgoingHtml}
    </div>
  `;
}

function resetHighlights() {
  // Reset lines
  document.querySelectorAll('.x-line').forEach(line => {
    line.style.opacity = '0.1';
    line.style.stroke = 'var(--text-secondary)';
    line.style.strokeWidth = '1';
  });

  // Reset Info Panel
  el.xInfoPanel.innerHTML = `
    <p style="color: var(--text-secondary); padding-top: var(--space-md);">Hub をホバーして関係を確認</p>
  `;
}


// --- Navigation ---
function switchView(viewName) {
  // Hide all
  el.homeView.classList.add('hidden');
  el.detailView.classList.add('hidden');
  el.xSeriesView.classList.add('hidden');

  if (viewName === 'detail') {
    el.detailView.classList.remove('hidden');
  } else if (viewName === 'x-series') {
    el.xSeriesView.classList.remove('hidden');
  } else {
    el.homeView.classList.remove('hidden');
  }
  state.currentView = viewName;
}

function setupNavigation() {
  el.backBtn.addEventListener('click', () => switchView('home'));
  el.xBackBtn.addEventListener('click', () => switchView('home'));
  el.navXSeries.addEventListener('click', () => switchView('x-series'));
  el.navXSeries.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      switchView('x-series');
    }
  });
}

// --- Command Input Logic ---
function setupInputListeners() {
  el.cmdInput.addEventListener('input', (e) => {
    const val = e.target.value;
    if (val.startsWith('/')) {
      showSuggestions(val);
    } else {
      hideSuggestions();
    }
  });

  // Close suggestions when clicking outside
  document.addEventListener('click', (e) => {
    if (!el.cmdInput.contains(e.target) && !el.suggestionBox.contains(e.target)) {
      hideSuggestions();
    }
  });
}

function showSuggestions(inputVal) {
  const matches = state.workflows.filter(wf =>
    wf.command.startsWith(inputVal) ||
    wf.description.toLowerCase().includes(inputVal.toLowerCase())
  );

  if (matches.length === 0) {
    hideSuggestions();
    return;
  }

  el.suggestionBox.innerHTML = matches.map(wf => `
    <div class="suggestion-item" onclick="selectCommand('${wf.command}')">
      <span class="suggestion-cmd">${wf.command}</span>
      <span class="font-sm">${wf.description}</span>
    </div>
  `).join('');

  el.suggestionBox.classList.add('active');
}

function hideSuggestions() {
  el.suggestionBox.classList.remove('active');
}

// Global scope for onclick handler (Vite modules are scoped)
window.selectCommand = (cmd) => {
  el.cmdInput.value = cmd;
  hideSuggestions();
  el.cmdInput.focus();
};

// Start
init();
