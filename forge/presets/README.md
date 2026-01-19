# Forge Presets - Google AI Studio用プリセット集

このディレクトリには、Google AI StudioのSystem Instructionsに
コピー＆ペーストで使えるプリセットが含まれています。

## 使い方

1. 使いたいプリセットファイル (`.txt`) を開く
2. 内容を全選択してコピー
3. Google AI Studio → System Instructions に貼り付け
4. チャットを開始

## プリセット一覧

| ファイル | 用途 | モジュール |
|----------|------|-----------|
| `architect.txt` | 設計・アーキテクチャ | Hypervisor + TDD + DMZ |
| `coder.txt` | コーディング支援 | Hypervisor + TDD + Logging |
| `analyst.txt` | 分析・調査 | 問題特定 + 状況把握 + 比較 |
| `writer.txt` | 文章作成 | 文章を書く + 品質確認 |
| `decision.txt` | 意思決定支援 | 決断 + リスク + 優先順位 |
| `brainstorm.txt` | アイデア出し | 脳内吐き出し + アイデア + 逆転 |

## カスタムプリセットの作り方

```powershell
# CLIでプリセットを生成
.\forge.ps1 preset create "my-preset" -modules "決断,リスク,計画"
```
