# PROOF: [L1/基盤] <- mekhane/synteleia/ パターン辞書ローダー
# PURPOSE: L1 Agent のパターン辞書を外部 YAML からロードする共通機構
"""
Pattern Loader — Shared YAML loading for L1 Agents

All L1 agents share the same loading pattern:
1. Try to load from YAML
2. Fall back to hardcoded defaults if YAML unavailable

Usage:
    patterns = load_patterns(yaml_path, "ousia")
    vague = patterns.get("vague_patterns", FALLBACK)
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# PURPOSE: 文字列リテラルとコメントを除去して L1 エージェントの誤検知を防ぐ
def strip_strings_and_comments(content: str) -> str:
    """文字列リテラルとコメントを空白に置換。パターンマッチの偽陽性を防ぐ。

    対応言語: Python, TypeScript/JavaScript, Rust, Go
    """
    # 1. ブロックコメント (/* ... */ — JS/TS/Rust/Go)
    result = re.sub(r'/\*[\s\S]*?\*/', ' ', content)
    # 2. 行コメント (// — JS/TS/Rust/Go)
    result = re.sub(r'//.*$', ' ', result, flags=re.MULTILINE)
    # 3. 三重クォート文字列 (Python)
    result = re.sub(r'"""[\s\S]*?"""', ' ', result)
    result = re.sub(r"'''[\s\S]*?'''", ' ', result)
    # 4. テンプレートリテラル (JS/TS backtick strings)
    result = re.sub(r'`[^`]*`', ' ', result)
    # 5. JS/TS 正規表現リテラル (/pattern/flags)
    #    代入・引数・return 等の後に来る / を正規表現と判定
    result = re.sub(r'(?<=[=(,;:!&|?+\-~^])\s*/(?![/*])(?:[^/\\\n]|\\.)*/', ' ', result)
    # 6. 通常の文字列
    result = re.sub(r'"[^"\n]*"', ' ', result)
    result = re.sub(r"'[^'\n]*'", ' ', result)
    # 7. 行コメント (# — Python/Shell)
    result = re.sub(r'#.*$', ' ', result, flags=re.MULTILINE)
    return result

logger = logging.getLogger(__name__)

# Cache loaded YAML to avoid repeated disk I/O
_cache: Dict[str, Dict[str, Any]] = {}

# F5: パターンヒットカウンター
_hit_counter: Dict[str, int] = {}


def record_hit(code: str) -> None:
    """パターンヒットを記録。"""
    _hit_counter[code] = _hit_counter.get(code, 0) + 1


def get_stats() -> Dict[str, int]:
    """パターンヒット統計を返す（コード → ヒット数）。"""
    return dict(sorted(_hit_counter.items(), key=lambda x: x[1], reverse=True))


def reset_stats() -> None:
    """統計をリセット（テスト用）。"""
    _hit_counter.clear()


def load_patterns(yaml_path: Path, agent_key: str) -> Dict[str, Any]:
    """YAML からエージェント固有のパターンをロード。

    Args:
        yaml_path: patterns.yaml のパス
        agent_key: YAML 内のエージェントキー (e.g. "ousia", "operator")

    Returns:
        パターン辞書。失敗時は空辞書。
    """
    cache_key = f"{yaml_path}:{agent_key}"
    if cache_key in _cache:
        return _cache[cache_key]

    result: Dict[str, Any] = {}
    try:
        if yaml_path.exists():
            import yaml

            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and agent_key in data:
                result = data[agent_key]
                if not isinstance(result, dict):
                    result = {}
    except Exception as exc:
        logger.warning("Pattern YAML load failed (%s): %s", yaml_path, exc)

    _cache[cache_key] = result
    return result


# F4: ユーザーカスタムパターンパス
_USER_PATTERN_DIR = Path.home() / ".config" / "hegemonikon" / "synteleia"


def load_merged_patterns(
    project_yaml: Path,
    agent_key: str,
    custom_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """3層マージでパターンをロード。

    優先順位: カスタム > プロジェクト YAML > _FALLBACK (呼出側)

    Args:
        project_yaml: プロジェクトの patterns.yaml
        agent_key: エージェントキー
        custom_dir: カスタムパターンディレクトリ (省略時は ~/.config/hegemonikon/synteleia)

    Returns:
        マージ済みパターン辞書
    """
    base = load_patterns(project_yaml, agent_key)

    custom_path = (custom_dir or _USER_PATTERN_DIR) / project_yaml.name
    custom = load_patterns(custom_path, agent_key)

    # カスタムが存在するキーはカスタムで上書き
    merged = {**base, **custom}
    return merged


def parse_pattern_list(
    raw: Any,
    default: List[Tuple[str, Optional[str], Optional[str]]],
) -> List[Tuple[str, Optional[str], Optional[str]]]:
    """YAML のパターンリスト → (regex, code, message) タプルに変換。

    YAML format:
        - pattern: '\\bfoo\\b'
          code: "X-001"
          message: "fooは問題"

    Falls back to default if raw is None or invalid.
    """
    if not isinstance(raw, list):
        return default

    result = []
    for entry in raw:
        if isinstance(entry, dict):
            result.append((
                entry.get("pattern", ""),
                entry.get("code"),
                entry.get("message"),
            ))
        elif isinstance(entry, (list, tuple)) and len(entry) >= 3:
            result.append(tuple(entry[:3]))
    return result or default


def parse_pattern_list_with_severity(
    raw: Any,
    default: List[Tuple[str, str, str, str]],
) -> List[Tuple[str, str, str, str]]:
    """YAML のパターンリスト → (regex, code, message, severity) タプルに変換。

    YAML format:
        - pattern: '\\beval\\s*\\('
          code: "SEC-001"
          message: "eval() は危険"
          severity: "critical"
    """
    if not isinstance(raw, list):
        return default

    result = []
    for entry in raw:
        if isinstance(entry, dict):
            result.append((
                entry.get("pattern", ""),
                entry.get("code", ""),
                entry.get("message", ""),
                entry.get("severity", "low"),
            ))
        elif isinstance(entry, (list, tuple)) and len(entry) >= 4:
            result.append(tuple(entry[:4]))
    return result or default


def parse_keyword_list(raw: Any, default: List[str]) -> List[str]:
    """YAML のキーワードリスト → List[str] に変換。"""
    if isinstance(raw, list) and all(isinstance(x, str) for x in raw):
        return raw
    return default


def parse_string_dict(raw: Any, default: Dict[str, str]) -> Dict[str, str]:
    """YAML の dict → Dict[str, str] に変換。"""
    if isinstance(raw, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in raw.items()
    ):
        return raw
    return default


def parse_pair_list(
    raw: Any,
    default: List[Tuple[str, str]],
) -> List[Tuple[str, str]]:
    """YAML のペアリスト → List[Tuple[str, str]] に変換。

    YAML format:
        - ["必須", "任意"]
    """
    if not isinstance(raw, list):
        return default

    result = []
    for entry in raw:
        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
            result.append((str(entry[0]), str(entry[1])))
    return result or default


def clear_cache() -> None:
    """テスト用: キャッシュをクリア。"""
    _cache.clear()
