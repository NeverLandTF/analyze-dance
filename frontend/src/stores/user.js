import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  
  const isLoggedIn = computed(() => !!token.value)
  const userId = computed(() => user.value?.id || null)
  
  function setUser(userData, authToken) {
    user.value = userData
    token.value = authToken
    if (authToken) {
      localStorage.setItem('token', authToken)
    }
  }
  
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }
  
  return { user, token, isLoggedIn, userId, setUser, logout }
})
