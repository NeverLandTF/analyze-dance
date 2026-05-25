import api from './index'

export const authAPI = {
  // 用户注册
  register(username, email, password) {
    return api.post('/auth/register', { username, email, password })
  },
  
  // 用户登录
  login(username, password) {
    return api.post('/auth/login', { username, password })
  }
}

export const dancerAPI = {
  // 获取所有舞者
  getDancers(userId, isAdmin = false) {
    return api.get(`/dancers?user_id=${userId}&is_admin=${isAdmin}`)
  },
  
  // 创建舞者
  createDancer(userData) {
    return api.post('/dancers', userData)
  },
  
  // 获取舞者详情
  getDancer(dancerId) {
    return api.get(`/dancers/${dancerId}`)
  }
}

export const videoAPI = {
  // 上传视频
  uploadVideo(videoData) {
    return api.post('/videos', videoData)
  }
}

export const analysisAPI = {
  // 分析视频
  analyzeVideo(videoId, userId) {
    return api.post('/analyze', { video_id: videoId, user_id: userId })
  }
}

export const progressAPI = {
  // 获取进步追踪数据
  getProgress(dancerId) {
    return api.get(`/progress/${dancerId}`)
  }
}
