# Hegemonikón 索引 (Πίναξ)

> **Version**: 2.3.0
> **Updated**: 2026-01-29

---

## 🏛️ 定理体系 (6系列 × 4定理 = 24)

### O - Ousia (本質)

| ID | 名 | ギリシャ語 | 役割 | ワークフロー |
|:---|:---|:-----------|:-----|:-------------|
| O1 | Noēsis | Νόησις | 純粋思考・直観 | /noe |
| O2 | Boulēsis | Βούλησις | 意志・目的 | /bou |
| O3 | Zētēsis | Ζήτησις | 探求・問い | /zet |
| O4 | Energeia | Ἐνέργεια | 行為・実現 | /ene |

---

### S - Schema (戦略)

| ID | 名 | ギリシャ語 | 役割 | ワークフロー | 統合セクション |
|:---|:---|:-----------|:-----|:-------------|:---------------|
| S1 | Metron | Μέτρον | スケール配置 | /met | - |
| S2 | Mekhanē | Μηχανή | 方法配置 | /mek | - |
| S3 | Stathmos | Σταθμός | 基準配置 | /sta | **Metrika, Chreos** |
| S4 | Praxis | Πρᾶξις | 実践配置 | /pra | **Graphē** |

---

### H - Hormē (衝動)

| ID | 名 | ギリシャ語 | 役割 | ワークフロー | 統合セクション |
|:---|:---|:-----------|:-----|:-------------|:---------------|
| H1 | Propatheia | Προπάθεια | 前感情 | /pro | - |
| H2 | Pistis | Πίστις | 確信度 | /pis | - |
| H3 | Orexis | Ὄρεξις | 欲求 | /ore | - |
| H4 | Doxa | Δόξα | 信念・記録 | /dox | **Palimpsest** |

---

### P - Perigraphē (環境)

| ID | 名 | ギリシャ語 | 役割 | ワークフロー | 統合セクション |
|:---|:---|:-----------|:-----|:-------------|:---------------|
| P1 | Khōra | Χώρα | 場・スコープ | /kho | **Horos** |
| P2 | Hodos | Ὁδός | 道・経路 | /hod | - |
| P3 | Trokhia | Τροχιά | 軌道・サイクル | /tro | - |
| P4 | Tekhnē | Τέχνη | 技法 | /tek | - |

---

### K - Kairos (文脈)

| ID | 名 | ギリシャ語 | 役割 | ワークフロー | 統合セクション |
|:---|:---|:-----------|:-----|:-------------|:---------------|
| K1 | Eukairia | Εὐκαιρία | 好機 | /euk | - |
| K2 | Chronos | Χρόνος | 時間 | /chr | **Kymation** |
| K3 | Telos | Τέλος | 目的 | /tel | - |
| K4 | Sophia | Σοφία | 知恵・調査 | /sop | - |

---

### A - Akribeia (精度)

| ID | 名 | ギリシャ語 | 役割 | ワークフロー | 統合セクション |
|:---|:---|:-----------|:-----|:-------------|:---------------|
| A1 | Pathos | Πάθος | メタ感情 | /pat | - |
| A2 | Krisis | Κρίσις | 判定・批評 | /dia | **Aspis** |
| A3 | Gnōmē | Γνώμη | 格言・原則 | /gno | - |
| A4 | Epistēmē | Ἐπιστήμη | 知識昇格 | /epi | - |

---

## 📜 Naturalized 概念マッピング

### Horos (P1 Khōra) — 境界の守護

| 新名 | 旧名 (Legacy) | 意味 |
|:-----|:--------------|:-----|
| Temenos | DMZ Protocol | 聖域 — 侵入不可の保護領域 |
| Taxis | Topology Lock | 秩序 — 構造の不変性 |
| Autarkeia | Dependency Quarantine | 自足 — 外部依存の最小化 |
| Sphragis | Docker First | 封印 — 環境の再現性 |

### Metrika (S3 Stathmos) — 品質門

| 新名 | 旧名 (Legacy) | 閾値 |
|:-----|:--------------|:-----|
| Dokimē | TDD Protocol | Red→Green→Refactor |
| Syntomia | Complexity Budget | ネスト≤3, 関数≤30行, 引数≤4 |
| Prosbasimotēs | a11y Mandate | WCAG 2.1 AA |
| Atomos | Atomic Design | 単一責任, ≤120行 |
| Katharos | Dead Code Reaper | 死コード0 |

### Chreos (S3 Stathmos) — 技術的負債

| 新名 | 旧名 (Legacy) | 形式 |
|:-----|:--------------|:-----|
| Chreos | TODO Expiration | `TODO({Owner}, {YYYY-MM-DD}): {Description}` |

### Aspis (A2 Krisis) — 敵対的防護

| 新名 | 旧名 (Legacy) | 発動条件 |
|:-----|:--------------|:---------|
| Alloiōsis | Mutation Testing | テスト完成後 |
| Ephodos | Red Teaming | DB/認証/入力処理時 |
| Anarkhia | Chaos Monkey | 外部通信時 |
| Synthēkē | Mock First | API実装時 |
| Takhytēs | Performance Budget | ループ/DB処理時 |

### Kymation (K2 Chronos) — 時間波及

| 新名 | 旧名 (Legacy) | 機能 |
|:-----|:--------------|:-----|
| Rhipē | Ripple Effect | 変更の影響範囲予測 |
| Palindromia | Rollback Strategy | 逆操作保証 |

### Graphē (S4 Praxis) — 構造化記録

| 新名 | 旧名 (Legacy) | 対象 |
|:-----|:--------------|:-----|
| Domedomē | Structured Logging | ランタイムログ |
| Epos | Narrative Commit | コミットメッセージ |
| Synchronismos | Auto-Documentation | Docstring+README同期 |

### Palimpsest (H4 Doxa) — コード考古学

| 新名 | 旧名 (Legacy) | 機能 |
|:-----|:--------------|:-----|
| Oulē | Chesterton's Fence | 傷跡検出 (HACK/FIXME) |

---

## 🔧 ワークフロー一覧

### コアワークフロー

| コマンド | 定理 | 用途 |
|:---------|:-----|:-----|
| /boot | - | セッション開始 |
| /bye | - | セッション終了・引き継ぎ |
| /ax | ALL | 全定理群順次実行 |

### O-series (本質)

| コマンド | 定理 | 用途 |
|:---------|:-----|:-----|
| /o | O-Hub | O1-O4へのハブ |
| /noe | O1 | 深層思考 |
| /bou | O2 | 意志・目的定義 |
| /zet | O3 | 問い発見 |
| /ene | O4 | 行為実現 |
| /why | O3派生 | Five Whys |
| /poc | O3派生 | Spike/PoC |
| /pre | O2派生 | Premortem |
| /flag | O4派生 | Feature Flags |

### S-series (戦略)

| コマンド | 定理 | 用途 |
|:---------|:-----|:-----|
| /s | S-Hub | S1-S4へのハブ |
| /met | S1 | スケール決定 |
| /mek | S2 | 方法配置 |
| /sta | S3 | 基準設定 |
| /pra | S4 | 実践選択 |

### H-series (衝動)

| コマンド | 定理 | 用途 |
|:---------|:-----|:-----|
| /h | H-Hub | H1-H4へのハブ |
| /pro | H1 | 前感情評価 |
| /pis | H2 | 確信度評価 |
| /ore | H3 | 欲求評価 |
| /dox | H4 | 信念記録 |

### P-series (環境)

| コマンド | 定理 | 用途 |
|:---------|:-----|:-----|
| /p | P-Hub | P1-P4へのハブ |
| /kho | P1 | スコープ定義 |
| /hod | P2 | 経路定義 |
| /tro | P3 | サイクル定義 |
| /tek | P4 | 技法選択 |

### K-series (文脈)

| コマンド | 定理 | 用途 |
|:---------|:-----|:-----|
| /k | K-Hub | K1-K4へのハブ |
| /euk | K1 | 好機判定 |
| /chr | K2 | 時間評価 |
| /tel | K3 | 目的確認 |
| /sop | K4 | Perplexity調査 |

### A-series (精度)

| コマンド | 定理 | 用途 |
|:---------|:-----|:-----|
| /a | A-Hub | A1-A4へのハブ |
| /pat | A1 | メタ感情 |
| /dia | A2 | 批評・監査 |
| /gno | A3 | 原則抽出 |
| /epi | A4 | 知識昇格 |

### X-series (関係)

| コマンド | 用途 |
|:---------|:-----|
| /x | 定理間従属関係の可視化 |

### Meta

| コマンド | 用途 |
|:---------|:-----|
| /eat | 外部概念の消化 |
| /fit | 消化品質検証 |
| /syn | 偉人評議会召喚 |
| /pan | 盲点発見メタ認知 |
| /u | Claude主観引き出し |
| /vet | Cross-Model検証 |

---

## 🔤 ギリシャ語用語辞典

| 用語 | 読み | 意味 | 使用箇所 |
|:-----|:-----|:-----|:---------|
| Akribeia | アクリベイア | 精度・正確性 | A-series |
| Alloiōsis | アロイオーシス | 変異 | Aspis |
| Anarkhia | アナルキア | 混沌 | Aspis |
| Atomos | アトモス | 原子 | Metrika |
| Autarkeia | アウタルケイア | 自足 | Horos |
| Boulēsis | ブーレーシス | 意志 | O2 |
| Chreos | クレオス | 負債 | S3 |
| Chronos | クロノス | 時間 | K2 |
| Diorthōsis | ディオルトーシス | 自動修正 | /boot |
| Dokimē | ドキメー | 試験 | Metrika |
| Doxa | ドクサ | 信念 | H4 |
| Domedomē | ドメドメー | 構造化 | Graphē |
| Energeia | エネルゲイア | 活動・実現 | O4 |
| Ephodos | エフォドス | 攻撃 | Aspis |
| Epistēmē | エピステーメー | 知識 | A4 |
| Epos | エポス | 叙事詩 | Graphē |
| Eukairia | エウカイリア | 好機 | K1 |
| Gnōmē | グノーメー | 格言 | A3 |
| Graphē | グラフェー | 書記 | S4 |
| Hexis | ヘクシス | 状態・様態 | /boot |
| Hodos | ホドス | 道 | P2 |
| Hormē | ホルメー | 衝動 | H-series |
| Horos | ホロス | 境界 | P1 |
| Kairos | カイロス | 適時 | K-series |
| Katharos | カタロス | 清浄 | Metrika |
| Khōra | コーラ | 場・空間 | P1 |
| Krisis | クリシス | 判定 | A2 |
| Kymation | キューマティオン | 波 | K2 |
| Mekhanē | メーカネー | 装置・方法 | S2 |
| Metrika | メトリカ | 測定術 | S3 |
| Metron | メトロン | 尺度 | S1 |
| Noēsis | ノエーシス | 思考・直観 | O1 |
| Orexis | オレクシス | 欲求 | H3 |
| Oulē | ウーレー | 傷跡 | Palimpsest |
| Ousia | ウーシア | 本質 | O-series |
| Palimpsest | パリンプセスト | 羊皮紙 | H4 |
| Palindromia | パリンドロミア | 回帰 | Kymation |
| Pathos | パトス | 情念 | A1 |
| Perigraphē | ペリグラフェー | 輪郭 | P-series |
| Pistis | ピスティス | 確信 | H2 |
| Poiēsis | ポイエーシス | 制作 | Hexis派生 |
| Praxis | プラクシス | 実践 | S4 |
| Propatheia | プロパテイア | 前感情 | H1 |
| Prosbasimotēs | プロスバシモテース | 到達可能性 | Metrika |
| Rhipē | リペー | 波及 | Kymation |
| Schema | スケーマ | 図式・戦略 | S-series |
| Sophia | ソフィア | 知恵 | K4 |
| Sphragis | スフラギス | 封印 | Horos |
| Stathmos | スタトモス | 基準点 | S3 |
| Synedrion | シュネドリオン | 評議会 | /syn |
| Synchronismos | シンクロニスモス | 同期 | Graphē |
| Synthēkē | シュンテーケー | 契約 | Aspis |
| Syntomia | シュントミア | 簡潔 | Metrika |
| Takhytēs | タキュテース | 速度 | Aspis |
| Taxis | タクシス | 秩序 | Horos |
| Tekhnē | テクネー | 技術 | P4 |
| Telos | テロス | 目的 | K3 |
| Temenos | テメノス | 聖域 | Horos |
| Theōria | テオーリア | 観想 | Hexis派生 |
| Trokhia | トロキア | 軌道 | P3 |
| Zētēsis | ゼーテーシス | 探求 | O3 |

---

*Πίναξ: 古代ギリシャにおける「板・索引・目録」*
