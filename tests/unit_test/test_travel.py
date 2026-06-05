"""
旅行接口单元测试 — GET /api/v1/travel 分页列表
                   GET /api/v1/travel/:id 详情
测试覆盖: 正常查询、标签筛选、城市筛选、关键词搜索、空结果、详情、404、is_collected
"""

# ============================================================
# 分页列表 GET /api/v1/travel
# ============================================================

def test_list_returns_paginated_data(client):
    """正常查询：返回分页列表，包含 list/total/page/page_size"""
    res = client.get("/api/v1/travel?page=1&page_size=3")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert "data" in data
    assert len(data["data"]["list"]) == 3
    assert data["data"]["total"] == 5
    assert data["data"]["page"] == 1
    assert data["data"]["page_size"] == 3
    # 列表字段校验（精简字段，不含 images/description/address）
    item = data["data"]["list"][0]
    assert "id" in item
    assert "title" in item
    assert "subtitle" in item
    assert "cover_image" in item
    assert "city" in item
    assert "tag_ids" in item
    assert "tags" in item
    assert "create_time" in item
    assert "images" not in item          # 列表不返回详情的 images
    assert "description" not in item     # 列表不返回 description
    assert "address" not in item         # 列表不返回 address


def test_list_filters_by_tags(client):
    """标签筛选：传入 tags=1,3，匹配任一标签即返回"""
    # 标签1=胶片摄影, 标签3=复古 → 匹配 item 1 (北京书店 tag_ids=[1,2,3,7])
    # 也匹配 item 3 (上海咖啡 tag_ids=[7,8,9,3])
    res = client.get("/api/v1/travel?tags=1,3")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    ids = [item["id"] for item in data["data"]["list"]]
    assert 1 in ids   # 北京书店 含 [1,2,3,7]
    assert 3 in ids   # 上海咖啡 含 [7,8,9,3]
    # item 2 (野长城 tag_ids=[4,5,6]) 不应出现
    assert 2 not in ids


def test_list_filters_by_city(client):
    """城市筛选：传入 city=上海，只返回上海的项目"""
    res = client.get("/api/v1/travel?city=上海")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 1
    assert data["data"]["list"][0]["city"] == "上海"
    assert data["data"]["list"][0]["id"] == 3


def test_list_filters_by_keyword(client):
    """关键词搜索：传入 keyword=长城，模糊匹配标题"""
    res = client.get("/api/v1/travel?keyword=长城")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert data["data"]["total"] >= 1
    titles = [item["title"] for item in data["data"]["list"]]
    assert any("长城" in t for t in titles)


def test_list_returns_empty_for_no_match(client):
    """空数据场景：筛选不存在的标签，返回空列表"""
    res = client.get("/api/v1/travel?tags=999")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert len(data["data"]["list"]) == 0
    assert data["data"]["total"] == 0


def test_list_pagination_page2(client):
    """分页：第2页返回剩余数据"""
    res = client.get("/api/v1/travel?page=2&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert data["data"]["page"] == 2
    assert data["data"]["page_size"] == 2
    # 总共5条，第1页2条，第2页2条，第3页1条
    assert len(data["data"]["list"]) == 2


def test_list_page_size_max_50(client):
    """分页：page_size 超过50应截断为50（或返回不超过50条）"""
    res = client.get("/api/v1/travel?page=1&page_size=100")
    assert res.status_code == 200
    data = res.json()
    # 总共只有5条测试数据
    assert len(data["data"]["list"]) <= 5


# ============================================================
# 详情 GET /api/v1/travel/:id
# ============================================================

def test_detail_returns_full_item(client):
    """正常详情：返回全量字段"""
    res = client.get("/api/v1/travel/1")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    item = data["data"]
    assert item["id"] == 1
    assert item["title"] == "藏在胡同里的胶片书店"
    assert "images" in item          # 详情有 images
    assert "description" in item    # 详情有 description
    assert "address" in item        # 详情有 address
    assert "tags" in item
    assert "is_collected" in item
    # 不传 user_id 时 is_collected 应为 false
    assert item["is_collected"] is False


def test_detail_returns_404_for_invalid_id(client):
    """404场景：查询不存在的ID"""
    res = client.get("/api/v1/travel/99999")
    assert res.status_code == 404
    data = res.json()
    assert data["code"] == 404


def test_detail_with_user_id_shows_collected_true(client):
    """传入 user_id 时，is_collected 正确反映收藏状态"""
    # user_alex 收藏了 item 1
    res = client.get("/api/v1/travel/1?user_id=user_alex")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert data["data"]["is_collected"] is True


def test_detail_with_user_id_shows_not_collected(client):
    """传入未收藏的 user_id，is_collected 为 false"""
    # user_alex 没有收藏 item 2
    res = client.get("/api/v1/travel/2?user_id=user_alex")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert data["data"]["is_collected"] is False


def test_detail_tags_are_populated(client):
    """详情中的 tags 字段由服务端根据 tag_ids 拼接完整标签信息"""
    res = client.get("/api/v1/travel/1")
    assert res.status_code == 200
    data = res.json()
    tags = data["data"]["tags"]
    assert isinstance(tags, list)
    assert len(tags) > 0
    # 每个 tag 应有 id/name/emoji
    for tag in tags:
        assert "id" in tag
        assert "name" in tag
        assert "emoji" in tag
