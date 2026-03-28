/**
 * BlogEngine - Media Vuex Module
 *
 * Manages media library state: file listing, uploads, galleries.
 */

import { mediaApi } from '../../api/mediaApi'

export default {
  namespaced: true,

  state() {
    return {
      files: [],
      galleries: [],
      selectedFiles: [],
      currentGallery: null,
      pagination: {
        count: 0,
        currentPage: 1,
        totalPages: 1,
        pageSize: 24,
      },
      uploading: false,
      uploadProgress: 0,
      loading: false,
      error: null,
      filterType: null, // 'image', 'video', 'document', etc.
    }
  },

  mutations: {
    SET_FILES(state, { results, count, page }) {
      state.files = results
      state.pagination.count = count
      state.pagination.currentPage = page
      state.pagination.totalPages = Math.ceil(count / state.pagination.pageSize)
    },
    ADD_FILES(state, newFiles) {
      state.files = [...newFiles, ...state.files]
      state.pagination.count += newFiles.length
    },
    REMOVE_FILE(state, fileId) {
      state.files = state.files.filter((f) => f.id !== fileId)
      state.pagination.count = Math.max(0, state.pagination.count - 1)
    },
    SET_GALLERIES(state, galleries) {
      state.galleries = galleries
    },
    SET_CURRENT_GALLERY(state, gallery) {
      state.currentGallery = gallery
    },
    SET_SELECTED_FILES(state, files) {
      state.selectedFiles = files
    },
    TOGGLE_FILE_SELECTION(state, file) {
      const idx = state.selectedFiles.findIndex((f) => f.id === file.id)
      if (idx === -1) {
        state.selectedFiles.push(file)
      } else {
        state.selectedFiles.splice(idx, 1)
      }
    },
    CLEAR_SELECTION(state) {
      state.selectedFiles = []
    },
    SET_UPLOADING(state, uploading) {
      state.uploading = uploading
    },
    SET_UPLOAD_PROGRESS(state, progress) {
      state.uploadProgress = progress
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    SET_FILTER_TYPE(state, type) {
      state.filterType = type
    },
  },

  actions: {
    async fetchFiles({ commit, state }, page = 1) {
      commit('SET_LOADING', true)
      try {
        const params = {
          page,
          page_size: state.pagination.pageSize,
        }
        if (state.filterType) {
          params.file_type = state.filterType
        }
        const response = await mediaApi.listFiles(params)
        commit('SET_FILES', {
          results: response.data.results,
          count: response.data.count,
          page,
        })
      } catch {
        commit('SET_ERROR', 'Failed to load media files.')
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async uploadFiles({ commit }, files) {
      commit('SET_UPLOADING', true)
      commit('SET_UPLOAD_PROGRESS', 0)
      try {
        const response = await mediaApi.upload(files, (progress) => {
          commit('SET_UPLOAD_PROGRESS', Math.round(progress * 100))
        })
        if (response.data.uploaded) {
          commit('ADD_FILES', response.data.uploaded)
        }
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Upload failed.')
        throw error
      } finally {
        commit('SET_UPLOADING', false)
        commit('SET_UPLOAD_PROGRESS', 0)
      }
    },

    async deleteFile({ commit }, fileId) {
      try {
        await mediaApi.deleteFile(fileId)
        commit('REMOVE_FILE', fileId)
      } catch {
        commit('SET_ERROR', 'Failed to delete file.')
      }
    },

    async fetchGalleries({ commit }) {
      try {
        const response = await mediaApi.listGalleries()
        commit('SET_GALLERIES', response.data.results || response.data)
      } catch {
        commit('SET_ERROR', 'Failed to load galleries.')
      }
    },

    async createGallery({ commit, dispatch }, galleryData) {
      const response = await mediaApi.createGallery(galleryData)
      await dispatch('fetchGalleries')
      return response.data
    },

    toggleFileSelection({ commit }, file) {
      commit('TOGGLE_FILE_SELECTION', file)
    },

    clearSelection({ commit }) {
      commit('CLEAR_SELECTION')
    },

    setFilterType({ commit, dispatch }, type) {
      commit('SET_FILTER_TYPE', type)
      dispatch('fetchFiles', 1)
    },
  },

  getters: {
    allFiles: (state) => state.files,
    imageFiles: (state) => state.files.filter((f) => f.file_type === 'image'),
    selectedFiles: (state) => state.selectedFiles,
    selectionCount: (state) => state.selectedFiles.length,
    isUploading: (state) => state.uploading,
    uploadProgress: (state) => state.uploadProgress,
    isLoading: (state) => state.loading,
    galleries: (state) => state.galleries,
    pagination: (state) => state.pagination,
  },
}
