#!/usr/bin/env python3
# PROOF: [L2/アプリケーション] <- mekhane/symploke/ A0→レビュー戦略が必要→synedrion_reviewer が担う
"""
Synedrion Reviewer - Hegemonikón Specialist Review Orchestrator

Separated from JulesClient (TH-003, TH-009, ES-009, AI-011 fixes).
This module handles the domain-specific review strategy logic,
while JulesClient remains a pure API transport layer.

Usage:
    from mekhane.symploke.synedrion_reviewer import SynedrionReviewer, run_review
    
    reviewer = SynedrionReviewer(client)
    results = await reviewer.review(source="owner/repo")
"""

import logging
from typing import Optional

from mekhane.symploke.jules_client import JulesClient, JulesResult

logger = logging.getLogger(__name__)


# PURPOSE: Synedrion v2.1 review orchestrator
class SynedrionReviewer:
    """
    Synedrion v2.1 review orchestrator.
    
    Purpose: Separate review strategy (application layer) from
    API transport (infrastructure layer) per SRP principle.
    
    TH-003, TH-009, ES-009, AI-011 fixes.
    """
    
    def __init__(
        self,
        client: JulesClient,
        batch_size: Optional[int] = None,
    ):
        """
        Initialize reviewer with a JulesClient instance.
        
        Args:
            client: JulesClient instance for API communication
            batch_size: Override batch size (default: client.MAX_CONCURRENT)
        """
        self.client = client
        self.batch_size = batch_size or client.MAX_CONCURRENT
    
    # PURPOSE: Execute Synedrion v2.1 multi-perspective review
    async def review(
        self,
        source: str,
        branch: str = "master",
        domains: Optional[list[str]] = None,
        axes: Optional[list[str]] = None,
        progress_callback: Optional[callable] = None,
    ) -> list[JulesResult]:
        """
        Execute Synedrion v2.1 multi-perspective review.
        
        This orchestrates the 480 orthogonal perspectives from the
        Hegemonikón theorem grid across multiple batches.
        
        Args:
            source: GitHub repository source (e.g., "sources/github/owner/repo")
            branch: Starting branch for review
            domains: Optional list of domains to filter (e.g., ["Security", "Ethics"])
            axes: Optional list of axes to filter (e.g., ["O1", "A2"])
            progress_callback: Optional callback(batch_num, total_batches, completed)
        
        Returns:
            List of JulesResult objects from all perspectives
        """
        # Import perspective matrix (application layer dependency)
        try:
            from mekhane.ergasterion.synedrion import PerspectiveMatrix
        except ImportError:
            raise ImportError(
                "Synedrion module not found. Ensure mekhane.ergasterion.synedrion is installed."
            )
        
        # Load perspective matrix
        matrix = PerspectiveMatrix.load()
        perspectives = matrix.all_perspectives()
        
        # Apply domain filter
        if domains:
            perspectives = [p for p in perspectives if p.domain_id in domains]
            logger.info(
                f"Filtered to domains: {domains} ({len(perspectives)} perspectives)"
            )
        
        # Apply axis filter
        if axes:
            perspectives = [p for p in perspectives if p.axis_id in axes]
            logger.info(f"Filtered to axes: {axes} ({len(perspectives)} perspectives)")
        
        if not perspectives:
            logger.warning(
                "No perspectives match the filters. Returning empty results."
            )
            return []
        
        # Generate tasks from perspectives
        tasks = [
            {
                "prompt": matrix.generate_prompt(p),
                "source": source,
                "branch": branch,
                "perspective_id": p.id,
                "perspective_name": p.name,
                "theorem": p.theorem,
            }
            for p in perspectives
        ]
        
        # Calculate batches
        total_batches = (len(tasks) + self.batch_size - 1) // self.batch_size
        
        logger.info(
            f"Starting Synedrion v2.1 review: "
            f"{len(tasks)} perspectives, {total_batches} batches"
        )
        
        # Execute and track progress
        all_results = []
        for batch_num, i in enumerate(range(0, len(tasks), self.batch_size), 1):
            batch_tasks = tasks[i : i + self.batch_size]
            
            logger.info(
                f"Batch {batch_num}/{total_batches}: {len(batch_tasks)} perspectives"
            )
            
            batch_results = await self.client.batch_execute(batch_tasks)
            all_results.extend(batch_results)
            
            # Progress callback if provided
            if progress_callback:
                progress_callback(batch_num, total_batches, len(all_results))
        
        # Log summary
        succeeded = sum(1 for r in all_results if r.is_success)
        failed = len(all_results) - succeeded
        silent = sum(
            1 for r in all_results 
            if r.is_success and r.session.output and "SILENCE" in r.session.output
        )
        
        logger.info(
            f"Synedrion review complete: "
            f"{succeeded} succeeded, {failed} failed, {silent} silent (no issues)"
        )
        
        return all_results


# PURPOSE: Convenience function to run a review with default settings
async def run_review(
    source: str,
    api_key: Optional[str] = None,
    **kwargs
) -> list[JulesResult]:
    """
    Convenience function to run a review with default settings.
    
    Args:
        source: GitHub repository source
        api_key: Optional API key (uses env var if not provided)
        **kwargs: Additional arguments passed to SynedrionReviewer.review()
    
    Returns:
        List of JulesResult objects
    """
    client = JulesClient(api_key=api_key)
    async with client:
        reviewer = SynedrionReviewer(client)
        return await reviewer.review(source=source, **kwargs)
