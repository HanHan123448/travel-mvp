<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="visible" class="toast">{{ message }}</div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch } from 'vue'

const props = defineProps({
  message: { type: String, default: '' },
  visible: { type: Boolean, default: false },
  duration: { type: Number, default: 2000 }
})

const emit = defineEmits(['update:visible'])

watch(() => props.visible, (val) => {
  if (val) {
    setTimeout(() => emit('update:visible', false), props.duration)
  }
})
</script>

<style scoped>
.toast {
  position: fixed;
  bottom: calc(var(--bottom-nav-height) + var(--space-lg));
  left: 50%;
  transform: translateX(-50%);
  background: rgba(37, 37, 62, 0.95);
  backdrop-filter: blur(12px);
  color: var(--text-primary);
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-body);
  font-weight: 500;
  white-space: nowrap;
  z-index: 200;
  box-shadow: var(--shadow-modal);
}

.toast-enter-active { transition: all 300ms var(--ease-out); }
.toast-leave-active { transition: all 300ms var(--ease-in); }
.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
