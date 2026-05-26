import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { useUserStore } from './stores/user'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// 在路由之前初始化用户 store，确保刷新页面时从 localStorage 恢复登录状态
const userStore = useUserStore(pinia)

app.use(router)
app.mount('#app')
