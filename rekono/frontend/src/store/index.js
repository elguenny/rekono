import Vue from 'vue'
import Vuex from 'vuex'
import router from '@/router'
import AuthenticationApi from '@/backend/authentication'
import { accessTokenKey } from '@/backend/constants'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    user: null,
    role: null,
    mainTabs: true
  },
  mutations: {
    login (state, userData) {
      state.user = userData.user
      state.role = userData.role
    },
    logout (state) {
      state.user = null
      state.role = null
    },
    showMainTabs (state) {
      state.mainTabs = true
    },
    hideMainTabs (state) {
      state.mainTabs = false
    }
  },
  actions: {
    checkState ({ commit }) {
      const accessToken = localStorage.getItem(accessTokenKey)
      if (accessToken) {
        commit('login', AuthenticationApi.decodeToken(accessToken))
      } else {
        commit('login', { user: null, role: null })
      }
    },
    loginAction ({ commit }, { username, password }) {
      return AuthenticationApi.login(username, password)
        .then(data => {
          commit('login', data)
          return Promise.resolve()
        })
    },
    logoutAction ({ commit, dispatch }) {
      return AuthenticationApi.logout()
        .then(() => {
          commit('logout')
          dispatch('redirectToLogin')
          return Promise.resolve()
        })
    },
    redirectToLogin ({ dispatch }) {
      dispatch('checkState')
      router.push({ name: 'login' })
    },
    changeMainTabs ({ state, commit }) {
      if (state.mainTabs) {
        commit('hideMainTabs')
      } else {
        commit('showMainTabs')
      }
    }
  }
})
