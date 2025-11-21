<template>
  <div class="alarm-dialog" tabindex="0" @keydown.esc="$emit('close')">
    <div class="header-bar">
      <div class="title-center">报警监测</div>
      <div class="actions">
        <button class="clear-btn" @click="alarmStore.clearAlarms()">
          清空
        </button>
        <button class="close-btn" @click="$emit('close')">关闭</button>
      </div>
    </div>

    <div class="alarm-table">
      <div class="alarm-row header">
        <div class="cell time">时间</div>
        <div class="cell content">报警内容</div>
        <div class="cell value">数值</div>
      </div>
      <div
        class="alarm-row"
        v-for="(item, index) in alarmStore.alarmList"
        :key="index"
      >
        <div class="cell time">{{ item.time }}</div>
        <div class="cell content">{{ item.content }}</div>
        <div class="cell value">{{ item.value }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAlarmStore } from "@/stores/useAlarmStore";
const alarmStore = useAlarmStore();

// alarmStore.alarmList  // => 报警记录
// alarmStore.clearAlarms() // => 手动清空
</script>

<style scoped>
.alarm-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  width: 600px;
  height: 400px;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.92);
  border-radius: 16px;
  padding: 20px;
  z-index: 99999;
  pointer-events: auto;
  box-shadow: 0 0 40px rgba(0, 128, 255, 0.3);
  display: flex;
  flex-direction: column;
  outline: none;
}

.header-bar {
  position: relative;
  height: 40px;
  margin-bottom: 16px;
}

.title-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 24px;
  font-weight: bold;
  color: white;
  line-height: 40px;
  background: rgba(0, 0, 0, 0.4);
  padding: 4px 16px;
  border-radius: 10px;
  box-shadow: 0 0 8px rgba(0, 255, 255, 0.4);
}

.actions {
  position: absolute;
  right: 0;
  top: 0;
  display: flex;
  gap: 10px;
  align-items: center;
  height: 40px;
}

.close-btn,
.clear-btn {
  background: rgba(0, 128, 255, 0.6);
  border: none;
  color: white;
  padding: 6px 12px;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
}

.alarm-table {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  font-size: 14px;
  color: white;
}

.alarm-row {
  display: flex;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.alarm-row.header {
  font-weight: bold;
  color: #00cfff;
}

.cell {
  padding: 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.time {
  width: 100px;
}

.content {
  flex: 1;
}

.value {
  width: 60px;
  text-align: right;
}
</style>
