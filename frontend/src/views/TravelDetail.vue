<template>
  <div class="detail-page">
    <!-- 加载态 -->
    <template v-if="loading">
      <div class="detail-skeleton">
        <div class="detail-skeleton__hero" />
        <div class="detail-skeleton__body">
          <div class="skeleton-line skeleton-line--short" />
          <div class="skeleton-line skeleton-line--long" />
          <div class="skeleton-line skeleton-line--medium" />
        </div>
      </div>
    </template>

    <!-- 404 -->
    <div v-else-if="notFound" class="empty-state">
      <span class="empty-state__icon">🗺️</span>
      <p class="empty-state__text">内容不见了</p>
      <button class="empty-state__btn" @click="$router.push('/')">返回探索</button>
    </div>

    <!-- 正常内容 -->
    <template v-else-if="item">
      <!-- Hero 图片区 -->
      <div class="hero">
        <div class="hero__images" ref="carouselRef">
          <img
            v-for="(img, idx) in imageList"
            :key="idx"
            :src="img"
            :alt="`${item.title} - 图片${idx + 1}`"
            class="hero__img"
            loading="lazy"
            @error="onHeroImgError($event, idx)"
          />
          <div v-if="imageList.length === 0" class="hero__placeholder">
            <span>🗺️</span>
          </div>
        </div>

        <!-- 页码指示器 -->
        <div v-if="imageList.length > 1" class="hero__dots">
          <span
            v-for="(_, idx) in imageList"
            :key="idx"
            class="hero__dot"
            :class="{ 'hero__dot--active': idx === currentImage }"
          />
        </div>

        <!-- 返回按钮 -->
        <button class="hero__back" @click="$router.back()" aria-label="返回">
          ←
        </button>

        <!-- 收藏按钮 -->
        <button
          class="hero__collect"
          :class="{ 'hero__collect--active': collected }"
          @click="handleCollect"
        >
          {{ collected ? '❤️' : '🤍' }}
        </button>
      </div>

      <!-- 内容区 -->
      <div class="detail-body">
        <!-- 标签行 -->
        <div v-if="displayTags.length" class="detail-tags hide-scrollbar">
          <span
            v-for="tag in displayTags"
            :key="tag.id"
            class="detail-tag"
          >{{ tag.emoji }} {{ tag.name }}</span>
        </div>

        <!-- 标题 & 副标题 -->
        <h1 class="detail-title">{{ item.title }}</h1>
        <p v-if="item.subtitle" class="detail-subtitle">{{ item.subtitle }}</p>

        <hr class="detail-divider" />

        <!-- 元信息 -->
        <div class="detail-meta">
          <p v-if="item.address" class="detail-meta__item">📍 {{ item.address }}</p>
          <p v-if="item.create_time" class="detail-meta__item">
            🕐 发布于 {{ formatDate(item.create_time) }}
          </p>
        </div>

        <hr class="detail-divider" />

        <!-- 正文 -->
        <div v-if="item.description" class="detail-description">
          <p>{{ item.description }}</p>
        </div>
      </div>
    </template>

    <!-- Toast -->
    <AppToast v-model:visible="toastVisible" :message="toastMessage" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppToast from '@/components/AppToast.vue'
import { fetchTravelDetail, addCollect, removeCollect } from '@/api'

const route = useRoute()
const USER_ID = 'user_demo'

const item = ref(null)
const loading = ref(true)
const notFound = ref(false)
const collected = ref(false)
const currentImage = ref(0)

// Toast
const toastVisible = ref(false)
const toastMessage = ref('')

function showToast(msg) {
  toastMessage.value = msg
  toastVisible.value = true
}

// 图片列表：cover_image + images JSON
const imageList = computed(() => {
  if (!item.value) return []
  const list = []
  if (item.value.cover_image) list.push(item.value.cover_image)
  try {
    const extra = typeof item.value.images === 'string'
      ? JSON.parse(item.value.images)
      : (item.value.images || [])
    extra.forEach(url => { if (url) list.push(url) })
  } catch { /* ignore parse errors */ }
  return list
})

const displayTags = computed(() => {
  if (item.value?.tags && Array.isArray(item.value.tags)) return item.value.tags
  return []
})

function onHeroImgError(e, idx) {
  e.target.style.display = 'none'
}

function formatDate(dateStr) {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric', month: 'long', day: 'numeric'
    })
  } catch {
    return dateStr
  }
}

// 加载详情
async function loadDetail() {
  loading.value = true
  try {
    const res = await fetchTravelDetail(route.params.id, USER_ID)
    if (res.code === 0) {
      item.value = res.data
      collected.value = res.data.is_collected || false
    } else {
      notFound.value = true
    }
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

// 收藏
async function handleCollect() {
  if (!item.value) return
  try {
    if (collected.value) {
      const res = await removeCollect(USER_ID, item.value.id)
      if (res.code === 0) {
        collected.value = false
        showToast('已取消收藏')
      }
    } else {
      const res = await addCollect(USER_ID, item.value.id)
      if (res.code === 0) {
        collected.value = true
        showToast('已加入收藏 💜')
      } else if (res.code === 409) {
        collected.value = true
        showToast('已经收藏过了～')
      }
    }
  } catch {
    showToast('操作失败，请重试')
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: var(--bg-deep-dark);
  padding-bottom: var(--space-3xl);
}

/* Hero */
.hero {
  position: relative;
  width: 100%;
  height: 360px;
  overflow: hidden;
  background: var(--bg-elevated);
}
.hero__images {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  height: 100%;
}
.hero__images::-webkit-scrollbar { display: none; }
.hero__img {
  flex: 0 0 100%;
  width: 100%;
  height: 100%;
  object-fit: cover;
  scroll-snap-align: start;
}
.hero__placeholder {
  flex: 0 0 100%;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 72px;
  background: var(--gradient-active);
}

.hero__dots {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
}
.hero__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  transition: all 200ms;
}
.hero__dot--active {
  background: var(--accent-purple);
  width: 18px;
  border-radius: 3px;
}

.hero__back {
  position: absolute;
  top: max(8px, env(safe-area-inset-top));
  left: var(--space-lg);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(15, 15, 26, 0.6);
  backdrop-filter: blur(8px);
  color: #fff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero__collect {
  position: absolute;
  bottom: var(--space-lg);
  right: var(--space-lg);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(15, 15, 26, 0.6);
  backdrop-filter: blur(8px);
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 300ms var(--ease-bounce);
}
.hero__collect:active {
  transform: scale(1.3);
}

/* 内容区 */
.detail-body {
  padding: var(--space-2xl) var(--page-h-padding);
}

.detail-tags {
  display: flex;
  gap: var(--space-sm);
  overflow-x: auto;
  margin-bottom: var(--space-lg);
}
.detail-tag {
  flex-shrink: 0;
  font-size: var(--fs-chip);
  color: var(--text-secondary);
  background: var(--bg-input);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}

.detail-title {
  font-size: var(--fs-h1);
  font-weight: 800;
  line-height: var(--lh-h1);
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}
.detail-subtitle {
  font-size: var(--fs-body);
  line-height: var(--lh-body);
  color: var(--text-secondary);
}

.detail-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  margin: var(--space-lg) 0;
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}
.detail-meta__item {
  font-size: var(--fs-body);
  color: var(--text-secondary);
  line-height: var(--lh-body);
}

.detail-description {
  font-size: var(--fs-body);
  line-height: var(--lh-body);
  color: var(--text-secondary);
  white-space: pre-line;
}

/* Skeleton */
.detail-skeleton__hero {
  width: 100%;
  height: 360px;
  background: var(--bg-input);
  animation: pulse 1.5s var(--ease-out) infinite;
}
.detail-skeleton__body {
  padding: var(--space-2xl) var(--page-h-padding);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}
.skeleton-line {
  height: 16px;
  background: var(--bg-input);
  border-radius: 4px;
  animation: pulse 1.5s var(--ease-out) infinite;
}
.skeleton-line--short { width: 35%; }
.skeleton-line--long { width: 85%; }
.skeleton-line--medium { width: 55%; }

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

/* Empty */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
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
</style>
