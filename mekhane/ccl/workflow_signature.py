# PROOF: [L1/定理] <- mekhane/ccl/ CCL→CCLパーサーが必要→workflow_signature が担う
"""
Workflow CCL Signature Registry

Maps workflows to their CCL signature - the algebraic essence of the workflow.
Enables macro-style reference to workflows without full procedural execution.
"""

from typing import Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
import yaml

logger = logging.getLogger(__name__)


@dataclass
class WorkflowSignature:
    """A workflow's CCL signature."""

    workflow: str  # Workflow name (e.g., "/eat")
    ccl_signature: str  # CCL representation (e.g., "/mek+_/s+_/dox+_/fit")
    description: str  # What the workflow does
    has_side_effects: bool  # Whether it has I/O or user interaction


# Core workflow signatures
WORKFLOW_SIGNATURES: Dict[str, WorkflowSignature] = {
    "/boot": WorkflowSignature(
        workflow="/boot",
        ccl_signature="/noe_/s_/dox",
        description="セッション開始: 認識→戦略→信念確認",
        has_side_effects=True,
    ),
    "/bye": WorkflowSignature(
        workflow="/bye",
        ccl_signature="/dox+_/s_/bye",
        description="セッション終了: 信念永続化→戦略→引き継ぎ",
        has_side_effects=True,
    ),
    "/eat": WorkflowSignature(
        workflow="/eat",
        ccl_signature="/mek+_/s+_/dox+_/fit",
        description="消化: 方法→戦略→信念化→検証",
        has_side_effects=True,
    ),
    "/s": WorkflowSignature(
        workflow="/s",
        ccl_signature="/noe_/bou_/zet_/ene",
        description="戦略: 認識→意志→探求→実行",
        has_side_effects=False,
    ),
    "/dia": WorkflowSignature(
        workflow="/dia",
        ccl_signature="/pat_/pis_/kri",
        description="判定: 感情→確信→判断",
        has_side_effects=False,
    ),
    "/noe": WorkflowSignature(
        workflow="/noe",
        ccl_signature="/zet^_/bou^_/noe^",
        description="深い認識: メタ探求→メタ意志→メタ認識",
        has_side_effects=False,
    ),
    "/bou": WorkflowSignature(
        workflow="/bou",
        ccl_signature="/ore_/bou_/ene",
        description="意志: 欲求→意志→実行",
        has_side_effects=False,
    ),
    "/zet": WorkflowSignature(
        workflow="/zet",
        ccl_signature="/noe_/zet_/sop",
        description="探求: 認識→探求→知恵",
        has_side_effects=True,  # May call Perplexity
    ),
    "/ene": WorkflowSignature(
        workflow="/ene",
        ccl_signature="/s_/ene_/dia",
        description="行為: 戦略→実行→判定",
        has_side_effects=True,
    ),
    "/mek": WorkflowSignature(
        workflow="/mek",
        ccl_signature="/met_/mek_/sta_/pra",
        description="方法: 尺度→方法→基準→実践",
        has_side_effects=True,
    ),
    "/dox": WorkflowSignature(
        workflow="/dox",
        ccl_signature="/pis_/dox_/epi",
        description="信念: 確信→信念→知識",
        has_side_effects=True,
    ),
    "/u": WorkflowSignature(
        workflow="/u",
        ccl_signature="/u",
        description="対話: Creatorへの問い",
        has_side_effects=True,
    ),
}


class SignatureRegistry:
    """Registry for workflow CCL signatures."""

    def __init__(self):
        """Initialize with built-in signatures."""
        self.signatures = dict(WORKFLOW_SIGNATURES)

    def get(self, workflow: str) -> Optional[WorkflowSignature]:
        """
        Get CCL signature for a workflow.

        Args:
            workflow: Workflow name (e.g., "/eat" or "eat")

        Returns:
            WorkflowSignature if found
        """
        # Normalize: ensure leading slash
        if not workflow.startswith("/"):
            workflow = f"/{workflow}"
        return self.signatures.get(workflow)

    def get_ccl(self, workflow: str) -> Optional[str]:
        """Get just the CCL signature string."""
        sig = self.get(workflow)
        return sig.ccl_signature if sig else None

    def list_pure(self) -> list:
        """List workflows without side effects (pure CCL)."""
        return [s for s in self.signatures.values() if not s.has_side_effects]

    def list_impure(self) -> list:
        """List workflows with side effects."""
        return [s for s in self.signatures.values() if s.has_side_effects]

    def add_from_yaml(self, workflow_path: Path):
        """
        Extract CCL signature from a workflow YAML frontmatter.

        Args:
            workflow_path: Path to workflow .md file
        """
        if not workflow_path.exists():
            return

        content = workflow_path.read_text()
        if not content.startswith("---"):
            return

        try:
            # Extract YAML frontmatter
            end_idx = content.find("---", 3)
            if end_idx == -1:
                return
            frontmatter = yaml.safe_load(content[3:end_idx])

            if "ccl_signature" in frontmatter:
                name = f"/{workflow_path.stem}"
                self.signatures[name] = WorkflowSignature(
                    workflow=name,
                    ccl_signature=frontmatter["ccl_signature"],
                    description=frontmatter.get("description", ""),
                    has_side_effects=frontmatter.get("has_side_effects", True),
                )
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse workflow signature from {workflow_path}: {e}")
