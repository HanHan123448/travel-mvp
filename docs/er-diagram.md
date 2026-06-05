# 数据库ER图

```mermaid
erDiagram
    travel_item {
        INTEGER id PK "主键，自增"
        TEXT title "标题，NOT NULL"
        TEXT subtitle "副标题/一句话描述"
        TEXT cover_image "封面图URL"
        TEXT images "配图JSON数组，如 [\"url1\",\"url2\"]"
        TEXT description "正文描述"
        TEXT address "地址"
        TEXT city "城市"
        TEXT tag_ids "标签ID JSON数组，如 [1,3,5]"
        TEXT create_time "创建时间 ISO8601"
    }

    tag {
        INTEGER id PK "主键，自增"
        TEXT name UK "标签名，UNIQUE NOT NULL"
        TEXT emoji "emoji图标"
    }

    user_collect {
        INTEGER id PK "主键，自增"
        TEXT user_id "用户标识，NOT NULL"
        INTEGER item_id FK "关联travel_item.id，NOT NULL"
        TEXT create_time "收藏时间 ISO8601"
    }

    travel_item ||--o{ user_collect : "item_id 引用 id"
    travel_item }o--|| tag : "tag_ids JSON数组 逻辑引用 tag.id"
```

### 关系说明

| 关系 | 类型 | 实现方式 |
|------|------|---------|
| travel_item → user_collect | 一对多 | user_collect.item_id 外键引用 travel_item.id |
| travel_item → tag | 多对多（逻辑） | travel_item.tag_ids 存 JSON 数组，应用层关联 |

> **注意**: travel_item 与 tag 之间不使用数据库外键约束，而是通过 `tag_ids` JSON 字段在应用层做逻辑关联。此设计受限于3表约束（无中间表），查询时由服务端解析 tag_ids 后 join 拼接 tag 完整信息。
