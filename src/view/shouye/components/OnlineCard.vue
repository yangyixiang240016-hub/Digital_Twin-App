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

  <!-- 选择在线模拟优化方式的面板 -->
  <OnlineSelectDialog
    v-if="showSelectDialog"
    @close="showSelectDialog = false"
    @confirm="onSelectConfirm"
  />

  <!-- 在线模拟流程弹窗 -->
  <OnlineSimulationDialog
    v-if="
      showOnlineSimulation &&
      currentSimulationConfig &&
      currentSimulationConfig.mode === 'simulate'
    "
    :processType="currentSimulationConfig.processType"
    :mode="currentSimulationConfig.mode"
    @close="closeOnlineSimulation"
    @complete="onSimulationComplete"
  />

  <!-- 在线优化流程弹窗 -->
  <OnlineOptimizationDialog
    v-if="
      showOnlineOptimization &&
      currentSimulationConfig &&
      currentSimulationConfig.mode === 'optimize'
    "
    :processType="currentSimulationConfig.processType"
    @close="closeOnlineOptimization"
    @complete="onOptimizationComplete"
  />

  <!-- 右侧面板 -->
  <div class="rightPanel a-fadeinR">
    <!-- 在线操作统一入口按钮 -->
    <div class="simulate-btns">
      <div class="sim-btn-wrapper" @click="showSelectDialog = true">
        <div class="sim-btn-circle" :class="{ active: isOnlineRunning }">
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
        <div class="sim-btn-label">在线模拟</div>
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
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, onBeforeUnmount } from "vue";
import axios from "axios";
import FlowBall from "@/components/common/FlowBall.vue";
import OnlineSelectDialog from "@/components/common/OnlineSelectDialog.vue";
import { useAlarmStore } from "@/stores/useAlarmStore";
import OnlineSimulationDialog from "@/components/common/OnlineSimulationDialog.vue";
import OnlineOptimizationDialog from "@/components/common/OnlineOptimizationDialog.vue";

import infoIcon from "@/assets/icons/info.png";
import waterIcon from "@/assets/icons/water.png";
import designIcon from "@/assets/icons/design-icon.png";
import codIcon from "@/assets/params/cod.png";
import tpIcon from "@/assets/params/tp.png";
import nh3nIcon from "@/assets/params/nh3n.png";
import tnIcon from "@/assets/params/tn.png";
import ssIcon from "@/assets/params/ss.png";

import { startAAO, stopAAO, startMBR, stopMBR } from "@/api/simulate";
import { useSimulationParamsStore } from "@/stores/useSimulationParamsStore";
import SimOverlay from "@/components/common/SimOverlay.vue";

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

// ---------------------- 原有业务代码（进/出水等） ----------------------
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

const bindDesignParams = () => {
  const c = simulationParamsStore.params.effluentConstraints;
  indicatorList.value = [
    { name: "COD", value: `< ${c.cod}`, icon: codIcon },
    { name: "TP", value: `< ${c.tp}`, icon: tpIcon },
    { name: "NH3-N", value: `< ${c.nh3n}`, icon: nh3nIcon },
    { name: "TN", value: `< ${c.tn}`, icon: tnIcon },
    { name: "SS", value: `< ${c.ss}`, icon: ssIcon },
  ];
};

bindDesignParams();

const stopIndicatorWatch = watch(
  () => simulationParamsStore.params.effluentConstraints,
  bindDesignParams,
  { deep: true }
);

onBeforeUnmount(() => {
  stopIndicatorWatch && stopIndicatorWatch();
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

// ---------------------- 在线模拟/优化状态 ----------------------
const showSelectDialog = ref(false);
const showOnlineSimulation = ref(false);
const showOnlineOptimization = ref(false);
const isOnlineRunning = ref(false);
const currentSimulationConfig = ref<{
  processType: "AAO" | "MBR";
  mode: "simulate" | "optimize";
} | null>(null);

function openOnlineSimulation(
  processType: "AAO" | "MBR",
  mode: "simulate" | "optimize"
) {
  currentSimulationConfig.value = { processType, mode };
  if (mode === "simulate") {
    showOnlineSimulation.value = true;
  } else if (mode === "optimize") {
    showOnlineOptimization.value = true;
  }
}

function closeOnlineSimulation() {
  showOnlineSimulation.value = false;
  currentSimulationConfig.value = null;
}

function closeOnlineOptimization() {
  showOnlineOptimization.value = false;
  currentSimulationConfig.value = null;
}

function onSimulationComplete(result: any) {
  console.log("在线模拟完成:", result);
  closeOnlineSimulation();
  isOnlineRunning.value = false;
  // 这里可以处理模拟结果，比如显示结果页面
}

function onOptimizationComplete(result: any) {
  console.log("在线优化完成:", result);
  closeOnlineOptimization();
  isOnlineRunning.value = false;
  // 这里可以处理优化结果，比如显示结果页面
}

function onSelectConfirm(config: {
  processType: "AAO" | "MBR";
  mode: "simulate" | "optimize";
}) {
  showSelectDialog.value = false;
  // 移除红色状态，在线模拟按钮保持蓝色
  // isOnlineRunning.value = true;
  openOnlineSimulation(config.processType, config.mode);
}

// ---------------------- 初始化 ----------------------
onMounted(() => {
  // 刷新后恢复按钮状态，避免误重复启动
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
