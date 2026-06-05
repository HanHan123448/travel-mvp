import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomePage.vue'),
    meta: { title: '⚡ 小众探索' }
  },
  {
    path: '/travel/:id',
    name: 'travel-detail',
    component: () => import('@/views/TravelDetail.vue'),
    meta: { title: '详情' }
  },
  {
    path: '/collect',
    name: 'collect',
    component: () => import('@/views/CollectPage.vue'),
    meta: { title: '🔖 我的收藏' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  document.title = to.meta.title || '⚡ 小众探索'
})

export default router
