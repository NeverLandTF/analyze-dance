<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-brand">🎵 舞蹈 AI 分析</div>
      <div class="nav-links">
        <router-link to="/dancers" class="nav-link">舞者管理</router-link>
        <router-link to="/upload" class="nav-link">上传视频</router-link>
        <button @click="handleLogout" class="btn-logout">退出</button>
      </div>
    </nav>
    
    <main class="main-content">
      <div class="welcome-section">
        <h1>欢迎使用舞蹈视频 AI 分析系统</h1>
        <p>通过先进的大模型技术，精准追踪街舞舞者的每一个进步瞬间</p>
      </div>
      
      <div class="features-grid">
        <div class="feature-card" @click="$router.push('/dancers')">
          <div class="feature-icon">👤</div>
          <h3>舞者管理</h3>
          <p>创建和管理多个舞者档案，实现个人数据隔离</p>
        </div>
        
        <div class="feature-card" @click="$router.push('/upload')">
          <div class="feature-icon">📹</div>
          <h3>视频上传</h3>
          <p>上传舞蹈视频，支持多种街舞风格</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🤖</div>
          <h3>AI 分析</h3>
          <p>大模型驱动的动作识别与评分</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>进步追踪</h3>
          <p>可视化展示舞者的成长曲线和趋势</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

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

.btn-logout {
  padding: 8px 20px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s;
}

.btn-logout:hover {
  background: #c0392b;
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
</style>
