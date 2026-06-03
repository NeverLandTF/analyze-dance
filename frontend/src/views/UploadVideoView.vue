<template>
  <div class="upload-container">
    <nav class="navbar">
      <router-link to="/" class="nav-brand">🎵 舞蹈 AI 分析</router-link>
      <div class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link v-if="userStore.isAdmin" to="/dancers" class="nav-link">用户管理</router-link>
        <router-link to="/my-videos" class="nav-link">我的视频</router-link>
        
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
        <h1>上传视频</h1>
      </div>
      
      <div class="upload-section">
        <!-- 选择舞者 - 仅管理员可见 -->
        <div v-if="userStore.isAdmin" class="form-group">
          <label>选择舞者（用户）</label>
          <select v-model="selectedDancerId" class="form-select" :disabled="loading || uploading">
            <option value="">请选择用户</option>
            <option v-for="user in users" :key="user.id" :value="user.id">
              {{ user.username }}
            </option>
          </select>
        </div>
        
        <!-- 视频标题 -->
        <div class="form-group">
          <label>视频标题</label>
          <div class="title-input-group">
            <input 
              type="text" 
              v-model="videoTitle" 
              placeholder="输入视频标题"
              class="form-input"
              :disabled="uploading"
            />
            <button @click="generateTimestampTitle" type="button" class="btn-timestamp" :disabled="uploading">
              🕐 生成时间戳标题
            </button>
          </div>
        </div>
        
        <!-- 舞蹈风格 -->
        <div class="form-group">
          <label>舞蹈风格（可选）</label>
          <select v-model="danceStyle" class="form-select" :disabled="uploading">
            <option value="">请选择风格</option>
            <option value="breaking">Breaking (霹雳舞)</option>
            <option value="popping">Popping (机械舞)</option>
            <option value="locking">Locking (锁舞)</option>
            <option value="hiphop">Hip-hop (嘻哈舞)</option>
            <option value="jazz">Jazz (爵士舞)</option>
            <option value="contemporary">Contemporary (现代舞)</option>
            <option value="other">Other (其他)</option>
          </select>
        </div>
        
        <!-- 文件上传区域 -->
        <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
          <input 
            type="file" 
            ref="fileInputRef" 
            accept="video/*" 
            @change="handleFileSelect"
            multiple
            class="file-input"
            :disabled="uploading"
          />
          <div v-if="selectedFiles.length === 0" class="upload-placeholder">
            <div class="upload-icon">📹</div>
            <p>拖拽视频文件到此处，或点击选择文件</p>
            <p class="hint">支持 MP4, AVI, MOV, MKV, WebM 格式，最大 1GB，可多选</p>
            <button @click="triggerFileInput" class="btn-select" :disabled="uploading">
              选择文件
            </button>
          </div>
          <div v-else class="file-list">
            <!-- 继续添加文件按钮 -->
            <button @click="triggerFileInput" class="btn-add-more" :disabled="uploading">
              ➕ 继续添加文件
            </button>
            <div v-for="(file, index) in selectedFiles" :key="index" class="file-info" :class="{ 
              'box-selected-file': boxSelectedMap[index],
              'box-unselected-warning': fileVideoTypeMap[index] === 'multiple' && showUnboxedWarning && !boxSelectedMap[index]
            }">
              <div class="file-icon">🎬</div>
              <div class="file-details">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size) }}</div>
                <div class="file-title-preview">标题：{{ getAutoTitle(index) }}</div>
                <!-- 单人/多人视频类型选择 -->
                <div class="file-video-type-options">
                  <label class="radio-option-small">
                    <input type="radio" :checked="fileVideoTypeMap[index] === 'single'" @change="setFileVideoType(index, 'single')" :disabled="uploading" />
                    <span class="option-label-small">单人</span>
                  </label>
                  <label class="radio-option-small">
                    <input type="radio" :checked="fileVideoTypeMap[index] === 'multiple'" @change="setFileVideoType(index, 'multiple')" :disabled="uploading" />
                    <span class="option-label-small">多人</span>
                  </label>
                </div>
                <!-- 单个文件上传进度 -->
                <div v-if="uploading && fileProgressMap[index] !== undefined" class="file-progress">
                  <div class="file-progress-bar">
                    <div class="file-progress-fill" :style="{ width: fileProgressMap[index] + '%' }"></div>
                  </div>
                  <span class="file-progress-text">{{ fileProgressMap[index] }}%</span>
                </div>
              </div>
              <div class="file-actions">
                <!-- 仅当该视频选择为多人视频时显示框选按钮 -->
                <button 
                  v-if="fileVideoTypeMap[index] === 'multiple'" 
                  @click="openBoxSelection(index)" 
                  class="btn-box-select"
                  :class="{ 'box-selected': boxSelectedMap[index] }"
                  :disabled="uploading"
                  :title="boxSelectedMap[index] ? '已框选' : '框选人物主体'"
                >
                  {{ boxSelectedMap[index] ? '✅' : '⬜' }}
                </button>
                <button @click="removeFile(index)" class="btn-remove" :disabled="uploading">
                  ✕
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="actions">
          <button @click="handleUpload" :disabled="!canUpload || uploading" class="btn-primary">
            {{ uploading ? '上传中...' : '开始上传' }}
          </button>
          <button @click="resetForm" :disabled="uploading" class="btn-secondary">
            重置
          </button>
        </div>
        
        <!-- 上传结果 -->
        <div v-if="uploadError" class="error-message">
          {{ uploadError }}
        </div>
        
        <div v-if="uploadedVideo && Array.isArray(uploadedVideo)" class="success-message">
          <div class="success-icon">✓</div>
          <p>上传成功！共上传 {{ uploadedVideo.length }} 个视频</p>
          <div class="video-list">
            <div v-for="(video, index) in uploadedVideo" :key="index" class="video-item">
              <div class="video-thumbnail-wrapper">
                <!-- 缩略图 - 使用后端返回的封面图 -->
                <div class="video-thumbnail" @click="openPreview(video)">
                  <img 
                    v-if="video.thumbnail_url" 
                    :src="getThumbnailUrl(video.thumbnail_url)" 
                    alt="视频封面"
                    class="thumbnail-image"
                  />
                  <div v-else class="thumbnail-placeholder">
                    <span class="play-icon">▶</span>
                  </div>
                  <div class="thumbnail-overlay">
                    <span class="preview-text">点击预览</span>
                  </div>
                </div>
              </div>
              <div class="video-info">
                <h4>{{ video.title }}</h4>
                <p>文件大小：{{ formatFileSize(selectedFiles[index]?.size || 0) }}</p>
              </div>
              <div class="video-actions">
                <button @click="openPreview(video)" class="btn-preview-small">
                  👁️ 预览
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
                  @click="handleAnalyzeSingle(video)" 
                  class="btn-small btn-analyze-small"
                  :disabled="analyzingVideoIds.has(video.id)"
                >
                  <span v-if="analyzingVideoIds.has(video.id)" class="loading-spinner">⏳</span>
                  <span v-else>🤖 AI 分析</span>
                </button>
              </div>
            </div>
          </div>
          <div class="success-actions">
            <button @click="resetForm" class="btn-secondary">
              继续上传
            </button>
          </div>
        </div>
        
        <!-- 单个视频上传成功的旧版展示（兼容） -->
        <div v-else-if="uploadedVideo && !Array.isArray(uploadedVideo)" class="success-message">
          <div class="success-icon">✓</div>
          <p>上传成功！</p>
          <div class="video-thumbnail-wrapper-single">
            <div class="video-thumbnail" @click="openPreview(uploadedVideo)">
              <img 
                v-if="uploadedVideo.thumbnail_url" 
                :src="getThumbnailUrl(uploadedVideo.thumbnail_url)" 
                alt="视频封面"
                class="thumbnail-image-single"
              />
              <div v-else class="thumbnail-placeholder-single">
                <span class="play-icon">▶</span>
              </div>
              <div class="thumbnail-overlay">
                <span class="preview-text">点击预览</span>
              </div>
            </div>
          </div>
          <div class="success-actions">
            <button @click="openPreview(uploadedVideo)" class="btn-preview">
              👁️ 预览视频
            </button>
            <button 
              v-if="hasAnalysis(uploadedVideo)" 
              @click="viewAnalysisResult(uploadedVideo)" 
              class="btn-analyze"
            >
              📊 查看最新分析
            </button>
            <button 
              v-else 
              @click="handleAnalyze" 
              class="btn-analyze"
              :disabled="analyzingVideoIds.has(uploadedVideo.id)"
            >
              <span v-if="analyzingVideoIds.has(uploadedVideo.id)" class="loading-spinner">⏳</span>
              <span v-else>🤖 AI 分析</span>
            </button>
            <button @click="resetForm" class="btn-secondary">
              继续上传
            </button>
          </div>
        </div>
        
        <!-- 视频预览弹窗 -->
        <div v-if="showPreview" class="modal-overlay" @click.self="closePreview">
          <div class="preview-modal" @click.stop>
            <div class="modal-header">
              <h2>{{ currentPreviewVideo?.title || '视频预览' }}</h2>
              <button @click="closePreview" class="btn-close">×</button>
            </div>
            <div class="modal-body">
              <video 
                ref="videoPlayer"
                :src="getVideoUrl(currentPreviewVideo?.file_path)" 
                controls 
                autoplay
                class="video-player-full"
              ></video>
              <div class="video-details">
                <div class="detail-item">
                  <span class="label">舞蹈风格：</span>
                  <span class="value">{{ getDanceStyleName(currentPreviewVideo?.dance_style) || '未指定' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">上传时间：</span>
                  <span class="value">{{ formatDateTime(new Date()) }}</span>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button 
                v-if="currentPreviewVideo && hasAnalysis(currentPreviewVideo)" 
                @click="viewAnalysisResult(currentPreviewVideo)" 
                class="btn-analyze"
              >
                📊 查看最新分析
              </button>
              <button 
                v-else 
                @click="analyzeCurrentPreviewVideo" 
                class="btn-analyze"
                :disabled="currentPreviewVideo && analyzingVideoIds.has(currentPreviewVideo.id)"
              >
                <span v-if="currentPreviewVideo && analyzingVideoIds.has(currentPreviewVideo.id)" class="loading-spinner">⏳</span>
                <span v-else>🤖 AI 分析</span>
              </button>
              <button @click="closePreview" class="btn-secondary">
                关闭
              </button>
            </div>
          </div>
        </div>

        <!-- 框选人物主体弹窗 -->
        <div v-if="showBoxSelection" class="modal-overlay" @click.self="closeBoxSelection">
          <div class="box-selection-modal" @click.stop>
            <div class="modal-header">
              <h2>框选人物主体 - {{ selectedFiles[currentBoxFileIndex]?.name }}</h2>
              <button @click="closeBoxSelection" class="btn-close">×</button>
            </div>
            <div class="modal-body box-selection-body">
              <div class="box-selection-instructions">
                <p>1. 拖动进度条选择合适帧</p>
                <p>2. 在视频上点击并拖动绘制矩形框</p>
                <p>3. 点击"保存选中区域"按钮</p>
              </div>
              <div class="video-canvas-container" ref="videoCanvasContainerRef">
                <video 
                  ref="boxSelectionVideo"
                  :src="currentBoxVideoUrl"
                  class="box-selection-video"
                  @loadedmetadata="onVideoLoaded"
                  @seeked="onVideoSeeked"
                ></video>
                <canvas 
                  ref="boxCanvas"
                  class="box-canvas"
                  @mousedown="startDrawing"
                  @mousemove="draw"
                  @mouseup="stopDrawing"
                  @mouseleave="stopDrawing"
                ></canvas>
              </div>
              <div class="video-controls">
                <button @click="togglePlayPause" class="btn-control">
                  {{ isPlaying ? '⏸️ 暂停' : '▶️ 播放' }}
                </button>
                <input 
                  type="range" 
                  ref="videoProgress"
                  min="0" 
                  max="100" 
                  value="0" 
                  class="progress-slider"
                  @input="onProgressChange"
                />
                <span class="time-display">{{ currentTimeDisplay }} / {{ durationDisplay }}</span>
              </div>
            </div>
            <div class="modal-footer box-selection-footer">
              <button @click="saveBoxSelection" class="btn-primary" :disabled="!hasBoxSelection">
                💾 保存选中区域
              </button>
              <button @click="clearBoxSelection" class="btn-secondary" :disabled="!hasBoxSelection">
                🗑️ 清除选区
              </button>
              <button @click="closeBoxSelection" class="btn-secondary">
                取消
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, inject, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { videoAPI, userAPI, analysisAPI } from '../api/modules'
import { useUserStore } from '../stores/user'

const router = useRouter()
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
  loadUsers()
  
  // 监听窗口大小变化，重新初始化 canvas 尺寸
  window.addEventListener('resize', handleWindowResize)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', handleWindowResize)
})

// 表单数据
const users = ref([])
const selectedDancerId = ref(null)
const videoTitle = ref('')
const danceStyle = ref('')
const fileVideoTypeMap = ref({}) // 记录每个文件的视频类型 { [index]: 'single' | 'multiple' }
const selectedFiles = ref([])
const fileInputRef = ref(null)

// 上传状态
const uploading = ref(false)
const fileProgressMap = ref({}) // 存储每个文件的上传进度
const uploadError = ref('')
const uploadedVideo = ref(null)

// 预览相关
const showPreview = ref(false)
const currentPreviewVideo = ref(null)

// 框选功能相关
const showBoxSelection = ref(false)
const currentBoxFileIndex = ref(-1)
const currentBoxVideoUrl = ref('')
const currentBoxVideoFile = ref(null)
const boxSelectionVideo = ref(null)
const boxCanvas = ref(null)
const videoCanvasContainerRef = ref(null)
const videoProgress = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const isDrawing = ref(false)
const startX = ref(0)
const startY = ref(0)
const currentX = ref(0)
const currentY = ref(0)
const boxSelectionData = ref(null) // 保存的画框数据 {x, y, width, height, timestamp}
const boxSelectedMap = ref({}) // 记录每个文件是否已完成框选 { [index]: true/false }
const showUnboxedWarning = ref(false) // 是否显示未框选警告样式
const unboxedFileIndices = ref([]) // 未框选的文件索引列表

// 加载状态
const loading = ref(false)

// 分析状态 - 存储正在分析的视频 ID 集合
const analyzingVideoIds = ref(new Set())
// 记录每个视频最新分析的 analysis_id（调用 /analyze 接口返回的）
const latestAnalysisIds = reactive({})

// 计算属性
const canUpload = computed(() => {
  // 普通用户不需要选择舞者（自动使用自己的 ID），只需要标题和文件
  if (!userStore.isAdmin) {
    return videoTitle.value && selectedFiles.value.length > 0
  }
  // 管理员需要选择舞者、标题和文件
  return selectedDancerId.value && videoTitle.value && selectedFiles.value.length > 0
})

// 加载用户列表（用于选择舞者）
const loadUsers = async () => {
  try {
    loading.value = true
    console.log('开始加载用户列表，isAdmin:', userStore.isAdmin)
    // 仅管理员需要加载用户列表，普通用户直接使用自己的 ID
    if (userStore.isAdmin) {
      const response = await userAPI.getUsers(userStore.userId, userStore.isAdmin)
      console.log('获取用户列表响应:', response)
      // 过滤掉管理员用户，只保留普通用户作为可选舞者
      users.value = (response.users || []).filter(user => !user.is_admin)
      console.log('过滤后的用户列表:', users.value)
      
      // 自动选择第一个用户（使用用户的 id 作为 dancer_id）
      if (users.value.length > 0 && selectedDancerId.value === null) {
        selectedDancerId.value = users.value[0].id
        console.log('自动选择第一个用户:', users.value[0].username, 'userid:', selectedDancerId.value)
      }
    } else {
      // 普通用户直接设置自己的 ID，不需要传递 dancer_id，后端会自动获取
      users.value = [{ id: userStore.userId, username: userStore.user?.username }]
      selectedDancerId.value = null  // 设置为 null，让后端自动获取默认舞者
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    uploadError.value = '加载用户列表失败：' + (error.message || '未知错误')
  } finally {
    loading.value = false
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  if (files.length > 0) {
    validateAndSetFiles(files)
  }
}

// 处理拖放
const handleDrop = (event) => {
  const files = Array.from(event.dataTransfer.files)
  if (files.length > 0) {
    validateAndSetFiles(files)
  }
}

// 验证并设置文件（支持多个）
const validateAndSetFiles = (files) => {
  // 检查文件类型
  const validFiles = files.filter(file => {
    if (!file.type.startsWith('video/')) {
      uploadError.value = '请选择视频文件'
      return false
    }
    
    // 检查文件大小 (1GB)
    const maxSize = 1024 * 1024 * 1024
    if (file.size > maxSize) {
      uploadError.value = '文件大小不能超过 1GB'
      return false
    }
    
    return true
  })
  
  if (validFiles.length > 0) {
    const startIndex = selectedFiles.value.length
    selectedFiles.value = [...selectedFiles.value, ...validFiles]
    uploadError.value = ''
    
    // 为新添加的文件初始化视频类型为 'single'（默认单人）
    validFiles.forEach((_, i) => {
      fileVideoTypeMap.value[startIndex + i] = 'single'
    })
  }
}

// 设置单个文件的视频类型
const setFileVideoType = (index, type) => {
  fileVideoTypeMap.value[index] = type
  // 如果从多人改为单人，清除框选状态
  if (type === 'single' && boxSelectedMap.value[index]) {
    delete boxSelectedMap.value[index]
  }
}

// 移除单个文件
const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
  // 同时清除框选状态和视频类型
  if (boxSelectedMap.value[index]) {
    delete boxSelectedMap.value[index]
  }
  if (fileVideoTypeMap.value[index]) {
    delete fileVideoTypeMap.value[index]
  }
  // 重新索引剩余的 map
  const newBoxMap = {}
  const newVideoTypeMap = {}
  selectedFiles.value.forEach((_, idx) => {
    if (boxSelectedMap.value[idx + 1]) {
      newBoxMap[idx] = boxSelectedMap.value[idx + 1]
    }
    if (fileVideoTypeMap.value[idx + 1]) {
      newVideoTypeMap[idx] = fileVideoTypeMap.value[idx + 1]
    }
  })
  boxSelectedMap.value = newBoxMap
  fileVideoTypeMap.value = newVideoTypeMap
}

// 生成时间戳标题
const generateTimestampTitle = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  videoTitle.value = `视频_${year}${month}${day}_${hours}${minutes}${seconds}`
}

// 自动生成标题（带索引）
const getAutoTitle = (index) => {
  if (!videoTitle.value) return `视频 ${index + 1}`
  return `${videoTitle.value}_${index + 1}`
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 获取视频 URL
const getVideoUrl = (filePath) => {
  if (!filePath) return ''
  // 假设后端配置了静态文件服务
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
  return `${baseURL}${filePath}`
}

// 处理上传 - 支持批量上传，并行上传，每个文件显示独立进度条
const handleUpload = async () => {
  // 检查所有标记为多人视频的文件是否已完成框选
  const unboxedIndices = selectedFiles.value
    .map((_, index) => index)
    .filter(index => fileVideoTypeMap.value[index] === 'multiple' && !boxSelectedMap.value[index])
  
  if (unboxedIndices.length > 0) {
    showToast('请为所有多人视频完成人物框选后再上传', 'warning')
    // 标记未框选的文件需要显示红色边框（通过临时添加一个标记）
    showUnboxedWarning.value = true
    unboxedFileIndices.value = unboxedIndices
    // 2 秒后清除警告样式
    setTimeout(() => {
      showUnboxedWarning.value = false
      unboxedFileIndices.value = []
    }, 2000)
    return
  }
  
  if (!canUpload.value) return
  
  uploading.value = true
  fileProgressMap.value = {} // 重置每个文件的进度
  uploadError.value = ''
  uploadedVideo.value = null
  
  try {
    const totalFiles = selectedFiles.value.length
    
    // 并行上传所有文件
    const uploadPromises = selectedFiles.value.map((file, index) => {
      // 自动生成带索引的标题
      const autoTitle = getAutoTitle(index)
      // 普通用户不需要传递 dancer_id，后端会自动获取默认舞者
      const dancerIdParam = userStore.isAdmin ? selectedDancerId.value : null
      
      // 初始化该文件的进度为 0
      fileProgressMap.value[index] = 0
      
      // 获取框选的帧图片 blob（如果有）
      const frameImageBlob = file.frameImage ? file.frameImage.blob : null
      
      // 获取该文件的视频类型（单人/多人），默认为 'single'
      const fileVideoType = fileVideoTypeMap.value[index] || 'single'
      
      return new Promise((resolve, reject) => {
        videoAPI.uploadVideoFile(
          file,
          userStore.userId,
          dancerIdParam,
          autoTitle,
          danceStyle.value,
          (progress) => {
            // 更新该文件的进度
            fileProgressMap.value[index] = progress
          },
          fileVideoType,  // 传递该文件的视频类型（单人/多人）
          frameImageBlob    // 传递框选的帧图片（如果有）
        ).then(resolve).catch(reject)
      })
    })
    
    const results = await Promise.all(uploadPromises)
    
    // 上传接口已返回 thumbnail_url 等详细信息，直接使用
    uploadedVideo.value = results
    
    // 不再加载视频列表，因为已删除该部分 UI
  } catch (error) {
    console.error('上传失败:', error)
    uploadError.value = error.response?.data?.error || '上传失败，请稍后重试'
  } finally {
    uploading.value = false
  }
}

// 重置表单
const resetForm = () => {
  // 管理员重置为第一个用户（使用用户的 id），普通用户重置为 null（后端会自动获取）
  if (userStore.isAdmin) {
    selectedDancerId.value = users.value.length > 0 ? users.value[0].id : null
  } else {
    selectedDancerId.value = null  // 普通用户设置为 null，让后端自动获取
  }
  videoTitle.value = ''
  danceStyle.value = ''
  selectedFiles.value = []
  boxSelectedMap.value = {}  // 重置框选状态
  fileVideoTypeMap.value = {}  // 重置每个文件的视频类型
  uploadError.value = ''
  uploadedVideo.value = null
  
  // 清空 file input 的值，这样即使选择相同的文件也能触发 change 事件
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// 处理上传成功后清空文件选择，允许重新选择
const clearFileSelection = () => {
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// 触发文件选择
const triggerFileInput = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

// 开始 AI 分析（单个视频）
const handleAnalyzeSingle = async (video) => {
  if (!video) return
  
  // 将视频 ID 添加到分析中集合
  analyzingVideoIds.value.add(video.id)
  
  try {
    const result = await analysisAPI.analyzeVideo(video.id, userStore.userId)
    // 分析成功，移除分析中状态
    analyzingVideoIds.value.delete(video.id)
    // 接口返回了 analysis_id，保存到这个 video 对应的最新 analysis_id
    if (result.analysis_id) {
      latestAnalysisIds[video.id] = result.analysis_id
      
      // 更新 uploadedVideo 中对应视频的分析记录
      if (uploadedVideo.value) {
        if (Array.isArray(uploadedVideo.value)) {
          const index = uploadedVideo.value.findIndex(v => v.id === video.id)
          if (index !== -1) {
            if (!uploadedVideo.value[index].analyses) {
              uploadedVideo.value[index].analyses = []
            }
            uploadedVideo.value[index].analyses.push({ id: result.analysis_id })
          }
        } else {
          // 单个视频对象
          if (!uploadedVideo.value.analyses) {
            uploadedVideo.value.analyses = []
          }
          uploadedVideo.value.analyses.push({ id: result.analysis_id })
        }
      }
      
      // 如果当前预览的是这个视频，也更新它
      if (currentPreviewVideo.value && currentPreviewVideo.value.id === video.id) {
        if (!currentPreviewVideo.value.analyses) {
          currentPreviewVideo.value.analyses = []
        }
        currentPreviewVideo.value.analyses.push({ id: result.analysis_id })
      }
    }
  } catch (error) {
    console.error('AI 分析失败:', error)
    showToast('AI 分析失败：' + (error.response?.data?.error || '请稍后重试'), 'error')
    // 分析失败，移除分析中状态
    analyzingVideoIds.value.delete(video.id)
  }
}

// 开始 AI 分析（旧版，兼容单个视频）
const handleAnalyze = async () => {
  if (!uploadedVideo.value) return
  
  // 如果是数组，取第一个
  const video = Array.isArray(uploadedVideo.value) ? uploadedVideo.value[0] : uploadedVideo.value
  if (!video) return
  
  // 将视频 ID 添加到分析中集合
  analyzingVideoIds.value.add(video.id)
  
  try {
    const result = await analysisAPI.analyzeVideo(video.id, userStore.userId)
    // 分析成功，移除分析中状态
    analyzingVideoIds.value.delete(video.id)
    // 接口返回了 analysis_id，保存到这个 video 对应的最新 analysis_id
    if (result.analysis_id) {
      latestAnalysisIds[video.id] = result.analysis_id
      
      // 更新 uploadedVideo 中对应视频的分析记录
      if (Array.isArray(uploadedVideo.value)) {
        const index = uploadedVideo.value.findIndex(v => v.id === video.id)
        if (index !== -1) {
          if (!uploadedVideo.value[index].analyses) {
            uploadedVideo.value[index].analyses = []
          }
          uploadedVideo.value[index].analyses.push({ id: result.analysis_id })
        }
      } else {
        // 单个视频对象
        if (!uploadedVideo.value.analyses) {
          uploadedVideo.value.analyses = []
        }
        uploadedVideo.value.analyses.push({ id: result.analysis_id })
      }
      
      // 如果当前预览的是这个视频，也更新它
      if (currentPreviewVideo.value && currentPreviewVideo.value.id === video.id) {
        if (!currentPreviewVideo.value.analyses) {
          currentPreviewVideo.value.analyses = []
        }
        currentPreviewVideo.value.analyses.push({ id: result.analysis_id })
      }
    }
  } catch (error) {
    console.error('AI 分析失败:', error)
    showToast('AI 分析失败：' + (error.response?.data?.error || '请稍后重试'), 'error')
    // 分析失败，移除分析中状态
    analyzingVideoIds.value.delete(video.id)
  }
}

// 打开预览弹窗
const openPreview = (video) => {
  currentPreviewVideo.value = video
  showPreview.value = true
}

// 关闭预览弹窗
const closePreview = () => {
  showPreview.value = false
  // 停止视频播放
  if (videoPlayer.value) {
    videoPlayer.value.pause()
    videoPlayer.value.currentTime = 0
  }
  currentPreviewVideo.value = null
}

// 分析当前预览的视频（从弹窗中）
const analyzeCurrentPreviewVideo = async () => {
  if (!currentPreviewVideo.value) return
  
  // 将视频 ID 添加到分析中集合
  analyzingVideoIds.value.add(currentPreviewVideo.value.id)
  
  try {
    const result = await analysisAPI.analyzeVideo(currentPreviewVideo.value.id, userStore.userId)
    // 分析成功，移除分析中状态
    analyzingVideoIds.value.delete(currentPreviewVideo.value.id)
    // 接口返回了 analysis_id，保存到这个 video 对应的最新 analysis_id
    if (result.analysis_id) {
      latestAnalysisIds[currentPreviewVideo.value.id] = result.analysis_id
      
      // 更新 currentPreviewVideo 的分析记录
      if (!currentPreviewVideo.value.analyses) {
        currentPreviewVideo.value.analyses = []
      }
      currentPreviewVideo.value.analyses.push({ id: result.analysis_id })
      
      // 同时更新 uploadedVideo 中对应的视频
      if (uploadedVideo.value) {
        if (Array.isArray(uploadedVideo.value)) {
          const index = uploadedVideo.value.findIndex(v => v.id === currentPreviewVideo.value.id)
          if (index !== -1) {
            if (!uploadedVideo.value[index].analyses) {
              uploadedVideo.value[index].analyses = []
            }
            uploadedVideo.value[index].analyses.push({ id: result.analysis_id })
          }
        } else {
          if (!uploadedVideo.value.analyses) {
            uploadedVideo.value.analyses = []
          }
          uploadedVideo.value.analyses.push({ id: result.analysis_id })
        }
      }
    }
  } catch (error) {
    console.error('AI 分析失败:', error)
    showToast('AI 分析失败：' + (error.response?.data?.error || '请稍后重试'), 'error')
    // 分析失败，移除分析中状态
    analyzingVideoIds.value.delete(currentPreviewVideo.value.id)
  }
}

// 获取封面图 URL
const getThumbnailUrl = (thumbnailPath) => {
  if (!thumbnailPath) return ''
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
  return `${baseURL}${thumbnailPath}`
}

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return ''
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

// 检查是否有分析结果（通过 latestAnalysisIds 判断）
const hasAnalysis = (video) => {
  if (!video) return false
  return !!latestAnalysisIds[video.id] || (video.analyses && video.analyses.length > 0)
}

// 获取最新的分析 ID - 优先使用调用/analyze接口返回的analysis_id
const getLatestAnalysisId = (video) => {
  if (!video) return null
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

// 查看分析结果 - 使用 analysis id 而不是 video id
const viewAnalysisResult = (video) => {
  const analysisId = getLatestAnalysisId(video)
  if (analysisId) {
    router.push(`/analysis/${analysisId}`)
  } else {
    showToast('未找到分析结果', 'error')
  }
}

// 视频播放器引用
const videoPlayer = ref(null)

// ========== 框选功能方法实现 ==========

// 打开框选弹窗
const openBoxSelection = (index) => {
  if (index < 0 || index >= selectedFiles.value.length) return
  
  currentBoxFileIndex.value = index
  const file = selectedFiles.value[index]
  currentBoxVideoFile.value = file
  
  // 创建本地 URL 用于预览
  currentBoxVideoUrl.value = URL.createObjectURL(file)
  
  // 重置画框数据（但保留已保存的框选状态）
  boxSelectionData.value = null
  isDrawing.value = false
  
  showBoxSelection.value = true
  
  // 等待视频加载完成后再初始化 canvas
  // 使用 @loadedmetadata 事件确保视频元数据已加载
}

// 关闭框选弹窗
const closeBoxSelection = () => {
  showBoxSelection.value = false
  
  // 停止视频播放
  if (boxSelectionVideo.value) {
    boxSelectionVideo.value.pause()
    boxSelectionVideo.value.currentTime = 0
  }
  
  // 释放本地 URL
  if (currentBoxVideoUrl.value) {
    URL.revokeObjectURL(currentBoxVideoUrl.value)
    currentBoxVideoUrl.value = ''
  }
  
  currentBoxFileIndex.value = -1
  currentBoxVideoFile.value = null
  boxSelectionData.value = null
}

// 初始化 Canvas
const initCanvas = () => {
  if (!boxCanvas.value || !boxSelectionVideo.value) return
  
  const canvas = boxCanvas.value
  const video = boxSelectionVideo.value
  const container = videoCanvasContainerRef.value
  const ctx = canvas.getContext('2d')
  
  // 设置 canvas 内部尺寸为视频实际分辨率，保证框选比例与原视频一致
  canvas.width = video.videoWidth || 640
  canvas.height = video.videoHeight || 360
  
  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // 等待 DOM 更新后，将 canvas 的 CSS 显示尺寸设置为与视频元素一致
  nextTick(() => {
    if (!video || !canvas || !container) return
    
    // 获取容器和视频元素的显示尺寸
    const containerRect = container.getBoundingClientRect()
    const videoRect = video.getBoundingClientRect()
    
    // 关键修复：canvas 的 CSS 显示尺寸应该与视频元素的显示尺寸一致
    // 这样才能确保鼠标点击位置的坐标映射正确
    // 由于 object-fit: contain，videoRect 已经是视频实际显示区域（不含黑边）
    canvas.style.width = videoRect.width + 'px'
    canvas.style.height = videoRect.height + 'px'
    
    // 重新绘制已存在的选区（如果有）
    if (boxSelectionData.value) {
      redrawBoxSelection()
    }
    
    // 额外调用一次 setupCanvasSize 确保视频渲染完成后尺寸正确
    setTimeout(() => {
      setupCanvasSize()
    }, 200)
  })
}

// 窗口大小变化时重新初始化 canvas
const handleWindowResize = () => {
  if (boxSelectionVideo.value && boxCanvas.value) {
    // 保存当前选区数据
    const savedSelection = boxSelectionData.value
    
    // 重新初始化 canvas（会重新设置内部尺寸和 CSS 显示尺寸）
    initCanvas()
    
    // 恢复选区数据（如果有）
    if (savedSelection) {
      boxSelectionData.value = savedSelection
      redrawBoxSelection()
    }
  }
}

// 视频加载完成后也需要等待视频尺寸稳定后再设置 canvas 尺寸
const setupCanvasSize = () => {
  if (!boxSelectionVideo.value || !boxCanvas.value) return
  
  const video = boxSelectionVideo.value
  const canvas = boxCanvas.value
  const container = videoCanvasContainerRef.value
  
  if (!container) return
  
  // 获取容器和视频元素的显示尺寸
  const containerRect = container.getBoundingClientRect()
  const videoRect = video.getBoundingClientRect()
  
  // 关键修复：canvas 的 CSS 尺寸必须与视频显示尺寸完全一致
  // 这样才能确保鼠标点击位置的坐标正确映射到视频分辨率
  canvas.style.width = videoRect.width + 'px'
  canvas.style.height = videoRect.height + 'px'
}

// 视频加载完成
const onVideoLoaded = () => {
  if (!boxSelectionVideo.value || !videoProgress.value) return
  
  const video = boxSelectionVideo.value
  duration.value = video.duration || 0
  
  // 初始化 canvas（设置内部分辨率和 CSS 显示尺寸）
  initCanvas()
  
  // 更新时间显示
  updateTimeDisplay()
  
  // 额外调用一次 setupCanvasSize 确保视频渲染完成后尺寸正确
  nextTick(() => {
    setupCanvasSize()
  })
}

// 视频 seek 完成
const onVideoSeeked = () => {
  if (!boxSelectionVideo.value) return
  currentTime.value = boxSelectionVideo.value.currentTime
  updateTimeDisplay()
  
  // 重新绘制 canvas（如果有已保存的选区）
  redrawBoxSelection()
}

// 更新进度条
const onProgressChange = (event) => {
  if (!boxSelectionVideo.value || !duration.value) return
  
  const percent = event.target.value
  const newTime = (percent / 100) * duration.value
  boxSelectionVideo.value.currentTime = newTime
}

// 切换播放/暂停
const togglePlayPause = () => {
  if (!boxSelectionVideo.value) return
  
  const video = boxSelectionVideo.value
  if (video.paused) {
    video.play()
    isPlaying.value = true
    // 监听时间更新
    video.addEventListener('timeupdate', onTimeUpdate)
  } else {
    video.pause()
    isPlaying.value = false
    video.removeEventListener('timeupdate', onTimeUpdate)
  }
}

// 时间更新处理
const onTimeUpdate = () => {
  if (!boxSelectionVideo.value || !videoProgress.value) return
  
  const video = boxSelectionVideo.value
  currentTime.value = video.currentTime
  
  // 更新进度条
  if (duration.value > 0) {
    const percent = (currentTime.value / duration.value) * 100
    videoProgress.value.value = percent
  }
  
  updateTimeDisplay()
}

// 格式化时间显示
const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

// 更新时间显示
const updateTimeDisplay = () => {
  currentTimeDisplay.value = formatTime(currentTime.value)
  durationDisplay.value = formatTime(duration.value)
}

// 开始绘制
const startDrawing = (event) => {
  if (!boxCanvas.value || !boxSelectionVideo.value) return
  
  isDrawing.value = true
  const rect = boxCanvas.value.getBoundingClientRect()
  const displayX = event.clientX - rect.left
  const displayY = event.clientY - rect.top
  
  // 将显示尺寸坐标映射到视频实际分辨率坐标
  const scaleX = boxCanvas.value.width / rect.width
  const scaleY = boxCanvas.value.height / rect.height
  
  startX.value = displayX * scaleX
  startY.value = displayY * scaleY
  currentX.value = startX.value
  currentY.value = startY.value
}

// 绘制矩形
const draw = (event) => {
  if (!isDrawing.value || !boxCanvas.value || !boxSelectionVideo.value) return
  
  const rect = boxCanvas.value.getBoundingClientRect()
  const displayX = event.clientX - rect.left
  const displayY = event.clientY - rect.top
  
  // 将显示尺寸坐标映射到视频实际分辨率坐标
  const scaleX = boxCanvas.value.width / rect.width
  const scaleY = boxCanvas.value.height / rect.height
  
  currentX.value = displayX * scaleX
  currentY.value = displayY * scaleY
  
  redrawBoxSelection()
}

// 停止绘制
const stopDrawing = () => {
  if (!isDrawing.value) return
  isDrawing.value = false
  
  // 计算并保存选区
  const width = currentX.value - startX.value
  const height = currentY.value - startY.value
  
  // 确保宽高为正数
  const x = width < 0 ? currentX.value : startX.value
  const y = height < 0 ? currentY.value : startY.value
  const absWidth = Math.abs(width)
  const absHeight = Math.abs(height)
  
  // 只有当选区足够大时才保存
  if (absWidth > 10 && absHeight > 10) {
    boxSelectionData.value = {
      x,
      y,
      width: absWidth,
      height: absHeight,
      timestamp: currentTime.value,
      canvasWidth: boxCanvas.value?.width || 0,
      canvasHeight: boxCanvas.value?.height || 0
    }
    
    // 重绘最终选区
    redrawBoxSelection()
  }
}

// 重绘选区
const redrawBoxSelection = () => {
  if (!boxCanvas.value) return
  
  const canvas = boxCanvas.value
  const ctx = canvas.getContext('2d')
  
  // 清空画布 - 完全透明，不遮挡视频
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // 如果有已保存的选区，绘制它
  if (boxSelectionData.value) {
    const { x, y, width, height } = boxSelectionData.value
    
    // 只绘制边框和角落标记，不再绘制半透明遮罩，避免遮挡视频内容
    // 绘制选区边框
    ctx.strokeStyle = '#00ff00'
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, width, height)
    
    // 绘制角落标记
    const cornerSize = 10
    ctx.strokeStyle = '#00ff00'
    ctx.lineWidth = 3
    
    // 左上角
    ctx.beginPath()
    ctx.moveTo(x, y + cornerSize)
    ctx.lineTo(x, y)
    ctx.lineTo(x + cornerSize, y)
    ctx.stroke()
    
    // 右上角
    ctx.beginPath()
    ctx.moveTo(x + width - cornerSize, y)
    ctx.lineTo(x + width, y)
    ctx.lineTo(x + width, y + cornerSize)
    ctx.stroke()
    
    // 左下角
    ctx.beginPath()
    ctx.moveTo(x, y + height - cornerSize)
    ctx.lineTo(x, y + height)
    ctx.lineTo(x + cornerSize, y + height)
    ctx.stroke()
    
    // 右下角
    ctx.beginPath()
    ctx.moveTo(x + width - cornerSize, y + height)
    ctx.lineTo(x + width, y + height)
    ctx.lineTo(x + width, y + height - cornerSize)
    ctx.stroke()
  } else if (isDrawing.value) {
    // 正在绘制时，绘制临时矩形
    const width = currentX.value - startX.value
    const height = currentY.value - startY.value
    const x = width < 0 ? currentX.value : startX.value
    const y = height < 0 ? currentY.value : startY.value
    const absWidth = Math.abs(width)
    const absHeight = Math.abs(height)
    
    // 只绘制边框，不再绘制半透明遮罩，避免遮挡视频内容
    ctx.strokeStyle = '#00ff00'
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, absWidth, absHeight)
  }
}

// 清除选区
const clearBoxSelection = () => {
  boxSelectionData.value = null
  if (boxCanvas.value) {
    const ctx = boxCanvas.value.getContext('2d')
    ctx.clearRect(0, 0, boxCanvas.value.width, boxCanvas.value.height)
  }
  // 清除该文件的框选状态
  if (currentBoxFileIndex.value >= 0 && boxSelectedMap.value[currentBoxFileIndex.value]) {
    delete boxSelectedMap.value[currentBoxFileIndex.value]
  }
}

// 保存选区 - 截取当前帧并保存为图片
const saveBoxSelection = async () => {
  if (!boxSelectionData.value || currentBoxFileIndex.value < 0) {
    showToast('请先绘制选区', 'error')
    return
  }
  
  const file = selectedFiles.value[currentBoxFileIndex.value]
  if (!file) return
  
  try {
    // 获取视频元素和 canvas
    const video = boxSelectionVideo.value
    const canvas = boxCanvas.value
    const container = videoCanvasContainerRef.value
    
    if (!video || !canvas || !container) {
      showToast('视频或画布未准备好', 'error')
      return
    }
    
    // 关键修复：先跳转到保存的时间点，确保截取的帧与预览时一致
    const targetTime = boxSelectionData.value.timestamp || currentTime.value
    if (Math.abs(video.currentTime - targetTime) > 0.1) {
      video.currentTime = targetTime
      // 等待视频 seek 完成
      await new Promise((resolve) => {
        const onSeeked = () => {
          video.removeEventListener('seeked', onSeeked)
          resolve()
        }
        video.addEventListener('seeked', onSeeked)
        // 超时保护
        setTimeout(resolve, 500)
      })
    }
    
    // 创建一个临时 canvas 用于截取带选区的帧
    const tempCanvas = document.createElement('canvas')
    const tempCtx = tempCanvas.getContext('2d')
    
    // 设置 canvas 尺寸与视频原始分辨率一致
    tempCanvas.width = video.videoWidth
    tempCanvas.height = video.videoHeight
    
    // 关键修复：计算视频实际显示区域（排除 object-fit: contain 产生的黑边）
    // 获取 container 和 video 的显示尺寸
    const containerRect = container.getBoundingClientRect()
    const videoRect = video.getBoundingClientRect()
    
    // 计算视频在 container 中的实际渲染尺寸与原始分辨率的比例
    // 由于 object-fit: contain，视频会被等比例缩放并居中显示，两侧可能有黑边
    // 但 drawImage(video, 0, 0, video.videoWidth, video.videoHeight) 会自动处理
    // 因为 video 元素的 intrinsic size 就是视频的原始分辨率
    
    // 绘制视频当前帧 - 使用最简单的方式，让浏览器自动处理 object-fit
    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height)
    
    // 使用保存的选区数据（已经是基于视频原始分辨率的坐标）
    const { x, y, width, height } = boxSelectionData.value
    
    // 直接使用坐标，因为它们已经是基于视频原始分辨率
    const drawX = x
    const drawY = y
    const drawWidth = width
    const drawHeight = height
    
    // 绘制选区边框
    tempCtx.strokeStyle = '#00ff00'
    tempCtx.lineWidth = 2
    tempCtx.strokeRect(drawX, drawY, drawWidth, drawHeight)
    
    // 绘制角落标记
    const cornerSize = 10
    tempCtx.strokeStyle = '#00ff00'
    tempCtx.lineWidth = 3
    
    // 左上角
    tempCtx.beginPath()
    tempCtx.moveTo(drawX, drawY + cornerSize)
    tempCtx.lineTo(drawX, drawY)
    tempCtx.lineTo(drawX + cornerSize, drawY)
    tempCtx.stroke()
    
    // 右上角
    tempCtx.beginPath()
    tempCtx.moveTo(drawX + drawWidth - cornerSize, drawY)
    tempCtx.lineTo(drawX + drawWidth, drawY)
    tempCtx.lineTo(drawX + drawWidth, drawY + cornerSize)
    tempCtx.stroke()
    
    // 左下角
    tempCtx.beginPath()
    tempCtx.moveTo(drawX, drawY + drawHeight - cornerSize)
    tempCtx.lineTo(drawX, drawY + drawHeight)
    tempCtx.lineTo(drawX + cornerSize, drawY + drawHeight)
    tempCtx.stroke()
    
    // 右下角
    tempCtx.beginPath()
    tempCtx.moveTo(drawX + drawWidth - cornerSize, drawY + drawHeight)
    tempCtx.lineTo(drawX + drawWidth, drawY + drawHeight)
    tempCtx.lineTo(drawX + drawWidth, drawY + drawHeight - cornerSize)
    tempCtx.stroke()
    
    // 将 canvas 转换为 Blob (PNG 格式)
    const blob = await new Promise((resolve) => {
      tempCanvas.toBlob((blob) => {
        resolve(blob)
      }, 'image/png')
    })
    
    if (!blob) {
      showToast('生成图片失败', 'error')
      return
    }
    
    // 创建缩略图文件名
    const thumbnailFileName = file.name.replace(/\.[^/.]+$/, '') + '_frame.png'
    
    // 将截取的帧图片保存到文件对象中
    file.frameImage = {
      blob: blob,
      fileName: thumbnailFileName,
      timestamp: targetTime,
      url: URL.createObjectURL(blob) // 用于预览
    }
    
    // 标记该文件已完成框选
    boxSelectedMap.value[currentBoxFileIndex.value] = true
    
    showToast('帧图片已保存！', 'success')
  } catch (error) {
    console.error('保存帧图片失败:', error)
    showToast('保存帧图片失败', 'error')
  }
  
  // 关闭弹窗
  closeBoxSelection()
}

// 计算属性：是否有选区
const hasBoxSelection = computed(() => {
  return boxSelectionData.value !== null
})

// 计算属性：当前时间显示
const currentTimeDisplay = ref('00:00')

// 计算属性：总时长显示
const durationDisplay = ref('00:00')

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.upload-container {
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
  margin-bottom: 30px;
}

.header h1 {
  font-size: 32px;
  color: #333;
}

.upload-section {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 40px;
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

.form-select,
.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.title-input-group {
  display: flex;
  gap: 10px;
}

.title-input-group .form-input {
  flex: 1;
}

.btn-timestamp {
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
  white-space: nowrap;
}

.btn-timestamp:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-timestamp:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  transition: border-color 0.3s;
  margin: 30px 0;
}

.upload-area:hover {
  border-color: #667eea;
}

.file-input {
  display: none;
}

.upload-placeholder {
  color: #666;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.hint {
  font-size: 13px;
  color: #999;
  margin-top: 10px;
}

/* 视频类型选项样式 */
.video-type-options {
  display: flex;
  gap: 20px;
  padding: 10px 0;
}

.radio-option {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  transition: all 0.2s;
}

.radio-option:hover {
  border-color: #667eea;
  background: #f5f7ff;
}

.radio-option input[type="radio"] {
  margin-right: 8px;
  accent-color: #667eea;
}

.radio-option input[type="radio"]:disabled {
  cursor: not-allowed;
}

.radio-option .option-label {
  font-size: 14px;
  color: #333;
}

.btn-select {
  margin-top: 15px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  font-weight: 600;
}

.btn-select:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.file-info {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

/* 框选成功后的文件项样式 */
.file-info.box-selected-file {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border: 2px solid #10b981;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
}

/* 未框选警告样式（红色边框） */
.file-info.box-unselected-warning {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 2px solid #ef4444;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
}

.file-actions {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin-top: 8px;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-list {
  max-height: 400px;
  overflow-y: auto;
}

.btn-add-more {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 15px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-add-more:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-add-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.file-title-preview {
  font-size: 12px;
  color: #667eea;
  margin-top: 4px;
  font-weight: 500;
}

/* 文件级别的视频类型选项样式 */
.file-video-type-options {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  padding: 6px 10px;
  background: #f0f0f0;
  border-radius: 4px;
}

.radio-option-small {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.radio-option-small:hover {
  opacity: 0.8;
}

.radio-option-small input[type="radio"] {
  margin-right: 4px;
  accent-color: #667eea;
  cursor: pointer;
}

.radio-option-small input[type="radio"]:disabled {
  cursor: not-allowed;
}

.radio-option-small .option-label-small {
  font-size: 12px;
  color: #333;
  font-weight: 500;
}

/* 单个文件进度条样式 */
.file-progress {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-progress-bar {
  flex: 1;
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.file-progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
}

.file-progress-text {
  font-size: 11px;
  color: #667eea;
  font-weight: 600;
  min-width: 35px;
  text-align: right;
}

.file-icon {
  font-size: 36px;
}

.file-details {
  flex: 1;
  text-align: left;
}

.file-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.file-size {
  font-size: 13px;
  color: #999;
}

.btn-remove {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f0f0;
  color: #666;
  border: none;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-remove:hover:not(:disabled) {
  background: #e74c3c;
  color: white;
}

.btn-remove:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-box-select {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f0f0;
  color: #666;
  border: none;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-box-select:hover:not(:disabled) {
  background: #667eea;
  color: white;
}

.btn-box-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 框选成功后的样式 */
.btn-box-select.box-selected {
  background: #10b981;
  color: white;
  border: 2px solid #059669;
  animation: pulse-success 0.5s ease-in-out;
}

@keyframes pulse-success {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn-primary {
  padding: 12px 30px;
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
  cursor: not-allowed;
}

.btn-secondary {
  padding: 12px 30px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  margin-top: 20px;
  padding: 15px;
  background: #fee;
  color: #c33;
  border-radius: 6px;
  border-left: 4px solid #c33;
}

.success-message {
  margin-top: 30px;
  padding: 30px;
  background: #efe;
  border-radius: 12px;
  text-align: center;
  border-left: 4px solid #4a4;
}

.success-icon {
  font-size: 48px;
  color: #4a4;
  margin-bottom: 15px;
}

.success-message p {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
}

.video-preview {
  margin: 20px 0;
}

.video-player {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.success-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
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

/* 分析中按钮样式 */
.btn-loading {
  background: linear-gradient(135deg, #95a5a6 0%, #bdc3c7 100%);
  cursor: not-allowed;
  opacity: 0.8;
}

.btn-loading:hover {
  transform: none;
}

/* 点击查看分析按钮样式 */
.btn-view-analysis {
  padding: 12px 30px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  font-weight: 600;
}

.btn-view-analysis:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
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

  .header h1 {
    font-size: 26px;
  }

  .upload-section {
    padding: 25px 20px;
  }

  .actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }

  .success-actions {
    flex-direction: column;
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

  .upload-section {
    padding: 20px 15px;
  }

  .upload-area {
    padding: 25px 15px;
  }

  .file-info {
    flex-direction: column;
    text-align: center;
  }

  .file-details {
    text-align: center;
  }
}

/* 多视频列表样式 */
.video-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 20px 0;
}

.video-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  gap: 20px;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.video-thumbnail-wrapper {
  flex-shrink: 0;
}

.video-thumbnail {
  position: relative;
  width: 320px;
  height: 180px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background: #000;
  transition: transform 0.2s, box-shadow 0.2s;
}

.video-thumbnail:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.thumbnail-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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

.play-icon {
  font-size: 48px;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

.video-info {
  flex: 1;
}

.video-info h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
}

.video-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.video-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex-shrink: 0;
}

.btn-preview-small {
  padding: 10px 20px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-preview-small:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
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

/* 单视频缩略图样式 */
.video-thumbnail-wrapper-single {
  margin: 20px 0;
  display: flex;
  justify-content: center;
}

.video-thumbnail-wrapper-single .video-thumbnail {
  width: 640px;
  height: 360px;
}

.thumbnail-image-single {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.thumbnail-placeholder-single {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.btn-preview {
  padding: 12px 30px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-preview:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
}

/* 预览弹窗样式 - 与我的视频页面保持一致 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.preview-modal {
  background: white;
  border-radius: 12px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  animation: slideUp 0.3s ease;
  display: flex;
  flex-direction: column;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.btn-close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f0f0f0;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.btn-close:hover {
  background: #e0e0e0;
}

.modal-body {
  padding: 20px;
  background: #000;
  flex: 1;
  overflow-y: auto;
}

.video-player-full {
  width: 100%;
  max-height: 70vh;
  display: block;
}

.video-details {
  padding: 15px 0;
  color: #fff;
}

.detail-item {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item .label {
  color: #aaa;
}

.detail-item .value {
  color: #fff;
}

.modal-footer {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 15px 20px;
  border-top: 1px solid #eee;
  background: #f9f9f9;
}

/* 框选弹窗样式 */
.box-selection-modal {
  width: 90vw;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  min-height: 0; /* 允许 modal 在 flex 布局中正确收缩 */
  height: 90vh; /* 固定高度以更好地处理纵向视频 */
}

.box-selection-body {
  padding: 20px;
  background: #1a1a1a;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-height: 0; /* 允许 flex 子项收缩以适应容器 */
}

.box-selection-instructions {
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  color: #fff;
  flex-shrink: 0; /* 防止说明区域被压缩 */
}

.box-selection-instructions p {
  margin: 5px 0;
  font-size: 14px;
}

.video-canvas-container {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  /* 移除固定宽高比，让容器自适应视频实际比例 */
  flex: 1; /* 让容器占据剩余空间 */
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0; /* 允许容器收缩 */
}

.box-selection-video {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  display: block;
  object-fit: contain;
}

.box-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: crosshair;
  /* 确保 canvas 内容透明，不遮挡视频 */
  background: transparent;
  pointer-events: auto;
  /* Canvas 内部尺寸由 JS 设置为视频实际分辨率 */
}

.video-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  flex-shrink: 0; /* 防止控制栏被压缩 */
}

.btn-control {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn-control:hover {
  background: #45a049;
}

.progress-slider {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  outline: none;
}

.progress-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #4CAF50;
  border-radius: 50%;
  cursor: pointer;
}

.progress-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #4CAF50;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.time-display {
  color: #fff;
  font-size: 14px;
  min-width: 100px;
  text-align: right;
  font-family: monospace;
}

.box-selection-footer {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 15px 20px;
  border-top: 1px solid #333;
  background: #2a2a2a;
  flex-shrink: 0; /* 防止底部按钮区域被压缩 */
}

.box-selection-footer .btn-primary,
.box-selection-footer .btn-secondary {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.box-selection-footer .btn-primary {
  background: #4CAF50;
  color: white;
  border: none;
}

.box-selection-footer .btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.box-selection-footer .btn-primary:disabled {
  background: #666;
  cursor: not-allowed;
}

.box-selection-footer .btn-secondary {
  background: transparent;
  color: #fff;
  border: 1px solid #666;
}

.box-selection-footer .btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.box-selection-footer .btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .video-item {
    flex-direction: column;
    text-align: center;
  }
  
  .video-thumbnail {
    width: 100%;
    height: auto;
    aspect-ratio: 16/9;
  }
  
  .video-actions {
    width: 100%;
    flex-direction: row;
    justify-content: center;
  }
  
  .btn-preview-small,
  .btn-analyze-small {
    width: 100%;
  }
  
  .video-thumbnail-wrapper-single .video-thumbnail {
    width: 100%;
    height: auto;
    aspect-ratio: 16/9;
  }
  
  .preview-content {
    max-width: 95vw;
  }
}

.loading-spinner {
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
