# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [3.2.0] - 2026-01-29

### Added

- **LLM Hybrid 派生選択** (v3.1)
  - Gemini Flash free tier フォールバック
  - 低信頼度 (<55%) 時に自動 LLM 選択
  - `_select_with_llm()`, `_hybrid_select()` 関数

- **派生選択学習基盤** (v3.2)
  - 選択ログ自動記録 (`derivative_selections.yaml`)
  - `_log_selection()` 関数
  - /bye + /boot 連携準備

### Changed

- `LLM_FALLBACK_THRESHOLD`: 0.50 → 0.55
- `select_derivative()`: `use_llm_fallback` パラメータ追加

### Fixed

- `_hybrid_select()`: 存在しない属性参照を修正

## [2.1.0] - 2026-01-27

### Changed

- **Complete restructure to 60-element system**
  - 7 Axioms (L0: FEP, L1: Flow/Value, L1.5: Scale/Function, L1.75: Valence/Precision)
  - 24 Theorems (6 series × 4)
  - 36 Relations (X-series)

### Renamed

- T-series → **S-series (Schema)**
- R-series → **H-series (Hormē)**
- Old P-series → **P-series (Perigraphē)**
- R1: Hormē → **H1: Propatheia**

### Added

- `kernel/naming_conventions.md` — Classical Greek naming rationale
- `kernel/schema.md`, `kernel/horme.md`, `kernel/perigraphe.md` — New theorem docs
- "Hyperengineering as a Badge of Honor" design philosophy

### Archived

- Old update manuals moved to `docs/archive/`
- Old AI_ARCHITECTURE.md moved to `docs/archive/`

## [0.1.0] - 2026-01-19

### Added

- Repository initialization
- README, CONTRIBUTING, LICENSE
- .gitignore for large files
