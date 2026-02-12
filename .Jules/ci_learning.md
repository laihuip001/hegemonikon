## 2024-05-22 - [GitHub Actions PyTorch CPU Install]
**Learning:** PyTorch CPU wheels are hosted on a separate index (https://download.pytorch.org/whl/cpu). When using `--index-url` in `pip install`, pip restricts its search to ONLY that index, causing installations of standard packages (like `pytest`) to fail if they aren't mirrored there.
**Action:** Always install PyTorch CPU wheels in a separate `pip install` step using `--index-url`, BEFORE installing other dependencies from the default PyPI index.
