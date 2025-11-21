<template>
  <div ref="historyDataPage" class="historyDataPage">
    <!-- 顶部标题栏 -->
    <div class="header-container">
      <div class="title">历史数据查询</div>
      <div class="back-button" @click="goBack">
        <a-button type="primary">返回首页</a-button>
      </div>
    </div>

    <!-- 历史数据内容 -->
    <div ref="historyData" class="historyData fadein">
      <!-- 顶部框 -->
      <div class="topFrame">
        <div class="header">
          <div class="header_menu_center">
            <div class="header_menu_date">
              <a-range-picker
                v-model:value="queryDate"
                format="YYYY-MM-DD"
                style="width: 100%"
              />
            </div>
            <div class="header_menu_button">
              <a-button type="primary" @click="handleQuery" :loading="loading">
                <SearchOutlined />查询
              </a-button>
            </div>
          </div>
        </div>
        <div class="chartRegion">
          <div class="historyChart" id="historyChart" ref="historyChart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import moment from "moment";
import * as echarts from "echarts";
import dayjs from "dayjs";
import { SearchOutlined } from "@ant-design/icons-vue";
import { queryHistoryData, queryCleanedHistoryData } from "@/api/historyData";
import "./history.less";

const router = useRouter();

// 查询日期
let queryDate = ref([dayjs().subtract(7, "day"), dayjs()]);
// 加载状态
const loading = ref(false);
// 图表实例
let historyChart = null;
// resize事件处理函数
let resizeHandler = null;

// 返回首页
function goBack() {
  router.push("/");
}

onMounted(() => {
  // 设置网页标题
  document.title = "历史数据查询";

  // 宽度缩放比
  const widthScale = document.body.clientWidth / screen.availWidth;
  // 高度缩放比
  const heightScale = document.body.clientHeight / (screen.availHeight - 109);
  // 时间控件大小根据页面缩放比自适应
  const timeControlScale = setInterval(() => {
    // 获取时间控件
    const timeControl = [
      ...document.getElementsByClassName("ant-picker-dropdown"),
    ];
    // 存在长度length则表示获取到时间控件元素
    if (timeControl.length) {
      // 设置缩放比
      timeControl[0].style.transform = `scale(${widthScale},${heightScale})`;
      timeControl[0].style.transformOrigin = "left top";
      // 销毁这个定时器
      clearInterval(timeControlScale);
    }
  }, 500);
  // 初始化视图
  initChart();
  // 首次加载时自动查询
  handleQuery();
});

// 组件卸载时清理
onBeforeUnmount(() => {
  // 移除resize事件监听器
  if (resizeHandler) {
    window.removeEventListener("resize", resizeHandler);
    resizeHandler = null;
  }
  // 销毁图表实例
  if (historyChart && typeof historyChart.dispose === "function") {
    try {
      historyChart.dispose();
    } catch (error) {
      console.warn("销毁图表实例时出错:", error);
    }
    historyChart = null;
  }
});

// 初始化图表
function initChart() {
  nextTick(() => {
    const chartElement = document.getElementById("historyChart");
    if (!chartElement) {
      console.error("图表容器未找到");
      return;
    }
    // 如果已经存在图表实例，先销毁它
    if (historyChart && typeof historyChart.dispose === "function") {
      try {
        historyChart.dispose();
      } catch (error) {
        console.warn("销毁旧图表实例时出错:", error);
      }
    }
    historyChart = echarts.init(chartElement);

    // 设置默认的空数据配置
    const option = {
      title: {
        text: "历史数据趋势图",
        x: "center",
        y: "0%",
        textStyle: {
          color: "#BBFFFF",
          fontWeight: "500",
          fontSize: 20,
        },
      },
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "cross",
        },
        extraCssText:
          "background: linear-gradient(270deg, #1D4A63 0%, #0F244D 100%);border:0px;color:#BBFFFF;",
        formatter: function (params) {
          if (!params || params.length === 0) return "";
          const date = `<div style="margin-bottom: 5px; font-weight: bold;">${moment(
            params[0].axisValue
          ).format("YYYY-MM-DD")}</div>`;
          let data = "";
          params.forEach((item) => {
            const marker = item.marker;
            const value =
              item.value !== null && item.value !== undefined
                ? item.value
                : "无数据";
            data += `<div style="margin: 2px 0;">${marker} ${item.seriesName}：${value}</div>`;
          });
          return `${date}${data}`;
        },
      },
      legend: {
        data: [],
        top: "6%",
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
        top: "18%",
        bottom: "10%",
      },
      xAxis: {
        type: "time",
        axisLine: {
          lineStyle: {
            color: "#BBFFFF",
          },
        },
        axisLabel: {
          color: "#BBFFFF",
          formatter: function (value) {
            return moment(value).format("MM-DD");
          },
        },
        splitLine: {
          show: false,
        },
      },
      yAxis: [
        {
          type: "value",
          name: "流量 (m³/d)",
          position: "left",
          axisLine: {
            lineStyle: {
              color: "#BBFFFF",
            },
          },
          axisLabel: {
            color: "#BBFFFF",
          },
          splitLine: {
            lineStyle: {
              color: "#AFEEEE",
              opacity: 0.3,
            },
          },
        },
        {
          type: "value",
          name: "浓度 (mg/L)",
          position: "right",
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
      ],
      series: [],
    };
    historyChart.setOption(option);

    // 监听窗口大小变化
    resizeHandler = () => {
      if (historyChart && typeof historyChart.resize === "function") {
        historyChart.resize();
      }
    };
    window.addEventListener("resize", resizeHandler);
  });
}

// 处理查询
async function handleQuery() {
  if (!queryDate.value || queryDate.value.length !== 2) {
    alert("请选择开始日期和结束日期");
    return;
  }

  const startDate = queryDate.value[0].format("YYYY-MM-DD");
  const endDate = queryDate.value[1].format("YYYY-MM-DD");

  if (startDate > endDate) {
    alert("开始日期必须早于或等于结束日期");
    return;
  }

  loading.value = true;

  try {
    let rawData = [];
    let cleanedData = [];

    // 同时查询原始数据和清洗数据
    const [rawResult, cleanedResult] = await Promise.all([
      queryHistoryData(startDate, endDate),
      queryCleanedHistoryData(startDate, endDate),
    ]);

    if (rawResult.success && rawResult.data) {
      rawData = rawResult.data;
    } else {
      console.warn("查询原始数据失败:", rawResult.message);
    }

    if (cleanedResult.success && cleanedResult.data) {
      cleanedData = cleanedResult.data;
    } else {
      console.warn("查询清洗数据失败:", cleanedResult.message);
    }

    // 更新图表
    if (rawData.length > 0 || cleanedData.length > 0) {
      updateChart(rawData, cleanedData);
    } else {
      alert("未查询到数据");
      updateChart([], []);
    }
  } catch (error) {
    console.error("查询历史数据失败:", error);
    alert("查询失败：" + (error.message || "未知错误"));
  } finally {
    loading.value = false;
  }
}

// 更新图表数据
function updateChart(rawData, cleanedData) {
  if (!historyChart || typeof historyChart.setOption !== "function") {
    console.warn("图表未初始化，正在初始化...");
    initChart();
    // 等待图表初始化完成后再更新
    nextTick(() => {
      if (historyChart && typeof historyChart.setOption === "function") {
        updateChartData(rawData, cleanedData);
      }
    });
    return;
  }
  updateChartData(rawData, cleanedData);
}

// 更新图表数据（内部函数）
function updateChartData(rawData, cleanedData) {
  if (!historyChart || typeof historyChart.setOption !== "function") {
    return;
  }

  const fieldNames = [
    "总进水量",
    "AAO流量",
    "MBR流量",
    "COD",
    "NH3-N",
    "TN",
    "TP",
  ];

  const series = [];
  const rawLegendData = [];
  const cleanedLegendData = [];

  // 原始数据的颜色配置
  const rawColors = {
    总进水量: "#04CDF0",
    AAO流量: "#1B8CDC",
    MBR流量: "#00FF00",
    COD: "#FF6B6B",
    "NH3-N": "#FFD93D",
    TN: "#9B59B6",
    TP: "#E67E22",
  };

  // 清洗数据的颜色配置
  const cleanedColors = {
    总进水量: "#04CDF0",
    AAO流量: "#1B8CDC",
    MBR流量: "#00FF00",
    COD: "#FF6B6B",
    "NH3-N": "#FFD93D",
    TN: "#9B59B6",
    TP: "#E67E22",
  };

  // 处理原始数据
  if (rawData && rawData.length > 0) {
    fieldNames.forEach((fieldName) => {
      const data = rawData.map((item) => [item.ts, item[fieldName]]);
      const seriesName = `raw_${fieldName}`;
      series.push({
        name: seriesName,
        type: "line",
        data: data,
        yAxisIndex:
          fieldName === "总进水量" ||
          fieldName === "AAO流量" ||
          fieldName === "MBR流量"
            ? 0
            : 1,
        smooth: true,
        lineStyle: { color: rawColors[fieldName], width: 2 },
        itemStyle: { color: rawColors[fieldName] },
      });
      rawLegendData.push({ name: seriesName, fieldName: fieldName });
    });
  }

  // 处理清洗数据
  if (cleanedData && cleanedData.length > 0) {
    fieldNames.forEach((fieldName) => {
      const data = cleanedData.map((item) => [item.ts, item[fieldName]]);
      const seriesName = `cleaned_${fieldName}`;
      series.push({
        name: seriesName,
        type: "line",
        data: data,
        yAxisIndex:
          fieldName === "总进水量" ||
          fieldName === "AAO流量" ||
          fieldName === "MBR流量"
            ? 0
            : 1,
        smooth: true,
        lineStyle: {
          color: cleanedColors[fieldName],
          width: 2,
          type: "dashed", // 使用虚线区分清洗数据
        },
        itemStyle: { color: cleanedColors[fieldName] },
      });
      cleanedLegendData.push({ name: seriesName, fieldName: fieldName });
    });
  }

  // 创建虚拟的series用于显示"原始："和"清洗："标签
  // 这些series不在图表中显示，只在图例中显示文本
  const labelSeries = [];
  if (rawLegendData.length > 0) {
    labelSeries.push({
      name: "__label_raw__",
      type: "line",
      data: [],
      showSymbol: false,
      symbol: "none",
      symbolSize: 0,
      lineStyle: { opacity: 0, width: 0 },
      itemStyle: { opacity: 0 },
      legendHoverLink: false,
    });
  }
  if (cleanedLegendData.length > 0) {
    labelSeries.push({
      name: "__label_cleaned__",
      type: "line",
      data: [],
      showSymbol: false,
      symbol: "none",
      symbolSize: 0,
      lineStyle: { opacity: 0, width: 0 },
      itemStyle: { opacity: 0 },
      legendHoverLink: false,
    });
  }

  // 构建图例数据
  const allLegendData = [];
  if (rawLegendData.length > 0) {
    allLegendData.push("__label_raw__");
  }
  rawLegendData.forEach((item) => {
    allLegendData.push(item.name);
  });
  if (cleanedLegendData.length > 0) {
    allLegendData.push("__label_cleaned__");
  }
  cleanedLegendData.forEach((item) => {
    allLegendData.push(item.name);
  });

  // 合并所有series
  const allSeries = [...labelSeries, ...series];

  // 更新图表
  historyChart.setOption({
    legend: {
      data: allLegendData,
      formatter: function (name) {
        // 如果是标签项，只显示文本
        if (name === "__label_raw__") {
          return "原始：";
        }
        if (name === "__label_cleaned__") {
          return "清洗：";
        }
        // 判断是原始数据还是清洗数据
        if (name.startsWith("raw_")) {
          return name.replace("raw_", "");
        } else if (name.startsWith("cleaned_")) {
          return name.replace("cleaned_", "");
        }
        return name;
      },
      selectedMode: true,
    },
    series: allSeries,
  });
}
</script>

<style scoped>
::v-deep .ant-picker-dropdown {
  transform: calc(2) !important;
}
</style>
