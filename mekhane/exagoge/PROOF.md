# PROOF.md — mekhane/exagoge/

PURPOSE: データエクスポート・変換機能を提供し、外部システムとの連携を可能にする
REASON: Hegemonikón の内部データを外部形式に変換するための標準化されたパイプラインが必要だった

> **∃ exagoge/** — この場所は存在しなければならない

## モジュール構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | パッケージ初期化、定数定義 |
| `extractor.py` | BaseExporter 基底クラス + HandoffExporter |
| `library/` | プロンプトテンプレートライブラリ (51ファイル) |
