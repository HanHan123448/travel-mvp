/**
 * API 层 — 严格对齐 SDD 6个接口规范
 * Base URL: /api/v1
 */

const BASE = '/api/v1'

async function request(url, options = {}) {
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options
  }
  const res = await fetch(`${BASE}${url}`, config)
  const data = await res.json()
  if (!res.ok && data.code !== 409) {
    throw new Error(data.message || '请求失败')
  }
  return data
}

// 1. 分页列表 GET /travel
export function fetchTravelList({ page = 1, page_size = 20, tags, city, keyword } = {}) {
  const params = new URLSearchParams()
  params.set('page', page)
  params.set('page_size', page_size)
  if (tags) params.set('tags', tags)
  if (city) params.set('city', city)
  if (keyword) params.set('keyword', keyword)
  return request(`/travel?${params}`)
}

// 2. 详情 GET /travel/:id
export function fetchTravelDetail(id, userId) {
  const params = userId ? `?user_id=${encodeURIComponent(userId)}` : ''
  return request(`/travel/${id}${params}`)
}

// 3. 标签列表 GET /tags
export function fetchTags() {
  return request('/tags')
}

// 4. 收藏列表 GET /collect
export function fetchCollectList(userId, { page = 1, page_size = 20 } = {}) {
  const params = new URLSearchParams()
  params.set('user_id', userId)
  params.set('page', page)
  params.set('page_size', page_size)
  return request(`/collect?${params}`)
}

// 5. 新增收藏 POST /collect
export function addCollect(userId, itemId) {
  return request('/collect', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, item_id: itemId })
  })
}

// 6. 取消收藏 DELETE /collect?user_id=&item_id=
export function removeCollect(userId, itemId) {
  const params = new URLSearchParams()
  params.set('user_id', userId)
  params.set('item_id', itemId)
  return request(`/collect?${params}`, { method: 'DELETE' })
}
