import api from './index'

export const authAPI = {
  // 用户注册
  register(username, email, password, avatarUrl = null) {
    return api.post('/auth/register', { username, email, password, avatar_url: avatarUrl })
  },
  
  // 用户登录
  login(username, password) {
    return api.post('/auth/login', { username, password })
  },
  
  // 获取用户信息
  getUser(userId) {
    return api.get(`/users/${userId}`)
  },
  
  // 更新用户头像（支持文件上传）
  updateAvatar(userId, avatarUrl) {
    return api.put(`/users/${userId}/avatar`, { avatar_url: avatarUrl })
  },
  
  // 上传头像文件
  uploadAvatarFile(userId, file) {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.put(`/users/${userId}/avatar`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 修改密码
  changePassword(userId, oldPassword, newPassword) {
    return api.post(`/users/${userId}/change-password`, { old_password: oldPassword, new_password: newPassword })
  }
}

export const userAPI = {
  // 获取所有用户（仅管理员）
  getUsers(userId, isAdmin = false) {
    return api.get(`/users?user_id=${userId}&is_admin=${isAdmin}`)
  },
  
  // 创建用户（仅管理员）
  createUser(userData) {
    return api.post('/users', userData)
  },
  
  // 获取用户详情
  getUser(userId) {
    return api.get(`/users/${userId}`)
  },

  // 更新用户信息（包括角色）（仅管理员）
  updateUser(userId, userData) {
    return api.put(`/users/${userId}`, userData)
  },

  // 删除用户（仅管理员）
  deleteUser(userId) {
    return api.delete(`/users/${userId}`)
  },
  
  // 根据舞者 ID 获取对应的用户信息
  getDancerUser(dancerId) {
    return api.get(`/dancers/${dancerId}/user`)
  }
}

// 向后兼容的 dancerAPI，已废弃，请使用 userAPI
export const dancerAPI = {
  // 获取所有用户（仅管理员，已废弃，请使用 userAPI.getUsers）
  getDancers(userId, isAdmin = false) {
    return userAPI.getUsers(userId, isAdmin)
  },
  
  // 创建用户（已废弃，请使用 userAPI.createUser）
  createDancer(userData) {
    return userAPI.createUser(userData)
  },
  
  // 获取用户详情（已废弃，请使用 userAPI.getUser）
  getDancer(dancerId) {
    return userAPI.getUser(dancerId)
  }
}

export const videoAPI = {
  // 上传视频文件
  uploadVideoFile(file, userId, dancerId, title, danceStyle = '', onProgress = null, videoType = 'single', frameImageBlob = null) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_id', userId)
    // 只在 dancerId 有值时添加，允许后端自动获取默认舞者
    if (dancerId) {
      formData.append('dancer_id', dancerId)
    }
    formData.append('title', title)
    if (danceStyle) {
      formData.append('dance_style', danceStyle)
    }
    // 添加视频类型参数（单人/多人）
    formData.append('video_type', videoType)
    
    // 如果有框选的帧图片，添加到 formData 中
    if (frameImageBlob) {
      formData.append('frame_image', frameImageBlob, 'frame.png')
    }
    
    return api.post('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        if (onProgress) {
          onProgress(percentCompleted)
        }
      }
    })
  },
  
  // 获取视频列表（支持时间过滤和分页）
  getVideos(userId, dancerId = null, params = {}) {
    let url = `/videos?user_id=${userId}`
    if (dancerId) {
      url += `&dancer_id=${dancerId}`
    }
    // 添加时间过滤参数
    if (params.startDate) {
      url += `&start_date=${params.startDate}`
    }
    if (params.endDate) {
      url += `&end_date=${params.endDate}`
    }
    // 添加分页参数
    if (params.page) {
      url += `&page=${params.page}`
    }
    if (params.perPage) {
      url += `&per_page=${params.perPage}`
    }
    return api.get(url)
  },
  
  // 获取单个视频详情（不再包含 analyses 字段）
  getVideo(videoId) {
    return api.get(`/videos/${videoId}`)
  },
  
  // 获取单个视频的分析结果列表（新增接口）
  getVideoAnalyses(videoId) {
    return api.get(`/videos/${videoId}/analyses`)
  },
  
  // 删除视频
  deleteVideo(videoId) {
    return api.delete(`/videos/${videoId}`)
  },
  
  // 上传视频（元数据方式，兼容旧接口）
  uploadVideo(videoData) {
    return api.post('/videos', videoData)
  }
}

export const analysisAPI = {
  // 分析视频
  analyzeVideo(videoId, userId, videoUrl) {
    return api.post('/analyze', { video_id: videoId, user_id: userId, video_url: videoUrl })
  },
  
  // 重新分析视频（更新原记录，不生成新记录）
  reanalyzeVideo(analysisId) {
    return api.post(`/analysis/${analysisId}/reanalyze`)
  },
  
  // 获取视频分析结果（使用新的专用接口）
  getAnalysisResults(videoId) {
    return api.get(`/videos/${videoId}/analyses`).then(res => res.analyses || [])
  },

  // 获取分析详情（新增接口）
  getAnalysisDetail(analysisId) {
    return api.get(`/analysis/${analysisId}`)
  },

  // 获取分析历史列表（支持时间过滤、舞者过滤和分页）
  getAnalysisHistory(userId, dancerId = null, params = {}) {
    let url = `/analysis/history?user_id=${userId}`
    if (dancerId) {
      url += `&dancer_id=${dancerId}`
    }
    // 添加时间过滤参数
    if (params.startDate) {
      url += `&start_date=${params.startDate}`
    }
    if (params.endDate) {
      url += `&end_date=${params.endDate}`
    }
    // 添加分页参数
    if (params.page) {
      url += `&page=${params.page}`
    }
    if (params.perPage) {
      url += `&per_page=${params.perPage}`
    }
    return api.get(url)
  }
}

export const progressAPI = {
  // 获取进步追踪数据
  getProgress(dancerId, params = {}) {
    let url = `/progress/${dancerId}`
    // 添加 dancer_id 参数（用于管理员选择特定舞者）
    if (params.dancerId) {
      url += `?dancer_id=${params.dancerId}`
    }
    return api.get(url)
  }
}
