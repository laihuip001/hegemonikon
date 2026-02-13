# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

P3 → 記憶の永続化が必要
   → 永続化された知識との対話が必要
   → gnosis_chat.py が担う

Q.E.D.

---

Gnōsis Chat — NotebookLM 的 ローカル RAG 対話エンジン

Architecture:
  Query → GPU Embedding (BGE-small, 133MB)
       → LanceDB セマンティック検索 (Top-K)
       → Qwen 2.5 3B Instruct (4bit, ~2.5GB)
       → マルチターン対話で回答生成

VRAM Budget:
  BGE-small embedding: ~133MB
  Qwen 2.5 3B (4bit): ~2.5GB
  Total: ~2.6GB / 8GB RTX 2070 SUPER

Knowledge Sources:
  - Gnōsis 論文 (LanceDB papers table)
  - Handoff 引継書 (mneme sessions)
  - KI/Insight (mneme sessions)
  - Kernel ドキュメント (kernel/)
  - セッションログ (mneme sessions)
"""

import sys
import time
from pathlib import Path
from typing import Optional
from mekhane.anamnesis.lancedb_compat import get_table_names

# Hegemonikon root
_THIS_DIR = Path(__file__).parent
_HEGEMONIKON_ROOT = _THIS_DIR.parent.parent

# Knowledge source paths
_MNEME_ROOT = Path.home() / "oikos" / "mneme" / ".hegemonikon"
MNEME_SESSIONS = _MNEME_ROOT / "sessions"
MNEME_KNOWLEDGE = _MNEME_ROOT / "knowledge"
MNEME_HANDOFFS = _MNEME_ROOT / "handoffs"
MNEME_DOXA = _MNEME_ROOT / "doxa"
MNEME_WORKFLOWS = _MNEME_ROOT / "workflows"
MNEME_RESEARCH = _MNEME_ROOT / "research"
MNEME_XSERIES = _MNEME_ROOT / "x-series"
KERNEL_DIR = _HEGEMONIKON_ROOT / "kernel"
HANDOFF_DIR = _HEGEMONIKON_ROOT / "docs" / "handoff"


# PURPOSE: マルチターン対話の履歴管理.
class ConversationHistory:
    """マルチターン対話の履歴管理."""

    # PURPOSE: ConversationHistory の初期化 — ターンを追加.
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.turns: list[dict] = []

    # PURPOSE: ターンを追加.
    def add(self, role: str, content: str):
        """ターンを追加."""
        self.turns.append({"role": role, "content": content})
        # 最大ターン数を超えたら古いものを削除
        if len(self.turns) > self.max_turns * 2:
            self.turns = self.turns[-(self.max_turns * 2):]

    # PURPOSE: プロンプト用にフォーマット.
    def format_for_prompt(self) -> str:
        """プロンプト用にフォーマット."""
        if not self.turns:
            return ""
        parts = []
        for t in self.turns:
            if t["role"] == "user":
                parts.append(f"<|im_start|>user\n{t['content']}<|im_end|>")
            else:
                parts.append(f"<|im_start|>assistant\n{t['content']}<|im_end|>")
        return "\n".join(parts)

    # PURPOSE: 状態のリセットと再初期化
    def clear(self):
        self.turns.clear()

    # PURPOSE: gnosis_chat の turn count 処理を実行する
    @property
# PURPOSE: Cross-encoder Reranker for precision improvement.
    # PURPOSE: Cross-encoder Reranker for precision improvement. Strategy: bi-encoder でオーバーフェッチ
    def turn_count(self) -> int:
        return len(self.turns) // 2


# PURPOSE: の統一的インターフェースを実現する
class Reranker:
    """Cross-encoder Reranker for precision improvement.

    Strategy: bi-encoder でオーバーフェッチ → cross-encoder で re-score
    → top-k に絞る。精度を大幅に向上させる。

    VRAM: ~50MB (cross-encoder-ms-marco-MiniLM-L-6-v2)
    """

    DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # PURPOSE: Reranker の構成と依存関係の初期化
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self._model = None

    # PURPOSE: cross-encoder モデルの遅延ロード — ネットワーク障害時のフォールバック付き
    def _load(self):
        if self._model is not None:
            return
        if getattr(self, "_failed", False):
            return  # 既に失敗済み — ロード再試行しない
        import os
        from sentence_transformers import CrossEncoder
        # Strategy: ローカルキャッシュ優先 → リモートフォールバック → 無効化
        for attempt, offline in enumerate(["1", ""]):
            try:
                if offline:
                    os.environ["HF_HUB_OFFLINE"] = "1"
                    os.environ["TRANSFORMERS_OFFLINE"] = "1"
                self._model = CrossEncoder(self.model_name, device="cuda")
                print(f"[Reranker] Loaded ({self.model_name},"
                      f" offline={bool(offline)})", flush=True)
                return
            except Exception as e:
                if attempt == 0:
                    # ローカル失敗 → リモート試行
                    os.environ.pop("HF_HUB_OFFLINE", None)
                    os.environ.pop("TRANSFORMERS_OFFLINE", None)
                    continue
                # 全試行失敗
                print(f"[Reranker] ⚠️ Failed to load ({e}), "
                      f"falling back to bi-encoder only", flush=True)
                self._failed = True
                return

    # Cross-encoder score threshold (Layer 2)
    # MiniLM scores are relative, not absolute.
    # Used only as a secondary noise filter.
    SCORE_THRESHOLD = -4.0

    # PURPOSE: 検索結果を cross-encoder で再スコアリング + 閾値フィルタ.
    def rerank(
        self, query: str, results: list[dict], top_k: int = 5
    ) -> list[dict]:
        """検索結果を cross-encoder で再スコアリング + 閾値フィルタ.

        Args:
            query: 検索クエリ
            results: bi-encoder の検索結果
            top_k: 返す件数

        Returns:
            re-scored, filtered & sorted results (top_k)
        """
        if not results:
            return results

        self._load()

        # Reranker ロード失敗時は bi-encoder 結果をそのまま返す
        if self._model is None:
            return sorted(results, key=lambda r: r.get("_distance", 999))[:top_k]

        # (query, document) ペアを作成
        pairs = []
        for r in results:
            table = r.get("_source_table", "unknown")
            if table == "knowledge":
                text = r.get("content", r.get("abstract", ""))[:512]
            else:
                text = f"{r.get('title', '')} {r.get('abstract', '')[:400]}"
            pairs.append((query, text))

        # Cross-encoder scoring
        scores = self._model.predict(pairs)

        # スコアを結果に付与
        for r, score in zip(results, scores):
            r["_rerank_score"] = float(score)

        # Layer 2: cross-encoder 閾値フィルタ
        filtered = [
            r for r in results
            if r.get("_rerank_score", -999) > self.SCORE_THRESHOLD
# PURPOSE: Hegemonikón 全知識をインデックスに追加するユーティリティ.
        ]

        # re-rank score でソート (高い方が良い)
        filtered.sort(key=lambda r: r.get("_rerank_score", -999), reverse=True)

        return filtered[:top_k]


# PURPOSE: Hegemonikón 全知識をインデックスに追加するユーティリティ
class KnowledgeIndexer:
    """Hegemonikón 全知識をインデックスに追加するユーティリティ."""

    # PURPOSE: gnosis_chat の discover knowledge files 処理を実行する
    @staticmethod
    # PURPOSE: 全知識ソースからファイルを発見.
    def discover_knowledge_files() -> list[dict]:
        """全知識ソースからファイルを発見.

        Returns:
            list of dict with keys: path, source_type, title
        """
        files = []

        # 1. Handoff files (mneme/sessions)
        if MNEME_SESSIONS.exists():
            for f in sorted(MNEME_SESSIONS.glob("handoff_*.md")):
                files.append({
                    "path": f,
                    "source_type": "handoff",
                    "title": f.stem.replace("_", " ").title(),
                })

        # 2. Session logs (mneme/sessions)
        if MNEME_SESSIONS.exists():
            for f in sorted(MNEME_SESSIONS.glob("2026-*_conv_*.md")):
                files.append({
                    "path": f,
                    "source_type": "session",
                    "title": f.stem.split("_", 3)[-1].replace("_", " ")
                    if "_" in f.stem else f.stem,
                })

        # 3. KI / Insight files (mneme/sessions)
        if MNEME_SESSIONS.exists():
            for f in sorted(MNEME_SESSIONS.glob("insight_*.md")):
                files.append({
                    "path": f,
                    "source_type": "ki",
                    "title": f.stem.replace("_", " ").title(),
                })
            for f in sorted(MNEME_SESSIONS.glob("weekly_review_*.md")):
                files.append({
                    "path": f,
                    "source_type": "review",
                    "title": f.stem.replace("_", " ").title(),
                })

        # 4. Knowledge (mneme/knowledge/)
        if MNEME_KNOWLEDGE.exists():
            for f in sorted(MNEME_KNOWLEDGE.glob("*.md")):
                files.append({
                    "path": f,
                    "source_type": "ki",
                    "title": f.stem.replace("_", " ").title(),
                })

        # 5. Handoff (docs/)
        if HANDOFF_DIR.exists():
            for f in sorted(HANDOFF_DIR.glob("*.md")):
                files.append({
                    "path": f,
                    "source_type": "handoff",
                    "title": f.stem.replace("_", " ").title(),
                })

        # 6. Mneme Handoffs (handoffs/ dir)
        if MNEME_HANDOFFS.exists():
            for f in sorted(MNEME_HANDOFFS.glob("*.md")):
                files.append({
                    "path": f,
                    "source_type": "handoff",
                    "title": f.stem.replace("_", " ").title(),
                })

        # 7. Doxa (belief records)
        if MNEME_DOXA.exists():
            for f in sorted(MNEME_DOXA.rglob("*.md")):
                files.append({
                    "path": f,
                    "source_type": "doxa",
                    "title": f.stem.replace("_", " ").title(),
                })

        # 8. Workflow artifacts
        if MNEME_WORKFLOWS.exists():
            for f in sorted(MNEME_WORKFLOWS.glob("*.md")):
                files.append({
                    "path": f,
                    "source_type": "workflow",
                    "title": f.stem.replace("_", " ").title(),
                })

        # 9. Research notes
        if MNEME_RESEARCH.exists():
            for f in sorted(MNEME_RESEARCH.glob("*.md")):
                files.append({
                    "path": f,
                    "source_type": "research",
                    "title": f.stem.replace("_", " ").title(),
                })

        # 10. X-series relation maps
        if MNEME_XSERIES.exists():
            for f in sorted(MNEME_XSERIES.glob("*.md")):
                files.append({
                    "path": f,
                    "source_type": "xseries",
                    "title": f.stem.replace("_", " ").title(),
                })

        # 11. Kernel docs
        if KERNEL_DIR.exists():
            for f in sorted(KERNEL_DIR.glob("*.md")):
                files.append({
                    "path": f,
                    "source_type": "kernel",
                    "title": f.stem.replace("_", " ").title(),
                })
            # CEP
            cep_dir = KERNEL_DIR / "cep"
            if cep_dir.exists():
                for f in sorted(cep_dir.glob("*.md")):
                    files.append({
                        "path": f,
                        "source_type": "kernel",
                        "title": f"CEP: {f.stem}",
                    })

        return files

    @staticmethod
    # PURPOSE: テキストをセマンティック境界で分割 (Markdown セクション対応).
    def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
        """テキストをセマンティック境界で分割.

        戦略:
          1. Markdown ## ヘッダーでセクション分割 (セマンティック単位)
          2. セクションが chunk_size を超える場合、段落 (空行) で分割
          3. それでも超える場合、文の途中で切らないよう改行で分割
        """
        if len(text) <= chunk_size:
            return [text]

        import re

        # Phase 1: Markdown セクション分割 (##, ###, ----)
        sections = re.split(r'\n(?=#{1,4}\s|\-{3,})', text)

        chunks = []
        for section in sections:
            section = section.strip()
            if not section:
                continue

            if len(section) <= chunk_size:
                chunks.append(section)
            else:
                # Phase 2: 空行で段落分割
                paragraphs = re.split(r'\n\s*\n', section)
                buffer = ""
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue

                    if len(buffer) + len(para) + 2 <= chunk_size:
                        buffer = f"{buffer}\n\n{para}" if buffer else para
                    else:
                        if buffer:
                            chunks.append(buffer)
                        # Phase 3: 段落自体が大きい場合、改行で切る
                        if len(para) > chunk_size:
                            sub_chunks = KnowledgeIndexer._split_long_text(
                                para, chunk_size, overlap
                            )
                            chunks.extend(sub_chunks)
                        else:
                            buffer = para
                            continue
                        buffer = ""
                if buffer:
                    chunks.append(buffer)

        return [c for c in chunks if c and len(c) > 20]

    @staticmethod
    # PURPOSE: [L2-auto] フォールバック: 改行で切る固定サイズ分割.
    def _split_long_text(text: str, chunk_size: int, overlap: int) -> list[str]:
        """フォールバック: 改行で切る固定サイズ分割."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            if end < len(text):
                last_nl = chunk.rfind("\n")
                if last_nl > chunk_size // 2:
                    end = start + last_nl + 1
                    chunk = text[start:end]

            chunks.append(chunk.strip())
            # Guard: start は必ず前進する (overlap > effective chunk 時の無限ループ防止)
            start = max(start + 1, end - overlap)
        return [c for c in chunks if c]

    @staticmethod
    # PURPOSE: [L2-auto] embedding 用テキストを構築 (タイトル + ソース + コンテンツ).
    def _build_embedding_text(title: str, source: str, content: str) -> str:
        """embedding 用テキストを構築 (タイトル + ソース + コンテンツ).

        検索精度向上のため、構造化されたプレフィックスを付与。
        """
        prefix = f"[{source}] {title}\n"
        max_content = 500 - len(prefix)
        return prefix + content[:max_content]

    # PURPOSE: gnosis_chat の index knowledge 処理を実行する
    @staticmethod
    # PURPOSE: 全知識をインデックスに追加.
    def index_knowledge(force_reindex: bool = False) -> int:
        """全知識をインデックスに追加.

        Returns:
            追加されたドキュメント数
        """
        from mekhane.anamnesis.index import GnosisIndex, LANCE_DIR
        from mekhane.anamnesis.models.paper import Paper

        index = GnosisIndex()

        # 既存の knowledge テーブルを確認
        table_name = "knowledge"
        existing_keys = set()

        if not force_reindex and table_name in get_table_names(index.db):
            try:
                table = index.db.open_table(table_name)
                df = table.search().select(["primary_key"]).limit(None).to_pandas()
                existing_keys = set(df["primary_key"].tolist())
                print(f"[Knowledge] Existing: {len(existing_keys)} chunks")
            except Exception:
                pass

        files = KnowledgeIndexer.discover_knowledge_files()
        print(f"[Knowledge] Discovered {len(files)} knowledge files")

        # チャンクに分割してインデックス
        embedder = index._get_embedder()
        data = []
        skipped = 0

        for finfo in files:
            try:
                text = finfo["path"].read_text(encoding="utf-8")
            except Exception:
                continue

            chunks = KnowledgeIndexer._chunk_text(text)

            for ci, chunk in enumerate(chunks):
                primary_key = f"{finfo['source_type']}:{finfo['path'].stem}:{ci}"

                if primary_key in existing_keys:
                    skipped += 1
                    continue

                data.append({
                    "primary_key": primary_key,
                    "title": finfo["title"],
                    "source": finfo["source_type"],
                    "abstract": chunk[:300],
                    "content": chunk,
                    "authors": "",
                    "doi": "",
                    "arxiv_id": "",
                    "url": str(finfo["path"]),
                    "citations": 0,
                })

        if not data:
            print(f"[Knowledge] No new documents (skipped {skipped})")
            return 0

        # バッチ embedding
        print(f"[Knowledge] Embedding {len(data)} chunks...", flush=True)
        BATCH_SIZE = 32
        for i in range(0, len(data), BATCH_SIZE):
            batch = data[i:i + BATCH_SIZE]
            texts = [
                KnowledgeIndexer._build_embedding_text(
                    d["title"], d["source"], d["content"]
                )
                for d in batch
            ]
            vectors = embedder.embed_batch(texts)

            for d, v in zip(batch, vectors):
                d["vector"] = v

            done = min(i + BATCH_SIZE, len(data))
            print(f"  Embedded {done}/{len(data)}...", flush=True)

# PURPOSE: Gnōsis 対話型 RAG エンジン.
        # LanceDB に追加
        if table_name in get_table_names(index.db):
            table = index.db.open_table(table_name)
            table.add(data)
        else:
            index.db.create_table(table_name, data=data)

        print(f"[Knowledge] Added {len(data)} chunks (skipped {skipped})")
        return len(data)


# PURPOSE: Gnōsis 対話型 RAG エンジン
class GnosisChat:
    """Gnōsis 対話型 RAG エンジン.

    NotebookLM のように、自分のデータに基づいて対話する。
    完全ローカル (オフライン動作可能)。

    3層ハルシネーション防御:
      Layer 1: bi-encoder distance threshold
      Layer 2: cross-encoder score threshold
      Layer 3: confidence assessment → prompt adaptation

    Layer 4: Prompt-level steering
      System prompt に contrastive guidance を注入して振る舞いを制御。
    """

    DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"

    # Layer 1: bi-encoder distance threshold
    # LanceDB L2 distance on normalized vectors:
    #   0 = identical, ~1.0 = unrelated, ~1.41 = opposite
    DISTANCE_THRESHOLD = 0.85

    # Papers: cross-language gap (+0.21~0.28) を考慮して緩和
    PAPERS_DISTANCE_THRESHOLD = 0.95

    # Prompt-level steering profiles
    STEERING_PROFILES = {
        "hegemonikon": (
            "\n## 振る舞い指針 (Steering)\n"
            "- 不確実な場合は『確信度が低いですが...』と前置きする\n"
            "- 質問に答える前に、回答の前提条件を明示する\n"
            "- 複数の解釈が可能な場合は、それぞれの可能性を列挙する\n"
            "- 潜在的なリスクや注意点に気づいた場合は、積極的に指摘する\n"
            "- 回答が知識ベースの情報のみに基づくことを意識し、推測と事実を明確に区別する\n"
        ),
        "neutral": "",  # No steering
        "academic": (
            "\n## 振る舞い指針 (Steering)\n"
            "- 学術的な正確さを最優先する\n"
            "- 主張には必ず根拠 [番号] を付与する\n"
            "- 対立する見解がある場合は両方を提示する\n"
            "- 方法論的な限界を指摘する\n"
        ),
    }

    # Confidence levels
    CONFIDENCE_HIGH = "high"
    CONFIDENCE_MEDIUM = "medium"
    CONFIDENCE_LOW = "low"
    CONFIDENCE_NONE = "none"

    # PURPOSE: 知識基盤コンポーネントの初期化
    def __init__(
        self,
        model_id: Optional[str] = None,
        top_k: int = 5,
        max_new_tokens: int = 512,
        search_knowledge: bool = True,
        search_papers: bool = True,
        use_reranker: bool = True,
        steering_profile: str = "hegemonikon",
    ):
        self.model_id = model_id or self.DEFAULT_MODEL
        self.top_k = top_k
        self.max_new_tokens = max_new_tokens
        self.search_knowledge = search_knowledge
        self.search_papers = search_papers
        self.use_reranker = use_reranker
        self.steering_profile = steering_profile

        self._index = None
        self._model = None
        self._tokenizer = None
        self._reranker = Reranker() if use_reranker else None
        self.history = ConversationHistory(max_turns=5)

    # PURPOSE: Gnōsis インデックスをロード (GPU embedding).
    def _load_index(self):
        """Gnōsis インデックスをロード (GPU embedding)."""
        if self._index is not None:
            return
        from mekhane.anamnesis.index import GnosisIndex
        self._index = GnosisIndex()
        print("[Gnōsis Chat] Index loaded", flush=True)

    # PURPOSE: VRAM タイムシェア: Embedder を解放して LLM 用に VRAM を確保.
    def _unload_embedder(self):
        """VRAM タイムシェア: Embedder を解放して LLM 用に VRAM を確保.

        BGE-m3 (2.3GB) + Qwen 3B (2.1GB) = 4.4GB > 8GB GPU
        検索完了後に Embedder をアンロードして LLM ロード可能にする。
        """
        import gc
        import torch
        if self._index is not None:
            embedder = self._index._get_embedder()
            if hasattr(embedder, '_st_model') and embedder._st_model is not None:
                del embedder._st_model
                embedder._st_model = None
                embedder._use_gpu = False
            # Reranker も解放
            if self._reranker and self._reranker._model is not None:
                del self._reranker._model
                self._reranker._model = None
            gc.collect()
            torch.cuda.empty_cache()
            vram_mb = torch.cuda.memory_allocated() / 1e6
            print(f"[Gnōsis Chat] Embedder unloaded ({vram_mb:.0f}MB VRAM)", flush=True)

    # PURPOSE: LLM をロード (4bit量子化 on GPU).
    def _load_model(self):
        """LLM をロード (4bit量子化 on GPU)."""
        if self._model is not None:
            return

        # VRAM タイムシェア: Embedder を先に解放
        self._unload_embedder()

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        print(f"[Gnōsis Chat] Loading {self.model_id}...", flush=True)
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=bnb_config,
            device_map="auto",
        )

        vram_mb = torch.cuda.memory_allocated() / 1e6
        print(f"[Gnōsis Chat] Model loaded ({vram_mb:.0f}MB VRAM)", flush=True)

    # PURPOSE: 全テーブルからセマンティック検索 + 閾値フィルタ + rerank.
    def _retrieve(self, query: str) -> list[dict]:
        """全テーブルからセマンティック検索 + 閾値フィルタ + rerank."""
        self._load_index()
        results = []
        fetch_k = self.top_k * 3 if self._reranker else self.top_k

        # Papers table
        if self.search_papers:
            try:
                paper_results = self._index.search(query, k=fetch_k)
                for r in paper_results:
                    r["_source_table"] = "papers"
                results.extend(paper_results)
            except Exception:
                pass

        # Knowledge table
        if self.search_knowledge:
            try:
                if "knowledge" in get_table_names(self._index.db):
                    embedder = self._index._get_embedder()
                    # Dimension check: knowledge table may be indexed with a different model
                    table = self._index.db.open_table("knowledge")
                    from mekhane.anamnesis.index import _get_vector_dimension
                    table_dim = _get_vector_dimension(table)
                    embedder_dim = getattr(embedder, '_dimension', 0)
                    if table_dim and embedder_dim and table_dim != embedder_dim:
                        print(
                            f"[Gnōsis Chat] ⚠️ Knowledge table dimension mismatch: "
                            f"table={table_dim}, embedder={embedder_dim} "
                            f"({'ONNX fallback' if getattr(embedder, '_is_onnx_fallback', False) else embedder.model_name}). "
                            f"Skipping knowledge search.",
                            flush=True,
                        )
                    else:
                        qvec = embedder.embed(query)
                        k_results = table.search(qvec).limit(fetch_k).to_list()
                        for r in k_results:
                            r["_source_table"] = "knowledge"
                        results.extend(k_results)
            except Exception:
                pass

        # Layer 1: bi-encoder 距離閾値フィルタ (papers/knowledge で閾値分離)
        before_filter = len(results)
        results = [
            r for r in results
            if r.get("_distance", 999) < (
                self.PAPERS_DISTANCE_THRESHOLD
                if r.get("_source_table") == "papers"
                else self.DISTANCE_THRESHOLD
            )
        ]
        if before_filter > 0 and len(results) == 0:
            print(f"[Gnōsis Chat] Layer 1: all {before_filter} results filtered "
                  f"(knowledge>{self.DISTANCE_THRESHOLD}, "
                  f"papers>{self.PAPERS_DISTANCE_THRESHOLD})", flush=True)

        results.sort(key=lambda r: r.get("_distance", 999))

        # Layer 2: Reranker
        if self._reranker and results:
            results = self._reranker.rerank(query, results, top_k=self.top_k)
        else:
            results = results[:self.top_k]

        return results

    # PURPOSE: Layer 3: 検索結果の品質から確信度を判定.
    def _assess_confidence(self, results: list[dict]) -> str:
        """Layer 3: 検索結果の品質から確信度を判定.

        距離 (bi-encoder) のみで判定する。
        cross-encoder スコアは relative ranking 用であり absolute 判定には不適。

        BGE-m3 距離スケール (L2, normalized):
          - 関連: 0.5-0.8
          - 曖昧: 0.8-0.9
          - 無関連: >0.9 (DISTANCE_THRESHOLD で除去済み)
        """
        if not results:
            return self.CONFIDENCE_NONE

        distances = [r.get("_distance", 999) for r in results]
        min_dist = min(distances)
        avg_dist = sum(distances) / len(distances)
        n = len(results)

        if min_dist < 0.6 and n >= 3 and avg_dist < 0.75:
            return self.CONFIDENCE_HIGH
        elif min_dist < 0.7:
            return self.CONFIDENCE_HIGH
        elif min_dist < 0.8:
            return self.CONFIDENCE_MEDIUM
        else:
            return self.CONFIDENCE_LOW

    # PURPOSE: 検索結果からコンテキスト文字列を構築 (Source Grounding 強化).
    def _build_context(self, results: list[dict]) -> str:
        """検索結果からコンテキスト文字列を構築.

        Source Grounding: 各引用パッセージにソースファイルパスと
        チャンク ID を付与し、回答の追跡可能性を確保する。
        """
        context_parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            source = r.get("source", "unknown")
            table = r.get("_source_table", "unknown")

            # knowledge テーブルの場合は content を使用
            if table == "knowledge":
                content = r.get("content", r.get("abstract", ""))[:600]
            else:
                content = r.get("abstract", "")[:500]

            authors = r.get("authors", "")[:80]
            dist = r.get("_distance", 0)

            # Source Grounding: ファイルパスと chunk_id で追跡可能にする
            primary_key = r.get("primary_key", "")
            url = r.get("url", "")
            source_loc = ""
            if primary_key:
                source_loc = f"    Source: {primary_key}\n"
            elif url:
                source_loc = f"    Source: {url}\n"

            context_parts.append(
                f"[{i}] [{source}] {title}\n"
                f"    Relevance: {1 - dist:.2f}\n"
                f"{source_loc}"
                f"    {content}"
            )
        return "\n\n".join(context_parts)

    # PURPOSE: LLM で回答を生成.
    def _generate(self, prompt: str) -> str:
        """LLM で回答を生成."""
        import torch

        self._load_model()

        inputs = self._tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=2048
        ).to(self._model.device)

        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.15,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        # プロンプト部分を除去して回答のみ返す
        input_len = inputs["input_ids"].shape[1]
        answer_tokens = outputs[0][input_len:]
        return self._tokenizer.decode(answer_tokens, skip_special_tokens=True)

    # PURPOSE: 質問に回答する (RAG + マルチターン + 3層防御).
    def ask(self, question: str) -> dict:
        """質問に回答する (RAG + マルチターン + 3層防御)."""
        # 1. Retrieve (Layer 1 + 2)
        t0 = time.time()
        results = self._retrieve(question)
        retrieval_time = time.time() - t0

        # 2. Layer 3: Confidence
        confidence = self._assess_confidence(results)
        context = self._build_context(results)

        # 3. Confidence-adaptive response
        if confidence == self.CONFIDENCE_NONE:
            answer = (
                "📋 **ソースに情報がありません**\n\n"
                "この質問に関連する情報は、現在の知識ベースに見つかりませんでした。\n"
                "Gnōsis はソースに基づく回答のみを提供し、推測は行いません。\n\n"
                "**対処法:**\n"
                "- 🔄 別のキーワードで質問する\n"
                "- 📥 `/index` で知識ベースを更新する\n"
                "- 📄 `collect` コマンドで関連する論文を追加する\n"
                "- 🔍 質問の範囲を狭める（具体的なトピック名を含める）"
            )
            generation_time = 0
        else:
            conf_instr = {
                self.CONFIDENCE_HIGH: "検索結果に十分な情報があります。自信を持って回答してください。",
                self.CONFIDENCE_MEDIUM: (
                    "検索結果に部分的な情報があります。"
                    "不確実な部分は『知識ベースに十分な情報がありません』と明示してください。"
                ),
                self.CONFIDENCE_LOW: (
                    "検索結果との関連性が低い可能性があります。"
                    "推測や創作は絶対にしないでください。"
                    "回答冒頭に『⚠️ 関連性が低い情報に基づく回答です』と記載してください。"
                    "答えられない場合は『十分な情報がありません』と正直に返してください。"
                ),
            }.get(confidence, "")

            system_prompt = (
                "あなたは Hegemonikón の知識ベース対話アシスタントです。\n"
                "以下の検索結果に基づいて、ユーザーの質問に日本語で正確に回答してください。\n"
                f"{conf_instr}\n"
                "回答は簡潔で構造的にしてください。\n"
                "引用する場合は [番号] の形式で参照元を示してください。\n"
                "検索結果にない情報を創作・推測しないでください。"
                + self.STEERING_PROFILES.get(self.steering_profile, "")
            )

            prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            history_text = self.history.format_for_prompt()
            if history_text:
                prompt += history_text + "\n"
            prompt += (
                f"<|im_start|>user\n"
                f"## 検索結果 (関連文書)\n\n{context}\n\n"
                f"## 質問\n{question}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )

            t0 = time.time()
            answer = self._generate(prompt)
            generation_time = time.time() - t0

        self.history.add("user", question)
        self.history.add("assistant", answer.strip())

        sources = []
        for r in results:
            sources.append({
                "title": r.get("title", "Untitled")[:80],
                "source": r.get("source", "unknown"),
                "table": r.get("_source_table", "unknown"),
                "url": r.get("url", ""),
                "primary_key": r.get("primary_key", ""),
                "content_snippet": (r.get("content", r.get("abstract", "")))[:200],
                "distance": round(r.get("_distance", 0), 4),
                "relevance": round(1 - r.get("_distance", 0), 4),
                "rerank_score": r.get("_rerank_score"),
            })

        return {
            "answer": answer.strip(),
            "sources": sources,
            "confidence": confidence,
            "retrieval_time": round(retrieval_time, 3),
            "generation_time": round(generation_time, 1),
            "context_docs": len(results),
            "turn": self.history.turn_count,
        }

    # PURPOSE: 検索のみ実行 (LLM 不使用). Claude (IDE) が Generation する用
    def retrieve_only(self, query: str) -> dict:
        """検索のみ実行 (LLM 不使用). Claude (IDE) が Generation する用."""
        t0 = time.time()
        results = self._retrieve(query)
        retrieval_time = time.time() - t0
        confidence = self._assess_confidence(results)
        context = self._build_context(results)

        sources = []
        for r in results:
            sources.append({
                "title": r.get("title", "Untitled")[:80],
                "source": r.get("source", "unknown"),
                "table": r.get("_source_table", "unknown"),
                "url": r.get("url", ""),
                "distance": round(r.get("_distance", 0), 4),
                "rerank_score": r.get("_rerank_score"),
            })

        return {
            "context": context,
            "sources": sources,
            "confidence": confidence,
            "retrieval_time": round(retrieval_time, 3),
            "context_docs": len(results),
        }

    # PURPOSE: 対話ループ (REPL).
    def interactive(self):
        """対話ループ (REPL)."""
        print("\n" + "=" * 60)
        print("  Gnōsis Chat — Hegemonikón ローカル知識ベース対話")
        print(f"  Model: {self.model_id}")
        print(f"  Steering: {self.steering_profile}")
        print("  Commands: /quit, /sources, /stats, /clear, /index, /steering")
        print("=" * 60)

        last_result = None

        while True:
            try:
                turn = self.history.turn_count
                question = input(f"\n[{turn}] ❓ ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye.")
                break

            if not question:
                continue

            if question in ("/quit", "/q", "/exit"):
                print("bye.")
                break

            if question == "/clear":
                self.history.clear()
                print("🔄 会話履歴をクリアしました")
                continue

            if question == "/sources" and last_result:
                print("\n📚 Sources:")
                for i, s in enumerate(last_result["sources"], 1):
                    icon = {"papers": "📄", "knowledge": "🧠"}.get(
                        s["table"], "📁"
                    )
                    print(f"  [{i}] {icon} [{s['source']}] {s['title']}")
                    print(f"      Relevance: {s['relevance']}")
                    if s["url"]:
                        print(f"      {s['url']}")
                continue

            if question == "/stats":
                self._load_index()
                stats = self._index.stats()
                print(f"\n📊 Papers: {stats['total']}")
                for src, cnt in stats.get("sources", {}).items():
                    print(f"   {src}: {cnt}")

                # Knowledge table stats
                if "knowledge" in get_table_names(self._index.db):
                    kt = self._index.db.open_table("knowledge")
                    kdf = kt.to_pandas()
                    print(f"\n🧠 Knowledge chunks: {len(kdf)}")
                    for src, cnt in kdf["source"].value_counts().items():
# PURPOSE: CLI entry point for chat command.
                        print(f"   {src}: {cnt}")
                continue

            if question == "/index":
                print("📝 Indexing knowledge files...", flush=True)
                added = KnowledgeIndexer.index_knowledge()
                print(f"✅ Indexed {added} new chunks")
                continue

            if question.startswith("/steering"):
                parts = question.split()
                if len(parts) == 1:
                    print(f"🧭 Current: {self.steering_profile}")
                    print(f"   Available: {', '.join(self.STEERING_PROFILES.keys())}")
                elif parts[1] in self.STEERING_PROFILES:
                    self.steering_profile = parts[1]
                    print(f"🧭 Switched to: {self.steering_profile}")
                else:
                    print(f"❌ Unknown: {parts[1]}. Available: {', '.join(self.STEERING_PROFILES.keys())}")
                continue

            # Ask
            print("🔍 Searching...", flush=True)
            result = self.ask(question)
            last_result = result

            print(f"\n💡 [{result['turn']}] Answer "
                  f"({result['generation_time']}s, "
                  f"{result['context_docs']} docs):\n")
            print(result["answer"])
            print(f"\n📚 {len(result['sources'])} sources (/sources for details)")


# PURPOSE: CLI entry point for chat command
def cmd_chat(args) -> int:
    """CLI entry point for chat command."""
    chat = GnosisChat(
        top_k=args.top_k,
        max_new_tokens=args.max_tokens,
        steering_profile=args.steering,
    )

    if args.index:
        print("📝 Indexing knowledge files...", flush=True)
        added = KnowledgeIndexer.index_knowledge()
        print(f"✅ Indexed {added} new chunks")
        if not args.question:
            return 0

    if args.question:
        result = chat.ask(args.question)
        conf_icon = {"high": "🟢", "medium": "🟡", "low": "🟠", "none": "🔴"}.get(
            result.get("confidence", ""), "⚪")
        print(f"\n{conf_icon} Confidence: {result.get('confidence', '?')}")
        print(f"\n💡 Answer:\n\n{result['answer']}")
        print(f"\n---")
        print(f"📚 Sources ({result['context_docs']} docs, "
              f"retrieval: {result['retrieval_time']}s, "
              f"generation: {result['generation_time']}s):")
        for i, s in enumerate(result["sources"], 1):
            icon = {"papers": "📄", "knowledge": "🧠"}.get(s["table"], "📁")
            d = s.get('distance', 0)
            rs = s.get('rerank_score')
            score_str = f" rs={rs:.1f}" if rs is not None else ""
            print(f"  [{i}] {icon} [{s['source']}] {s['title']} (d={d:.4f}{score_str})")
            if s["url"]:
                print(f"      {s['url']}")
        return 0
    else:
        chat.interactive()
        return 0


# PURPOSE: CLI entry point for retrieve command (no LLM)
def cmd_retrieve(args) -> int:
    """CLI entry point for retrieve command (no LLM)."""
    chat = GnosisChat(top_k=args.top_k)

    result = chat.retrieve_only(args.query)

    conf_icon = {"high": "🟢", "medium": "🟡", "low": "🟠", "none": "🔴"}.get(
        result.get("confidence", ""), "⚪")

    print(f"\n{conf_icon} Confidence: {result['confidence']} "
          f"({result['context_docs']} docs, {result['retrieval_time']}s)")

    if result["context"]:
        print(f"\n{'=' * 60}")
        print("📚 Retrieved Context")
        print(f"{'=' * 60}\n")
        print(result["context"])
        print(f"\n{'=' * 60}")

    print("\n📑 Sources:")
    for i, s in enumerate(result["sources"], 1):
        icon = {"papers": "📄", "knowledge": "🧠"}.get(s["table"], "📁")
        d = s.get("distance", 0)
        rs = s.get("rerank_score")
        score_str = f" rs={rs:.1f}" if rs is not None else ""
        print(f"  [{i}] {icon} [{s['source']}] {s['title']} (d={d:.4f}{score_str})")
        if s["url"]:
            print(f"      {s['url']}")

    return 0
