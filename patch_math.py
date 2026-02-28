import re

with open("mekhane/fep/derivative_selector.py", "r") as f:
    content = f.read()

# Fix the math: we should store the unnormalized Dirichlet parameters (counts)
# Let's change the initialization to ones (uniform prior with alpha=1)
# And we just add the update to the counts, then we can optionally normalize when needed.
# Wait, actually in pymdp A matrix is the probabilities, and they do `pA += eta * outer(...)`
# Wait, HegemonikónFEPAgent does exactly this. But it stores the normalized A in `agent.A` and the unnormalized in `pA`?
# Let's check fep_agent.py update_A_dirichlet
