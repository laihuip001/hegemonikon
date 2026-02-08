#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: Attractor Engine ダッシュボード — mixture, inhibition, E/I flow の可視化
"""
Attractor Dashboard

24 定理 Attractor Engine の状態を可視化する。
入力テキストに対する:
  - Mixture 分布 (Q2 entropy + Series 集約)
  - Inhibition Network (Q7 抑制パターン)
  - E/I Flow 比較 (excitation-only vs E/I)
  - Basin Separation (Q1 distance map)

Usage:
    python scripts/attractor_dashboard.py "Why does this truly exist?"
    python scripts/attractor_dashboard.py --serve  # ブラウザで自動起動
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def generate_attractor_data(query: str) -> dict:
    """入力クエリに対する Attractor 分析データを生成."""
    from mekhane.fep.theorem_attractor import TheoremAttractor, THEOREM_KEYS

    ta = TheoremAttractor()

    # Q2: Mixture
    mixture = ta.diagnose_mixture(query)

    # Standard suggest
    suggest = ta.suggest(query, top_k=24)

    # Q4: Multiview suggest
    multiview = ta.suggest_multiview(query, top_k=24)

    # Q1: Basin separation
    sep = ta.basin_separation()

    # E/I Flow comparison
    flow_excite = ta.simulate_flow(query, steps=10)
    flow_ei_02 = ta.simulate_flow_ei(query, steps=12, beta=0.2)
    flow_ei_04 = ta.simulate_flow_ei(query, steps=12, beta=0.4)

    # Q7: Inhibition for top-3 theorems
    top3 = [r.theorem for r in suggest[:3]]
    inhibition_data = {}
    for t in top3:
        inhibited = ta.get_inhibited(t, threshold=0.03)  # row-norm'd values are smaller
        inhibition_data[t] = inhibited[:5]

    # Q6: Decomposition
    decomp = ta.suggest_decomposed(query)

    # 24 定理の SimMatrix for heatmap (from prototype)
    ta._ensure_initialized()
    proto = ta._proto_tensor
    if hasattr(proto, 'cpu'):
        proto = proto.cpu().numpy()
    import numpy as np
    norms = np.linalg.norm(proto, axis=1, keepdims=True)
    norms[norms == 0] = 1
    proto_normed = proto / norms
    sim_matrix = (proto_normed @ proto_normed.T).tolist()

    return {
        "query": query,
        "theorem_keys": THEOREM_KEYS,
        "mixture": {
            "distribution": mixture.distribution,
            "entropy": mixture.entropy,
            "dominant_series": mixture.dominant_series,
            "series_distribution": mixture.series_distribution,
        },
        "suggest": [
            {"theorem": r.theorem, "name": r.name, "sim": round(r.similarity, 4)}
            for r in suggest
        ],
        "multiview": [
            {"theorem": r.theorem, "name": r.name, "sim": round(r.similarity, 4)}
            for r in multiview
        ],
        "flows": {
            "excite": {
                "label": "Excitation-Only",
                "converged": flow_excite.converged_at,
                "states": [
                    {"step": s.step, "top3": s.top_theorems[:3]}
                    for s in flow_excite.states
                ],
            },
            "ei_02": {
                "label": "E/I (β=0.2)",
                "converged": flow_ei_02.converged_at,
                "states": [
                    {"step": s.step, "top3": s.top_theorems[:3]}
                    for s in flow_ei_02.states
                ],
            },
            "ei_04": {
                "label": "E/I (β=0.4)",
                "converged": flow_ei_04.converged_at,
                "states": [
                    {"step": s.step, "top3": s.top_theorems[:3]}
                    for s in flow_ei_04.states
                ],
            },
        },
        "inhibition": {t: [(p, round(s, 4)) for p, s in pairs]
                       for t, pairs in inhibition_data.items()},
        "decomposition": {
            "divergence": decomp["divergence"],
            "segments": [
                {"text": seg["text"], "top": seg["theorems"][0].theorem if seg["theorems"] else "?"}
                for seg in decomp["segments"]
            ],
        },
        "separation": {
            "avg": round(sep["avg_separation"], 4),
            "min": round(sep["min_separation"], 4),
            "max": round(sep["max_separation"], 4),
            "closest": [(t1, t2, round(d, 4)) for t1, t2, d in sep["closest_pairs"]],
            "farthest": [(t1, t2, round(d, 4)) for t1, t2, d in sep["farthest_pairs"]],
        },
        "sim_matrix": [[round(v, 3) for v in row] for row in sim_matrix],
    }


def generate_html(data: dict) -> str:
    """Attractor Dashboard HTML を生成."""
    series_colors = {
        "O": "#e74c3c", "S": "#3498db", "H": "#f39c12",
        "P": "#2ecc71", "K": "#9b59b6", "A": "#1abc9c",
    }
    data_json = json.dumps(data, ensure_ascii=False)
    colors_json = json.dumps(series_colors)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🧠 Attractor Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Inter', 'Noto Sans JP', system-ui, sans-serif;
    background: #0a0e17;
    color: #e0e6ed;
    min-height: 100vh;
}}
.header {{
    background: linear-gradient(135deg, #1a1f35 0%, #0d1321 100%);
    padding: 24px 32px;
    border-bottom: 1px solid rgba(99, 179, 237, 0.15);
}}
.header h1 {{
    font-size: 1.5rem; font-weight: 600;
    background: linear-gradient(90deg, #63b3ed, #b794f6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.header .query {{
    color: #a0aec0; font-size: 0.95rem; margin-top: 6px;
    font-style: italic;
}}
.metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px; padding: 20px 32px;
}}
.metric-card {{
    background: linear-gradient(135deg, #1a2332 0%, #141c2b 100%);
    border: 1px solid rgba(99, 179, 237, 0.1);
    border-radius: 12px; padding: 16px; text-align: center;
}}
.metric-value {{
    font-size: 1.8rem; font-weight: 700;
    background: linear-gradient(90deg, #63b3ed, #b794f6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.metric-label {{ color: #718096; font-size: 0.75rem; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }}
.grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px; padding: 0 32px 32px;
}}
.card {{
    background: linear-gradient(135deg, #1a2332 0%, #141c2b 100%);
    border: 1px solid rgba(99, 179, 237, 0.1);
    border-radius: 12px; padding: 20px;
}}
.card.full {{ grid-column: 1 / -1; }}
.card h3 {{
    font-size: 0.9rem; color: #a0aec0; margin-bottom: 14px; font-weight: 500;
}}
canvas {{ width: 100% !important; }}
.flow-table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; }}
.flow-table th {{ color: #718096; text-align: left; padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
.flow-table td {{ padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.03); }}
.flow-table .converged {{ color: #68d391; }}
.inhib-item {{
    display: inline-block; margin: 4px;
    background: rgba(252, 129, 129, 0.1);
    border: 1px solid rgba(252, 129, 129, 0.2);
    border-radius: 8px; padding: 4px 10px; font-size: 0.75rem;
}}
.inhib-source {{ color: #63b3ed; font-weight: 600; margin-bottom: 6px; }}
.sep-pair {{
    display: inline-block; margin: 4px;
    border-radius: 8px; padding: 4px 10px; font-size: 0.75rem;
}}
.sep-close {{ background: rgba(252,129,129,0.1); border: 1px solid rgba(252,129,129,0.2); color: #fc8181; }}
.sep-far {{ background: rgba(104,211,145,0.1); border: 1px solid rgba(104,211,145,0.2); color: #68d391; }}
.decomp-seg {{
    display: inline-block; margin: 4px;
    background: rgba(99,179,237,0.1);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 8px; padding: 4px 10px; font-size: 0.75rem; color: #63b3ed;
}}
</style>
</head>
<body>
<div class="header">
    <h1>🧠 Attractor Dashboard — 24 定理認知マップ</h1>
    <div class="query">Query: "{data['query']}"</div>
</div>

<div class="metrics" id="metrics"></div>
<div class="grid" id="charts"></div>

<script>
const D = {data_json};
const COLORS = {colors_json};

// --- Metrics ---
const metricsEl = document.getElementById('metrics');
const metrics = [
    {{ label: 'Entropy', value: D.mixture.entropy.toFixed(2) }},
    {{ label: 'Dominant', value: D.mixture.dominant_series }},
    {{ label: 'Top-1', value: D.suggest[0].theorem }},
    {{ label: 'MV Top-1', value: D.multiview[0].theorem }},
    {{ label: 'Divergence', value: D.decomposition.divergence.toFixed(2) }},
    {{ label: 'Sep (avg)', value: D.separation.avg.toFixed(3) }},
];
metricsEl.innerHTML = metrics.map(m => `
    <div class="metric-card">
        <div class="metric-value">${{m.value}}</div>
        <div class="metric-label">${{m.label}}</div>
    </div>`).join('');

// --- Charts Grid ---
const chartsEl = document.getElementById('charts');

// 1. Mixture Bar Chart
chartsEl.innerHTML += `<div class="card"><h3>🔬 Mixture Distribution (T=0.05)</h3><canvas id="mixChart" height="200"></canvas></div>`;
// 2. Series Pie
chartsEl.innerHTML += `<div class="card"><h3>📊 Series Distribution</h3><canvas id="seriesChart" height="200"></canvas></div>`;
// 3. Flow Comparison Table
chartsEl.innerHTML += `<div class="card full"><h3>🌊 Flow Comparison — Excitation vs E/I</h3><div id="flowTable"></div></div>`;
// 4. Inhibition Network
chartsEl.innerHTML += `<div class="card"><h3>🚫 Inhibition Network (Q7)</h3><div id="inhibDiv"></div></div>`;
// 5. Separation
chartsEl.innerHTML += `<div class="card"><h3>📏 Basin Separation (Q1)</h3><div id="sepDiv"></div></div>`;
// 6. Decomposition
chartsEl.innerHTML += `<div class="card full"><h3>🔍 Segment Decomposition (Q6)</h3><div id="decompDiv"></div></div>`;

// --- Mixture Bar ---
const mixCtx = document.getElementById('mixChart').getContext('2d');
const mixLabels = Object.keys(D.mixture.distribution);
const mixValues = Object.values(D.mixture.distribution);
const mixColors = mixLabels.map(t => COLORS[t[0]] || '#7f8c8d');
new Chart(mixCtx, {{
    type: 'bar',
    data: {{
        labels: mixLabels,
        datasets: [{{ data: mixValues, backgroundColor: mixColors, borderWidth: 0 }}]
    }},
    options: {{
        responsive: true, indexAxis: 'y',
        scales: {{
            x: {{ grid: {{ color: 'rgba(255,255,255,0.03)' }}, ticks: {{ color: '#718096' }} }},
            y: {{ ticks: {{ color: '#a0aec0', font: {{ size: 10 }} }} }}
        }},
        plugins: {{ legend: {{ display: false }} }}
    }}
}});

// --- Series Pie ---
const seriesCtx = document.getElementById('seriesChart').getContext('2d');
const seriesLabels = Object.keys(D.mixture.series_distribution);
const seriesValues = Object.values(D.mixture.series_distribution);
new Chart(seriesCtx, {{
    type: 'doughnut',
    data: {{
        labels: seriesLabels,
        datasets: [{{
            data: seriesValues,
            backgroundColor: seriesLabels.map(s => COLORS[s] || '#7f8c8d'),
            borderWidth: 0
        }}]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#a0aec0' }} }} }} }}
}});

// --- Flow Table ---
const flowDiv = document.getElementById('flowTable');
let html = '<table class="flow-table"><tr><th>Step</th>';
for (const key of ['excite', 'ei_02', 'ei_04']) {{
    html += `<th>${{D.flows[key].label}}</th>`;
}}
html += '</tr>';
const maxSteps = Math.max(...Object.values(D.flows).map(f => f.states.length));
for (let i = 0; i < Math.min(maxSteps, 8); i++) {{
    html += `<tr><td>${{i}}</td>`;
    for (const key of ['excite', 'ei_02', 'ei_04']) {{
        const st = D.flows[key].states[i];
        if (st) {{
            const tops = st.top3.map(([t, v]) => `${{t}}(${{v.toFixed(3)}})`).join(' ');
            const cls = D.flows[key].converged === i ? 'converged' : '';
            html += `<td class="${{cls}}">${{tops}}</td>`;
        }} else {{
            html += '<td>—</td>';
        }}
    }}
    html += '</tr>';
}}
html += '</table>';
flowDiv.innerHTML = html;

// --- Inhibition ---
const inhibDiv = document.getElementById('inhibDiv');
let inhibHtml = '';
for (const [src, pairs] of Object.entries(D.inhibition)) {{
    inhibHtml += `<div class="inhib-source">${{src}} ⊣</div>`;
    pairs.forEach(([tgt, str]) => {{
        inhibHtml += `<span class="inhib-item">${{tgt}} (${{str.toFixed(3)}})</span>`;
    }});
    inhibHtml += '<br>';
}}
inhibDiv.innerHTML = inhibHtml;

// --- Separation ---
const sepDiv = document.getElementById('sepDiv');
let sepHtml = '<b style="color:#fc8181">Closest:</b><br>';
D.separation.closest.forEach(([t1, t2, d]) => {{
    sepHtml += `<span class="sep-pair sep-close">${{t1}}-${{t2}}: ${{d}}</span>`;
}});
sepHtml += '<br><br><b style="color:#68d391">Farthest:</b><br>';
D.separation.farthest.forEach(([t1, t2, d]) => {{
    sepHtml += `<span class="sep-pair sep-far">${{t1}}-${{t2}}: ${{d}}</span>`;
}});
sepDiv.innerHTML = sepHtml;

// --- Decomposition ---
const decompDiv = document.getElementById('decompDiv');
let decompHtml = `<div style="margin-bottom:8px; color:#718096">Divergence: ${{D.decomposition.divergence}}</div>`;
D.decomposition.segments.forEach(seg => {{
    decompHtml += `<span class="decomp-seg">"${{seg.text}}" → ${{seg.top}}</span>`;
}});
decompDiv.innerHTML = decompHtml;
</script>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Attractor Dashboard")
    parser.add_argument(
        "query", nargs="?", default="Why does this truly exist?",
        help="入力テキスト (default: 'Why does this truly exist?')",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output HTML path",
    )
    parser.add_argument(
        "--serve", action="store_true",
        help="生成後にブラウザで自動起動",
    )
    args = parser.parse_args()

    print(f"[*] Query: {args.query}")
    data = generate_attractor_data(args.query)

    print(f"[*] Mixture: H={data['mixture']['entropy']:.2f}, dom={data['mixture']['dominant_series']}")
    print(f"[*] Top-3: {', '.join(r['theorem'] for r in data['suggest'][:3])}")

    html = generate_html(data)

    output_path = args.output or str(
        Path.home() / "oikos/hegemonikon/logs/attractor_dashboard.html"
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n[✓] Dashboard: {output_path}")

    if args.serve:
        import webbrowser
        webbrowser.open(f"file://{output_path}")


if __name__ == "__main__":
    main()
