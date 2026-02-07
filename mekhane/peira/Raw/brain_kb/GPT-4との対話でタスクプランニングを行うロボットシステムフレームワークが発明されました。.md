---
created: 2026-01-01T09:30:01 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/56954
author: AIDB Research
---

# GPT-4との対話でタスクプランニングを行うロボットシステムフレームワークが発明されました。 - AIDB

> ## Excerpt
> 複雑なプロンプトエンジニアリングなしで細かな機能実行可能とのこと。 いわゆる “お料理ロボット” の原型が如く、一連の材料を正しい手順で混ぜてドリンクを作ることに成功しています。 UCバークレーの研究者らによる発表です。@ Boyi Li et al., “Interactive Task Planning with Language Models”…

---
複雑なプロンプトエンジニアリングなしで細かな機能実行可能とのこと。

いわゆる “お料理ロボット” の原型が如く、一連の材料を正しい手順で混ぜてドリンクを作ることに成功しています。

UCバークレーの研究者らによる発表です。  
@ Boyi Li et al., “Interactive Task Planning with Language Models”

![[GPT-4との対話でタスクプランニングを行うロボットシステムフレームワークが発明されました。 - AIDB/AIDB_X_20231018_1-723x1024.jpg]]

従来のロボットタスクプランニングは、目標に応じて事前に定義されたモジュール設計が必要であり、汎用的ではありませんでした。  
最近、LLMの活用が注目を集めてきましたが、ドメインごとの学習やプロンプトエンジニアリングが複雑だと言われてきました。

そこで研究者らは、さまざまなタスクにおいて、シンプルな対話で細かな作業が行えるフレームワーク『Interactive Task Planning（ITP）』を開発しました。

本稿は論文の簡単な紹介記事です。

## 『ITP』フレームワークの方法論

ここから限定コンテンツ

① ビジョン言語モデル（VLM）で視覚入力を言語に変換  
② GPT-4を言語モデルとして使用  
③ 高レベルのプランと低レベル（細かい機能）のロボットスキル実行を生成  
④ 各レベルに異なる言語エージェントを採用  
⑤ ロボットスキルを機能的なAPIに変換

## 実証実験

① ドリンク作成システムを検証した  
② タスクは、一連の材料から特定のドリンクを作成すること

## 実験の結果

① 既存のレシピから実行可能なプランを生成できる  
② ユーザーの入力に基づいてプランを動的に調整

## 主な結論

① 対話型のタスクプランニングにおいて有用  
② リアルワールドのロボットシステムに適用可能  
③ コードレベルのプロンプトエンジニアリングが不要

## 今後の展望

ユーザーからの新しいリクエストやフィードバックをリアルタイムで組み込む能力が必要

## 論文情報と関連研究

### 論文情報

Interactive Task Planning with Language Models  
URL：[https://arxiv.org/abs/2310.10645](https://arxiv.org/abs/2310.10645)  
プロジェクト：[https://wuphilipp.github.io/itp\_site/](https://wuphilipp.github.io/itp_site/)  
コード（GitHub）：[https://github.com/Boyiliee/ITP/](https://github.com/Boyiliee/ITP/) (coming soon)  
プレゼン（YouTube）：[https://youtube.com/watch?v=TrKLuyv26\_g](https://youtube.com/watch?v=TrKLuyv26_g)

### 関連研究

・[ロボットが「初めて見る環境」で「初めて聞く指示」に対しても行動をとれるようにする  
](https://ai-data-base.com/archives/54069)・[仮想世界でサッカーを学んだロボットが実世界で上手にサッカーをプレイ　DeepMindが研究報告  
](https://ai-data-base.com/archives/52175)・[LLMは世界モデルを持ち「物事がどのように位置づけられ、時間がどのように進行するか」を理解する可能性](https://ai-data-base.com/archives/56365)

本投稿は[AIDBのXポスト](https://twitter.com/ai_database/status/1714472746644832596)の転載です。次の最新研究を最速で読みたい読者は[本アカウント](https://twitter.com/ai_database)をチェックしてみてくださいね。  
Xポストでは論文のカジュアルな紹介、本サイトではさらに論文の詳細な解説も掲載しています。

Copyright © Parks, Inc. All rights reserved.
