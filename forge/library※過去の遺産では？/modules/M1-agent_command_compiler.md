---
id: M-1
trigger: manual
---

# M-1: Agent Command Compiler (コーディング仕様書コンパイル)

## Objective

ユーザー（Architect）の抽象的意図を、ワーカーAIが誤解なく実行可能な「完全な仕様書（Task Order）」にコンパイルする。

## Context Variables

- `{{target_environment}}`: Termux / AWS Lambda / Docker / Vercel
- `{{worker_agent}}`: Jules / Cursor / Cline / Copilot
- `{{constraints}}`: Pure Pythonのみ / 外部通信禁止 / 後方互換性維持

## Operational Protocols

- **Environment Audit:** 指示が対象環境で確実に動作するか検証
- **Reference First:** コードをHallucinationで生成せず、ファイル読み込みを先行
- **Non-Destructive:** 設定ファイル/DBの上書き禁止、TDD強制

## Output Template

```markdown
# 🛡️ {{worker_agent}} TASK ORDER: [Task Name]

## 1. Context & Objectives
- **Goal:** (一行定義)
- **Scope:** (変更対象)
- **Reference:** (まず読むべきファイル)

## 2. Constraints (Non-Negotiable)
- **Environment:** Must work on {{target_environment}}
- **Safety:** 破壊的変更禁止
- **Tech Stack:** {{constraints}}

## 3. Execution Steps
1. Analyze: Read reference files
2. Plan: 実装方針策定
3. Test Plan: 検証スクリプト作成
4. Implement: コーディング
5. Verify: テスト実行
```
