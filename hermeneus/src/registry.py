# PROOF: [L2/インフラ] Workflow Registry
"""
Hermēneus Registry — ワークフロー定義管理

.agent/workflows/ からワークフロー定義をロードし、
CCL 実行に必要なメタデータを提供する。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from functools import lru_cache


# =============================================================================
# Types
# =============================================================================

@dataclass
class WorkflowStage:
    """ワークフローステージ"""
    name: str
    description: str = ""
    substages: List[str] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    """ワークフロー定義"""
    name: str                           # 例: "noe", "bou", "ene"
    ccl: str                            # 例: "/noe+", "/bou+"
    description: str                    # 説明
    stages: List[WorkflowStage] = field(default_factory=list)
    modes: List[str] = field(default_factory=list)  # 派生モード
    output_format: str = "markdown"     # 出力形式
    source_path: Optional[Path] = None  # 元ファイルパス
    raw_content: str = ""               # 生のマークダウン内容
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_prompt_template(self) -> str:
        """プロンプトテンプレートを生成"""
        template = f"# {self.description}\n\n"
        
        for stage in self.stages:
            template += f"## {stage.name}\n"
            if stage.description:
                template += f"{stage.description}\n"
            for sub in stage.substages:
                template += f"- {sub}\n"
            template += "\n"
        
        return template


# =============================================================================
# Parser
# =============================================================================

class WorkflowParser:
    """ワークフロー Markdown パーサー"""
    
    FRONTMATTER_PATTERN = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n",
        re.DOTALL
    )
    STAGE_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    MODE_PATTERN = re.compile(r"^###\s+--mode=(\w+)", re.MULTILINE)
    
    def parse(self, path: Path) -> WorkflowDefinition:
        """ワークフローファイルをパース"""
        content = path.read_text(encoding="utf-8")
        
        # フロントマター抽出
        metadata = {}
        body = content
        
        fm_match = self.FRONTMATTER_PATTERN.match(content)
        if fm_match:
            try:
                metadata = yaml.safe_load(fm_match.group(1)) or {}
            except yaml.YAMLError:
                metadata = {}
            body = content[fm_match.end():]
        
        # ワークフロー名を推定 (ファイル名から)
        name = path.stem  # 例: noe.md → noe
        ccl = f"/{name}+"
        
        # 説明を抽出
        description = metadata.get("description", "")
        if not description:
            # 最初の見出しから取得
            h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            if h1_match:
                description = h1_match.group(1)
        
        # ステージを抽出
        stages = self._parse_stages(body)
        
        # モードを抽出
        modes = self.MODE_PATTERN.findall(body)
        
        return WorkflowDefinition(
            name=name,
            ccl=ccl,
            description=description,
            stages=stages,
            modes=modes,
            source_path=path,
            raw_content=content,
            metadata=metadata
        )
    
    def _parse_stages(self, content: str) -> List[WorkflowStage]:
        """ステージをパース"""
        stages = []
        
        # ## で区切る
        parts = re.split(r"^##\s+", content, flags=re.MULTILINE)
        
        for part in parts[1:]:  # 最初は空またはヘッダー前
            lines = part.strip().split("\n")
            if not lines:
                continue
            
            stage_name = lines[0].strip()
            
            # サブステージ (箇条書き) を抽出
            substages = []
            description_lines = []
            
            for line in lines[1:]:
                if line.strip().startswith("- "):
                    substages.append(line.strip()[2:])
                elif line.strip().startswith("###"):
                    break  # モード定義に入ったら終了
                elif line.strip():
                    description_lines.append(line.strip())
            
            stages.append(WorkflowStage(
                name=stage_name,
                description=" ".join(description_lines[:3]),  # 最初の3行
                substages=substages[:10]  # 最大10個
            ))
        
        return stages


# =============================================================================
# Registry
# =============================================================================

class WorkflowRegistry:
    """ワークフローレジストリ
    
    .agent/workflows/ からワークフロー定義をロードし管理する。
    """
    
    DEFAULT_PATHS = [
        Path.home() / "oikos" / ".agent" / "workflows",
        Path.home() / "oikos" / "hegemonikon" / ".agent" / "workflows",
    ]
    
    def __init__(
        self,
        workflows_dir: Optional[Path] = None,
        search_paths: Optional[List[Path]] = None
    ):
        self.search_paths = search_paths or []
        
        if workflows_dir:
            self.search_paths.insert(0, workflows_dir)
        
        # デフォルトパスを追加
        for default in self.DEFAULT_PATHS:
            if default.exists() and default not in self.search_paths:
                self.search_paths.append(default)
        
        self.parser = WorkflowParser()
        self._cache: Dict[str, WorkflowDefinition] = {}
    
    def get(self, name: str) -> Optional[WorkflowDefinition]:
        """ワークフロー定義を取得
        
        Args:
            name: ワークフロー名 (例: "noe", "bou", "/noe+")
            
        Returns:
            WorkflowDefinition or None
        """
        # 正規化
        clean_name = self._normalize_name(name)
        
        # キャッシュチェック
        if clean_name in self._cache:
            return self._cache[clean_name]
        
        # ファイル検索
        for search_path in self.search_paths:
            path = search_path / f"{clean_name}.md"
            if path.exists():
                wf = self.parser.parse(path)
                self._cache[clean_name] = wf
                return wf
        
        return None
    
    def load_all(self) -> Dict[str, WorkflowDefinition]:
        """全ワークフローをロード"""
        result = {}
        
        for search_path in self.search_paths:
            if not search_path.exists():
                continue
            
            for path in search_path.glob("*.md"):
                if path.name.startswith("_"):
                    continue  # _ で始まるファイルはスキップ
                
                name = path.stem
                if name not in result:
                    try:
                        result[name] = self.parser.parse(path)
                    except Exception:
                        continue  # パース失敗はスキップ
        
        self._cache.update(result)
        return result
    
    def list_names(self) -> List[str]:
        """ワークフロー名一覧を取得"""
        names = set()
        
        for search_path in self.search_paths:
            if search_path.exists():
                for path in search_path.glob("*.md"):
                    if not path.name.startswith("_"):
                        names.add(path.stem)
        
        return sorted(names)
    
    def _normalize_name(self, name: str) -> str:
        """名前を正規化"""
        # /noe+ → noe
        name = name.strip()
        name = name.lstrip("/")
        name = name.rstrip("+")
        name = name.rstrip("-")
        return name
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self._cache.clear()


# =============================================================================
# Convenience Functions
# =============================================================================

@lru_cache(maxsize=1)
def get_default_registry() -> WorkflowRegistry:
    """デフォルトレジストリを取得"""
    return WorkflowRegistry()


def get_workflow(name: str) -> Optional[WorkflowDefinition]:
    """ワークフロー定義を取得 (便利関数)"""
    return get_default_registry().get(name)


def list_workflows() -> List[str]:
    """ワークフロー一覧を取得 (便利関数)"""
    return get_default_registry().list_names()
