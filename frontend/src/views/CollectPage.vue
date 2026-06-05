<template>
  <div class="collect-page">
    <!-- Header -->
    <header class="collect-header">
      <button class="collect-header__back" @click="$router.push('/')" aria-label="返回">
        ←
      </button>
      <h1 class="collect-header__title">🔖 我的收藏</h1>
      <div style="width:40px" />
    </header>

    <!-- 列表 -->
    <main class="waterfall" ref="scrollRef" @scroll="onScroll">
      <!-- 骨架屏 -->
      <template v-if="loading && list.length === 0">
        <SkeletonCard v-for="n in 6" :key="'s-' + n" />
      </template>

      <!-- 空状态 -->
      <div v-else-if="!loading && list.length === 0" class="empty-state">
        <span class="empty-state__icon">📌</span>
        <p class="empty-state__text">还没有收藏，去探索吧</p>
        <button class="empty-state__btn" @click="$router.push('/')">去探索</button>
      </div>

      <!-- 收藏卡片 -->
      <template v-else>
        <TravelCard
          v-for="item in list"
          :key="item.id"
          :item="item"
          :collected="true"
          @collect="handleRemove(item.id)"
        />

        <div v-if="loading && list.length > 0" class="loading-more">
          <div class="loading-spinner" />
        </div>

        <div v-if="!hasMore && list.length > 0" class="no-more">
          — 已经到底了 —
        </div>
      </template>
    </main>

    <AppToast v-model:visible="toastVisible" :message="toastMessage" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TravelCard from '@/components/TravelCard.vue'
import SkeletonCard from '@/components/SkeletonCard.vue'
import AppToast from '@/components/AppToast.vue'
import { fetchCollectList, removeCollect } from '@/api'

const USER_ID = 'user_demo'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const hasMore = ref(true)

const toastVisible = ref(false)
const toastMessage = ref('')

function showToast(msg) {
  toastMessage.value = msg
  toastVisible.value = true
}

async function loadList(reset = false) {
  if (loading.value) return
  if (reset) { page.value = 1; list.value = []; hasMore.value = true }
  loading.value = true
  try {
    const res = await fetchCollectList(USER_ID, { page: page.value, page_size: 20 })
    if (res.code === 0) {
      if (reset) {
        list.value = res.data.list
      } else {
        list.value.push(...res.data.list)
      }
      total.value = res.data.total
      hasMore.value = list.value.length < total.value
    }
  } catch {
    showToast('加载失败，请重试')
  } finally {
    loading.value = false
  }
}

function onScroll() {
  const el = scrollRef.value
  if (!el || !hasMore.value || loading.value) return
  if (el.scrollHeight - el.scrollTop - el.clientHeight < 300) {
    page.value++
    loadList()
  }
}

async function handleRemove(itemId) {
  try {
    const res = await removeCollect(USER_ID, itemId)
    if (res.code === 0) {
      list.value = list.value.filter(item => item.id !== itemId)
      total.value--
      showToast('已取消收藏')
    }
  } catch {
    showToast('操作失败')
  }
}

onMounted(() => loadList())
</script>

<style scoped>
.collect-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
}

.collect-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 var(--page-h-padding);
  background: var(--bg-deep-dark);
  flex-shrink: 0;
}
.collect-header__back {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--text-secondary);
  border-radius: var(--radius-full);
}
.collect-header__title {
  font-size: var(--fs-h2);
  font-weight: 700;
  color: var(--text-primary);
}

.waterfall {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--page-h-padding);
  padding-bottom: var(--space-xl);
  columns: 2;
  column-gap: var(--card-gap);
}

/* 空状态 */
.empty-state {
  break-inside: avoid;
  column-span: all;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px var(--space-xl);
  text-align: center;
}
.empty-state__icon { font-size: 56px; margin-bottom: var(--space-lg); }
.empty-state__text { font-size: var(--fs-body); color: var(--text-muted); margin-bottom: var(--space-xl); }
.empty-state__btn {
  padding: 10px 24px;
  background: var(--accent-purple);
  color: var(--text-primary);
  border-radius: var(--radius-full);
  font-size: var(--fs-body);
  font-weight: 500;
}

.loading-more {
  break-inside: avoid;
  column-span: all;
  display: flex;
  justify-content: center;
  padding: var(--space-xl);
}
.loading-spinner {
  width: 24px; height: 24px;
  border: 2px solid var(--bg-input);
  border-top-color: var(--accent-purple);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.no-more {
  break-inside: avoid;
  column-span: all;
  text-align: center;
  padding: var(--space-xl);
  font-size: var(--fs-caption);
  color: var(--text-muted);
}
</style>
