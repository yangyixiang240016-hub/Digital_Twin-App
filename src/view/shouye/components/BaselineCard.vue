<template>
  <!-- 左侧面板 -->
  <div class="leftPanel a-fadeinL">
    <!-- 报警监测卡片 -->
    <div class="common alarm-card">
      <div class="card-title">
        <div class="title-left"></div>
        <div class="title-section">
          <img :src="infoIcon" class="icon" />
          <span class="title-text">报警监测</span>
        </div>
        <button class="clear-btn" @click="alarmStore.clearAlarms()">
          清空
        </button>
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
        <div v-if="alarmStore.alarmList.length === 0" class="alarm-empty">
          暂无报警信息
        </div>
      </div>
    </div>

    <!-- 全场进水卡片 -->
    <div class="inflow-panel">
      <div class="title-row">
        <img class="title-icon" :src="waterIcon" />
        <span class="title-text">全场进水</span>
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

  <!-- 右侧面板 -->
  <div class="rightPanel a-fadeinR">
    <!-- 模拟按钮区域 -->
    <div class="simulate-btns">
      <div class="sim-btn-wrapper" @click="showAAODialog = true">
        <div class="sim-btn-circle">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            class="sim-icon"
          >
            <path
              d="M20.492,7.969,10.954.975A5,5,0,0,0,3,5.005V19a4.994,4.994,0,0,0,7.954,4.03l9.538-6.994a5,5,0,0,0,0-8.062Z"
              fill="white"
            />
          </svg>
        </div>
        <div class="sim-btn-label">AAO模拟</div>
      </div>

      <div class="sim-btn-wrapper" @click="showMBRDialog = true">
        <div class="sim-btn-circle">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            class="sim-icon"
          >
            <path
              d="M20.492,7.969,10.954.975A5,5,0,0,0,3,5.005V19a4.994,4.994,0,0,0,7.954,4.03l9.538-6.994a5,5,0,0,0,0-8.062Z"
              fill="white"
            />
          </svg>
        </div>
        <div class="sim-btn-label">MBR模拟</div>
      </div>
    </div>

    <!-- 设计参数 -->
    <div class="common design-param-card with-sim-btns">
      <div class="rightTitleName">
        <img :src="designIcon" class="title-icon" />设计参数（出水标准）
      </div>
      <div class="titleBg"></div>
      <div class="indicator-grid">
        <div
          class="indicator-item"
          v-for="item in indicatorList"
          :key="item.name"
        >
          <img :src="item.icon" class="indicator-icon" />
          <div class="indicator-info">
            <div class="indicator-name">{{ item.name }}</div>
            <div class="indicator-value">
              <span class="highlight">{{ item.value }}</span>
              <span class="unit">mg/L</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 全场出水 -->
    <div class="outflow-panel">
      <div class="title-row">
        <img class="title-icon" :src="waterIcon" />
        <span class="title-text">全场出水</span>
      </div>

      <div class="outflow-main">
        <FlowBall :value="outflow" />
        <div class="outflow-right">
          <div class="label">出水流量</div>
          <div class="value-row">
            <span class="number">{{ outflow?.toFixed(2) || "--" }}</span>
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
          <div>{{ item.realtime ?? "-" }}</div>
          <div>{{ item.simulated ?? "-" }}</div>
          <div>{{ item.predicted ?? "-" }}</div>
          <div>{{ item.unit }}</div>
        </div>
      </div>
    </div>

  </div>

  <!-- 覆盖层：进度条 + 结果文案 -->
  <SimOverlay
    :visible="overlay.visible"
    :title="overlay.title"
    :desc="overlay.desc"
    :progress="overlay.progress"
  />

  <!-- 基准模拟选择弹窗 -->
  <BaselineSimulateDialog
    v-if="showAAODialog"
    :visible="showAAODialog"
    processType="AAO"
    :currentStatus="isAAORunning"
    @close="showAAODialog = false"
    @statusChanged="handleAAOStatusChanged"
  />
  <BaselineSimulateDialog
    v-if="showMBRDialog"
    :visible="showMBRDialog"
    processType="MBR"
    :currentStatus="isMBRRunning"
    @close="showMBRDialog = false"
    @statusChanged="handleMBRStatusChanged"
  />
</template>

<script setup>
import {
  ref,
  reactive,
  onMounted,
  computed,
  onBeforeUnmount,
  watch,
} from "vue";
import axios from "axios";
import FlowBall from "@/components/common/FlowBall.vue";
import { useSimulationParamsStore } from "@/stores/useSimulationParamsStore";
import { useAlarmStore } from "@/stores/useAlarmStore";

import infoIcon from "@/assets/icons/info.png";
import waterIcon from "@/assets/icons/water.png";
import designIcon from "@/assets/icons/design-icon.png";
import codIcon from "@/assets/params/cod.png";
import tpIcon from "@/assets/params/tp.png";
import nh3nIcon from "@/assets/params/nh3n.png";
import tnIcon from "@/assets/params/tn.png";
import ssIcon from "@/assets/params/ss.png";

import SimOverlay from "@/components/common/SimOverlay.vue";
import BaselineSimulateDialog from "@/components/common/BaselineSimulateDialog.vue";

// ---------------------- 覆盖层状态 ----------------------
const overlay = reactive({
  visible: false,
  title: "",
  desc: "",
  progress: 0,
});
let overlayTimer = null;
const showLoading = (title, desc = "") => {
  overlay.visible = true;
  overlay.title = title;
  overlay.desc = desc;
  overlay.progress = 0;
  if (overlayTimer) clearInterval(overlayTimer);
  overlayTimer = setInterval(() => {
    if (overlay.progress < 90) {
      overlay.progress += Math.max(1, (90 - overlay.progress) * 0.08);
    }
  }, 100);
};
const showResult = (text) => {
  if (overlayTimer) {
    clearInterval(overlayTimer);
    overlayTimer = null;
  }
  overlay.title = text;
  overlay.desc = "";
  overlay.progress = 100;
  setTimeout(() => (overlay.visible = false), 900);
};
const showError = (text) => {
  if (overlayTimer) {
    clearInterval(overlayTimer);
    overlayTimer = null;
  }
  overlay.title = "操作失败";
  overlay.desc = text || "未知错误";
  overlay.progress = 100;
  setTimeout(() => (overlay.visible = false), 1500);
};

// ---------------------- 本地持久化（刷新恢复） ----------------------
const LS_AAO = "baseline:aao:running";
const LS_MBR = "baseline:mbr:running";

// ---------------------- 运行状态 ----------------------
const isAAORunning = ref(false);
const isMBRRunning = ref(false);

// ---------------------- 弹窗控制 ----------------------
const showAAODialog = ref(false);
const showMBRDialog = ref(false);

// ---------------------- 状态变化处理 ----------------------
const handleAAOStatusChanged = (status) => {
  isAAORunning.value = status;
  if (status) {
    localStorage.setItem(LS_AAO, "1");
  } else {
    localStorage.removeItem(LS_AAO);
  }
};

const handleMBRStatusChanged = (status) => {
  isMBRRunning.value = status;
  if (status) {
    localStorage.setItem(LS_MBR, "1");
  } else {
    localStorage.removeItem(LS_MBR);
  }
};

// ---------------------- 你的原有业务代码（进/出水等） ----------------------
const inflow = ref(null);
const fetchInflow = async () => {
  try {
    const res = await axios.get("/api/inflow");
    inflow.value = res.data.value;
  } catch {
    inflow.value = null;
  }
};

const inflowRealtime = ref({});
const inflowPredict = ref({});
const fetchInflowRealtime = async () => {
  try {
    inflowRealtime.value = (
      await axios.get("/api/realtime/inflow/quality")
    ).data;
  } catch {
    inflowRealtime.value = {};
  }
};
const fetchInflowPredict = async () => {
  try {
    inflowPredict.value = (await axios.get("/api/predict/inflow/quality")).data;
  } catch {
    inflowPredict.value = {};
  }
};

const waterTable = computed(() => [
  {
    name: "COD",
    value: inflowRealtime.value.cod?.toFixed(2),
    predicted: inflowPredict.value.cod?.toFixed(2),
    unit: "mg/L",
  },
  {
    name: "NH3-N",
    value: inflowRealtime.value.nh3n?.toFixed(2),
    predicted: inflowPredict.value.nh3n?.toFixed(2),
    unit: "mg/L",
  },
  {
    name: "TN",
    value: inflowRealtime.value.tn?.toFixed(2),
    predicted: inflowPredict.value.tn?.toFixed(2),
    unit: "mg/L",
  },
  {
    name: "TP",
    value: inflowRealtime.value.tp?.toFixed(2),
    predicted: inflowPredict.value.tp?.toFixed(2),
    unit: "mg/L",
  },
  {
    name: "PH",
    value: inflowRealtime.value.ph?.toFixed(2),
    predicted: inflowPredict.value.ph?.toFixed(2),
    unit: "",
  },
  {
    name: "T",
    value: inflowRealtime.value.t?.toFixed(2),
    predicted: inflowPredict.value.t?.toFixed(2),
    unit: "℃",
  },
]);

const selectedParam = ref("flow");

const simulationParamsStore = useSimulationParamsStore();
const indicatorList = ref([
  { name: "COD", value: "< 30", icon: codIcon },
  { name: "TP", value: "< 0.4", icon: tpIcon },
  { name: "NH3-N", value: "< 2", icon: nh3nIcon },
  { name: "TN", value: "< 15", icon: tnIcon },
  { name: "SS", value: "< 8", icon: ssIcon },
]);

function bindDesignParams() {
  const constraints = simulationParamsStore.params.effluentConstraints;
  indicatorList.value = [
    { name: "COD", value: `< ${constraints.cod}`, icon: codIcon },
    { name: "TP", value: `< ${constraints.tp}`, icon: tpIcon },
    { name: "NH3-N", value: `< ${constraints.nh3n}`, icon: nh3nIcon },
    { name: "TN", value: `< ${constraints.tn}`, icon: tnIcon },
    { name: "SS", value: `< ${constraints.ss}`, icon: ssIcon },
  ];
}

bindDesignParams();
const unwatchStore = watch(
  () => simulationParamsStore.params.effluentConstraints,
  bindDesignParams,
  { deep: true }
);

onBeforeUnmount(() => {
  unwatchStore && unwatchStore();
});

const outflow = ref(null);
const fetchOutflow = async () => {
  try {
    const res = await axios.get("/api/outflow");
    outflow.value = res.data.value;
  } catch {
    outflow.value = null;
  }
};
const outflowRealtime = ref({});
const outflowSimulate = ref({});
const outflowPredict = ref({});

const fetchOutflowRealtime = async () => {
  try {
    outflowRealtime.value = (
      await axios.get("/api/realtime/outflow/quality")
    ).data;
  } catch {
    outflowRealtime.value = {};
  }
};
const fetchOutflowSimulate = async () => {
  try {
    outflowSimulate.value = (
      await axios.get("/api/simulate/outflow/quality")
    ).data;
  } catch {
    outflowSimulate.value = {};
  }
};
const fetchOutflowPredict = async () => {
  try {
    outflowPredict.value = (
      await axios.get("/api/predict/outflow/quality")
    ).data;
  } catch {
    outflowPredict.value = {};
  }
};

const outTable = computed(() => [
  {
    name: "COD",
    realtime: outflowRealtime.value.cod?.toFixed(2),
    simulated: outflowSimulate.value.cod?.toFixed(2),
    predicted: outflowPredict.value.cod?.toFixed(2),
    unit: "mg/L",
  },
  {
    name: "NH3-N",
    realtime: outflowRealtime.value.nh3n?.toFixed(2),
    simulated: outflowSimulate.value.nh3n?.toFixed(2),
    predicted: outflowPredict.value.nh3n?.toFixed(2),
    unit: "mg/L",
  },
  {
    name: "TN",
    realtime: outflowRealtime.value.tn?.toFixed(2),
    simulated: outflowSimulate.value.tn?.toFixed(2),
    predicted: outflowPredict.value.tn?.toFixed(2),
    unit: "mg/L",
  },
  {
    name: "TP",
    realtime: outflowRealtime.value.tp?.toFixed(2),
    simulated: outflowSimulate.value.tp?.toFixed(2),
    predicted: outflowPredict.value.tp?.toFixed(2),
    unit: "mg/L",
  },
  {
    name: "SS",
    realtime: outflowRealtime.value.ss?.toFixed(2),
    simulated: outflowSimulate.value.ss?.toFixed(2),
    predicted: outflowPredict.value.ss?.toFixed(2),
    unit: "mg/L",
  },
  {
    name: "PH",
    realtime: outflowRealtime.value.ph?.toFixed(2),
    simulated: outflowSimulate.value.ph?.toFixed(2),
    predicted: outflowPredict.value.ph?.toFixed(2),
    unit: "",
  },
]);

// ---------------------- 报警监测 ----------------------
const alarmStore = useAlarmStore();

// ---------------------- 初始化 ----------------------
onMounted(() => {
  // 刷新后恢复按钮状态，避免误重复启动
  isAAORunning.value = localStorage.getItem(LS_AAO) === "1";
  isMBRRunning.value = localStorage.getItem(LS_MBR) === "1";

  fetchInflow();
  fetchOutflow();
  fetchInflowRealtime();
  fetchInflowPredict();
  fetchOutflowRealtime();
  fetchOutflowSimulate();
  fetchOutflowPredict();

  setInterval(fetchInflow, 5000);
  setInterval(fetchOutflow, 5000);
  setInterval(fetchInflowRealtime, 5000);
  setInterval(fetchInflowPredict, 5000);
  setInterval(fetchOutflowRealtime, 5000);
  setInterval(fetchOutflowSimulate, 5000);
  setInterval(fetchOutflowPredict, 5000);
});
</script>
