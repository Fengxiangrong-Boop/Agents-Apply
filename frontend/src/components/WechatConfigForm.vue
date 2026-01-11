<template>
  <div class="wechat-config-form">
    <n-spin :show="loading">
      <div v-if="!config && !isEditing" class="empty-state">
        <n-empty description="暂无微信公众号配置">
          <template #extra>
            <n-button type="primary" @click="startCreate">立即配置</n-button>
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
          <n-form-item label="AppID" path="app_id">
            <n-input v-model:value="model.app_id" placeholder="请输入微信公众号 AppID" :disabled="!isEditing" />
          </n-form-item>
          <n-form-item label="AppSecret" path="app_secret">
            <n-input
              v-model:value="model.app_secret"
              type="password"
              show-password-on="mousedown"
              placeholder="请输入微信公众号 AppSecret"
              :disabled="!isEditing"
            />
          </n-form-item>
          
          <div v-if="config && !isEditing" class="status-info">
             <n-alert title="状态信息" type="success" :bordered="false">
               Token 有效期至: {{ config.token_expires_at ? new Date(config.token_expires_at).toLocaleString() : '未知' }}
             </n-alert>
          </div>

          <div class="actions">
            <template v-if="!isEditing">
              <n-button type="primary" @click="startEdit">修改配置</n-button>
              <n-popconfirm @positive-click="handleDelete">
                <template #trigger>
                  <n-button type="error" ghost style="margin-left: 12px">删除配置</n-button>
                </template>
                确定要删除微信配置吗？这将导致无法同步文章。
              </n-popconfirm>
            </template>
            <template v-else>
              <n-button type="primary" @click="handleSave" :loading="submitting">保存</n-button>
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
import { wechatApi, type WechatConfig } from '@/api/wechat'

const message = useMessage()
const formRef = ref(null)
const loading = ref(false)
const submitting = ref(false)
const isEditing = ref(false)
const config = ref<WechatConfig | null>(null)

const model = reactive({
  app_id: '',
  app_secret: ''
})

const rules = {
  app_id: { required: true, message: '请输入 AppID', trigger: 'blur' },
  app_secret: { required: true, message: '请输入 AppSecret', trigger: 'blur' }
}

const fetchConfig = async () => {
  loading.value = true
  try {
    const data = await wechatApi.getConfig()
    config.value = data
    if (data) {
      model.app_id = data.app_id
      // AppSecret后端通常不返回明文或者已脱敏，这里如果需要修改则需重新输入
      model.app_secret = data.app_secret // 注意：这里假设后端返回了伪装值或空，修改时需重置
    }
  } catch (error: any) {
    // 如果是404或400错误，说明用户还没有配置，不显示错误提示
    if (error.response?.status === 404 || error.response?.status === 400) {
      config.value = null
    } else {
      // 其他错误才显示提示
      message.error('获取配置失败：' + (error.response?.data?.detail || error.message || '网络错误'))
    }
  } finally {
    loading.value = false
  }
}

const startCreate = () => {
  isEditing.value = true
  model.app_id = ''
  model.app_secret = ''
}

const startEdit = () => {
  isEditing.value = true
  // 如果是编辑，保留 AppID，AppSecret 清空让用户重新输入（为了安全）
  // 或者用户只想改 AppID? 通常是全改。
  model.app_secret = '' 
}

const cancelEdit = () => {
  isEditing.value = false
  if (config.value) {
    model.app_id = config.value.app_id
    model.app_secret = config.value.app_secret
  } else {
    // 之前没有配置，取消创建
    model.app_id = ''
    model.app_secret = ''
  }
}

const handleSave = () => {
  ;(formRef.value as any)?.validate(async (errors: any) => {
    if (!errors) {
      submitting.value = true
      try {
        if (config.value) {
           await wechatApi.updateConfig(model)
        } else {
           await wechatApi.createConfig(model)
        }
        message.success('保存成功')
        isEditing.value = false
        await fetchConfig()
      } catch (error: any) {
        message.error('保存失败：' + (error.response?.data?.detail || '未知错误'))
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = async () => {
  try {
    await wechatApi.deleteConfig()
    message.success('删除成功')
    config.value = null
    model.app_id = ''
    model.app_secret = ''
  } catch (error) {
     message.error('删除失败')
  }
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.wechat-config-form {
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
