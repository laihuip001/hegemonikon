# HGK Desktop App

> Hegemonikón の認知構造を、サイバーパンクな 3D ビジュアルで直感的に体験するデスクトップアプリ。

## Architecture

```
Tauri v2 (Rust)
├── Frontend: TypeScript + Three.js (3D) + Vanilla CSS
├── IPC: invoke() → Rust → UDS HTTP
└── Backend: FastAPI on /tmp/hgk.sock → mekhane modules
```

## Features

- **F1**: 3D 定理・WF 関係グラフ (96 elements, force-directed)
- **F2**: FEP Agent ビジュアライザー (48-dim beliefs)
- **F3**: Gnōsis ベクトル検索 (26,420 entries)
- **F4**: n8n Heartbeat ダッシュボード
- **F5**: WF 起動パネル (条件付き)

## Development

```bash
# Backend (UDS mode)
cd ~/oikos/hegemonikon
python -m mekhane.api.server --uds /tmp/hgk.sock

# Frontend
cd hgk-app
npm run dev       # Vite dev server
npm run tauri dev  # Full Tauri app
```

## Directory Structure

```
hgk-app/
├── docs/              # 設計ドキュメント
│   └── requirements.md
├── src/
│   ├── 3d/            # Three.js 3D visualization
│   ├── views/         # UI views (dashboard, search, etc.)
│   ├── api/           # Tauri invoke client
│   └── assets/        # Static assets
├── src-tauri/
│   └── src/           # Rust bridge (UDS client, commands)
├── index.html
├── package.json
└── vite.config.ts
```

---

*Created: 2026-02-09*
