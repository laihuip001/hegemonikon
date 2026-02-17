# WF 分類マトリックス (Python Analogy)

> **Date**: 2026-02-17 | **CCL**: `/s+`
> **Total**: 58 ワークフロー (24 Core + 6 Hub + 11 Utility + 17 CCL Macro)

---

## 1. Core WF (24) — `builtins`

定理群に直接対応するプリミティブ。Python の `print`, `len`, `type` に相当。

### O-series (Ousia: 本質)

| WF | 定理 | Python 対応 | 説明 |
|:---|:-----|:------------|:-----|
| `/noe` | O1 Noēsis | `type()`, `isinstance()` | 本質認識 (メタ認知を含む) |
| `/bou` | O2 Boulēsis | `input()` (意図取得) | 意志・目的 |
| `/zet` | O3 Zētēsis | `dir()`, `help()` | 探求・問い |
| `/ene` | O4 Energeia | `exec()`, `eval()` | 実行・行為 |

### S-series (Schema: 様態)

| WF | 定理 | Python 対応 | 説明 |
|:---|:-----|:------------|:-----|
| `/met` | S1 Metron | `len()`, `sys.getsizeof()` | 尺度・スケール |
| `/mek` | S2 Mekhanē | `def`, `lambda` | 方法・関数定義 |
| `/sta` | S3 Stathmos | `assert`, `unittest` | 基準・テスト |
| `/pra` | S4 Praxis | `functools.partial()` | 実践・適用 |

### H-series (Hormē: 傾向)

| WF | 定理 | Python 対応 | 説明 |
|:---|:-----|:------------|:-----|
| `/pro` | H1 Propatheia | `logging.debug()` | 前反応・直感 |
| `/pis` | H2 Pistis | `confidence` (仮想) | 確信度 |
| `/ore` | H3 Orexis | `preferences` | 欲求・傾向 |
| `/dox` | H4 Doxa | `pickle`, `shelve` | 信念・永続化 |

### P-series (Perigraphē: 条件)

| WF | 定理 | Python 対応 | 説明 |
|:---|:-----|:------------|:-----|
| `/kho` | P1 Khōra | `os.getcwd()`, `Path` | 場・空間 |
| `/hod` | P2 Hodos | `pathlib.Path` | 道・経路 |
| `/tro` | P3 Trokhia | `itertools.cycle()` | 軌道・サイクル |
| `/tek` | P4 Tekhnē | `importlib` | 技法・モジュール |

### K-series (Kairos: 文脈)

| WF | 定理 | Python 対応 | 説明 |
|:---|:-----|:------------|:-----|
| `/euk` | K1 Eukairia | `time.time()` | 好機・タイミング |
| `/chr` | K2 Chronos | `datetime` | 時間 |
| `/tel` | K3 Telos | `@property` (目的属性) | 目的 |
| `/sop` | K4 Sophia | `requests`, `API` | 知恵・外部調査依頼 |

### A-series (Akribeia: 精密)

| WF | 定理 | Python 対応 | 説明 |
|:---|:-----|:------------|:-----|
| `/pat` | A1 Pathos | `logging.info()` | 情念・感情 |
| `/dia` | A2 Krisis | `assert`, `validate()` | 判定・検証 |
| `/gno` | A3 Gnōmē | `docstring` | 格言・原則 |
| `/epi` | A4 Epistēmē | `typing`, `annotations` | 知識・型 |

---

## 2. Hub WF (6) — `abc.ABC` (抽象基底クラス)

シリーズの入口。内部 4 定理を振動として巡回。

| WF | シリーズ | Python 対応 | 説明 |
|:---|:---------|:------------|:-----|
| `/o` | O-series | `abc.ABC` | Ousia 振動 |
| `/s` | S-series | `abc.ABC` | Schema 振動 |
| `/h` | H-series | `abc.ABC` | Hormē 振動 |
| `/p` | P-series | `abc.ABC` | Perigraphē 振動 |
| `/k` | K-series | `abc.ABC` | Kairos 振動 |
| `/a` | A-series | `abc.ABC` | Akribeia 振動 |

---

## 3. Utility WF (11) — `stdlib` 拡張

ライフサイクル・対話・統合・品質に関わる非定理系 WF。

| WF | Python 対応 | 分類 | 説明 |
|:---|:------------|:-----|:-----|
| `/boot` | `__init__` + `atexit` | ライフサイクル | セッション開始 |
| `/bye` | `__del__` + `pickle.dump()` | ライフサイクル | セッション終了・永続化 |
| `/rom` | `shelve.sync()` | ライフサイクル | RAM→ROM 中間セーブ |
| `/u` | `__call__` + `input()` | インタラクション | AI の主観・対話 |
| `/m` | `signal.SIGUSR1` | インタラクション | 本気モード発動 |
| `/ax` | `unittest.TestSuite` | オーケストレーション | 全層統合 (大循環) |
| `/x` | `import` 解決 | オーケストレーション | X-series 関係ナビゲーション |
| `/eat` | `with open()` + `json.load()` | 複合 | 外部消化 |
| `/vet` | `subprocess.check_call()` | 品質 | Cross-Model Verification |
| `/basanos` | `multiprocessing.Pool` | 品質 | 偉人評議会 (多角的レビュー) |
| `/dendron` | `ast.parse()` + `inspect` | 品質 | 存在証明チェック |

---

## 4. CCL Macro WF (17) — `Makefile` ターゲット

CCL 式を定義済みパイプラインとして再利用するマクロ。

| WF | 日本語名 | CCL 式 | 用途 |
|:---|:---------|:-------|:-----|
| `@build` | 組む | `/bou-_/s+_/ene+_V:{/dia-}_I:[✓]{/dox-}` | 段階的構築 |
| `@chew` | 噛む | `/s-_/pro_F:[×3]{/eat+~(...)}_...` | 深い消化 |
| `@desktop` | 操作 | AT-SPI → Bytebot VLM | デスクトップ操作 |
| `@dig` | 掘る | `/pro_/s+~(/p*/a)_/ana_/dia*/o+_...` | 深掘り調査 |
| `@fix` | 直す | `/kho_/tel_C:{/dia+_/ene+}_...` | バグ修正 |
| `@helm` | 舵 | `/pro_/kho_/bou+*%/zet+\|>/u++_...` | 方向決定 |
| `@kyc` | 回す | `/pro_C:{/sop_/noe_/ene_/dia-}_...` | KYC サイクル |
| `@learn` | 刻む | `/pro_/dox+_F:[×2]{/u+~(...)}_...` | 学習定着 |
| `@nous` | 問う | `/pro_/s-_R:{F:[×2]{/u+*^/u^}}_...` | 深い問い |
| `@plan` | 段取る | `/bou+_/chr_/s+~(/p*/k)_V:{/dia}_...` | 計画策定 |
| `@proof` | 裁く | `V:{/noe~/dia}_I:[✓]{/ene{...}}_...` | 品質裁定 |
| `@read` | 読む | `/s-_/pro_F:[×3]{/m.read~(...)}_...` | 熟読 |
| `@ready` | 見渡す | `/bou-_/pro_/kho_/chr_/euk_...` | 準備確認 |
| `@rpr` | RPR | React→Plan→Reflect | 反復収束 |
| `@syn` | 監る | `/kho_/s-_/pro_/dia+{synteleia}_...` | Synteleia 監査 |
| `@tak` | 捌く | `/s1_F:[×3]{/sta~/chr}_...` | タスク整理 |
| `@vet` | 確かめる | `/kho{git_diff}_C:{V:{/dia+}_...}` | 変更検証 |

---

## サマリー

| カテゴリ | 数 | Python 対応 |
|:---------|---:|:------------|
| Core WF (定理) | 24 | `builtins` |
| Hub WF | 6 | `abc.ABC` |
| Utility WF | 11 | `stdlib` |
| CCL Macro WF | 17 | `Makefile` |
| **合計** | **58** | |

---

*Updated 2026-02-17 | WF Classification Matrix v2*
