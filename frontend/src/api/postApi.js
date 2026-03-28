/**
 * BlogEngine - Post API Module
 *
 * API methods for posts, categories, tags, and series endpoints.
 */

import api from './axiosConfig'

export const postApi = {
  /**
   * List published posts with pagination and filtering.
   */
  list(params = {}) {
    return api.get('/posts/posts/', { params })
  },

  /**
   * Get a single post by slug.
   */
  get(slug) {
    return api.get(`/posts/posts/${slug}/`)
  },

  /**
   * Create a new post.
   */
  create(data) {
    return api.post('/posts/posts/', data)
  },

  /**
   * Update an existing post by slug.
   */
  update(slug, data) {
    return api.patch(`/posts/posts/${slug}/`, data)
  },

  /**
   * Delete a post by slug.
   */
  delete(slug) {
    return api.delete(`/posts/posts/${slug}/`)
  },

  /**
   * Toggle like on a post.
   */
  toggleLike(slug) {
    return api.post(`/posts/posts/${slug}/like/`)
  },

  /**
   * Get featured posts.
   */
  getFeatured() {
    return api.get('/posts/posts/featured/')
  },

  /**
   * Search posts by query string.
   */
  search(query) {
    return api.get('/posts/posts/search/', { params: { q: query } })
  },

  /**
   * Get the author's own posts (drafts, published, etc.).
   */
  getMyPosts(params = {}) {
    return api.get('/posts/posts/', { params: { mine: true, ...params } })
  },

  // -----------------------------------------------------------------------
  // Categories
  // -----------------------------------------------------------------------
  getCategories(params = {}) {
    return api.get('/posts/categories/', { params })
  },

  getCategory(slug) {
    return api.get(`/posts/categories/${slug}/`)
  },

  // -----------------------------------------------------------------------
  // Tags
  // -----------------------------------------------------------------------
  getTags(params = {}) {
    return api.get('/posts/tags/', { params })
  },

  // -----------------------------------------------------------------------
  // Series
  // -----------------------------------------------------------------------
  getSeries(params = {}) {
    return api.get('/posts/series/', { params })
  },

  getSeriesDetail(slug) {
    return api.get(`/posts/series/${slug}/`)
  },

  getSeriesPosts(slug) {
    return api.get(`/posts/series/${slug}/posts/`)
  },

  // -----------------------------------------------------------------------
  // Comments on posts (lightweight)
  // -----------------------------------------------------------------------
  getPostComments(slug) {
    return api.get(`/posts/${slug}/comments/`)
  },

  addPostComment(slug, body) {
    return api.post(`/posts/${slug}/comments/`, { body })
  },
}

export default postApi
