<template>
  <!-- 巡检进度条 -->
  <div id="progressBar" ref="progressBar">
    <div id="progress" ref="progress"></div>
    <div class="slider" ref="slider">
      <img
        src="../../../assets/shouye/schedule.png"
        alt=""
        style="width: 100%; height: 100%; vertical-align: baseline"
      />
    </div>
    <div class="inspectText">巡检进度</div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from "vue";
// 首页传值
const props = defineProps(["schedule", "inspectState"]);
// 传递事件
const emit = defineEmits(["progressBarChange"]);
// 滑块元素
const slider = ref();
// 进度条元素
const progressBar = ref();
// 进度条进度元素
const progress = ref();

// 监听当前巡检进度
watch(props, (e) => {
  // 当前进度
  const schedule = e.schedule;
  progress.value.style.width = schedule + "%";
  // 进度条宽度
  const width = progressBar.value.clientWidth - slider.value.clientWidth;
  slider.value.style.left = (width * (schedule * 0.01)).toFixed(2) + "px";
});

onMounted(() => {
  // 监听滑块元素的鼠标按下事件
  slider.value.addEventListener("mousedown", (e) => {
    // 通过 emit 事件通知父组件修改 inspectState
    emit("progressBarChange", { action: "pause" });
    document.addEventListener("mousemove", computeSlideValue);
  });
  // 监听鼠标松开事件
  document.addEventListener("mouseup", function () {
    // 通过 emit 事件通知父组件修改 inspectState
    emit("progressBarChange", { action: "resume" });
    document.removeEventListener("mousemove", computeSlideValue);
  });
});

// 计算鼠标滑动值
function computeSlideValue(e) {
  // 进度条的相对页面的位置
  const progressBarRect = progressBar.value.getBoundingClientRect();
  // 鼠标相对于进度条的水平位置
  let mouseX = e.clientX - progressBarRect.left;
  // 进度条宽度
  const width = progressBar.value.clientWidth - slider.value.clientWidth;
  // 计算滑块的新位置，需要限制在0到width之间
  let left = Math.min(Math.max(0, mouseX), width);
  // 设置滑块位置
  slider.value.style.left = left + "px";
  // 进度百分比
  const schedule = ((left / width) * 100).toFixed(2) - "";
  progress.value.style.width = schedule + "%";
  emit("progressBarChange", schedule);
}
</script>
<style lang="less" scoped>
#progressBar {
  position: absolute;
  display: flex;
  align-items: center;
  bottom: 8%;
  right: 5%;
  width: 15vw;
  height: 0.5vw;
  background: #ccc;
  border-radius: 1vw;
  z-index: 999;
  #progress {
    position: absolute;
    width: 0%;
    height: 100%;
    background: rgb(3, 98, 175);
    border-radius: 1vw;
  }
  .slider {
    position: absolute;
    cursor: pointer;
    display: flex;
    width: 1.3vw;
    height: 1.3vw;
    background: #dae4f5;
    border: 2px solid rgb(71, 135, 219);
  }

  .inspectText {
    font-size: 0.9vw;
    position: relative;
    left: -35%;
    font-weight: 500;
    letter-spacing: 0.1vw;
    color: #fafafa;
    background: rgb(26, 109, 218);
    padding: 0.15vw 0.45vw;
    border-radius: 30px;
  }
}
</style>
