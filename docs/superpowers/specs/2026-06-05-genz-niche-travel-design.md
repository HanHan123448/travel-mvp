# Z世代小众旅行网站 — 设计文档

> **日期**: 2026-06-05  
> **状态**: 已定稿  
> **方法论**: SDD 契约驱动开发 (Specification-Driven Development)

---

## 1. 产品概述

面向Z世代的综合型小众旅行内容平台，收录城市隐藏打卡点（咖啡馆、独立书店、街头艺术等）与户外秘境（徒步路线、野瀑布、无人沙滩等），非热门商业化景点皆可收录。

**技术约束**:
- 数据库：SQLite
- 数据表：严格仅限3张（travel_item、tag、user_collect），禁止新增
- 架构：RESTful API，MVP轻量化

---

## 2. 数据库设计

### 2.1 ER关系

```
travel_item (1) ── (N) user_collect ── user_id (外部字符串)
travel_item.tag_ids ── JSON数组逻辑引用 ── tag.id (非DB外键约束)
```

### 2.2 travel_item（旅行项目表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| title | TEXT | NOT NULL | 标题 |
| subtitle | TEXT | DEFAULT '' | 副标题/一句话描述 |
| cover_image | TEXT | DEFAULT '' | 封面图URL |
| images | TEXT | DEFAULT '[]' | 配图JSON数组 |
| description | TEXT | DEFAULT '' | 正文描述 |
| address | TEXT | DEFAULT '' | 地址 |
| city | TEXT | DEFAULT '' | 城市 |
| tag_ids | TEXT | DEFAULT '[]' | 标签ID JSON数组 |
| create_time | TEXT | NOT NULL | 创建时间 ISO8601 |

### 2.3 tag（标签表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| name | TEXT | NOT NULL, UNIQUE | 标签名 |
| emoji | TEXT | DEFAULT '' | emoji图标 |

### 2.4 user_collect（收藏表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 主键 |
| user_id | TEXT | NOT NULL | 用户标识 |
| item_id | INTEGER | NOT NULL, FK→travel_item.id | 旅行项目ID |
| create_time | TEXT | NOT NULL | 收藏时间 ISO8601 |

**唯一约束**: `UNIQUE(user_id, item_id)` 防止重复收藏。

---

## 3. API设计

**Base URL**: `/api/v1`  
**通用返回格式**: `{"code": 0, "data": {...}, "message": "..."}`  
**错误码**: 0-成功, 404-资源不存在, 409-重复收藏, 500-服务端错误

### 3.1 接口清单

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /travel | 分页列表+标签/城市/关键词筛选 |
| GET | /travel/:id | 详情（可选user_id参数返回收藏状态） |
| GET | /tags | 标签全量列表 |
| GET | /collect | 用户收藏分页列表 |
| POST | /collect | 新增收藏 |
| DELETE | /collect | 取消收藏（Query参数传参） |

### 3.2 列表返回规则

列表接口返回精简字段（不含images、description、address），`tags`字段由服务端根据`tag_ids`拼接标签完整信息后返回。详情接口返回全量字段。

### 3.3 关键设计决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 标签关联 | JSON数组存tag_ids | 3表限制，无中间表 |
| 用户标识 | 纯字符串user_id | 无用户表，MVP极简 |
| 图片 | 存外部URL | SQLite不存二进制 |
| 分页 | page/page_size | 标准RESTful惯例 |
| DELETE传参 | Query参数 | REST规范，无请求体 |

---

## 4. 交付物清单

| 序号 | 文件 | 说明 |
|------|------|------|
| 1 | docs/er-diagram.md | Mermaid格式数据库ER图 |
| 2 | sql/schema.sql | SQLite建表语句 |
| 3 | sql/seed.sql | 5条业务测试数据 |
| 4 | docs/api-documentation.md | RESTful接口完整文档 |

---

## 5. 约束与边界

- **本次交付**: 只生产数据库Schema + API文档及测试数据，不涉及后端实现代码
- **后续扩展**: user_id后续可对接真实用户系统；图片上传可接入OSS
- **不包含**: 用户注册/登录、评论系统、推荐算法、后台管理
