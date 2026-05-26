import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 初始化时从 localStorage 读取用户数据
  const storedUser = localStorage.getItem('user')
  const user = ref(storedUser ? JSON.parse(storedUser) : null)
  const token = ref(localStorage.getItem('token') || null)
  const isAdmin = ref(false)
  
  // 初始化时从 localStorage 读取管理员状态
  if (localStorage.getItem('is_admin')) {
    isAdmin.value = localStorage.getItem('is_admin') === 'true'
  }
  
  const isLoggedIn = computed(() => !!token.value)
  const userId = computed(() => user.value?.id || null)
  
  function setUser(userData, authToken, adminStatus = false) {
    user.value = userData
    token.value = authToken
    isAdmin.value = adminStatus
    if (authToken) {
      localStorage.setItem('token', authToken)
      localStorage.setItem('is_admin', adminStatus.toString())
      localStorage.setItem('user', JSON.stringify(userData))
    }
  }
  
  function logout() {
    user.value = null
    token.value = null
    isAdmin.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('is_admin')
    localStorage.removeItem('user')
  }
  
  // 更新用户信息（例如头像）
  function updateUser(updatedData) {
    if (user.value) {
      user.value = { ...user.value, ...updatedData }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }
  
  return { user, token, isAdmin, isLoggedIn, userId, setUser, logout, updateUser }
})
