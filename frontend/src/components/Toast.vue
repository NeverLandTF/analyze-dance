<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'info', // info, success, error, warning
    validator: (value) => ['info', 'success', 'error', 'warning'].includes(value)
  },
  duration: {
    type: Number,
    default: 3000
  }
})

const emit = defineEmits(['close'])

const visible = ref(false)
const toastMessage = ref('')
const toastType = ref('info')
let timer = null

const typeConfig = {
  info: {
    icon: '🔔',
    title: '提示'
  },
  success: {
    icon: '✅',
    title: '成功'
  },
  error: {
    icon: '❌',
    title: '错误'
  },
  warning: {
    icon: '⚠️',
    title: '警告'
  }
}

const show = (message, type = 'info', duration = 3000) => {
  toastMessage.value = message
  toastType.value = type
  visible.value = true
  
  if (timer) {
    clearTimeout(timer)
  }
  
  timer = setTimeout(() => {
    hide()
  }, duration)
}

const hide = () => {
  visible.value = false
  emit('close')
}

defineExpose({ show })

onUnmounted(() => {
  if (timer) {
    clearTimeout(timer)
  }
})
</script>

<template>
  <transition name="toast">
    <div v-if="visible" class="toast" :class="`toast-${toastType}`">
      <span class="toast-icon">{{ typeConfig[toastType].icon }}</span>
      <div class="toast-content">
        <div class="toast-title">{{ typeConfig[toastType].title }}</div>
        <span class="toast-message">{{ toastMessage }}</span>
      </div>
      <button @click="hide" class="toast-close">×</button>
    </div>
  </transition>
</template>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 12px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
  z-index: 9999;
  min-width: 320px;
  max-width: 500px;
  backdrop-filter: blur(10px);
}

.toast-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.toast-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.toast-error {
  background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
}

.toast-warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.toast-icon {
  font-size: 22px;
  flex-shrink: 0;
  line-height: 1;
}

.toast-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toast-title {
  font-size: 15px;
  font-weight: 600;
  opacity: 0.95;
}

.toast-message {
  font-size: 13px;
  opacity: 0.9;
  word-break: break-word;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  color: white;
  font-size: 22px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.toast-close:hover {
  opacity: 1;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>
