<template>
  <div class="online-select-mask" @click.self="$emit('close')">
    <div class="online-select-dialog" @click.stop>
      <div class="dialog-content">
        <!-- 头部 -->
        <div class="header">
          <div class="title-center">选择在线模拟/优化方式</div>
        </div>

        <!-- 中部：两张工艺卡 + 选项 -->
        <div class="middle">
          <div class="subtitle">
            请先选择需要模拟/优化的工艺及方式，然后再根据步骤进行相关操作；
          </div>
          <div class="cards">
            <div
              class="proc-card"
              :class="{ active: process === 'AAO' }"
              @click="process = 'AAO'"
            >
              <div class="proc-name">AAO 工艺</div>
              <div class="btn-row">
                <!-- AAO 卡片 -->
                <button
                  :class="{ on: process === 'AAO' && func === 'simulate' }"
                  @click.stop="selectAction('AAO', 'simulate')"
                >
                  模拟
                </button>
                <button
                  :class="{ on: process === 'AAO' && func === 'optimize' }"
                  @click.stop="selectAction('AAO', 'optimize')"
                >
                  优化
                </button>
              </div>
            </div>

            <div
              class="proc-card"
              :class="{ active: process === 'MBR' }"
              @click="process = 'MBR'"
            >
              <div class="proc-name">MBR 工艺</div>
              <div class="btn-row">
                <!-- MBR 卡片 -->
                <button
                  :class="{ on: process === 'MBR' && func === 'simulate' }"
                  @click.stop="selectAction('MBR', 'simulate')"
                >
                  模拟
                </button>
                <button
                  :class="{ on: process === 'MBR' && func === 'optimize' }"
                  @click.stop="selectAction('MBR', 'optimize')"
                >
                  优化
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部：固定在底 -->
        <div class="footer">
          <button class="primary" :disabled="!process" @click="confirm">
            确 定
          </button>
          <button @click="$emit('close')">取 消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
const process = ref<"AAO" | "MBR" | null>("AAO");
const func = ref<"simulate" | "optimize">("simulate");

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "confirm",
    p: {
      processType: "AAO" | "MBR";
      mode: "simulate" | "optimize";
    }
  ): void;
}>();

function confirm() {
  if (!process.value) return;
  emit("confirm", {
    processType: process.value,
    mode: func.value,
  });
}

function selectAction(p: "AAO" | "MBR", f: "simulate" | "optimize") {
  process.value = p;
  func.value = f;
}
</script>

<style scoped>
.online-select-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  pointer-events: auto;
}

.online-select-dialog {
  width: 1000px;
  height: 600px;
  max-width: 95vw;
  max-height: 95vh;
  background: linear-gradient(180deg, #0a2d5e, #031836);
  border: 1px solid rgba(0, 160, 255, 0.25);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
  border-radius: 14px;
  color: #e6f3ff;
  font-size: 16px;
  position: relative;
  overflow: hidden;
  pointer-events: auto;
}

.dialog-content {
  padding: 40px 60px;
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 30px;
}

.header {
  text-align: center;
}

.title-center {
  font-size: 28px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 10px;
}

.middle {
  display: flex;
  flex-direction: column;
  gap: 30px;
  flex: 1;
  justify-content: center;
}

.subtitle {
  color: #e6f3ff;
  font-size: 16px;
  text-align: center;
  opacity: 0.8;
}

.cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  height: 200px;
  width: 100%;
} 

.proc-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 30px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.proc-card.active {
  border-color: #00c9ff;
  background: rgba(0, 201, 255, 0.1);
  box-shadow: 0 0 20px rgba(0, 201, 255, 0.3);
}

.proc-name {
  font-size: 20px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 20px;
  text-align: center;
}

.btn-row {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn-row button {
  padding: 12px 24px;
  border: 2px solid rgba(0, 201, 255, 0.3);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #e6f3ff;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 16px;
  font-weight: 500;
  min-width: 80px;
}

.btn-row button:hover {
  background: rgba(0, 201, 255, 0.1);
  border-color: rgba(0, 201, 255, 0.5);
}

.btn-row button.on {
  background: #00c9ff;
  border-color: #00c9ff;
  color: #ffffff;
  box-shadow: 0 0 15px rgba(0, 201, 255, 0.4);
}

.footer {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.footer button {
  padding: 14px 32px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 100px;
}

.footer button.primary {
  background: #4f46e5;
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
}

.footer button.primary:hover:not(:disabled) {
  background: #4338ca;
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

.footer button.primary:disabled {
  background: rgba(255, 255, 255, 0.2);
  cursor: not-allowed;
}

.footer button:not(.primary) {
  background: rgba(255, 255, 255, 0.1);
  color: #e6f3ff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.footer button:not(.primary):hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
