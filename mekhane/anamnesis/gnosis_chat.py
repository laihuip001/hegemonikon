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
  Query → GPU Embedding (BGE-small) → LanceDB → Top-K → Qwen 1.5B → Answer

VRAM Budget:
  BGE-small embedding: ~133MB
  Qwen 2.5 1.5B (4bit): ~1.2GB
  Total: ~1.4GB / 8GB RTX 2070 SUPER
"""

import sys
import time
from pathlib import Path
from typing import Optional

# Hegemonikon root
_THIS_DIR = Path(__file__).parent
_HEGEMONIKON_ROOT = _THIS_DIR.parent.parent


class GnosisChat:
    """Gnōsis 対話型 RAG エンジン.

    NotebookLM のように、自分のデータに基づいて対話する。
    完全ローカル (オフライン動作可能)。
    """

    def __init__(
        self,
        model_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
        top_k: int = 5,
        max_new_tokens: int = 512,
    ):
        self.model_id = model_id
        self.top_k = top_k
        self.max_new_tokens = max_new_tokens

        self._index = None
        self._model = None
        self._tokenizer = None

    def _load_index(self):
        """Gnōsis インデックスをロード (GPU embedding)."""
        if self._index is not None:
            return
        from mekhane.anamnesis.index import GnosisIndex
        self._index = GnosisIndex()
        print("[Gnōsis Chat] Index loaded", flush=True)

    def _load_model(self):
        """Qwen 1.5B をロード (4bit量子化 on GPU)."""
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

        import torch
        vram_mb = torch.cuda.memory_allocated() / 1e6
        print(f"[Gnōsis Chat] Model loaded ({vram_mb:.0f}MB VRAM)", flush=True)

    def _retrieve(self, query: str) -> list[dict]:
        """セマンティック検索で関連文書を取得."""
        self._load_index()
        return self._index.search(query, k=self.top_k)

    def _build_context(self, results: list[dict]) -> str:
        """検索結果からコンテキスト文字列を構築."""
        context_parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            abstract = r.get("abstract", "")[:500]
            authors = r.get("authors", "")[:100]
            source = r.get("source", "unknown")
            context_parts.append(
                f"[{i}] {title}\n"
                f"    Authors: {authors}\n"
                f"    Source: {source}\n"
                f"    {abstract}"
            )
        return "\n\n".join(context_parts)

    def _generate(self, prompt: str) -> str:
        """LLM で回答を生成."""
        import torch

        self._load_model()

        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)

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
        """質問に回答する (RAG).

        Returns:
            dict with keys: answer, sources, retrieval_time, generation_time
        """
        # 1. Retrieve
        t0 = time.time()
        results = self._retrieve(question)
        retrieval_time = time.time() - t0

        # 2. Build context
        context = self._build_context(results)

        # 3. Generate with context
        system_prompt = (
            "あなたは Gnōsis 知識ベースの対話アシスタントです。\n"
            "以下の検索結果に基づいて、ユーザーの質問に日本語で正確に回答してください。\n"
            "検索結果に含まれない情報については、その旨を明示してください。\n"
            "回答は簡潔で構造的にしてください。"
        )

        prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n"
            f"## 検索結果 (関連文書)\n\n{context}\n\n"
            f"## 質問\n{question}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        t0 = time.time()
        answer = self._generate(prompt)
        generation_time = time.time() - t0

        # 4. Format sources
        sources = []
        for r in results:
            sources.append({
                "title": r.get("title", "Untitled")[:80],
                "source": r.get("source", "unknown"),
                "url": r.get("url", ""),
            })

        return {
            "answer": answer.strip(),
            "sources": sources,
            "retrieval_time": round(retrieval_time, 3),
            "generation_time": round(generation_time, 1),
            "context_docs": len(results),
        }

    def interactive(self):
        """対話ループ (REPL)."""
        print("\n" + "=" * 60)
        print("  Gnōsis Chat — ローカル知識ベース対話")
        print("  Model: " + self.model_id)
        print("  Commands: /quit, /sources, /stats")
        print("=" * 60)

        last_result = None

        while True:
            try:
                question = input("\n❓ ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye.")
                break

            if not question:
                continue

            if question in ("/quit", "/q", "/exit"):
                print("bye.")
                break

            if question == "/sources" and last_result:
                print("\n📚 Sources:")
                for i, s in enumerate(last_result["sources"], 1):
                    print(f"  [{i}] {s['title']}")
                    if s["url"]:
                        print(f"      {s['url']}")
                continue

            if question == "/stats":
                self._load_index()
                stats = self._index.stats()
                print(f"\n📊 Total papers: {stats['total']}")
                for src, cnt in stats.get("sources", {}).items():
                    print(f"   {src}: {cnt}")
                continue

            # Ask
            print("🔍 Searching...", flush=True)
            result = self.ask(question)
            last_result = result

            print(f"\n💡 Answer ({result['generation_time']}s, "
                  f"{result['context_docs']} docs):\n")
            print(result["answer"])
            print(f"\n📚 {len(result['sources'])} sources (type /sources for details)")


def cmd_chat(args) -> int:
    """CLI entry point for chat command."""
    chat = GnosisChat(
        top_k=args.top_k,
        max_new_tokens=args.max_tokens,
    )

    if args.question:
        # Single question mode
        result = chat.ask(args.question)
        print(f"\n💡 Answer:\n\n{result['answer']}")
        print(f"\n---")
        print(f"📚 Sources ({result['context_docs']} docs, "
              f"retrieval: {result['retrieval_time']}s, "
              f"generation: {result['generation_time']}s):")
        for i, s in enumerate(result["sources"], 1):
            print(f"  [{i}] {s['title']}")
            if s["url"]:
                print(f"      {s['url']}")
        return 0
    else:
        # Interactive mode
        chat.interactive()
        return 0
