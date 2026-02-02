# PROOF: [L2/インフラ] <- mekhane/poiema/flow/ O4→創造機能が必要
"""
Epochē Shield — A2 Krisis (Epochē) Instantiation

Philosophical Reference:
    A2 Krisis (判定力): 判断を下す能力
    Epochē (判断停止): 判断を一時保留し、安全側に倒す

Design Principle:
    外部API送信前にPIIをマスク → 判断を「保留」した状態で通信
    レスポンス後にアンマスク → 判断を「再開」
    = Zero Trust Privacy の哲学的実装

Original: Flow AI v4.1 PrivacyHandler, PrivacyScanner
Recast: Hegemonikón A2 Krisis (Epochē) vocabulary
"""

import re
from typing import Dict, List, Tuple, Optional


class EpocheScanner:
    """
    A2 Krisis の偵察機能: リスク検知

    Philosophical Reference:
        判断を下す前に「何を判断すべきか」を明確にする
        = リスクの可視化
    """

    def __init__(self):
        # PII検知パターン（A2 Krisis の「判断基準」）
        self.patterns = {
            # 基本PII
            "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "PHONE": r"\d{2,4}-\d{2,4}-\d{3,4}",
            "ZIP": r"〒?\d{3}-\d{4}",
            "MY_NUMBER": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}",
            # 拡張パターン
            "IP_ADDRESS": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            "CREDIT_CARD": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}",
            # API Keys
            "API_KEY": r"(?:sk-|pk_|AIza|ghp_|gsk_|glpat-|xox[baprs]-|Bearer\s+)[a-zA-Z0-9_-]{20,}",
            "AWS_KEY": r"AKIA[0-9A-Z]{16}",
            # パスワード系
            "PASSWORD": r"(?i)(?:password|passwd|pwd|secret|token)\s*[=:]\s*['\"]?[^\s'\"]{8,}",
            # 日本住所
            "JP_ADDRESS": r"(?:東京都|北海道|(?:京都|大阪)府|[^\s]{2,3}県)[^\s]{2,}[市区町村]",
        }

        # 機密キーワード（H3 Orexis: 保護すべき欲求）
        self.sensitive_keywords = [
            "CONFIDENTIAL",
            "NDA",
            "INTERNAL ONLY",
            "機密",
            "社外秘",
            "SECRET",
            "PRIVATE",
            "DO NOT SHARE",
            "取扱注意",
        ]

    def scan(self, text: str) -> Dict:
        """
        リスクスキャン: PIIとセンシティブキーワードを検出

        Philosophical Reference:
            O3 Zētēsis (探求): 何が問題かを探し出す
        """
        findings = {}

        # Regex パターンマッチ
        for p_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[p_type] = list(set(matches))

        # キーワードマッチ
        text_upper = text.upper()
        keyword_hits = [
            kw for kw in self.sensitive_keywords if kw.upper() in text_upper
        ]
        if keyword_hits:
            findings["SENSITIVE_KEYWORD"] = keyword_hits

        count = sum(len(v) for v in findings.values())
        return {"has_risks": count > 0, "risks": findings, "risk_count": count}

    def check_deny_list(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        厳格な拒否リストチェック

        Philosophical Reference:
            A2 Krisis の最終防衛ライン
            これに引っかかったら即座にEpochē発動
        """
        text_upper = text.upper()
        for kw in self.sensitive_keywords:
            if kw.upper() in text_upper:
                return True, kw
        return False, None


class EpocheShield:
    """
    A2 Krisis (Epochē) の防御機能: PIIマスキング

    Philosophical Reference:
        Epochē = 判断停止
        外部に送信する前に、判断を「保留」した状態にする
        = PIIをプレースホルダに置換

        レスポンス後、判断を「再開」
        = プレースホルダを元の値に復元

    Design Principle:
        「判断を保留した状態で外部と通信する」
        これにより、外部が判断材料（PII）を得ることを防ぐ
    """

    def __init__(self):
        self.scanner = EpocheScanner()

    def mask(
        self, text: str, use_custom_vocab: bool = True
    ) -> Tuple[str, Dict[str, str]]:
        """
        Epochē 発動: PIIをプレースホルダに置換

        Philosophical Reference:
            判断を保留 → 外部に送信可能な状態にする

        Args:
            text: 入力テキスト
            use_custom_vocab: カスタム語彙も使用するか

        Returns:
            (masked_text, mapping): マスク済みテキストと復元用マッピング
        """
        findings = self.scanner.scan(text)

        masked_text = text
        mapping = {}
        counter = 0

        # Regexベースのマスク
        if findings["has_risks"]:
            for pii_type, values in findings["risks"].items():
                for val in values:
                    if val in masked_text:
                        placeholder = f"[EPOCHE_{counter}]"
                        masked_text = masked_text.replace(val, placeholder)
                        mapping[placeholder] = val
                        counter += 1

        # カスタム語彙ベースのマスク（オプション）
        if use_custom_vocab:
            try:
                from .vocab_store import get_vocab_store

                store = get_vocab_store()
                custom_terms = store.find_in_text(masked_text)
                for term in custom_terms:
                    if term in masked_text:
                        placeholder = f"[VOCAB_{counter}]"
                        masked_text = masked_text.replace(term, placeholder)
                        mapping[placeholder] = term
                        counter += 1
            except Exception:
                pass  # TODO: Add proper error handling

        return masked_text, mapping

    def unmask(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Epochē 解除: プレースホルダを元のPIIに復元

        Philosophical Reference:
            判断を再開 → 外部からのレスポンスを元の文脈に戻す
        """
        result = text
        for placeholder, original in mapping.items():
            result = result.replace(placeholder, original)
        return result


# Backward compatibility aliases
PrivacyScanner = EpocheScanner
PrivacyHandler = EpocheShield


def mask_pii(text: str, use_custom_vocab: bool = True) -> Tuple[str, Dict[str, str]]:
    """Backward compatibility function"""
    return EpocheShield().mask(text, use_custom_vocab)


def unmask_pii(text: str, mapping: Dict[str, str]) -> str:
    """Backward compatibility function"""
    return EpocheShield().unmask(text, mapping)
