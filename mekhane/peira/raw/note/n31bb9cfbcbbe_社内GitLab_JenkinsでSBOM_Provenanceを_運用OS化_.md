# 社内GitLab/JenkinsでSBOM＋Provenanceを“運用OS化”する

> **Source**: https://note.com/tasty_dunlin998/n/n31bb9cfbcbbe
> **Published**: 2025-12-29T19:29:06+09:00
> **Collected**: 2026-02-06T21:35:28.234574

---

cosign＋syft＋in-toto（SLSA）を、SaaS無しで回すテンプレ付き

社内でソフトウェアを配布していると、ある日こう言われます。

「その成果物、何が入ってるの？」
「どの環境で、誰が、どうやって作ったの？」
「改ざんされてないって、どう証明するの？」

これを毎回“人力で説明”していると、QAもSREも消耗します。だから、SBOM（中身）＋Provenance（作られ方）をCIで自動生成して、署名して、配布側で強制検証する——ここまでをまとめて「運用OS」
