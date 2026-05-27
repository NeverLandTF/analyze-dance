<template>
  <div class="dancer-list-container">
    <nav class="navbar">
      <div class="nav-brand">🎵 舞蹈 AI 分析</div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link v-if="userStore.isAdmin" to="/dancers" class="nav-link">用户管理</router-link>
        <router-link to="/upload" class="nav-link">上传视频</router-link>
        
        <!-- 用户头像下拉菜单 -->
        <div class="user-menu" ref="userMenuRef">
          <div class="avatar-btn" @click="toggleUserMenu">
            <div class="avatar-small">
              {{ userStore.user?.username?.charAt(0).toUpperCase() }}
            </div>
          </div>
          
          <div v-if="showUserMenu" class="dropdown-menu">
            <div class="dropdown-header">
              <div class="avatar-medium">
                {{ userStore.user?.username?.charAt(0).toUpperCase() }}
              </div>
              <div class="user-info">
                <div class="username">{{ userStore.user?.username }}</div>
                <div class="role-badge" :class="userStore.isAdmin ? 'admin' : 'user'">
                  {{ userStore.isAdmin ? '管理员' : '普通用户' }}
                </div>
              </div>
            </div>
            
            <div class="dropdown-divider"></div>
            
            <router-link to="/profile" class="dropdown-item">
              <span class="icon">👤</span> 个人中心
            </router-link>
            <router-link to="/profile#password" class="dropdown-item">
              <span class="icon">🔐</span> 密码修改
            </router-link>
            
            <div class="dropdown-divider"></div>
            
            <button @click="handleLogout" class="dropdown-item logout-btn">
              <span class="icon">🚪</span> 退出登录
            </button>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="main-content">
      <div v-if="!userStore.isAdmin" class="access-denied">
        <h1>无权访问</h1>
        <p>普通用户无法查看用户管理页面，每个用户即代表一个舞者。</p>
        <button @click="$router.push('/upload')" class="btn-primary">去上传视频</button>
      </div>
      
      <div v-else>
        <div class="header">
          <h1>用户管理</h1>
          <div class="header-actions">
            <span class="admin-badge">管理员</span>
            <button @click="showCreateModal = true" class="btn-primary">+ 创建新用户</button>
          </div>
        </div>
        
        <div v-if="loading" class="loading">加载中...</div>
        
        <div v-else-if="users.length === 0" class="empty-state">
          <p>暂无用户，点击上方按钮创建第一个用户</p>
        </div>
        
        <div v-else class="users-grid">
          <div 
            v-for="user in users" 
            :key="user.id" 
            class="user-card"
          >
            <div class="user-actions">
              <button 
                @click.stop="handleDelete(user)" 
                class="btn-delete"
                title="删除用户"
              >
                🗑️
              </button>
            </div>
            <div 
              class="user-card-content"
              @click="$router.push(`/dancers/${user.id}`)"
            >
              <div class="user-avatar">
                {{ user.username.charAt(0).toUpperCase() }}
              </div>
              <h3>{{ user.username }}</h3>
              <p class="email">{{ user.email }}</p>
              <div class="role-badge" :class="user.is_admin ? 'admin' : 'user'">
                {{ user.is_admin ? '管理员' : '普通用户' }}
              </div>
              <div class="stats">
                <span>视频数：{{ user.video_count }}</span>
                <span>注册时间：{{ new Date(user.created_at).toLocaleDateString() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 创建用户模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h2>创建新用户</h2>
        <form @submit.prevent="handleCreate">
          <div class="form-group">
            <label>用户名 *</label>
            <input 
              type="text" 
              v-model="newUser.username" 
              required 
              placeholder="输入用户名"
            />
          </div>
          
          <div class="form-group">
            <label>邮箱 *</label>
            <input 
              type="email" 
              v-model="newUser.email" 
              required 
              placeholder="输入邮箱地址"
            />
          </div>
          
          <div class="form-group">
            <label>密码 *</label>
            <input 
              type="password" 
              v-model="newUser.password" 
              required 
              placeholder="输入初始密码"
            />
          </div>
          
          <div class="form-group">
            <label>描述</label>
            <textarea 
              v-model="newUser.description" 
              placeholder="可选：用户的简介或风格"
              rows="3"
            ></textarea>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="btn-secondary">取消</button>
            <button type="submit" :disabled="creating" class="btn-primary">
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { userAPI } from '../api/modules'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const showToast = inject('toast')
const showConfirm = inject('confirm')

const users = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const creating = ref(false)

// 用户菜单相关
const showUserMenu = ref(false)
const userMenuRef = ref(null)

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  await loadUsers()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const loadUsers = async () => {
  // 普通用户直接返回，不加载数据
  if (!userStore.isAdmin) {
    loading.value = false
    return
  }
  
  try {
    // 只有管理员才能加载用户列表
    const response = await userAPI.getUsers(userStore.userId, userStore.isAdmin)
    users.value = response.users
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

const newUser = reactive({
  username: '',
  email: '',
  password: '',
  description: ''
})

const handleCreate = async () => {
  creating.value = true
  
  try {
    // 管理员创建用户
    await userAPI.createUser({
      admin_user_id: userStore.userId,
      username: newUser.username,
      email: newUser.email,
      password: newUser.password,
      description: newUser.description
    })
    
    showCreateModal.value = false
    newUser.username = ''
    newUser.email = ''
    newUser.password = ''
    newUser.description = ''
    
    await loadUsers()
  } catch (error) {
    showToast('创建失败：' + (error.response?.data?.error || '请稍后重试'), 'error')
  } finally {
    creating.value = false
  }
}

const handleDelete = async (user) => {
  const confirmed = await showConfirm({
    title: '删除用户确认',
    message: `确定要删除用户 "${user.username}" 吗？\n\n警告：此操作将删除该用户的所有数据，包括：\n- 所有上传的视频文件\n- 所有视频缩略图\n- 用户头像\n- 所有分析记录\n- 所有进步追踪记录\n\n此操作不可恢复！`,
    confirmText: '删除',
    cancelText: '取消',
    type: 'danger'
  })
  
  if (!confirmed) {
    return
  }
  
  try {
    await userAPI.deleteUser(user.id)
    showToast('用户已删除', 'success')
    await loadUsers()
  } catch (error) {
    showToast('删除失败：' + (error.response?.data?.error || '请稍后重试'), 'error')
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dancer-list-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.access-denied {
  text-align: center;
  padding: 80px 20px;
  max-width: 500px;
  margin: 0 auto;
}

.access-denied h1 {
  font-size: 36px;
  color: #e74c3c;
  margin-bottom: 20px;
}

.access-denied p {
  font-size: 18px;
  color: #666;
  margin-bottom: 30px;
  line-height: 1.6;
}

.navbar {
  background: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-brand {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
}

.nav-links {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-link {
  color: #333;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background 0.3s;
}

/* 用户头像下拉菜单样式 */
.user-menu {
  position: relative;
}

.avatar-btn {
  cursor: pointer;
  transition: transform 0.2s;
}

.avatar-btn:hover {
  transform: scale(1.1);
}

.avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

.dropdown-menu {
  position: absolute;
  top: 50px;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  min-width: 220px;
  z-index: 1000;
  overflow: hidden;
}

.dropdown-header {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.avatar-medium {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.user-info {
  flex: 1;
}

.username {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.role-badge {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  display: inline-block;
}

.role-badge.admin {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.role-badge.user {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.dropdown-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 8px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: #333;
  text-decoration: none;
  transition: background 0.2s;
  border: none;
  background: none;
  width: 100%;
  cursor: pointer;
  font-size: 14px;
}

.dropdown-item:hover {
  background: #f5f7fa;
}

.dropdown-item.logout-btn {
  color: #e74c3c;
}

.icon {
  font-size: 18px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.admin-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.header h1 {
  font-size: 32px;
  color: #333;
}

.btn-primary {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
}

.loading, .empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 18px;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.user-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  position: relative;
}

.user-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.user-actions {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 10;
}

.btn-delete {
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-delete:hover {
  background: #fdd;
  border-color: #faa;
  transform: scale(1.1);
}

.user-card-content {
  cursor: pointer;
}

.user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 15px;
}

.user-card h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 10px;
}

.email {
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
  line-height: 1.5;
}

.role-badge {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
  margin-bottom: 10px;
}

.role-badge.admin {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.role-badge.user {
  background: #f0f0f0;
  color: #666;
}

.stats {
  color: #999;
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: white;
  padding: 40px;
  border-radius: 12px;
  width: 100%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h2 {
  margin-bottom: 25px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 25px;
}

.btn-secondary {
  padding: 12px 24px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .navbar {
    padding: 15px 20px;
    flex-direction: column;
    gap: 15px;
  }

  .nav-brand {
    font-size: 20px;
  }

  .main-content {
    padding: 30px 15px;
  }

  .header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .header h1 {
    font-size: 26px;
  }

  .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .users-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 20px;
  }

  .user-card {
    padding: 25px;
  }

  .modal {
    padding: 30px 20px;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 12px 15px;
  }

  .nav-brand {
    font-size: 18px;
  }

  .nav-link {
    padding: 6px 12px;
    font-size: 14px;
  }

  .main-content {
    padding: 20px 10px;
  }

  .header h1 {
    font-size: 22px;
  }

  .users-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .user-card {
    padding: 20px;
  }

  .user-avatar {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }

  .user-card h3 {
    font-size: 18px;
  }

  .email {
    font-size: 13px;
  }

  .modal {
    padding: 25px 15px;
  }

  .form-group input,
  .form-group textarea {
    font-size: 16px; /* 防止 iOS 缩放 */
    padding: 10px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
  }
}
</style>
