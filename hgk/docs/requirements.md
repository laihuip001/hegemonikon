# HGK Desktop App — 要件定義書 v1.0

> /bou~/zet Phase 0-2 成果 (2026-02-09)
> PROOF: [L3/設計] <- hgk-app/docs/

---

## ビジョン

> **Hegemonikón の認知構造を、サイバーパンクな 3D ビジュアルで直感的に体験する。**

## デザイン哲学

| 原則 | 意味 |
|:---|:---|
| **Jobs-Worthy** | ジョブスが唸る「作品」。妥協は冒涜 |
| **Cyberpunk Aesthetic** | ダーク基調、ネオングロー、粒子エフェクト |
| **UI First** | UIがゴミなら使われない。心地よさ最優先 |
| **Direct Manipulation** | 回せる、触れる、ズームできる |
| **Intuitive > Functional** | 説明不要で伝わる |

---

## 確定機能 (Must)

### F1: 3D 定理・WF 関係グラフ

96 要素 (7公理 + 24定理 + 72関係) を力学モデル 3D グラフで表示。
Series 別ネオンカラー。X-series 関係を方向付き矢印で接続。
OrbitControls で回転・ズーム・パン。ノードクリックで詳細。
FEP step 時にアクティブ定理が発光。

### F2: FEP Agent ビジュアライザー

48 次元 beliefs を radar chart / 3D 球面マッピング。
step ごとにスムーズアニメーション。epsilon を透明度/サイズで表現。

### F3: Gnōsis 検索

検索バー + 結果カード (abstract プレビュー)。26,420 entries。
source フィルタ、score 閾値。

### F4: n8n Heartbeat ダッシュボード

WF 稼働状況・最終実行時刻・エラー数。脈拍アニメーション。

### F5: WF 起動パネル (条件付き — IDE 連携)

方式 A: クリップボード注入（確実）
方式 B: VS Code Extension API（可能）
方式 C: Antigravity MCP（要調査）

---

## 技術スタック

| 層 | 技術 |
|:---|:---|
| Desktop | Tauri v2 (Rust) |
| 3D | Three.js + OrbitControls + WebGL Shaders |
| UI | TypeScript + Vanilla CSS |
| Backend | FastAPI on UDS (`/tmp/hgk.sock`) |
| IPC | Tauri invoke → Rust → UDS HTTP → FastAPI |

## カラーパレット

```
--bg-deep:     #0a0e17       (深い宇宙)
--neon-blue:   #00d4ff       (プライマリ)
--neon-purple: #a855f7       (セカンダリ)
--neon-green:  #10b981       (成功)
--neon-red:    #ef4444       (エラー)
--neon-amber:  #f59e0b       (警告)
```

---

*Requirements v1.0 — /bou~/zet (2026-02-09)*
