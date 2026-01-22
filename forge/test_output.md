# 推論モデルが人間のように6つの思考パターンを使い分けているとの実験結果 - AIDB

# 推論モデルが人間のように6つの思考パターンを使い分けているとの実験結果

2024.10.242025.12.22

[深堀り解説](https://ai-data-base.com/archives/category/deep-dive)

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABAAAAAQAAQMAAABF07nAAAAAA1BMVEUAAACnej3aAAAAAXRSTlMAQObYZgAAAJZJREFUGBntwQEBAAAAgqD+r3ZIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAewEEHgABB9i6GAAAAABJRU5ErkJggg==) ![](https://ai-data-base.com/wp-content/uploads/2024/10/AIDB_77445_eye.jpeg)

クリップする [](https://twitter.com/share?url=https%3A%2F%2Fai-data-base.com%2Farchives%2F77445&text=%E6%8E%A8%E8%AB%96%E3%83%A2%E3%83%87%E3%83%AB%E3%81%8C%E4%BA%BA%E9%96%93%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB6%E3%81%A4%E3%81%AE%E6%80%9D%E8%80%83%E3%83%91%E3%82%BF%E3%83%BC%E3%83%B3%E3%82%92%E4%BD%BF%E3%81%84%E5%88%86%E3%81%91%E3%81%A6%E3%81%84%E3%82%8B%E3%81%A8%E3%81%AE%E5%AE%9F%E9%A8%93%E7%B5%90%E6%9E%9C) [](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fai-data-base.com%2Farchives%2F77445&src=sdkpreparse) [](https://note.com/intent/post?url=https%3A%2F%2Fai-data-base.com%2Farchives%2F77445)

[分析](https://ai-data-base.com/archives/type-tag/analysis)

[LLM](https://ai-data-base.com/archives/tech-tag/llm)

本記事では、AIの性能向上における「推論時の工夫」の効果について紹介します。

これまでAIの性能向上といえば「モデルを大きくする」「データを増やす」が定石でしたが、OpenAIが開発したo1モデルは「じっくり考える時間を確保する」という、人間に近い方法でブレークスルーを実現しました。今回研究者らは、o1モデルの詳細な分析を通じて、AIにおける「考える時間」の重要性と活用方法を明らかにしています。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABAAAAAJAAQMAAAApW4aWAAAAA1BMVEUAAACnej3aAAAAAXRSTlMAQObYZgAAAF5JREFUGBntwQEBAAAAgqD+r3ZIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgHsBIk8AAeBiYYYAAAAASUVORK5CYII=)![](https://ai-data-base.com/wp-content/uploads/2024/10/AIDB_77445-1024x576.png)

**本記事の関連研究**

  * [「o1-preview」は自己評価メカニズムを持つ 計画立案中に自分の行動をチェックして修正 ](https://ai-data-base.com/archives/77179)

  * [OpenAIのo1-previewモデル、Kaggleのグランドマスター基準を上回るデータ分析性能を発揮](https://ai-data-base.com/archives/77077)

  * [OpenAIの新しいモデルo1、従来のLLMと比べて「計画能力」で圧倒的な性能向上](https://ai-data-base.com/archives/76177)

  * [「o1」は従来のモデルとは明確に異なり「珍しいタイプの問題」にも強い](https://ai-data-base.com/archives/76609)




## 背景

最近のLLMは、推論やコーディング、数学など、様々な分野で素晴らしい成果を上げています。モデルの性能を向上させるためにされてきたこととしては、モデルのパラメータ（学習可能な重みの数）を増やしたり、学習データを増やしたりする方法が取られてきました。

しかし、このアプローチには限界が見えてきました。モデルを大きくすればするほど性能向上の効率が下がり、さらに計算コストが膨大になってしまうという問題に直面しています。

そこで注目されているのは推論時の工夫です。OpenAIが開発したo1モデルは、回答を出す前により時間をかけて考えることで、モデルサイズを増やさなくても性能を向上させることができました。この手法は、従来の方法と比べてより効率的だということが分かってきています。

しかし、推論時の工夫がどのように機能しているのか、その仕組みについてはまだよく分かっていません。その解明のため、今回研究者らははo1モデルの性能を詳しく調査し、既存の手法と比較することにしました。数学、コーディング、常識的推論という3つの重要な分野で評価を行い、活用法も明らかにしようとしています。

プレミアム会員限定コンテンツです

閲覧には、アカウント作成後の決済が必要です。

  * 全記事・論文コンテンツを無制限で閲覧可能
  * 平日毎日更新、専門家による最新リサーチを配信



[まずはアカウントを作成](/membership-join)

[ログイン](/membership-login)

[プレミアム会員について](/premium-visitor)

クリップする [](https://twitter.com/share?url=https%3A%2F%2Fai-data-base.com%2Farchives%2F77445&text=%E6%8E%A8%E8%AB%96%E3%83%A2%E3%83%87%E3%83%AB%E3%81%8C%E4%BA%BA%E9%96%93%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB6%E3%81%A4%E3%81%AE%E6%80%9D%E8%80%83%E3%83%91%E3%82%BF%E3%83%BC%E3%83%B3%E3%82%92%E4%BD%BF%E3%81%84%E5%88%86%E3%81%91%E3%81%A6%E3%81%84%E3%82%8B%E3%81%A8%E3%81%AE%E5%AE%9F%E9%A8%93%E7%B5%90%E6%9E%9C) [](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fai-data-base.com%2Farchives%2F77445&src=sdkpreparse) [](https://note.com/intent/post?url=https%3A%2F%2Fai-data-base.com%2Farchives%2F77445)
