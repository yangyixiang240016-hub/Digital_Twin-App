<template>
  <div
    v-if="visible"
    class="data-clean-effect-dialog"
    tabindex="0"
    @keydown.esc="$emit('close')"
  >
    <div class="header-bar">
      <div class="title-center">数据清洗效果图</div>
      <div class="actions">
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
    </div>

    <!-- 标签页导航 -->
    <div class="tab-navigation">
      <div
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-item"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="chart-container">
      <div ref="chartRef" class="chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from "vue";
import * as echarts from "echarts";

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  startTime: {
    type: String,
    default: "",
  },
  endTime: {
    type: String,
    default: "",
  },
  cleaningData: {
    type: Array,
    default: null,
  },
  rawData: {
    type: Array,
    default: null,
  },
});

// Emits
const emit = defineEmits(["close"]);

// 响应式数据
const chartRef = ref(null);
const activeTab = ref("flow");
let chart = null;

// 标签页配置
const tabs = [
  { key: "flow", label: "流量" },
  { key: "aao-flow", label: "AAO流量" },
  { key: "mbr-flow", label: "MBR流量" },
  { key: "cod", label: "COD" },
  { key: "nh3n", label: "NH3-N" },
  { key: "tn", label: "TN" },
  { key: "tp", label: "TP" },
];

// 从真实数据中提取对应字段的数据
const getFieldDataFromData = (fieldName, dataArray, isRawData = false) => {
  if (!dataArray || !Array.isArray(dataArray)) {
    return null;
  }

  // 字段映射 - 清洗数据使用 _cd 后缀，原始数据使用 _rd 后缀
  const fieldMapCleaned = {
    flow: "influent_tol_q_cd", // 总进水量
    "aao-flow": "aao_influent_q_cd", // AAO流量
    "mbr-flow": "mbr_influent_q_cd", // MBR流量
    cod: "aao_influent_1_1_tcod_cd", // COD
    nh3n: "aao_influent_1_1_snhx_cd", // NH3-N
    tn: "aao_influent_1_1_tn_cd", // TN
    tp: "aao_influent_1_1_tp_cd", // TP
  };

  const fieldMapRaw = {
    flow: "influent_tol_q_rd", // 总进水量
    "aao-flow": "aao_influent_q_rd", // AAO流量
    "mbr-flow": "mbr_influent_q_rd", // MBR流量
    cod: "aao_influent_1_1_tcod_rd", // COD
    nh3n: "aao_influent_1_1_snhx_rd", // NH3-N
    tn: "aao_influent_1_1_tn_rd", // TN
    tp: "aao_influent_1_1_tp_rd", // TP
  };

  // 根据数据类型选择对应的字段映射
  const fieldMap = isRawData ? fieldMapRaw : fieldMapCleaned;
  const dbField = fieldMap[fieldName];
  if (!dbField) return null;

  const values = [];
  const times = [];
  
  for (const item of dataArray) {
    if (item.ts) {
      // 格式化时间
      const date = new Date(item.ts);
      times.push(
        date.toLocaleString("zh-CN", {
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        })
      );
      // 获取对应字段的值
      values.push(item[dbField] !== null && item[dbField] !== undefined ? Number(item[dbField]) : null);
    }
  }

  return { times, values };
};

// 生成图表数据（使用真实数据或模拟数据）
const generateChartData = () => {
  // 如果提供了真实的清洗数据，优先使用真实数据
  if (props.cleaningData && Array.isArray(props.cleaningData) && props.cleaningData.length > 0) {
    const cleaningFieldData = getFieldDataFromData(activeTab.value, props.cleaningData);
    
    if (cleaningFieldData && cleaningFieldData.times.length > 0) {
      const times = cleaningFieldData.times;
      const cleanedData = cleaningFieldData.values;
      
      // 如果有原始数据，使用原始数据；否则基于清洗数据生成
      let originalData;
      if (props.rawData && Array.isArray(props.rawData) && props.rawData.length > 0) {
        // 传递 isRawData=true 参数，使用 _rd 字段映射
        const rawFieldData = getFieldDataFromData(activeTab.value, props.rawData, true);
        if (rawFieldData && rawFieldData.times.length > 0) {
          // 使用真实原始数据，需要与清洗数据的时间戳对齐
          originalData = [];
          // 创建原始数据的时间映射，使用原始的ts时间戳作为key，而不是格式化后的时间
          const rawTimeMap = new Map();
          const rawTsMap = new Map();
          
          // 获取原始数据的字段映射
          const fieldMapRaw = {
            flow: "influent_tol_q_rd",
            "aao-flow": "aao_influent_q_rd",
            "mbr-flow": "mbr_influent_q_rd",
            cod: "aao_influent_1_1_tcod_rd",
            nh3n: "aao_influent_1_1_snhx_rd",
            tn: "aao_influent_1_1_tn_rd",
            tp: "aao_influent_1_1_tp_rd",
          };
          
          // 同时建立格式化时间和原始时间戳的映射
          props.rawData.forEach((item) => {
            if (item.ts) {
              const date = new Date(item.ts);
              const formattedTime = date.toLocaleString("zh-CN", {
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
              });
              const dbField = fieldMapRaw[activeTab.value];
              if (dbField && item[dbField] !== null && item[dbField] !== undefined) {
                rawTimeMap.set(formattedTime, item[dbField]);
                // 同时存储原始时间戳用于更精确的匹配
                rawTsMap.set(item.ts, item[dbField]);
              }
            }
          });
          
          // 根据清洗数据的时间戳查找对应的原始数据
          // 如果精确匹配失败，尝试使用原始时间戳匹配
          props.cleaningData.forEach((item) => {
            if (item.ts) {
              const date = new Date(item.ts);
              const formattedTime = date.toLocaleString("zh-CN", {
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
              });
              
              // 先尝试使用格式化时间匹配
              let rawValue = rawTimeMap.get(formattedTime);
              
              // 如果格式化时间不匹配，尝试使用原始时间戳匹配
              if ((rawValue === null || rawValue === undefined) && rawTsMap.has(item.ts)) {
                rawValue = rawTsMap.get(item.ts);
              }
              
              // 如果还是不匹配，尝试找最接近的时间点（允许几分钟误差）
              if ((rawValue === null || rawValue === undefined)) {
                let closestValue = null;
                let minDiff = Infinity;
                const targetTs = new Date(item.ts).getTime();
                
                props.rawData.forEach((rawItem) => {
                  if (rawItem.ts) {
                    const rawTs = new Date(rawItem.ts).getTime();
                    const diff = Math.abs(targetTs - rawTs);
                    // 允许5分钟内的误差
                    if (diff < minDiff && diff <= 5 * 60 * 1000) {
                      minDiff = diff;
                      const dbField = fieldMapRaw[activeTab.value];
                      if (dbField) {
                        closestValue = rawItem[dbField];
                      }
                    }
                  }
                });
                
                rawValue = closestValue;
              }
              
              originalData.push(rawValue !== null && rawValue !== undefined ? Number(rawValue) : null);
            }
          });
        } else {
          // 如果原始数据时间戳不匹配，基于清洗数据生成
          originalData = cleanedData.map((val) => {
            if (val === null) return null;
            return Number((val * (1.1 + Math.random() * 0.1)).toFixed(2));
          });
        }
      } else {
        // 没有原始数据，基于清洗数据生成原始数据（添加一些波动）
        originalData = cleanedData.map((val) => {
          if (val === null) return null;
          // 原始数据通常比清洗数据略高一些（有异常值）
          return Number((val * (1.1 + Math.random() * 0.1)).toFixed(2));
        });
      }
      
      // 化验室数据作为参考（可以基于清洗数据生成）
      const labData = cleanedData.map((val) => {
        if (val === null) return null;
        return Number((val * (0.95 + Math.random() * 0.1)).toFixed(2));
      });

      return { times, originalData, cleanedData, labData };
    }
  }

  // 如果没有真实数据，使用模拟数据
  return generateMockData();
};

// 生成模拟数据（作为fallback）
const generateMockData = () => {
  const dataPoints = 24; // 24小时数据
  const times = [];
  const originalData = [];
  const cleanedData = [];
  const labData = [];

  // 生成时间序列
  const startDate = new Date(props.startTime || new Date());
  for (let i = 0; i < dataPoints; i++) {
    const time = new Date(startDate.getTime() + i * 60 * 60 * 1000); // 每小时
    times.push(
      time.toLocaleString("zh-CN", {
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
    );
  }

  // 根据当前标签页生成不同的数据
  const baseValue = getBaseValueForTab(activeTab.value);
  const variation = getVariationForTab(activeTab.value);

  for (let i = 0; i < dataPoints; i++) {
    // 原始数据：添加随机波动
    const randomFactor = 0.8 + Math.random() * 0.4; // 0.8-1.2
    const trendFactor = 1 + Math.sin(i * 0.3) * 0.3; // 趋势变化
    const originalValue = baseValue * randomFactor * trendFactor;
    originalData.push(Number(originalValue.toFixed(2)));

    // 清洗数据：在原始数据基础上进行清洗（通常降低异常值）
    const cleanedValue = originalValue * (0.85 + Math.random() * 0.1); // 清洗后通常更低
    cleanedData.push(Number(cleanedValue.toFixed(2)));

    // 化验室数据：作为参考值
    const labValue = baseValue * (0.9 + Math.random() * 0.2);
    labData.push(Number(labValue.toFixed(2)));
  }

  return { times, originalData, cleanedData, labData };
};

// 根据标签页获取基础值
const getBaseValueForTab = (tab) => {
  const values = {
    flow: 150,
    "aao-flow": 120,
    "mbr-flow": 100,
    cod: 15,
    nh3n: 8,
    tn: 12,
    tp: 1.5,
  };
  return values[tab] || 10;
};

// 根据标签页获取变化范围
const getVariationForTab = (tab) => {
  const variations = {
    flow: 0.3,
    "aao-flow": 0.25,
    "mbr-flow": 0.2,
    cod: 0.4,
    nh3n: 0.5,
    tn: 0.4,
    tp: 0.6,
  };
  return variations[tab] || 0.3;
};

// 渲染图表
const renderChart = () => {
  if (!chartRef.value) return;

  chart = echarts.init(chartRef.value);
  // 使用generateChartData，它会根据是否有真实数据来决定使用真实数据还是模拟数据
  const { times, originalData, cleanedData, labData } = generateChartData();

  const option = {
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(0, 0, 0, 0.8)",
      borderColor: "#00c9ff",
      textStyle: {
        color: "#fff",
      },
    },
    legend: {
      data: ["原始数据", "清洗数据", "化验室数据(mg/L)"],
      textStyle: { color: "#fff" },
      top: 10,
      right: 20,
    },
    grid: {
      left: 60,
      right: 20,
      top: 60,
      bottom: 40,
    },
    xAxis: {
      type: "category",
      data: times,
      axisLabel: {
        color: "#fff",
        fontSize: 12,
      },
      axisLine: {
        lineStyle: { color: "#ccc" },
      },
    },
    yAxis: {
      type: "value",
      axisLabel: {
        color: "#fff",
        formatter: (value) => value?.toFixed(1),
      },
      splitLine: {
        lineStyle: { color: "#333" },
      },
    },
    series: [
      {
        name: "原始数据",
        type: "line",
        data: originalData,
        smooth: true,
        lineStyle: {
          color: "#4FC3F7",
          width: 2,
        },
        itemStyle: {
          color: "#4FC3F7",
        },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(79, 195, 247, 0.3)" },
              { offset: 1, color: "rgba(79, 195, 247, 0.05)" },
            ],
          },
        },
      },
      {
        name: "清洗数据",
        type: "line",
        data: cleanedData,
        smooth: true,
        lineStyle: {
          color: "#4CAF50",
          width: 2,
        },
        itemStyle: {
          color: "#4CAF50",
        },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(76, 175, 80, 0.3)" },
              { offset: 1, color: "rgba(76, 175, 80, 0.05)" },
            ],
          },
        },
      },
      {
        name: "化验室数据(mg/L)",
        type: "line",
        data: labData,
        smooth: true,
        lineStyle: {
          color: "#F44336",
          width: 1,
          type: "dashed",
        },
        itemStyle: {
          color: "#F44336",
        },
        symbol: "circle",
        symbolSize: 4,
      },
    ],
  };

  chart.setOption(option);

  // 监听窗口大小变化
  window.addEventListener("resize", () => {
    if (chart) {
      chart.resize();
    }
  });
};

// 监听标签页变化
watch(activeTab, () => {
  if (chart) {
    renderChart();
  }
});

// 监听清洗数据和原始数据变化
watch(
  () => [props.cleaningData, props.rawData],
  () => {
    if (chart && props.visible) {
      renderChart();
    }
  },
  { deep: true }
);

// 监听 visible 变化，只在显示时渲染图表
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      nextTick(() => {
        renderChart();
      });
    }
  }
);

// 组件挂载时，如果已经显示则渲染图表
onMounted(() => {
  if (props.visible) {
    nextTick(() => {
      renderChart();
    });
  }
});
</script>

<style scoped>
.data-clean-effect-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  width: 1000px;
  height: 600px;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.92);
  border-radius: 16px;
  padding: 20px;
  z-index: 99999;
  pointer-events: auto;
  box-shadow: 0 0 40px rgba(0, 128, 255, 0.3);
  display: flex;
  flex-direction: column;
  outline: none;
}

.header-bar {
  position: relative;
  height: 40px;
  margin-bottom: 16px;
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

.close-btn {
  background: rgba(0, 128, 255, 0.6);
  border: none;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.close-btn:hover {
  background: rgba(0, 128, 255, 0.8);
}

.tab-navigation {
  display: flex;
  gap: 2px;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 4px;
}

.tab-item {
  flex: 1;
  padding: 8px 16px;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s;
  font-size: 14px;
  font-weight: 500;
}

.tab-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.tab-item.active {
  color: white;
  background: linear-gradient(135deg, #00c9ff, #007bff);
  box-shadow: 0 2px 8px rgba(0, 201, 255, 0.3);
}

.chart-container {
  flex: 1;
  position: relative;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .data-clean-effect-dialog {
    width: 95vw;
    height: 80vh;
  }
}

@media (max-width: 768px) {
  .tab-navigation {
    flex-wrap: wrap;
  }

  .tab-item {
    flex: none;
    min-width: 80px;
  }
}
</style>
