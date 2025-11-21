<template>
  <!-- 左侧面板（沿用基准样式类名） -->
  <div class="leftPanel a-fadeinL">
    <!-- 全场进水卡片 -->
    <div class="inflow-panel">
      <div class="title-row">
        <img class="title-icon" :src="waterIcon" />
        <span class="title-text">接触消毒池进水</span>
      </div>

      <div class="inflow-main">
        <FlowBall :value="inflow" />
        <div class="inflow-right">
          <div class="label">进水流量</div>
          <div class="value-row">
            <span class="number">{{ inflow?.toFixed(2) || "--" }}</span>
            <span class="unit">m³/d</span>
          </div>
        </div>
      </div>

      <div class="inflow-table">
        <div class="table-header">
          <div>参数名称</div>
          <div>实际进水</div>
          <div>进水预测</div>
          <div></div>
        </div>
        <div class="table-row" v-for="item in waterTable" :key="item.name">
          <div>{{ item.name }}</div>
          <div>{{ item.value ?? "-" }}</div>
          <div>{{ item.predicted ?? "-" }}</div>
          <div>{{ item.unit }}</div>
        </div>
      </div>
    </div>
  </div>

  <div class="dept-global-inout">
    <!-- 右侧面板 -->
    <div class="rightPanel a-fadeinR">
      <!-- 全场出水 -->
      <div class="outflow-panel">
        <div class="title-row">
          <img class="title-icon" :src="waterIcon" />
          <span class="title-text">接触消毒池出水</span>
        </div>

        <div class="outflow-main">
          <FlowBall :value="outflow" />
          <div class="outflow-right">
            <div class="label">出水流量</div>
            <div class="value-row">
              <span class="number">{{ to2(outflow) }}</span>
              <span class="unit">m³/d</span>
            </div>
          </div>
        </div>

        <div class="outflow-table">
          <div class="table-header">
            <div>参数名称</div>
            <div>实际出水</div>
            <div>出水模拟</div>
            <div>出水预测</div>
            <div></div>
          </div>
          <div class="table-row" v-for="item in outTable" :key="item.name">
            <div>{{ item.name }}</div>
            <div>{{ item.realtime }}</div>
            <div>{{ item.simulated }}</div>
            <div>{{ item.predicted }}</div>
            <div>{{ item.unit }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import axios from "axios";
import FlowBall from "@/components/common/FlowBall.vue";
import TrendInline from "@/components/common/TrendInline.vue";
import waterIcon from "@/assets/icons/water.png";

/* ================== 状态 ================== */
const showTrendDialog = ref(false);

const inflow = ref(null); // 进水流量 m³/d
const outflow = ref(null); // 出水流量 m³/d

const inflowRealtime = ref({});
const inflowPredict = ref({});

const outflowRealtime = ref({});
const outflowSimulate = ref({});
const outflowPredict = ref({});

const to2 = (n) => (n === 0 || n ? Number(n).toFixed(2) : "--");

/* ================== 拉数（并行） ================== */
async function refreshAll() {
  try {
    const [
      inFlowRes,
      outFlowRes,
      inRealRes,
      inPredRes,
      outRealRes,
      outSimRes,
      outPredRes,
    ] = await Promise.all([
      axios.get("/api/inflow"),
      axios.get("/api/outflow"),
      axios.get("/api/realtime/inflow/quality"),
      axios.get("/api/predict/inflow/quality"),
      axios.get("/api/realtime/outflow/quality"),
      axios.get("/api/simulate/outflow/quality"),
      axios.get("/api/predict/outflow/quality"),
    ]);
    inflow.value = inFlowRes?.data?.value ?? null;
    outflow.value = outFlowRes?.data?.value ?? null;

    inflowRealtime.value = inRealRes?.data || {};
    inflowPredict.value = inPredRes?.data || {};

    outflowRealtime.value = outRealRes?.data || {};
    outflowSimulate.value = outSimRes?.data || {};
    outflowPredict.value = outPredRes?.data || {};
  } catch (e) {
    // 可按需 toast/上报；这里静默兜底
  }
}

/* ================== 表格映射 ================== */
const waterTable = computed(() => [
  {
    name: "COD",
    value: to2(inflowRealtime.value.cod),
    predicted: to2(inflowPredict.value.cod),
    unit: "mg/L",
  },
  {
    name: "NH3-N",
    value: to2(inflowRealtime.value.nh3n),
    predicted: to2(inflowPredict.value.nh3n),
    unit: "mg/L",
  },
  {
    name: "TN",
    value: to2(inflowRealtime.value.tn),
    predicted: to2(inflowPredict.value.tn),
    unit: "mg/L",
  },
  {
    name: "TP",
    value: to2(inflowRealtime.value.tp),
    predicted: to2(inflowPredict.value.tp),
    unit: "mg/L",
  },
  {
    name: "PH",
    value: to2(inflowRealtime.value.ph),
    predicted: to2(inflowPredict.value.ph),
    unit: "",
  },
  {
    name: "T",
    value: to2(inflowRealtime.value.t),
    predicted: to2(inflowPredict.value.t),
    unit: "℃",
  },
]);

const outTable = computed(() => [
  {
    name: "COD",
    realtime: to2(outflowRealtime.value.cod),
    simulated: to2(outflowSimulate.value.cod),
    predicted: to2(outflowPredict.value.cod),
    unit: "mg/L",
  },
  {
    name: "NH3-N",
    realtime: to2(outflowRealtime.value.nh3n),
    simulated: to2(outflowSimulate.value.nh3n),
    predicted: to2(outflowPredict.value.nh3n),
    unit: "mg/L",
  },
  {
    name: "TN",
    realtime: to2(outflowRealtime.value.tn),
    simulated: to2(outflowSimulate.value.tn),
    predicted: to2(outflowPredict.value.tn),
    unit: "mg/L",
  },
  {
    name: "TP",
    realtime: to2(outflowRealtime.value.tp),
    simulated: to2(outflowSimulate.value.tp),
    predicted: to2(outflowPredict.value.tp),
    unit: "mg/L",
  },
  {
    name: "SS",
    realtime: to2(outflowRealtime.value.ss),
    simulated: to2(outflowSimulate.value.ss),
    predicted: to2(outflowPredict.value.ss),
    unit: "mg/L",
  },
  {
    name: "PH",
    realtime: to2(outflowRealtime.value.ph),
    simulated: to2(outflowSimulate.value.ph),
    predicted: to2(outflowPredict.value.ph),
    unit: "",
  },
]);

/* ================== 定时刷新 ================== */
let timer = null;
onMounted(() => {
  refreshAll();
  timer = setInterval(refreshAll, 5000);
});
onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>
