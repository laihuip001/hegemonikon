import { api } from './api/client';
import './styles.css';

// Simple Router
const routes: Record<string, () => Promise<void>> = {
    'dashboard': renderDashboard,
    'fep': renderFep,
    'gnosis': renderGnosis,
    'quality': renderQuality,
};

let currentRoute = 'dashboard';

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    navigate('dashboard');
});

function setupNavigation() {
    const navButtons = document.querySelectorAll('nav button');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const route = btn.getAttribute('data-route');
            if (route) navigate(route);
        });
    });
}

function navigate(route: string) {
    currentRoute = route;

    // Update Active State
    document.querySelectorAll('nav button').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-route') === route);
    });

    // Render View
    const app = document.getElementById('view-content');
    if (app) {
        app.innerHTML = '<div class="loading">Loading...</div>';
        const renderer = routes[route];
        if (renderer) {
            renderer().catch(err => {
                app.innerHTML = `< div class="error" > Error: ${err.message} </div>`;
            });
        }
    }
}

// --- View Renderers ---

async function renderDashboard() {
    const [health, fep] = await Promise.all([
        api.status().catch(() => null),
        api.fepState().catch(() => null)
    ]);

    const app = document.getElementById('view-content')!;

    const healthStatus = health
        ? `<span class="status-ok">Online (Score: ${health.score})</span>`
        : '<span class="status-error">Offline</span>';

    const historyLen = fep ? fep.history_length : '-';

    app.innerHTML = `
    <h1>Dashboard</h1>
    <div class="grid">
      <div class="card">
        <h3>System Status</h3>
        <div class="metric">${healthStatus}</div>
        <p>Uptime: ${health?.items.find(i => i.name === 'uptime')?.metric?.toFixed(0) || 0}s</p>
      </div>
      <div class="card">
        <h3>FEP Agent</h3>
        <div class="metric">${historyLen} <small>steps</small></div>
        <p>Active Inference History</p>
      </div>
    </div>
  `;
}

async function renderFep() {
    const state = await api.fepState();
    const app = document.getElementById('view-content')!;

    // Render Beliefs Bar Chart
    const beliefsHtml = state.beliefs.map((b: number) =>
        `<div class="belief-bar" style="height: ${b * 100}%" title="${b.toFixed(3)}"></div>`
    ).join('');

    app.innerHTML = `
    <h1>FEP Agent State</h1>
    <div class="card">
      <h3>Belief Distribution (48 dimensions)</h3>
      <div class="beliefs-chart">${beliefsHtml}</div>
    </div>
    <div class="grid">
       <div class="card">
         <h3>Epsilon (Precision)</h3>
         <pre>${JSON.stringify(state.epsilon, null, 2)}</pre>
       </div>
    </div>
  `;
}

async function renderGnosis() {
    const app = document.getElementById('view-content')!;
    app.innerHTML = `
    <h1>Gnōsis Search</h1>
    <div class="card">
      <input type="text" id="gpt-search-input" class="input" placeholder="Search knowledge base..." />
      <button id="gpt-search-btn" class="btn" style="margin-top: 0.5rem">Search</button>
    </div>
    <div id="search-results"></div>
  `;

    document.getElementById('gpt-search-btn')?.addEventListener('click', async () => {
        const query = (document.getElementById('gpt-search-input') as HTMLInputElement).value;
        if (!query) return;

        const resultsDiv = document.getElementById('search-results')!;
        resultsDiv.innerHTML = 'Searching...';

        try {
            const res = await api.gnosisSearch(query);
            resultsDiv.innerHTML = res.results.map(r => `
        <div class="search-result">
          <h3><a href="${r.url || '#'}" target="_blank">${r.title || 'Untitled'}</a></h3>
          <p>${r.abstract?.substring(0, 200)}...</p>
          <small>Score: ${r.score?.toFixed(2)} | Source: ${r.source}</small>
        </div>
      `).join('');
        } catch (e) {
            resultsDiv.innerHTML = `<div class="status-error">Search failed: ${e}</div>`;
        }
    });
}

async function renderQuality() {
    const report = await api.dendronReport('summary');
    const app = document.getElementById('view-content')!;
    const s = report.summary;

    app.innerHTML = `
    <h1>Code Quality (Dendron)</h1>
    <div class="grid">
      <div class="card">
        <h3>Coverage</h3>
        <div class="metric">${(s.coverage_percent * 100).toFixed(1)}%</div>
        <p>${s.files_with_proof} / ${s.total_files} files verified</p>
      </div>
       <div class="card">
        <h3>Structure</h3>
        <div class="metric">${s.total_dirs}</div>
        <p>Directories Tracked</p>
      </div>
    </div>
  `;
}
