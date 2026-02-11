#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Sophia KI (Knowledge Items) CRUD API
"""
Sophia KI Routes — Knowledge Items の CRUD 管理 API

GET    /api/sophia/ki              — KI 一覧
GET    /api/sophia/ki/{ki_id}      — KI 詳細 (Markdown 本文含む)
POST   /api/sophia/ki              — KI 新規作成
PUT    /api/sophia/ki/{ki_id}      — KI 編集
DELETE /api/sophia/ki/{ki_id}      — KI 削除 (.trash/ へ移動)
GET    /api/sophia/search          — KI テキスト検索
"""

import logging
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.sophia")

router = APIRouter(prefix="/sophia", tags=["sophia"])

# --- Knowledge Directory ---
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
KNOWLEDGE_DIR = _PROJECT_ROOT / "kernel" / "knowledge"


# --- Security: Path Traversal 防御 ---
def _sanitize_ki_id(ki_id: str) -> str:
    """ki_id をサニタイズ。パストラバーサル攻撃を防止。

    許可: 英数字, ハイフン, アンダースコア, ドット (先頭以外)
    """
    # 危険な文字列を拒否
    if ".." in ki_id or "/" in ki_id or "\\" in ki_id:
        raise HTTPException(status_code=400, detail="Invalid ki_id: path traversal detected")
    # 空文字列を拒否
    if not ki_id or not ki_id.strip():
        raise HTTPException(status_code=400, detail="Invalid ki_id: empty")
    # 先頭のドットを拒否 (隠しファイル防止)
    if ki_id.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid ki_id: hidden file")
    return ki_id.strip()


def _slugify(title: str) -> str:
    """タイトルから URL 安全な slug を生成。日本語対応。"""
    # 英数字以外をハイフンに変換
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    # 空になった場合 (全角文字のみ等) はタイムスタンプ
    if not slug:
        slug = f"ki-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    return slug[:80]  # 80文字制限


def _resolve_ki_path(ki_id: str) -> Path:
    """ki_id から安全なファイルパスを解決。"""
    ki_id = _sanitize_ki_id(ki_id)
    path = (KNOWLEDGE_DIR / f"{ki_id}.md").resolve()
    # 解決後のパスが KNOWLEDGE_DIR 内にあることを確認
    if not str(path).startswith(str(KNOWLEDGE_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid ki_id: path escape")
    return path


def _ensure_knowledge_dir():
    """knowledge ディレクトリが存在しなければ作成。"""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


# --- Frontmatter Parser ---
def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """YAML frontmatter を解析。(metadata, body) を返す。"""
    metadata = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            for line in fm_text.split("\n"):
                if ":" in line:
                    key, _, value = line.partition(":")
                    metadata[key.strip()] = value.strip().strip('"').strip("'")

    return metadata, body


def _build_frontmatter(metadata: dict) -> str:
    """メタデータから YAML frontmatter 文字列を生成。"""
    lines = ["---"]
    for key, value in metadata.items():
        lines.append(f'{key}: "{value}"')
    lines.append("---\n")
    return "\n".join(lines)


# --- Pydantic Models ---

# PURPOSE: KIListItem の機能を提供する
class KIListItem(BaseModel):
    """KI 一覧の項目。"""
    id: str
    title: str
    source_type: str = "ki"
    updated: str = ""
    created: str = ""
    size_bytes: int = 0


# PURPOSE: KIDetail の機能を提供する
class KIDetail(BaseModel):
    """KI 詳細 (本文含む)。"""
    id: str
    title: str
    content: str = Field(description="Markdown 本文")
    source_type: str = "ki"
    updated: str = ""
    created: str = ""
    size_bytes: int = 0
    backlinks: list[str] = Field(default_factory=list)


# PURPOSE: KICreateRequest の機能を提供する
class KICreateRequest(BaseModel):
    """KI 新規作成リクエスト。"""
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="", description="Markdown 本文")
    source_type: str = Field(default="ki", description="ノードの種別")


# PURPOSE: KIUpdateRequest の機能を提供する
class KIUpdateRequest(BaseModel):
    """KI 編集リクエスト。"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None


# PURPOSE: KIListResponse の機能を提供する
class KIListResponse(BaseModel):
    """KI 一覧レスポンス。"""
    items: list[KIListItem]
    total: int


# PURPOSE: KISearchResult の機能を提供する
class KISearchResult(BaseModel):
    """検索結果。"""
    id: str
    title: str
    snippet: str = Field(description="マッチした行の周辺テキスト")
    line_number: int = 0


# PURPOSE: KISearchResponse の機能を提供する
class KISearchResponse(BaseModel):
    """検索レスポンス。"""
    query: str
    results: list[KISearchResult]
    total: int


# --- Routes ---

# PURPOSE: sophia の list ki 処理を実行する
@router.get("/ki", response_model=KIListResponse)
async def list_ki() -> KIListResponse:
    """KI 一覧を取得。"""
    _ensure_knowledge_dir()

    items: list[KIListItem] = []
    for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        if md_file.name.startswith("."):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
            metadata, _ = _parse_frontmatter(content)
            stat = md_file.stat()
            items.append(KIListItem(
                id=md_file.stem,
                title=metadata.get("title", md_file.stem),
                source_type=metadata.get("source_type", "ki"),
                updated=metadata.get("updated", datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()),
                created=metadata.get("created", ""),
                size_bytes=stat.st_size,
            ))
        except Exception as e:
            logger.warning("Failed to parse KI %s: %s", md_file.name, e)

    return KIListResponse(items=items, total=len(items))


# PURPOSE: ki を取得する
@router.get("/ki/{ki_id}", response_model=KIDetail)
async def get_ki(ki_id: str) -> KIDetail:
    """KI 詳細を取得 (Markdown 本文含む)。"""
    path = _resolve_ki_path(ki_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"KI not found: {ki_id}")

    content = path.read_text(encoding="utf-8")
    metadata, body = _parse_frontmatter(content)
    stat = path.stat()

    # バックリンク検索 (同ディレクトリ内で [[ki_id]] を参照しているファイル)
    backlinks: list[str] = []
    search_pattern = f"[[{ki_id}]]"
    for md_file in KNOWLEDGE_DIR.glob("*.md"):
        if md_file.stem == ki_id:
            continue
        try:
            if search_pattern in md_file.read_text(encoding="utf-8"):
                backlinks.append(md_file.stem)
        except Exception:
            pass

    return KIDetail(
        id=ki_id,
        title=metadata.get("title", ki_id),
        content=body,
        source_type=metadata.get("source_type", "ki"),
        updated=metadata.get("updated", datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()),
        created=metadata.get("created", ""),
        size_bytes=stat.st_size,
        backlinks=backlinks,
    )


# PURPOSE: ki を構築する
@router.post("/ki", response_model=KIDetail, status_code=201)
async def create_ki(req: KICreateRequest) -> KIDetail:
    """KI を新規作成。"""
    _ensure_knowledge_dir()

    ki_id = _slugify(req.title)
    path = _resolve_ki_path(ki_id)

    # 重複チェック: 同名ファイルがあればサフィックス追加
    counter = 1
    original_id = ki_id
    while path.exists():
        ki_id = f"{original_id}-{counter}"
        path = _resolve_ki_path(ki_id)
        counter += 1

    now = datetime.now(timezone.utc).isoformat()
    metadata = {
        "title": req.title,
        "source_type": req.source_type,
        "created": now,
        "updated": now,
    }

    file_content = _build_frontmatter(metadata) + req.content
    path.write_text(file_content, encoding="utf-8")
    logger.info("Created KI: %s (%s)", ki_id, req.title)

    return KIDetail(
        id=ki_id,
        title=req.title,
        content=req.content,
        source_type=req.source_type,
        created=now,
        updated=now,
        size_bytes=path.stat().st_size,
    )


# PURPOSE: ki を更新する
@router.put("/ki/{ki_id}", response_model=KIDetail)
async def update_ki(ki_id: str, req: KIUpdateRequest) -> KIDetail:
    """KI を編集。"""
    path = _resolve_ki_path(ki_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"KI not found: {ki_id}")

    content = path.read_text(encoding="utf-8")
    metadata, body = _parse_frontmatter(content)

    # 更新
    if req.title is not None:
        metadata["title"] = req.title
    if req.content is not None:
        body = req.content
    metadata["updated"] = datetime.now(timezone.utc).isoformat()

    file_content = _build_frontmatter(metadata) + body
    path.write_text(file_content, encoding="utf-8")
    logger.info("Updated KI: %s", ki_id)

    return KIDetail(
        id=ki_id,
        title=metadata.get("title", ki_id),
        content=body,
        source_type=metadata.get("source_type", "ki"),
        created=metadata.get("created", ""),
        updated=metadata["updated"],
        size_bytes=path.stat().st_size,
    )


# PURPOSE: ki を削除する
@router.delete("/ki/{ki_id}")
async def delete_ki(ki_id: str) -> dict:
    """KI を削除 (.trash/ へ移動。安全な操作)。"""
    path = _resolve_ki_path(ki_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"KI not found: {ki_id}")

    # .trash ディレクトリに移動
    trash_dir = KNOWLEDGE_DIR / ".trash"
    trash_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trash_path = trash_dir / f"{ki_id}_{timestamp}.md"
    shutil.move(str(path), str(trash_path))
    logger.info("Deleted (trashed) KI: %s -> %s", ki_id, trash_path.name)

    return {"status": "deleted", "id": ki_id}


# PURPOSE: ki を検索する
@router.get("/search", response_model=KISearchResponse)
async def search_ki(
    q: str = Query(..., min_length=1, description="検索クエリ"),
    limit: int = Query(20, ge=1, le=100),
) -> KISearchResponse:
    """KI をテキスト検索 (ファイル名 + 本文)。"""
    _ensure_knowledge_dir()

    query_lower = q.lower()
    results: list[KISearchResult] = []

    for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        if md_file.name.startswith("."):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
            metadata, body = _parse_frontmatter(content)
            title = metadata.get("title", md_file.stem)

            # タイトルマッチ
            if query_lower in title.lower():
                snippet = title
                results.append(KISearchResult(
                    id=md_file.stem, title=title, snippet=snippet, line_number=0,
                ))
                continue

            # 本文マッチ
            for i, line in enumerate(body.split("\n"), 1):
                if query_lower in line.lower():
                    # 周辺コンテキスト
                    snippet = line.strip()[:200]
                    results.append(KISearchResult(
                        id=md_file.stem, title=title, snippet=snippet, line_number=i,
                    ))
                    break  # 1ファイル1結果

        except Exception as e:
            logger.warning("Search failed for %s: %s", md_file.name, e)

        if len(results) >= limit:
            break

    return KISearchResponse(query=q, results=results, total=len(results))
