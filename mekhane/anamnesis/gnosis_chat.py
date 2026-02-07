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

# Hegemonikon root
_THIS_DIR = Path(__file__).parent
_HEGEMONIKON_ROOT = _THIS_DIR.parent.parent

# Knowledge source paths
MNEME_SESSIONS = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "sessions"
MNEME_KNOWLEDGE = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "knowledge"
KERNEL_DIR = _HEGEMONIKON_ROOT / "kernel"
HANDOFF_DIR = _HEGEMONIKON_ROOT / "docs" / "handoff"


class ConversationHistory:
    """マルチターン対話の履歴管理."""

    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.turns: list[dict] = []

    def add(self, role: str, content: str):
        """ターンを追加."""
        self.turns.append({"role": role, "content": content})
        # 最大ターン数を超えたら古いものを削除
        if len(self.turns) > self.max_turns * 2:
            self.turns = self.turns[-(self.max_turns * 2):]

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

    def clear(self):
        self.turns.clear()

    @property
    def turn_count(self) -> int:
        return len(self.turns) // 2


class Reranker:
    """Cross-encoder Reranker for precision improvement.

    Strategy: bi-encoder でオーバーフェッチ → cross-encoder で re-score
    → top-k に絞る。精度を大幅に向上させる。

    VRAM: ~50MB (cross-encoder-ms-marco-MiniLM-L-6-v2)
    """

    DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self._model = None

    def _load(self):
        if self._model is not None:
            return
        from sentence_transformers import CrossEncoder
        self._model = CrossEncoder(self.model_name, device="cuda")
        print(f"[Reranker] Loaded ({self.model_name})", flush=True)

    def rerank(
        self, query: str, results: list[dict], top_k: int = 5
    ) -> list[dict]:
        """検索結果を cross-encoder で再スコアリング.

        Args:
            query: 検索クエリ
            results: bi-encoder の検索結果
            top_k: 返す件数

        Returns:
            re-scored & sorted results (top_k)
        """
        if not results:
            return results

        self._load()

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

        # re-rank score でソート (高い方が良い)
        results.sort(key=lambda r: r.get("_rerank_score", -999), reverse=True)

        return results[:top_k]


class KnowledgeIndexer:
    """Hegemonikón 全知識をインデックスに追加するユーティリティ."""

    @staticmethod
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

        # 6. Kernel docs
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
    def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        """テキストをチャンクに分割 (overlap 付き)."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # 文の途中で切らないようにする
            if end < len(text):
                # 最後の改行で切る
                last_nl = chunk.rfind("\n")
                if last_nl > chunk_size // 2:
                    end = start + last_nl + 1
                    chunk = text[start:end]

            chunks.append(chunk.strip())
            start = end - overlap

        return [c for c in chunks if c]

    @staticmethod
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

        if not force_reindex and table_name in index.db.table_names():
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
            texts = [d["content"][:512] for d in batch]
            vectors = embedder.embed_batch(texts)

            for d, v in zip(batch, vectors):
                d["vector"] = v

            done = min(i + BATCH_SIZE, len(data))
            print(f"  Embedded {done}/{len(data)}...", flush=True)

        # LanceDB に追加
        if table_name in index.db.table_names():
            table = index.db.open_table(table_name)
            table.add(data)
        else:
            index.db.create_table(table_name, data=data)

        print(f"[Knowledge] Added {len(data)} chunks (skipped {skipped})")
        return len(data)


class GnosisChat:
    """Gnōsis 対話型 RAG エンジン.

    NotebookLM のように、自分のデータに基づいて対話する。
    完全ローカル (オフライン動作可能)。
    """

    # Qwen 3B (4bit) — 品質とVRAMのバランス
    DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"

    def __init__(
        self,
        model_id: Optional[str] = None,
        top_k: int = 5,
        max_new_tokens: int = 512,
        search_knowledge: bool = True,
        search_papers: bool = True,
        use_reranker: bool = True,
    ):
        self.model_id = model_id or self.DEFAULT_MODEL
        self.top_k = top_k
        self.max_new_tokens = max_new_tokens
        self.search_knowledge = search_knowledge
        self.search_papers = search_papers
        self.use_reranker = use_reranker

        self._index = None
        self._model = None
        self._tokenizer = None
        self._reranker = Reranker() if use_reranker else None
        self.history = ConversationHistory(max_turns=5)

    def _load_index(self):
        """Gnōsis インデックスをロード (GPU embedding)."""
        if self._index is not None:
            return
        from mekhane.anamnesis.index import GnosisIndex
        self._index = GnosisIndex()
        print("[Gnōsis Chat] Index loaded", flush=True)

    def _load_model(self):
        """LLM をロード (4bit量子化 on GPU)."""
        if self._model is not None:
            return

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

    def _retrieve(self, query: str) -> list[dict]:
        """全テーブルからセマンティック検索 + rerank.

        Strategy:
          1. bi-encoder で 3x オーバーフェッチ
          2. cross-encoder で re-score
          3. top-k に絞る
        """
        self._load_index()
        results = []

        # reranker 使用時は 3x オーバーフェッチ
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
                if "knowledge" in self._index.db.table_names():
                    embedder = self._index._get_embedder()
                    qvec = embedder.embed(query)
                    table = self._index.db.open_table("knowledge")
                    k_results = table.search(qvec).limit(fetch_k).to_list()
                    for r in k_results:
                        r["_source_table"] = "knowledge"
                    results.extend(k_results)
            except Exception:
                pass

        # _distance でソート (低い方が類似度が高い)
        results.sort(key=lambda r: r.get("_distance", 999))

        # Reranker で精度向上
        if self._reranker and results:
            results = self._reranker.rerank(query, results, top_k=self.top_k)
        else:
            results = results[:self.top_k]

        return results

    def _build_context(self, results: list[dict]) -> str:
        """検索結果からコンテキスト文字列を構築."""
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

            context_parts.append(
                f"[{i}] [{source}] {title}\n"
                f"    Relevance: {1 - dist:.2f}\n"
                f"    {content}"
            )
        return "\n\n".join(context_parts)

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

    def ask(self, question: str) -> dict:
        """質問に回答する (RAG + マルチターン).

        Returns:
            dict with keys: answer, sources, retrieval_time, generation_time
        """
        # 1. Retrieve
        t0 = time.time()
        results = self._retrieve(question)
        retrieval_time = time.time() - t0

        # 2. Build context
        context = self._build_context(results)

        # 3. System prompt
        system_prompt = (
            "あなたは Hegemonikón の知識ベース対話アシスタントです。\n"
            "以下の検索結果に基づいて、ユーザーの質問に日本語で正確に回答してください。\n"
            "検索結果に含まれない情報については、その旨を明示してください。\n"
            "回答は簡潔で構造的にしてください。\n"
            "引用する場合は [番号] の形式で参照元を示してください。"
        )

        # 4. Build prompt with history
        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n"

        # 過去の会話履歴を追加
        history_text = self.history.format_for_prompt()
        if history_text:
            prompt += history_text + "\n"

        # 現在の質問 + コンテキスト
        prompt += (
            f"<|im_start|>user\n"
            f"## 検索結果 (関連文書)\n\n{context}\n\n"
            f"## 質問\n{question}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        # 5. Generate
        t0 = time.time()
        answer = self._generate(prompt)
        generation_time = time.time() - t0

        # 6. 履歴に追加
        self.history.add("user", question)
        self.history.add("assistant", answer.strip())

        # 7. Format sources
        sources = []
        for r in results:
            sources.append({
                "title": r.get("title", "Untitled")[:80],
                "source": r.get("source", "unknown"),
                "table": r.get("_source_table", "unknown"),
                "url": r.get("url", ""),
                "relevance": round(1 - r.get("_distance", 0), 2),
            })

        return {
            "answer": answer.strip(),
            "sources": sources,
            "retrieval_time": round(retrieval_time, 3),
            "generation_time": round(generation_time, 1),
            "context_docs": len(results),
            "turn": self.history.turn_count,
        }

    def interactive(self):
        """対話ループ (REPL)."""
        print("\n" + "=" * 60)
        print("  Gnōsis Chat — Hegemonikón ローカル知識ベース対話")
        print(f"  Model: {self.model_id}")
        print("  Commands: /quit, /sources, /stats, /clear, /index")
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
                if "knowledge" in self._index.db.table_names():
                    kt = self._index.db.open_table("knowledge")
                    kdf = kt.to_pandas()
                    print(f"\n🧠 Knowledge chunks: {len(kdf)}")
                    for src, cnt in kdf["source"].value_counts().items():
                        print(f"   {src}: {cnt}")
                continue

            if question == "/index":
                print("📝 Indexing knowledge files...", flush=True)
                added = KnowledgeIndexer.index_knowledge()
                print(f"✅ Indexed {added} new chunks")
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


def cmd_chat(args) -> int:
    """CLI entry point for chat command."""
    chat = GnosisChat(
        top_k=args.top_k,
        max_new_tokens=args.max_tokens,
    )

    if args.index:
        print("📝 Indexing knowledge files...", flush=True)
        added = KnowledgeIndexer.index_knowledge()
        print(f"✅ Indexed {added} new chunks")
        if not args.question:
            return 0

    if args.question:
        # Single question mode
        result = chat.ask(args.question)
        print(f"\n💡 Answer:\n\n{result['answer']}")
        print(f"\n---")
        print(f"📚 Sources ({result['context_docs']} docs, "
              f"retrieval: {result['retrieval_time']}s, "
              f"generation: {result['generation_time']}s):")
        for i, s in enumerate(result["sources"], 1):
            icon = {"papers": "📄", "knowledge": "🧠"}.get(s["table"], "📁")
            print(f"  [{i}] {icon} [{s['source']}] {s['title']}")
            if s["url"]:
                print(f"      {s['url']}")
        return 0
    else:
        # Interactive mode
        chat.interactive()
        return 0
