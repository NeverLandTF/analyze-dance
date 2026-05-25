<template>
  <div class="placeholder-view">
    <h1>进步追踪</h1>
    <p>该页面正在开发中...</p>
    <router-link to="/dancers" class="btn-home">返回舞者列表</router-link>
  </div>
</template>

<script setup>
// 进步追踪页面 - 待实现
</script>

<style scoped>
.placeholder-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 20px;
}

h1 {
  font-size: 36px;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

p {
  font-size: 18px;
  color: #666;
  margin-bottom: 30px;
  text-align: center;
}

.btn-home {
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  transition: transform 0.2s;
}

.btn-home:hover {
  transform: translateY(-2px);
}

/* 移动端适配 */
@media (max-width: 768px) {
  h1 {
    font-size: 28px;
  }

  p {
    font-size: 16px;
  }

  .btn-home {
    padding: 10px 24px;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: 24px;
  }

  p {
    font-size: 14px;
  }

  .btn-home {
    padding: 10px 20px;
    font-size: 14px;
  }
}
</style>
