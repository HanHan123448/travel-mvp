<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="filter-overlay" @click.self="close">
        <Transition name="sheet">
          <div v-if="visible" class="filter-sheet">
            <!-- 拖动手柄 -->
            <div class="filter-sheet__handle" />

            <!-- 头部 -->
            <div class="filter-sheet__header">
              <h2 class="filter-sheet__title">筛选</h2>
              <button class="filter-sheet__reset" @click="resetAll">重置</button>
            </div>

            <!-- 城市选择 -->
            <div class="filter-section">
              <h3 class="filter-section__label">城市</h3>
              <div class="filter-section__chips hide-scrollbar">
                <button
                  v-for="city in cityOptions"
                  :key="city"
                  class="filter-chip"
                  :class="{ 'filter-chip--active': localCity === city }"
                  @click="selectCity(city)"
                >{{ city }}</button>
              </div>
            </div>

            <!-- 标签选择 -->
            <div class="filter-section">
              <h3 class="filter-section__label">标签</h3>
              <div class="filter-section__grid">
                <button
                  v-for="tag in tags"
                  :key="tag.id"
                  class="filter-chip filter-chip--grid"
                  :class="{ 'filter-chip--active': localTags.includes(tag.id) }"
                  @click="toggleTag(tag.id)"
                >{{ tag.emoji }} {{ tag.name }}</button>
              </div>
            </div>

            <!-- 确认按钮 -->
            <button class="filter-sheet__apply" @click="apply">
              👀 查看结果
            </button>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  tags: { type: Array, default: () => [] },
  cities: { type: Array, default: () => [] },
  selectedTags: { type: Array, default: () => [] },
  selectedCity: { type: String, default: '' }
})

const emit = defineEmits(['update:visible', 'apply'])

const localCity = ref('')
const localTags = ref([])

watch(() => props.visible, (val) => {
  if (val) {
    localCity.value = props.selectedCity
    localTags.value = [...props.selectedTags]
  }
})

const cityOptions = ['全部', ...props.cities]

function selectCity(city) {
  localCity.value = city === '全部' ? '' : city
}

function toggleTag(tagId) {
  const idx = localTags.value.indexOf(tagId)
  if (idx === -1) {
    localTags.value.push(tagId)
  } else {
    localTags.value.splice(idx, 1)
  }
}

function resetAll() {
  localCity.value = ''
  localTags.value = []
}

function apply() {
  emit('apply', { city: localCity.value, tags: [...localTags.value] })
}

function close() {
  emit('update:visible', false)
}
</script>

<style scoped>
.filter-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
  display: flex;
  align-items: flex-end;
}

.filter-sheet {
  width: 100%;
  max-height: 65vh;
  background: var(--bg-elevated);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  box-shadow: var(--shadow-modal);
  padding: var(--space-lg) var(--space-xl) var(--space-3xl);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.filter-sheet__handle {
  width: 36px;
  height: 4px;
  background: var(--text-muted);
  border-radius: 2px;
  align-self: center;
  margin-bottom: var(--space-sm);
}

.filter-sheet__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-sheet__title {
  font-size: var(--fs-h2);
  font-weight: 700;
  color: var(--text-primary);
}
.filter-sheet__reset {
  font-size: var(--fs-body);
  color: var(--accent-teal);
  font-weight: 500;
}

/* Section */
.filter-section__label {
  font-size: var(--fs-body);
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: var(--space-md);
}
.filter-section__chips {
  display: flex;
  gap: var(--space-sm);
  overflow-x: auto;
}
.filter-section__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-sm);
}

/* Chip */
.filter-chip {
  padding: 8px 14px;
  background: var(--bg-input);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: var(--fs-chip);
  font-weight: 500;
  white-space: nowrap;
  text-align: center;
  transition: all 200ms var(--ease-out);
}
.filter-chip--grid {
  padding: 10px 8px;
}
.filter-chip--active {
  background: var(--gradient-active);
  color: var(--text-primary);
}

/* Apply Button */
.filter-sheet__apply {
  width: 100%;
  padding: 14px;
  background: var(--gradient-hero);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  font-size: var(--fs-body);
  font-weight: 600;
  text-align: center;
  margin-top: var(--space-sm);
}

/* Transitions */
.modal-enter-active { transition: opacity 300ms var(--ease-out); }
.modal-leave-active { transition: opacity 250ms var(--ease-in); }
.modal-enter-from,
.modal-leave-to { opacity: 0; }

.sheet-enter-active { transition: transform 300ms var(--ease-out); }
.sheet-leave-active { transition: transform 250ms var(--ease-in); }
.sheet-enter-from,
.sheet-leave-to { transform: translateY(100%); }
</style>
