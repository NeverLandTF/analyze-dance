<script setup>
import { ref } from 'vue'

// 创建全局 toast 引用
const toastRef = ref(null)

// 提供全局 toast 方法给所有子组件
const showToast = (message, type = 'info', duration = 3000) => {
  if (toastRef.value) {
    toastRef.value.show(message, type, duration)
  }
}

// 将 showToast 挂载到全局属性，使得所有组件可以通过 this.$toast 或 getCurrentInstance().appContext.config.globalProperties.$toast 访问
// 但更简单的方式是在每个组件中通过 inject 获取
import { provide } from 'vue'
provide('toast', showToast)
</script>

<template>
  <router-view />
  <Toast ref="toastRef" />
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
