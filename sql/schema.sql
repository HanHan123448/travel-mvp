-- ============================================
-- Z世代小众旅行网站 — SQLite 建表语句
-- 日期: 2026-06-05
-- 约束: 严格仅限3张数据表
-- ============================================

-- 1. 标签表（字典表，先建以便旅行表引用）
CREATE TABLE IF NOT EXISTS tag (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL UNIQUE,
    emoji   TEXT    DEFAULT ''
);

-- 2. 旅行项目表
CREATE TABLE IF NOT EXISTS travel_item (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    subtitle    TEXT    DEFAULT '',
    cover_image TEXT    DEFAULT '',
    images      TEXT    DEFAULT '[]',      -- JSON数组，存储多张配图URL
    description TEXT    DEFAULT '',
    address     TEXT    DEFAULT '',
    city        TEXT    DEFAULT '',
    tag_ids     TEXT    DEFAULT '[]',      -- JSON数组，存储标签ID列表 [1,3,5]
    create_time TEXT    NOT NULL           -- ISO8601格式时间戳
);

-- 3. 用户收藏表
CREATE TABLE IF NOT EXISTS user_collect (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    NOT NULL,
    item_id     INTEGER NOT NULL,
    create_time TEXT    NOT NULL,          -- ISO8601格式时间戳
    FOREIGN KEY (item_id) REFERENCES travel_item(id),
    UNIQUE(user_id, item_id)               -- 防止重复收藏
);

-- 索引：加速城市筛选
CREATE INDEX IF NOT EXISTS idx_travel_item_city ON travel_item(city);

-- 索引：加速用户收藏查询
CREATE INDEX IF NOT EXISTS idx_user_collect_user_id ON user_collect(user_id);

-- 索引：加速按收藏项目查询
CREATE INDEX IF NOT EXISTS idx_user_collect_item_id ON user_collect(item_id);
