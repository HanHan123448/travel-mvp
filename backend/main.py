"""
FastAPI 后端 — Z世代小众旅行网站
SQLite 数据库，6个 RESTful 接口，100% 对齐 SDD 接口文档
"""
import sqlite3
import json
import os
from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ============================================================
# App & Config
# ============================================================

# 生产环境使用文件DB，测试环境通过 dependency_overrides 注入 :memory:
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "travel_data.db")

app = FastAPI(title="小众探索 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """自定义异常格式：{code, message} 而非 {detail: {...}}"""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": str(exc.detail)}
    )


# ============================================================
# Database
# ============================================================

def get_db():
    """数据库连接依赖（可被测试覆写）"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """初始化数据库 schema（首次启动时执行），测试阶段可安全跳过"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=1, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tag (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                emoji TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS travel_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subtitle TEXT DEFAULT '',
                cover_image TEXT DEFAULT '',
                images TEXT DEFAULT '[]',
                description TEXT DEFAULT '',
                address TEXT DEFAULT '',
                city TEXT DEFAULT '',
                tag_ids TEXT DEFAULT '[]',
                create_time TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_collect (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                create_time TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES travel_item(id),
                UNIQUE(user_id, item_id)
            );
            CREATE INDEX IF NOT EXISTS idx_travel_item_city ON travel_item(city);
            CREATE INDEX IF NOT EXISTS idx_user_collect_user_id ON user_collect(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_collect_item_id ON user_collect(item_id);
        """)
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        pass  # 测试环境并发启动时文件锁冲突，安全跳过


# ============================================================
# Helpers
# ============================================================

def _parse_tag_ids(tag_ids_str):
    """解析 tag_ids JSON 字符串 → int 列表"""
    try:
        return json.loads(tag_ids_str) if tag_ids_str else []
    except (json.JSONDecodeError, TypeError):
        return []


def _enrich_tags(db: sqlite3.Connection, tag_ids_str: str):
    """根据 tag_ids JSON 字符串查询 tag 表，返回完整标签列表"""
    ids = _parse_tag_ids(tag_ids_str)
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    rows = db.execute(
        f"SELECT id, name, emoji FROM tag WHERE id IN ({placeholders})",
        ids
    ).fetchall()
    return [{"id": r["id"], "name": r["name"], "emoji": r["emoji"]} for r in rows]


def _item_to_dict(row, tags=None):
    """将 Row 对象转为字典，可选附加 tags"""
    d = dict(row)
    if tags is not None:
        d["tags"] = tags
    return d


def _list_item_dict(row, db: sqlite3.Connection):
    """列表精简字段 + tags 拼接"""
    d = {
        "id": row["id"],
        "title": row["title"],
        "subtitle": row["subtitle"],
        "cover_image": row["cover_image"],
        "city": row["city"],
        "tag_ids": row["tag_ids"],
        "tags": _enrich_tags(db, row["tag_ids"]),
        "create_time": row["create_time"],
    }
    return d


def _detail_item_dict(row, db: sqlite3.Connection, is_collected: bool):
    """详情全量字段 + tags + is_collected"""
    d = {
        "id": row["id"],
        "title": row["title"],
        "subtitle": row["subtitle"],
        "cover_image": row["cover_image"],
        "images": row["images"],
        "description": row["description"],
        "address": row["address"],
        "city": row["city"],
        "tag_ids": row["tag_ids"],
        "tags": _enrich_tags(db, row["tag_ids"]),
        "create_time": row["create_time"],
        "is_collected": is_collected,
    }
    return d


# ============================================================
# Routes — GET /api/v1/travel  分页列表
# ============================================================

@app.get("/api/v1/travel")
def travel_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    tags: str = Query(None),
    city: str = Query(None),
    keyword: str = Query(None),
    db: sqlite3.Connection = Depends(get_db),
):
    """分页查询旅行项目列表，支持标签/城市/关键词筛选"""
    page_size = min(page_size, 50)  # 上限50
    conditions = []
    params = []

    if tags:
        # 标签筛选：匹配 tag_ids JSON 数组中包含任一指定标签ID
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        or_clauses = []
        for tid in tag_list:
            # SQLite JSON 数组中匹配单个数字
            or_clauses.append("tag_ids LIKE ?")
            params.append(f"%{tid}%")
        if or_clauses:
            conditions.append("(" + " OR ".join(or_clauses) + ")")

    if city:
        conditions.append("city = ?")
        params.append(city)

    if keyword:
        conditions.append("title LIKE ?")
        params.append(f"%{keyword}%")

    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""

    # 查询总数
    count_row = db.execute(f"SELECT COUNT(*) as cnt FROM travel_item{where}", params).fetchone()
    total = count_row["cnt"]

    # 分页查询
    offset = (page - 1) * page_size
    rows = db.execute(
        f"SELECT * FROM travel_item{where} ORDER BY id DESC LIMIT ? OFFSET ?",
        params + [page_size, offset]
    ).fetchall()

    items = [_list_item_dict(r, db) for r in rows]

    return {
        "code": 0,
        "data": {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


# ============================================================
# Routes — GET /api/v1/travel/{id}  详情
# ============================================================

@app.get("/api/v1/travel/{item_id}")
def travel_detail(
    item_id: int,
    user_id: str = Query(None),
    db: sqlite3.Connection = Depends(get_db),
):
    """查询旅行项目详情，可选 user_id 返回收藏状态"""
    row = db.execute("SELECT * FROM travel_item WHERE id = ?", (item_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail={"code": 404, "message": "旅行项目不存在"})

    is_collected = False
    if user_id:
        coll = db.execute(
            "SELECT id FROM user_collect WHERE user_id = ? AND item_id = ?",
            (user_id, item_id)
        ).fetchone()
        is_collected = coll is not None

    return {
        "code": 0,
        "data": _detail_item_dict(row, db, is_collected),
    }


# ============================================================
# Routes — GET /api/v1/tags  标签列表
# ============================================================

@app.get("/api/v1/tags")
def tag_list(db: sqlite3.Connection = Depends(get_db)):
    """返回全量标签列表"""
    rows = db.execute("SELECT id, name, emoji FROM tag ORDER BY id").fetchall()
    tags = [{"id": r["id"], "name": r["name"], "emoji": r["emoji"]} for r in rows]
    return {"code": 0, "data": tags}


# ============================================================
# Routes — POST /api/v1/collect  新增收藏
# ============================================================

@app.post("/api/v1/collect")
def collect_add(body: dict, db: sqlite3.Connection = Depends(get_db)):
    """新增收藏，重复收藏返回 409"""
    user_id = body.get("user_id")
    item_id = body.get("item_id")

    if not user_id or not item_id:
        raise HTTPException(status_code=400, detail={"code": 400, "message": "参数不完整"})

    # 检查项目是否存在
    item = db.execute("SELECT id FROM travel_item WHERE id = ?", (item_id,)).fetchone()
    if not item:
        raise HTTPException(status_code=404, detail={"code": 404, "message": "旅行项目不存在"})

    # 检查重复
    existing = db.execute(
        "SELECT id FROM user_collect WHERE user_id = ? AND item_id = ?",
        (user_id, item_id)
    ).fetchone()
    if existing:
        raise HTTPException(status_code=409, detail={"code": 409, "message": "已收藏，不可重复收藏"})

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    db.execute(
        "INSERT INTO user_collect (user_id, item_id, create_time) VALUES (?, ?, ?)",
        (user_id, item_id, now)
    )
    db.commit()
    return {"code": 0, "message": "收藏成功"}


# ============================================================
# Routes — DELETE /api/v1/collect  取消收藏
# ============================================================

@app.delete("/api/v1/collect")
def collect_remove(
    user_id: str = Query(...),
    item_id: int = Query(...),
    db: sqlite3.Connection = Depends(get_db),
):
    """取消收藏，Query参数传 user_id + item_id，无请求体"""
    existing = db.execute(
        "SELECT id FROM user_collect WHERE user_id = ? AND item_id = ?",
        (user_id, item_id)
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail={"code": 404, "message": "收藏记录不存在"})

    db.execute("DELETE FROM user_collect WHERE user_id = ? AND item_id = ?", (user_id, item_id))
    db.commit()
    return {"code": 0, "message": "取消收藏成功"}


# ============================================================
# Routes — GET /api/v1/collect  收藏列表
# ============================================================

@app.get("/api/v1/collect")
def collect_list(
    user_id: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: sqlite3.Connection = Depends(get_db),
):
    """查询用户收藏列表，分页返回"""
    # 总数
    count_row = db.execute(
        "SELECT COUNT(*) as cnt FROM user_collect WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    total = count_row["cnt"]

    # 分页
    offset = (page - 1) * page_size
    rows = db.execute(
        """SELECT uc.create_time as collect_time, ti.*
           FROM user_collect uc
           JOIN travel_item ti ON uc.item_id = ti.id
           WHERE uc.user_id = ?
           ORDER BY uc.create_time DESC
           LIMIT ? OFFSET ?""",
        (user_id, page_size, offset)
    ).fetchall()

    items = []
    for r in rows:
        d = {
            "id": r["id"],
            "title": r["title"],
            "subtitle": r["subtitle"],
            "cover_image": r["cover_image"],
            "city": r["city"],
            "tag_ids": r["tag_ids"],
            "tags": _enrich_tags(db, r["tag_ids"]),
            "collect_time": r["collect_time"],
            "create_time": r["create_time"],
        }
        items.append(d)

    return {
        "code": 0,
        "data": {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


# ============================================================
# Startup
# ============================================================

@app.on_event("startup")
def on_startup():
    init_db()
