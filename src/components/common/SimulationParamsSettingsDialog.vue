<template>
  <div v-if="visible" class="params-settings-mask" @click.self="$emit('close')">
    <div class="params-settings-dialog" @click.stop>
      <!-- 标题栏 -->
      <div class="dialog-header">
        <div class="dialog-title">模拟参数设置</div>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <!-- 内容区域 -->
      <div class="dialog-content">
        <!-- 模拟基础设置 -->
        <div class="params-section">
          <div class="section-title">模拟基础设置</div>
          <div class="section-content two-columns">
            <div class="column">
              <!-- 数据类型 -->
              <div class="form-group">
                <label class="form-label">数据类型</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="原始数据"
                      v-model="localParams.basicSettings.dataType"
                    />
                    <span>原始数据</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="清洗数据"
                      v-model="localParams.basicSettings.dataType"
                    />
                    <span>清洗数据</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="化验室数据"
                      v-model="localParams.basicSettings.dataType"
                    />
                    <span>化验室数据</span>
                  </label>
                </div>
              </div>

              <!-- 预测算法选择 -->
              <div class="form-group">
                <label class="form-label">预测算法</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="arima"
                      v-model="predictAlgorithm"
                    />
                    <span>ARIMA</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="transformer"
                      v-model="predictAlgorithm"
                    />
                    <span>Transformer</span>
                  </label>
                </div>
              </div>

              <!-- 进水时间预测 -->
              <div class="form-group">
                <label class="form-label">进水时间预测</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="12小时"
                      v-model="localParams.basicSettings.inletTimePrediction"
                    />
                    <span>12小时</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="24小时"
                      v-model="localParams.basicSettings.inletTimePrediction"
                    />
                    <span>24小时</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="48小时"
                      v-model="localParams.basicSettings.inletTimePrediction"
                    />
                    <span>48小时</span>
                  </label>
                </div>
              </div>
            </div>

            <div class="column">
              <!-- 模拟时间间隔 -->
              <div class="form-group">
                <label class="form-label">模拟时间间隔</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="1小时"
                      v-model="localParams.basicSettings.simulationTimeInterval"
                    />
                    <span>1小时</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="2小时"
                      v-model="localParams.basicSettings.simulationTimeInterval"
                    />
                    <span>2小时</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="4小时"
                      v-model="localParams.basicSettings.simulationTimeInterval"
                    />
                    <span>4小时</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="24小时"
                      v-model="localParams.basicSettings.simulationTimeInterval"
                    />
                    <span>24小时</span>
                  </label>
                </div>
              </div>

              <!-- 自动校准周期 -->
              <div class="form-group">
                <label class="form-label">自动校准周期</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="30天"
                      v-model="localParams.basicSettings.autoCalibrationPeriod"
                    />
                    <span>30天</span>
                  </label>
                </div>
              </div>

              <!-- 清洗算法选择 -->
              <div class="form-group">
                <label class="form-label">清洗算法</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="原始数据"
                      v-model="localParams.cleaningAlgorithm"
                    />
                    <span>原始数据</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="清洗算法一"
                      v-model="localParams.cleaningAlgorithm"
                    />
                    <span>清洗算法一</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="清洗算法二"
                      v-model="localParams.cleaningAlgorithm"
                    />
                    <span>清洗算法二</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 模拟输出偏离度设置 -->
        <div class="params-section">
          <div class="section-title">模拟输出偏离度设置</div>
          <div class="section-content two-columns">
            <div class="column">
              <div
                v-for="item in leftDeviationParams"
                :key="item.key"
                class="deviation-item"
              >
                <label class="checkbox-label">
                  <input
                    type="checkbox"
                    v-model="localParams.deviationSettings[item.key].enabled"
                  />
                  <span class="param-label">{{ item.label }}:</span>
                </label>
                <input
                  type="number"
                  v-model.number="localParams.deviationSettings[item.key].value"
                  class="number-input"
                  :disabled="!localParams.deviationSettings[item.key].enabled"
                />
                <span class="unit">{{ item.unit }}</span>
              </div>
            </div>
            <div class="column">
              <div
                v-for="item in rightDeviationParams"
                :key="item.key"
                class="deviation-item"
              >
                <label class="checkbox-label">
                  <input
                    type="checkbox"
                    v-model="localParams.deviationSettings[item.key].enabled"
                  />
                  <span class="param-label">{{ item.label }}:</span>
                </label>
                <input
                  type="number"
                  v-model.number="localParams.deviationSettings[item.key].value"
                  class="number-input"
                  :disabled="!localParams.deviationSettings[item.key].enabled"
                />
                <span class="unit">{{ item.unit }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 进水数据清洗对象 -->
        <div class="params-section">
          <div class="section-title">进水数据清洗对象</div>
          <div class="section-content">
            <div class="cleaning-objects-checkboxes">
              <label
                v-for="item in cleaningObjectOptions"
                :key="item.key"
                class="checkbox-item"
              >
                <input
                  type="checkbox"
                  v-model="localParams.cleaningObjects[item.key]"
                />
                <span>{{ item.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- 出水指标约束 -->
        <div class="params-section">
          <div class="section-title">出水指标约束</div>
          <div class="section-content two-columns">
            <div
              v-for="item in effluentConstraintOptions"
              :key="item.key"
              class="constraint-item"
            >
              <label class="param-label">{{ item.label }}:</label>
              <input
                type="number"
                v-model.number="localParams.effluentConstraints[item.key]"
                class="number-input"
                step="0.1"
              />
              <span class="unit">mg/l</span>
            </div>
          </div>
        </div>

        <!-- 超参数设置 -->
        <div class="params-section">
          <div class="section-title">超参数设置</div>
          <div class="section-content two-columns">
            <div class="column">
              <div class="hyperparam-item">
                <label class="param-label">迭代次数:</label>
                <input
                  type="number"
                  v-model.number="localParams.hyperparameters.iterations"
                  class="number-input"
                />
              </div>
              <div class="hyperparam-item">
                <label class="param-label">种群大小:</label>
                <input
                  type="number"
                  v-model.number="localParams.hyperparameters.populationSize"
                  class="number-input"
                />
              </div>
              <div class="hyperparam-item">
                <label class="param-label">模拟步长大小:</label>
                <input
                  type="number"
                  v-model.number="
                    localParams.hyperparameters.simulationStepSize
                  "
                  class="number-input"
                  step="0.1"
                />
              </div>
            </div>
            <div class="column">
              <div class="hyperparam-item">
                <label class="param-label">变异阀值:</label>
                <input
                  type="number"
                  v-model.number="localParams.hyperparameters.mutationThreshold"
                  class="number-input"
                  step="0.001"
                />
              </div>
              <div class="hyperparam-item">
                <label class="param-label">混沌因子:</label>
                <input
                  type="number"
                  v-model.number="localParams.hyperparameters.chaosFactor"
                  class="number-input"
                  step="0.001"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="dialog-actions">
        <button class="btn btn-secondary" @click="handleCancel">取消</button>
        <button class="btn btn-primary" @click="handleSave">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from "vue";
import { useSimulationParamsStore } from "@/stores/useSimulationParamsStore";
import type { SimulationParams } from "@/stores/useSimulationParamsStore";
import { getSystemParams, updateSystemParams } from "@/api/systemParams";

const props = defineProps<{
  visible: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const paramsStore = useSimulationParamsStore();

const localParams = reactive<SimulationParams>(
  JSON.parse(JSON.stringify(paramsStore.params))
);

const predictAlgorithm = ref<"arima" | "transformer">(
  paramsStore.predictAlgorithm
);
const loading = ref(false);
const saving = ref(false);

watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      loadSystemParams();
    }
  }
);

async function loadSystemParams() {
  loading.value = true;
  try {
    const result = await getSystemParams();
    console.log("加载系统参数 result:", result);
    if (result.success && result.data) {
      paramsStore.applyBackendParams(result.data);
      Object.assign(
        localParams,
        JSON.parse(JSON.stringify(paramsStore.params))
      );
      predictAlgorithm.value = paramsStore.predictAlgorithm;
    } else {
      console.error("获取系统参数失败:", result.message);
    }
  } catch (error) {
    console.error("获取系统参数失败:", error);
  } finally {
    loading.value = false;
  }
}

// 左侧偏离度参数
const leftDeviationParams = [
  { key: "codRelativeError", label: "COD相对误差", unit: "%" },
  { key: "nh3nAbsoluteError", label: "NH3-N绝对误差", unit: "mg/L" },
  { key: "ssRelativeError", label: "SS相对误差", unit: "%" },
  { key: "tpAbsoluteError", label: "TP绝对误差", unit: "mg/L" },
  { key: "tnRelativeError", label: "TN相对误差", unit: "%" },
];

// 右侧偏离度参数
const rightDeviationParams = [
  { key: "do1_1PercentageError", label: "DO1-1百分比误差", unit: "%" },
  { key: "do1_2PercentageError", label: "DO1-2百分比误差", unit: "%" },
  { key: "do2_1PercentageError", label: "DO2-1百分比误差", unit: "%" },
  { key: "do2_2PercentageError", label: "DO2-2百分比误差", unit: "%" },
];

// 清洗对象选项
const cleaningObjectOptions = [
  { key: "inletNH3N", label: "进水NH3-N" },
  { key: "inletTN", label: "进水TN" },
  { key: "inletTP", label: "进水TP" },
  { key: "inletCOD", label: "进水COD" },
  { key: "inletSS", label: "进水SS" },
  { key: "AAODO", label: "AAODO" },
  { key: "MBRDO", label: "MBRDO" },
];

// 出水约束指标选项
const effluentConstraintOptions = [
  { key: "cod", label: "COD" },
  { key: "tp", label: "TP" },
  { key: "nh3n", label: "NH3-N" },
  { key: "tn", label: "TN" },
  { key: "ss", label: "SS" },
];

function handleCancel() {
  // 重置为原始值
  Object.assign(localParams, JSON.parse(JSON.stringify(paramsStore.params)));
  predictAlgorithm.value = paramsStore.predictAlgorithm;
  emit("close");
}

async function handleSave() {
  try {
    if (loading.value || saving.value) return;
    saving.value = true;
    paramsStore.updateParams(localParams);
    const payload = paramsStore.buildBackendPayload(paramsStore.getParams(), {
      predictAlgorithm: predictAlgorithm.value,
    });
    console.log("提交系统参数 payload:", payload);
    const result = await updateSystemParams(payload);
    if (!result.success) {
      console.error("保存系统参数失败:", result.message);
      alert("保存失败: " + result.message);
      return;
    }
    if (result.data) {
      paramsStore.applyBackendParams(result.data);
      Object.assign(
        localParams,
        JSON.parse(JSON.stringify(paramsStore.params))
      );
      predictAlgorithm.value = paramsStore.predictAlgorithm;
    }
    emit("close");
  } catch (error) {
    const responseData = (error as any)?.response?.data;
    console.error("保存失败:", error, responseData);
    const message =
      responseData?.message || (error as any)?.message || "保存失败，请重试";
    alert(message);
  } finally {
    saving.value = false;
  }
}
</script>

<style lang="less" scoped>
.params-settings-mask {
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

.params-settings-dialog {
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  background: linear-gradient(
    135deg,
    rgba(0, 43, 84, 0.98),
    rgba(0, 20, 40, 0.98)
  );
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
  gap: 20px;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-label {
  color: #fff;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  input[type="radio"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #00c9ff;
  }

  span {
    font-size: 14px;
  }
}

.deviation-item,
.constraint-item,
.hyperparam-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 15px;
  background: rgba(0, 43, 84, 0.6);
  border-radius: 6px;
  border: 1px solid rgba(0, 201, 255, 0.2);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #00c9ff;
  }
}

.param-label {
  color: #fff;
  font-size: 15px;
  white-space: nowrap;
}

.number-input {
  flex: 1;
  padding: 8px 12px;
  background: rgba(0, 43, 84, 0.8);
  border: 1px solid rgba(0, 201, 255, 0.4);
  border-radius: 6px;
  color: #fff;
  font-size: 15px;
  outline: none;
  transition: border-color 0.3s;

  &:focus {
    border-color: #00c9ff;
    box-shadow: 0 0 5px rgba(0, 201, 255, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.unit {
  color: #00c9ff;
  font-size: 14px;
  min-width: 40px;
}

.cleaning-objects-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(0, 43, 84, 0.6);
  border: 1px solid rgba(0, 201, 255, 0.3);
  border-radius: 20px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(0, 201, 255, 0.2);
    border-color: #00c9ff;
  }

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #00c9ff;
  }

  span {
    font-size: 14px;
  }
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

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
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
