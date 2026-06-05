<template>
  <div class="home-page">
    <!-- Header -->
    <header class="home-header">
      <h1 class="home-header__title">⚡ 小众探索</h1>
      <div class="home-header__actions">
        <button class="home-header__icon" aria-label="搜索" @click="showSearch">
          🔍
        </button>
        <button class="home-header__icon" aria-label="收藏" @click="$router.push('/collect')">
          🔖
        </button>
      </div>
    </header>

    <!-- 筛选栏 -->
    <TagFilter
      :tags="allTags"
      :selected-tags="selectedTags"
      :selected-city="selectedCity"
      @open-filter="showFilter = true"
      @toggle-tag="toggleQuickTag"
      @clear-city="clearCity"
    />

    <!-- 瀑布流 -->
    <main class="waterfall" ref="waterfallRef" @scroll="onScroll">
      <!-- 骨架屏 -->
      <template v-if="loading && list.length === 0">
        <SkeletonCard v-for="n in 6" :key="'s-' + n" />
      </template>

      <!-- 空状态 -->
      <div v-else-if="!loading && list.length === 0" class="empty-state">
        <span class="empty-state__icon">{{ isFiltered ? '🔍' : '🗺️' }}</span>
        <p class="empty-state__text">
          {{ isFiltered ? '没找到相关内容，换个条件试试' : '还没有旅行内容，敬请期待' }}
        </p>
        <button v-if="isFiltered" class="empty-state__btn" @click="clearAllFilters">
          清除筛选
        </button>
      </div>

      <!-- 卡片流 -->
      <template v-else>
        <TravelCard
          v-for="item in list"
          :key="item.id"
          :item="item"
          :collected="collectedIds.has(item.id)"
          @collect="handleCollect(item.id)"
        />

        <!-- 加载更多指示器 -->
        <div v-if="loading && list.length > 0" class="loading-more">
          <div class="loading-spinner" />
        </div>

        <!-- 没有更多 -->
        <div v-if="!hasMore && list.length > 0" class="no-more">
          — 已经到底了 —
        </div>
      </template>
    </main>

    <!-- 筛选弹窗 -->
    <FilterModal
      v-model:visible="showFilter"
      :tags="allTags"
      :cities="allCities"
      :selected-tags="selectedTags"
      :selected-city="selectedCity"
      @apply="applyFilters"
    />

    <!-- Toast -->
    <AppToast
      v-model:visible="toastVisible"
      :message="toastMessage"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import TravelCard from '@/components/TravelCard.vue'
import TagFilter from '@/components/TagFilter.vue'
import FilterModal from '@/components/FilterModal.vue'
import SkeletonCard from '@/components/SkeletonCard.vue'
import AppToast from '@/components/AppToast.vue'
import { fetchTravelList, fetchTags, addCollect, removeCollect } from '@/api'

const route = useRoute()
const USER_ID = 'user_demo'

// 状态
const list = ref([])
const allTags = ref([])
const allCities = ref([])
const collectedIds = ref(new Set())
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const hasMore = ref(true)
const showFilter = ref(false)

// 筛选
const selectedTags = ref([])
const selectedCity = ref('')

const isFiltered = computed(() => selectedTags.value.length > 0 || selectedCity.value !== '')

// Toast
const toastVisible = ref(false)
const toastMessage = ref('')

function showToast(msg) {
  toastMessage.value = msg
  toastVisible.value = true
}

// 加载标签
async function loadTags() {
  try {
    const res = await fetchTags()
    if (res.code === 0) allTags.value = res.data
  } catch { /* 静默失败 */ }
}

// 加载列表
async function loadList(reset = false) {
  if (loading.value) return
  if (reset) {
    page.value = 1
    list.value = []
    hasMore.value = true
  }
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: 20
    }
    if (selectedTags.value.length) {
      params.tags = selectedTags.value.join(',')
    }
    if (selectedCity.value) {
      params.city = selectedCity.value
    }
    const res = await fetchTravelList(params)
    if (res.code === 0) {
      if (reset) {
        list.value = res.data.list
      } else {
        list.value.push(...res.data.list)
      }
      total.value = res.data.total
      hasMore.value = list.value.length < total.value

      // 提取城市列表
      const cities = new Set(allCities.value)
      res.data.list.forEach(item => {
        if (item.city) cities.add(item.city)
      })
      allCities.value = [...cities]
    }
  } catch {
    showToast('加载失败，请重试')
  } finally {
    loading.value = false
  }
}

// 无限滚动
const waterfallRef = ref(null)
function onScroll() {
  const el = waterfallRef.value
  if (!el || !hasMore.value || loading.value) return
  if (el.scrollHeight - el.scrollTop - el.clientHeight < 300) {
    page.value++
    loadList()
  }
}

// 快捷标签切换
function toggleQuickTag(tagId) {
  const idx = selectedTags.value.indexOf(tagId)
  if (idx === -1) {
    selectedTags.value.push(tagId)
  } else {
    selectedTags.value.splice(idx, 1)
  }
  loadList(true)
}

function clearCity() {
  selectedCity.value = ''
  loadList(true)
}

// 筛选弹窗
function applyFilters({ city, tags }) {
  selectedCity.value = city
  selectedTags.value = tags
  showFilter.value = false
  loadList(true)
}

function clearAllFilters() {
  selectedCity.value = ''
  selectedTags.value = []
  loadList(true)
}

// 收藏/取消
async function handleCollect(itemId) {
  try {
    if (collectedIds.value.has(itemId)) {
      const res = await removeCollect(USER_ID, itemId)
      if (res.code === 0) {
        collectedIds.value.delete(itemId)
        showToast('已取消收藏')
      }
    } else {
      const res = await addCollect(USER_ID, itemId)
      if (res.code === 0) {
        collectedIds.value.add(itemId)
        showToast('已加入收藏 💜')
      } else if (res.code === 409) {
        showToast('已经收藏过了～')
        collectedIds.value.add(itemId)
      }
    }
  } catch {
    showToast('操作失败，请重试')
  }
}

function showSearch() {
  // 搜索功能预留
  showToast('搜索功能即将上线')
}

onMounted(() => {
  loadTags()
  loadList()
})

onBeforeUnmount(() => {
  // cleanup
})
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
}

/* Header */
.home-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 var(--page-h-padding);
  background: var(--bg-deep-dark);
  flex-shrink: 0;
}
.home-header__title {
  font-size: var(--fs-h1);
  font-weight: 800;
  background: var(--gradient-hero);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.home-header__actions {
  display: flex;
  gap: var(--space-md);
}
.home-header__icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--text-secondary);
  border-radius: var(--radius-full);
  transition: color 150ms;
}
.home-header__icon:active {
  color: var(--accent-purple);
}

/* Waterfall */
.waterfall {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--page-h-padding);
  padding-bottom: var(--bottom-nav-height);
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
.empty-state__icon {
  font-size: 56px;
  margin-bottom: var(--space-lg);
}
.empty-state__text {
  font-size: var(--fs-body);
  color: var(--text-muted);
  margin-bottom: var(--space-xl);
}
.empty-state__btn {
  padding: 10px 24px;
  background: var(--accent-purple);
  color: var(--text-primary);
  border-radius: var(--radius-full);
  font-size: var(--fs-body);
  font-weight: 500;
}

/* 加载更多 */
.loading-more {
  break-inside: avoid;
  column-span: all;
  display: flex;
  justify-content: center;
  padding: var(--space-xl);
}
.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--bg-input);
  border-top-color: var(--accent-purple);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-more {
  break-inside: avoid;
  column-span: all;
  text-align: center;
  padding: var(--space-xl);
  font-size: var(--fs-caption);
  color: var(--text-muted);
}
</style>
