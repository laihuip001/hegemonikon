# 改行の境界官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項

### Critical (> 120 chars) — 窒息（即時修正が必要）
1. **L179** (124 chars): `        lines.append(f"  統計: {len(projects)}件 / Active {len(active)} / Dormant {len(dormant)} / Archived {len(archived)}")`
2. **L512** (256 chars): `    print(f"📊 Handoff: {h_count}件 | KI: {ki_count}件 | Sessions: {sessions} | PKS: {pks_count}件 | Safety: {'✅' if safety_errors == 0 else f'⚠️{safety_errors}'} | EPT: {ept_str} | PJ: {proj_str} | Attractor: {attractor_str} | FB: {fb_str}")`
3. **L684** (132 chars): `        lines.append(f"統計: Active {len(active)} / Dormant {len(dormant)} / Archived {len(archived)} / Total {len(projects)}")`
4. **L753** (128 chars): `            + (f" (≥ {min_chars})" if char_count >= min_chars else f" (< {min_chars}, need {min_chars - char_count} more)"),`
5. **L802** (124 chars): `        "self_profile_ref": bool(re.search(r"(?:self.profile|ミスパターン|能力境界|Self-Profile)", content, re.IGNORECASE)),`

### Medium (> 80 chars) — 呼吸困難（修正推奨）
1. **L20** (92 chars): `    python boot_integration.py --postcheck /tmp/boot_report.md --mode detailed  # ポストチェック`
2. **L85** (81 chars): `    dispatch_info = {"primary": "", "alternatives": [], "dispatch_formatted": ""}`
3. **L113** (85 chars): `    result = {"projects": [], "active": 0, "dormant": 0, "total": 0, "formatted": ""}`
4. **L145** (91 chars): `            elif path.startswith(".") or p.get("id") in ("kalon", "aristos", "autophonos"):`
5. **L154** (89 chars): `        status_icons = {"active": "🟢", "dormant": "💤", "archived": "🗄️", "planned": "📋"}`
6. **L194** (96 chars): `# PURPOSE: /boot 起動時に全 Skill を発見し、Agent がコンテキストに取り込めるようにする`
7. **L278** (84 chars): `def get_boot_context(mode: str = "standard", context: Optional[str] = None) -> dict:`
8. **L282** (85 chars): `    GPU プリフライトチェック付き: GPU 占有時は embedding 系を CPU フォールバックで実行`
9. **L345** (86 chars): `                    wal_lines.append(f"   ⚠️ Blockers: {', '.join(prev_wal.blockers)}")`
10. **L347** (101 chars): `                incomplete = [e for e in prev_wal.progress if e.status in ("in_progress", "blocked")]`
11. **L376** (87 chars): `        lines.append(format_boot_output(handoffs_result, verbose=(mode == "detailed")))`
12. **L407** (89 chars): `                bc_violation_result = {"formatted": bc_summary, "count": len(bc_entries)}`
13. **L415** (81 chars): `    incoming_dir = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "incoming"`
14. **L416** (91 chars): `    incoming_files = sorted(incoming_dir.glob("eat_*.md")) if incoming_dir.exists() else []`
15. **L417** (95 chars): `    incoming_result = {"count": len(incoming_files), "files": [f.name for f in incoming_files]}`
16. **L478** (81 chars): `        from mekhane.fep.theorem_recommender import todays_theorem, usage_summary`
17. **L604** (86 chars): `            title = h.metadata.get("primary_task", h.metadata.get("title", "Unknown"))`
18. **L672** (93 chars): `        status_icons = {"active": "🟢", "dormant": "💤", "archived": "🗄️", "planned": "📋"}`
19. **L720** (109 chars): `            "checks": [{"name": "file_exists", "passed": False, "detail": f"File not found: {report_path}"}],`
20. **L721** (95 chars): `            "formatted": f"❌ Boot Report Validation: FAIL\n  ❌ File not found: {report_path}",`
21. **L734** (93 chars): `            + ("" if fill_count == 0 else f" remaining (<!-- FILL --> found {fill_count}x)"),`
22. **L763** (97 chars): `            + (f" (≥ {expected_h})" if handoff_refs >= expected_h else f" (< {expected_h})"),`
23. **L792** (85 chars): `                + (" (required for /boot and /boot+)" if not wal_filled else ""),`
24. **L801** (104 chars): `        "handoff_context": bool(re.search(r"(?:引き継ぎ|handoff|Handoff|前回)", content, re.IGNORECASE)),`
25. **L803** (100 chars): `        "meaningful_moment": bool(re.search(r"(?:意味ある瞬間|印象的|感動|発見)", content, re.IGNORECASE)),`
26. **L804** (95 chars): `        "task_continuity": bool(re.search(r"(?:前回の続き|継続|再開|残タスク)", content, re.IGNORECASE)),`
27. **L825** (81 chars): `        "detail": f"Adjunction L⊣R: ε={epsilon_precision:.0%}, Drift={drift:.0%}"`
28. **L826** (98 chars): `            + (f" (fill_penalty: {fill_remaining} FILL remaining)" if fill_remaining > 0 else "")`
29. **L827** (83 chars): `            + f" ({', '.join(k for k, v in adjunction_indicators.items() if v)})"`
30. **L829** (90 chars): `            else f"Adjunction L⊣R: ε=0%, Drift=100% (no context restoration detected)",`
31. **L840** (88 chars): `    lines = [f"{icon} Boot Report Validation: {status} ({passed_count}/{total} checks)"]`

## 重大度
Critical
