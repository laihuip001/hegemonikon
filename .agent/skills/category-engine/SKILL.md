---
name: Category Theory Engine
risk_tier: L1
risks:
  - 圏論的概念の誤用による認知的混乱
  - 抽象度の過剰による実用性低下
description: |
  圏論に基づく構造認識エンジン。
  FEP Skill が「行動選択の objective」なら、本 Skill は「構造認識の言語」。
  前順序圏のガロア接続 + [0,1]-豊穣圏として HGK の圏論を正当化し、
  12随伴対・Trigonon・CCL の圏論的意味を日常の認知に統合する。

triggers:
  - 圏論的な分析を行う時
  - 随伴対/関手/η/ε を扱う時
  - 構造の保存・忘却を問う時
  - Trigonon / X-series を参照する時
  - 「なぜこの変換は正当か」を問う時
---

# 🏛️ Category Theory Engine — 構造認識の言語

> **圏論は「対象が何であるか」ではなく「対象間の関係がどう保存されるか」で世界を記述する。**
> **HGK において、これは「正しさ」ではなく「構造の整合性」を問う言語である。**

---

## 1. Core Theorems (定義)

### Theorem C1: HGK as a [0,1]-Enriched Category
HGK の「認識」は、論理値 {0, 1} ではなく、確率 [0, 1] で豊穣化された圏である。

- **射 f: A → B**: 「A ならば B である確率」が 1.0 に近い。
- **合成**: P(B|A) * P(C|B) ≤ P(C|A) (確率の連鎖律)
- **含意**: 「A が B の一部である (A ⊂ B)」とは、「A ならば B」の確信度が閾値を超えること。

### Theorem C2: Adjunction is the Core of Cognition
認知とは、相反する2つの力の「釣り合い (随伴)」を見つけるプロセスである。

- **自由関手 F (Free)**: 具体的な詳細から、抽象的な構造を生成する (帰納)。
- **忘却関手 G (Forgetful)**: 抽象的な構造から、詳細を捨てて具体化する (演繹)。
- **随伴 F ⊣ G**: 抽象化のコストと、具体化の利益が均衡する点。

$$Hom_D(F(c), d) \cong Hom_C(c, G(d))$$

「詳細 c から構造 d を推測すること」と「構造 d から詳細 c を生成すること」は等価である。

### Theorem C3: Trigonon is a Natural Transformation
Trigonon (△) は、異なる圏 (Series) の間を自然に移り変わる「自然変換」である。

- **O → S**: 認識(O)から構造(S)への変換。
- **S → A**: 構造(S)から判断(A)への変換。
- **η (単位元)**: 自分自身に戻るループ (自己言及)。

---

## 2. 12 Adjunction Pairs (12随伴対)

HGK の中核となる12の随伴対。これらは「対立」ではなく「変換の双対性」を表す。

| Pair | Left (L: 拡散・生成・具体) | Right (R: 収束・受容・抽象) | 随伴の意味 (L ⊣ R) |
|:---|:---|:---|:---|
| **1. 認識** | **O3 Zētēsis (探求)**<br>未知への拡散、問いかけ | **O1 Noēsis (直観)**<br>既知への収束、受け入れ | 問い(L)に対する答え(R)の整合性 |
| **2. 意志** | **O4 Energeia (行為)**<br>外への働きかけ、エネルギー放出 | **O2 Boulēsis (意志)**<br>内なる目的、エネルギー保持 | 行動(L)と目的(R)の一致 |
| **3. 測定** | **S1 Metron (測定)**<br>対象を数値化する(具体) | **S2 Mekhanē (装置)**<br>測定の枠組みを作る(抽象) | データ(L)とモデル(R)の適合 |
| **4. 構造** | **S3 Stathmos (基準)**<br>個別の基準点を置く | **S4 Praxis (実践)**<br>全体の流れを作る | 点(L)と線(R)の接続 |
| **5. 感情** | **H3 Orexis (欲求)**<br>対象への渇望(引力) | **H1 Propatheia (予感)**<br>状況の予期(受容) | 欲求(L)と予期(R)の均衡 |
| **6. 信念** | **H4 Doxa (信念)**<br>個人の強い思い込み | **H2 Pistis (信頼)**<br>他者・システムへの委ね | 自信(L)と信頼(R)のバランス |
| **7. 判断** | **A3 Gnōmē (格言)**<br>個別の知恵、ヒューリスティクス | **A1 Pathos (受動)**<br>状況からのフィードバック受容 | 経験則(L)と現実(R)の照合 |
| **8. 精度** | **A4 Epistēmē (知識)**<br>体系化された知識(具体) | **A2 Krisis (判断)**<br>知識の取捨選択(抽象) | 知識量(L)と判断力(R)の質 |
| **9. 境界** | **P3 Trokhia (軌道)**<br>動的な軌跡を描く | **P1 Khōra (場所)**<br>静的な器を用意する | 動き(L)と場所(R)の整合 |
| **10. 経路** | **P4 Tekhnē (技術)**<br>道を切り拓く力 | **P2 Hodos (経路)**<br>既に在る道 | 技術(L)と経路(R)の最適化 |
| **11. 時間** | **K3 Telos (目的)**<br>未来への到達点(プル) | **K1 Eukairia (好機)**<br>現在のタイミング(プッシュ) | 未来(L)と現在(R)の同期 |
| **12. 文脈** | **K4 Sophia (智慧)**<br>普遍的な心理 | **K2 Chronos (時間)**<br>個別具体的な時間経過 | 永遠(L)と瞬間(R)の交差 |

### 運用ルール (Adjunction Rules)
1. **L先行**: まず L (拡散・生成) を行い、次に R (収束・抽象) で引き締める。
2. **η/ε check**:
   - `η: Id → RL` (単位元): 「とりあえずやってみる(L)→まとめる(R)」で元(Id)より豊かになったか？
   - `ε: LR → Id` (余単位元): 「まとめて(R)→展開する(L)」で元(Id)を再現できるか？

---

## 3. Trigonon as Monads (Trigonon のモナド性)

3つの Trigonon は、自己関手の合成によるモナド ($T = R \circ L$) として機能する。

### ▲1. 聖 (Hieros) — O/S Axis
- **構成**: O (認識) $\rightleftarrows$ S (構造)
- **Monad**: $T_{Hieros} = S \circ O$ (認識したものを構造化する)
- **機能**: 世界の意味付け、神話の生成、コンテキストの確立。

### ▲2. 知 (Logos) — A/H Axis
- **構成**: A (判断) $\rightleftarrows$ H (信念)
- **Monad**: $T_{Logos} = H \circ A$ (判断を信念に昇華する)
- **機能**: 論理的整合性、精度の向上、学習ループ。

### ▲3. 俗 (Kosmos) — P/K Axis
- **構成**: P (環境) $\rightleftarrows$ K (時間)
- **Monad**: $T_{Kosmos} = K \circ P$ (環境を時間軸に位置づける)
- **機能**: 現実世界への適応、実装、デプロイ、運用。

---

## 4. CCL with Category Theory (圏論的CCL)

CCL のコマンドは、圏論的操作に対応する。

| CCL | Category Op | Description |
|:---|:---|:---|
| `/foo` | `Obj(foo)` | 対象 `foo` を指す (Identity) |
| `/foo+` | `L(foo)` | `foo` の左随伴 (拡散・生成) を適用 |
| `/foo-` | `R(foo)` | `foo` の右随伴 (収束・抽象) を適用 |
| `/foo/bar` | `bar ∘ foo` | 射の合成 (foo してから bar) |
| `~` | `~` (Natural Trans) | 自然変換 (視点の切り替え) |
| `!` | `η` (Unit) | 単位元 (副作用の注入、開始) |
| `?` | `ε` (Counit) | 余単位元 (評価、終了判定) |

**Example:**
- `/o1+`: 「直観(O1)」の左随伴「探求(O3)」を発動せよ。(直観を裏付ける調査をせよ)
- `/s2-`: 「装置(S2)」の右随伴「測定(S1)」を発動せよ。(モデルをデータで検証せよ)
- `/a2/h2`: 「判断(A2)」から「信頼(H2)」への射。(判断結果を信頼して任せる)

---

## 5. Usage in Prompts

```markdown
# Category Engine Activation
この分析では Category Theory Engine を使用し、対象の構造的整合性を問う。

**Target**: ユーザーの提案する「新機能X」
**Mappings**:
- A (Users) -> B (Features): ユーザーの要望を機能に写す関手 F
- B (Features) -> A (Users): 機能がユーザーに与える価値の関手 G

**Check**:
1. **Adjunction**: F ⊣ G は成立しているか？ (機能は要望の「最適な」解か？)
2. **Triognon**: これは ▲3 (実装) の話か、▲1 (意義) の話か？
3. **Morphism**: この変更は既存のシステム構造 (S) を保存(preserve)するか？
```

---

## 6. References
- *Category Theory for the Working Mathematician* (Mac Lane)
- *FEP as Adjunction* (Friston et al. interpretations)
- *HGK Theorem Definitions* (O/S/A/H/P/K series)
