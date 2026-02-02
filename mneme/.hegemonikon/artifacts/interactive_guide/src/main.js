import hubsData from './data/hubs.json';
import workflowsData from './data/workflows.json';

// State
const state = {
  hubs: hubsData.hubs,
  workflows: workflowsData.workflows,
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
  backBtn: document.getElementById('back-btn')
};

// --- Initialization ---
function init() {
  renderHubs();
  setupInputListeners();
  setupNavigation();
}

// --- Rendering ---
function renderHubs() {
  el.hubGrid.innerHTML = state.hubs.map(hub => `
    <div class="glass-card hub-card ${hub.color_var}" data-id="${hub.id}">
      <div class="hub-icon">${hub.symbol}</div>
      <h3 class="font-lg">${hub.name}</h3>
      <p class="font-sm">${hub.meaning}</p>
    </div>
  `).join('');

  // Add Click Listeners
  document.querySelectorAll('.hub-card').forEach(card => {
    card.addEventListener('click', () => showHubDetail(card.dataset.id));
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

// --- Navigation ---
function switchView(viewName) {
  if (viewName === 'detail') {
    el.homeView.classList.add('hidden');
    el.detailView.classList.remove('hidden');
  } else {
    el.detailView.classList.add('hidden');
    el.homeView.classList.remove('hidden');
  }
  state.currentView = viewName;
}

function setupNavigation() {
  el.backBtn.addEventListener('click', () => switchView('home'));
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
