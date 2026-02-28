import sys
with open("mekhane/symploke/jules_daily_scheduler.py", "r") as f:
    content = f.read()

content = content.replace("async def process_file(", "# PURPOSE: ファイルごとに専門家を実行\\n    async def process_file(")

with open("mekhane/symploke/jules_daily_scheduler.py", "w") as f:
    f.write(content)
