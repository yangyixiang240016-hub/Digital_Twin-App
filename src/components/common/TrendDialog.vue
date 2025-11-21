<template>
  <div class="trend-dialog" tabindex="0" @keydown.esc="$emit('close')">
    <div class="header-bar">
      <div class="algorithm-label">当前预测算法：{{ algorithmDisplayName }}</div>
      <div class="title-center">进出水趋势</div>
      <div class="actions">
        <select v-model="param" class="param-select">
          <option value="total_flow">总流量</option>
          <option value="aao_flow">AAO流量</option>
          <option value="cod">COD</option>
          <option value="nh3n">NH3-N</option>
          <option value="tn">TN</option>
          <option value="tp">TP</option>
          <option value="ss">SS</option>
        </select>
        <button class="close-btn" @click="$emit('close')">关闭</button>
      </div>
    </div>

    <div ref="chartRef" class="trend-chart"></div>
    <div class="unit-text">单位：{{ unit }}</div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from "vue";
import * as echarts from "echarts";
import axios from "axios";
import http from "@/api/http";

const emit = defineEmits(["close"]);

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

// 趋势数据
const trendData = reactive({
  realtime_in: [],
  predict_in: [],
  realtime_out: [],
  predict_out: [],
});

// 图表实例
let chartInstance = null;

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

// 渲染图表
function renderChart() {
  if (!chartRef.value) return;
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  
  chartInstance.setOption({
    tooltip: { trigger: "axis" },
    legend: {
      data: ["实时进水", "预测进水", "实时出水", "预测出水"],
      textStyle: { color: "#fff" },
    },
    grid: { left: 60, right: 20, top: 60, bottom: 40 },
    xAxis: {
      type: "category",
      data: times.value,
      axisLabel: { color: "#fff" },
      axisLine: { lineStyle: { color: "#ccc" } },
    },
    yAxis: {
      type: "value",
      axisLabel: {
        color: "#fff",
        formatter: (value) => value?.toLocaleString(),
      },
      splitLine: { lineStyle: { color: "#333" } },
    },
    series: [
      {
        name: "实时进水",
        type: "line",
        data: trendData.realtime_in,
        color: "#00ffff",
      },
      {
        name: "预测进水",
        type: "line",
        data: trendData.predict_in,
        lineStyle: { type: "dashed" },
        color: "#00ff00",
      },
      {
        name: "实时出水",
        type: "line",
        data: trendData.realtime_out,
        color: "#ff66cc",
      },
      {
        name: "预测出水",
        type: "line",
        data: trendData.predict_out,
        lineStyle: { type: "dashed" },
        color: "#ffcc00",
      },
    ],
  });
  
  chartInstance.resize();
}

// 加载预测算法
async function loadPredictAlgorithm() {
  try {
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

// 定时刷新预测算法的定时器
let algorithmRefreshInterval = null;

// 窗口大小调整监听器
let resizeHandler = null;

onMounted(() => {
  nextTick(() => {
    // 加载预测算法
    loadPredictAlgorithm();
    
    // 加载趋势数据
    fetchTrendData();
    
    // 激活键盘监听
    chartRef.value?.focus();
    
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

<style scoped>
.trend-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1100px;
  height: 600px;
  background: rgba(0, 0, 0, 0.92);
  border-radius: 16px;
  padding: 24px;
  z-index: 9999;
  box-shadow: 0 0 40px rgba(0, 255, 255, 0.2);
  outline: none;
  display: flex;
  flex-direction: column;
  pointer-events: auto;
}

.header-bar {
  position: relative;
  height: 40px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.algorithm-label {
  position: absolute;
  left: 0;
  font-size: 14px;
  color: #00c9ff;
  font-weight: 500;
  padding: 4px 12px;
  background: rgba(0, 201, 255, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(0, 201, 255, 0.3);
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

.param-select {
  background-color: rgba(0, 128, 255, 0.6);
  color: white;
  border: none;
  padding: 6px 16px 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  min-width: 120px;
  width: auto;
  background-image: url("data:image/svg+xml;utf8,<svg fill='white' height='10' viewBox='0 0 24 24' width='10' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/></svg>");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px 16px;
  appearance: none;
  cursor: pointer;
}

.param-select:hover {
  background-color: rgba(0, 128, 255, 0.8);
}

.close-btn {
  background-color: rgba(0, 128, 255, 0.6);
  border: none;
  color: white;
  padding: 6px 16px;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: rgba(0, 128, 255, 0.8);
}

.trend-chart {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 0;
}

.unit-text {
  text-align: right;
  color: #ccc;
  margin-top: 8px;
  font-size: 13px;
}
</style>
