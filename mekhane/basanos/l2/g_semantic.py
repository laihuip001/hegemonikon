# PROOF: [L2/テスト] <- mekhane/basanos/ L2レベルのセマンティック/構造的品質検証が必要
# PURPOSE: G_semantic — LLM で HGK 専門用語を一般学術用語に翻訳する
# REASON: G = G_struct ∘ G_semantic の G_semantic 部分。外部比較のために HGK 語彙を汎化する
"""G_semantic: LLM-based translation of HGK terms to general academic terms.

Uses Gemini API (via ochema/cortex) to translate HGK-specific vocabulary
(e.g., "Noēsis", "Boulēsis", "FEP prediction error") into standard
academic terminology for external comparison.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import replace
from pathlib import Path
from typing import Optional

from mekhane.basanos.l2.models import ExternalForm


# HGK → General mapping (static, manually curated for common terms)
STATIC_TRANSLATIONS: dict[str, str] = {
    # Series names
    "Ousia": "essence / core cognitive functions",
    "Schema": "strategic patterns / operational modes",
    "Hormē": "motivational drives / impulse tendencies",
    "Perigraphē": "contextual constraints / boundary conditions",
    "Kairos": "temporal context / situational timing",
    "Akribeia": "precision / rigorous evaluation",
    # Theorem names
    "Noēsis": "deep reasoning / intuitive cognition",
    "Boulēsis": "goal-directed intention / volition",
    "Zētēsis": "inquiry / exploratory search",
    "Energeia": "actualization / task execution",
    "Mekhanē": "method design / tooling",
    "Diairesis": "analytical decomposition",
    "Praxis": "practical implementation",
    "Propatheia": "pre-reflective affect / gut feeling",
    "Pistis": "confidence assessment / belief strength",
    "Orexis": "desire / value orientation",
    "Doxa": "belief / opinion persistence",
    "Krisis": "critical judgment / evaluation",
    "Epistēmē": "verified knowledge / justified true belief",
    "Sophia": "wisdom / deep research",
    "Chronos": "temporal tracking / version history",
    # FEP terms
    "FEP": "Free Energy Principle",
    "variational free energy": "variational free energy (Bayesian inference bound)",
    "expected free energy": "expected free energy (action selection objective)",
    "prediction error": "prediction error (surprise signal)",
    "active inference": "active inference (perception-action loop)",
    "precision": "precision (inverse variance / confidence weighting)",
    # HGK-specific
    "CCL": "Cognitive Control Language (domain-specific workflow notation)",
    "trigonon": "triangular relation structure (adjunction + natural transformation + duality)",
    "Hegemonikón": "cognitive hypervisor framework",
    "kernel/": "core axiom and theorem definitions",
    "mekhane/": "implementation layer",
}


class GSemantic:
    """Translate HGK-specific terms to general academic vocabulary.

    Operates in two modes:
    1. Static: Use curated STATIC_TRANSLATIONS dictionary (fast, deterministic)
    2. Dynamic: Use Gemini API for unknown terms (slower, more flexible)
    """

    def __init__(self, use_llm: bool = False) -> None:
        """Initialize GSemantic.

        Args:
            use_llm: If True, use Gemini API for terms not in static dict.
                     If False, only use static translations.
        """
        self.use_llm = use_llm

    def translate(self, external_form: ExternalForm) -> ExternalForm:
        """Translate HGK terms in ExternalForm to general terms.

        Returns a new ExternalForm with translated keywords/claims.
        """
        translated_keywords = []
        for kw in external_form.keywords:
            translated = self._translate_term(kw)
            translated_keywords.append(translated)
            if translated != kw:
                translated_keywords.append(kw)  # Keep original too

        translated_claims = [self._translate_term(c) for c in external_form.claims]

        return replace(
            external_form,
            keywords=list(set(translated_keywords)),
            claims=translated_claims,
        )

    def _translate_term(self, term: str) -> str:
        """Translate a single term."""
        # Try static translation first
        for hgk_term, general_term in STATIC_TRANSLATIONS.items():
            if hgk_term.lower() in term.lower():
                return term.replace(hgk_term, general_term)

        # If LLM mode enabled and no static match, try dynamic
        if self.use_llm:
            result = self._llm_translate(term)
            if result:
                return result

        return term  # Return unchanged if no translation found

    def _llm_translate(self, term: str) -> Optional[str]:
        """Use Gemini to translate an HGK-specific term."""
        prompt = (
            f"以下の Hegemonikón (認知フレームワーク) の専門用語を、"
            f"一般的な認知科学・AI 研究の用語に翻訳してください。\n"
            f"用語: {term}\n"
            f"翻訳結果のみを返してください（説明不要）。"
        )
        try:
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"from mekhane.ochema.cortex_client import CortexClient; "
                    f"c = CortexClient(); "
                    f"r = c.ask('{prompt}', model='gemini-2.0-flash'); "
                    f"print(r.text)",
                ],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(Path(__file__).resolve().parents[3]),
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, OSError):
            pass
        return None
