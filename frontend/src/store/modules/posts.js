/**
 * BlogEngine - Posts Vuex Module
 *
 * Manages post listing, CRUD operations, categories, and tags state.
 */

import { postApi } from '../../api/postApi'

export default {
  namespaced: true,

  state() {
    return {
      posts: [],
      currentPost: null,
      categories: [],
      tags: [],
      series: [],
      pagination: {
        count: 0,
        currentPage: 1,
        totalPages: 1,
        pageSize: 12,
      },
      loading: false,
      error: null,
      filters: {
        category: null,
        tag: null,
        search: '',
        status: null,
      },
    }
  },

  mutations: {
    SET_POSTS(state, { results, count, page }) {
      state.posts = results
      state.pagination.count = count
      state.pagination.currentPage = page
      state.pagination.totalPages = Math.ceil(count / state.pagination.pageSize)
    },
    SET_CURRENT_POST(state, post) {
      state.currentPost = post
    },
    SET_CATEGORIES(state, categories) {
      state.categories = categories
    },
    SET_TAGS(state, tags) {
      state.tags = tags
    },
    SET_SERIES(state, series) {
      state.series = series
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    SET_FILTERS(state, filters) {
      state.filters = { ...state.filters, ...filters }
    },
    REMOVE_POST(state, slug) {
      state.posts = state.posts.filter((p) => p.slug !== slug)
    },
    UPDATE_POST_IN_LIST(state, updatedPost) {
      const idx = state.posts.findIndex((p) => p.id === updatedPost.id)
      if (idx !== -1) {
        state.posts.splice(idx, 1, updatedPost)
      }
    },
  },

  actions: {
    async fetchPosts({ commit, state }, page = 1) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const params = {
          page,
          page_size: state.pagination.pageSize,
          ...state.filters,
        }
        const response = await postApi.list(params)
        commit('SET_POSTS', {
          results: response.data.results,
          count: response.data.count,
          page,
        })
      } catch (error) {
        commit('SET_ERROR', 'Failed to load posts.')
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async fetchPost({ commit }, slug) {
      commit('SET_LOADING', true)
      try {
        const response = await postApi.get(slug)
        commit('SET_CURRENT_POST', response.data)
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Post not found.')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async createPost({ commit, dispatch }, postData) {
      commit('SET_LOADING', true)
      try {
        const response = await postApi.create(postData)
        await dispatch('fetchPosts')
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Failed to create post.')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async updatePost({ commit }, { slug, data }) {
      commit('SET_LOADING', true)
      try {
        const response = await postApi.update(slug, data)
        commit('SET_CURRENT_POST', response.data)
        commit('UPDATE_POST_IN_LIST', response.data)
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Failed to update post.')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async deletePost({ commit }, slug) {
      commit('SET_LOADING', true)
      try {
        await postApi.delete(slug)
        commit('REMOVE_POST', slug)
      } catch (error) {
        commit('SET_ERROR', 'Failed to delete post.')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async toggleLike({ commit }, slug) {
      const response = await postApi.toggleLike(slug)
      return response.data
    },

    async fetchCategories({ commit }) {
      try {
        const response = await postApi.getCategories()
        commit('SET_CATEGORIES', response.data.results || response.data)
      } catch {
        console.error('Failed to load categories')
      }
    },

    async fetchTags({ commit }) {
      try {
        const response = await postApi.getTags()
        commit('SET_TAGS', response.data.results || response.data)
      } catch {
        console.error('Failed to load tags')
      }
    },

    async searchPosts({ commit }, query) {
      commit('SET_LOADING', true)
      try {
        const response = await postApi.search(query)
        return response.data
      } catch {
        return []
      } finally {
        commit('SET_LOADING', false)
      }
    },

    setFilters({ commit, dispatch }, filters) {
      commit('SET_FILTERS', filters)
      dispatch('fetchPosts', 1)
    },
  },

  getters: {
    allPosts: (state) => state.posts,
    currentPost: (state) => state.currentPost,
    featuredPosts: (state) => state.posts.filter((p) => p.is_featured),
    postsByCategory: (state) => (categorySlug) =>
      state.posts.filter((p) => p.category?.slug === categorySlug),
    isLoading: (state) => state.loading,
    pagination: (state) => state.pagination,
    categories: (state) => state.categories,
    tags: (state) => state.tags,
  },
}
