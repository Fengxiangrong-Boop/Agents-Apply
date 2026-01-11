<template>
  <div class="api-key-form">
    <n-spin :show="loading">
       <n-alert title="说明" type="info" :bordered="false" style="margin-bottom: 20px">
         配置硅基流动的 API Key 用于调用 LLM 生成文章。Key 将被安全加密存储。
       </n-alert>

      <div v-if="!config && !isEditing" class="empty-state">
        <n-empty description="暂无 API Key 配置">
          <template #extra>
            <n-button type="primary" @click="startCreate">配置 API Key</n-button>
          </template>
        </n-empty>
      </div>

      <div v-else>
        <n-form
          ref="formRef"
          :model="model"
          :rules="rules"
          label-placement="left"
          label-width="120"
          require-mark-placement="right-hanging"
        >
          <n-form-item label="服务提供商" path="provider">
             <n-input v-model:value="model.provider" disabled />
          </n-form-item>
          <n-form-item label="API Key" path="api_key">
            <n-input
              v-model:value="model.api_key"
              type="password"
              show-password-on="mousedown"
              placeholder="sk-..."
              :disabled="!isEditing"
            />
          </n-form-item>
          
          <div v-if="config && !isEditing" class="status-info">
             <n-alert :title="config.is_valid ? '验证通过' : '验证失败'" :type="config.is_valid ? 'success' : 'error'" :bordered="false">
               当前 API Key 状态: {{ config.is_valid ? '有效' : '无效 (请检查余额或 Key 是否正确)' }}
             </n-alert>
          </div>

          <div class="actions">
            <template v-if="!isEditing">
              <n-button type="primary" @click="startEdit">修改 Key</n-button>
              <n-popconfirm @positive-click="handleDelete">
                <template #trigger>
                  <n-button type="error" ghost style="margin-left: 12px">删除配置</n-button>
                </template>
                确定要删除吗？删除后将无法生成文章。
              </n-popconfirm>
            </template>
            <template v-else>
              <n-button type="primary" @click="handleSave" :loading="submitting">验证并保存</n-button>
              <n-button @click="cancelEdit" style="margin-left: 12px" :disabled="submitting">取消</n-button>
            </template>
          </div>
        </n-form>
      </div>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage, NButton, NForm, NFormItem, NInput, NEmpty, NSpin, NPopconfirm, NAlert } from 'naive-ui'
import { apiKeyApi, type ApiKeyConfig } from '@/api/apikey'

const message = useMessage()
const formRef = ref(null)
const loading = ref(false)
const submitting = ref(false)
const isEditing = ref(false)
const config = ref<ApiKeyConfig | null>(null)

const model = reactive({
  provider: 'siliconflow',
  api_key: ''
})

const rules = {
  api_key: { required: true, message: '请输入 API Key', trigger: 'blur' }
}

const fetchConfig = async () => {
  loading.value = true
  try {
    const data = await apiKeyApi.getApiKey('siliconflow')
    config.value = data
    if (data) {
      model.api_key = data.api_key // 同样注意安全性，这里假设后端返回脱敏数据
    }
  } catch (error: any) {
    // 如果是404或400错误，说明用户还没有配置，不显示错误提示
    if (error.response?.status === 404 || error.response?.status === 400) {
      config.value = null
    } else {
      // 其他错误才显示提示
      message.error('获取 API Key 配置失败：' + (error.response?.data?.detail || error.message || '网络错误'))
    }
  } finally {
    loading.value = false
  }
}

const startCreate = () => {
  isEditing.value = true
  model.api_key = ''
}

const startEdit = () => {
  isEditing.value = true
  model.api_key = ''
}

const cancelEdit = () => {
  isEditing.value = false
  if (config.value) {
    model.api_key = config.value.api_key
  } else {
    model.api_key = ''
  }
}

const handleSave = () => {
  ;(formRef.value as any)?.validate(async (errors: any) => {
    if (!errors) {
      submitting.value = true
      try {
        // 创建和更新都用同一个接口逻辑在组件层面，但后端区分
        // 这里后端其实 update 也是创建/覆盖逻辑
        if (config.value) {
           await apiKeyApi.updateApiKey(model)
        } else {
           await apiKeyApi.createApiKey(model)
        }
        message.success('保存成功')
        isEditing.value = false
        await fetchConfig()
      } catch (error: any) {
        message.error('保存失败：' + (error.response?.data?.detail || '验证未通过，请检查 Key'))
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = async () => {
  try {
    await apiKeyApi.deleteApiKey('siliconflow')
    message.success('删除成功')
    config.value = null
    model.api_key = ''
  } catch (error) {
     message.error('删除失败')
  }
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.api-key-form {
  max-width: 600px;
  padding: 20px 0;
}
.empty-state {
  padding: 40px;
  display: flex;
  justify-content: center;
}
.status-info {
  margin-bottom: 24px;
}
</style>
