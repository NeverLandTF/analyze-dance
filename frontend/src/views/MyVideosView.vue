<template>
  <div class="my-videos-container">
    <nav class="navbar">
      <div class="nav-brand">🎵 舞蹈 AI 分析</div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link v-if="userStore.isAdmin" to="/dancers" class="nav-link">用户管理</router-link>
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
      <div class="header">
        <h1>我的视频</h1>
        <button @click="$router.push('/upload')" class="btn-primary">
          📹 上传新视频
        </button>
      </div>
      
      <!-- 视频列表 -->
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="videos.length === 0" class="empty-state">
        <div class="empty-icon">📹</div>
        <p>暂无上传的视频</p>
        <button @click="$router.push('/upload')" class="btn-secondary">去上传第一个视频</button>
      </div>
      <div v-else class="videos-grid">
        <div v-for="video in videos" :key="video.id" class="video-card">
          <div class="video-thumbnail" @click="openPreviewModal(video)">
            <!-- 仅显示封面图，不加载视频内容 -->
            <img 
              v-if="video.thumbnail_url" 
              :src="getThumbnailUrl(video.thumbnail_url)" 
              alt="视频封面"
              class="thumbnail-image"
            />
            <div v-else class="thumbnail-placeholder">
              <span class="play-icon">▶</span>
              <span class="video-duration">{{ video.duration || '--:--' }}</span>
            </div>
            <div class="thumbnail-overlay">
              <span class="preview-text">点击预览</span>
            </div>
          </div>
          <div class="video-info">
            <h3>{{ video.title }}</h3>
            <p class="video-meta">
              <span v-if="video.dance_style" class="dance-style">{{ getDanceStyleName(video.dance_style) }}</span>
              <span class="upload-date">{{ formatDate(video.upload_date) }}</span>
            </p>
            <div class="video-actions">
              <button @click="openPreviewModal(video)" class="btn-small">
                ▶ 预览
              </button>
              <button @click="analyzeVideo(video)" class="btn-small btn-analyze-small">
                🤖 AI 分析
              </button>
              <button @click="viewAnalysisResult(video)" class="btn-small btn-view-small" v-if="hasAnalysis(video)">
                📊 查看结果
              </button>
              <button @click="confirmDeleteVideo(video)" class="btn-small btn-delete-small">
                🗑️ 删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 视频预览弹窗 -->
    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="preview-modal">
        <div class="modal-header">
          <h2>{{ currentVideo?.title }}</h2>
          <button @click="closePreviewModal" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <video 
            ref="videoPlayer"
            :src="getVideoUrl(currentVideo?.file_path)" 
            controls 
            autoplay
            class="video-player-full"
          ></video>
          <div class="video-details">
            <div class="detail-item">
              <span class="label">舞蹈风格：</span>
              <span class="value">{{ getDanceStyleName(currentVideo?.dance_style) || '未指定' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">上传时间：</span>
              <span class="value">{{ formatDateTime(currentVideo?.upload_date) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">时长：</span>
              <span class="value">{{ currentVideo?.duration || '--:--' }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="analyzeCurrentVideo" class="btn-analyze">
            🤖 开始 AI 分析
          </button>
          <button @click="viewCurrentAnalysis" class="btn-secondary" v-if="hasAnalysis(currentVideo)">
            📊 查看分析结果
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { videoAPI, analysisAPI } from '../api/modules'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

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
  loadVideos()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 视频列表相关
const videos = ref([])
const loading = ref(false)

// 预览弹窗相关
const showPreviewModal = ref(false)
const currentVideo = ref(null)
const videoPlayer = ref(null)

// 加载视频列表 - 仅获取基本信息（封面、标题等），不加载视频内容
const loadVideos = async () => {
  try {
    loading.value = true
    const response = await videoAPI.getVideos(userStore.userId)
    videos.value = response.videos
  } catch (error) {
    console.error('加载视频列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取封面图 URL
const getThumbnailUrl = (thumbnailPath) => {
  if (!thumbnailPath) return ''
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
  return `${baseURL}${thumbnailPath}`
}

// 获取视频 URL
const getVideoUrl = (filePath) => {
  if (!filePath) return ''
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
  return `${baseURL}${filePath}`
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 格式化详细日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 获取舞蹈风格名称
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
  return styleMap[style] || style
}

// 检查是否有分析结果
const hasAnalysis = (video) => {
  return video.analyses && video.analyses.length > 0
}

// 打开预览弹窗
const openPreviewModal = (video) => {
  currentVideo.value = video
  showPreviewModal.value = true
}

// 关闭预览弹窗
const closePreviewModal = () => {
  showPreviewModal.value = false
  // 停止视频播放
  if (videoPlayer.value) {
    videoPlayer.value.pause()
    videoPlayer.value.currentTime = 0
  }
  currentVideo.value = null
}

// 分析视频
const analyzeVideo = async (video) => {
  try {
    const result = await analysisAPI.analyzeVideo(video.id, userStore.userId)
    alert('AI 分析完成！')
    // 重新加载视频列表以更新分析状态
    await loadVideos()
    router.push(`/analysis/${video.id}`)
  } catch (error) {
    console.error('AI 分析失败:', error)
    alert('AI 分析失败：' + (error.response?.data?.error || '请稍后重试'))
  }
}

// 分析当前视频（从弹窗中）
const analyzeCurrentVideo = async () => {
  if (!currentVideo.value) return
  await analyzeVideo(currentVideo.value)
}

// 查看分析结果
const viewAnalysisResult = (video) => {
  router.push(`/analysis/${video.id}`)
}

// 查看当前视频的分析结果（从弹窗中）
const viewCurrentAnalysis = () => {
  if (!currentVideo.value) return
  viewAnalysisResult(currentVideo.value)
}

// 删除视频确认
const confirmDeleteVideo = async (video) => {
  if (!confirm(`确定要删除视频"${video.title}"吗？删除后分析记录也将被同步删除，此操作不可恢复。`)) {
    return
  }
  
  try {
    await videoAPI.deleteVideo(video.id)
    alert('视频已删除')
    // 重新加载视频列表
    await loadVideos()
  } catch (error) {
    console.error('删除视频失败:', error)
    alert('删除失败：' + (error.response?.data?.error || '请稍后重试'))
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.my-videos-container {
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
  padding: 40px 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
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
  transition: transform 0.2s;
}

.btn-secondary:hover {
  transform: translateY(-2px);
}

.loading, .empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state p {
  font-size: 18px;
  margin-bottom: 20px;
}

.videos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.video-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}

.video-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.video-thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 比例 */
  background: #000;
  cursor: pointer;
  overflow: hidden;
}

.thumbnail-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}

.play-icon {
  font-size: 48px;
  opacity: 0.9;
}

.video-duration {
  margin-top: 10px;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.6);
  padding: 4px 8px;
  border-radius: 4px;
}

.thumbnail-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.video-thumbnail:hover .thumbnail-overlay {
  opacity: 1;
}

.preview-text {
  color: white;
  font-size: 16px;
  font-weight: 600;
  background: rgba(102, 126, 234, 0.9);
  padding: 10px 20px;
  border-radius: 20px;
}

.video-info {
  padding: 20px;
}

.video-info h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  font-size: 13px;
}

.dance-style {
  background: #f0f0f0;
  padding: 3px 8px;
  border-radius: 12px;
  color: #666;
}

.upload-date {
  color: #999;
}

.video-actions {
  display: flex;
  gap: 8px;
}

.btn-small {
  flex: 1;
  padding: 8px 12px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-small:hover {
  background: #e0e0e0;
}

.btn-analyze-small {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-analyze-small:hover {
  background: linear-gradient(135deg, #5568d3 0%, #6a4190 100%);
}

.btn-view-small {
  background: #e8f5e9;
  color: #2e7d32;
}

.btn-view-small:hover {
  background: #c8e6c9;
}

.btn-delete-small {
  background: #ffebee;
  color: #c62828;
}

.btn-delete-small:hover {
  background: #ffcdd2;
}

/* 预览弹窗样式 */
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

.video-details {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.detail-item {
  display: flex;
  margin-bottom: 10px;
  font-size: 14px;
}

.label {
  color: #666;
  font-weight: 500;
  width: 100px;
}

.value {
  color: #333;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 25px;
  border-top: 1px solid #e0e0e0;
}

.btn-analyze {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s;
}

.btn-analyze:hover {
  transform: translateY(-2px);
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

  .videos-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 20px;
  }

  .preview-modal {
    max-width: 100%;
  }

  .modal-footer {
    flex-direction: column;
  }

  .btn-analyze,
  .btn-secondary {
    width: 100%;
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

  .videos-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .video-info h3 {
    font-size: 16px;
  }

  .video-actions {
    flex-wrap: wrap;
  }

  .btn-small {
    flex: 1 1 calc(50% - 4px);
  }
}
</style>
