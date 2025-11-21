<template>
  <div
    v-if="visible"
    class="data-clean-dialog-overlay"
    @click="closeDialog"
    @mousedown.stop
    @mouseup.stop
  >
    <div class="data-clean-dialog" @click.stop @mousedown.stop @mouseup.stop>
      <!-- 标题栏 -->
      <div class="header-bar">
        <div class="title-center">数据清洗</div>
        <div class="actions">
          <button class="close-btn" @click="closeDialog">×</button>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="dialog-content">
        <!-- 开始时间 -->
        <div class="form-group">
          <label class="form-label">开始时间</label>
          <div class="datetime-input-wrapper">
            <input type="date" v-model="startDate" class="date-input" />
            <input type="time" v-model="startTime" class="time-input" />
          </div>
        </div>

        <!-- 结束时间 -->
        <div class="form-group">
          <label class="form-label">结束时间</label>
          <div class="datetime-input-wrapper">
            <input type="date" v-model="endDate" class="date-input" />
            <input type="time" v-model="endTime" class="time-input" />
          </div>
        </div>

        <!-- 清洗算法选择 -->
        <div class="form-group">
          <label class="form-label">清洗算法</label>
          <select v-model="selectedAlgorithm" class="algorithm-select">
            <option value="pca_dbscan">PCA-DBSCAN</option>
            <option value="dbscan">DBSCAN</option>
          </select>
        </div>

        <!-- 操作按钮 -->
        <div class="dialog-actions">
          <button class="cancel-btn" @click="closeDialog">取消</button>
          <button
            class="start-clean-btn"
            @click="startCleaning"
            :disabled="isLoading"
          >
            {{ isLoading ? "清洗中，请稍候..." : "开始清洗" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import axios from "axios";
import { getCleaningData, getRawData } from "@/api/dataClean";

// 创建独立的axios实例，避免全局baseURL影响
const apiClient = axios.create({
  baseURL: "", // 使用空baseURL，确保使用相对路径
  timeout: 0, // 数据清洗需要较长时间，设置为0表示无超时限制
});

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
});

// Emits
const emit = defineEmits(["close", "success"]);

// 响应式数据
const startDate = ref("");
const startTime = ref("");
const endDate = ref("");
const endTime = ref("");
const isLoading = ref(false);
const selectedAlgorithm = ref("pca_dbscan"); // 默认清洗算法

// 计算属性 - 格式化时间
const formattedStartTime = computed(() => {
  if (startDate.value && startTime.value) {
    return `${startDate.value} ${startTime.value}:00`;
  }
  return "";
});

const formattedEndTime = computed(() => {
  if (endDate.value && endTime.value) {
    return `${endDate.value} ${endTime.value}:00`;
  }
  return "";
});

// 方法
const closeDialog = () => {
  // 重置加载状态
  isLoading.value = false;
  emit("close");
};

// 获取数据清洗数据和原始数据（在清洗完成后调用）
const fetchCleaningData = async () => {
  try {
    console.log("清洗完成，开始获取数据清洗数据和原始数据");
    console.log("开始时间:", formattedStartTime.value);
    console.log("结束时间:", formattedEndTime.value);

    // 并行获取清洗数据和原始数据
    const [cleaningResult, rawResult] = await Promise.all([
      getCleaningData(formattedStartTime.value, formattedEndTime.value),
      getRawData(formattedStartTime.value, formattedEndTime.value),
    ]);

    console.log("数据清洗数据获取API响应:", cleaningResult);
    console.log("原始数据获取API响应:", rawResult);

    if (cleaningResult.success) {
      // API调用成功
      console.log(`数据清洗数据获取成功，共 ${cleaningResult.count} 条记录`);
      if (rawResult.success) {
        console.log(`原始数据获取成功，共 ${rawResult.count} 条记录`);
      } else {
        console.warn("原始数据获取失败:", rawResult.message);
      }

      emit("success", {
        startTime: formattedStartTime.value,
        endTime: formattedEndTime.value,
        data: cleaningResult.data, // 清洗数据
        rawData: rawResult.success ? rawResult.data : null, // 原始数据
        count: cleaningResult.count,
        rawCount: rawResult.success ? rawResult.count : 0,
        message: cleaningResult.message,
        showEffect: true,
      });
      closeDialog();
    } else {
      // API返回失败
      alert("获取数据失败：" + (cleaningResult.message || "未知错误"));
      isLoading.value = false;
    }
  } catch (error) {
    console.error("获取数据失败:", error);

    // 检查是否是网络错误
    if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
      alert("网络连接失败：服务器不可达或网络异常。\n\n请检查网络连接后重试。");
    } else if (error.response) {
      // 服务器响应了错误状态码
      const errorMsg =
        error.response.data?.message || error.response.data || "服务器错误";
      alert("获取数据失败：" + errorMsg);
    } else {
      // 其他错误
      alert("获取数据失败：" + (error.message || error.__msg || "未知错误"));
    }
    isLoading.value = false;
  }
};

// 开始数据清洗流程：先清洗，完成后获取数据
const startCleaning = async () => {
  // 验证输入
  if (
    !startDate.value ||
    !startTime.value ||
    !endDate.value ||
    !endTime.value
  ) {
    alert("请选择完整的开始时间和结束时间");
    return;
  }

  // 验证时间逻辑
  const startDateTime = new Date(formattedStartTime.value);
  const endDateTime = new Date(formattedEndTime.value);

  if (startDateTime >= endDateTime) {
    alert("开始时间必须早于结束时间");
    return;
  }

  isLoading.value = true;

  try {
    // 调用API - 使用Vite代理避免CORS问题
    // 使用/alt路径代理到192.168.3.91:8000
    const apiUrl = "/alt/DataHandle/";
    console.log("调用数据清洗API:", apiUrl);
    console.log("当前环境:", import.meta.env.MODE);
    console.log(
      "开发服务器代理应该将请求转发到: http://192.168.3.91:8000/DataHandle/"
    );

    // 使用独立的axios实例，避免全局baseURL影响
    const response = await apiClient.post(apiUrl, {
      start_time: formattedStartTime.value,
      end_time: formattedEndTime.value,
      data_clean_algrithm: selectedAlgorithm.value,
    });

    console.log("数据清洗API响应:", response.data);
    console.log("响应数据类型:", typeof response.data);
    console.log("响应数据内容:", JSON.stringify(response.data));

    // 检查API返回结果 - 更灵活的匹配
    const responseText = String(response.data || "");
    if (
      responseText.includes("aao调用数据清洗模块完成") ||
      responseText.includes("数据清洗模块完成") ||
      responseText.includes("清洗完成")
    ) {
      // 数据清洗成功，现在获取清洗后的数据
      console.log("数据清洗成功，开始获取清洗后的数据");
      await fetchCleaningData();
    } else {
      // API返回异常
      console.log("API返回内容不匹配预期:", responseText);
      alert("数据清洗失败：" + (response.data || "未知错误"));
      isLoading.value = false;
    }
  } catch (error) {
    console.error("数据清洗失败:", error);

    // 检查是否是网络错误
    if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
      // 网络错误时，询问用户是否使用模拟数据
      const useMockData = confirm(
        "网络连接失败：服务器不可达或网络异常。\n\n是否使用模拟数据进行演示？\n\n点击确定使用模拟数据，点击取消退出。"
      );

      if (useMockData) {
        // 使用模拟数据，直接获取数据（跳过清洗步骤）
        console.log("使用模拟数据，跳过清洗步骤，直接获取数据...");
        await fetchCleaningData();
        return;
      }
      isLoading.value = false;
    } else if (error.response) {
      // 服务器响应了错误状态码
      alert("数据清洗失败：" + (error.response.data || "服务器错误"));
      isLoading.value = false;
    } else {
      // 其他错误
      alert("数据清洗失败：" + (error.message || "未知错误"));
      isLoading.value = false;
    }
  }
};

// 初始化默认时间
const initDefaultTimes = () => {
  // 开始时间：2025-11-01 01:00
  startDate.value = "2025-11-01";
  startTime.value = "01:00";

  // 结束时间：2025-11-04 19:00
  endDate.value = "2025-11-04";
  endTime.value = "19:00";
};

// 组件挂载时初始化
onMounted(() => {
  initDefaultTimes();
});

// 监听对话框显示状态，打开时重置加载状态和时间
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      // 对话框打开时，重置加载状态并初始化默认时间
      isLoading.value = false;
      initDefaultTimes();
    }
  }
);
</script>

<style scoped>
.data-clean-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100000;
  pointer-events: auto;
}

.data-clean-dialog {
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border-radius: 12px;
  height: 600px;
  width: 1000px;
  max-width: 95vw;
  max-height: 95vh;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  pointer-events: auto;
  position: relative;
  z-index: 100001;
}

.header-bar {
  position: relative;
  height: 120px;
  margin-bottom: -40px;
}

.title-center {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 28px;
  font-weight: bold;
  color: white;
  background: rgba(0, 0, 0, 0.4);
  padding: 4px 16px;
  border-radius: 10px;
  box-shadow: 0 0 8px rgba(0, 255, 255, 0.4);
}

.actions {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 10px;
  align-items: center;
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

.dialog-content {
  padding: 50px 60px;
}

.form-group {
  margin-bottom: 40px;
}

.form-label {
  display: block;
  color: white;
  margin-bottom: 12px;
  font-size: 20px;
  font-weight: 500;
}

.datetime-input-wrapper {
  display: flex;
  gap: 15px;
  align-items: center;
  max-width: 500px;
  margin: 0 auto;
}

.date-input,
.time-input {
  flex: 1;
  padding: 18px 24px;
  background: rgba(0, 43, 84, 0.8);
  border: 1px solid #00c9ff;
  border-radius: 6px;
  color: white;
  font-size: 17px;
  outline: none;
  transition: border-color 0.3s;
  height: 55px;
}

.date-input:focus,
.time-input:focus {
  border-color: #00c9ff;
  box-shadow: 0 0 5px rgba(0, 201, 255, 0.3);
}

.date-input::-webkit-calendar-picker-indicator,
.time-input::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}

.algorithm-select {
  display: block;
  width: 260px;
  max-width: 100%;
  margin: 0 auto;
  padding: 0px 70px;
  background: rgba(0, 43, 84, 0.8);
  border: 1px solid #00c9ff;
  border-radius: 6px;
  color: white;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
  height: 55px;
  cursor: pointer;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.algorithm-select:focus {
  border-color: #00c9ff;
  box-shadow: 0 0 8px rgba(0, 201, 255, 0.3);
}

.algorithm-select option {
  background: rgba(26, 26, 46, 0.95);
  color: white;
  padding: 10px;
}

.dialog-actions {
  display: flex;
  justify-content: center;
  gap: 25px;
  margin-top: 40px;
}

.cancel-btn,
.start-clean-btn {
  padding: 14px 40px;
  border: none;
  border-radius: 6px;
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 120px;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.start-clean-btn {
  background: linear-gradient(135deg, #00c9ff, #007bff);
  color: white;
  border: 1px solid #00c9ff;
}

.start-clean-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #00b8e6, #0066cc);
  box-shadow: 0 5px 15px rgba(0, 201, 255, 0.3);
}

.start-clean-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 600px) {
  .data-clean-dialog {
    width: 95vw;
    margin: 20px;
  }

  .datetime-input-wrapper {
    flex-direction: column;
  }

  .dialog-actions {
    flex-direction: column;
  }

  .cancel-btn,
  .start-clean-btn {
    width: 100%;
  }
}
</style>
