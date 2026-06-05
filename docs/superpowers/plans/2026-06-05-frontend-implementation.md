# Z世代小众旅行网站 — 前端实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建Vue3+Vite移动端小众旅行网站前端，严格对齐UI设计规范与SDD接口契约

**Architecture:** 组件化Vue3 SPA，Vue Router管理路由，API层封装全部6个SDD接口，CSS Custom Properties驱动暗黑Ins风格主题

**Tech Stack:** Vue 3 (Composition API), Vite, Vue Router 4, CSS Custom Properties, Inter font

---

## File Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.js
    ├── App.vue
    ├── router/index.js
    ├── api/index.js              # API层，6个SDD接口
    ├── styles/variables.css       # 设计Token CSS变量
    ├── components/
    │   ├── TravelCard.vue         # 旅行卡片
    │   ├── TagFilter.vue          # 标签筛选栏
    │   ├── FilterModal.vue        # 筛选弹窗（底部滑出）
    │   ├── SkeletonCard.vue       # 卡片骨架屏
    │   └── AppToast.vue           # Toast提示
    └── views/
        ├── HomePage.vue           # 首页瀑布流
        ├── TravelDetail.vue       # 旅行详情页
        └── CollectPage.vue        # 收藏列表页
```

---
