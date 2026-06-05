<template>
  <div class="app-shell">
    <!-- 路由视图 -->
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- 底部导航栏 -->
    <nav class="bottom-nav glass">
      <router-link to="/" class="nav-item" active-class="nav-item--active" exact>
        <span class="nav-item__icon">🏠</span>
        <span class="nav-item__label">首页</span>
      </router-link>
      <router-link to="/collect" class="nav-item" active-class="nav-item--active">
        <span class="nav-item__icon">🔖</span>
        <span class="nav-item__label">收藏</span>
      </router-link>
      <div class="nav-item nav-item--disabled">
        <span class="nav-item__icon">👤</span>
        <span class="nav-item__label">我的</span>
      </div>
    </nav>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--bg-deep-dark);
}

/* Bottom Nav */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--bottom-nav-height);
  display: flex;
  align-items: center;
  justify-content: space-around;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  z-index: 50;
  padding-bottom: env(safe-area-inset-bottom);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 4px 16px;
  color: var(--text-muted);
  transition: color 150ms;
  -webkit-tap-highlight-color: transparent;
}
.nav-item--active {
  color: var(--accent-purple);
}
.nav-item--disabled {
  opacity: 0.4;
  cursor: default;
}
.nav-item__icon {
  font-size: 22px;
  line-height: 1;
}
.nav-item__label {
  font-size: 11px;
  font-weight: 500;
}

/* Page Transition */
.page-enter-active,
.page-leave-active {
  transition: opacity 250ms var(--ease-out), transform 250ms var(--ease-out);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
