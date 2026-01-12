<template>
  <div class="register-container">
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
        <p class="brand-slogan">开启AI内容创作之旅</p>
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
          <h2>创建账户</h2>
          <p>注册后即可开始使用所有功能</p>
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

          <n-form-item path="email">
            <n-input
              v-model:value="model.email"
              placeholder="邮箱地址"
              :input-props="{ autocomplete: 'email' }"
            >
              <template #prefix>
                <n-icon :component="Mail" />
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password">
            <n-input
              v-model:value="model.password"
              type="password"
              show-password-on="click"
              placeholder="密码"
              :input-props="{ autocomplete: 'new-password' }"
            >
              <template #prefix>
                <n-icon :component="Lock" />
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="confirm_password">
            <n-input
              v-model:value="model.confirm_password"
              type="password"
              show-password-on="click"
              placeholder="确认密码"
              :input-props="{ autocomplete: 'new-password' }"
              @keyup.enter="handleRegister"
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
            @click="handleRegister"
            class="register-button"
          >
            注册
          </n-button>
        </n-form>

        <div class="form-footer">
          <span>已有账户？</span>
          <router-link to="/login" class="link-text">登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NForm, NFormItem, NInput, NButton, NIcon } from 'naive-ui'
import { User, Mail, Lock } from 'lucide-vue-next'
import { authApi } from '@/api/auth'

const router = useRouter()
const message = useMessage()
const formRef = ref(null)
const loading = ref(false)

const features = [
  '完全免费使用',
  '安全的数据加密',
  '即刻开始创作'
]

const model = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: ''
})

const validateConfirmPassword = (_rule: any, value: string) => {
  if (!value) {
    return new Error('请再次输入密码')
  }
  if (value !== model.password) {
    return new Error('两次输入的密码不一致')
  }
  return true
}

const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  email: { required: true, message: '请输入邮箱地址', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' },
  confirm_password: { required: true, validator: validateConfirmPassword, trigger: ['blur', 'input'] }
}

const handleRegister = () => {
  ;(formRef.value as any)?.validate(async (errors: any) => {
    if (!errors) {
      loading.value = true
      try {
        await authApi.register({
          username: model.username,
          email: model.email,
          password: model.password
        })
        message.success('注册成功，请登录')
        router.push({ name: 'Login' })
      } catch (error: any) {
        let errorMsg = '注册失败'
        if (error.response?.data?.detail) {
          const detail = error.response.data.detail
          if (Array.isArray(detail)) {
            errorMsg = detail.map((err: any) => err.msg || JSON.stringify(err)).join('; ')
          } else {
            errorMsg = detail
          }
        } else {
          errorMsg = error.message || '注册失败'
        }
        message.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 复用登录页样式 */
.register-container {
  display: flex;
  min-height: 100vh;
  background: var(--bg-base);
}

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

.register-button {
  margin-top: var(--spacing-md);
  background: var(--primary-gradient);
  border: none;
  font-weight: 600;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.register-button:active {
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
