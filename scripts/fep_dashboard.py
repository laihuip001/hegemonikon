#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: FEP v2 学習過程の可視化ダッシュボード
"""
FEP v2 Visualization Dashboard

E2E endurance テストのログから学習過程を可視化する。
HTML ダッシュボードを生成し、ブラウザで表示。

Usage:
    python scripts/fep_dashboard.py
    python scripts/fep_dashboard.py --log logs/e2e_endurance_*.jsonl
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_log(log_path: str) -> list:
    """JSONL ログを読み込む"""
    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def analyze(entries: list) -> dict:
    """ログエントリを分析"""
    # Time series data
    entropy_over_time = []
    confidence_over_time = []
    action_counts = Counter()
    series_counts = Counter()
    action_series_over_time = []  # (cycle_idx, action, series)
    
    # Sliding window for entropy trend
    window_size = 50
    entropy_windows = []
    
    for i, e in enumerate(entries):
        if "error" in e:
            continue
        
        entropy = e.get("entropy", 0)
        confidence = e.get("confidence", 0)
        action = e.get("action", "unknown")
        series = e.get("series") or "none"
        
        entropy_over_time.append(entropy)
        confidence_over_time.append(confidence)
        action_counts[action] += 1
        series_counts[series] += 1
        action_series_over_time.append((i, action, series))
        
        # Sliding window entropy
        if len(entropy_over_time) >= window_size:
            window = entropy_over_time[-window_size:]
            entropy_windows.append(sum(window) / len(window))
    
    # Phase detection (entropy plateau detection)
    phases = []
    if entropy_windows:
        current_phase_start = 0
        current_mean = entropy_windows[0]
        threshold = 0.1
        
        for i, ew in enumerate(entropy_windows):
            if abs(ew - current_mean) > threshold:
                phases.append({
                    "start": current_phase_start,
                    "end": i,
                    "mean_entropy": current_mean,
                })
                current_phase_start = i
                current_mean = ew
        phases.append({
            "start": current_phase_start,
            "end": len(entropy_windows),
            "mean_entropy": current_mean,
        })
    
    return {
        "total_entries": len(entries),
        "valid_entries": len(entropy_over_time),
        "entropy_over_time": entropy_over_time,
        "confidence_over_time": confidence_over_time,
        "entropy_windows": entropy_windows,
        "action_counts": dict(action_counts),
        "series_counts": dict(series_counts),
        "action_series_over_time": action_series_over_time,
        "phases": phases,
        "entropy_start": entropy_over_time[0] if entropy_over_time else 0,
        "entropy_end": entropy_over_time[-1] if entropy_over_time else 0,
        "entropy_min": min(entropy_over_time) if entropy_over_time else 0,
        "entropy_max": max(entropy_over_time) if entropy_over_time else 0,
    }


def generate_html(analysis: dict, log_path: str) -> str:
    """HTML ダッシュボードを生成"""
    
    # Downsample for chart (max 500 points)
    entropy = analysis["entropy_over_time"]
    confidence = analysis["confidence_over_time"]
    step = max(1, len(entropy) // 500)
    entropy_sampled = entropy[::step]
    confidence_sampled = confidence[::step]
    windows_sampled = analysis["entropy_windows"][::max(1, len(analysis["entropy_windows"]) // 500)]
    
    # Series color map
    series_colors = {
        "O": "#e74c3c", "S": "#3498db", "H": "#f39c12",
        "P": "#2ecc71", "K": "#9b59b6", "A": "#1abc9c",
        "none": "#7f8c8d",
    }
    
    # Action timeline data (sampled)
    timeline_step = max(1, len(analysis["action_series_over_time"]) // 1000)
    timeline_data = analysis["action_series_over_time"][::timeline_step]
    
    # Series distribution for pie chart
    series_data = json.dumps(analysis["series_counts"])
    action_data = json.dumps(analysis["action_counts"])
    
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FEP v2 — Learning Dashboard</title>
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
    font-size: 1.5rem;
    font-weight: 600;
    background: linear-gradient(90deg, #63b3ed, #b794f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.header .subtitle {{ color: #718096; font-size: 0.85rem; margin-top: 4px; }}
.metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    padding: 24px 32px;
}}
.metric-card {{
    background: linear-gradient(135deg, #1a2332 0%, #141c2b 100%);
    border: 1px solid rgba(99, 179, 237, 0.1);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}}
.metric-value {{
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #63b3ed, #b794f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.metric-label {{ color: #718096; font-size: 0.8rem; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }}
.charts {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    padding: 0 32px 32px;
}}
.chart-card {{
    background: linear-gradient(135deg, #1a2332 0%, #141c2b 100%);
    border: 1px solid rgba(99, 179, 237, 0.1);
    border-radius: 12px;
    padding: 24px;
}}
.chart-card.full {{ grid-column: 1 / -1; }}
.chart-card h3 {{
    font-size: 0.95rem;
    color: #a0aec0;
    margin-bottom: 16px;
    font-weight: 500;
}}
canvas {{ width: 100% !important; }}
.phase-list {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}}
.phase-tag {{
    background: rgba(99, 179, 237, 0.1);
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.75rem;
    color: #63b3ed;
}}
</style>
</head>
<body>
<div class="header">
    <h1>🧠 FEP v2 — Learning Dashboard</h1>
    <div class="subtitle">Log: {Path(log_path).name} | Generated from {analysis['total_entries']} entries</div>
</div>

<div class="metrics">
    <div class="metric-card">
        <div class="metric-value">{analysis['valid_entries']}</div>
        <div class="metric-label">Total Cycles</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{analysis['entropy_start']:.2f}</div>
        <div class="metric-label">Initial Entropy</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{analysis['entropy_end']:.2f}</div>
        <div class="metric-label">Final Entropy</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{analysis['entropy_min']:.2f}</div>
        <div class="metric-label">Min Entropy</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{len(analysis['phases'])}</div>
        <div class="metric-label">Learning Phases</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{len(analysis['series_counts']) - (1 if 'none' in analysis['series_counts'] else 0)}</div>
        <div class="metric-label">Active Series</div>
    </div>
</div>

<div class="charts">
    <div class="chart-card full">
        <h3>📈 Entropy Over Time (Sliding Window = 50)</h3>
        <canvas id="entropyChart" height="80"></canvas>
    </div>

    <div class="chart-card">
        <h3>🎯 Action Distribution</h3>
        <canvas id="actionChart" height="200"></canvas>
    </div>

    <div class="chart-card">
        <h3>📊 Series Distribution</h3>
        <canvas id="seriesChart" height="200"></canvas>
    </div>

    <div class="chart-card full">
        <h3>🔄 Learning Phases</h3>
        <div class="phase-list">
            {"".join(f'<span class="phase-tag">Phase {i+1}: cycles {p["start"]}-{p["end"]} (entropy ≈ {p["mean_entropy"]:.2f})</span>' for i, p in enumerate(analysis["phases"]))}
        </div>
    </div>
</div>

<script>
// Entropy chart
const entropyCtx = document.getElementById('entropyChart').getContext('2d');
new Chart(entropyCtx, {{
    type: 'line',
    data: {{
        labels: {json.dumps(list(range(len(entropy_sampled))))},
        datasets: [{{
            label: 'Raw Entropy',
            data: {json.dumps([round(e, 4) for e in entropy_sampled])},
            borderColor: 'rgba(99, 179, 237, 0.3)',
            backgroundColor: 'rgba(99, 179, 237, 0.05)',
            fill: true,
            pointRadius: 0,
            borderWidth: 1,
        }}, {{
            label: 'Moving Average (50)',
            data: {json.dumps([round(w, 4) for w in windows_sampled])},
            borderColor: '#b794f6',
            borderWidth: 2,
            pointRadius: 0,
        }}]
    }},
    options: {{
        responsive: true,
        scales: {{
            x: {{ display: false }},
            y: {{
                grid: {{ color: 'rgba(255,255,255,0.05)' }},
                ticks: {{ color: '#718096' }}
            }}
        }},
        plugins: {{ legend: {{ labels: {{ color: '#a0aec0' }} }} }}
    }}
}});

// Action chart
const actionCtx = document.getElementById('actionChart').getContext('2d');
const actionData = {action_data};
new Chart(actionCtx, {{
    type: 'doughnut',
    data: {{
        labels: Object.keys(actionData),
        datasets: [{{
            data: Object.values(actionData),
            backgroundColor: ['#63b3ed', '#b794f6', '#f6ad55', '#68d391', '#fc8181', '#4fd1c5', '#a0aec0'],
            borderWidth: 0,
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#a0aec0', padding: 12 }} }} }}
    }}
}});

// Series chart
const seriesCtx = document.getElementById('seriesChart').getContext('2d');
const seriesData = {series_data};
const seriesColors = {json.dumps(series_colors)};
new Chart(seriesCtx, {{
    type: 'doughnut',
    data: {{
        labels: Object.keys(seriesData),
        datasets: [{{
            data: Object.values(seriesData),
            backgroundColor: Object.keys(seriesData).map(s => seriesColors[s] || '#7f8c8d'),
            borderWidth: 0,
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#a0aec0', padding: 12 }} }} }}
    }}
}});
</script>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="FEP v2 Dashboard")
    parser.add_argument(
        "--log", type=str, default=None,
        help="Path to JSONL log (default: latest in logs/)",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output HTML path (default: logs/fep_dashboard.html)",
    )
    args = parser.parse_args()
    
    # Find latest log
    if args.log:
        log_path = args.log
    else:
        log_dir = Path.home() / "oikos/hegemonikon/logs"
        logs = sorted(log_dir.glob("e2e_endurance_*.jsonl"))
        if not logs:
            print("[!] No endurance logs found")
            sys.exit(1)
        log_path = str(logs[-1])
    
    print(f"[*] Loading: {log_path}")
    entries = load_log(log_path)
    print(f"[*] Loaded {len(entries)} entries")
    
    analysis = analyze(entries)
    
    print(f"[*] Analysis:")
    print(f"    Valid cycles: {analysis['valid_entries']}")
    print(f"    Entropy: {analysis['entropy_start']:.3f} → {analysis['entropy_end']:.3f}")
    print(f"    Actions: {analysis['action_counts']}")
    print(f"    Series: {analysis['series_counts']}")
    print(f"    Phases: {len(analysis['phases'])}")
    
    html = generate_html(analysis, log_path)
    
    output_path = args.output or str(Path.home() / "oikos/hegemonikon/logs/fep_dashboard.html")
    with open(output_path, "w") as f:
        f.write(html)
    
    print(f"\n[✓] Dashboard: {output_path}")
    print(f"    Open in browser to view")


if __name__ == "__main__":
    main()
