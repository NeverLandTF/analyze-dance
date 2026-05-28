<template>
  <div class="analysis-history-container">
    <nav class="navbar">
      <div class="nav-brand">🎵 舞蹈 AI 分析</div>
      <div class="nav-links">
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
      <div class="header">
        <h1>📊 AI 分析历史</h1>
        <button @click="$router.push('/my-videos')" class="btn-secondary">
          📹 我的视频
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
              :class="['filter-btn', { active: selectedTimeFilter === option.value }]">
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
      
      <!-- 滚动加载容器 -->
      <div ref="scrollContainer" class="scroll-container" @scroll="handleScroll">
      
      <div v-if="loading && analyses.length === 0" class="loading">加载中...</div>

      <div v-else-if="analyses.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">📊</div>
        <p>{{ '暂无 AI 分析记录' }}</p>
        <button @click="$router.push('/upload')" class="btn-primary">去上传视频并分析</button>
      </div>

      <div v-else class="analyses-list">
        <div 
          v-for="item in analyses" 
          :key="item.id" 
          :id="`analysis-${item.id}`"
          class="analysis-card" 
          @click="viewAnalysisDetail(item)"
        >
          <div class="analysis-thumbnail">
            <img 
              v-if="item.thumbnail_url" 
              :src="getThumbnailUrl(item.thumbnail_url)" 
              alt="视频封面"
              class="thumbnail-image"
            />
            <div v-else class="thumbnail-placeholder">
              <span>▶</span>
            </div>
          </div>
          <div class="analysis-info">
            <h3>{{ item.video_title }}</h3>
            <div class="analysis-meta">
              <span class="dance-style" v-if="item.dance_style">{{ getDanceStyleName(item.dance_style) }}</span>
              <span class="analysis-date">{{ formatDateTime(item.analyzed_at) }}</span>
            </div>
            <div class="score-preview">
              <span class="score-label">综合得分：</span>
              <span class="score-value" :class="getScoreClass(item.overall_score)">
                {{ item.overall_score || 0 }}
              </span>
            </div>
            <div class="analysis-summary" v-if="item.summary">
              {{ item.summary.substring(0, 80) }}{{ item.summary.length > 80 ? '...' : '' }}
            </div>
          </div>
          <div class="analysis-action">
            <span class="view-hint">查看详情 →</span>
          </div>
        </div>
      </div>
      <!-- 滚动加载提示 -->
      <div v-if="loadingMore" class="loading-more">加载中...</div>
      <div v-if="!hasMore && analyses.length > 0" class="no-more">没有更多了</div>
    </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { analysisAPI, userAPI } from '../api/modules'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
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

// 舞者过滤相关 (仅管理员)
const selectedDancerId = ref('')
const dancers = ref([])

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // 如果是管理员，加载舞者列表
  if (userStore.isAdmin) {
    loadDancers()
  }
  loadAnalyses().then(() => {
    // 加载完成后，检查是否有 hash 用于滚动定位
    scrollToAnalysisFromHash()
  })
})

// 根据 URL hash 滚动到对应的分析记录
const scrollToAnalysisFromHash = () => {
  const hash = route.hash
  if (hash && hash.startsWith('#analysis-')) {
    const analysisId = hash.replace('#analysis-', '')
    nextTick(() => {
      const element = document.getElementById(`analysis-${analysisId}`)
      if (element) {
        // 平滑滚动到元素位置
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        // 添加一个高亮效果，持续 2 秒
        element.classList.add('highlight-animation')
        setTimeout(() => {
          element.classList.remove('highlight-animation')
        }, 2000)
      }
    })
  }
}

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const analyses = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)
const perPage = ref(10)

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

// 加载分析历史列表（支持分页和滚动加载）
const loadAnalyses = async (isLoadMore = false) => {
  try {
    if (isLoadMore) {
      loadingMore.value = true
    } else {
      loading.value = true
      currentPage.value = 1
      analyses.value = []
    }
    
    const params = {
      page: currentPage.value,
      perPage: perPage.value
    }
    
    // 添加时间过滤参数
    if (startDate.value && endDate.value) {
      params.startDate = startDate.value
      params.endDate = endDate.value
    } else if (selectedTimeFilter.value !== 'all') {
      const dateRange = getDateRangeFromFilter(selectedTimeFilter.value)
      if (dateRange.start && dateRange.end) {
        params.startDate = dateRange.start
        params.endDate = dateRange.end
      }
    }
    
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
    
    const result = await analysisAPI.getAnalysisHistory(userId, dancerId, params)
    const newAnalyses = result.analyses || []
    
    if (isLoadMore) {
      analyses.value = [...analyses.value, ...newAnalyses]
    } else {
      analyses.value = newAnalyses
    }
    
    // 判断是否还有更多数据
    hasMore.value = newAnalyses.length === perPage.value
    if (hasMore.value) {
      currentPage.value++
    }
  } catch (error) {
    console.error('加载分析历史失败:', error)
    if (!isLoadMore) {
      analyses.value = []
    }
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 根据预设的时间选项计算日期范围
const getDateRangeFromFilter = (filterValue) => {
  const now = new Date()
  const daysMap = {
    '7days': 7,
    '30days': 30,
    '90days': 90
  }
  
  const days = daysMap[filterValue]
  if (!days) return { start: null, end: null }
  
  const startDateObj = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  return {
    start: formatDate(startDateObj),
    end: formatDate(now)
  }
}

// 格式化日期为 YYYY-MM-DD
const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 应用自定义日期范围
const applyDateRange = () => {
  selectedTimeFilter.value = 'custom'
  loadAnalyses()
}

// 清除自定义日期范围
const clearDateRange = () => {
  startDate.value = ''
  endDate.value = ''
  selectedTimeFilter.value = 'all'
  loadAnalyses()
}

// 监听时间筛选变化
const handleTimeFilterChange = (value) => {
  selectedTimeFilter.value = value
  if (value === 'all') {
    startDate.value = ''
    endDate.value = ''
  }
  loadAnalyses()
}

// 舞者选择变化处理
const handleDancerChange = () => {
  loadAnalyses()
}

// 加载舞者列表 (仅管理员)
const loadDancers = async () => {
  try {
    const response = await userAPI.getUsers(userStore.userId, true)
    // 过滤掉管理员，只显示普通用户
    dancers.value = (response.users || []).filter(u => !u.is_admin)
  } catch (error) {
    console.error('加载舞者列表失败:', error)
  }
}

// 获取封面图 URL
const getThumbnailUrl = (thumbnailPath) => {
  if (!thumbnailPath) return ''
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
  return `${baseURL}${thumbnailPath}`
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '--'
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
  return styleMap[style] || style || '未指定'
}

// 根据分数返回样式类
const getScoreClass = (score) => {
  if (!score) return ''
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-fair'
  return 'score-poor'
}

// 查看分析详情
const viewAnalysisDetail = (item) => {
  router.push(`/analysis/${item.id}`)
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 滚动加载相关
const scrollContainer = ref(null)

const handleScroll = (event) => {
  const target = event.target
  const scrollTop = target.scrollTop
  const scrollHeight = target.scrollHeight
  const clientHeight = target.clientHeight
  
  // 当滚动到距离底部 100px 时，加载更多数据
  if (scrollHeight - scrollTop - clientHeight < 100 && !loadingMore.value && hasMore.value) {
    loadAnalyses(true)
  }
}
</script>

<style scoped>
.analysis-history-container {
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

.analyses-list {
  display: grid;
  gap: 20px;
}

.analysis-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  gap: 20px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s, background-color 0.5s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.analysis-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* 高亮动画效果 */
.analysis-card.highlight-animation {
  animation: highlight-pulse 2s ease-in-out;
}

@keyframes highlight-pulse {
  0% {
    background-color: white;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  }
  20% {
    background-color: #e8eaf6;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  40% {
    background-color: #fff;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  }
  60% {
    background-color: #e8eaf6;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  100% {
    background-color: white;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  }
}

.analysis-thumbnail {
  width: 200px;
  flex-shrink: 0;
  position: relative;
  padding-top: 112.5px; /* 16:9 比例 */
  background: #000;
  border-radius: 8px;
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
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
}

.analysis-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.analysis-info h3 {
  font-size: 20px;
  color: #333;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.analysis-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 14px;
}

.dance-style {
  background: #f0f0f0;
  padding: 3px 10px;
  border-radius: 12px;
  color: #666;
}

.analysis-date {
  color: #999;
}

.score-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.score-label {
  color: #666;
}

.score-value {
  font-weight: bold;
  font-size: 20px;
}

.score-excellent {
  color: #27ae60;
}

.score-good {
  color: #2ecc71;
}

.score-fair {
  color: #f39c12;
}

.score-poor {
  color: #e74c3c;
}

.analysis-summary {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.analysis-action {
  display: flex;
  align-items: center;
}

.view-hint {
  color: #667eea;
  font-weight: 600;
  font-size: 14px;
}

@media (max-width: 768px) {
  .navbar {
    padding: 15px 20px;
    flex-direction: column;
    gap: 15px;
  }

  .analysis-card {
    flex-direction: column;
  }

  .analysis-thumbnail {
    width: 100%;
    padding-top: 56.25%;
  }

  .header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
}

/* 滚动加载容器样式 */
.scroll-container {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  padding-right: 10px;
}

.scroll-container::-webkit-scrollbar {
  width: 8px;
}

.scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.scroll-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.scroll-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* 加载更多提示样式 */
.loading-more {
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 14px;
}

.no-more {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
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
</style>
