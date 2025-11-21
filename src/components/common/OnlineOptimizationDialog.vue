<template>
  <div class="online-optimization-mask" @click.self="$emit('close')">
    <div class="online-optimization-dialog" @click.stop>
      <!-- 关闭按钮 -->
      <div class="close-btn" @click="$emit('close')">×</div>

      <!-- 标题 -->
      <div class="dialog-title">在线模式——{{ processType }}优化</div>

      <!-- 步骤进度条 -->
      <div class="progress-bar">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="step-item"
          :class="{
            active: currentStep === index + 1,
            completed: currentStep > index + 1,
          }"
        >
          <div class="step-circle">{{ index + 1 }}</div>
          <div class="step-label">{{ step }}</div>
        </div>
        <div
          class="progress-line"
          :style="{ transform: `scaleX(${progressScale})` }"
        ></div>
      </div>

      <!-- 步骤内容 -->
      <div class="step-content">
        <!-- 步骤1: 选择优化算法 -->
        <div v-if="currentStep === 1" class="step-panel">
          <div class="step-title">
            <div class="step-title-left">
              <span class="arrow">→</span>
              选择优化算法
            </div>
          </div>
          <div class="algorithm-options">
            <div
              v-for="algorithm in algorithms"
              :key="algorithm.id"
              class="algorithm-card"
              :class="{ selected: selectedAlgorithm === algorithm.id }"
              @click="selectedAlgorithm = algorithm.id"
            >
              <div class="algorithm-name">{{ algorithm.name }}</div>
              <div v-if="selectedAlgorithm === algorithm.id" class="check-icon">
                ✓
              </div>
            </div>
          </div>
          <div class="step-actions">
            <button
              class="next-btn"
              @click="nextStep"
              :disabled="!selectedAlgorithm"
            >
              下一步
            </button>
          </div>
        </div>

        <!-- 步骤2: 选择优化目标 -->
        <div v-if="currentStep === 2" class="step-panel">
          <div class="step-title">
            <div class="step-title-left">
              <span class="arrow">→</span>
              选择优化目标
            </div>
            <select
              v-if="processType === 'AAO'"
              v-model="optimizeData.aaoConfigName"
              class="config-select"
              @change="handleConfigChange"
            >
              <option value="">请选择参数配置</option>
              <option value="wry_tn">跟踪总氮 (wry_tn)</option>
              <option value="wry_tn_economy">经济总氮 (wry_tn_economy)</option>
            </select>
          </div>
          <div class="objectives-container">
            <div class="objectives-grid">
              <div class="objective-section">
                <div class="section-title">出水指标及权重比设置</div>
                <div class="objectives-table">
                  <div class="table-header">
                    <div class="header-cell">出水指标</div>
                    <div class="header-cell">目标值</div>
                    <div class="header-cell">权重比</div>
                  </div>
                  <div class="table-body">
                    <div class="table-row">
                      <div class="cell">
                        <span>NH4</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.nh4.target"
                          class="target-input"
                          :disabled="isConfigSelected"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.nh4.weight"
                          class="weight-input"
                          :disabled="isConfigSelected"
                        />
                      </div>
                    </div>
                    <div class="table-row">
                      <div class="cell">
                        <span>TN</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.tn.target"
                          class="target-input"
                          :disabled="isConfigSelected"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.tn.weight"
                          class="weight-input"
                          :disabled="isConfigSelected"
                        />
                      </div>
                    </div>
                    <div class="table-row">
                      <div class="cell">
                        <span>TP</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.tp.target"
                          class="target-input"
                          :disabled="isConfigSelected"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.tp.weight"
                          class="weight-input"
                          :disabled="isConfigSelected"
                        />
                      </div>
                    </div>
                    <div class="table-row">
                      <div class="cell">
                        <span>SS</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.ss.target"
                          class="target-input"
                          :disabled="isConfigSelected"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.ss.weight"
                          class="weight-input"
                          :disabled="isConfigSelected"
                        />
                      </div>
                    </div>
                    <div class="table-row">
                      <div class="cell">
                        <span>COD</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.cod.target"
                          class="target-input"
                          :disabled="isConfigSelected"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="cell">
                        <input
                          type="number"
                          v-model.number="objectives.cod.weight"
                          class="weight-input"
                          :disabled="isConfigSelected"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="objective-section">
                <div class="section-title">经济消耗指标及目标值</div>
                <div class="economic-mode-setting">
                  <div class="economic-mode-row">
                    <label class="economic-mode-label">是否采用经济模式:</label>
                    <label class="switch">
                      <input
                        type="checkbox"
                        v-model="objectives.useEconomicMode"
                        :disabled="isConfigSelected"
                      />
                      <span class="slider"></span>
                    </label>
                    <span class="economic-mode-status">{{
                      objectives.useEconomicMode ? "是" : "否"
                    }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="objectives-note">
            优化指标可多选, 可单选; 其中出水指标的权重比例默加=1;
          </div>
          <div class="step-actions">
            <button class="prev-btn" @click="prevStep">上一步</button>
            <button class="next-btn" @click="nextStep">下一步</button>
          </div>
        </div>

        <!-- 步骤3: 优化参数设置 -->
        <div v-if="currentStep === 3" class="step-panel">
          <div class="step-title">
            <div class="step-title-left">
              <span class="arrow">→</span>
              设置优化参数
            </div>
          </div>
          <div v-if="processType === 'AAO'" class="parameters-selection">
            <div class="parameter-options">
              <div
                v-for="param in aaoParamOptions"
                :key="param.id"
                class="parameter-card"
                :class="{
                  selected: selectedParameters.includes(param.id),
                  disabled: isConfigSelected,
                }"
                @click="!isConfigSelected && toggleParameter(param.id)"
              >
                <span class="parameter-name">{{ param.name }}</span>
                <div
                  v-if="selectedParameters.includes(param.id)"
                  class="check-icon"
                >
                  ✓
                </div>
              </div>
            </div>
            <div class="parameter-note">优化参数可多选,可单选:</div>
          </div>
          <div v-else class="parameters-selection">
            <div class="parameter-options">
              <div
                v-for="param in parameterOptions"
                :key="param.id"
                class="parameter-card"
                :class="{
                  selected: selectedParameters.includes(param.id),
                  disabled: isConfigSelected,
                }"
                @click="!isConfigSelected && toggleParameter(param.id)"
              >
                <span class="parameter-name">{{ param.name }}</span>
                <div
                  v-if="selectedParameters.includes(param.id)"
                  class="check-icon"
                >
                  ✓
                </div>
              </div>
            </div>
            <div class="parameter-note">优化参数可多选,可单选:</div>
          </div>
          <div class="step-actions">
            <button class="prev-btn" @click="prevStep">上一步</button>
            <button class="next-btn" @click="nextStep">下一步</button>
          </div>
        </div>

        <!-- 步骤4: 生成优化结果 -->
        <div v-if="currentStep === 4" class="step-panel">
          <div class="step-title">
            <div class="step-title-left">
              <span class="arrow">→</span>
              生成优化结果
            </div>
          </div>
          <div class="optimization-progress">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: progress.toFixed(2) + '%' }"
              ></div>
            </div>
            <div class="progress-text">{{ progress.toFixed(2) }}%</div>
          </div>
          <div class="step-actions">
            <button class="prev-btn" @click="prevStep">上一步</button>
            <button
              v-if="progress < 100"
              class="start-btn"
              @click="startOptimization"
            >
              开始优化
            </button>
            <button v-else class="next-btn" @click="nextStep">下一步</button>
          </div>
        </div>

        <!-- 步骤5: 优化结果对比图 -->
        <div v-if="currentStep === 5" class="step-panel">
          <div class="step-title">
            <div class="step-title-left">
              <span class="arrow">→</span>
              优化结果对比图
            </div>
          </div>
          <!-- AAO在线优化结果详情 -->
          <div
            v-if="optimizeResultData && processType === 'AAO'"
            class="aao-result-details"
          >
            <div class="aao-result-container">
              <!-- 左侧列 -->
              <div class="aao-result-column">
                <!-- 进水量 -->
                <div class="aao-result-section">
                  <div class="aao-section-title">
                    <span class="arrow">→</span>
                    进水量
                  </div>
                  <div class="aao-param-row">
                    <label>1#AAO生化池进水流量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_influent_1_q_oor") || "—"
                    }}</span>
                    <span class="param-unit">m³/d</span>
                  </div>
                  <div class="aao-param-row">
                    <label>2#AAO生化池进水流量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_influent_2_q_oor") || "—"
                    }}</span>
                    <span class="param-unit">m³/d</span>
                  </div>
                </div>

                <!-- 出水参数 -->
                <div class="aao-result-section">
                  <div class="aao-section-title">
                    <span class="arrow">→</span>
                    出水参数
                  </div>
                  <div class="aao-param-row">
                    <label>出水流量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_q_oor") || "—"
                    }}</span>
                    <span class="param-unit">m³/d</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水化学需氧量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_tcod_oor") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水生化需氧量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_tbod_oor") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水悬浮固体浓度:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_ss_oor") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水总磷:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_tp_oor") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水总氮:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_tn_oor") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水氨氮:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_snhx_oor") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水硝氮:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_snox_oor") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水正磷酸盐:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_spo4_oor") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                </div>

                <!-- 药剂参数 -->
                <div class="aao-result-section">
                  <div class="aao-section-title">
                    <span class="arrow">→</span>
                    药剂参数
                  </div>
                  <div class="aao-param-row">
                    <label>2号加药间聚合氯化铝投加量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_pac_q_oor") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                </div>

                <!-- 回流参数 -->
                <div class="aao-result-section">
                  <div class="aao-section-title">
                    <span class="arrow">→</span>
                    回流参数
                  </div>
                  <div class="aao-param-row">
                    <label>1#回流污泥流量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_ras_1_q_oor") || "—"
                    }}</span>
                    <span class="param-unit">m³/d</span>
                  </div>
                  <div class="aao-param-row">
                    <label>2#回流污泥流量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_ras_2_q_oor") || "—"
                    }}</span>
                    <span class="param-unit">m³/d</span>
                  </div>
                </div>
              </div>

              <!-- 右侧列 -->
              <div class="aao-result-column">
                <!-- 曝气参数 -->
                <div class="aao-result-section">
                  <div class="aao-section-title">
                    <span class="arrow">→</span>
                    曝气参数
                  </div>
                  <!-- 1-1#AAO生化池 -->
                  <div class="aao-bioreactor-group">
                    <div class="aao-bioreactor-title">1-1#AAO生化池</div>
                    <div class="aao-param-row">
                      <label>好氧段1曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr3_1_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段2曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr4_1_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段3曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr5_1_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段4曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr6_1_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段5曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr7_1_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                  </div>
                  <!-- 1-2#AAO生化池 -->
                  <div class="aao-bioreactor-group">
                    <div class="aao-bioreactor-title">1-2#AAO生化池</div>
                    <div class="aao-param-row">
                      <label>好氧段1曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr3_1_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段2曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr4_1_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段3曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr5_1_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段4曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr6_1_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段5曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr7_1_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                  </div>
                  <!-- 2-1#AAO生化池 -->
                  <div class="aao-bioreactor-group">
                    <div class="aao-bioreactor-title">2-1#AAO生化池</div>
                    <div class="aao-param-row">
                      <label>好氧段1曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr3_2_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段2曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr4_2_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段3曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr5_2_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段4曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr6_2_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段5曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr7_2_1_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                  </div>
                  <!-- 2-2#AAO生化池 -->
                  <div class="aao-bioreactor-group">
                    <div class="aao-bioreactor-title">2-2#AAO生化池</div>
                    <div class="aao-param-row">
                      <label>好氧段1曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr3_2_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段2曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr4_2_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段3曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr5_2_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段4曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr6_2_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段5曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr7_2_2_qair_ntp_oor") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="complete-btn" @click="completeOptimization">
              完成优化
            </button>
            <button class="reconfigure-btn" @click="reconfigure">
              重新配置
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { aaoSimulationService } from "@/api/aaoSimulation";

const props = defineProps<{
  processType: "AAO" | "MBR";
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "complete", result: any): void;
}>();

// 响应式数据
const currentStep = ref(1);
const progress = ref(0);
const selectedAlgorithm = ref<string>("");
const selectedParameters = ref<string[]>([]);
const selectedChartParam = ref<string>("1-1AAO#曝气量");
const optimizeResultData = ref<any>(null);
const optimizationStartTime = ref<string>("");

// 优化数据
const optimizeData = reactive({
  aaoConfigName: "",
});

// 步骤定义
const steps = [
  "选择优化算法",
  "选择优化目标",
  "设置优化参数",
  "生成优化结果",
  "优化结果对比图",
];

// 进度比例计算
const progressScale = computed(() => {
  return currentStep.value / steps.length;
});

// 优化目标
const objectives = reactive({
  nh4: { target: 0, weight: 1 },
  tn: { target: 0, weight: 1 },
  tp: { target: 0, weight: 1 },
  ss: { target: 0, weight: 1 },
  cod: { target: 0, weight: 1 },
  useEconomicMode: false,
});

// 优化算法选项
const algorithms = [
  { id: "KD-DD01", name: "KD-DD01" },
  { id: "KD-DD02", name: "KD-DD02" },
  { id: "KD-DD03", name: "KD-DD03" },
];

// AAO优化参数选项
const aaoParamOptions = [
  { id: "aeration", name: "曝气量" },
  { id: "sludgeDischarge", name: "排泥量" },
  { id: "internalRecycle", name: "内回流参数" },
  { id: "externalRecycle", name: "外回流参数" },
  { id: "multiInlet", name: "多点进水比例" },
  { id: "do", name: "DO参数" },
  { id: "pac", name: "PAC参数" },
  { id: "carbonSource", name: "碳源" },
  { id: "sludgeConcentration", name: "生物池污泥浓度" },
];

// 优化参数选项 (MBR用)
const parameterOptions = computed(() => {
  if (props.processType === "AAO") {
    return aaoParamOptions;
  } else {
    return [
      { id: "aeration", name: "曝气参数" },
      { id: "pacDosage", name: "PAC投加量" },
      { id: "mlrReturn", name: "MLR回流流量" },
      { id: "rasReturn", name: "RAS回流流量" },
      { id: "sasSludge", name: "SAS污泥量" },
    ];
  }
});

// 判断是否选择了参数配置(仅AAO类型,且选择了wry_tn或wry_tn_economy)
const isConfigSelected = computed(() => {
  if (props.processType !== "AAO") return false;
  const configName = optimizeData.aaoConfigName;
  return configName === "wry_tn" || configName === "wry_tn_economy";
});

// 图表参数选项
const chartParams = [
  { id: "1-1AAO#曝气量", name: "1-1AAO#曝气量" },
  { id: "1-2AAO#曝气量", name: "1-2AAO#曝气量" },
  { id: "2-1AAO#曝气量", name: "2-1AAO#曝气量" },
  { id: "2-2AAO#曝气量", name: "2-2AAO#曝气量" },
  { id: "AAO内回流量", name: "AAO内回流量" },
  { id: "AAO外回流量", name: "AAO外回流量" },
  { id: "AAO剩余污泥量", name: "AAO剩余污泥量" },
  { id: "AAO生物池污泥浓度", name: "AAO生物池污泥浓度" },
];

// 方法
const nextStep = () => {
  if (currentStep.value < 5) {
    currentStep.value++;
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
  }
};

const toggleParameter = (paramId: string) => {
  if (isConfigSelected.value) return;
  const index = selectedParameters.value.indexOf(paramId);
  if (index > -1) {
    selectedParameters.value.splice(index, 1);
  } else {
    selectedParameters.value.push(paramId);
  }
};

const handleConfigChange = () => {
  // 当选择参数配置后,可以在这里添加额外的逻辑
  // 如果需要根据配置自动设置某些参数,可以在这里实现
};

const startOptimization = async () => {
  progress.value = 0;

  try {
    console.log("启动在线优化:", props.processType);

    // 调用相应的在线优化API
    let response;
    if (props.processType === "AAO") {
      response = await aaoSimulationService.startAAOOnlineOptimization();
    } else {
      response = await aaoSimulationService.startMBROnlineOptimization();
    }

    if (!response.success) {
      throw new Error(response.message || "在线优化启动失败");
    }

    console.log("在线优化启动成功:", response);

    // 记录优化开始时间
    optimizationStartTime.value = new Date()
      .toISOString()
      .slice(0, 16)
      .replace("T", " ");

    // 模拟进度更新
    const interval = setInterval(async () => {
      progress.value += Math.random() * 10 + 5;
      if (progress.value >= 100) {
        progress.value = 100;
        clearInterval(interval);
        // 加载优化结果数据
        await loadOnlineOptimizationResultData();
        // 完成优化后自动跳转到优化结果对比图界面
        setTimeout(() => {
          currentStep.value = 5;
        }, 500);
      }
    }, 200);
  } catch (error) {
    console.error("在线优化启动失败:", error);
    progress.value = 0;
    alert(error instanceof Error ? error.message : "在线优化启动失败");
  }
};

const stopOptimization = () => {
  emit("close");
};

const completeOptimization = () => {
  emit("complete", {
    algorithm: selectedAlgorithm.value,
    parameters: selectedParameters.value,
    objectives: objectives,
  });
};

const reconfigure = () => {
  currentStep.value = 1;
  selectedAlgorithm.value = "";
  selectedParameters.value = [];
  progress.value = 0;
};

// 获取字段值的辅助函数
const getFieldValue = (fieldName: string) => {
  if (!optimizeResultData.value || !optimizeResultData.value.fields) {
    return null;
  }
  const fieldData = optimizeResultData.value.fields[fieldName];
  if (
    fieldData &&
    typeof fieldData.value !== "undefined" &&
    fieldData.value !== null
  ) {
    return fieldData.value;
  }
  return null;
};

// 从后端加载在线优化结果数据
const loadOnlineOptimizationResultData = async () => {
  try {
    console.log("开始从后端加载在线优化结果数据...");

    // 查询最新一条数据（仅AAO类型）
    if (props.processType === "AAO") {
      const response =
        await aaoSimulationService.getOnlineOptimizationResultByStartTime();

      if (response.success && response.data) {
        console.log("成功获取在线优化结果:", response.data);
        optimizeResultData.value = response.data;
        return;
      }
    }

    // 如果查询失败，使用空数据
    console.warn("未获取到在线优化结果数据");
    optimizeResultData.value = null;
  } catch (error) {
    console.error("加载在线优化结果数据失败:", error);
    optimizeResultData.value = null;
  }
};

// 时间格式转换函数：将ISO格式转换为后端需要的格式
const formatTimeForAPI = (isoTime: string) => {
  if (!isoTime) return "";
  const date = new Date(isoTime);
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");
  const seconds = date.getSeconds().toString().padStart(2, "0");

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

onMounted(() => {
  selectedAlgorithm.value = "KD-DD01";
});
</script>

<style scoped>
.online-optimization-mask {
  position: fixed;
  inset: 0;
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(6px);
  pointer-events: auto;
}

.online-optimization-dialog {
  width: 1200px;
  height: 800px;
  max-width: 95vw;
  max-height: 95vh;
  background: linear-gradient(180deg, #0a2d5e, #031836);
  border: 1px solid rgba(0, 160, 255, 0.25);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
  border-radius: 14px;
  color: #e6f3ff;
  font-size: 16px;
  position: relative;
  overflow: hidden;
  pointer-events: auto;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  width: 30px;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  color: white;
  z-index: 10;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.dialog-title {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  color: white;
  padding: 20px 0;
  background: rgba(0, 0, 0, 0.4);
  margin-bottom: 20px;
}

.progress-bar {
  position: relative;
  padding: 60px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
  z-index: 2;
  min-width: 0;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.step-item.active .step-circle {
  background: #4f46e5;
  box-shadow: 0 0 15px rgba(79, 70, 229, 0.6);
  transform: scale(1.1);
}

.step-item.completed .step-circle {
  background: #10b981;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

.step-label {
  color: #ffffff;
  font-size: 12px;
  text-align: center;
  line-height: 1.2;
  word-break: break-word;
  max-width: 100%;
}

.progress-line {
  position: absolute;
  top: 50px;
  left: 20px;
  height: 3px;
  background: linear-gradient(90deg, #4f46e5 0%, #10b981 100%);
  transition: transform 0.3s ease;
  z-index: 1;
  border-radius: 2px;
  transform-origin: left center;
  box-sizing: border-box;
  margin-left: 20px;
  /* 确保进度线能够到达最后一个圆 */
  right: 20px;
  width: calc(100% - 40px);
}

.step-content {
  padding: 0 30px 30px;
  height: calc(100% - 200px);
  overflow-y: auto;
}

.step-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.step-title {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 20px;
  font-weight: bold;
  color: #00c9ff;
}

.step-title:has(.config-select) {
  justify-content: space-between;
}

.step-title-left {
  display: flex;
  align-items: center;
}

.arrow {
  margin-right: 10px;
  font-size: 18px;
}

.config-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  cursor: pointer;
  min-width: 200px;
}

.config-select option {
  background: #0a2d5e;
  color: white;
}

.algorithm-options {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.algorithm-card {
  flex: 1;
  padding: 20px;
  background: rgba(0, 160, 255, 0.1);
  border: 2px solid rgba(0, 160, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.algorithm-card:hover {
  border-color: rgba(0, 160, 255, 0.6);
}

.algorithm-card.selected {
  background: rgba(255, 193, 7, 0.2);
  border-color: #ffc107;
}

.algorithm-name {
  font-size: 16px;
  font-weight: bold;
  text-align: center;
}

.check-icon {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 20px;
  height: 20px;
  background: #28a745;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.objectives-container {
  margin-bottom: 20px;
}

.objectives-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.objective-section {
  background: rgba(0, 160, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 15px;
  text-align: center;
}

.objective-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.target-input {
  width: 80px;
  padding: 5px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  text-align: center;
}

.target-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.weight-input {
  width: 60px;
  padding: 5px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  text-align: center;
}

.weight-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.unit {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

/* 表格样式 */
.objectives-table {
  width: 100%;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 15px;
}

.header-cell {
  color: #00c9ff;
  font-size: 14px;
  font-weight: bold;
  text-align: center;
  padding: 8px;
  background: rgba(0, 160, 255, 0.1);
  border-radius: 6px;
}

.table-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  align-items: center;
}

.cell {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  min-height: 40px;
}

.cell span {
  color: white;
  font-size: 14px;
}

/* 经济模式设置 */
.economic-mode-setting {
  padding: 15px;
}

.economic-mode-row {
  display: flex;
  align-items: center;
  gap: 15px;
  justify-content: center;
}

.economic-mode-label {
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.economic-mode-status {
  color: #00c9ff;
  font-size: 14px;
  font-weight: bold;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.3);
  transition: 0.3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

.switch input:checked + .slider {
  background-color: #00c9ff;
}

.switch input:disabled + .slider {
  opacity: 0.5;
  cursor: not-allowed;
}

.switch input:checked + .slider:before {
  transform: translateX(26px);
}

.objectives-note {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
  margin-bottom: 30px;
}

.parameters-selection {
  margin-bottom: 30px;
}

.parameter-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.parameter-card {
  padding: 15px;
  background: rgba(0, 160, 255, 0.1);
  border: 2px solid rgba(0, 160, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  text-align: center;
}

.parameter-card:hover {
  border-color: rgba(0, 160, 255, 0.6);
}

.parameter-card.selected {
  background: rgba(255, 193, 7, 0.2);
  border-color: #ffc107;
}

.parameter-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.parameter-name {
  font-size: 14px;
  font-weight: bold;
}

.parameter-note {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
}

.optimization-progress {
  margin-bottom: 30px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00c9ff, #007bff);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  font-size: 16px;
  font-weight: bold;
  color: #00c9ff;
}

.optimization-data {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.data-section {
  background: rgba(0, 160, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
}

.data-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.value {
  color: #00c9ff;
  font-weight: bold;
}

.chart-container {
  display: flex;
  height: 400px;
  gap: 20px;
}

.chart-params {
  width: 200px;
  background: rgba(0, 160, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
}

.param-title {
  font-size: 16px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 15px;
  text-align: center;
}

.param-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-item {
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
  position: relative;
}

.param-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.param-item.selected {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.chart-area {
  flex: 1;
  background: rgba(0, 160, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
}

.algorithm-info {
  font-size: 14px;
  color: #00c9ff;
  margin-bottom: 15px;
  text-align: center;
}

.charts {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chart-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 8px;
}

.chart-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  text-align: center;
}

.chart-placeholder {
  height: 60px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: auto;
}

.step-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.next-btn,
.view-chart-btn,
.view-result-btn {
  background: #007bff;
  color: white;
}

.next-btn:hover,
.view-chart-btn:hover,
.view-result-btn:hover {
  background: #0056b3;
}

.prev-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.prev-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.start-btn {
  background: #28a745;
  color: white;
}

.start-btn:hover {
  background: #1e7e34;
}

.stop-btn {
  background: #dc3545;
  color: white;
}

.stop-btn:hover {
  background: #c82333;
}

.reconfigure-btn {
  background: #ffc107;
  color: #212529;
}

.reconfigure-btn:hover {
  background: #e0a800;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 第六步样式 */
.result-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.summary-section {
  background: rgba(0, 160, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.summary-item .value {
  color: #00c9ff;
  font-weight: bold;
}

.complete-btn {
  background: #28a745;
  color: white;
}

/* AAO在线优化结果样式 */
.aao-result-details {
  margin-top: 0;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 25px;
  border: 2px solid #10b981;
}

.aao-result-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  width: 100%;
}

.aao-result-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.aao-result-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
  border-left: 3px solid #4f46e5;
}

.aao-section-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 201, 255, 0.3);
}

.aao-section-title .arrow {
  margin-right: 8px;
  font-size: 16px;
  color: #00c9ff;
}

.aao-param-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  margin-bottom: 10px;
  width: 100%;
  min-width: 0;
}

.aao-param-row label {
  font-size: 13px;
  color: #ffffff;
  min-width: 140px;
  flex-shrink: 0;
  white-space: nowrap;
}

.aao-param-row .param-value {
  font-size: 13px;
  color: #10b981;
  font-weight: bold;
  min-width: 80px;
  text-align: right;
  flex-shrink: 0;
}

.aao-param-row .param-unit {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 45px;
  flex-shrink: 0;
}

.aao-bioreactor-group {
  margin-bottom: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
}

.aao-bioreactor-title {
  font-size: 13px;
  color: #ffffff;
  font-weight: bold;
  margin-bottom: 8px;
  padding-bottom: 5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.complete-btn:hover {
  background: #1e7e34;
}
</style>
