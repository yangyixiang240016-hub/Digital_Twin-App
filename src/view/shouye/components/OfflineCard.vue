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

  <!-- 选择离线模拟优化方式的面板 -->
  <OfflineSelectDialog
    v-if="showSelectDialog"
    @close="showSelectDialog = false"
    @confirm="onSelectConfirm"
  />

  <!-- 离线模拟流程弹窗 -->
  <OfflineSimulationDialog
    v-if="
      showOfflineSimulation &&
      currentSimulationConfig &&
      currentSimulationConfig.mode === 'simulate'
    "
    :processType="currentSimulationConfig.processType"
    :mode="currentSimulationConfig.mode"
    @close="closeOfflineSimulation"
    @complete="onSimulationComplete"
  />

  <!-- 离线优化流程弹窗 -->
  <OfflineOptimizeDialog
    v-if="
      showOfflineOptimization &&
      currentSimulationConfig &&
      currentSimulationConfig.mode === 'optimize'
    "
    :processType="currentSimulationConfig.processType"
    @close="closeOfflineOptimization"
    @complete="onOptimizationComplete"
  />

  <!-- 右侧面板 -->
  <div class="rightPanel a-fadeinR">
    <!-- 离线操作统一入口按钮 -->
    <div class="simulate-btns">
      <div class="sim-btn-wrapper" @click="showSelectDialog = true">
        <div class="sim-btn-circle" :class="{ active: isOfflineRunning }">
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
        <div class="sim-btn-label">离线模拟</div>
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
import http from "@/api/http";
import { altApi } from "@/api/http";
import FlowBall from "@/components/common/FlowBall.vue";
import { useAlarmStore } from "@/stores/useAlarmStore";

import infoIcon from "@/assets/icons/info.png";
import waterIcon from "@/assets/icons/water.png";
import designIcon from "@/assets/icons/design-icon.png";
import codIcon from "@/assets/params/cod.png";
import tpIcon from "@/assets/params/tp.png";
import nh3nIcon from "@/assets/params/nh3n.png";
import tnIcon from "@/assets/params/tn.png";
import ssIcon from "@/assets/params/ss.png";

import { startAAO, stopAAO, startMBR, stopMBR } from "@/api/simulate";
import SimOverlay from "@/components/common/SimOverlay.vue";

import OfflineSelectDialog from "@/components/common/OfflineSelectDialog.vue";
import OfflineSimulationDialog from "@/components/common/OfflineSimulationDialog.vue";
import OfflineOptimizeDialog from "@/components/common/OfflineOptimizeDialog.vue";
import { useSimulationParamsStore } from "@/stores/useSimulationParamsStore";

// ---------------------- 离线模拟参数 ----------------------
import { useRouter } from "vue-router";
import { useOfflineStore } from "/src/stores/useOfflineStore"; // 如果你用了 Pinia 状态

const router = useRouter();
const offlineStore = useOfflineStore();

function handleOfflineConfirm(p: {
  process: "aao" | "mbr";
  mode: "simulate" | "optimize";
  simType: "dynamic" | "steady";
  controlMode: "aeration" | "do";
}) {
  // 可写入全局状态，流程页会用到
  offlineStore.setSelection({ process: p.process, mode: p.mode });
  // 其它可选项也存一下（如果需要）
  // offlineStore.setExtra({ simType: p.simType, controlMode: p.controlMode });

  // 关闭弹窗
  showOffline.value = false;

  // 跳转到统一流程页
  router.push({
    name: "offline-runner",
    params: { process: p.process, mode: p.mode }, // 直接小写
    // 如果你想在 URL 携带额外选项，用 query：
    // query: { simType: p.simType, controlMode: p.controlMode }
  });
}
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

// ---------------------- 离线模拟参数 ----------------------
const showSelectDialog = ref(false);
const showOfflineSimulation = ref(false);
const showOfflineOptimization = ref(false);
const showOffline = ref(false);
const isOfflineRunning = ref(false);
const currentSimulationConfig = ref<{
  processType: "AAO" | "MBR";
  mode: "simulate" | "optimize";
} | null>(null);

function openOfflineSimulation(
  processType: "AAO" | "MBR",
  mode: "simulate" | "optimize"
) {
  currentSimulationConfig.value = { processType, mode };
  if (mode === "simulate") {
    showOfflineSimulation.value = true;
  } else if (mode === "optimize") {
    showOfflineOptimization.value = true;
  }
}

function closeOfflineSimulation() {
  showOfflineSimulation.value = false;
  currentSimulationConfig.value = null;
}

function closeOfflineOptimization() {
  showOfflineOptimization.value = false;
  currentSimulationConfig.value = null;
}

function onSimulationComplete(result: any) {
  console.log("模拟完成:", result);
  closeOfflineSimulation();
  // 这里可以处理模拟结果，比如显示结果页面
}

function onOptimizationComplete(result: any) {
  console.log("优化完成:", result);
  closeOfflineOptimization();
  // 这里可以处理优化结果，比如显示结果页面
}

function onSelectConfirm(payload) {
  showSelectDialog.value = false;
  // 根据选择的结果打开相应的离线模拟弹窗
  const processType = payload.process as "AAO" | "MBR";
  const mode = payload.func as "simulate" | "optimize";
  openOfflineSimulation(processType, mode);
}

async function runOffline(opts: {
  process: "AAO" | "MBR";
  func: "simulate" | "optimize";
  simType: "dynamic" | "steady";
  mode: "aeration" | "do";
}) {
  // 这里你也可以把时间段、数据源等一起带上（若已有选择控件，就从本页拿）
  const range = { start: null, end: null }; // TODO: 有时间段控件时替换
  const source = "cleaned"; // TODO: raw/cleaned/lab 从你的选择控件取

  showLoading(
    "模拟进行中",
    `${opts.process} · ${opts.simType === "dynamic" ? "动态" : "稳态"} · ${
      opts.mode === "aeration" ? "曝气" : "溶解氧"
    }`
  );

  try {
    // 1) 启动后端离线任务
    const payload: any = {
      process: opts.process,
      type: opts.simType,
      mode: opts.mode,
      source,
      range: [range.start, range.end],
      params: {}, // TODO: 若你有参数面板，这里传入
    };
    if (opts.func === "optimize") {
      payload.objectives = {}; // TODO: 目标/约束/权重等
      payload.ranges = {};
      payload.constraints = {};
    }

    const { data } = await altApi.post("/ManualSimulate/AAO/", payload);
    const jobId = data?.jobId;
    if (!jobId) throw new Error("后端未返回 jobId");

    // 2) 轮询进度
    while (true) {
      const { data: st } = await altApi.get("/ManualSimulate/AAO/status", {
        params: { jobId },
      });
      overlay.progress = Math.min(98, Number(st?.progress ?? overlay.progress));
      if (st?.status === "done") break;
      if (st?.status === "error") throw new Error(st?.message || "后端错误");
      await new Promise((r) => setTimeout(r, 800));
    }

    // 3) 拉取结果，写回你现有的 UI 容器（直接喂给表格/球体/趋势）
    const result = (
      await altApi.get("/ManualSimulate/AAO/result", { params: { jobId } })
    ).data;

    // ——把结果映射到你已有的变量：——
    inflow.value = result?.kpi?.inflow_q ?? inflow.value;
    outflow.value = result?.kpi?.effluent_q ?? outflow.value;

    inflowRealtime.value = result?.kpi?.influent ?? inflowRealtime.value; // “历史进水”
    inflowPredict.value = result?.kpi?.influent_pred ?? inflowPredict.value; // “进水预测”

    outflowRealtime.value = result?.kpi?.effluent_real ?? outflowRealtime.value; // “历史出水”
    outflowSimulate.value = result?.kpi?.effluent_sim ?? outflowSimulate.value; // “出水模拟”
    outflowPredict.value = result?.kpi?.effluent_pred ?? outflowPredict.value; // “出水预测”

    showResult("离线任务完成");
  } catch (e: any) {
    showError(e?.message || "离线任务失败");
  }
}

// ---------------------- 原有业务代码（进/出水等） ----------------------
const inflow = ref(null);
const fetchInflow = async () => {
  try {
    const res = await http.get("/inflow");
    inflow.value = res.data.value;
  } catch {
    inflow.value = null;
  }
};

const inflowRealtime = ref({});
const inflowPredict = ref({});
const fetchInflowRealtime = async () => {
  try {
    inflowRealtime.value = (await http.get("/realtime/inflow/quality")).data;
  } catch {
    inflowRealtime.value = {};
  }
};
const fetchInflowPredict = async () => {
  try {
    inflowPredict.value = (await http.get("/predict/inflow/quality")).data;
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

const syncIndicators = () => {
  const c = simulationParamsStore.params.effluentConstraints;
  indicatorList.value = [
    { name: "COD", value: `< ${c.cod}`, icon: codIcon },
    { name: "TP", value: `< ${c.tp}`, icon: tpIcon },
    { name: "NH3-N", value: `< ${c.nh3n}`, icon: nh3nIcon },
    { name: "TN", value: `< ${c.tn}`, icon: tnIcon },
    { name: "SS", value: `< ${c.ss}`, icon: ssIcon },
  ];
};
syncIndicators();
const stopIndicatorWatch = watch(
  () => simulationParamsStore.params.effluentConstraints,
  syncIndicators,
  { deep: true }
);

onBeforeUnmount(() => {
  stopIndicatorWatch && stopIndicatorWatch();
});

const outflow = ref(null);
const fetchOutflow = async () => {
  try {
    const res = await http.get("/outflow");
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
    outflowRealtime.value = (await http.get("/realtime/outflow/quality")).data;
  } catch {
    outflowRealtime.value = {};
  }
};
const fetchOutflowSimulate = async () => {
  try {
    outflowSimulate.value = (await http.get("/simulate/outflow/quality")).data;
  } catch {
    outflowSimulate.value = {};
  }
};
const fetchOutflowPredict = async () => {
  try {
    outflowPredict.value = (await http.get("/predict/outflow/quality")).data;
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
