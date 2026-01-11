import { createApp } from 'vue'
import './style.css'
import './assets/variables.css' // 设计系统变量
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'
import naive from 'naive-ui'
import 'vfonts/Lato.css' // 通用字体
import 'vfonts/FiraCode.css' // 等宽字体

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(naive)

app.mount('#app')
