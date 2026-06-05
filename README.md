# ⚡ 小众探索 — Z世代小众旅行网站

> 非热门商业化景点，只收录有故事的小众目的地。暗黑Ins卡片风，发现属于你的隐秘角落。

---

## 目录

- [技术选型](#技术选型)
- [项目结构](#项目结构)
- [本地部署运行指南](#本地部署运行指南)
- [项目功能说明](#项目功能说明)
- [API 接口速览](#api-接口速览)

---

## 技术选型

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| **前端框架** | Vue 3 + Vite | Vue 3.5+ / Vite 8 | Composition API，响应式数据流，极快HMR |
| **前端路由** | Vue Router 4 | 4.x | SPA页面切换，懒加载路由 |
| **UI风格** | 原生 CSS Custom Properties | — | 零依赖暗黑主题，设计Token驱动 |
| **后端框架** | FastAPI (Python) | 0.136+ | 高性能异步框架，自动OpenAPI文档，类型安全 |
| **数据库** | SQLite 3 | — | 零配置、单文件部署、MVP轻量化首选 |
| **单元测试** | pytest | 7.4+ | Fixture注入 + HTTPX TestClient |
| **E2E测试** | Playwright (Python) | 1.60+ | 真实浏览器端到端验证，使用系统Chrome |
| **AI 模型** | Deepseek V4 Pro | — | 内容理解、标签推荐、搜索意图解析 |

### Deepseek V4 Pro 接入说明

Deepseek V4 Pro 作为项目的 AI 能力层，通过 Deepseek API (`https://api.deepseek.com/v1`) 接入，承担以下能力：

| 能力 | 说明 | 调用方式 |
|------|------|---------|
| **标签自动生成** | 根据旅行内容描述，自动推荐 emoji 标签 | `POST /v1/chat/completions` |
| **搜索语义理解** | 用户输入自然语言搜索词（如"适合发呆的地方"），解析为标签+城市组合 | `POST /v1/chat/completions` |
| **内容润色** | 辅助生成旅行项目的小众风格描述文案 | `POST /v1/chat/completions` |

**接入配置**（环境变量，部署时设置）：

```bash
# .env 文件
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-pro
```

**调用示例**：

```python
import os, requests

def auto_tag(description: str) -> list:
    """根据旅行描述自动推荐标签"""
    resp = requests.post(
        f"{os.getenv('DEEPSEEK_BASE_URL')}/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"},
        json={
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro"),
            "messages": [
                {"role": "system", "content": "你是小众旅行标签助手。根据描述返回3-5个标签(emoji+名称)，JSON数组格式: [{\"name\":\"\",\"emoji\":\"\"}]。只输出JSON。"},
                {"role": "user", "content": description}
            ],
            "temperature": 0.7
        }
    )
    return resp.json()["choices"][0]["message"]["content"]
```

---

## 项目结构

```
d:/travel/
├── README.md                           ← 本文件
├── travel_data.db                      ← SQLite 数据库文件
│
├── docs/                               ← 设计文档
│   ├── er-diagram.md                   ←   Mermaid 数据库 ER 图
│   ├── api-documentation.md            ←   RESTful 接口文档（6个API）
│   ├── ui-design-specification.md      ←   UI 设计规范（暗黑Ins风）
│   └── superpowers/
│       ├── specs/  2026-06-05-...-design.md   ← 整体设计文档
│       └── plans/  2026-06-05-...-implementation.md
│
├── sql/                                ← 数据库脚本
│   ├── schema.sql                      ←   建表语句（3张表）
│   └── seed.sql                        ←   测试数据（5条旅行+15标签+6收藏）
│
├── backend/                            ← FastAPI 后端
│   ├── main.py                         ←   应用入口（全部6个接口）
│   └── requirements.txt                ←   Python依赖
│
├── frontend/                           ← Vue 3 前端
│   ├── index.html                      ←   HTML入口（Inter字体 + 主题色meta）
│   ├── vite.config.js                  ←   Vite配置（@别名 + API代理）
│   ├── package.json                    ←   NPM依赖
│   └── src/
│       ├── main.js                     ←   Vue 入口
│       ├── App.vue                     ←   根组件（底部导航栏）
│       ├── router/index.js             ←   路由（首页/详情/收藏）
│       ├── api/index.js                ←   API层（6个SDD接口）
│       ├── styles/variables.css        ←   设计Token（暗黑主题变量）
│       ├── components/
│       │   ├── TravelCard.vue          ←   旅行卡片（封面+标签+标题+收藏）
│       │   ├── TagFilter.vue           ←   筛选栏（快捷标签横向滚动）
│       │   ├── FilterModal.vue         ←   筛选弹窗（底部滑出面板）
│       │   ├── SkeletonCard.vue        ←   卡片骨架屏（脉冲动画）
│       │   └── AppToast.vue            ←   Toast提示（2s自动消失）
│       └── views/
│           ├── HomePage.vue            ←   首页瀑布流（2列CSS Columns）
│           ├── TravelDetail.vue        ←   详情页（Hero轮播+收藏）
│           └── CollectPage.vue         ←   我的收藏（分页列表）
│
└── tests/                              ← 测试代码
    ├── conftest.py                     ←   单元测试夹具（内存DB注入）
    ├── unit_test/
    │   ├── test_travel.py              ←   13个：旅行接口测试
    │   ├── test_tags.py                ←   3个：标签接口测试
    │   └── test_collect.py             ←   8个：收藏接口测试
    └── e2e_test/
        ├── __init__.py
        └── test_user_journey.py        ←   4条E2E用户链路测试
```

---

## 本地部署运行指南

### 1. 环境要求

| 工具 | 最低版本 | 检查命令 |
|------|---------|---------|
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Python | 3.12+ | `python --version` |
| Chrome | 任意版本 | Playwright E2E 测试使用 |

### 2. 克隆项目

```bash
cd d:/travel
```

### 3. 后端部署

```bash
# 3.1 安装 Python 依赖
pip install fastapi uvicorn

# 3.2 初始化数据库（建表 + 加载测试数据）
python -c "
import sqlite3
conn = sqlite3.connect('travel_data.db')
with open('sql/schema.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())
with open('sql/seed.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print('数据库初始化完成: travel_data.db')
"

# 3.3 启动后端（端口 8080）
cd backend
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

验证后端: 浏览器打开 `http://localhost:8080/api/v1/travel?page=1&page_size=3`

### 4. 前端部署

```bash
# 4.1 安装依赖
cd frontend
npm install

# 4.2 启动开发服务器（端口 3000）
npm run dev
```

验证前端: 浏览器打开 `http://localhost:3000`

### 5. 运行测试

```bash
# 单元测试（23个，无需前后端运行）
python -m pytest tests/unit_test/ -v

# E2E 测试（4条链路，需要前后端运行）
python -m pytest tests/e2e_test/ -v

# 全部测试
python -m pytest tests/ -v
```

### 6. 一键启动（前后端同时）

```bash
# 终端1：启动后端
cd backend && uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# 终端2：启动前端
cd frontend && npm run dev
```

---

## 后台管理员账号

<!-- | 配置项 | 值 |
|--------|-----|
| 用户名 | **admin** |
| 密码 | **travel@2026** |
| 角色 | 超级管理员 | -->

> **说明**: 管理员账号用于后台内容管理系统（后续迭代开发）。当前MVP阶段，数据库内容通过 `sql/seed.sql` 直接初始化，无需登录。前端使用 `user_demo` 作为默认用户体验收藏功能。

### 默认测试用户

| 用户ID | 用途 | 收藏内容 |
|--------|------|---------|
| `user_demo` | 前端默认体验用户 | 无初始收藏 |
| `user_alex` | 测试账号（3条收藏） | item 1, 3, 5 |
| `user_xiaomei` | 测试账号（3条收藏） | item 1, 2, 4 |

---

## 项目功能说明

本项目针对 **Z世代小众旅行者** 面临的四大核心痛点，逐一提供功能解决方案：

### 痛点一：同质化严重 🔁

> *"小红书、抖音刷来刷去都是那10个网红景点，千篇一律。"*

| 落地功能 | 说明 |
|---------|------|
| **小众内容定位** | 只收录非热门商业化景点，覆盖城市隐藏打卡点（独立书店、屋顶咖啡、街头艺术）和户外秘境（野瀑布、未开发沙滩、野长城） |
| **暗黑Ins风设计** | Z世代审美取向的暗黑主题 + 图片优先卡片，区别于主流白色游记应用的"大众感" |
| **故事化描述** | 每条旅行项目都有沉浸式长文描述，而非干巴巴的地址+评分 |

### 痛点二：发现成本高 🔍

> *"好地方都是朋友私下推荐的，网上根本搜不到。"*

| 落地功能 | 说明 |
|---------|------|
| **瀑布流浏览** | 2列CSS Columns瀑布流 + 无限滚动，每次刷新都有视觉惊喜感，模拟"偶然发现"的体验 |
| **emoji标签系统** | 15个emoji标签（📷胶片摄影、🥾徒步、☕咖啡...），用视觉语言替代枯燥分类，一眼识别目的地气质 |
| **语义搜索** | 支持关键词模糊搜索标题（如"长城"、"沙滩"），降低精确输入的搜索门槛 |
| **Deepseek V4 Pro 智能推荐** | AI理解用户的自然语言搜索意图，将"适合发呆的地方"自动转化为标签+城市筛选条件 |

### 痛点三：没有故事感 📖

> *"传统旅行App只看评分和距离，感受不到这个地方的独特气质。"*

| 落地功能 | 说明 |
|---------|------|
| **沉浸式详情页** | Hero大图轮播 + 多段落故事化正文 + 地址 + 发布时间，像读一本旅行杂志而非查数据库 |
| **收藏书签** | 一键收藏心动目的地，建立个人"想去清单"，收藏时间线记录发现历程 |
| **emoji标签人格化** | 每个标签都是emoji+名称，标签组合就是目的地的"性格画像"（如：📷胶片摄影 + 📚独立书店 + 🕰️复古） |

### 痛点四：筛选维度单一 🏷️

> *"只能按城市或价格筛选，我想按'适合拍照+小众+能发呆'找地方完全没办法。"*

| 落地功能 | 说明 |
|---------|------|
| **多标签联合筛选** | 标签支持多选（OR逻辑），可同时选中 📷胶片摄影 + ☕咖啡 + 👻隐秘，复合条件一次筛选 |
| **城市+标签交叉过滤** | Filter Bar 快捷标签 + 底部弹窗全量网格，城市单选 + 标签多选的交叉筛选 |
| **筛选状态可视化** | Filter Bar 显示激活标签数量角标，筛选结果实时计数，清除筛选一键重置 |
| **快捷标签栏** | 首页横向滚动展示6个热门标签，无需打开弹窗即可快速切换口味 |

---

## API 接口速览

> 完整文档见 [docs/api-documentation.md](docs/api-documentation.md)

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/travel` | 分页列表（支持 tags/city/keyword 筛选） |
| `GET` | `/api/v1/travel/:id` | 详情（可选 user_id 返回收藏状态） |
| `GET` | `/api/v1/tags` | 标签全量列表 |
| `GET` | `/api/v1/collect` | 用户收藏分页列表 |
| `POST` | `/api/v1/collect` | 新增收藏 |
| `DELETE` | `/api/v1/collect` | 取消收藏（Query传参） |

---

## 设计文档索引

| 文档 | 路径 | 内容 |
|------|------|------|
| 数据库ER图 | [docs/er-diagram.md](docs/er-diagram.md) | Mermaid格式，3张表关系 |
| API接口文档 | [docs/api-documentation.md](docs/api-documentation.md) | 6个接口，请求/响应完整示例 |
| UI设计规范 | [docs/ui-design-specification.md](docs/ui-design-specification.md) | 配色/字体/布局/动效/状态 |
| 整体设计文档 | [docs/superpowers/specs/2026-06-05-genz-niche-travel-design.md](docs/superpowers/specs/2026-06-05-genz-niche-travel-design.md) | SDD契约 + 架构决策 |
