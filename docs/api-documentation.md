# Z世代小众旅行网站 — RESTful API 文档

> **Base URL**: `/api/v1`  
> **Content-Type**: `application/json`  
> **通用返回结构**: `{"code": 0, "data": {...}, "message": "..."}`

---

## 错误码约定

| code | 含义 |
|------|------|
| 0 | 成功 |
| 404 | 资源不存在 |
| 409 | 重复收藏 |
| 500 | 服务端错误 |

---

## 接口清单

### 1. 分页列表

```
GET /api/v1/travel
```

**Query参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页条数（最大50） |
| tags | string | 否 | — | 标签ID逗号分隔，如 `"1,3"`，匹配任一即返回 |
| city | string | 否 | — | 城市名精确匹配 |
| keyword | string | 否 | — | 标题模糊搜索（LIKE %keyword%） |

**请求示例**:
```
GET /api/v1/travel?page=1&page_size=10&tags=1,3&city=北京
```

**返回示例**:
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 1,
        "title": "藏在胡同里的胶片书店",
        "subtitle": "北京东城区一家隐秘的摄影主题书店",
        "cover_image": "https://cdn.example.com/cover/bookstore.jpg",
        "city": "北京",
        "tag_ids": "[1, 2]",
        "tags": [
          {"id": 1, "name": "胶片摄影", "emoji": "📷"},
          {"id": 2, "name": "独立书店", "emoji": "📚"}
        ],
        "create_time": "2026-06-01T10:30:00Z"
      }
    ],
    "total": 42,
    "page": 1,
    "page_size": 10
  }
}
```

> **注意**: 列表返回精简字段，不含 `images`、`description`、`address`。`tags` 由服务端解析 `tag_ids` 后拼接完整标签信息。

---

### 2. 详情

```
GET /api/v1/travel/:id
```

**Query参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 否 | 传入时返回 `is_collected` 收藏状态 |

**请求示例**:
```
GET /api/v1/travel/1?user_id=user_abc
```

**返回示例**:
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "title": "藏在胡同里的胶片书店",
    "subtitle": "北京东城区一家隐秘的摄影主题书店",
    "cover_image": "https://cdn.example.com/cover/bookstore.jpg",
    "images": "[\"https://cdn.example.com/detail/1.jpg\",\"https://cdn.example.com/detail/2.jpg\"]",
    "description": "这家书店藏在东四胡同深处，推开木门便是满墙胶片相机和独立出版物...",
    "address": "北京市东城区东四北大街XX号",
    "city": "北京",
    "tag_ids": "[1, 2]",
    "tags": [
      {"id": 1, "name": "胶片摄影", "emoji": "📷"},
      {"id": 2, "name": "独立书店", "emoji": "📚"}
    ],
    "create_time": "2026-06-01T10:30:00Z",
    "is_collected": true
  }
}
```

> **注意**: 详情返回全量字段。`is_collected` 需传入 `user_id` 参数，不传时默认 `false`。

**404返回**:
```json
{"code": 404, "message": "旅行项目不存在"}
```

---

### 3. 标签列表

```
GET /api/v1/tags
```

**无参数**。

**返回示例**:
```json
{
  "code": 0,
  "data": [
    {"id": 1, "name": "胶片摄影", "emoji": "📷"},
    {"id": 2, "name": "独立书店", "emoji": "📚"},
    {"id": 3, "name": "徒步", "emoji": "🥾"}
  ]
}
```

---

### 4. 收藏列表

```
GET /api/v1/collect
```

**Query参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| user_id | string | 是 | — | 用户标识 |
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页条数（最大50） |

**请求示例**:
```
GET /api/v1/collect?user_id=user_abc&page=1&page_size=10
```

**返回示例**:
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 1,
        "title": "藏在胡同里的胶片书店",
        "subtitle": "北京东城区一家隐秘的摄影主题书店",
        "cover_image": "https://cdn.example.com/cover/bookstore.jpg",
        "city": "北京",
        "tag_ids": "[1, 2]",
        "tags": [
          {"id": 1, "name": "胶片摄影", "emoji": "📷"},
          {"id": 2, "name": "独立书店", "emoji": "📚"}
        ],
        "collect_time": "2026-06-03T14:20:00Z",
        "create_time": "2026-06-01T10:30:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 10
  }
}
```

> **注意**: 收藏列表返回原文的旅行项目精简字段，额外增加 `collect_time` 表示收藏时间。

---

### 5. 新增收藏

```
POST /api/v1/collect
```

**请求体 JSON**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户标识 |
| item_id | int | 是 | 旅行项目ID |

**请求示例**:
```json
POST /api/v1/collect
Content-Type: application/json

{"user_id": "user_abc", "item_id": 1}
```

**成功返回**:
```json
{"code": 0, "message": "收藏成功"}
```

**重复收藏返回**:
```json
{"code": 409, "message": "已收藏，不可重复收藏"}
```

**404返回**:
```json
{"code": 404, "message": "旅行项目不存在"}
```

---

### 6. 取消收藏

```
DELETE /api/v1/collect
```

**Query参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户标识 |
| item_id | int | 是 | 旅行项目ID |

> **注意**: 无请求体，参数通过Query传递。

**请求示例**:
```
DELETE /api/v1/collect?user_id=user_abc&item_id=1
```

**成功返回**:
```json
{"code": 0, "message": "取消收藏成功"}
```

**404返回**:
```json
{"code": 404, "message": "收藏记录不存在"}
```

---

## 字段说明汇总

### travel_item 列表字段（精简）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| title | string | 标题 |
| subtitle | string | 副标题 |
| cover_image | string | 封面图URL |
| city | string | 城市 |
| tag_ids | string | 标签ID JSON数组（原始值） |
| tags | array | 服务端拼接的完整标签信息 |
| create_time | string | 创建时间 ISO8601 |

### travel_item 详情字段（全量）

在列表字段基础上增加：

| 字段 | 类型 | 说明 |
|------|------|------|
| images | string | 配图JSON数组 |
| description | string | 正文描述 |
| address | string | 地址 |
| is_collected | bool | 当前用户是否已收藏 |

### tag 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| name | string | 标签名 |
| emoji | string | emoji图标 |

### 收藏列表额外字段

| 字段 | 类型 | 说明 |
|------|------|------|
| collect_time | string | 收藏时间 ISO8601 |
