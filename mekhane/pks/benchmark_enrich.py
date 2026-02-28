import time
import sys
from pathlib import Path

_PKS_DIR = Path(__file__).resolve().parent
_MEKHANE_DIR = _PKS_DIR.parent
_HEGEMONIKON_ROOT = _MEKHANE_DIR.parent

if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

from mekhane.pks.pks_engine import SuggestedQuestionGenerator, KnowledgeNugget
from mekhane.pks.llm_client import PKSLLMClient

# Mock the generate method
original_generate = PKSLLMClient.generate

def mock_generate(self, prompt: str) -> str:
    time.sleep(1) # Simulate 1 second delay
    return "1. Mock question 1\n2. Mock question 2\n3. Mock question 3"

PKSLLMClient.generate = mock_generate

def run_benchmark():
    generator = SuggestedQuestionGenerator(model="gemini-2.0-flash")
    # Force it to be available
    generator._llm._client = True

    nuggets = [
        KnowledgeNugget(
            title=f"Title {i}",
            abstract=f"Abstract {i}",
            source=f"Source {i}",
            relevance_score=0.9
        )
        for i in range(5)
    ]

    start_time = time.time()
    generator.enrich_batch(nuggets)
    end_time = time.time()

    print(f"Time taken for 5 nuggets: {end_time - start_time:.2f} seconds")
    for i, nugget in enumerate(nuggets):
        print(f"Nugget {i} questions: {nugget.suggested_questions}")

if __name__ == "__main__":
    run_benchmark()
