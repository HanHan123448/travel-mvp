# FastAPI 后端 — TDD实现计划

> **Goal:** FastAPI + SQLite 后端，6个SDD接口，TDD测试先行

**Architecture:** FastAPI 单文件应用，SQLite3直接操作，pytest + httpx TestClient

**Tech Stack:** Python 3.12+, FastAPI, sqlite3, pytest, httpx

---

## File Structure

```
backend/
├── requirements.txt
├── main.py                # FastAPI app (全部路由)
tests/
├── conftest.py            # 测试夹具
└── unit_test/
    ├── test_travel.py     # 旅行接口测试
    ├── test_tags.py       # 标签接口测试
    └── test_collect.py    # 收藏接口测试
```

## TDD Order

1. Write conftest.py (test fixtures)
2. Write ALL test files (tests fail — no app yet)
3. Write main.py (all tests pass)

---
