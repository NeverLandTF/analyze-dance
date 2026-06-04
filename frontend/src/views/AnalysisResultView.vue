<template>
  <div class="analysis-result-container">
    <nav class="navbar">
      <router-link to="/" class="nav-brand">🎵 舞蹈 AI 分析</router-link>
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
        <p>正在加载分析结果...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <h1>😕 加载失败</h1>
        <p>{{ error }}</p>
        <button @click="loadAnalysis" class="btn-primary">重新加载</button>
      </div>
      
      <div v-else-if="!analysis || Object.keys(analysis).length === 0" class="empty-state">
        <h1>📊 暂无分析结果</h1>
        <p>该视频尚未进行 AI 分析</p>
        <button @click="startAnalysis" class="btn-primary">开始 AI 分析</button>
        <button @click="goBackToHistory" class="btn-secondary">← 返回分析历史</button>
      </div>
      
      <div v-else class="analysis-content">
        <div class="header">
          <button @click="goBackToHistory" class="btn-back">← 返回分析历史</button>
          <h1>🤖 AI 分析报告</h1>
          <div class="header-actions">
            <button @click="reanalyze" class="btn-analyze">🔄 重新分析</button>
          </div>
        </div>
        
        <div class="video-info-card">
          <h2>📹 视频信息</h2>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">视频标题：</span>
              <span class="video-title-text" @click="showVideoPreview = true" style="cursor: pointer;">{{ videoInfo?.title || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="label">舞蹈风格：</span>
              <span class="value">{{ getDanceStyleName(videoInfo?.dance_style) }}</span>
            </div>
            <div class="info-item">
              <span class="label">上传时间：</span>
              <span class="value">{{ formatDateTime(videoInfo?.upload_date) }}</span>
            </div>
            <div class="info-item">
              <span class="label">分析时间：</span>
              <span class="value">{{ formatDateTime(analysis.analyzed_at) }}</span>
            </div>
          </div>
        </div>
        
        <!-- 视频预览弹窗 -->
        <div v-if="showVideoPreview" class="modal-overlay" @click.self="showVideoPreview = false">
          <div class="preview-modal">
            <div class="modal-header">
              <h2>{{ videoInfo?.title || '视频预览' }}</h2>
              <button @click="showVideoPreview = false" class="btn-close">×</button>
            </div>
            <div class="modal-body">
              <video 
                ref="videoPlayerRef"
                v-if="videoInfo?.video_url" 
                :src="getVideoUrl(videoInfo.video_url)" 
                controls 
                autoplay
                class="video-player-full"
              >
                您的浏览器不支持视频播放
              </video>
              <div v-else class="no-video">暂无视频资源</div>
            </div>
          </div>
        </div>
        
        <div class="score-overview">
          <h2>📈 综合评分</h2>
          <div class="score-cards">
            <div class="score-card total">
              <div class="score-value">{{ analysis.overall_score || 0 }}</div>
              <div class="score-label">综合得分</div>
            </div>
            <div class="score-card">
              <div class="score-value">{{ analysis.technique_score || 0 }}</div>
              <div class="score-label">技术分</div>
            </div>
            <div class="score-card">
              <div class="score-value">{{ analysis.rhythm_score || 0 }}</div>
              <div class="score-label">节奏分</div>
            </div>
            <div class="score-card">
              <div class="score-value">{{ analysis.expression_score || 0 }}</div>
              <div class="score-label">表现力分</div>
            </div>
            <div class="score-card">
              <div class="score-value">{{ analysis.completeness_score || 0 }}</div>
              <div class="score-label">完整性分</div>
            </div>
          </div>
        </div>
        
        <div class="detailed-feedback">
          <h2>💡 详细反馈</h2>
          <div class="feedback-sections">
            <div class="feedback-section">
              <h3>✨ 优点</h3>
              <ul class="feedback-list positive">
                <li v-for="(item, index) in (analysis.strengths || [])" :key="index">
                  {{ item }}
                </li>
                <li v-if="!analysis.strengths || analysis.strengths.length === 0">暂无数据</li>
              </ul>
            </div>
            
            <div class="feedback-section">
              <h3>🎯 需要改进</h3>
              <ul class="feedback-list improvement">
                <li v-for="(item, index) in (analysis.improvements || [])" :key="index">
                  {{ item }}
                </li>
                <li v-if="!analysis.improvements || analysis.improvements.length === 0">暂无数据</li>
              </ul>
            </div>
          </div>
        </div>
        
        <div class="movement-analysis" v-if="analysis.movements && analysis.movements.length > 0">
          <h2>🦴 动作分析</h2>
          <div class="movements-timeline">
            <div 
              v-for="(move, index) in analysis.movements" 
              :key="index" 
              class="movement-item"
            >
              <div class="movement-time" @click="openVideoAtTime(move.timestamp)">
                <span class="time-badge">{{ formatTime(move.timestamp) }}</span>
              </div>
              <div class="movement-content">
                <div class="movement-name">{{ move.name }}</div>
                <div class="movement-quality" v-if="move.quality">
                  <span class="quality-label">质量：</span>
                  <span class="quality-value" :class="getQualityClass(move.quality)">
                    {{ move.quality }}
                  </span>
                </div>
                <div class="movement-comment" v-if="move.comment">
                  {{ move.comment }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="ai-suggestions">
          <h2>📚 AI 建议</h2>
          <div class="suggestions-list">
            <div 
              v-for="(suggestion, index) in (analysis.suggestions || [])" 
              :key="index" 
              class="suggestion-item"
            >
              <span class="suggestion-icon">💡</span>
              <span class="suggestion-text">{{ suggestion }}</span>
            </div>
            <div v-if="!analysis.suggestions || analysis.suggestions.length === 0" class="no-data">
              暂无具体建议
            </div>
          </div>
        </div>
        
        <div class="action-buttons">
          <button @click="goBackToHistory" class="btn-secondary">
            ← 返回分析历史
          </button>
          <button @click="viewProgress" class="btn-primary" v-if="videoInfo?.user_id">
            查看进步追踪
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { analysisAPI, videoAPI } from '../api/modules'
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
  loadAnalysis()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const loading = ref(true)
const error = ref('')
const analysis = ref(null)
const videoInfo = ref(null)
const showVideoPreview = ref(false)
const videoPlayerRef = ref(null)

// 打开视频预览并定位到指定时间（减 500ms，慢动作播放）
const openVideoAtTime = (timestamp) => {
  if (timestamp === undefined || timestamp === null) return
  
  showVideoPreview.value = true
  
  // 等待 DOM 更新后操作 video 元素
  setTimeout(() => {
    const video = videoPlayerRef.value
    if (video) {
      // 定位到指定时间减 500ms
      video.currentTime = Math.max(0, timestamp - 0.5)
      // 设置慢动作播放（0.5 倍速）
      video.playbackRate = 0.5
      // 自动播放
      video.play().catch(err => {
        console.log('自动播放被阻止:', err)
      })
    }
  }, 100)
}

const loadAnalysis = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const analysisId = route.params.analysisId
    
    // 调用后端新增的 analysis 详情查询接口
    const response = await analysisAPI.getAnalysisDetail(analysisId)
    
    if (response) {
      // 将 result_data 中的数据合并到 analysis 对象中，以便模板可以直接访问
      analysis.value = {
        ...response.result_data,  // 展开 result_data 中的字段（overall_score, strengths, improvements 等）
        id: response.id,
        analysis_type: response.analysis_type,
        confidence_score: response.confidence_score,
        analyzed_at: response.processed_at  // 使用 processed_at 作为 analyzed_at
      }
      
      // 获取关联的视频信息
      if (response.video_id) {
        const videoResponse = await videoAPI.getVideo(response.video_id)
        videoInfo.value = videoResponse
      }
    } else {
      analysis.value = null
    }
  } catch (err) {
    console.error('加载分析结果失败:', err)
    error.value = '加载分析结果失败：' + (err.response?.data?.error || '请稍后重试')
  } finally {
    loading.value = false
  }
}

const startAnalysis = async () => {
  try {
    loading.value = true
    const result = await analysisAPI.analyzeVideo(videoInfo.value.id, userStore.userId)
    showToast('AI 分析完成！', 'success')
    await loadAnalysis()
  } catch (err) {
    console.error('AI 分析失败:', err)
    showToast('AI 分析失败：' + (err.response?.data?.error || '请稍后重试'), 'error')
  } finally {
    loading.value = false
  }
}

// 重新分析（更新原记录，不生成新记录）
const reanalyze = async () => {
  if (!analysis.value?.id) {
    showToast('当前没有可重新分析的报告', 'error')
    return
  }
  
  // 确认提示
  if (!confirm('确定要重新分析此视频吗？这将更新当前的分析报告，不会生成新记录。')) {
    return
  }
  
  try {
    loading.value = true
    const result = await analysisAPI.reanalyzeVideo(analysis.value.id)
    showToast('重新分析完成！', 'success')
    await loadAnalysis()
  } catch (err) {
    console.error('重新分析失败:', err)
    showToast('重新分析失败：' + (err.response?.data?.error || '请稍后重试'), 'error')
  } finally {
    loading.value = false
  }
}

const getDanceStyleName = (style) => {
  const styleMap = {
    'breaking': '霹雳舞',
    'popping': '机械舞',
    'locking': '锁舞',
    'hiphop': '嘻哈舞',
    'jazz': '爵士舞',
    'contemporary': '现代舞',
    'choreography': '编舞',
    'heels': '高跟鞋舞',
    'waacking': '甩手舞',
    'tutting': '手指舞',
    'krump': '狂派舞',
    'house': '浩室舞',
    'urban': '都市舞',
    'kpop': '韩舞',
    'ballet': '芭蕾舞',
    'other': '其他'
  }
  return styleMap[style] || style || '未指定'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '--'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatTime = (seconds) => {
  if (seconds === undefined || seconds === null) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const getQualityClass = (quality) => {
  if (!quality) return ''
  const q = quality.toLowerCase()
  if (q.includes('优秀') || q.includes('excellent') || q.includes('good')) return 'quality-good'
  if (q.includes('一般') || q.includes('fair')) return 'quality-fair'
  if (q.includes('需改进') || q.includes('poor')) return 'quality-poor'
  return ''
}

const viewProgress = () => {
  router.push('/progress')
}

// 返回分析历史页面，并滚动定位到当前分析记录
const goBackToHistory = () => {
  const analysisId = route.params.analysisId
  // 跳转到分析历史页面，并传递 analysisId 作为 hash 用于滚动定位
  router.push({
    path: '/analysis-history',
    hash: `#analysis-${analysisId}`
  })
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 获取视频 URL（添加 /api 前缀）
const getVideoUrl = (filePath) => {
  if (!filePath) return ''
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
  return `${baseURL}${filePath}`
}
</script>

<style scoped>
.analysis-result-container {
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
  text-decoration: none;
  cursor: pointer;
}

.nav-brand:hover {
  opacity: 0.8;
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

.analysis-content {
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

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-analyze {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s;
}

.btn-analyze:hover {
  transform: translateY(-2px);
}

.video-info-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.video-info-card h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item .label {
  font-size: 14px;
  color: #999;
}

.info-item .value {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.video-title-text {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #333;
  font-weight: 500;
}

.video-title-text:hover {
  color: #667eea;
}

.score-overview {
  background: white;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.score-overview h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 20px;
}

.score-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.score-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  transition: transform 0.2s;
}

.score-card:hover {
  transform: translateY(-3px);
}

.score-card.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.score-card.total .score-value {
  color: white;
}

.score-card.total .score-label {
  color: rgba(255, 255, 255, 0.9);
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 8px;
}

.score-label {
  font-size: 14px;
  color: #666;
}

.detailed-feedback {
  background: white;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.detailed-feedback h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 20px;
}

.feedback-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.feedback-section h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.feedback-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feedback-list li {
  padding: 12px 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 10px;
  font-size: 15px;
  line-height: 1.5;
}

.feedback-list.positive li {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.feedback-list.improvement li {
  background: #fff3e0;
  border-left: 4px solid #ff9800;
}

.movement-analysis {
  background: white;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.movement-analysis h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 20px;
}

.movements-timeline {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.movement-item {
  display: flex;
  gap: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
  align-items: flex-start;
}

.movement-time {
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.2s;
}

.movement-time:hover {
  transform: scale(1.05);
}

.time-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  display: inline-block;
}

.movement-content {
  flex: 1;
}

.movement-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.movement-quality {
  margin-bottom: 8px;
}

.quality-label {
  font-size: 14px;
  color: #666;
}

.quality-value {
  font-size: 14px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
  margin-left: 5px;
}

.quality-good {
  background: #e8f5e9;
  color: #2e7d32;
}

.quality-fair {
  background: #fff3e0;
  color: #f57c00;
}

.quality-poor {
  background: #ffebee;
  color: #c62828;
}

.movement-comment {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.ai-suggestions {
  background: white;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.ai-suggestions h2 {
  font-size: 22px;
  color: #333;
  margin-bottom: 20px;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 15px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  border-radius: 10px;
}

.suggestion-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.suggestion-text {
  font-size: 15px;
  color: #333;
  line-height: 1.6;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 20px;
  font-size: 15px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

/* 视频预览弹窗样式 - 与其他页面一致 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.preview-modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  font-size: 22px;
  color: #333;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 5px 10px;
  transition: color 0.2s;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 25px;
}

.video-player-full {
  width: 100%;
  max-height: 500px;
  background: #000;
  border-radius: 8px;
}

.no-video {
  text-align: center;
  color: #999;
  padding: 40px;
  font-size: 16px;
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

  .header-actions {
    justify-content: center;
  }

  .score-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .feedback-sections {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
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

  .score-cards {
    grid-template-columns: 1fr;
  }

  .score-value {
    font-size: 28px;
  }

  .video-info-card,
  .score-overview,
  .detailed-feedback,
  .movement-analysis,
  .ai-suggestions {
    padding: 20px 15px;
  }

  .movement-item {
    flex-direction: column;
    gap: 10px;
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
