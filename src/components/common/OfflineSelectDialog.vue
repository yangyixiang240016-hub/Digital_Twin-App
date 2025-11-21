<template>
  <div class="offline-select-mask" @click.self="$emit('close')">
    <div class="offline-select-dialog" @click.stop>
      <div class="dialog-content">
        <!-- 头部 -->
        <div class="header">
          <div class="title-center">选择离线模拟/优化方式</div>
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
const simType = ref<"dynamic" | "steady">("dynamic");
const mode = ref<"aeration" | "do">("aeration");

const emit = defineEmits<{
  (e: "close"): void;
  (
    e: "confirm",
    p: {
      process: "AAO" | "MBR";
      func: "simulate" | "optimize";
      simType: "dynamic" | "steady";
      mode: "aeration" | "do";
    }
  ): void;
}>();

function confirm() {
  if (!process.value) return;
  emit("confirm", {
    process: process.value,
    func: func.value,
    simType: simType.value,
    mode: mode.value,
  });
}

function selectAction(p: "AAO" | "MBR", f: "simulate" | "optimize") {
  process.value = p;
  func.value = f;
}
</script>

<style scoped>
.offline-select-mask {
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

.offline-select-dialog {
  width: 90%;
  max-width: 1000px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  pointer-events: auto;
  position: relative;
}

.dialog-content {
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header {
  text-align: center;
}

.title-center {
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
}

.middle {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.subtitle {
  color: #ffffff;
  font-size: 14px;
  text-align: center;
  opacity: 0.8;
}

.cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.proc-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s;
}

.proc-card.active {
  border-color: #4f46e5;
  background: rgba(79, 70, 229, 0.1);
}

.proc-name {
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 15px;
  text-align: center;
}

.btn-row {
  display: flex;
  gap: 10px;
}

.btn-row button {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-row button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-row button.on {
  background: #4f46e5;
  border-color: #4f46e5;
}

.footer {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.footer button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.footer button.primary {
  background: #4f46e5;
  color: #ffffff;
}

.footer button.primary:hover:not(:disabled) {
  background: #4338ca;
}

.footer button.primary:disabled {
  background: rgba(255, 255, 255, 0.2);
  cursor: not-allowed;
}

.footer button:not(.primary) {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.footer button:not(.primary):hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
