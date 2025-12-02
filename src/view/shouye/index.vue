<template>
  <div class="shouye-container">
    <div id="whole" ref="whole">
      <!-- 页面阴影背景元素 -->
      <div class="back fadein" ref="shadowBg"></div>
      <!-- 标题 -->
      <div class="header-container">
        <div class="title">污水处理线智能数字孪生平台</div>
      </div>

      <!-- 顶部欢迎信息 -->
      <div class="top-info-bar">
        <div class="welcome">欢迎您！<span class="user">超级管理员</span></div>
        <div class="time-bar">
          <img :src="calendarIcon" class="calendar-icon" />
          <span>{{ currentTime }}</span>
        </div>
      </div>

      <!-- 右上角按钮容器 -->
      <div class="top-right-buttons">
        <div
          class="mode-fixed-button"
          ref="modeBtnRef"
          @click="toggleModePanel"
        >
          模式
        </div>
        <div
          class="dept-fixed-button"
          ref="deptBtnRef"
          @click="toggleDeptPanel"
        >
          工艺
        </div>
        <div
          class="data-fixed-button"
          ref="dataBtnRef"
          @click="toggleDataPanel"
        >
          数据
        </div>
        <div class="report-fixed-button">报表</div>
        <div
          class="system-fixed-button"
          ref="systemBtnRef"
          @click="toggleSystemPanel"
        >
          系统
        </div>
      </div>

      <!-- 模式面板 -->
      <div class="mode-panel-fixed" ref="modePanelRef" v-if="showModePanel">
        <div
          class="mode-item"
          :class="{ active: currentMode === 'baseline' }"
          @click="selectMode('baseline')"
        >
          基准模式
        </div>
        <div
          class="mode-item"
          :class="{ active: currentMode === 'offline' }"
          @click="selectMode('offline')"
        >
          离线模式
        </div>
        <div
          class="mode-item"
          :class="{ active: currentMode === 'online' }"
          @click="selectMode('online')"
        >
          在线模式
        </div>
      </div>

      <!-- 部门面板 -->
      <div class="dept-panel-fixed" ref="deptPanelRef" v-if="showDeptPanel">
        <div class="dept-list">
          <div
            v-for="dep in departments"
            :key="dep.key"
            class="dept-item"
            :class="{ active: currentMode === dep.key }"
            @click="selectDepartment(dep.key)"
            title="点击切换到该部门"
          >
            {{ dep.label }}
          </div>
        </div>
      </div>

      <!-- 数据面板 -->
      <div class="data-panel-fixed" ref="dataPanelRef" v-if="showDataPanel">
        <div class="data-item" @click="selectDataOption('data-clean')">
          数据清洗
        </div>
      </div>

      <!-- 系统面板 -->
      <div
        class="system-panel-fixed"
        ref="systemPanelRef"
        v-if="showSystemPanel"
      >
        <div class="system-item" @click="selectSystemOption('system-params')">
          系统参数
        </div>
        <div class="system-item" @click="selectSystemOption('params-settings')">
          参数设置
        </div>
      </div>

      <!-- 数据清洗弹窗 -->
      <DataCleanDialog
        :visible="showDataCleanDialog"
        @close="closeDataCleanDialog"
        @success="onDataCleanSuccess"
      />

      <!-- 数据清洗效果图弹窗 -->
      <DataCleanEffectDialog
        :visible="showDataCleanEffectDialog"
        :startTime="dataCleanStartTime"
        :endTime="dataCleanEndTime"
        :cleaningData="dataCleanData"
        :rawData="rawData"
        @close="closeDataCleanEffectDialog"
      />

      <!-- 系统参数弹窗 -->
      <SystemParamsDialog
        :visible="showSystemParamsDialog"
        @close="closeSystemParamsDialog"
      />

      <!-- 参数设置弹窗 -->
      <SimulationParamsSettingsDialog
        :visible="showParamsSettingsDialog"
        @close="closeParamsSettingsDialog"
      />

      <!-- 渲染卡片（保持现有 selectedMenu 的控制） -->
      <component
        v-if="activeComponent && selectedMenu === 'shouye'"
        :is="activeComponent"
      />

      <!-- 底部按钮 -->
      <div ref="bottomBut" class="button a-fadeinB">
        <div
          :class="selectedMenu === 'shouye' ? 'selected common' : 'common'"
          @click="shouYeClick"
        >
          <img
            src="../../assets/shouye/menu1.png"
            style="margin-right: 3px"
          />首页
        </div>
        <div class="common" @click="trendClick">
          <img
            src="../../assets/shouye/menu2.png"
            style="margin-right: 3px"
          />进出水趋势
        </div>
        <div
          :class="selectedMenu === 'data' ? 'selected common' : 'common'"
          @click="historyDataClick"
        >
          <img
            src="../../assets/shouye/menu2.png"
            style="margin-right: 3px"
          />历史数据
        </div>
        <div
          :class="selectedMenu === 'craft' ? 'selected common' : 'common'"
          @click="craftAssistClick"
        >
          <img
            src="../../assets/shouye/menu3.png"
            style="margin-right: 3px"
          />工艺辅助
        </div>
        <div
          :class="selectedMenu === 'inspect' ? 'selected common' : 'common'"
          @click="inspectClick"
        >
          <img
            src="../../assets/shouye/menu4.png"
            style="margin-right: 3px"
          />巡检
        </div>
      </div>
      <!-- 工艺辅助 -->
      <craftAssist
        :visible="selectedMenu === 'craft' ? true : false"
        @openAnimation="openAnimation"
      >
      </craftAssist>
    </div>
    <!-- 三维污水厂 -->
    <sewageFactory
      @closeInspect="closeInspect"
      @craftAnimationEnd="craftAnimationEnd"
      :craftAnimationStatus="craftAnimationStatus"
      :craftAnimationType="craftAnimationType"
      :selectedMenu="selectedMenu"
    ></sewageFactory>
  </div>
</template>

<script setup>
import moment from "moment";
import * as echarts from "echarts";
import { onMounted, onUnmounted, reactive, ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
// 三维污水厂
import sewageFactory from "../threejs/index.vue";
// 工艺辅助
import craftAssist from "./craftAssist.vue";
import axios from "axios";
import FlowBall from "@/components/common/FlowBall.vue";
import DataCleanDialog from "@/components/common/DataCleanDialog.vue";
import DataCleanEffectDialog from "@/components/common/DataCleanEffectDialog.vue";
import SystemParamsDialog from "@/components/common/SystemParamsDialog.vue";
import SimulationParamsSettingsDialog from "@/components/common/SimulationParamsSettingsDialog.vue";
import BaselineCard from "./components/BaselineCard.vue";
import OfflineCard from "./components/OfflineCard.vue";
import OnlineCard from "./components/OnlineCard.vue";

import calendarIcon from "@/assets/icons/calendar.png";

import { useAlarmStore } from "@/stores/useAlarmStore";

const router = useRouter();

// ====== 部门卡片组件 ======
import DeptGlobalInOut from "./components/departments/DeptGlobalInOut.vue"; // 总进出水
import DeptDistributeWell from "./components/departments/DeptDistributeWell.vue"; // 总配水井
import DeptAAOPool1 from "./components/departments/DeptAAO11.vue"; // 1#AAO池
import DeptAAOPool2 from "./components/departments/DeptAAO12.vue"; // 2#AAO池
import DeptAAOPool3 from "./components/departments/DeptMBR11.vue"; // 3#AAO池
import DeptAAOPool4 from "./components/departments/DeptMBR12.vue"; // 4#AAO池
import DeptSecondaryClarifier1 from "./components/departments/DeptSecondaryClarifier1.vue"; // 1#二次沉淀池
import DeptSecondaryClarifier2 from "./components/departments/DeptSecondaryClarifier2.vue"; // 2#二次沉淀池
import DeptLiftPump from "./components/departments/DeptLiftPump.vue"; // 二次提升泵房
import DeptHighEffluentSed from "./components/departments/DeptHighEffluentSed.vue"; // 高效沉淀池
import DeptDeepBedFilter from "./components/departments/DeptDeepBedFilter.vue"; // 深床滤池
import DeptContactDisinfection from "./components/departments/DeptDisinfection1.vue"; // 接触消毒池
import DeptEffluentWell from "./components/departments/DeptEffluentWell.vue"; // 出水井

/** ========= 面板开关 ========= */
const showModePanel = ref(false);
const showDeptPanel = ref(false);
const showDataPanel = ref(false);
const showSystemPanel = ref(false);
const showDataCleanDialog = ref(false);
const showDataCleanEffectDialog = ref(false);
const showSystemParamsDialog = ref(false);
const showParamsSettingsDialog = ref(false);
const dataCleanStartTime = ref("");
const dataCleanEndTime = ref("");
const dataCleanData = ref(null);
const rawData = ref(null);

const toggleModePanel = () => {
  showModePanel.value = !showModePanel.value;
  if (showModePanel.value) {
    showDeptPanel.value = false;
    showDataPanel.value = false;
  }
};
const toggleDeptPanel = () => {
  showDeptPanel.value = !showDeptPanel.value;
  if (showDeptPanel.value) {
    showModePanel.value = false;
    showDataPanel.value = false;
  }
};
const toggleDataPanel = () => {
  showDataPanel.value = !showDataPanel.value;
  if (showDataPanel.value) {
    showModePanel.value = false;
    showDeptPanel.value = false;
    showSystemPanel.value = false;
  }
};

const toggleSystemPanel = () => {
  showSystemPanel.value = !showSystemPanel.value;
  if (showSystemPanel.value) {
    showModePanel.value = false;
    showDeptPanel.value = false;
    showDataPanel.value = false;
  }
};

/** ========= 统一的 currentMode ========= */
const currentMode = ref("baseline");

/** ========= 组件映射 ========= */
const MODE_COMPONENTS = {
  baseline: BaselineCard,
  offline: OfflineCard,
  online: OnlineCard,
};
const DEPT_COMPONENTS = {
  "dept-global-inout": DeptGlobalInOut,
  "dept-distribute-well": DeptDistributeWell,
  "dept-aao-1": DeptAAOPool1,
  "dept-aao-2": DeptAAOPool2,
  "dept-aao-3": DeptAAOPool3,
  "dept-aao-4": DeptAAOPool4,
  "dept-secondary-clarifier-1": DeptSecondaryClarifier1,
  "dept-secondary-clarifier-2": DeptSecondaryClarifier2,
  "dept-lift-pump": DeptLiftPump,
  "dept-high-effluent-sed": DeptHighEffluentSed,
  "dept-deepbed-filter": DeptDeepBedFilter,
  "dept-contact-disinfection": DeptContactDisinfection,
  "dept-effluent-well": DeptEffluentWell,
};

// 合并映射：更直观
const ALL_COMPONENTS = { ...MODE_COMPONENTS, ...DEPT_COMPONENTS };

/** ========= 部门列表 ========= */
const departments = [
  { key: "dept-global-inout", label: "总进出水" },
  { key: "dept-distribute-well", label: "总配水井" },
  { key: "dept-aao-1", label: "1#AAO池" },
  { key: "dept-aao-2", label: "2#AAO池" },
  { key: "dept-aao-3", label: "3#AAO池" },
  { key: "dept-aao-4", label: "4#AAO池" },
  { key: "dept-secondary-clarifier-1", label: "1#二次沉淀池" },
  { key: "dept-secondary-clarifier-2", label: "2#二次沉淀池" },
  { key: "dept-lift-pump", label: "二次提升泵房" },
  { key: "dept-high-effluent-sed", label: "高效沉淀池" },
  { key: "dept-deepbed-filter", label: "深床滤池" },
  { key: "dept-contact-disinfection", label: "接触消毒池" },
  { key: "dept-effluent-well", label: "出水井" },
];

/** ========= 选择 ========= */
const selectMode = (mode) => {
  currentMode.value = mode;
  showModePanel.value = false;
  showDeptPanel.value = false;
};
const selectDepartment = (depKey) => {
  currentMode.value = depKey;
  showDeptPanel.value = false;
  showModePanel.value = false;
};
const selectDataOption = (option) => {
  console.log("选择数据选项:", option);
  showDataPanel.value = false;
  // 这里可以根据选项执行相应的操作
  if (option === "data-clean") {
    // 打开数据清洗弹窗
    showDataCleanDialog.value = true;
  }
};

const selectSystemOption = (option) => {
  console.log("选择系统选项:", option);
  showSystemPanel.value = false;
  if (option === "system-params") {
    // 打开系统参数弹窗
    showSystemParamsDialog.value = true;
  } else if (option === "params-settings") {
    // 打开参数设置弹窗
    showParamsSettingsDialog.value = true;
  }
};

// 关闭系统参数弹窗
const closeSystemParamsDialog = () => {
  showSystemParamsDialog.value = false;
};

// 关闭参数设置弹窗
const closeParamsSettingsDialog = () => {
  showParamsSettingsDialog.value = false;
};

// 关闭数据清洗弹窗
const closeDataCleanDialog = () => {
  showDataCleanDialog.value = false;
};

// 数据清洗成功回调
const onDataCleanSuccess = (result) => {
  console.log("数据清洗成功:", result);

  // 如果API调用成功且需要显示效果图
  if (result.showEffect) {
    dataCleanStartTime.value = result.startTime;
    dataCleanEndTime.value = result.endTime;
    // 保存获取到的清洗数据，替换原本的清洗数据
    dataCleanData.value = result.data || null;
    // 保存获取到的原始数据，替换原本的原始数据
    rawData.value = result.rawData || null;
    console.log("保存清洗数据，共", result.count, "条记录");
    if (result.rawData) {
      console.log("保存原始数据，共", result.rawCount, "条记录");
    }
    showDataCleanEffectDialog.value = true;
  }
};

// 关闭数据清洗效果图弹窗
const closeDataCleanEffectDialog = () => {
  showDataCleanEffectDialog.value = false;
};

/** ========= 当前卡片 ========= */
const activeComponent = computed(
  () => ALL_COMPONENTS[currentMode.value] || null
);

/** ========= 点击空白处收起面板 ========= */
const modeBtnRef = ref(null);
const modePanelRef = ref(null);
const deptBtnRef = ref(null);
const deptPanelRef = ref(null);
const dataBtnRef = ref(null);
const dataPanelRef = ref(null);
const systemBtnRef = ref(null);
const systemPanelRef = ref(null);

const onGlobalClick = (e) => {
  const t = e.target;
  const inMode =
    (modeBtnRef.value && modeBtnRef.value.contains(t)) ||
    (modePanelRef.value && modePanelRef.value.contains(t));
  const inDept =
    (deptBtnRef.value && deptBtnRef.value.contains(t)) ||
    (deptPanelRef.value && deptPanelRef.value.contains(t));
  const inData =
    (dataBtnRef.value && dataBtnRef.value.contains(t)) ||
    (dataPanelRef.value && dataPanelRef.value.contains(t));
  const inSystem =
    (systemBtnRef.value && systemBtnRef.value.contains(t)) ||
    (systemPanelRef.value && systemPanelRef.value.contains(t));

  // 如果数据清洗弹窗、效果图弹窗、系统参数弹窗或参数设置弹窗打开，不处理全局点击
  if (
    showDataCleanDialog.value ||
    showDataCleanEffectDialog.value ||
    showSystemParamsDialog.value ||
    showParamsSettingsDialog.value
  ) {
    return;
  }

  // 点击到四个面板/按钮外时，收起
  if (!inMode && !inDept && !inData && !inSystem) {
    showModePanel.value = false;
    showDeptPanel.value = false;
    showDataPanel.value = false;
    showSystemPanel.value = false;
  }
};

// 时间显示
const currentTime = ref("");

//当前时间显示
const updateTime = () => {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  const h = String(now.getHours()).padStart(2, "0");
  const min = String(now.getMinutes()).padStart(2, "0");
  currentTime.value = `${y}年${m}月${d}日 ${h}:${min}`;
};

// 阴影背景元素
const shadowBg = ref();
// 底部菜单选中项
const selectedMenu = ref("shouye");

// 总元素
const whole = ref();
// 工艺动画播放状态
let craftAnimationStatus = ref(false);
// 工艺动画类型
let craftAnimationType = ref("");

// 封装页面缩放函数
function scalePage() {
  const scale = `${document.body.clientWidth / 1920},${
    document.body.clientHeight / 941
  }`;
  if (whole.value) {
    whole.value.style.width = "1920px";
    whole.value.style.height = "941px";
    whole.value.style.transform = `scale(${scale})`;
  }
}
// 实时监听页面尺寸变化，做出相应适配
window.addEventListener("resize", scalePage);
// 首页按钮点击事件
function shouYeClick() {
  // 选择菜单切换为首页shouye
  selectedMenu.value = "shouye";
}
// 查看进出水趋势按钮点击事件
function trendClick() {
  // 在新标签页打开进出水趋势页面
  const baseUrl = window.location.origin + window.location.pathname;
  const trendUrl = `${baseUrl}#/trend`;
  window.open(trendUrl, "_blank");
}

// 历史数据按钮点击事件
function historyDataClick() {
  // 在新标签页打开历史数据页面
  const baseUrl = window.location.origin + window.location.pathname;
  const historyUrl = `${baseUrl}#/history`;
  window.open(historyUrl, "_blank");
}
// 工艺辅助按钮点击事件
function craftAssistClick() {
  selectedMenu.value = "craft";
}
// 巡检按钮点击事件
function inspectClick() {
  selectedMenu.value = "inspect";
}
// 关闭巡检
function closeInspect() {
  selectedMenu.value = "shouye";
}
// 工艺动画播放开启
function openAnimation(type, device) {
  // 工艺动画播放状态为true，子页面监听后开启播放相应的工艺动画
  craftAnimationStatus.value = true;
  craftAnimationType.value = type;
}
// 工艺动画播放结束
function craftAnimationEnd() {
  craftAnimationStatus.value = false;
}

onMounted(() => {
  updateTime();
  scalePage(); // 首次加载时缩放
  window.addEventListener("resize", scalePage); // 后续缩放监听
  const alarm = useAlarmStore();
  alarm.checkOutflowAlarm(); // 初始执行一次
  document.addEventListener("click", onGlobalClick, true); // 添加点击监听
  setInterval(() => alarm.checkOutflowAlarm(), 60000); // 每分钟执行一次
  setInterval(updateTime, 60000);
});

onUnmounted(() => {
  document.removeEventListener("click", onGlobalClick, true); // 取消监听
});

// 当切换底部菜单或路由时也收起面板
watch(
  () => selectedMenu.value,
  () => {
    showModePanel.value = false;
    showDeptPanel.value = false;
    showDataPanel.value = false;
    showSystemPanel.value = false;
  }
);
</script>

<style lang="less">
@import "./index.less";
</style>
