<template>
  <div class="trend-inline">
    <div class="trend-header">
      <div class="tab-group">
        <button
          v-for="p in paramList"
          :key="p.key"
          class="tab"
          :class="{ active: p.key === param }"
          @click="onChangeParam(p.key)"
          :title="p.label"
        >
          {{ p.label }}
        </button>
      </div>
    </div>

    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<script setup>
import {
  ref,
  reactive,
  onMounted,
  onBeforeUnmount,
  watch,
  computed,
  nextTick,
} from "vue";
import * as echarts from "echarts";
import axios from "axios";

/** props */
const props = defineProps({
  /** 'inflow' | 'outflow' */
  variant: { type: String, default: "inflow" },
  height: { type: Number, default: 140 },
});

const chartRef = ref(null);
let chart = null;

const unit = ref("");
const param = ref("total_flow");

const paramsIn = [
  { key: "total_flow", label: "流量" },
  { key: "cod", label: "COD" },
  { key: "nh3n", label: "NH3-N" },
  { key: "tn", label: "TN" },
  { key: "tp", label: "TP" },
  // ✅ 进水不含 SS
];

const paramsOut = [
  { key: "total_flow", label: "流量" },
  { key: "cod", label: "COD" },
  { key: "nh3n", label: "NH3-N" },
  { key: "tn", label: "TN" },
  { key: "tp", label: "TP" },
  { key: "ss", label: "SS" }, // ✅ 出水含 SS，6 个凑满一排
];

const paramList = computed(() =>
  props.variant === "inflow" ? paramsIn : paramsOut
);

/** 保证切换 inflow 时若当前是 ss 则回退到 flow */
watch(
  () => props.variant,
  () => {
    if (props.variant === "inflow" && param.value === "ss") {
      param.value = "total_flow";
    }
  },
  { immediate: true }
);

const state = reactive({
  times: [],
  seriesA: [],
  seriesB: [],
});

function onChangeParam(p) {
  if (p !== param.value) param.value = p;
}

async function fetchTrend() {
  const { data } = await axios.get(`/api/trend?param=${param.value}`);
  state.times = data?.times || [];
  unit.value = data?.unit || "";

  if (props.variant === "inflow") {
    state.seriesA = data?.realtime_in || [];
    state.seriesB = data?.predict_in || [];
  } else {
    state.seriesA = data?.realtime_out || [];
    state.seriesB = data?.predict_out || [];
  }

  render();
}

function render() {
  if (!chart) chart = echarts.init(chartRef.value);

  const nameA = props.variant === "inflow" ? "实时进水" : "实时出水";
  const nameB = props.variant === "inflow" ? "预测进水" : "预测出水";

  chart.setOption({
    tooltip: { trigger: "axis" },
    legend: {
      data: [nameA, nameB],
      top: 6,
      left: "center", // ✅ 居中图例
      itemWidth: 14,
      textStyle: { color: "#cfe8ff", fontSize: 12 },
    },
    title: [
      {
        text: unit.value ? `单位：${unit.value}` : "",
        right: 10, // 单位靠右
        top: 6,
        textStyle: { color: "#9cc3ff", fontSize: 12, fontWeight: "normal" },
      },
    ],
    grid: {
      left: 60,
      right: 10, // ✅ 给右侧刻度留足空间
      top: 32,
      bottom: 24,
    },
    xAxis: {
      type: "category",
      data: state.times,
      axisLabel: { color: "#9cc3ff" },
      axisLine: { lineStyle: { color: "rgba(255,255,255,.25)" } },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#9cc3ff" },
      splitLine: { lineStyle: { color: "rgba(255,255,255,.12)" } },
    },
    series: [
      {
        name: nameA,
        type: "line",
        showSymbol: false,
        data: state.seriesA,
        lineStyle: { width: 2 },
      },
      {
        name: nameB,
        type: "line",
        showSymbol: false,
        data: state.seriesB,
        lineStyle: { type: "dashed", width: 2 },
      },
    ],
    animation: false,
  });
  chart.resize();
}

function onResize() {
  chart && chart.resize();
}

onMounted(async () => {
  chartRef.value.style.height = props.height + "px";
  await nextTick();
  fetchTrend();
  window.addEventListener("resize", onResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
  if (chart) {
    chart.dispose();
    chart = null;
  }
});

watch(param, fetchTrend);
</script>

<style scoped>
.trend-inline {
  margin-top: 12px;
  background: rgba(0, 30, 60, 0.55);
  border: 1px solid rgba(0, 140, 255, 0.25);
  border-radius: 10px;
  padding: 10px 12px 6px;
}

/* 顶部参数按钮区域 */
.trend-header {
  margin-bottom: 6px;
}

/* ✅ 让出水 6 个按钮一排排下，同时自适应收缩 */
.tab-group {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap; /* 不换行 */
  justify-content: space-between;
}

.tab {
  flex: 1 1 0; /* 可收缩可拉伸，保证一排排下 */
  min-width: 0; /* 允许变窄 */
  height: 26px;
  padding: 0 6px; /* 收窄左右内边距以容纳 6 个 */
  font-size: 12px;
  line-height: 26px;
  white-space: nowrap;
  color: #cfe8ff;
  background: rgba(0, 110, 200, 0.28);
  border: 1px solid rgba(0, 180, 255, 0.35);
  border-radius: 6px;
  cursor: pointer;
  text-align: center;
}
.tab.active {
  color: #fff;
  background: linear-gradient(
    135deg,
    rgba(0, 198, 255, 0.5),
    rgba(0, 110, 255, 0.55)
  );
  border-color: rgba(0, 198, 255, 0.8);
  box-shadow: 0 0 8px rgba(0, 198, 255, 0.35) inset;
}

.chart {
  width: 100%;
}
</style>
