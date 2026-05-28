<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-brand">🎵 舞蹈 AI 分析</div>
      <div class="nav-links">
        <span v-if="userStore.isAdmin" class="admin-badge-nav">管理员</span>
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link v-if="userStore.isAdmin" to="/dancers" class="nav-link">用户管理</router-link>
        <router-link to="/my-videos" class="nav-link">我的视频</router-link>
        <router-link to="/upload" class="nav-link">上传视频</router-link>
        
        <!-- 用户头像下拉菜单 -->
        <div class="user-menu" ref="userMenuRef">
          <div class="avatar-btn" @click="toggleUserMenu">
            <img 
              v-if="userStore.user?.avatar_url" 
              :src="userStore.user.avatar_url" 
              alt="avatar"
              class="avatar-small-img"
            />
            <div v-else class="avatar-small">
              {{ userStore.user?.username?.charAt(0).toUpperCase() }}
            </div>
          </div>
          
          <div v-if="showUserMenu" class="dropdown-menu">
            <div class="dropdown-header">
              <img 
                v-if="userStore.user?.avatar_url" 
                :src="userStore.user.avatar_url" 
                alt="avatar"
                class="avatar-medium-img"
              />
              <div v-else class="avatar-medium">
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
      <div class="welcome-section">
        <h1>欢迎使用舞蹈视频 AI 分析系统</h1>
        <p>通过先进的大模型技术，精准追踪街舞舞者的每一个进步瞬间</p>
      </div>
      
      <div class="features-grid">
        <div class="feature-card" @click="$router.push('/dancers')" v-if="userStore.isAdmin">
          <div class="feature-icon">👤</div>
          <h3>用户管理</h3>
          <p>管理员可以创建和管理用户，每个用户即代表一个舞者</p>
        </div>
        
        <div class="feature-card" @click="$router.push('/my-videos')">
          <div class="feature-icon">📹</div>
          <h3>我的视频</h3>
          <p>查看和管理已上传的舞蹈视频，支持预览和 AI 分析</p>
        </div>
        
        <div class="feature-card" @click="$router.push('/upload')">
          <div class="feature-icon">⬆️</div>
          <h3>视频上传</h3>
          <p>上传新的舞蹈视频，支持多种街舞风格</p>
        </div>
        
        <div class="feature-card" @click="$router.push('/analysis-history')">
          <div class="feature-icon">🤖</div>
          <h3>AI 分析</h3>
          <p>查看 AI 分析历史记录，点击某次分析进入详情</p>
        </div>
        
        <div class="feature-card" @click="$router.push('/progress-tracking')">
          <div class="feature-icon">📊</div>
          <h3>进步追踪</h3>
          <p>可视化展示舞者的成长曲线和趋势</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { authAPI } from '../api/modules'

const router = useRouter()
const userStore = useUserStore()

const showUserMenu = ref(false)
const userMenuRef = ref(null)

// 加载用户最新信息（包括头像）
onMounted(async () => {
  if (userStore.userId) {
    try {
      const userInfo = await authAPI.getUser(userStore.userId)
      if (userInfo && userInfo.avatar_url) {
        userStore.updateUser({ avatar_url: userInfo.avatar_url })
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
  
  // 监听点击外部事件
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.home-container {
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
  position: sticky;
  top: 0;
  z-index: 1000;
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

.nav-link:hover {
  background: #f0f0f0;
}

.admin-badge-nav {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
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

.avatar-small-img,
.avatar-medium-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
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

.avatar-medium-img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
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
  padding: 60px 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 60px;
}

.welcome-section h1 {
  font-size: 42px;
  color: #333;
  margin-bottom: 15px;
}

.welcome-section p {
  font-size: 18px;
  color: #666;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 22px;
  color: #333;
  margin-bottom: 12px;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
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

  .nav-links {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .main-content {
    padding: 40px 15px;
  }

  .welcome-section h1 {
    font-size: 28px;
  }

  .welcome-section p {
    font-size: 16px;
  }

  .features-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
  }

  .feature-card {
    padding: 30px 20px;
  }

  .feature-icon {
    font-size: 40px;
  }

  .feature-card h3 {
    font-size: 18px;
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
    padding: 30px 10px;
  }

  .welcome-section {
    margin-bottom: 40px;
  }

  .welcome-section h1 {
    font-size: 24px;
  }

  .welcome-section p {
    font-size: 14px;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .feature-card {
    padding: 25px 20px;
  }
}
</style>
