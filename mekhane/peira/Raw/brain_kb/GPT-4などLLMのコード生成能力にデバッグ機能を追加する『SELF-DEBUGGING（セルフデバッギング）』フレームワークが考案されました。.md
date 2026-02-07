---
created: 2026-01-01T09:30:05 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/56958
author: AIDB Research
---

# GPT-4などLLMのコード生成能力にデバッグ機能を追加する『SELF-DEBUGGING（セルフデバッギング）』フレームワークが考案されました。 - AIDB

> ## Excerpt
> 追加訓練なしで、複数のベンチマークで優秀なパフォーマンスを達成しています。実行プロンプト例は比較的シンプルです。 DeepMindとUCバークレーの研究者らによる発表です。@ Xinyun Chen et al, “Teaching Large Language Models to Self-Debug” LLMはコード生成においても優れた性能を示していますが、複雑なプログ…

---
追加訓練なしで、複数のベンチマークで優秀なパフォーマンスを達成しています。  
実行プロンプト例は比較的シンプルです。

DeepMindとUCバークレーの研究者らによる発表です。  
@ Xinyun Chen et al, “Teaching Large Language Models to Self-Debug”

![[GPT-4などLLMのコード生成能力にデバッグ機能を追加する『SELF-DEBUGGING（セルフデバッギング）』フレームワークが考案されました。 - AIDB/AIDB_X_20231017_2-709x1024.jpg]]

LLMはコード生成においても優れた性能を示していますが、複雑なプログラミングタスクで一度に正確な解を生成するのは困難とも言われています。  
既存の研究はモデルの追加訓練を必要とするものが多くコストがかかります。

そんな中、研究者らはLLMが自ら生成したプログラムをデバッグする能力を教えるフレームワークを考案しました。

本稿は論文の簡単な紹介記事です。

## フレームワークの方法論

SELF-DEBUGGINGは以下3つのステップで構成されます。

ここから限定コンテンツ

① 生成（Generation）  
② 説明（Explanation）  
③ フィードバック（Feedback）  
※これらはユーザーとLLMおよび場合によって外部のツールとのやりとりで実行されます。

## 性能の実験

下記の実験で評価されました。  
① テキストからSQLを生成するタスク（Spiderデータセット）  
② C++からPythonへのコード変換（TransCoder）  
③ テキストからPythonを生成するタスク（MBPP）  
なお、実験に使用されたLLMはGPT-4、GPT-3.5

## 実験の結果

① いくつかのコード生成ベンチマークで最先端の性能を達成  
② Spiderデータセットでは、コードの説明を用いることでベースラインを2-3%改善  
③ TransCoderとMBPPでは、ユニットテストを用いることで最大で12%の精度向上

## 実装方法・実行プロンプト例

下記は論文をもとに具体化したプロンプト例です。

ユーザー：  
_\*\*\*\*が行いたいです。 この問題に対する_を生成してください。  
LLM：  
\*\*\*\*

ユーザー：  
生成した\*\*\*\*が何をするのか説明してください。  
LLM：  
\*\*\*\*

ユーザー：  
生成した\*\*\*は正確ですか？不正確であれば、何が問題か説明してください。

## 主な結論

① LLMに自己デバッグの能力を教えることで、コード生成の性能が向上する  
② アプローチは、人間のフィードバックやユニットテストが不足している場合でも有用

## 注意点

① ユニットテストが問題の説明に含まれていない場合、モデルが生成したプログラムの正確性を推測するのは困難になる  
② 使用するモデル自体の限界とバイアスが結果に影響を与える可能性はある

## 論文情報と関連研究

### 論文情報

Teaching Large Language Models to Self-Debug  
URL：[https://arxiv.org/abs/2304.05128](https://arxiv.org/abs/2304.05128)  
著者：Xinyun Chen, Maxwell Lin, Nathanael Schärli, Denny Zhou  
機関：Google DeepMind, UC Berkeley

### 関連研究

・[GPT-4などのLLMに「自らの論理的な整合性をチェック」させるフレームワーク『LogiCoT』と実行プロンプト  
](https://ai-data-base.com/archives/55805)・[LLMの出力から誤り（ハルシネーション）を減らす新手法『CoVe（Chain-of-Verification）』と実行プロンプト  
](https://ai-data-base.com/archives/55711)・[メタ認知をさせてLLMの能力を上げる手法「メタ認知プロンプティング」](https://ai-data-base.com/archives/54435)

  
本投稿は[AIDBのXポスト](https://twitter.com/ai_database/status/1714267736959078672)の転載です。次の最新研究を最速で読みたい読者は[本アカウント](https://twitter.com/ai_database)をチェックしてみてくださいね。  
Xポストでは論文のカジュアルな紹介、本サイトではさらに論文の詳細な解説も掲載しています。

Copyright © Parks, Inc. All rights reserved.
