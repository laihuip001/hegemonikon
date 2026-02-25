# 改行の境界官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Line 179: 122文字 (High) - `lines.append(f"  統計: {len(projects)}件 / Active {len(active)} / Dormant {len(dormant)} / Archived {le...`
- Line 513: 238文字 (High) - `print(f"📊 Handoff: {h_count}件 | KI: {ki_count}件 | Sessions: {sessions} | PKS: {pks_count}件 | Safety:...`
- Line 685: 125文字 (High) - `lines.append(f"統計: Active {len(active)} / Dormant {len(dormant)} / Archived {len(archived)} / Total ...`
- Line 754: 124文字 (High) - `+ (f" (≥ {min_chars})" if char_count >= min_chars else f" (< {min_chars}, need {min_chars - char_cou...`
- Line 20: 89文字 (Medium) - `python boot_integration.py --postcheck /tmp/boot_report.md --mode detailed  # ポストチェック`
- Line 85: 81文字 (Medium) - `dispatch_info = {"primary": "", "alternatives": [], "dispatch_formatted": ""}`
- Line 113: 85文字 (Medium) - `result = {"projects": [], "active": 0, "dormant": 0, "total": 0, "formatted": ""}`
- Line 145: 91文字 (Medium) - `elif path.startswith(".") or p.get("id") in ("kalon", "aristos", "autophonos"):`
- Line 154: 88文字 (Medium) - `status_icons = {"active": "🟢", "dormant": "💤", "archived": "🗄️", "planned": "📋"}`
- Line 278: 84文字 (Medium) - `def get_boot_context(mode: str = "standard", context: Optional[str] = None) -> dict:`
- Line 345: 87文字 (Medium) - `wal_lines.append(f"   ⚠️ Blockers: {', '.join(prev_wal.blockers)}")`
- Line 347: 101文字 (Medium) - `incomplete = [e for e in prev_wal.progress if e.status in ("in_progress", "blocked")]`
- Line 376: 87文字 (Medium) - `lines.append(format_boot_output(handoffs_result, verbose=(mode == "detailed")))`
- Line 407: 89文字 (Medium) - `bc_violation_result = {"formatted": bc_summary, "count": len(bc_entries)}`
- Line 416: 91文字 (Medium) - `incoming_files = sorted(incoming_dir.glob("eat_*.md")) if incoming_dir.exists() else []`
- Line 417: 95文字 (Medium) - `incoming_result = {"count": len(incoming_files), "files": [f.name for f in incoming_files]}`
- Line 479: 81文字 (Medium) - `from mekhane.fep.theorem_recommender import todays_theorem, usage_summary`
- Line 605: 86文字 (Medium) - `title = h.metadata.get("primary_task", h.metadata.get("title", "Unknown"))`
- Line 673: 88文字 (Medium) - `status_icons = {"active": "🟢", "dormant": "💤", "archived": "🗄️", "planned": "📋"}`
- Line 721: 109文字 (Medium) - `"checks": [{"name": "file_exists", "passed": False, "detail": f"File not found: {report_path}"}],`
- Line 722: 94文字 (Medium) - `"formatted": f"❌ Boot Report Validation: FAIL\n  ❌ File not found: {report_path}",`
- Line 735: 93文字 (Medium) - `+ ("" if fill_count == 0 else f" remaining (<!-- FILL --> found {fill_count}x)"),`
- Line 764: 93文字 (Medium) - `+ (f" (≥ {expected_h})" if handoff_refs >= expected_h else f" (< {expected_h})"),`
- Line 793: 81文字 (Medium) - `+ (" (required for /boot and /boot+)" if not wal_filled else ""),`
- Line 802: 99文字 (Medium) - `"handoff_context": bool(re.search(r"(?:引き継ぎ|handoff|Handoff|前回)", content, re.IGNORECASE)),`
- Line 803: 114文字 (Medium) - `"self_profile_ref": bool(re.search(r"(?:self.profile|ミスパターン|能力境界|Self-Profile)", content, re.IGNOREC...`
- Line 804: 94文字 (Medium) - `"meaningful_moment": bool(re.search(r"(?:意味ある瞬間|印象的|感動|発見)", content, re.IGNORECASE)),`
- Line 805: 92文字 (Medium) - `"task_continuity": bool(re.search(r"(?:前回の続き|継続|再開|残タスク)", content, re.IGNORECASE)),`
- Line 826: 81文字 (Medium) - `"detail": f"Adjunction L⊣R: ε={epsilon_precision:.0%}, Drift={drift:.0%}"`
- Line 827: 97文字 (Medium) - `+ (f" (fill_penalty: {fill_remaining} FILL remaining)" if fill_remaining > 0 else "")`
- Line 828: 81文字 (Medium) - `+ f" ({', '.join(k for k, v in adjunction_indicators.items() if v)})"`
- Line 830: 87文字 (Medium) - `else f"Adjunction L⊣R: ε=0%, Drift=100% (no context restoration detected)",`
- Line 841: 88文字 (Medium) - `lines = [f"{icon} Boot Report Validation: {status} ({passed_count}/{total} checks)"]`

## 重大度
High
