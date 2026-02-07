---
created: 2026-01-01T09:29:29 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/57212
author: AIDB Research
---

# 特定の個人の好みやニーズに最も適したレスポンスや行動を行うLLMを開発する手法、『Personalized Soups（意訳：ぼくだけのためのスープ）』が開発されました。 - AIDB

> ## Excerpt
> RLHF（人間のフィードバックによる強化学習）を個人に適用することで実現します。 ワシントン大学やカリフォルニア大学などの研究者らによる報告です。 @ Joel Jang et al., “Personalized Soups: Personalized Large Language Model Alignment via Post-hoc Parameter Merging&#822…

---
RLHF（人間のフィードバックによる強化学習）を個人に適用することで実現します。

ワシントン大学やカリフォルニア大学などの研究者らによる報告です。

@ Joel Jang et al., “Personalized Soups: Personalized Large Language Model Alignment via Post-hoc Parameter Merging”

![[特定の個人の好みやニーズに最も適したレスポンスや行動を行うLLMを開発する手法、『Personalized Soups（意訳：ぼくだけのためのスープ）』が開発されました。 - AIDB/AIDB_X_20231021-727x1024.jpg]]

RLHFは、一般的な人間の好みに合わせてLLMを調整するために、極めて有望な手法として知られています。  
しかし、個人に特化する用途では最適ではありませんでした。

そこで研究者らは「個人のフィードバックからの強化学習（RLPHF）」フレームワークを提案しています。

※本稿は論文の簡単な紹介記事です。

## RLPHFフレームワークの概要

フレームワークの概要は以下のとおりです。

ここから限定コンテンツ

① 複数の目標を同時に考慮するモデル（多目的強化学習）として設計  
② 複数の対立する目的を同時に持てるモデルを訓練する

## フレームワークの評価実験

GPT-4とTulu-7Bを用いて、対立する好みに基づいてペアワイズのフィードバックデータを収集

## 実験の結果

RLPHFは、下記の方法よりも個々のユーザーに対するより深いレベルの適応が可能だと評価されました。  
・教師ありの微調整  
・RLHF  
・プロンプト

## 実装方法・使い方

以下二つの方法が提案されています。  
① PROMPTED-MORL：プロンプトで目的の重要度を動的に変更  
② PERSONALIZED SOUPS：ポリシーを個別に最適化して、推論時にパラメータを合成する  
なお、GitHubにコードが公開されています。

## 主な結論

① RLPHFは、多様な個々の人間の好みに効率的に適応することができる  
② PERSONALIZED SOUPSはパラメータの合成を通じて効率的に複数の好みを組み合わせることができる

## 論文情報と関連研究

### 論文情報

Personalized Soups: Personalized Large Language Model Alignment via Post-hoc Parameter Merging  
URL：https://arxiv.org/abs/2310.11564  
コード（GitHub：https://github.com/joeljang/RLPHF）  
著者：Joel Jang, Seungone Kim, Bill Yuchen Lin, Yizhong Wang, Jack Hessel, Luke Zettlemoyer, Hannaneh Hajishirzi, Yejin Choi, Prithviraj Ammanabrolu  
機関：University of Washington, Allen Institute for AI, KAIST AI, UC San Diego

### 関連研究

・[「チャットハルヒ」既存のキャラクターの性格をLLMに模倣させることに特化したフレームワーク](https://ai-data-base.com/archives/54606)  
・[「わたしの話」を体系的に覚えてもらいながらLLMと会話する技術MemoChat登場](https://ai-data-base.com/archives/54560)  
・[AIは意識を持っているのか/持つのか、AI研究者と意識研究者たちが共同研究した結果](https://ai-data-base.com/archives/54645)  
・[LLMの個別の性格（人格）特性を、プロンプトで「測定」「形成」する手法](https://ai-data-base.com/archives/55413)

  
本投稿は[AIDBのXポスト](https://twitter.com/ai_database/status/1715677560091312613)の転載です。次の最新研究を最速で読みたい読者は[本アカウント](https://twitter.com/ai_database)をチェックしてみてくださいね。  
Xポストでは論文のカジュアルな紹介、本サイトではさらに論文の詳細な解説も掲載しています。

Copyright © Parks, Inc. All rights reserved.
