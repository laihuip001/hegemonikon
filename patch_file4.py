import re

with open('mekhane/symploke/jules_daily_scheduler.py', 'r') as f:
    content = f.read()

# I will write the replacement manually this time
# Find the start and end of the try block
try_start = content.find("    try:\n        for file_idx, target_file in enumerate(files, 1):")
try_end = content.find("    finally:\n        # API キー復元")

if try_start == -1 or try_end == -1:
    print("Cannot find try block")
    exit(1)

old_block = content[try_start:try_end]

new_block = """    try:
        stop_flag = False
        file_semaphore = asyncio.Semaphore(max_concurrent)
        print_lock = asyncio.Lock()

        # PURPOSE: 各ファイルを非同期で処理
        async def process_file(file_idx: int, target_file: str):
            nonlocal total_started, total_failed, stop_flag
            if stop_flag:
                return None

            async with file_semaphore:
                if stop_flag:
                    return None

                # 専門家プール選択
                if basanos_bridge is not None and hybrid_ratio > 0 and hybrid_ratio < 1.0:
                    # Hybrid mode: basanos + specialist を比率で混合
                    basanos_specs = basanos_bridge.get_perspectives_as_specialists(
                        domains=basanos_domains,
                    )
                    basanos_count = max(1, int(specialists_per_file * hybrid_ratio))
                    specialist_count = specialists_per_file - basanos_count
                    # basanos specs から basanos_count 個をサンプリング
                    sampled_basanos = random.sample(
                        basanos_specs, min(basanos_count, len(basanos_specs)),
                    )
                    # specialist pool から残りをサンプリング
                    pool = list(ALL_SPECIALISTS)
                    sampled_specialist = random.sample(
                        pool, min(specialist_count, len(pool)),
                    )
                    specs = sampled_basanos + sampled_specialist
                    random.shuffle(specs)  # 混合順序をランダム化
                elif basanos_bridge is not None:
                    # Basanos mode: 構造化パースペクティブを使用
                    if use_dynamic:
                        # F10: ファイル特性に基づく動的 perspective
                        specs = basanos_bridge.get_dynamic_perspectives(
                            file_path=target_file,
                            audit_issues=audit_issue_codes,
                            max_perspectives=specialists_per_file,
                        )
                        if not specs:
                            # フォールバック: 静的 perspective
                            specs = basanos_bridge.get_perspectives_as_specialists(
                                domains=basanos_domains,
                            )
                    else:
                        specs = basanos_bridge.get_perspectives_as_specialists(
                            domains=basanos_domains,
                        )
                else:
                    # Specialist mode: audit issue があれば adaptive、なければランダム
                    if audit_issue_codes:
                        from audit_specialist_matcher import AuditSpecialistMatcher
                        from specialist_v2 import get_specialists_by_category
                        matcher = AuditSpecialistMatcher()
                        categories = matcher.select_for_issues(
                            audit_issue_codes, total_budget=specialists_per_file,
                        )
                        specs = []
                        for cat in categories:
                            cat_pool = get_specialists_by_category(cat)
                            if cat_pool:
                                specs.append(random.choice(cat_pool))
                        # budget を満たさなければランダムで補充
                        if len(specs) < specialists_per_file:
                            pool = [s for s in ALL_SPECIALISTS if s not in specs]
                            remaining = specialists_per_file - len(specs)
                            specs.extend(random.sample(pool, min(remaining, len(pool))))
                    else:
                        pool = list(ALL_SPECIALISTS)
                        specs = random.sample(pool, min(specialists_per_file, len(pool)))

                # F14: 低品質 Perspective を実行時除外
                if exclude_low_quality and specs:
                    try:
                        from basanos_feedback import FeedbackStore as _FBStore
                        _excluded_ids = set(_FBStore().get_low_quality_perspectives(threshold=0.1))
                        if _excluded_ids:
                            before = len(specs)
                            specs = [s for s in specs if getattr(s, 'id', '') not in _excluded_ids]
                            culled = before - len(specs)
                            if culled > 0:
                                async with print_lock:
                                    print(f"    🗑️  F14: {culled} low-quality perspectives excluded")
                    except Exception:
                        pass  # FeedbackStore 不在時はスキップ

                if dry_run:
                    async with print_lock:
                        print(f"  [{file_idx}/{len(files)}] {target_file} × {len(specs)} specialists (DRY-RUN)")
                    return {
                        "file": target_file,
                        "specialists": len(specs),
                        "dry_run": True,
                    }

                async with print_lock:
                    print(f"  [{file_idx}/{len(files)}] {target_file} × {len(specs)} specialists")

                results = await run_batch(specs, target_file, max_concurrent)

                started = sum(1 for r in results if "session_id" in r)
                failed = sum(1 for r in results if "error" in r)

                # F9: session_id + perspective_id をログ保存 (jules_result_parser 連携)
                sessions_info = []
                for i, r in enumerate(results):
                    info = {}
                    if "session_id" in r:
                        info["session_id"] = r["session_id"]
                    if "error" in r:
                        info["error"] = str(r["error"])[:100]
                    if i < len(specs):
                        info["specialist"] = specs[i].name
                        info["perspective_id"] = getattr(specs[i], "id", "")
                    sessions_info.append(info)

                async with print_lock:
                    total_started += started
                    total_failed += failed

                    # 安全弁: エラー率チェック
                    total_attempted = total_started + total_failed
                    if total_attempted > 10:
                        error_rate = total_failed / total_attempted
                        if error_rate > MAX_ERROR_RATE:
                            print(f"  ⚠️  Error rate {error_rate:.1%} > {MAX_ERROR_RATE:.0%}, stopping slot")
                            stop_flag = True

                    print(f"    → {started}/{len(specs)} started, {failed} failed")

                return {
                    "file": target_file,
                    "specialists": len(specs),
                    "started": started,
                    "failed": failed,
                    "sessions": sessions_info,
                }

        tasks = [process_file(idx, f) for idx, f in enumerate(files, 1)]
        task_results = await asyncio.gather(*tasks)
        for res in task_results:
            if res is not None:
                all_results.append(res)

"""

new_content = content[:try_start] + new_block + content[try_end:]

with open('mekhane/symploke/jules_daily_scheduler.py', 'w') as f:
    f.write(new_content)

print("Patch applied")
