"""
/tak - Task Orchestration Module  
PHASE 8: OUTPUT - Must/Should 出力フォーマッター
"""
from datetime import datetime
from .models import TakResult, DeadlineBucket, Classification


# バケット表示設定
BUCKET_DISPLAY = {
    DeadlineBucket.TODAY: ("🔴", "TODAY", "今日中"),
    DeadlineBucket.THREE_DAYS: ("🟠", "3DAYS", "三日以内"),
    DeadlineBucket.WEEK: ("🟡", "WEEK", "今週中"),
    DeadlineBucket.THREE_WEEKS: ("🟢", "3WEEKS", "3週間以内"),
    DeadlineBucket.TWO_MONTHS: ("🔵", "2MONTHS", "2ヶ月以内"),
}


def format_output(result: TakResult) -> str:
    """
    TakResult を整形された出力文字列に変換
    
    Hegemonikón 標準出力形式に準拠
    """
    lines = []
    
    # ヘッダー
    lines.append("┌─[/tak: タスク整理完了]" + "─" * 50 + "┐")
    lines.append("│")
    
    # サマリー
    lines.append(f"│ 📊 サマリー")
    lines.append(f"│   {result.summary()}")
    lines.append("│")
    
    # 水平線
    lines.append("├" + "─" * 68 + "┤")
    
    # 各バケット
    for bucket in [
        DeadlineBucket.TODAY,
        DeadlineBucket.THREE_DAYS, 
        DeadlineBucket.WEEK,
        DeadlineBucket.THREE_WEEKS,
        DeadlineBucket.TWO_MONTHS,
    ]:
        if bucket not in result.buckets:
            continue
            
        schedule_bucket = result.buckets[bucket]
        emoji, code, label = BUCKET_DISPLAY[bucket]
        
        must_count = len(schedule_bucket.must_tasks)
        should_count = len(schedule_bucket.should_tasks)
        
        if must_count == 0 and should_count == 0:
            continue
        
        # バケットヘッダー
        lines.append(f"│ {emoji} {code} ({label}) — Must: {must_count}, Should: {should_count}")
        
        # Must タスク
        for task in schedule_bucket.must_tasks:
            hours = f"({task.estimate_hours:.1f}h)" if task.estimate_hours else ""
            lines.append(f"│   ├ [Must] {task.title} {hours}")
        
        # Should タスク  
        for task in schedule_bucket.should_tasks:
            hours = f"({task.estimate_hours:.1f}h)" if task.estimate_hours else ""
            lines.append(f"│   └ [Should] {task.title} {hours}")
        
        lines.append("│")
    
    # 不足情報
    unresolved_gaps = [g for g in result.gaps if not g.resolved]
    if unresolved_gaps:
        lines.append("├" + "─" * 68 + "┤")
        lines.append("│ ⚠️ 不足情報")
        for i, gap in enumerate(unresolved_gaps[:5], 1):
            auto = "→ 自動収集可" if gap.auto_collectible else "→ Creator確認待ち"
            lines.append(f"│   {i}. [{gap.gap_type.value.upper()}] {gap.question} {auto}")
        lines.append("│")
    
    # キャパシティ警告
    overflowed = [b for b in result.buckets.values() if b.is_overflowed]
    if overflowed:
        lines.append("├" + "─" * 68 + "┤")
        lines.append("│ 📈 キャパシティ警告")
        for bucket in overflowed:
            emoji, code, _ = BUCKET_DISPLAY[bucket.deadline]
            lines.append(
                f"│   {emoji} {code}: {bucket.total_hours:.1f}h 必要 / "
                f"{bucket.available_hours:.1f}h 可用 → ❌ オーバー"
            )
        lines.append("│")
    
    # フッター
    lines.append("└" + "─" * 68 + "┘")
    
    # 次のアクション提案
    if result.buckets.get(DeadlineBucket.TODAY):
        today_must = result.buckets[DeadlineBucket.TODAY].must_tasks
        if today_must:
            first_task = today_must[0].title
            lines.append("")
            lines.append(f"→ 今日は「{first_task}」から始めますか？ [y/n]")
    
    return "\n".join(lines)


def format_compact(result: TakResult) -> str:
    """
    コンパクト出力 (/tak- 用)
    """
    lines = []
    
    for bucket in [
        DeadlineBucket.TODAY,
        DeadlineBucket.THREE_DAYS,
        DeadlineBucket.WEEK,
    ]:
        if bucket not in result.buckets:
            continue
        
        schedule_bucket = result.buckets[bucket]
        emoji, code, _ = BUCKET_DISPLAY[bucket]
        
        tasks = schedule_bucket.must_tasks + schedule_bucket.should_tasks
        if not tasks:
            continue
        
        task_names = ", ".join(t.title[:20] for t in tasks[:3])
        if len(tasks) > 3:
            task_names += f" (+{len(tasks)-3})"
        
        lines.append(f"{emoji} {code}: {task_names}")
    
    return "\n".join(lines) if lines else "タスクなし"
