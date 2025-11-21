<template>
  <transition name="fade">
    <div v-if="visible" class="overlay">
      <div class="box">
        <!-- 居中标题 -->
        <div class="header-bar">
          <div class="title-center">{{ title }}</div>
        </div>

        <!-- 进度条 -->
        <div class="bar">
          <div class="bar-inner" :style="{ width: progress + '%' }"></div>
        </div>

        <!-- 描述 -->
        <div class="desc">{{ desc }}</div>
      </div>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: "正在处理…" },
  desc: { type: String, default: "" },
  progress: { type: Number, default: 0 },
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

/* 放大面板 */
.box {
  width: 600px; /* 原来420px → 放大 */
  padding: 30px 36px;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.92);
  color: #eaf6ff;
  box-shadow: 0 0 40px rgba(0, 255, 255, 0.2);
}

/* 标题区 */
.header-bar {
  position: relative;
  height: 50px;
  margin-bottom: 24px;
}

.title-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 26px;
  font-weight: bold;
  color: white;
  line-height: 50px;
  background: rgba(0, 0, 0, 0.4);
  padding: 4px 20px;
  border-radius: 10px;
  box-shadow: 0 0 8px rgba(0, 255, 255, 0.4);
  white-space: nowrap; /* ✅ 单行显示 */
}

/* 进度条 */
.bar {
  height: 14px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  overflow: hidden;
}
.bar-inner {
  height: 100%;
  background: linear-gradient(90deg, #62b2ff, #77f3ff);
  transition: width 0.25s ease;
}

/* 描述 */
.desc {
  margin-top: 16px;
  font-size: 15px;
  opacity: 0.9;
  text-align: center;
}
</style>
