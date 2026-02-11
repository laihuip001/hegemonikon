# PROOF: [L2/インフラ] <- mekhane/anamnesis/models/ A0→Libraryプロンプトのスキーマが必要→prompt_moduleが担う
"""
Gnōsis Prompt Module Model - Library プロンプト統一スキーマ

PURPOSE: Library 112ファイルのセマンティック検索を可能にする
PATTERN: Paper モデルと同じ dataclass → LanceDB dict パターン
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# PURPOSE: の統一的インターフェースを実現する
@dataclass
# PURPOSE: Library プロンプトモジュール統一スキーマ
class PromptModule:
    """Library プロンプトモジュール統一スキーマ"""

    # Identity
    id: str                              # prompt_{category}_{name_slug}
    filepath: str                        # 相対パス (Library root から)

    # Core metadata
    name: str = ""
    category: str = ""                   # modules, dev, forge, system-instructions
    origin: str = "Brain Vault (pre-FEP)"

    # Hegemonikón mapping
    hegemonikon_mapping: str = ""        # HGK WF/Skill 対応
    model_target: str = "universal"

    # Activation
    activation_triggers: list[str] = field(default_factory=list)
    essence: str = ""                    # 核心3-5行

    # Full content
    body: str = ""                       # プロンプト本文 (最大 2000 chars)

    # Metadata
    indexed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # PURPOSE: prompt_module の primary key 処理を実行する
    @property
    # PURPOSE: 重複排除用
    def primary_key(self) -> str:
        """重複排除用"""
        return self.filepath

    # PURPOSE: prompt_module の embedding text 処理を実行する
    @property
    # PURPOSE: 埋め込み生成用テキスト
    def embedding_text(self) -> str:
        """埋め込み生成用テキスト"""
        parts = [self.name, self.category, self.hegemonikon_mapping]
        parts.extend(self.activation_triggers)
        if self.essence:
            parts.append(self.essence[:500])
        if self.body:
            parts.append(self.body[:500])
        return " ".join(p for p in parts if p)

    # PURPOSE: LanceDB 保存用辞書
    def to_dict(self) -> dict:
        """LanceDB 保存用辞書"""
        return {
            "id": self.id,
            "primary_key": self.primary_key,
            "filepath": self.filepath,
            "name": self.name,
            "category": self.category,
            "origin": self.origin,
            "hegemonikon_mapping": self.hegemonikon_mapping,
            "model_target": self.model_target,
            "activation_triggers": ", ".join(self.activation_triggers),
            "essence": self.essence[:1000],
            "body": self.body[:2000],
            "indexed_at": self.indexed_at,
        }

    # PURPOSE: prompt_module の from dict 処理を実行する
    @classmethod
    # PURPOSE: 辞書から復元
    def from_dict(cls, data: dict) -> "PromptModule":
        """辞書から復元"""
        return cls(
            id=data["id"],
            filepath=data["filepath"],
            name=data.get("name", ""),
            category=data.get("category", ""),
            origin=data.get("origin", ""),
            hegemonikon_mapping=data.get("hegemonikon_mapping", ""),
            model_target=data.get("model_target", "universal"),
            activation_triggers=data.get("activation_triggers", "").split(", ")
                if data.get("activation_triggers") else [],
            essence=data.get("essence", ""),
            body=data.get("body", ""),
            indexed_at=data.get("indexed_at", datetime.now().isoformat()),
        )
