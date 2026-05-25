<template>
  <div class="dancer-list-container">
    <nav class="navbar">
      <div class="nav-brand">🎵 舞蹈 AI 分析</div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <button @click="handleLogout" class="btn-logout">退出</button>
      </div>
    </nav>
    
    <main class="main-content">
      <div class="header">
        <h1>舞者管理</h1>
        <div class="header-actions">
          <span v-if="userStore.isAdmin" class="admin-badge">管理员</span>
          <button @click="showCreateModal = true" class="btn-primary">+ 创建新舞者</button>
        </div>
      </div>
      
      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="dancers.length === 0" class="empty-state">
        <p>暂无舞者，点击上方按钮创建第一个舞者</p>
      </div>
      
      <div v-else class="dancers-grid">
        <div 
          v-for="dancer in dancers" 
          :key="dancer.id" 
          class="dancer-card"
          @click="$router.push(`/dancers/${dancer.id}`)"
        >
          <div class="dancer-avatar">
            {{ dancer.name.charAt(0).toUpperCase() }}
          </div>
          <h3>{{ dancer.name }}</h3>
          <p class="description">{{ dancer.description || '暂无描述' }}</p>
          <div class="stats">
            <span>视频数：{{ dancer.video_count }}</span>
            <span v-if="dancer.owner_username && !userStore.isAdmin" class="owner-info">所有者：{{ dancer.owner_username }}</span>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 创建舞者模态框 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h2>创建新舞者</h2>
        <form @submit.prevent="handleCreate">
          <div class="form-group">
            <label>舞者名称</label>
            <input 
              type="text" 
              v-model="newDancer.name" 
              required 
              placeholder="输入舞者名称"
            />
          </div>
          
          <div class="form-group">
            <label>描述</label>
            <textarea 
              v-model="newDancer.description" 
              placeholder="可选：舞者的简介或风格"
              rows="3"
            ></textarea>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="btn-secondary">取消</button>
            <button type="submit" :disabled="creating" class="btn-primary">
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dancerAPI } from '../api/modules'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const dancers = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const creating = ref(false)

const newDancer = reactive({
  name: '',
  description: ''
})

onMounted(async () => {
  await loadDancers()
})

const loadDancers = async () => {
  try {
    // 管理员不需要传 user_id，可以查看所有舞者
    const response = await dancerAPI.getDancers(userStore.userId, userStore.isAdmin)
    dancers.value = response.dancers
  } catch (error) {
    console.error('加载舞者列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  creating.value = true
  
  try {
    // 管理员创建舞者时，可以选择分配给任何用户（这里简化为分配给自己或创建公共舞者）
    await dancerAPI.createDancer({
      user_id: userStore.userId,
      name: newDancer.name,
      description: newDancer.description
    })
    
    showCreateModal.value = false
    newDancer.name = ''
    newDancer.description = ''
    
    await loadDancers()
  } catch (error) {
    alert('创建失败：' + (error.response?.data?.error || '请稍后重试'))
  } finally {
    creating.value = false
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dancer-list-container {
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

.btn-logout {
  padding: 8px 20px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.admin-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
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
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
}

.loading, .empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 18px;
}

.dancers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.dancer-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.dancer-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.dancer-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 15px;
}

.dancer-card h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 10px;
}

.description {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
  line-height: 1.5;
}

.stats {
  color: #999;
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.owner-info {
  color: #667eea;
  font-size: 12px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: white;
  padding: 40px;
  border-radius: 12px;
  width: 100%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h2 {
  margin-bottom: 25px;
  color: #333;
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

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 25px;
}

.btn-secondary {
  padding: 12px 24px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
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

  .dancers-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 20px;
  }

  .dancer-card {
    padding: 25px;
  }

  .modal {
    padding: 30px 20px;
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

  .btn-logout {
    padding: 6px 16px;
    font-size: 14px;
  }

  .main-content {
    padding: 20px 10px;
  }

  .header h1 {
    font-size: 22px;
  }

  .dancers-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .dancer-card {
    padding: 20px;
  }

  .dancer-avatar {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }

  .dancer-card h3 {
    font-size: 18px;
  }

  .description {
    font-size: 13px;
  }

  .modal {
    padding: 25px 15px;
  }

  .form-group input,
  .form-group textarea {
    font-size: 16px; /* 防止 iOS 缩放 */
    padding: 10px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
  }
}
</style>
