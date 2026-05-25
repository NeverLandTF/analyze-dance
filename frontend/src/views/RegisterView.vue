<template>
  <div class="register-container">
    <div class="register-box">
      <h1>注册账号</h1>
      <p class="subtitle">开始追踪您的舞蹈进步之旅</p>
      
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="avatar">头像</label>
          <div class="avatar-upload">
            <div v-if="avatarPreview" class="avatar-preview" :style="{ backgroundImage: `url(${avatarPreview})` }"></div>
            <div v-else class="avatar-placeholder">
              <span>?</span>
            </div>
            <label for="avatar-input" class="upload-btn">
              选择图片
              <input 
                type="file" 
                id="avatar-input" 
                accept="image/*" 
                @change="handleAvatarChange"
                style="display: none;"
              />
            </label>
          </div>
        </div>
        
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="formData.username" 
            required 
            placeholder="请输入用户名"
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="formData.email" 
            required 
            placeholder="请输入邮箱"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="formData.password" 
            required 
            placeholder="请输入密码"
            minlength="6"
          />
        </div>
        
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>
        
        <p class="switch-form">
          已有账号？<router-link to="/login">立即登录</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api/modules'
import api from '../api/index'

const router = useRouter()

const formData = reactive({
  username: '',
  email: '',
  password: ''
})

const avatarFile = ref(null)
const avatarPreview = ref(null)
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    error.value = '请选择图片文件'
    return
  }
  
  // 验证文件大小（最大 5MB）
  if (file.size > 5 * 1024 * 1024) {
    error.value = '图片大小不能超过 5MB'
    return
  }
  
  avatarFile.value = file
  error.value = ''
  
  // 创建预览 URL
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const uploadAvatarToBackend = async () => {
  if (!avatarFile.value) return null
  
  const formDataUpload = new FormData()
  formDataUpload.append('file', avatarFile.value)
  
  try {
    // 使用后端头像上传接口（临时用户 ID，实际会在注册后关联）
    // 这里我们先上传到一个临时位置，注册成功后再关联到用户
    const response = await api.post('/upload/temp-avatar', formDataUpload, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response && response.avatar_url) {
      return response.avatar_url
    }
    return null
  } catch (err) {
    console.error('上传头像失败:', err)
    return null
  }
}

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    let avatarUrl = null
    
    // 如果选择了头像，先上传头像到后端
    if (avatarFile.value) {
      avatarUrl = await uploadAvatarToBackend()
      if (!avatarUrl) {
        // 头像上传失败，但仍然允许注册（头像是可选的）
        console.warn('头像上传失败，将使用默认头像')
      }
    }
    
    await authAPI.register(formData.username, formData.email, formData.password, avatarUrl)
    
    success.value = '注册成功！即将跳转到登录页面...'
    
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    error.value = err.response?.data?.error || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 28px;
  text-align: center;
}

.subtitle {
  color: #666;
  text-align: center;
  margin-bottom: 30px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

/* 头像上传样式 */
.avatar-upload {
  display: flex;
  align-items: center;
  gap: 15px;
}

.avatar-preview,
.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
  background-color: #f0f0f0;
  border: 2px solid #667eea;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #999;
}

.upload-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: transform 0.2s;
  display: inline-block;
}

.upload-btn:hover {
  transform: translateY(-2px);
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
}

.success-message {
  color: #27ae60;
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
}

.switch-form {
  text-align: center;
  margin-top: 20px;
  color: #666;
  font-size: 14px;
}

.switch-form a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.switch-form a:hover {
  text-decoration: underline;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .register-container {
    padding: 15px;
  }

  .register-box {
    padding: 30px 20px;
  }

  h1 {
    font-size: 24px;
  }

  .subtitle {
    font-size: 13px;
  }

  input {
    padding: 10px;
    font-size: 16px; /* 防止 iOS 缩放 */
  }

  .btn-primary {
    padding: 14px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .register-box {
    padding: 25px 15px;
  }

  h1 {
    font-size: 22px;
  }
}
</style>
