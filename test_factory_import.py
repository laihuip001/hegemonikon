
import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

try:
    from mekhane.symploke.factory import VectorStoreFactory
    print("Factory imported successfully")
    print("Registered adapters:", VectorStoreFactory.list_adapters())
except Exception as e:
    print(f"Factory import failed: {e}")
