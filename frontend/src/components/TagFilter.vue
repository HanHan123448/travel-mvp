<template>
  <div class="filter-bar">
    <!-- 筛选按钮 -->
    <button class="filter-bar__btn" @click="$emit('open-filter')">
      🔽 筛选
      <span v-if="activeCount" class="filter-bar__badge">{{ activeCount }}</span>
    </button>

    <!-- 快捷标签 -->
    <div class="filter-bar__chips hide-scrollbar">
      <button
        v-for="tag in quickTags"
        :key="tag.id"
        class="filter-chip"
        :class="{ 'filter-chip--active': isTagSelected(tag.id) }"
        @click="$emit('toggle-tag', tag.id)"
      >
        {{ tag.emoji }} {{ tag.name }}
      </button>
      <button
        v-if="selectedCity"
        class="filter-chip filter-chip--city"
        @click="$emit('clear-city')"
      >
        📍 {{ selectedCity }} ✕
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tags: { type: Array, default: () => [] },
  selectedTags: { type: Array, default: () => [] },
  selectedCity: { type: String, default: '' }
})

defineEmits(['open-filter', 'toggle-tag', 'clear-city'])

const quickTags = computed(() => props.tags.slice(0, 6))

const activeCount = computed(() =>
  props.selectedTags.length + (props.selectedCity ? 1 : 0)
)

function isTagSelected(tagId) {
  return props.selectedTags.includes(tagId)
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  height: var(--filter-bar-height);
  padding: 0 var(--page-h-padding);
  position: sticky;
  top: var(--header-height);
  z-index: 10;
  background: var(--bg-deep-dark);
}

/* 筛选按钮 */
.filter-bar__btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: var(--bg-elevated);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
  font-size: var(--fs-caption);
  font-weight: 500;
  white-space: nowrap;
}
.filter-bar__badge {
  background: var(--accent-purple);
  color: #fff;
  font-size: 10px;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  border-radius: var(--radius-full);
  padding: 0 4px;
}

/* 快捷标签行 */
.filter-bar__chips {
  display: flex;
  gap: var(--space-sm);
  overflow-x: auto;
  flex: 1;
}
.filter-chip {
  flex-shrink: 0;
  padding: 6px 12px;
  background: var(--bg-input);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: var(--fs-chip);
  line-height: var(--lh-chip);
  font-weight: 500;
  white-space: nowrap;
  transition: all 200ms var(--ease-out);
}
.filter-chip--active {
  background: var(--accent-purple);
  color: var(--text-primary);
}
.filter-chip--city {
  background: rgba(168, 85, 247, 0.2);
  color: var(--accent-purple);
}
</style>
