"""
pytest 测试夹具 — 内存SQLite + FastAPI TestClient
在 backend/main.py 不存在时，导入会失败 → TDD RED phase
"""
import sqlite3
import pytest
from fastapi.testclient import TestClient

# ============================================================
# Schema & Seed — 来自 sql/schema.sql + sql/seed.sql
# ============================================================

SCHEMA_SQL = """
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
"""

SEED_SQL = """
INSERT INTO tag (id, name, emoji) VALUES
(1,  '胶片摄影',  '📷'),
(2,  '独立书店',  '📚'),
(3,  '复古',      '🕰️'),
(4,  '徒步',      '🥾'),
(5,  '历史遗迹',  '🏛️'),
(6,  '日出',      '🌅'),
(7,  '咖啡',      '☕'),
(8,  '城市景观',  '🌃'),
(9,  '隐秘',      '👻'),
(10, '瀑布',      '💧'),
(11, '夏日避暑',  '❄️'),
(12, '海滩',      '🏖️'),
(13, '日落',      '🌇'),
(14, '露营',      '⛺'),
(15, '街头艺术',  '🎨');

INSERT INTO travel_item (id, title, subtitle, cover_image, images, description, address, city, tag_ids, create_time) VALUES
(1, '藏在胡同里的胶片书店', '北京东城区一家隐秘的摄影主题独立书店', 'https://images.unsplash.com/photo-1526243741027-444d633d1a13?w=800', '["https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?w=1200"]', '推开东四胡同里一扇不起眼的木门...', '北京市东城区东四北大街XX号', '北京', '[1, 2, 3, 7]', '2026-05-15T08:00:00Z'),
(2, '京郊野长城徒步秘境', '箭扣段未修复野长城', 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800', '["https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1200"]', '箭扣长城是北京周边保存最原始的野长城段...', '北京市怀柔区雁栖镇西栅子村', '北京', '[4, 5, 6]', '2026-05-18T06:30:00Z'),
(3, '法租界梧桐树下的屋顶咖啡', '上海原法租界隐秘屋顶', 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800', '["https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1200"]', '这家咖啡店藏在武康路一栋老洋房的四楼...', '上海市徐汇区武康路XX号4楼', '上海', '[7, 8, 9, 3]', '2026-05-20T10:00:00Z'),
(4, '莫干山深处的野生瀑布', '连本地人都未必知道的隐秘瀑布', 'https://images.unsplash.com/photo-1428189923803-e9801d464d76?w=800', '["https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1200"]', '藏在莫干山后山的一个野生瀑布...', '浙江省湖州市德清县筏头乡', '湖州', '[4, 10, 11]', '2026-05-25T11:00:00Z'),
(5, '东山岛无人沙滩日落营地', '漳州东山岛南端废弃灯塔旁的野生沙滩', 'https://images.unsplash.com/photo-1509233725247-49e657c54213?w=800', '["https://images.unsplash.com/photo-1519046904884-53103b34b206?w=1200"]', '东山岛最南端有一处废弃的灯塔...', '福建省漳州市东山县澳角村', '漳州', '[12, 13, 14, 9]', '2026-05-28T14:00:00Z');

INSERT INTO user_collect (user_id, item_id, create_time) VALUES
('user_alex', 1, '2026-05-16T12:00:00Z'),
('user_alex', 3, '2026-05-21T09:30:00Z'),
('user_alex', 5, '2026-05-29T20:00:00Z'),
('user_xiaomei', 1, '2026-05-17T15:00:00Z'),
('user_xiaomei', 2, '2026-05-19T11:00:00Z'),
('user_xiaomei', 4, '2026-05-26T18:30:00Z');
"""


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def test_db():
    """创建内存SQLite数据库，加载 schema + seed 数据"""
    conn = sqlite3.connect("file:testdb?mode=memory&cache=shared", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_SQL)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def client(test_db):
    """
    构建 FastAPI TestClient，通过依赖覆写注入测试DB
    每个测试函数获得独立的 client + 数据库
    """
    from backend.main import app, get_db

    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
