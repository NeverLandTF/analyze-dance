<script setup>
import { ref } from 'vue'

const visible = ref(false)
const config = ref({
  title: '确认操作',
  message: '',
  confirmText: '确定',
  cancelText: '取消',
  type: 'warning' // warning, danger
})

let resolvePromise = null

const show = (options = {}) => {
  config.value = {
    title: options.title || '确认操作',
    message: options.message || '',
    confirmText: options.confirmText || '确定',
    cancelText: options.cancelText || '取消',
    type: options.type || 'warning'
  }
  visible.value = true
  
  return new Promise((resolve) => {
    resolvePromise = resolve
  })
}

const handleConfirm = () => {
  visible.value = false
  if (resolvePromise) {
    resolvePromise(true)
    resolvePromise = null
  }
}

const handleCancel = () => {
  visible.value = false
  if (resolvePromise) {
    resolvePromise(false)
    resolvePromise = null
  }
}

defineExpose({ show })
</script>

<template>
  <transition name="fade">
    <div v-if="visible" class="modal-overlay" @click.self="handleCancel">
      <div class="confirm-dialog">
        <div class="dialog-header" :class="`header-${config.type}`">
          <span class="dialog-icon">
            {{ config.type === 'danger' ? '⚠️' : '❓' }}
          </span>
          <h3 class="dialog-title">{{ config.title }}</h3>
        </div>
        <div class="dialog-body">
          <p class="dialog-message">{{ config.message }}</p>
        </div>
        <div class="dialog-footer">
          <button @click="handleCancel" class="btn-cancel">
            {{ config.cancelText }}
          </button>
          <button @click="handleConfirm" class="btn-confirm" :class="`btn-${config.type}`">
            {{ config.confirmText }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
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
  z-index: 9998;
  backdrop-filter: blur(4px);
}

.confirm-dialog {
  background: white;
  border-radius: 16px;
  min-width: 400px;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.dialog-header {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #eee;
}

.header-warning {
  background: linear-gradient(135deg, #fff7e6 0%, #fff 100%);
}

.header-danger {
  background: linear-gradient(135deg, #fff1f0 0%, #fff 100%);
}

.dialog-icon {
  font-size: 28px;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.dialog-body {
  padding: 24px;
}

.dialog-message {
  font-size: 15px;
  color: #555;
  line-height: 1.6;
  margin: 0;
  white-space: pre-line;
}

.dialog-footer {
  padding: 16px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #f9f9f9;
  border-top: 1px solid #eee;
}

.btn-cancel {
  padding: 10px 24px;
  border: 1px solid #ddd;
  background: white;
  color: #666;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.btn-confirm {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
}

.btn-confirm.btn-warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.btn-confirm.btn-warning:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
}

.btn-confirm.btn-danger {
  background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
}

.btn-confirm.btn-danger:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(235, 51, 73, 0.4);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-from .confirm-dialog,
.fade-leave-to .confirm-dialog {
  transform: translateY(-20px) scale(0.95);
}
</style>
