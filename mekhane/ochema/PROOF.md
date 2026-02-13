# Ochēma — 存在証明

## PURPOSE

Antigravity Language Server の非公式 Python クライアント。
Ultra プランの LLM を HGK システムから利用する橋渡しモジュール。

## REASON

1. 公式 API が提供されていないため、LS の ConnectRPC エンドポイントに直接アクセスする必要がある
2. agq-check.sh で実証済みのプロセス検出ロジックを Python で再利用する
3. 前セッションで確立した 4-Step API フロー (curl 実証済み) を再現可能な形で固定化する

## EVIDENCE

- agq-check.sh による LS 検出・API 呼び出しの 6ヶ月運用実績
- 前セッション (1ac0c0e6) での 4-Step フロー curl 実証
- Synteleia L1 監査 PASS (7 agents, 16 issues, none critical)

## SCOPE

- antigravity_client.py: メインクライアント (LS 検出 + 4-Step フロー + ポーリング)
- cli.py: CLI インターフェース (ask, status, chat)

## WARNING

ToS グレーゾーン。実験用途限定。公開リポジトリにコミットしない。
