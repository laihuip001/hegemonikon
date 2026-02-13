# Ochēma Vision — 認知的主権への乗り物

> **Ochēma** (ὄχημα) — 乗り物、魂の乗物
> HGK の認知インフラを外界に運ぶ、統一的アクセスレイヤー

---

## 核心命題

**計算は Claude。界面は自分たちのもの。**

LLM 計算リソース (Layer 2) は Claude API に委ねる — これは電力会社との契約と同じ、商品化されたユーティリティ。

しかし **Layer 1 (インターフェース)** と **Layer 3 (ローカルアクセス)** は垂直統合し、認知的主権を確立する。

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: インターフェース (UI)                        │ ← 垂直統合対象
│   claude.ai → OIKOS App に置換                       │
├─────────────────────────────────────────────────────┤
│ Layer 2: LLM 計算リソース                            │ ← Claude API (固定)
│   Claude API — 商品化された外部依存                   │
├─────────────────────────────────────────────────────┤
│ Layer 3: ローカルアクセス (MCP ブリッジ)              │ ← 垂直統合対象
│   MCP Gateway → 直接統合に置換                       │
└─────────────────────────────────────────────────────┘
```

---

## 進化の系譜

Ochēma は1つのプロジェクトとして、界面を段階的に広げてきた:

| Phase | 形態 | 状態 | 到達範囲 |
|:------|:-----|:-----|:---------|
| 0 | `antigravity_client.py` | ✅ 完成 | Python から LLM |
| 1 | `cli.py` | ✅ 完成 | ターミナルから LLM |
| 2 | `ochema_mcp_server.py` | ✅ 完成 | IDE (Antigravity) から LLM |
| 3 | `hgk_gateway.py` | ✅ 完成 | モバイル/claude.ai から HGK + LLM |
| 4 | **OIKOS App** | 🔮 構想 | 専用 UI から HGK 全機能 |

### Phase 3 → 4 の転換点

Phase 3 (Gateway) は Phase 4 (App) の**プロトタイプ**として機能する:

- Gateway の利用パターンから「何が本当に使われるか」を発見
- 発見を App の UI 設計に直結させる
- HGK モジュール API が安定してから App を構築

---

## アーキテクチャ

### 現在 (Phase 3)

```
[claude.ai web/mobile]
        │
        │ MCP (Streamable HTTP over Tailscale)
        ▼
┌─[HGK Gateway]─────────────────────────────┐
│  OAuth 2.1 + Tailscale Funnel              │
│  14+ ツール (検索, CCL, Digestor, ...)      │
│                                            │
│  [AntigravityClient] → [LS API] → Claude   │
└────────────────────────────────────────────┘
```

### 将来 (Phase 4)

```
┌─[OIKOS App]────────────────────────────────┐
│  ネイティブ UI (React Native?)             │
│  直接 HGK モジュール呼出し               │
│  Claude API 直接通信                       │
│                                            │
│  Gateway 不要 — 0段の間接参照              │
└────────────────────────────────────────────┘
```

---

## なぜ「認知的主権」か

claude.ai を使う限り:

| 依存 | リスク |
|:-----|:------|
| Anthropic の UI 設計 | 彼らの優先順位で変わる |
| MCP 仕様変更 | 互換性が壊れうる |
| レート制限 | 制御不能 |
| 利用規約 | 一方的変更のリスク |

OIKOS App ならば:

| 自由 | 効果 |
|:-----|:-----|
| UI は自分で設計 | Creator の認知特性 (AuDHD) に最適化 |
| HGK 直接統合 | MCP の間接参照なし |
| API は商品 | プロバイダー切替え可能 |

---

## 制約と前提

1. **Claude API への依存は受け入れる**: LLM 計算は自前で持つべきではない (コスト・品質)
2. **Gateway を捨てない**: Phase 4 でも Gateway は外部アクセス用に残す可能性
3. **HGK モジュール安定が先**: API が変わるたびに App を直すのは非効率

---

## 参照

- [antigravity_client.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/ochema/antigravity_client.py) — Phase 0
- [cli.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/ochema/cli.py) — Phase 1
- [ochema_mcp_server.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/mcp/ochema_mcp_server.py) — Phase 2
- [hgk_gateway.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/mcp/hgk_gateway.py) — Phase 3

---

*Created: 2026-02-13 — 認知的主権への乗り物*
