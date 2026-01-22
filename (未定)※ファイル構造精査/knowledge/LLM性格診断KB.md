<knowledge_module>
  <metadata>
    <topic_name>テキストベースの性格推定における定量的メタ分析 (2020-2025)</topic_name>
    <topic_prefix>CPP</topic_prefix>
    <generated_at>2025-12-31</generated_at>
    <latest_source_date>2025-12</latest_source_date>
    <keywords>
      <keyword>Computational Psychometrics</keyword>
      <keyword>Big Five (OCEAN)</keyword>
      <keyword>MBTI</keyword>
      <keyword>Dark Triad</keyword>
      <keyword>HEXACO</keyword>
      <keyword>Large Language Models (LLM)</keyword>
      <keyword>BERT/RoBERTa/DeBERTa</keyword>
      <keyword>Multimodal Learning</keyword>
      <keyword>Zero-shot Reasoning</keyword>
      <keyword>Alignment Problem</keyword>
      <keyword>Brain Rot</keyword>
      <keyword>PsyTEx Framework</keyword>
      <keyword>Narcissistic Personality Disorder (NPD)</keyword>
    </keywords>
  </metadata>

  <executive_summary>
    <![CDATA[
    * **パラダイムシフト:** 2020-2025年で、性格推定技術は辞書ベース（LIWC）から文脈理解（BERT）、そして心理的推論（LLM）へ移行。しかし、数値予測精度においてはエンコーダ型モデル（RoBERTa等）が生成AI（GPT-4等）を凌駕する傾向が継続している。
    * **予測精度の限界と突破口:** 連続値予測（Big Five）は相関係数 $r \approx 0.40$ で飽和状態（ガラスの天井）にある一方、二値分類（MBTI, Dark Triad）は「確信度閾値」の導入やドメイン適応により、実用レベル（Accuracy > 85%）に到達した。
    * **新たな課題:** 生成AIにおける「アライメント問題（中心化バイアス）」や、低品質データ学習による「Brain Rot（脳腐れ）」現象が浮上。対策として、心理学的に妥当なデータセット（PANDORA等）やマルチモーダル統合（HEXACO予測）が重要視されている。
    * **悪意の検出:** Dark TriadやNPD（自己愛性パーソナリティ障害）の検出において、特化したBERTモデルやハイブリッド手法が高い成果（F1 > 0.86）を上げている。
    ]]>
  </executive_summary>

  <structured_facts>
    <section title="Big Five (OCEAN): Benchmarks & Performance">
      <table_data>
        <![CDATA[
| Model/Team | Year | Dataset | Target | Metric | Performance | Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **YNU-HPCC** | 2023 | WASSA 2023 (Essay) | Empathy/Distress | Pearson r | 0.346 | DeBERTa + LoRA utilizing ensemble learning [2] |
| **Team Hawk** | 2023 | WASSA 2023 (Essay) | Openness | Pearson r | 0.3273 | BERT-based. High correlation with abstract vocabulary [3] |
| **Team Hawk** | 2023 | WASSA 2023 (Essay) | Extraversion | Pearson r | -0.1966 | Negative/Low correlation due to text volume not equaling extraversion [3] |
| **WASSA Winner** | 2024 | WASSA 2024 (Conversational) | Empathy/Emotion | Pearson r | 0.626 | RoBERTa-large. Significant jump due to dynamic interaction data [4] |
| **Zhu et al.** | 2025 | Interview Transcripts | Conscientiousness | Pearson r | 0.250 | GPT-4.1 Mini (Zero-shot). Shows alignment bias [1] |
| **ERNIE** | 2020 | MyPersonality | Big Five (All) | Accuracy | 87.17% | Legacy benchmark. Binary classification. Risk of overfitting [8] |
        ]]>
      </table_data>
      <narrative_list>
        <![CDATA[
        - **[CPP-FACT-001]** **データの変遷:** 研究用データセットは、小規模で自己呈示バイアスの強い「MyPersonality」から、1万人規模の「野生の」会話データを含む「PANDORA」や、動的な対話を含む「WASSA」へと移行した。
        - **[CPP-FACT-002]** **LLMの限界:** GPT-4.1 Miniなどの生成AIは、RLHFによるアライメント調整の影響で「中心化バイアス（Central Tendency Bias）」を持ち、性格特性の分散を捉えるのが苦手である。CoT（Chain-of-Thought）を行っても有意な改善は見られない [1]。
        - **[CPP-FACT-003]** **外向性のパラドックス:** テキストベース分析において、外向性は予測が難しい（r < 0, または低相関）。内向的な人間もテキストでは多弁になる可能性があり、従来の「発話量＝外向性」の仮説が成立しないためである [3]。
        ]]>
      </narrative_list>
    </section>

    <section title="MBTI & Dark Triad: Classification Dynamics">
      <table_data>
        <![CDATA[
| Task Domain | Model | Method | Performance | Insight |
| :--- | :--- | :--- | :--- | :--- |
| **MBTI (16-class)** | Transformer (Baseline) | Standard Classification | Acc ≈ 49-50% | Performance saturates without thresholding [5] |
| **MBTI (16-class)** | RoBERTa | **Confidence Threshold (>0.99)** | **Acc = 86.16%** | Supports "Prototype Theory"; highly accurate for typical users [5] |
| **MBTI (Binary)** | RoBERTa | I/E Axis Classification | F1 ≈ 0.78 | Linguistic markers are prominent for Introversion/Extraversion [5] |
| **Dark Triad** | Deep Learning (Hybrid) | PAN-2015 Benchmark | Acc = 79.51% | Outperforms LIWC by 15-20% due to context awareness |
| **NPD Detection** | BERT (DAPT) + Regex | "Cycle of Abuse" Detection | **F1 = 0.86** | Domain-Adaptive Pre-training on toxic data is crucial [6] |
        ]]>
      </table_data>
      <narrative_list>
        <![CDATA[
        - **[CPP-FACT-004]** **確信度閾値の発見:** すべてのユーザーを分類するのではなく、モデルの確信度が高い（>0.99）ユーザーのみを抽出することで、MBTI推定の正解率は49%から86%へ劇的に向上する。これはマーケティング等での実用性を示唆する [5]。
        - **[CPP-FACT-005]** **内向型バイアス:** Webテキストで学習されたモデルは、内向的・直観的（Intuitive）なペルソナをデフォルトで持ちやすい。これはオンライン空間でこれらのタイプのユーザーが活動的であることに起因する。
        - **[CPP-FACT-006]** **PsyTExフレームワーク:** LLMを直接分類器として使うのではなく、「心理学的特徴の抽出器」として使い、その出力を判定に用いることで、Dark Triad検出の解釈性と安定性が向上した。
        ]]>
      </narrative_list>
    </section>

    <section title="Architectures & Future Directions">
      <table_data>
        <![CDATA[
| Architecture Type | Examples | Strength | Weakness | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Encoder-only** | BERT, RoBERTa, DeBERTa | Precise numerical regression, High calibration | Limited generative capability | Scoring Big Five, Detecting NPD patterns |
| **Decoder-only** | GPT-4, Llama | Zero-shot reasoning, Explanation generation | Central tendency bias, Poor regression (r≈0.25) | Qualitative profiling, Data augmentation (PsyTEx) |
| **Multimodal** | Joint Model (ViT+BERT) | Capturing "Incongruence" (e.g., Honesty-Humility) | High computational cost | HEXACO H-factor detection, Deep behavioral analysis [7] |
        ]]>
      </table_data>
      <narrative_list>
        <![CDATA[
        - **[CPP-FACT-007]** **マルチタスク学習の優位性:** HEXACOとBig Fiveを同時に学習させる「結合モデリング」は、特にデータが少ないHEXACOのH因子（正直さ・謙虚さ）の予測精度を向上させる [7]。
        - **[CPP-FACT-008]** **Brain Rot現象:** 低品質なSNSデータや合成データを過剰に学習させると、モデルがステレオタイプを強化し、推論能力が低下する現象が2025年に確認された。
        - **[CPP-FACT-009]** **LIWCの役割:** 精度では深層学習に劣るが、「説明可能性（なぜその判定か）」においては依然として臨床的な価値を持つ。最新トレンドはBERTとLIWCのハイブリッド利用である。
        ]]>
      </narrative_list>
    </section>
  </structured_facts>

  <uncertainty_log>
    <![CDATA[
    - [UNCERTAIN] Big Five予測における相関係数の上限（r=0.40付近）が、現在のモデルアーキテクチャの限界なのか、テキストデータそのものが持つ情報量の上限（テキストには性格の全ては現れない）なのかは、議論が続いている。
    - [UNCERTAIN] GPT-4などのLLMにおいて、CoT（Chain-of-Thought）が性格推定精度を向上させないという結果 [1] は、他のタスクにおけるCoTの効果と矛盾しており、そのメカニズムは完全には解明されていない。
    ]]>
  </uncertainty_log>

  <source_index>
    <source id="[1]">
      <title>GPT-4.1 Mini Zero-shot Personality Estimation</title>
      <text_ref>Zhu et al. (2025)</text_ref>
    </source>
    <source id="[2]">
      <title>YNU-HPCC Team: DeBERTa + LoRA for Empathy Prediction</title>
      <text_ref>YNU-HPCC (2023) / WASSA 2023 Shared Task</text_ref>
    </source>
    <source id="[3]">
      <title>Team Hawk: BERT Ensemble for Big Five</title>
      <text_ref>Team Hawk (2023) / WASSA 2023 Shared Task</text_ref>
    </source>
    <source id="[4]">
      <title>RoBERTa-large Ensemble for Conversational Data</title>
      <text_ref>WASSA 2024 Winner (2024)</text_ref>
    </source>
    <source id="[5]">
      <title>MBTI Classification with Confidence Thresholding on Telegram Data</title>
      <text_ref>Shahnazari and Ayyoubzadeh (2025)</text_ref>
    </source>
    <source id="[6]">
      <title>Detecting Cycle of Abuse and NPD</title>
      <text_ref>Patel and Johnson (2025)</text_ref>
    </source>
    <source id="[7]">
      <title>Joint Modeling of Big Five and HEXACO using Multimodal Data</title>
      <text_ref>Masumura et al. (2025)</text_ref>
    </source>
    <source id="[8]">
      <title>ERNIE Model on MyPersonality Dataset</title>
      <text_ref>ERNIE Research (2020)</text_ref>
    </source>
  </source_index>
</knowledge_module>
