"""
标签接口单元测试 — GET /api/v1/tags
测试覆盖: 正常全量返回、数据结构校验
"""


def test_list_all_tags(client):
    """正常查询：返回全部15个标签"""
    res = client.get("/api/v1/tags")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == 0
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 15


def test_tags_have_correct_structure(client):
    """每个标签字段包含 id, name, emoji"""
    res = client.get("/api/v1/tags")
    assert res.status_code == 200
    data = res.json()
    for tag in data["data"]:
        assert "id" in tag
        assert "name" in tag
        assert "emoji" in tag
        assert isinstance(tag["id"], int)
        assert isinstance(tag["name"], str)
        assert isinstance(tag["emoji"], str)


def test_tags_contain_expected_data(client):
    """标签内容符合种子数据"""
    res = client.get("/api/v1/tags")
    assert res.status_code == 200
    data = res.json()
    tags_by_name = {t["name"]: t for t in data["data"]}
    assert "胶片摄影" in tags_by_name
    assert tags_by_name["胶片摄影"]["emoji"] == "📷"
    assert "徒步" in tags_by_name
    assert tags_by_name["徒步"]["emoji"] == "🥾"
