<template>
  <div class="profile-container">
    <nav class="navbar">
      <div class="nav-brand">🎵 舞蹈 AI 分析</div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <button @click="handleLogout" class="btn-logout">退出</button>
      </div>
    </nav>
    
    <main class="main-content">
      <div class="profile-card">
        <h1>个人中心</h1>
        
        <div class="profile-info">
          <div class="avatar-large">
            {{ userStore.user?.username?.charAt(0).toUpperCase() }}
          </div>
          
          <div class="info-item">
            <label>用户名：</label>
            <span>{{ userStore.user?.username }}</span>
          </div>
          
          <div class="info-item">
            <label>用户 ID：</label>
            <span>{{ userStore.user?.id }}</span>
          </div>
          
          <div class="info-item">
            <label>角色：</label>
            <span :class="userStore.isAdmin ? 'admin-badge' : 'user-badge'">
              {{ userStore.isAdmin ? '管理员' : '普通用户' }}
            </span>
          </div>
        </div>
        
        <div class="action-buttons">
          <button @click="showPasswordModal = true" class="btn-primary">
            修改密码
          </button>
        </div>
      </div>
    </main>
    
    <!-- 修改密码模态框 -->
    <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
      <div class="modal">
        <h2>修改密码</h2>
        <form @submit.prevent="handleChangePassword">
          <div class="form-group">
            <label>旧密码</label>
            <input 
              type="password" 
              v-model="passwordForm.oldPassword" 
              required 
              placeholder="请输入旧密码"
            />
          </div>
          
          <div class="form-group">
            <label>新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.newPassword" 
              required 
              placeholder="请输入新密码"
              minlength="6"
            />
          </div>
          
          <div class="form-group">
            <label>确认新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.confirmPassword" 
              required 
              placeholder="请再次输入新密码"
              minlength="6"
            />
          </div>
          
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
          <div v-if="passwordSuccess" class="success-message">{{ passwordSuccess }}</div>
          
          <div class="modal-actions">
            <button type="button" @click="showPasswordModal = false" class="btn-secondary">取消</button>
            <button type="submit" :disabled="changingPassword" class="btn-primary">
              {{ changingPassword ? '修改中...' : '确认修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api/modules'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const showPasswordModal = ref(false)
const changingPassword = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const handleChangePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''
  
  // 验证两次输入的密码是否一致
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  
  // 验证新密码长度
  if (passwordForm.newPassword.length < 6) {
    passwordError.value = '新密码长度不能少于 6 位'
    return
  }
  
  changingPassword.value = true
  
  try {
    await authAPI.changePassword(userStore.userId, passwordForm.oldPassword, passwordForm.newPassword)
    
    passwordSuccess.value = '密码修改成功，请重新登录'
    
    // 延迟后退出登录
    setTimeout(() => {
      userStore.logout()
      router.push('/login')
    }, 1500)
  } catch (error) {
    passwordError.value = error.response?.data?.error || '修改密码失败，请稍后重试'
  } finally {
    changingPassword.value = false
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: #f5f7fa;
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

.btn-logout {
  padding: 8px 20px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.profile-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.profile-card h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.avatar-large {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: bold;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 16px;
}

.info-item label {
  color: #666;
  font-weight: 500;
  min-width: 80px;
}

.info-item span {
  color: #333;
}

.admin-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.user-badge {
  background: #e0e0e0;
  color: #666;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
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
  transition: transform 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
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
}

.modal h2 {
  margin-bottom: 25px;
  color: #333;
  text-align: center;
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

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.error-message {
  color: #e74c3c;
  margin-top: 10px;
  text-align: center;
  font-size: 14px;
}

.success-message {
  color: #27ae60;
  margin-top: 10px;
  text-align: center;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 25px;
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

  .profile-card {
    padding: 30px 20px;
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

  .btn-logout {
    padding: 6px 16px;
    font-size: 14px;
  }

  .main-content {
    padding: 20px 10px;
  }

  .profile-card h1 {
    font-size: 24px;
  }

  .avatar-large {
    width: 80px;
    height: 80px;
    font-size: 36px;
  }

  .info-item {
    font-size: 14px;
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
