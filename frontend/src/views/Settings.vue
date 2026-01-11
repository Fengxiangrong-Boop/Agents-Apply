<template>
  <div class="settings-page">
    <n-card title="系统设置">
      <n-tabs type="line" animated>
        <!-- Tab 1: 微信配置 -->
        <n-tab-pane name="wechat" tab="微信公众号配置">
          <wechat-config-form />
        </n-tab-pane>
        
        <!-- Tab 2: API Key 配置 -->
        <n-tab-pane name="apikey" tab="API Key 配置">
          <api-key-form />
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { NCard, NTabs, NTabPane } from 'naive-ui'
import WechatConfigForm from '@/components/WechatConfigForm.vue'
import ApiKeyForm from '@/components/ApiKeyForm.vue'
</script>

<style scoped>
</style>
