<template>
  <div class="login-container">
    <!-- 左侧品牌展示区 -->
    <div class="brand-section">
      <div class="brand-content">
        <div class="logo-area">
          <div class="logo-icon gradient-bg">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="brand-title">WeChat Agent</h1>
        </div>
        <p class="brand-slogan">AI驱动的微信公众号内容创作平台</p>
        <div class="feature-list">
          <div class="feature-item" v-for="(feature, index) in features" :key="index">
            <div class="feature-icon">✓</div>
            <span>{{ feature }}</span>
          </div>
        </div>
      </div>
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>

    <!-- 右侧表单区 -->
    <div class="form-section">
      <div class="form-container">
        <div class="form-header">
          <h2>欢迎回来</h2>
          <p>登录您的账户，继续创作精彩内容</p>
        </div>

        <n-form ref="formRef" :model="model" :rules="rules" size="large">
          <n-form-item path="username">
            <n-input
              v-model:value="model.username"
              placeholder="用户名"
              :input-props="{ autocomplete: 'username' }"
            >
              <template #prefix>
                <n-icon :component="User" />
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password">
            <n-input
              v-model:value="model.password"
              type="password"
              show-password-on="click"
              placeholder="密码"
              :input-props="{ autocomplete: 'current-password' }"
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <n-icon :component="Lock" />
              </template>
            </n-input>
          </n-form-item>

          <n-button
            type="primary"
            size="large"
            block
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            登录
          </n-button>
        </n-form>

        <div class="form-footer">
          <span>还没有账户？</span>
          <router-link to="/register" class="link-text">注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NForm, NFormItem, NInput, NButton, NIcon } from 'naive-ui'
import { User, Lock } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const features = [
  'AI智能生成文章内容',
  '一键同步到微信草稿箱',
  '多样式模板自由选择'
]

const model = reactive({
  username: '',
  password: ''
})

const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' }
}

const handleLogin = () => {
  ;(formRef.value as any)?.validate(async (errors: any) => {
    if (!errors) {
      loading.value = true
      try {
        await authStore.login(model)
        message.success('登录成功')
        router.push({ name: 'Dashboard' })
      } catch (error: any) {
        const errorMsg = error.response?.data?.detail || error.message || '登录失败'
        message.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
  background: var(--bg-base);
}

/* ========== 左侧品牌展示区 ========== */
.brand-section {
  flex: 1;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: var(--spacing-2xl);
}

.brand-content {
  position: relative;
  z-index: 2;
  color: white;
  max-width: 500px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.logo-icon {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-lg);
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.brand-slogan {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: var(--spacing-xl);
  line-height: 1.6;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 16px;
  color: rgba(255, 255, 255, 0.95);
}

.feature-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

/* 装饰圆圈 */
.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(2px);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -50px;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: 50px;
  left: -50px;
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: 200px;
  right: 100px;
}

/* ========== 右侧表单区 ========== */
.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}

.form-container {
  width: 100%;
  max-width: 420px;
  background: var(--bg-card);
  padding: var(--spacing-2xl);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.form-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.form-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.form-header p {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 按钮样式 */
.login-button {
  margin-top: var(--spacing-md);
  background: var(--primary-gradient);
  border: none;
  font-weight: 600;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.login-button:active {
  transform: translateY(0);
}

.form-footer {
  margin-top: var(--spacing-lg);
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.link-text {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
  margin-left: var(--spacing-xs);
  transition: color var(--transition-fast);
}

.link-text:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .brand-section {
    display: none;
  }
  
  .form-section {
    flex: 1;
    background: var(--primary-gradient);
  }
  
  .form-container {
    background: var(--bg-card);
  }
}

@media (max-width: 640px) {
  .form-container {
    padding: var(--spacing-lg);
  }
  
  .form-header h2 {
    font-size: 24px;
  }
}
</style>
