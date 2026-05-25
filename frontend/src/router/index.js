import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue')
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: () => import('../views/UserProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dancers',
    name: 'Dancers',
    component: () => import('../views/DancerListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dancers/:id',
    name: 'DancerDetail',
    component: () => import('../views/DancerDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'UploadVideo',
    component: () => import('../views/UploadVideoView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/analysis/:videoId',
    name: 'AnalysisResult',
    component: () => import('../views/AnalysisResultView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/progress/:dancerId',
    name: 'ProgressTracking',
    component: () => import('../views/ProgressTrackingView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/')
  } else {
    next()
  }
})

export default router
