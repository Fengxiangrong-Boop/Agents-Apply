<template>
  <n-form
    ref="formRef"
    :model="formModel"
    :rules="rules"
    label-placement="left"
    label-width="100"
    require-mark-placement="right-hanging"
    size="medium"
  >
    <n-form-item label="样式名称" path="name">
      <n-input v-model:value="formModel.name" placeholder="例如：商业干货、清新文艺" />
    </n-form-item>
    <n-form-item label="描述" path="description">
      <n-input
        v-model:value="formModel.description"
        type="textarea"
        placeholder="简要描述样式的适用场景"
        :autosize="{ minRows: 2, maxRows: 4 }"
      />
    </n-form-item>
    <n-form-item label="提示词指令" path="prompt_instruction">
      <n-input
        v-model:value="formModel.prompt_instruction"
        type="textarea"
        placeholder="指导 AI 写作的特定指令。例如：使用专业的商业口吻，多用短句..."
        :autosize="{ minRows: 4, maxRows: 10 }"
      />
    </n-form-item>
    <n-form-item label="CSS 内容" path="css_content">
      <n-input
        v-model:value="formModel.css_content"
        type="textarea"
        placeholder="样式表的 CSS 内容，用于控制预览时的排版。"
        class="code-input"
        :autosize="{ minRows: 6, maxRows: 15 }"
      />
    </n-form-item>
    <n-space justify="end">
      <n-button @click="$emit('cancel')">取消</n-button>
      <n-button type="primary" :loading="loading" @click="handleSubmit">保存</n-button>
    </n-space>
  </n-form>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { NForm, NFormItem, NInput, NButton, NSpace, type FormInst } from 'naive-ui'
import type { Style, StyleCreate } from '@/api/style'

const props = defineProps<{
  initialData?: Style | null
  loading?: boolean
}>()

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref<FormInst | null>(null)
const formModel = ref<StyleCreate>({
  name: '',
  description: '',
  prompt_instruction: '',
  css_content: ''
})

const rules = {
  name: { required: true, message: '请输入样式名称', trigger: 'blur' },
  description: { required: true, message: '请输入描述', trigger: 'blur' },
  prompt_instruction: { required: true, message: '请输入提示词指令', trigger: 'blur' },
  css_content: { required: true, message: '请输入 CSS 内容', trigger: 'blur' }
}

watch(
  () => props.initialData,
  (newVal) => {
    if (newVal) {
      formModel.value = {
        name: newVal.name,
        description: newVal.description,
        prompt_instruction: newVal.prompt_instruction,
        css_content: newVal.css_content
      }
    } else {
      formModel.value = {
        name: '',
        description: '',
        prompt_instruction: '',
        css_content: ''
      }
    }
  },
  { immediate: true }
)

const handleSubmit = (e: MouseEvent) => {
  e.preventDefault()
  formRef.value?.validate((errors) => {
    if (!errors) {
      emit('submit', { ...formModel.value })
    }
  })
}
</script>

<style scoped>
.code-input :deep(textarea) {
  font-family: 'Fira Code', 'Courier New', Courier, monospace;
}
</style>
