# 改行の境界官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- L20: 80文字超過 (89文字) `python boot_integration.py --postcheck /tmp/boot_report.md --mode detailed  # ポストチェック` (Medium)
- L85: 80文字超過 (81文字) `dispatch_info = {"primary": "", "alternatives": [], "dispatch_formatted": ""}` (Medium)
- L113: 80文字超過 (85文字) `result = {"projects": [], "active": 0, "dormant": 0, "total": 0, "formatted": ""}` (Medium)
- L145: 80文字超過 (91文字) `elif path.startswith(".") or p.get("id") in ("kalon", "aristos", "autophonos"):` (Medium)
- L154: 80文字超過 (88文字) `status_icons = {"active": "🟢", "dormant": "💤", "archived": "🗄️", "planned": "📋"}` (Medium)
- L179: 120文字超過 (122文字) `lines.append(f"  統計: {len(projects)}件 / Active {len(active)} / Dormant {len(dormant)} / Archived {len(archived)}")` (Critical)
- L278: 80文字超過 (84文字) `def get_boot_context(mode: str = "standard", context: Optional[str] = None) -> dict:` (Medium)
- L345: 80文字超過 (87文字) `wal_lines.append(f"   ⚠️ Blockers: {', '.join(prev_wal.blockers)}")` (Medium)
- L347: 80文字超過 (101文字) `incomplete = [e for e in prev_wal.progress if e.status in ("in_progress", "blocked")]` (Medium)
- L376: 80文字超過 (87文字) `lines.append(format_boot_output(handoffs_result, verbose=(mode == "detailed")))` (Medium)
- L407: 80文字超過 (89文字) `bc_violation_result = {"formatted": bc_summary, "count": len(bc_entries)}` (Medium)
- L416: 80文字超過 (91文字) `incoming_files = sorted(incoming_dir.glob("eat_*.md")) if incoming_dir.exists() else []` (Medium)
- L417: 80文字超過 (95文字) `incoming_result = {"count": len(incoming_files), "files": [f.name for f in incoming_files]}` (Medium)
- L479: 80文字超過 (81文字) `from mekhane.fep.theorem_recommender import todays_theorem, usage_summary` (Medium)
- L513: 120文字超過 (238文字) `print(f"📊 Handoff: {h_count}件 | KI: {ki_count}件 | Sessions: {sessions} | PKS: {pks_count}件 | Safety: {'✅' if safety_errors == 0 else f'⚠️{safety_errors}'} | EPT: {ept_str} | PJ: {proj_str} | Attractor: {attractor_str} | FB: {fb_str}")` (Critical)
- L605: 80文字超過 (86文字) `title = h.metadata.get("primary_task", h.metadata.get("title", "Unknown"))` (Medium)
- L673: 80文字超過 (88文字) `status_icons = {"active": "🟢", "dormant": "💤", "archived": "🗄️", "planned": "📋"}` (Medium)
- L685: 120文字超過 (125文字) `lines.append(f"統計: Active {len(active)} / Dormant {len(dormant)} / Archived {len(archived)} / Total {len(projects)}")` (Critical)
- L721: 80文字超過 (109文字) `"checks": [{"name": "file_exists", "passed": False, "detail": f"File not found: {report_path}"}],` (Medium)
- L722: 80文字超過 (94文字) `"formatted": f"❌ Boot Report Validation: FAIL\n  ❌ File not found: {report_path}",` (Medium)
- L735: 80文字超過 (93文字) `+ ("" if fill_count == 0 else f" remaining (<!-- FILL --> found {fill_count}x)"),` (Medium)
- L754: 120文字超過 (124文字) `+ (f" (≥ {min_chars})" if char_count >= min_chars else f" (< {min_chars}, need {min_chars - char_count} more)"),` (Critical)
- L764: 80文字超過 (93文字) `+ (f" (≥ {expected_h})" if handoff_refs >= expected_h else f" (< {expected_h})"),` (Medium)
- L793: 80文字超過 (81文字) `+ (" (required for /boot and /boot+)" if not wal_filled else ""),` (Medium)
- L802: 80文字超過 (99文字) `"handoff_context": bool(re.search(r"(?:引き継ぎ|handoff|Handoff|前回)", content, re.IGNORECASE)),` (Medium)
- L803: 80文字超過 (114文字) `"self_profile_ref": bool(re.search(r"(?:self.profile|ミスパターン|能力境界|Self-Profile)", content, re.IGNORECASE)),` (Medium)
- L804: 80文字超過 (94文字) `"meaningful_moment": bool(re.search(r"(?:意味ある瞬間|印象的|感動|発見)", content, re.IGNORECASE)),` (Medium)
- L805: 80文字超過 (92文字) `"task_continuity": bool(re.search(r"(?:前回の続き|継続|再開|残タスク)", content, re.IGNORECASE)),` (Medium)
- L826: 80文字超過 (81文字) `"detail": f"Adjunction L⊣R: ε={epsilon_precision:.0%}, Drift={drift:.0%}"` (Medium)
- L827: 80文字超過 (97文字) `+ (f" (fill_penalty: {fill_remaining} FILL remaining)" if fill_remaining > 0 else "")` (Medium)
- L828: 80文字超過 (81文字) `+ f" ({', '.join(k for k, v in adjunction_indicators.items() if v)})"` (Medium)
- L830: 80文字超過 (87文字) `else f"Adjunction L⊣R: ε=0%, Drift=100% (no context restoration detected)",` (Medium)
- L841: 80文字超過 (88文字) `lines = [f"{icon} Boot Report Validation: {status} ({passed_count}/{total} checks)"]` (Medium)

## 重大度
Critical
