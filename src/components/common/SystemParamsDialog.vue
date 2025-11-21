<template>
  <div v-if="visible" class="system-params-mask" @click.self="$emit('close')">
    <div class="system-params-dialog" @click.stop>
      <!-- 标题栏 -->
      <div class="dialog-header">
        <div class="dialog-title">当前模拟参数</div>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <!-- 内容区域 -->
      <div class="dialog-content">
        <!-- 模拟基础设置 -->
        <div class="params-section">
          <div class="section-title">模拟基础设置</div>
          <div class="section-content two-columns">
            <div class="param-item">
              <span class="param-label">进水时间预测:</span>
              <span class="param-value">{{ params.basicSettings.inletTimePrediction }}</span>
            </div>
            <div class="param-item">
              <span class="param-label">数据类型:</span>
              <span class="param-value">{{ params.basicSettings.dataType }}</span>
            </div>
            <div class="param-item">
              <span class="param-label">模拟时间间隔:</span>
              <span class="param-value">{{ params.basicSettings.simulationTimeInterval }}</span>
            </div>
            <div class="param-item">
              <span class="param-label">自动校准周期:</span>
              <span class="param-value">{{ params.basicSettings.autoCalibrationPeriod }}</span>
            </div>
            <div class="param-item">
              <span class="param-label">清洗算法:</span>
              <span class="param-value">{{ params.cleaningAlgorithm }}</span>
            </div>
            <div class="param-item">
              <span class="param-label">预测算法:</span>
              <span class="param-value">{{ predictAlgorithmDisplay }}</span>
            </div>
          </div>
        </div>

        <!-- 模拟输出偏离度设置 -->
        <div class="params-section">
          <div class="section-title">模拟输出偏离度设置</div>
          <div class="section-content two-columns">
            <div class="column">
              <div class="param-item">
                <span class="param-label">COD相对误差:</span>
                <span class="param-value">{{ params.deviationSettings.codRelativeError.value }}%</span>
              </div>
              <div class="param-item">
                <span class="param-label">NH3-N绝对误差:</span>
                <span class="param-value">{{ params.deviationSettings.nh3nAbsoluteError.value }}mg/L</span>
              </div>
              <div class="param-item">
                <span class="param-label">SS相对误差:</span>
                <span class="param-value">{{ params.deviationSettings.ssRelativeError.value }}%</span>
              </div>
              <div class="param-item">
                <span class="param-label">TP绝对误差:</span>
                <span class="param-value">{{ params.deviationSettings.tpAbsoluteError.value }}mg/L</span>
              </div>
              <div class="param-item">
                <span class="param-label">TN相对误差:</span>
                <span class="param-value">{{ params.deviationSettings.tnRelativeError.value }}%</span>
              </div>
            </div>
            <div class="column">
              <div class="param-item">
                <span class="param-label">DO1-1百分比误差:</span>
                <span class="param-value">{{ params.deviationSettings.do1_1PercentageError.value }}%</span>
              </div>
              <div class="param-item">
                <span class="param-label">DO1-2百分比误差:</span>
                <span class="param-value">{{ params.deviationSettings.do1_2PercentageError.value }}%</span>
              </div>
              <div class="param-item">
                <span class="param-label">DO2-1百分比误差:</span>
                <span class="param-value">{{ params.deviationSettings.do2_1PercentageError.value }}%</span>
              </div>
              <div class="param-item">
                <span class="param-label">DO2-2百分比误差:</span>
                <span class="param-value">{{ params.deviationSettings.do2_2PercentageError.value }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 清洗对象 -->
        <div class="params-section">
          <div class="section-title">清洗对象</div>
          <div class="section-content">
            <div class="cleaning-objects">
              <span
                v-for="(enabled, key) in params.cleaningObjects"
                :key="key"
                class="object-tag"
                :class="{ disabled: !enabled }"
              >
                {{ getCleaningObjectLabel(key) }}{{ enabled ? '' : '(未启用)' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 出水约束指标 -->
        <div class="params-section">
          <div class="section-title">出水约束指标</div>
          <div class="section-content two-columns">
            <div class="param-item">
              <span class="param-label">COD:</span>
              <span class="param-value">{{ params.effluentConstraints.cod }} mg/l</span>
            </div>
            <div class="param-item">
              <span class="param-label">TP:</span>
              <span class="param-value">{{ params.effluentConstraints.tp }} mg/l</span>
            </div>
            <div class="param-item">
              <span class="param-label">NH3-N:</span>
              <span class="param-value">{{ params.effluentConstraints.nh3n }} mg/l</span>
            </div>
            <div class="param-item">
              <span class="param-label">TN:</span>
              <span class="param-value">{{ params.effluentConstraints.tn }} mg/l</span>
            </div>
            <div class="param-item">
              <span class="param-label">SS:</span>
              <span class="param-value">{{ params.effluentConstraints.ss }} mg/l</span>
            </div>
          </div>
        </div>

        <!-- 超参数设置 -->
        <div class="params-section">
          <div class="section-title">超参数设置</div>
          <div class="section-content two-columns">
            <div class="column">
              <div class="param-item">
                <span class="param-label">迭代次数:</span>
                <span class="param-value">{{ params.hyperparameters.iterations }}</span>
              </div>
              <div class="param-item">
                <span class="param-label">种群大小:</span>
                <span class="param-value">{{ params.hyperparameters.populationSize }}</span>
              </div>
              <div class="param-item">
                <span class="param-label">模拟步长大小:</span>
                <span class="param-value">{{ params.hyperparameters.simulationStepSize }}</span>
              </div>
            </div>
            <div class="column">
              <div class="param-item">
                <span class="param-label">变异阀值:</span>
                <span class="param-value">{{ params.hyperparameters.mutationThreshold }}</span>
              </div>
              <div class="param-item">
                <span class="param-label">混沌因子:</span>
                <span class="param-value">{{ params.hyperparameters.chaosFactor }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="dialog-actions">
        <button class="btn btn-primary" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useSimulationParamsStore } from "@/stores/useSimulationParamsStore";
import { getSystemParams } from "@/api/systemParams";

const props = defineProps<{
  visible: boolean;
}>();

defineEmits<{
  close: [];
}>();

const paramsStore = useSimulationParamsStore();
const params = computed(() => paramsStore.params);

const predictAlgorithmDisplay = computed(() =>
  paramsStore.predictAlgorithm === "arima" ? "ARIMA" : "Transformer"
);

async function loadSystemParams() {
  try {
    const result = await getSystemParams();
    if (result.success && result.data) {
      paramsStore.applyBackendParams(result.data);
    } else {
      console.error("获取系统参数失败:", result.message);
    }
  } catch (error) {
    console.error("获取系统参数失败:", error);
  }
}

watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      loadSystemParams();
    }
  }
);

function getCleaningObjectLabel(key: string): string {
  const labels: Record<string, string> = {
    inletNH3N: "进水NH3-N",
    inletTN: "进水TN",
    inletTP: "进水TP",
    inletCOD: "进水COD",
    inletSS: "进水SS",
    AAODO: "AAODO",
    MBRDO: "MBRDO",
  };
  return labels[key] || key;
}
</script>

<style lang="less" scoped>
.system-params-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  pointer-events: auto;
}

.system-params-dialog {
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  background: linear-gradient(135deg, rgba(0, 43, 84, 0.98), rgba(0, 20, 40, 0.98));
  border: 1px solid rgba(0, 201, 255, 0.3);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  pointer-events: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid rgba(0, 201, 255, 0.2);
}

.dialog-title {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
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
  flex: 1;
  overflow-y: auto;
  padding: 30px 40px;
}

.params-section {
  margin-bottom: 30px;
  background: rgba(0, 43, 84, 0.4);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid rgba(0, 201, 255, 0.2);
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 20px;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 201, 255, 0.3);
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: rgba(0, 43, 84, 0.6);
  border-radius: 6px;
  border: 1px solid rgba(0, 201, 255, 0.2);
}

.param-label {
  color: #fff;
  font-size: 16px;
}

.param-value {
  color: #00c9ff;
  font-weight: bold;
  font-size: 16px;
}

.cleaning-objects {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.object-tag {
  padding: 8px 15px;
  background: rgba(0, 201, 255, 0.2);
  border: 1px solid rgba(0, 201, 255, 0.4);
  border-radius: 20px;
  color: #00c9ff;
  font-size: 14px;
}

.object-tag.disabled {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.5);
}

.dialog-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px 30px;
  border-top: 1px solid rgba(0, 201, 255, 0.2);
}

.btn {
  padding: 12px 40px;
  border: none;
  border-radius: 6px;
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 120px;
}

.btn-primary {
  background: linear-gradient(135deg, #00c9ff, #007bff);
  color: white;
  border: 1px solid #00c9ff;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #00b8e6, #0066cc);
  box-shadow: 0 5px 15px rgba(0, 201, 255, 0.3);
}

/* 滚动条样式 */
.dialog-content::-webkit-scrollbar {
  width: 8px;
}

.dialog-content::-webkit-scrollbar-thumb {
  background: rgba(0, 201, 255, 0.3);
  border-radius: 4px;
}

.dialog-content::-webkit-scrollbar-track {
  background: transparent;
}
</style>

