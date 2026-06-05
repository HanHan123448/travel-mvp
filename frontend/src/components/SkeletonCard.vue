<template>
  <div class="skeleton-card">
    <div class="skeleton-card__image" />
    <div class="skeleton-card__body">
      <div class="skeleton-line skeleton-line--short" />
      <div class="skeleton-line skeleton-line--long" />
      <div class="skeleton-line skeleton-line--medium" />
    </div>
  </div>
</template>

<style scoped>
.skeleton-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  overflow: hidden;
  break-inside: avoid;
  margin-bottom: var(--card-gap);
}
.skeleton-card__image {
  width: 100%;
  height: 180px;
  background: var(--bg-input);
  animation: pulse 1.5s var(--ease-out) infinite;
}
.skeleton-card__body {
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}
.skeleton-line {
  height: 14px;
  background: var(--bg-input);
  border-radius: 4px;
  animation: pulse 1.5s var(--ease-out) infinite;
}
.skeleton-line--short { width: 40%; }
.skeleton-line--long { width: 90%; }
.skeleton-line--medium { width: 65%; }

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}
</style>
