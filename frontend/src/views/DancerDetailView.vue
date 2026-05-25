<template>
  <div class="placeholder-view">
    <h1>舞者详情页</h1>
    <p>该页面正在开发中...</p>
    <router-link to="/dancers" class="btn-home">返回舞者列表</router-link>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

onMounted(() => {
  console.log('Dancer ID:', route.params.id)
})
</script>

<style scoped>
.placeholder-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

h1 {
  font-size: 36px;
  color: #333;
  margin-bottom: 20px;
}

p {
  font-size: 18px;
  color: #666;
  margin-bottom: 30px;
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
</style>
