import re

with open("hermeneus/src/runtime.py", "r") as f:
    content = f.read()

# Replace the fallback return os.environ.get(key) with return None
content = re.sub(r"    # 4\. Fallback \(デフォルトの挙動\)\n    return os\.environ\.get\(key\)", "    # 4. Fallback (すでに環境変数になければ None)\n    return None", content)

with open("hermeneus/src/runtime.py", "w") as f:
    f.write(content)
