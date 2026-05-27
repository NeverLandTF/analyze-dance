<template>
  <div class="progress-tracking-container">
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
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>正在加载进步追踪数据...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <h1>😕 加载失败</h1>
        <p>{{ error }}</p>
        <button @click="loadProgress" class="btn-primary">重新加载</button>
      </div>
      
      <div v-else-if="!progressData || !progressData.videos || progressData.videos.length === 0" class="empty-state">
        <h1>📊 暂无追踪数据</h1>
        <p>该舞者还没有足够的分析记录来生成进步追踪</p>
        <button @click="$router.push('/upload')" class="btn-primary">去上传视频</button>
        <button @click="$router.push('/dancers')" class="btn-secondary">返回舞者列表</button>
      </div>
      
      <div v-else class="progress-content">
        <div class="header">
          <button @click="$router.push('/dancers')" class="btn-back">← 返回</button>
          <h1>📈 进步追踪</h1>
          <div class="dancer-name-badge">{{ dancerName }}</div>
        </div>
        
        <!-- 总体趋势概览 -->
        <div class="overview-cards">
          <div class="overview-card">
            <div class="overview-icon">📹</div>
            <div class="overview-value">{{ progressData.videos.length }}</div>
            <div class="overview-label">视频总数</div>
          </div>
          <div class="overview-card">
            <div class="overview-icon">🤖</div>
            <div class="overview-value">{{ progressData.analyzedCount || 0 }}</div>
            <div class="overview-label">已分析视频</div>
          </div>
          <div class="overview-card highlight">
            <div class="overview-icon">⭐</div>
            <div class="overview-value">{{ progressData.latestScore || 0 }}</div>
            <div class="overview-label">最新得分</div>
          </div>
          <div class="overview-card" v-if="progressData.improvement !== undefined">
            <div class="overview-icon">📊</div>
            <div class="overview-value" :class="getImprovementClass(progressData.improvement)">
              {{ progressData.improvement >= 0 ? '+' : '' }}{{ progressData.improvement }}
            </div>
            <div class="overview-label">较上次变化</div>
          </div>
        </div>
        
        <!-- 分数趋势图表区域 -->
        <div class="trend-section">
          <h2>📈 分数趋势</h2>
          <div class="trend-chart">
            <div class="chart-container">
              <div 
                v-for="(video, index) in progressData.videos" 
                :key="video.id" 
                class="chart-bar-wrapper"
              >
                <div class="chart-bar">
                  <div 
                    class="chart-fill" 
                    :style="{ height: getBarHeight(video.overall_score) + '%' }"
                    :title="'得分：' + (video.overall_score || 0)"
                  ></div>
                </div>
                <div class="chart-label">
                  <span class="date">{{ formatDate(video.upload_date) }}</span>
                  <span class="score">{{ video.overall_score || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 各项能力雷达图模拟 -->
        <div class="skills-section">
          <h2>💪 能力分析</h2>
          <div class="skills-grid">
            <div class="skill-item">
              <div class="skill-header">
                <span class="skill-name">技术能力</span>
                <span class="skill-value">{{ latestAnalysis?.technique_score || 0 }}</span>
              </div>
              <div class="skill-bar">
                <div 
                  class="skill-fill" 
                  :style="{ width: (latestAnalysis?.technique_score || 0) + '%' }"
                ></div>
              </div>
            </div>
            
            <div class="skill-item">
              <div class="skill-header">
                <span class="skill-name">节奏感</span>
                <span class="skill-value">{{ latestAnalysis?.rhythm_score || 0 }}</span>
              </div>
              <div class="skill-bar">
                <div 
                  class="skill-fill rhythm" 
                  :style="{ width: (latestAnalysis?.rhythm_score || 0) + '%' }"
                ></div>
              </div>
            </div>
            
            <div class="skill-item">
              <div class="skill-header">
                <span class="skill-name">表现力</span>
                <span class="skill-value">{{ latestAnalysis?.expression_score || 0 }}</span>
              </div>
              <div class="skill-bar">
                <div 
                  class="skill-fill expression" 
                  :style="{ width: (latestAnalysis?.expression_score || 0) + '%' }"
                ></div>
              </div>
            </div>
            
            <div class="skill-item">
              <div class="skill-header">
                <span class="skill-name">完整性</span>
                <span class="skill-value">{{ latestAnalysis?.completeness_score || 0 }}</span>
              </div>
              <div class="skill-bar">
                <div 
                  class="skill-fill completeness" 
                  :style="{ width: (latestAnalysis?.completeness_score || 0) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 历史视频列表 -->
        <div class="history-section">
          <h2>📹 历史视频</h2>
          <div class="videos-list">
            <div 
              v-for="video in progressData.videos" 
              :key="video.id" 
              class="video-row"
              @click="viewVideoAnalysis(video)"
            >
              <div class="video-info">
                <div class="video-title">{{ video.title }}</div>
                <div class="video-meta">
                  <span class="date">📅 {{ formatDateTime(video.upload_date) }}</span>
                  <span v-if="video.dance_style" class="style">💃 {{ getDanceStyleName(video.dance_style) }}</span>
                </div>
              </div>
              <div class="video-score">
                <div v-if="video.overall_score !== null && video.overall_score !== undefined" class="score-badge">
                  {{ video.overall_score }}
                </div>
                <div v-else class="no-score">待分析</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="action-buttons">
          <button @click="$router.push('/dancers')" class="btn-secondary">
            返回舞者列表
          </button>
          <button @click="$router.push('/upload')" class="btn-primary">
            📹 上传新视频
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { progressAPI, videoAPI, userAPI } from '../api/modules'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const showToast = inject('toast')

// 用户菜单相关
const showUserMenu = ref(false)
const userMenuRef = ref(null)

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  loadProgress()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const loading = ref(true)
const error = ref('')
const progressData = ref(null)
const dancerName = ref('舞者')

const latestAnalysis = computed(() => {
  if (!progressData.value || !progressData.value.videos || progressData.value.videos.length === 0) {
    return null
  }
  // 找到最后一个有分析的视频
  const analyzedVideos = progressData.value.videos.filter(v => v.analyses && v.analyses.length > 0)
  if (analyzedVideos.length === 0) return null
  const latest = analyzedVideos[analyzedVideos.length - 1]
  return latest.analyses[0]
})

const loadProgress = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const dancerId = route.params.dancerId
    
    // 获取舞者名称
    try {
      const dancerRes = await userAPI.getUser(dancerId)
      dancerName.value = dancerRes.username || '舞者'
    } catch (e) {
      console.error('获取舞者信息失败:', e)
    }
    
    // 获取进步追踪数据
    try {
      const response = await progressAPI.getProgress(dancerId)
      progressData.value = response
      
      // 如果没有 videos 字段，尝试从 videos 数组构建
      if (!progressData.value.videos && response.videos) {
        progressData.value.videos = response.videos
      }
    } catch (e) {
      console.error('获取进步数据失败:', e)
      // 尝试直接获取视频列表
      const videosRes = await videoAPI.getVideos(userStore.userId, dancerId)
      if (videosRes.videos && videosRes.videos.length > 0) {
        progressData.value = {
          videos: videosRes.videos,
          analyzedCount: videosRes.videos.filter(v => v.analyses && v.analyses.length > 0).length,
          latestScore: videosRes.videos.filter(v => v.analyses && v.analyses.length > 0).pop()?.analyses?.[0]?.overall_score || 0,
          improvement: 0
        }
      } else {
        progressData.value = { videos: [] }
      }
    }
  } catch (err) {
    console.error('加载进步追踪数据失败:', err)
    error.value = '加载失败：' + (err.response?.data?.error || '请稍后重试')
  } finally {
    loading.value = false
  }
}

const getBarHeight = (score) => {
  if (score === null || score === undefined) return 0
  return Math.max(10, score) // 至少显示 10% 高度
}

const getImprovementClass = (improvement) => {
  if (improvement > 0) return 'positive'
  if (improvement < 0) return 'negative'
  return 'neutral'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '--'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getDanceStyleName = (style) => {
  const styleMap = {
    'breaking': '霹雳舞',
    'popping': '机械舞',
    'locking': '锁舞',
    'hiphop': '嘻哈舞',
    'jazz': '爵士舞',
    'contemporary': '现代舞',
    'other': '其他'
  }
  return styleMap[style] || style || '未指定'
}

const viewVideoAnalysis = (video) => {
  if (video.analyses && video.analyses.length > 0) {
    router.push(`/analysis/${video.id}`)
  } else {
    showToast('该视频尚未进行 AI 分析', 'warning')
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.progress-tracking-container {
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

.loading, .error-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
}

.loading p, .error-state p, .empty-state p {
  font-size: 18px;
  color: #666;
  margin: 20px 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state h1, .empty-state h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 15px;
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
  margin: 5px;
  transition: transform 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
}

.btn-secondary {
  padding: 12px 24px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  font-weight: 500;
  margin: 5px;
  transition: transform 0.2s;
}

.btn-secondary:hover {
  transform: translateY(-2px);
}

.progress-content {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.header h1 {
  font-size: 32px;
  color: #333;
  margin: 0;
}

.btn-back {
  padding: 10px 20px;
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #667eea;
  color: white;
}

.dancer-name-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.overview-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
}

.overview-card:hover {
  transform: translateY(-3px);
}

.overview-card.highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.overview-card.highlight .overview-label {
  color: rgba(255, 255, 255, 0.9);
}

.overview-card.highlight .overview-value {
  color: white;
}

.overview-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.overview-value {
  font-size: 36px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 8px;
}

.overview-value.positive {
  color: #4caf50;
}

.overview-value.negative {
  color: #f44336;
}

.overview-value.neutral {
  color: #999;
}

.overview-label {
  font-size: 14px;
  color: #666;
}

.trend-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.trend-section h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 20px;
}

.trend-chart {
  overflow-x: auto;
}

.chart-container {
  display: flex;
  gap: 15px;
  padding: 20px 10px;
  min-height: 200px;
  align-items: flex-end;
}

.chart-bar-wrapper {
  flex: 1;
  min-width: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart-bar {
  width: 100%;
  max-width: 50px;
  height: 150px;
  background: #f0f0f0;
  border-radius: 8px 8px 0 0;
  position: relative;
  overflow: hidden;
}

.chart-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px 8px 0 0;
  transition: height 0.3s ease;
}

.chart-label {
  margin-top: 10px;
  text-align: center;
}

.chart-label .date {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.chart-label .score {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.skills-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.skills-section h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 20px;
}

.skills-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skill-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skill-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.skill-value {
  font-size: 18px;
  font-weight: bold;
  color: #667eea;
}

.skill-bar {
  height: 12px;
  background: #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
}

.skill-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.skill-fill.rhythm {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
}

.skill-fill.expression {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}

.skill-fill.completeness {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
}

.history-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.history-section h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 20px;
}

.videos-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.video-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.video-row:hover {
  background: #e8ecef;
  transform: translateX(5px);
}

.video-info {
  flex: 1;
}

.video-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.video-meta {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #666;
}

.video-meta .date,
.video-meta .style {
  display: flex;
  align-items: center;
  gap: 5px;
}

.video-score {
  flex-shrink: 0;
  margin-left: 15px;
}

.score-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: bold;
}

.no-score {
  background: #f0f0f0;
  color: #999;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
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
    align-items: stretch;
  }

  .header h1 {
    font-size: 26px;
    text-align: center;
  }

  .dancer-name-badge {
    text-align: center;
  }

  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-container {
    gap: 10px;
  }

  .chart-bar {
    max-width: 40px;
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

  .overview-cards {
    grid-template-columns: 1fr;
  }

  .overview-value {
    font-size: 28px;
  }

  .trend-section,
  .skills-section,
  .history-section {
    padding: 20px 15px;
  }

  .video-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .video-score {
    margin-left: 0;
    align-self: flex-end;
  }

  .action-buttons {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
