import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isAdmin = ref(false)
  
  const isLoggedIn = computed(() => !!token.value)
  const userId = computed(() => user.value?.id || null)
  
  function setUser(userData, authToken, adminStatus = false) {
    user.value = userData
    token.value = authToken
    isAdmin.value = adminStatus
    if (authToken) {
      localStorage.setItem('token', authToken)
      localStorage.setItem('is_admin', adminStatus.toString())
    }
  }
  
  // 初始化时从 localStorage 读取管理员状态
  if (localStorage.getItem('is_admin')) {
    isAdmin.value = localStorage.getItem('is_admin') === 'true'
  }
  
  function logout() {
    user.value = null
    token.value = null
    isAdmin.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('is_admin')
  }
  
  return { user, token, isAdmin, isLoggedIn, userId, setUser, logout }
})
