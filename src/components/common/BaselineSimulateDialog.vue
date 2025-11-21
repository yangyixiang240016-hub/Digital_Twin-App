<template>
  <div v-if="visible" class="baseline-simulate-mask" @click.self="$emit('close')">
    <div class="baseline-simulate-dialog" @click.stop>
      <!-- 标题栏 -->
      <div class="dialog-header">
        <div class="dialog-title">{{ processType === 'AAO' ? 'AAO' : 'MBR' }}基准模拟</div>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <!-- 内容区域 -->
      <div class="dialog-content">
        <div class="action-buttons">
          <button 
            class="action-btn start-btn" 
            @click="handleStart"
            :disabled="isRunning"
          >
            <div class="btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </div>
            <div class="btn-text">
              <div class="btn-title">启动基准模拟</div>
              <div class="btn-desc">开始运行基准模拟任务</div>
            </div>
          </button>

          <button 
            class="action-btn stop-btn" 
            @click="handleStop"
            :disabled="!isRunning"
          >
            <div class="btn-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white">
                <path d="M6 6h12v12H6z"/>
              </svg>
            </div>
            <div class="btn-text">
              <div class="btn-title">停止基准模拟</div>
              <div class="btn-desc">停止当前运行的基准模拟任务</div>
            </div>
          </button>
        </div>

        <!-- 状态显示 -->
        <div class="status-section">
          <div class="status-item">
            <span class="status-label">当前状态：</span>
            <span class="status-value" :class="{ running: isRunning }">
              {{ isRunning ? '运行中' : '已停止' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="dialog-actions">
        <button class="btn btn-secondary" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { startAAO, stopAAO, startMBR, stopMBR } from "@/api/simulate";

const props = defineProps<{
  visible: boolean;
  processType: "AAO" | "MBR";
  currentStatus: boolean; // 当前运行状态
}>();

const emit = defineEmits<{
  close: [];
  statusChanged: [status: boolean];
}>();

const isRunning = ref(props.currentStatus);
const isBusy = ref(false);

// 监听props变化更新本地状态
watch(
  () => props.currentStatus,
  (newVal) => {
    isRunning.value = newVal;
  }
);

const handleStart = async () => {
  if (isBusy.value || isRunning.value) return;
  
  isBusy.value = true;
  try {
    if (props.processType === "AAO") {
      await startAAO();
    } else {
      await startMBR();
    }
    isRunning.value = true;
    emit("statusChanged", true);
  } catch (err: any) {
    const msg = err?.__msg || err?.message || "";
    // 语义纠偏：后端提示"已有任务/已在运行"
    if (/已有.*基准任务/.test(msg) || /already.*running/i.test(msg)) {
      isRunning.value = true;
      emit("statusChanged", true);
    } else {
      alert("启动失败：" + msg);
    }
  } finally {
    isBusy.value = false;
  }
};

const handleStop = async () => {
  if (isBusy.value || !isRunning.value) return;
  
  isBusy.value = true;
  try {
    if (props.processType === "AAO") {
      await stopAAO();
    } else {
      await stopMBR();
    }
    isRunning.value = false;
    emit("statusChanged", false);
  } catch (err: any) {
    const msg = err?.__msg || err?.message || "";
    // 语义纠偏：后端提示"无任务在运行"
    if (/无.*在运行/.test(msg) || /not.*running/i.test(msg)) {
      isRunning.value = false;
      emit("statusChanged", false);
    } else {
      alert("停止失败：" + msg);
    }
  } finally {
    isBusy.value = false;
  }
};
</script>

<style lang="less" scoped>
.baseline-simulate-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  pointer-events: auto;
}

.baseline-simulate-dialog {
  width: 500px;
  background: linear-gradient(135deg, rgba(0, 43, 84, 0.98), rgba(0, 20, 40, 0.98));
  border: 1px solid rgba(0, 201, 255, 0.3);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  pointer-events: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid rgba(0, 201, 255, 0.2);
}

.dialog-title {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
}

.close-btn {
  background: rgba(0, 128, 255, 0.6);
  border: none;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.close-btn:hover {
  background: rgba(0, 128, 255, 0.8);
}

.dialog-content {
  flex: 1;
  padding: 40px 30px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 25px;
  border: 1px solid rgba(0, 201, 255, 0.3);
  border-radius: 10px;
  background: rgba(0, 43, 84, 0.6);
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;

  &:hover:not(:disabled) {
    background: rgba(0, 201, 255, 0.2);
    border-color: rgba(0, 201, 255, 0.6);
    transform: translateX(5px);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.start-btn {
  &:hover:not(:disabled) {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.1);
  }
}

.stop-btn {
  &:hover:not(:disabled) {
    border-color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }
}

.btn-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 201, 255, 0.2);
  border-radius: 8px;
  flex-shrink: 0;

  svg {
    width: 24px;
    height: 24px;
  }
}

.start-btn .btn-icon {
  background: rgba(16, 185, 129, 0.2);
}

.stop-btn .btn-icon {
  background: rgba(239, 68, 68, 0.2);
}

.btn-text {
  flex: 1;
}

.btn-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}

.btn-desc {
  font-size: 14px;
  opacity: 0.7;
}

.status-section {
  padding: 20px;
  background: rgba(0, 43, 84, 0.4);
  border-radius: 8px;
  border: 1px solid rgba(0, 201, 255, 0.2);
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-label {
  color: #fff;
  font-size: 16px;
}

.status-value {
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  font-weight: bold;

  &.running {
    color: #10b981;
  }
}

.dialog-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px 30px;
  border-top: 1px solid rgba(0, 201, 255, 0.2);
}

.btn {
  padding: 12px 40px;
  border: none;
  border-radius: 6px;
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 120px;
}

.btn-primary {
  background: linear-gradient(135deg, #00c9ff, #007bff);
  color: white;
  border: 1px solid #00c9ff;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #00b8e6, #0066cc);
  box-shadow: 0 5px 15px rgba(0, 201, 255, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>


