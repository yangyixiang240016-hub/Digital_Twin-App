<script setup>
import zhCN from "ant-design-vue/es/locale/zh_CN";
import dayjs from "dayjs";
import "dayjs/locale/zh-cn";
dayjs.locale("en");
</script>

<template>
  <!-- ant-design组件 -->
  <a-config-provider
    :locale="zhCN"
    :theme="{
      token: {
        // 主题风格颜色
        colorPrimary: '#00688B',
        // 背景颜色
        colorBgBase: '#04405D',
        // 文本颜色
        colorTextBase: '#fafafa',
        // 边框颜色
        colorBorder: '#00688B',
      },
    }"
  >
    <router-view class="element"></router-view>
  </a-config-provider>
</template>

<style scoped>
/* 默认情况下，不进行缩放 */
/* .element {
  transform: scale(1);
} */

/* @media (max-width: 1200px) {
  .element {
    transform: scale(0.8);
  }
}

@media (min-width: 2000px) {
  .element {
    transform: scale(1.2);
  }
} */
</style>
