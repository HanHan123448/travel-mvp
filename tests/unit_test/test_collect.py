"""
收藏接口单元测试 — POST   /api/v1/collect      新增收藏
                      DELETE /api/v1/collect      取消收藏
                      GET    /api/v1/collect      收藏列表
测试覆盖: 正常收藏/取消、重复收藏409、404项目不存在、收藏列表分页
"""


# ============================================================
# 新增收藏 POST /api/v1/collect
# ============================================================

def test_add_collect_success(client):
    """正常收藏：新增一条收藏记录成功"""
    res = client.post("/api/v1/collect", json={
        "user_id": "user_test",
        "item_id": 2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert "成功" in data["message"]


def test_add_collect_duplicate_returns_409(client):
    """重复收藏异常报错：user_alex 已收藏 item 1，再次收藏返回 409"""
    res = client.post("/api/v1/collect", json={
        "user_id": "user_alex",
        "item_id": 1
    })
    assert res.status_code == 409
    data = res.json()
    assert data["code"] == 409
    assert "重复" in data["message"] or "已收藏" in data["message"]


def test_add_collect_nonexistent_item_returns_404(client):
    """收藏不存在的项目返回 404"""
    res = client.post("/api/v1/collect", json={
        "user_id": "user_test",
        "item_id": 99999
    })
    assert res.status_code == 404
    data = res.json()
    assert data["code"] == 404


# ============================================================
# 取消收藏 DELETE /api/v1/collect
# ============================================================

def test_remove_collect_success(client):
    """正常取消收藏：删除已存在的收藏记录"""
    # user_alex 收藏了 item 3
    res = client.delete("/api/v1/collect?user_id=user_alex&item_id=3")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert "成功" in data["message"]

    # 验证已删除：再次收藏应成功（说明确实删掉了）
    res2 = client.post("/api/v1/collect", json={
        "user_id": "user_alex",
        "item_id": 3
    })
    assert res2.status_code == 200
    assert res2.json()["code"] == 0


def test_remove_collect_not_found_returns_404(client):
    """取消不存在的收藏记录返回 404"""
    res = client.delete("/api/v1/collect?user_id=nobody&item_id=1")
    assert res.status_code == 404
    data = res.json()
    assert data["code"] == 404


# ============================================================
# 收藏列表 GET /api/v1/collect
# ============================================================

def test_list_collects_returns_paginated(client):
    """正常查询：返回 user_alex 的收藏列表，含分页"""
    res = client.get("/api/v1/collect?user_id=user_alex&page=1&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert "list" in data["data"]
    assert "total" in data["data"]
    assert "page" in data["data"]
    assert "page_size" in data["data"]
    assert data["data"]["total"] == 3   # alex 收藏了 1,3,5
    assert len(data["data"]["list"]) == 2

    # 每个收藏项应有 collect_time + 旅行项目信息
    item = data["data"]["list"][0]
    assert "collect_time" in item
    assert "title" in item


def test_list_collects_second_page(client):
    """收藏列表分页第2页"""
    res = client.get("/api/v1/collect?user_id=user_alex&page=2&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert len(data["data"]["list"]) == 1  # 总共3条，第2页剩1条


def test_list_collects_empty_user(client):
    """空数据场景：没有收藏记录的用户返回空列表"""
    res = client.get("/api/v1/collect?user_id=user_nobody")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert len(data["data"]["list"]) == 0
    assert data["data"]["total"] == 0
