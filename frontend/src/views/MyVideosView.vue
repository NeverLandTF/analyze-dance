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
      
      <!-- 舞者选择器 (仅管理员) -->
      <div v-if="userStore.isAdmin" class="dancer-filter-section">
        <div class="filter-group">
          <label class="filter-label">👤 选择舞者：</label>
          <select v-model="selectedDancerId" @change="handleDancerChange" class="dancer-select">
            <option value="">全部舞者</option>
            <option v-for="dancer in dancers" :key="dancer.id" :value="dancer.id">
              {{ dancer.username }}
            </option>
          </select>
        </div>
      </div>
      
      <!-- 时间过滤器 -->
      <div class="filter-section">
        <div class="filter-group">
          <label class="filter-label">📅 按时间筛选：</label>
          <div class="time-filters">
            <button 
              v-for="option in timeFilterOptions" 
              :key="option.value"
              @click="handleTimeFilterChange(option.value)"
              :class="['filter-btn', { active: selectedTimeFilter === option.value }]"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
        <div class="filter-group date-range-group">
          <label class="filter-label">自定义范围：</label>
          <div class="date-range-inputs">
            <div class="date-input-wrapper">
              <input 
                type="date" 
                v-model="startDate" 
                class="date-input"
                :max="endDate || new Date().toISOString().split('T')[0]"
              />
            </div>
            <span class="date-separator">至</span>
            <div class="date-input-wrapper">
              <input 
                type="date" 
                v-model="endDate" 
                class="date-input"
                :min="startDate"
                :max="new Date().toISOString().split('T')[0]"
              />
            </div>
            <button @click="applyDateRange" class="btn-apply-date">应用</button>
            <button @click="clearDateRange" class="btn-clear-date">清除</button>
          </div>
        </div>
      </div>
      
      <!-- 视频列表 -->
      <div v-if="loading && videos.length === 0" class="loading">加载中...</div>
      <div v-else-if="videos.length === 0" class="empty-state">
        <div class="empty-icon">📹</div>
        <p>{{ '暂无上传的视频' }}</p>
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
              <span class="video-duration">{{ formatDuration(video.duration) }}</span>
            </div>
            <div class="thumbnail-overlay">
              <span class="preview-text">点击预览</span>
            </div>
          </div>
          <div class="video-info">
            <h3>{{ video.title }}</h3>
            <p class="video-meta">
              <span v-if="video.dance_style" class="dance-style">{{ getDanceStyleName(video.dance_style) }}</span>
              <span class="upload-date" :title="formatDateTime(video.upload_date)">{{ formatDate(video.upload_date) }}</span>
            </p>
            <div class="video-actions">
              <button @click="openPreviewModal(video)" class="btn-small">
                ▶ 预览
              </button>
              <button 
                v-if="hasAnalysis(video)"
                @click="viewAnalysisResult(video)" 
                class="btn-small btn-analyze-small"
              >
                📊 查看
              </button>
              <button 
                v-else
                @click="analyzeVideo(video)" 
                class="btn-small btn-analyze-small"
                :disabled="analyzingVideos[video.id]"
              >
                <span v-if="analyzingVideos[video.id]" class="loading-spinner">⏳</span>
                <span v-else>🤖 AI 分析</span>
              </button>
              <button @click="confirmDeleteVideo(video)" class="btn-small btn-delete-small">
                🗑️ 删除
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 滚动加载更多 -->
      <div v-if="isLoadingMore" class="loading-more">加载中...</div>
      <div v-else-if="hasMore && videos.length > 0" class="load-more-trigger" ref="loadMoreTrigger"></div>
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
              <span class="value">{{ formatDuration(currentVideo?.duration) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">文件格式：</span>
              <span class="value">{{ currentVideo?.file_format?.toUpperCase() || '--' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">文件大小：</span>
              <span class="value">{{ formatFileSize(currentVideo?.file_size) }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button 
            v-if="currentVideo && hasAnalysis(currentVideo)"
            @click="viewCurrentAnalysis" 
            class="btn-analyze"
          >
            📊 查看最新分析
          </button>
          <button 
            v-else
            @click="analyzeCurrentVideo" 
            class="btn-analyze"
            :disabled="currentVideo && analyzingVideos[currentVideo.id]"
          >
            <span v-if="currentVideo && analyzingVideos[currentVideo.id]" class="loading-spinner">⏳</span>
            <span v-else>🤖 AI 分析</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, inject, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { videoAPI, analysisAPI, userAPI } from '../api/modules'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const showToast = inject('toast')
const showConfirm = inject('confirm')

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

// 滚动加载更多相关
const loadMoreTrigger = ref(null)
let observer = null

const setupInfiniteScroll = () => {
  // 清理旧的观察者
  if (observer) {
    observer.disconnect()
  }
  
  // 创建 Intersection Observer
  observer = new IntersectionObserver((entries) => {
    const entry = entries[0]
    if (entry.isIntersecting && hasMore.value && !isLoadingMore.value) {
      loadMoreVideos()
    }
  }, {
    rootMargin: '100px' // 提前 100px 开始加载
  })
  
  // 观察触发元素
  nextTick(() => {
    if (loadMoreTrigger.value) {
      observer.observe(loadMoreTrigger.value)
    }
  })
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // 如果是管理员，加载舞者列表
  if (userStore.isAdmin) {
    loadDancers()
  }
  loadVideos().then(() => {
    // 初始加载后设置无限滚动
    setupInfiniteScroll()
  })
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  if (observer) {
    observer.disconnect()
  }
})

// 监听筛选条件变化，重新加载视频并重置滚动
const watchFilterChange = () => {
  // 当时间筛选条件改变时，会触发 applyDateRange 或 clearDateRange，它们已经调用了 loadVideos
  // loadVideos 会重置 currentPage 和 videos 数组，然后 setupInfiniteScroll 会重新设置观察者
  nextTick(() => {
    setupInfiniteScroll()
  })
}

// 视频列表相关
const videos = ref([])
const loading = ref(false)
// 记录每个视频的分析状态
const analyzingVideos = reactive({})
// 记录每个视频最新分析的 analysis_id（调用 /analyze 接口返回的）
const latestAnalysisIds = reactive({})

// 舞者过滤相关 (仅管理员)
const selectedDancerId = ref('')
const dancers = ref([])

// 分页相关
const currentPage = ref(1)
const perPage = 10
const hasMore = ref(true)
const isLoadingMore = ref(false)

// 时间过滤相关
const selectedTimeFilter = ref('all')
const startDate = ref('')
const endDate = ref('')
const timeFilterOptions = [
  { label: '全部', value: 'all' },
  { label: '最近 7 天', value: '7days' },
  { label: '最近 30 天', value: '30days' },
  { label: '最近 90 天', value: '90days' }
]

// 预览弹窗相关
const showPreviewModal = ref(false)
const currentVideo = ref(null)
const videoPlayer = ref(null)

// 获取当前筛选条件下的日期范围
const getDateRangeFromFilter = () => {
  // 如果有自定义日期范围，优先使用
  if (startDate.value && endDate.value) {
    return { startDate: startDate.value, endDate: endDate.value }
  }
  
  const now = new Date()
  
  // 根据预设的时间选项计算日期范围
  if (selectedTimeFilter.value === 'all') {
    return {}
  }
  
  const daysMap = {
    '7days': 7,
    '30days': 30,
    '90days': 90
  }
  
  const days = daysMap[selectedTimeFilter.value]
  if (!days) return {}
  
  const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  return {
    startDate: cutoffDate.toISOString().split('T')[0],
    endDate: now.toISOString().split('T')[0]
  }
}

// 加载更多视频（滚动加载）
const loadMoreVideos = async () => {
  if (isLoadingMore.value || !hasMore.value) return
  
  currentPage.value++
  await loadVideos(true)
}

// 根据时间过滤条件过滤视频
const filterVideosByTime = (videos) => {
  const now = new Date()
  
  // 如果有自定义日期范围，优先使用
  if (startDate.value && endDate.value) {
    const start = new Date(startDate.value)
    const end = new Date(endDate.value)
    end.setHours(23, 59, 59, 999) // 包含结束日期的整天
    
    return videos.filter(video => {
      if (!video.upload_date) return false
      const videoDate = new Date(video.upload_date)
      return videoDate >= start && videoDate <= end
    })
  }
  
  // 根据预设的时间选项过滤
  if (selectedTimeFilter.value === 'all') {
    return videos
  }
  
  const daysMap = {
    '7days': 7,
    '30days': 30,
    '90days': 90
  }
  
  const days = daysMap[selectedTimeFilter.value]
  if (!days) return videos
  
  const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  
  return videos.filter(video => {
    if (!video.upload_date) return false
    const videoDate = new Date(video.upload_date)
    return videoDate >= cutoffDate
  })
}

// 清除自定义日期范围
const clearDateRange = () => {
  startDate.value = ''
  endDate.value = ''
  selectedTimeFilter.value = 'all'
  // 重新加载视频列表
  loadVideos()
}

// 应用自定义日期范围
const applyDateRange = () => {
  selectedTimeFilter.value = 'custom'
  // 重新加载视频列表
  loadVideos()
}

// 监听时间筛选器变化
const handleTimeFilterChange = (value) => {
  selectedTimeFilter.value = value
  loadVideos()
}

// 舞者选择变化处理
const handleDancerChange = async () => {
  loadVideos()
}

// 加载舞者列表 (仅管理员)
const loadDancers = async () => {
  try {
    const response = await userAPI.getUsers(userStore.userId, true)
    // 过滤掉管理员，只显示普通用户（使用用户的 id 作为 dancer_id）
    dancers.value = (response.users || [])
      .filter(u => !u.is_admin)
      .map(u => ({
        id: u.id,
        username: u.username
      }))
  } catch (error) {
    console.error('加载舞者列表失败:', error)
  }
}

// 计算后的视频列表（由于后端已经处理了时间过滤，这里直接返回 videos）
const filteredVideos = computed(() => {
  return videos.value
})

// 获取当前筛选条件下的日期范围
const getDateRangeFromFilter = () => {
  // 如果有自定义日期范围，优先使用
  if (startDate.value && endDate.value) {
    return { startDate: startDate.value, endDate: endDate.value }
  }
  
  const now = new Date()
  
  // 根据预设的时间选项计算日期范围
  if (selectedTimeFilter.value === 'all') {
    return {}
  }
  
  const daysMap = {
    '7days': 7,
    '30days': 30,
    '90days': 90
  }
  
  const days = daysMap[selectedTimeFilter.value]
  if (!days) return {}
  
  const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  return {
    startDate: cutoffDate.toISOString().split('T')[0],
    endDate: now.toISOString().split('T')[0]
  }
}

// 加载视频列表 - 仅获取基本信息（封面、标题等），不加载视频内容
const loadVideos = async (isLoadMore = false) => {
  try {
    if (isLoadMore) {
      isLoadingMore.value = true
    } else {
      loading.value = true
      currentPage.value = 1
      videos.value = []
      // 清空 latestAnalysisIds，避免旧数据干扰
      for (const key in latestAnalysisIds) {
        delete latestAnalysisIds[key]
      }
    }
    
    const dateRange = getDateRangeFromFilter()
    // 如果是管理员且选择了舞者，传递 dancer_id 参数，并使用该舞者的 user_id
    let userId = userStore.userId
    let dancerId = null
    
    if (userStore.isAdmin && selectedDancerId.value) {
      dancerId = selectedDancerId.value
      // 获取选择舞者对应的 user_id
      try {
        const dancerUserResponse = await userAPI.getDancerUser(dancerId)
        userId = dancerUserResponse.id
      } catch (error) {
        console.error('获取舞者用户信息失败:', error)
        // 如果获取失败，使用当前登录用户的 ID
        userId = userStore.userId
      }
    }
    
    const response = await videoAPI.getVideos(userId, dancerId, {
      page: currentPage.value,
      perPage: perPage,
      ...dateRange
    })
    
    const newVideos = response.videos || []
    
    if (isLoadMore) {
      videos.value = [...videos.value, ...newVideos]
    } else {
      videos.value = newVideos
    }
    
    // 判断是否还有更多数据
    hasMore.value = response.pagination?.has_next || false
    
  } catch (error) {
    console.error('加载视频列表失败:', error)
    if (!isLoadMore) {
      videos.value = []
    }
  } finally {
    loading.value = false
    isLoadingMore.value = false
  }
}

// 加载更多视频（滚动加载）
const loadMoreVideos = async () => {
  if (isLoadingMore.value || !hasMore.value) return
  
  currentPage.value++
  await loadVideos(true)
}

// 根据时间过滤条件过滤视频
const filterVideosByTime = (videos) => {
  const now = new Date()
  
  // 如果有自定义日期范围，优先使用
  if (startDate.value && endDate.value) {
    const start = new Date(startDate.value)
    const end = new Date(endDate.value)
    end.setHours(23, 59, 59, 999) // 包含结束日期的整天
    
    return videos.filter(video => {
      if (!video.upload_date) return false
      const videoDate = new Date(video.upload_date)
      return videoDate >= start && videoDate <= end
    })
  }
  
  // 根据预设的时间选项过滤
  if (selectedTimeFilter.value === 'all') {
    return videos
  }
  
  const daysMap = {
    '7days': 7,
    '30days': 30,
    '90days': 90
  }
  
  const days = daysMap[selectedTimeFilter.value]
  if (!days) return videos
  
  const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  
  return videos.filter(video => {
    if (!video.upload_date) return false
    const videoDate = new Date(video.upload_date)
    return videoDate >= cutoffDate
  })
}

// 清除自定义日期范围
const clearDateRange = () => {
  startDate.value = ''
  endDate.value = ''
  selectedTimeFilter.value = 'all'
  // 重新加载视频列表
  loadVideos()
}

// 应用自定义日期范围
const applyDateRange = () => {
  selectedTimeFilter.value = 'custom'
  // 重新加载视频列表
  loadVideos()
}

// 监听时间筛选器变化
const handleTimeFilterChange = (value) => {
  selectedTimeFilter.value = value
  loadVideos()
}

// 舞者选择变化处理
const handleDancerChange = async () => {
  loadVideos()
}

// 加载视频列表 - 仅获取基本信息（封面、标题等），不加载视频内容
const loadVideos = async (isLoadMore = false) => {
  try {
    if (isLoadMore) {
      isLoadingMore.value = true
    } else {
      loading.value = true
      currentPage.value = 1
      videos.value = []
      // 清空 latestAnalysisIds，避免旧数据干扰
      for (const key in latestAnalysisIds) {
        delete latestAnalysisIds[key]
      }
    }
    
    const dateRange = getDateRangeFromFilter()
    // 如果是管理员且选择了舞者，传递 dancer_id 参数，并使用该舞者的 user_id
    let userId = userStore.userId
    let dancerId = null
    
    if (userStore.isAdmin && selectedDancerId.value) {
      dancerId = selectedDancerId.value
      // 获取选择舞者对应的 user_id
      try {
        const dancerUserResponse = await userAPI.getDancerUser(dancerId)
        userId = dancerUserResponse.id
      } catch (error) {
        console.error('获取舞者用户信息失败:', error)
        // 如果获取失败，使用当前登录用户的 ID
        userId = userStore.userId
      }
    }
    
    const response = await videoAPI.getVideos(userId, dancerId, {
      page: currentPage.value,
      perPage: perPage,
      ...dateRange
    })
    
    const newVideos = response.videos || []
    
    if (isLoadMore) {
      videos.value = [...videos.value, ...newVideos]
    } else {
      videos.value = newVideos
    }
    
    // 判断是否还有更多数据
    hasMore.value = response.pagination?.has_next || false
    
  } catch (error) {
    console.error('加载视频列表失败:', error)
    if (!isLoadMore) {
      videos.value = []
    }
  } finally {
    loading.value = false
    isLoadingMore.value = false
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

// 格式化视频时长（秒转换为 MM:SS 或 HH:MM:SS）
const formatDuration = (seconds) => {
  if (!seconds || seconds <= 0) return '--:--'
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes || bytes <= 0) return '--'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unitIndex = 0
  let size = bytes
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(size < 10 && unitIndex > 0 ? 2 : 1)} ${units[unitIndex]}`
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

// 检查是否有分析结果（通过 latestAnalysisIds 判断）
const hasAnalysis = (video) => {
  return !!latestAnalysisIds[video.id] || (video.analyses && video.analyses.length > 0)
}

// 获取最新的分析 ID - 优先使用调用/analyze接口返回的analysis_id
const getLatestAnalysisId = (video) => {
  // 优先使用调用/analyze接口返回的 analysis_id
  if (latestAnalysisIds[video.id]) {
    return latestAnalysisIds[video.id]
  }
  // 如果没有，则从 video.analyses 中获取最后一个
  if (!video.analyses || video.analyses.length === 0) {
    return null
  }
  return video.analyses[video.analyses.length - 1].id
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
  // 设置该视频为分析中状态
  analyzingVideos[video.id] = true
  
  try {
    // 如果是管理员且选择了舞者，传递选择的舞者 userid
    const userId = userStore.isAdmin && selectedDancerId.value ? selectedDancerId.value : userStore.userId
    const result = await analysisAPI.analyzeVideo(video.id, userId)
    // 分析成功，移除分析中状态
    delete analyzingVideos[video.id]
    // 接口返回了 analysis_id，保存到这个 video 对应的最新 analysis_id
    if (result.analysis_id) {
      latestAnalysisIds[video.id] = result.analysis_id
      
      // 在 videos 数组中找到对应的视频对象
      const index = videos.value.findIndex(v => v.id === video.id)
      if (index !== -1) {
        // 确保 analyses 数组存在
        if (!videos.value[index].analyses) {
          videos.value[index].analyses = []
        }
        // 添加新的分析记录（使用返回的 analysis_id）
        videos.value[index].analyses.push({ id: result.analysis_id })
      }
    }
  } catch (error) {
    console.error('AI 分析失败:', error)
    // 分析失败，移除分析中状态
    delete analyzingVideos[video.id]
    showToast('AI 分析失败：' + (error.response?.data?.error || '请稍后重试'), 'error')
  }
}

// 分析当前视频（从弹窗中）
const analyzeCurrentVideo = async () => {
  if (!currentVideo.value) return
  await analyzeVideo(currentVideo.value)
}

// 查看分析结果 - 使用 analysis id 而不是 video id
const viewAnalysisResult = (video) => {
  const analysisId = getLatestAnalysisId(video)
  if (analysisId) {
    router.push(`/analysis/${analysisId}`)
  } else {
    showToast('暂无分析结果', 'error')
  }
}

// 查看当前视频的分析结果（从弹窗中）
const viewCurrentAnalysis = () => {
  if (!currentVideo.value) return
  viewAnalysisResult(currentVideo.value)
}

// 删除视频确认
const confirmDeleteVideo = async (video) => {
  const confirmed = await showConfirm({
    title: '删除确认',
    message: `确定要删除视频"${video.title}"吗？\n\n删除后分析记录也将被同步删除，此操作不可恢复。`,
    confirmText: '删除',
    cancelText: '取消',
    type: 'danger'
  })
  
  if (!confirmed) {
    return
  }
  
  try {
    await videoAPI.deleteVideo(video.id)
    showToast('视频已删除', 'success')
    // 重新加载视频列表
    await loadVideos()
  } catch (error) {
    console.error('删除视频失败:', error)
    showToast('删除失败：' + (error.response?.data?.error || '请稍后重试'), 'error')
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

/* 舞者过滤器样式 (仅管理员) */
.dancer-filter-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.dancer-select {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  min-width: 200px;
  transition: all 0.2s;
  color: #333;
}

.dancer-select:hover {
  border-color: #667eea;
}

.dancer-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 时间过滤器样式 */
.filter-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.filter-group:last-child {
  margin-bottom: 0;
}

.filter-label {
  font-weight: 600;
  color: #555;
  font-size: 14px;
  white-space: nowrap;
}

.time-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  background: #f5f7fa;
  color: #666;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.filter-btn:hover {
  background: #e8eaf6;
  border-color: #667eea;
  color: #667eea;
}

.filter-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.date-range-group {
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.date-range-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.date-input-wrapper {
  position: relative;
  flex: 1;
  min-width: 140px;
  display: flex;
}

.date-input-wrapper input[type="date"] {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  color: #333;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.date-input-wrapper input[type="date"]::-webkit-calendar-picker-indicator {
  position: absolute;
  right: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background: transparent;
  cursor: pointer;
}

.date-input-wrapper:focus-within {
  outline: none;
}

.date-input-wrapper:focus-within input[type="date"] {
  border-color: #667eea;
}

.date-input-wrapper {
  position: relative;
  flex: 1;
  min-width: 140px;
  display: flex;
}

.date-input-wrapper input[type="date"] {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  color: #333;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.date-input-wrapper input[type="date"]::-webkit-calendar-picker-indicator {
  position: absolute;
  right: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background: transparent;
  cursor: pointer;
}

.date-separator {
  color: #999;
  font-size: 14px;
}

.btn-apply-date {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
  transition: transform 0.2s;
}

.btn-apply-date:hover {
  transform: translateY(-1px);
}

.btn-clear-date {
  padding: 8px 16px;
  background: #f5f7fa;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-clear-date:hover {
  background: #e0e0e0;
}

@media (max-width: 768px) {
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .time-filters {
    width: 100%;
  }
  
  .filter-btn {
    flex: 1;
    text-align: center;
  }
  
  .date-range-inputs {
    width: 100%;
  }
  
  .date-input {
    flex: 1;
    min-width: 140px;
  }
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
  cursor: help;
  transition: color 0.2s;
}

.upload-date:hover {
  color: #667eea;
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
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-analyze-small:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-analyze-small:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 小按钮的加载状态 */
.btn-analyze-small.btn-loading {
  background: linear-gradient(135deg, #95a5a6 0%, #bdc3c7 100%);
  cursor: not-allowed;
  opacity: 0.8;
}

.btn-analyze-small.btn-loading:hover {
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

.btn-analyze:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
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
