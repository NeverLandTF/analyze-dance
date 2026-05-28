<script setup>
import { ref, provide } from 'vue'
import Toast from './components/Toast.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'

// 创建全局 toast 引用
const toastRef = ref(null)
// 创建全局 confirmDialog 引用
const confirmDialogRef = ref(null)

// 提供全局 toast 方法给所有子组件
const showToast = (message, type = 'info', duration = 3000) => {
  if (toastRef.value) {
    toastRef.value.show(message, type, duration)
  }
}

// 提供全局 confirmDialog 方法给所有子组件
const showConfirm = (options = {}) => {
  if (confirmDialogRef.value) {
    return confirmDialogRef.value.show(options)
  }
  return Promise.resolve(false)
}

// 将 showToast 和 showConfirm 挂载到全局属性，使得所有组件可以通过 inject 获取
provide('toast', showToast)
provide('confirm', showConfirm)
</script>

<template>
  <router-view />
  <Toast ref="toastRef" />
  <ConfirmDialog ref="confirmDialogRef" />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}
</style>
