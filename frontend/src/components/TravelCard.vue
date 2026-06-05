<template>
  <div
    class="travel-card"
    :class="{ 'travel-card--no-image': !item.cover_image }"
    @click="$router.push(`/travel/${item.id}`)"
  >
    <!-- 封面图区 -->
    <div class="card-image">
      <img
        v-if="item.cover_image"
        :src="item.cover_image"
        :alt="item.title"
        loading="lazy"
        @error="onImageError"
      />
      <div v-else class="card-image__placeholder">
        <span>🗺️</span>
      </div>
      <div class="card-image__overlay" />
      <!-- 收藏按钮 -->
      <button
        class="card-image__collect"
        :class="{ 'card-image__collect--active': collected }"
        @click.stop="$emit('collect', item.id)"
        :aria-label="collected ? '取消收藏' : '收藏'"
      >
        {{ collected ? '❤️' : '🤍' }}
      </button>
    </div>

    <!-- 信息区 -->
    <div class="card-body">
      <!-- 标签行 -->
      <div v-if="displayTags.length" class="card-tags">
        <span
          v-for="tag in displayTags"
          :key="tag.id"
          class="card-tag"
        >{{ tag.emoji }} {{ tag.name }}</span>
        <span v-if="overflowTagCount > 0" class="card-tag card-tag--more">
          +{{ overflowTagCount }}
        </span>
      </div>

      <!-- 标题 -->
      <h3 class="card-title">{{ item.title }}</h3>

      <!-- 底部元信息 -->
      <div class="card-meta">
        <span v-if="item.city" class="card-meta__city">📍 {{ item.city }}</span>
        <span class="card-meta__time">{{ relativeTime }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  collected: { type: Boolean, default: false }
})

defineEmits(['collect'])

const imgFailed = ref(false)

function onImageError() {
  imgFailed.value = true
}

// 解析 tags：优先用服务端拼接的 tags 数组，否则解析 tag_ids
const parsedTags = computed(() => {
  if (props.item.tags && Array.isArray(props.item.tags)) {
    return props.item.tags
  }
  return []
})

const displayTags = computed(() => parsedTags.value.slice(0, 2))
const overflowTagCount = computed(() => Math.max(0, parsedTags.value.length - 2))

const relativeTime = computed(() => {
  if (!props.item.create_time) return ''
  const diff = Date.now() - new Date(props.item.create_time).getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  const weeks = Math.floor(days / 7)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return `${weeks}周前`
})
</script>

<style scoped>
.travel-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  overflow: hidden;
  break-inside: avoid;
  margin-bottom: var(--card-gap);
  transition: transform 150ms var(--ease-out), box-shadow 150ms var(--ease-out);
  cursor: pointer;
}
.travel-card:active {
  transform: scale(0.97);
}
.travel-card:hover {
  box-shadow: 0 0 0 1px rgba(168, 85, 247, 0.3);
}

/* 封面图区 */
.card-image {
  position: relative;
  width: 100%;
  min-height: 140px;
  max-height: 280px;
  overflow: hidden;
  background: var(--bg-elevated);
}
.card-image img {
  width: 100%;
  display: block;
  object-fit: cover;
  min-height: 140px;
  max-height: 280px;
}
.card-image__placeholder {
  width: 100%;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  font-size: 48px;
}
.card-image__overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: var(--card-overlay);
  pointer-events: none;
}

/* 收藏按钮 */
.card-image__collect {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(15, 15, 26, 0.55);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: transform 300ms var(--ease-bounce);
  z-index: 2;
}
.card-image__collect:active {
  transform: scale(1.3);
}

/* 信息区 */
.card-body {
  padding: var(--space-md);
}

/* 标签 */
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  margin-bottom: var(--space-sm);
}
.card-tag {
  font-size: var(--fs-chip);
  line-height: var(--lh-chip);
  color: var(--text-secondary);
  background: var(--bg-input);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  white-space: nowrap;
}
.card-tag--more {
  color: var(--accent-purple);
  background: transparent;
}

/* 标题 */
.card-title {
  font-size: var(--fs-h3);
  line-height: var(--lh-h3);
  font-weight: 600;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: var(--space-sm);
}

/* 底部元信息 */
.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--fs-caption);
  line-height: var(--lh-caption);
  color: var(--text-muted);
}
.card-meta__city {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 65%;
}
.card-meta__time {
  white-space: nowrap;
}
</style>
