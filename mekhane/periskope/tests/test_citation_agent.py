# PURPOSE: Tests for the CitationAgent implementation.
# PROOF: S4 (Schema/Praxis) <- mekhane/periskope/PROOF.md

import pytest
from mekhane.periskope.citation_agent import CitationAgent
from mekhane.periskope.models import Citation, TaintLevel

@pytest.fixture
def agent():
    return CitationAgent()

def test_verify_exact_match(agent):
    citation = Citation(claim="The sky is blue.", source_url="http://example.com")
    content = "The sky is blue. The grass is green."
    verified = agent.verify(citation, content)
    assert verified.taint_level == TaintLevel.SOURCE
    assert verified.similarity == 1.0

def test_verify_partial_match(agent):
    # This should yield a similarity between 0.5 and 0.8
    citation = Citation(claim="The sky is sort of blue.", source_url="http://example.com")
    content = "The sky is blue. The grass is green."
    verified = agent.verify(citation, content)
    # Expected ratio calculation:
    # Claim: "The sky is sort of blue." (24 chars)
    # Match: "The sky is blue." (16 chars)
    # 'The sky is ' (11) + 'blue.' (5) matches.
    # Ratio ≈ 2*matches / total_len
    # Let's just check the range
    assert verified.taint_level == TaintLevel.TAINT
    assert 0.5 < verified.similarity <= 0.8

def test_verify_no_match(agent):
    citation = Citation(claim="The moon is made of cheese.", source_url="http://example.com")
    content = "The sky is blue. The grass is green."
    verified = agent.verify(citation, content)
    assert verified.taint_level == TaintLevel.FABRICATED
    assert verified.similarity <= 0.5

def test_verify_empty_content(agent):
    citation = Citation(claim="The sky is blue.", source_url="http://example.com")
    content = ""
    verified = agent.verify(citation, content)
    assert verified.taint_level == TaintLevel.UNCHECKED
    assert verified.similarity == 0.0

def test_verify_missing_claim(agent):
    citation = Citation(claim="", source_url="http://example.com")
    content = "The sky is blue."
    verified = agent.verify(citation, content)
    # Empty claim -> ratio 0 -> FABRICATED
    assert verified.taint_level == TaintLevel.FABRICATED
    assert verified.similarity == 0.0
