<template>
  <div ref="trendPage" class="trendPage">
    <!-- 顶部标题栏 -->
    <div class="header-container">
      <div class="title">进出水趋势</div>
      <div class="back-button" @click="goBack">
        <a-button type="primary">返回首页</a-button>
      </div>
    </div>

    <!-- 趋势图内容 -->
    <div ref="trendContent" class="trendContent fadein">
      <div class="trend-container">
        <div class="header-bar">
          <div class="algorithm-label">
            当前预测算法：{{ algorithmDisplayName }}
          </div>
          <div class="chart-title">进出水趋势图</div>
          <div class="actions">
            <button
              class="offline-predict-btn"
              @click="showOfflinePredictDialog = true"
            >
              离线预测
            </button>
            <select v-model="param" class="param-select">
              <option value="total_flow">总流量</option>
              <option value="aao_flow">AAO流量</option>
              <option value="cod">COD</option>
              <option value="nh3n">NH3-N</option>
              <option value="tn">TN</option>
              <option value="tp">TP</option>
              <option value="ss">SS</option>
            </select>
          </div>
        </div>

        <div class="chartRegion">
          <div ref="chartRef" class="trend-chart"></div>
        </div>
      </div>
    </div>

    <!-- 离线预测对话框 -->
    <div
      v-if="showOfflinePredictDialog"
      class="offline-predict-mask"
      @click.self="showOfflinePredictDialog = false"
    >
      <div class="offline-predict-dialog" @click.stop>
        <div class="dialog-header">
          <div class="dialog-title">离线预测</div>
          <button class="close-btn" @click="showOfflinePredictDialog = false">
            ×
          </button>
        </div>
        <div class="dialog-content">
          <div class="form-row">
            <label>预测开始时间:</label>
            <input
              type="datetime-local"
              v-model="offlinePredictForm.endTime"
              class="datetime-input"
            />
          </div>
          <div class="form-info">
            <div class="info-item">
              <span class="info-label">预测步数:</span>
              <span class="info-value">{{ forecastStep }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">预测算法:</span>
              <span class="info-value">{{ forecastAlgorithm }}</span>
            </div>
          </div>
          <div class="dialog-actions">
            <button
              class="cancel-btn"
              @click="showOfflinePredictDialog = false"
            >
              取消
            </button>
            <button
              class="confirm-btn"
              @click="handleOfflinePredict"
              :disabled="predicting"
            >
              {{ predicting ? "预测中..." : "开始预测" }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  reactive,
  computed,
  onMounted,
  onUnmounted,
  watch,
  nextTick,
} from "vue";
import { useRouter } from "vue-router";
import * as echarts from "echarts";
import axios from "axios";
import { getSystemParams } from "@/api/systemParams";
import { altApi } from "@/api/http";
import { message } from "ant-design-vue";
import "./trend.less";

const router = useRouter();

// 参数选择
const param = ref("total_flow");
const chartRef = ref(null);
const times = ref([]);
const unit = ref("");

// 预测算法
const predictAlgorithm = ref("arima");

// 计算属性：显示算法名称
const algorithmDisplayName = computed(() => {
  return predictAlgorithm.value === "transformer" ? "transformer" : "arima";
});

// 离线预测相关
const showOfflinePredictDialog = ref(false);
const predicting = ref(false);
const offlinePredictForm = reactive({
  endTime: "",
});

// 系统参数
const systemParams = ref({
  predict_steps_sp: 12,
  predict_algorithm_sp: 0,
});

// 计算预测步数（根据系统参数中的predict_steps_sp）
const forecastStep = computed(() => {
  // 直接使用系统参数的值，无需映射
  return systemParams.value.predict_steps_sp || 6;
});

// 计算预测算法（根据系统参数中的predict_algorithm_sp）
const forecastAlgorithm = computed(() => {
  const algo = systemParams.value.predict_algorithm_sp;
  // 0=arima, 1=transformer
  // Transformer传itransformer，ARIMA传arima
  return algo === 1 ? "itransformer" : "arima";
});

// 趋势数据
const trendData = reactive({
  realtime_in: [],
  predict_in: [],
  realtime_out: [],
  predict_out: [],
});

// 图表实例
let chartInstance = null;

// 返回首页
function goBack() {
  router.push("/");
}

// 获取趋势数据
async function fetchTrendData() {
  try {
    const res = await axios.get(`/api/trend?param=${param.value}`);
    const data = res.data;
    times.value = data.times || [];
    trendData.realtime_in = data.realtime_in || [];
    trendData.predict_in = data.predict_in || [];
    trendData.realtime_out = data.realtime_out || [];
    trendData.predict_out = data.predict_out || [];
    unit.value = data.unit || "";
    renderChart();
  } catch (error) {
    console.error("趋势图数据获取失败:", error);
  }
}

// 根据参数类型获取颜色配置
function getColorConfig(paramType) {
  const colorMap = {
    total_flow: "#04CDF0", // 总流量 - 使用总进水量颜色
    aao_flow: "#1B8CDC", // AAO流量
    cod: "#FF6B6B", // COD
    nh3n: "#FFD93D", // NH3-N
    tn: "#9B59B6", // TN
    tp: "#E67E22", // TP
    ss: "#00FF00", // SS - 使用MBR流量颜色
  };

  return colorMap[paramType] || "#04CDF0"; // 默认使用总流量颜色
}

// 获取出水颜色（使用完全不同的颜色来明显区分）
function getOutflowColor(inflowColor) {
  // 将进水的颜色转换为出水颜色（使用完全不同的色系）
  const colorMap = {
    "#04CDF0": "#FF6B6B", // 总流量 - 进水青色，出水红色
    "#1B8CDC": "#FF9999", // AAO流量 - 进水蓝色，出水粉红色
    "#FF6B6B": "#4DA6FF", // COD - 进水红色，出水蓝色
    "#FFD93D": "#9B59B6", // NH3-N - 进水黄色，出水紫色
    "#9B59B6": "#FFD93D", // TN - 进水紫色，出水黄色
    "#E67E22": "#00FF00", // TP - 进水橙色，出水绿色
    "#00FF00": "#E67E22", // SS - 进水绿色，出水橙色
  };

  return colorMap[inflowColor] || "#FF6B6B"; // 默认使用红色
}

// 渲染图表
function renderChart() {
  if (!chartRef.value) return;

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }

  const inflowColor = getColorConfig(param.value);
  const outflowColor = getOutflowColor(inflowColor);

  chartInstance.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
      },
      extraCssText:
        "background: linear-gradient(270deg, #1D4A63 0%, #0F244D 100%);border:0px;color:#BBFFFF;",
    },
    legend: {
      data: ["实时进水", "预测进水", "实时出水", "预测出水"],
      top: "10%",
      left: "center",
      textStyle: {
        color: "#AFEEEE",
      },
      itemWidth: 15,
      itemHeight: 15,
      itemGap: 12,
      width: "85%",
    },
    grid: {
      left: "8%",
      right: "8%",
      top: "22%",
      bottom: "10%",
    },
    xAxis: {
      type: "category",
      data: times.value,
      axisLine: {
        lineStyle: {
          color: "#BBFFFF",
        },
      },
      axisLabel: {
        color: "#BBFFFF",
      },
      splitLine: {
        show: false,
      },
    },
    yAxis: {
      type: "value",
      name: unit.value || "",
      position: "left",
      axisLine: {
        lineStyle: {
          color: "#BBFFFF",
        },
      },
      axisLabel: {
        color: "#BBFFFF",
        formatter: (value) => value?.toLocaleString(),
      },
      splitLine: {
        lineStyle: {
          color: "#AFEEEE",
          opacity: 0.3,
        },
      },
    },
    series: [
      {
        name: "实时进水",
        type: "line",
        data: trendData.realtime_in,
        smooth: true,
        lineStyle: { color: inflowColor, width: 2 },
        itemStyle: { color: inflowColor },
      },
      {
        name: "预测进水",
        type: "line",
        data: trendData.predict_in,
        smooth: true,
        lineStyle: {
          color: inflowColor,
          width: 2,
          type: "dashed",
        },
        itemStyle: { color: inflowColor },
      },
      {
        name: "实时出水",
        type: "line",
        data: trendData.realtime_out,
        smooth: true,
        lineStyle: { color: outflowColor, width: 2 },
        itemStyle: { color: outflowColor },
      },
      {
        name: "预测出水",
        type: "line",
        data: trendData.predict_out,
        smooth: true,
        lineStyle: {
          color: outflowColor,
          width: 2,
          type: "dashed",
        },
        itemStyle: { color: outflowColor },
      },
    ],
  });

  chartInstance.resize();
}

// 加载预测算法
async function loadPredictAlgorithm() {
  try {
    const http = (await import("@/api/http")).default;
    const response = await http.get("/system-params/predict-algorithm");

    // 安全地获取数据
    let data = null;
    if (response && response.data !== undefined) {
      data = response.data;
    } else if (response) {
      data = response;
    }

    // 处理不同的返回格式
    if (data === null || data === undefined) {
      console.warn("API返回数据为空，使用默认值arima");
      predictAlgorithm.value = "arima";
      return;
    }

    // 如果返回的是数字（1或0）
    if (typeof data === "number") {
      predictAlgorithm.value = data === 1 ? "transformer" : "arima";
      return;
    }

    // 如果返回的是对象
    if (typeof data === "object" && data !== null) {
      // 检查是否有algorithm字段
      if (data.algorithm) {
        const algo = String(data.algorithm).toLowerCase();
        if (algo === "transformer" || algo === "arima") {
          predictAlgorithm.value = algo;
          return;
        }
      }

      // 检查是否有value字段（数字）
      if (typeof data.value === "number") {
        predictAlgorithm.value = data.value === 1 ? "transformer" : "arima";
        return;
      }
    }

    // 如果都不匹配，使用默认值
    console.warn("无法解析预测算法数据，使用默认值arima", data);
    predictAlgorithm.value = "arima";
  } catch (error) {
    console.error("获取预测算法失败:", error);
    predictAlgorithm.value = "arima";
  }
}

// 加载系统参数
async function loadSystemParams() {
  try {
    const result = await getSystemParams();
    if (result.success && result.data) {
      systemParams.value = {
        predict_steps_sp: result.data.predict_steps_sp || 12,
        predict_algorithm_sp: result.data.predict_algorithm_sp || 0,
      };
    }
  } catch (error) {
    console.error("获取系统参数失败:", error);
  }
}

// 处理离线预测
async function handleOfflinePredict() {
  if (!offlinePredictForm.endTime) {
    message.warning("请选择预测开始时间");
    return;
  }

  // 将datetime-local格式转换为API需要的格式 "YYYY-MM-DD HH:mm:ss"
  // datetime-local格式: "YYYY-MM-DDTHH:mm"
  // API需要格式: "YYYY-MM-DD HH:mm:ss"
  const endTimeStr = offlinePredictForm.endTime.replace("T", " ") + ":00";
  const startTimeStr = endTimeStr; // start_time与end_time相同

  const requestData = {
    start_time: startTimeStr,
    end_time: endTimeStr,
    forecast_step: Number(forecastStep.value),
    need_train: 0,
    forecast_algorithm: forecastAlgorithm.value,
  };

  console.log("离线预测请求数据:", requestData);
  console.log("请求URL:", "/alt/IOForcast/AAO/");

  predicting.value = true;
  try {
    const response = await altApi.post("/IOForcast/AAO/", requestData);
    console.log("离线预测响应:", response);
    message.success("离线预测请求已提交");
    showOfflinePredictDialog.value = false;
    // 预测完成后刷新趋势数据
    setTimeout(() => {
      fetchTrendData();
    }, 2000);
  } catch (error) {
    console.error("离线预测失败:", error);
    console.error("错误详情:", {
      message: error.message,
      response: error.response,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url,
    });

    // 如果返回的是HTML错误页面，说明后端服务可能有问题
    let errorMessage = "离线预测失败，请稍后重试";
    if (error.response?.data) {
      if (
        typeof error.response.data === "string" &&
        error.response.data.includes("<!DOCTYPE html>")
      ) {
        errorMessage =
          "后端服务错误：请检查后端服务是否正常运行（http://192.168.3.91:8000）";
      } else if (error.response.data.message) {
        errorMessage = error.response.data.message;
      } else if (error.response.data.error) {
        errorMessage = error.response.data.error;
      }
    } else if (error.message) {
      errorMessage = error.message;
    }

    message.error(errorMessage);
  } finally {
    predicting.value = false;
  }
}

// 打开离线预测对话框时加载系统参数并设置默认时间
watch(showOfflinePredictDialog, (newVal) => {
  if (newVal) {
    loadSystemParams();
    // 设置默认时间为当前整点时间（分钟和秒设为0）
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    offlinePredictForm.endTime = `${year}-${month}-${day}T${hours}:00`;
  }
});

// 定时刷新数据
let dataRefreshInterval = null;
// 定时刷新算法
let algorithmRefreshInterval = null;
// 窗口大小调整监听器
let resizeHandler = null;

onMounted(() => {
  // 设置网页标题
  document.title = "进出水趋势";

  nextTick(() => {
    // 加载预测算法
    loadPredictAlgorithm();

    // 加载系统参数
    loadSystemParams();

    // 加载趋势数据
    fetchTrendData();

    // 每5秒刷新一次数据
    dataRefreshInterval = setInterval(() => {
      fetchTrendData();
    }, 5000);

    // 每5秒刷新一次预测算法，确保与系统参数同步
    algorithmRefreshInterval = setInterval(() => {
      loadPredictAlgorithm();
    }, 5000);

    // 监听窗口大小变化
    resizeHandler = () => {
      if (chartInstance) {
        chartInstance.resize();
      }
    };
    window.addEventListener("resize", resizeHandler);
  });
});

// 组件卸载时清理
onUnmounted(() => {
  // 清除定时器
  if (dataRefreshInterval) {
    clearInterval(dataRefreshInterval);
    dataRefreshInterval = null;
  }
  if (algorithmRefreshInterval) {
    clearInterval(algorithmRefreshInterval);
    algorithmRefreshInterval = null;
  }

  // 移除窗口大小监听
  if (resizeHandler) {
    window.removeEventListener("resize", resizeHandler);
    resizeHandler = null;
  }

  // 销毁图表实例
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
});

// 监听参数变化
watch(param, () => {
  fetchTrendData();
});
</script>

<style lang="less" scoped>
@import "./trend.less";
</style>
