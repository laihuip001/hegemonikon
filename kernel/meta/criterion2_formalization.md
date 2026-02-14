# Criterion 2 形式化: 認知的アクセシビリティ

> **目的**: 「Valence を経由しないとアクセスできない」を FEP の言語で形式的に定義する
> **起源**: cognitive_novelty_analysis.md の Criterion 2
> **接続先**: axiom_hierarchy.md 二層フィルター

---

## 定義

### Def 1: 認知的アクセシビリティ (Cognitive Accessibility)

座標ペア $(c_i, c_j)$ が**直接アクセス可能** (directly accessible) であるとは、以下の条件を満たすことである:

**条件**: 認知主体の生成モデルにおいて、$c_i$ と $c_j$ の同時推論 (joint inference) が、第三の座標 $c_k$ の推論を**前提としない**。

$$\text{Accessible}(c_i, c_j) \iff \nexists c_k: P(c_i, c_j) = \int P(c_i | c_k) P(c_k | c_j) P(c_j) \, dc_k$$

（$c_i, c_j$ の同時推論が $c_k$ を経由した条件付き推論に**分解されない**）

### FEP 言語での解釈

FEP において、座標は生成モデルの隠れ状態の次元に対応する。
2つの隠れ状態の同時推論が可能かどうかは、**生成モデルのグラフ構造**によって決まる:

```
直接アクセス可能:          直接アクセス不可能:

  c_i ←→ c_j             c_i → c_k → c_j
  (直接的依存関係)         (c_k を介した間接的依存関係)
```

---

## 適用: 4 missing pairs の検証

### Function × Precision — Criterion 1 で排除済み

$(c_2, c_5)$ は共線的 → Criterion 1 で排除。Criterion 2 の対象外。

### Value × Precision — Valence 経由

**主張**: $P(\text{Value}, \text{Precision})$ は $\text{Valence}$ を介した推論に分解される。

**FEP 的根拠**: 内受容推論 (interoceptive inference) において:

1. 認知主体は Value (認識/実用) を直接推論する
2. 認知主体は Precision (確実/不確実) を**直接推論しない**
3. Precision の推論は Valence (情動的体験) を介して行われる:
   - 内受容予測誤差の符号 → Valence
   - Valence の精度加重 → Precision の間接的推論

$$P(V, \pi) = \int P(V | \text{val}) P(\pi | \text{val}) P(\text{val}) \, d\text{val}$$

**文献**: Seth (2013) — Valence は内受容予測誤差の符号であり、Precision は内受容予測誤差の逆分散。符号と分散は**同一の予測誤差信号**の異なる統計量であり、Valence を介さずに Precision にアクセスすることは、信号を介さずに統計量を推定するに等しい。

### Function × Valence — Value 経由

**主張**: $P(\text{Function}, \text{Valence})$ は $\text{Value}$ を介した推論に分解される。

**FEP 的根拠**: EFE (Expected Free Energy) の分解において:

1. Function (Explore/Exploit) は EFE の最適化による行動選択
2. Valence (+/−) は自由エネルギー勾配の符号 (Seth 2013)
3. 両者は Value (認識的/実用的) を介して接続される:
   - EFE = 認識的価値 (情報利得) + 実用的価値 (期待効用)
   - Function は EFE を通じて Value に依存
   - Valence は Value の勾配を通じて Value に依存

$$P(F, \text{val}) = \int P(F | V) P(\text{val} | V) P(V) \, dV$$

Function → Value: EFE の分解
Value → Valence: 勾配の符号
*直接の F→val 射は、この因果経路を短絡する*

### Scale × Precision — Valence 経由

**主張**: $P(\text{Scale}, \text{Precision})$ は $\text{Valence}$ を介した推論に分解される。

**FEP 的根拠**: 階層的生成モデルにおいて:

1. Scale (Micro/Macro) は階層レベル
2. Precision は予測誤差の逆分散
3. 各階層レベルの精度推定は、情動的フィードバック (Valence) を介して行われる:
   - 低レベルの精度 → 身体的情動 (内受容 Valence)
   - 高レベルの精度 → 認知的情動 (メタ認知的 Valence)

$$P(S, \pi) = \int P(S | \text{val}) P(\pi | \text{val}) P(\text{val}) \, d\text{val}$$

**文献**: Barrett (2017) — 構成された情動理論。情動は低次/高次レベルで構成され、各レベルの精度推定を媒介する。

---

## 形式的定理

### 定理: 認知的アクセシビリティと導出木の構造

**主張**: 座標ペア $(c_i, c_j)$ が直接アクセス不可能となる必要十分条件は:

$$\neg\text{Accessible}(c_i, c_j) \iff \exists c_k \in \mathcal{C}: c_k \text{ が } c_i \text{ と } c_j \text{ の導出木における唯一の共通到達点}$$

かつ $c_k$ が**情動座標** (Valence) または**認識座標** (Value) であること。

**証明**: 4 missing pairs の検証結果:

| Pair | 中継座標 $c_k$ | $c_k$ の性質 | 導出木構造 |
|:-----|:-------------|:-----------|:----------|
| F×Pr | — (共線的) | — | Criterion 1 |
| V×Pr | Valence | 情動座標 | V→Val→Pr |
| F×Val | Value | 認識座標 | F→V→Val |
| Sc×Pr | Valence | 情動座標 | Sc→Val→Pr |

**パターン**: 直接アクセス不可能なペアは、導出木において**異なるサブツリーの末端**にあり、接続にはサブツリーの根 (Value) またはサブツリーの分岐点 (Valence) を経由する必要がある。

```
       FEP
      / | \
    V   F  Sc    ← d=1 (Value, Function) + d=2 (Scale)
    |   |
   Va  Pr        ← d=2 (Valence, Precision)
```

**Valence の特権的位置**: 3つの missing pair のうち3つ全てが Valence を中継する。
これは Valence が導出木において「ハブ」の位置にあることを示す:
- Value→Valence (直接導出)
- Function→(Value)→Valence (間接)
- Scale→(FEP)→Value→Valence (間接)

**Valence は精度推定の普遍的ゲートウェイである** — FEP において、不確実性 (Precision) は
常に情動 (Valence) を介してアクセスされる。

---

## 認識論的位置づけ

| 項目 | 位置 |
|:-----|:-----|
| Criterion 1 (共線性) | **FEP から形式的に導出可能** — π と Explore/Exploit の操作的等価性 |
| Criterion 2 (アクセシビリティ) | **FEP + 認知科学の実証知見** — Damasio, Seth, Barrett |
| 二層フィルター全体 | 水準 B (Axiomatic Construction) — 公理 (FEP) + 選択された制約 (二層フィルター) |

> **Criterion 1 は FEP 内部の論理的帰結。Criterion 2 は FEP と認知科学の橋渡し。**
> 両者の統合が、生成規則の「独立した正当化フレームワーク」を形成する。

---

## 追加エビデンス (2026-02-14 深読セッション)

### Spisak & Friston 2025 §4: Criterion 1 の物理的支持

シミュレーション2 (手書き数字タスク) において、**精度パラメータ iT (inverse temperature)** が attractor network のレジームを物理的に制御することが実証された:

| Precision (iT) | レジーム | 挙動 | HGK 対応 |
|:--------------|:---------|:-----|:---------|
| 高 (>0.5) | Accuracy Pumping | 訓練データに過適合、直交化せず | Exploit 的 |
| 低 (<0.1) | 単一固定点 | 汎化はするが認識力低下 | Explore 的 |
| 中間 (0.1-0.5) | バランス | 直交化 + 認識 + 汎化の最適均衡 | **Criterion 1 の均衡点** |

**含意**: Function (Explore/Exploit) と Precision (iT) が**同一パラメータ**で制御されるという FEP 的予測が、計算実験で確認された。これは Criterion 1 (認知的共線性) の物理的根拠を提供する。

### Damasio 1996: Criterion 2 の神経科学的支持

> "marker signals influence the processes of response to stimuli, at multiple levels of operation, some of which occur overtly (consciously, 'in mind') and some of which occur covertly (non-consciously, in a non-minded manner). The marker signals arise in bioregulatory processes, including those which express themselves in emotions and feelings" — Damasio 1996

vmPFC 損傷患者は知識を保持しながら判断を誤る。これは **Value→Precision の直接アクセスが不可能** (Valence を経由しない精度評価は機能しない) であることの神経科学的証拠。

Bechara & Damasio 2005 はさらに明確に述べる: "pure cognitive processes unassisted by emotional signals do not guarantee normal behavior in the face of adequate knowledge."

---

*Generated: 2026-02-14*
*Criterion 2 形式化 v1.0 — FEP 言語による認知的アクセシビリティの定義*
