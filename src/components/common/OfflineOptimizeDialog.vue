<template>
  <div class="offline-optimize-mask" @click.self="$emit('close')">
    <div class="offline-optimize-dialog" @click.stop>
      <!-- 标题栏 -->
      <div class="dialog-header">
        <div class="offtitle">离线模式——{{ props.processType }}优化</div>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <!-- 进度条 -->
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

      <!-- 内容区域 -->
      <div class="dialog-content">
        <!-- 步骤1: 离线数据周期和数据类别选择 -->
        <div v-if="currentStep === 1" class="step-content">
          <div class="step-title">
            <div class="step-title-left">
              <span class="arrow">→</span>
              选择离线数据周期和数据类别
            </div>
          </div>
          <div class="data-settings">
            <div class="form-row">
              <label>开始时间:</label>
              <input
                type="datetime-local"
                v-model="optimizeData.startTime"
                class="datetime-input"
              />
            </div>
            <div class="form-row">
              <label>结束时间:</label>
              <input
                type="datetime-local"
                v-model="optimizeData.endTime"
                class="datetime-input"
              />
            </div>
            <div class="form-row">
              <label>数据类型:</label>
              <div class="radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    value="1"
                    v-model="optimizeData.dataSource"
                  />
                  <span>原始数据</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    value="2"
                    v-model="optimizeData.dataSource"
                  />
                  <span>清洗数据</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    value="3"
                    v-model="optimizeData.dataSource"
                  />
                  <span>实验数据</span>
                </label>
              </div>
            </div>
            <div class="form-row">
              <label>运行频率:</label>
              <input
                type="number"
                v-model.number="optimizeData.frequency"
                class="number-input"
                placeholder="默认120"
              />
            </div>
            <div class="form-row">
              <label>迭代次数:</label>
              <input
                type="number"
                v-model.number="optimizeData.psoIter"
                class="number-input"
                placeholder="默认10"
              />
            </div>
            <div class="form-row">
              <label>种群大小:</label>
              <input
                type="number"
                v-model.number="optimizeData.size"
                class="number-input"
                placeholder="默认15"
              />
            </div>
            <div class="form-row">
              <label>模拟预测步长:</label>
              <input
                type="number"
                v-model.number="optimizeData.mpcSteps"
                class="number-input"
                placeholder="默认3"
              />
            </div>
          </div>
        </div>

        <!-- 步骤2: 选择优化算法 -->
        <div v-if="currentStep === 2" class="step-content">
          <div class="step-title">
            <div class="step-title-left">
              <span class="arrow">→</span>
              选择优化算法
            </div>
          </div>
          <div class="algorithm-selection">
            <div
              v-for="algorithm in algorithms"
              :key="algorithm.id"
              class="algorithm-card"
              :class="{ selected: selectedAlgorithm === algorithm.id }"
              @click="selectAlgorithm(algorithm.id)"
            >
              <div class="algorithm-name">{{ algorithm.name }}</div>
              <div class="algorithm-desc">{{ algorithm.description }}</div>
              <div v-if="selectedAlgorithm === algorithm.id" class="check-icon">
                ✓
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤3: 选择优化目标 -->
        <div v-if="currentStep === 3" class="step-content">
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
            <select
              v-else-if="processType === 'MBR'"
              v-model="optimizeData.mbrConfigName"
              class="config-select"
              @change="handleConfigChange"
            >
              <option value="">请选择参数配置</option>
              <option value="mbr_nh4">跟踪氨氮 (mbr_nh4)</option>
              <option value="mbr_tn_economy">经济总氮 (mbr_tn_economy)</option>
            </select>
          </div>
          <div class="objectives-container">
            <!-- 出水指标及权重比设置 -->
            <div class="objectives-section">
              <div class="section-header">
                <span class="section-icon">▶</span>
                <span class="section-title">出水指标及权重比设置</span>
                <div class="aao-label"></div>
              </div>
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

            <!-- 经济消耗指标及目标值 -->
            <div class="objectives-section">
              <div class="section-header">
                <span class="section-icon">▶</span>
                <span class="section-title">经济消耗指标及目标值</span>
              </div>
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
          <div class="objectives-note">
            优化指标可多选, 可单选; 其中出水指标的权重比例默加=1;
          </div>
        </div>

        <!-- 步骤4: 设置优化参数 -->
        <div v-if="currentStep === 4" class="step-content">
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
        </div>

        <!-- 步骤5: 设置参数范围 -->
        <div v-if="currentStep === 5" class="step-content">
          <div class="step-title">
            <div class="step-title-left">
              <span class="arrow">→</span>
              设置参数范围
            </div>
          </div>
          <div v-if="processType === 'AAO'" class="parameter-ranges-container">
            <div v-if="isConfigSelected" class="config-note">
              已选择参数配置，无需设置参数范围
            </div>
            <div v-else>
              <div
                v-for="paramId in selectedParameters"
                :key="paramId"
                class="parameter-range-section"
              >
                <div class="parameter-range-title">
                  {{
                    aaoParamOptions.find((p) => p.id === paramId)?.name ||
                    paramId
                  }}
                </div>
                <div class="parameter-range-table">
                  <div class="range-table-header">
                    <div class="header-cell">参数名称</div>
                    <div class="header-cell">上限</div>
                    <div class="header-cell">下限</div>
                  </div>
                  <div class="range-table-body">
                    <div
                      v-for="(label, index) in parameterFieldMapping[paramId]
                        ?.labels || []"
                      :key="index"
                      class="range-table-row"
                    >
                      <div class="range-cell">{{ label }}</div>
                      <div class="range-cell">
                        <div class="range-input-wrapper">
                          <input
                            type="number"
                            :value="
                              parameterRanges[`${paramId}_${index}`]?.upper ??
                              null
                            "
                            @input="
                              (e) => {
                                const fieldKey = `${paramId}_${index}`;
                                const upperFieldName =
                                  parameterFieldMapping[paramId]?.upperFields[
                                    index
                                  ];
                                if (!parameterRanges[fieldKey]) {
                                  parameterRanges[fieldKey] = {
                                    upper: null,
                                    lower: null,
                                  };
                                }
                                const inputValue = e.target.value
                                  ? parseFloat(e.target.value)
                                  : null;

                                // 先更新值
                                parameterRanges[fieldKey].upper = inputValue;

                                // 然后验证
                                if (!rangeValidationErrors[fieldKey]) {
                                  rangeValidationErrors[fieldKey] = {};
                                }

                                if (inputValue !== null && upperFieldName) {
                                  const validation = validateFieldValue(
                                    upperFieldName,
                                    inputValue,
                                    true
                                  );
                                  if (!validation.valid) {
                                    rangeValidationErrors[fieldKey].upper =
                                      validation.message;
                                  } else {
                                    // 验证上限必须大于下限
                                    const currentLower =
                                      parameterRanges[fieldKey].lower;
                                    if (
                                      currentLower !== null &&
                                      inputValue <= currentLower
                                    ) {
                                      rangeValidationErrors[fieldKey].upper =
                                        '上限必须大于下限';
                                    } else {
                                      rangeValidationErrors[fieldKey].upper =
                                        undefined;
                                    }
                                  }
                                } else {
                                  rangeValidationErrors[fieldKey].upper =
                                    undefined;
                                }
                              }
                            "
                            :class="[
                              'range-input',
                              {
                                'range-input-error':
                                  rangeValidationErrors[`${paramId}_${index}`]
                                    ?.upper,
                              },
                            ]"
                            placeholder="上限"
                            step="0.01"
                          />
                          <div
                            v-if="
                              rangeValidationErrors[`${paramId}_${index}`]
                                ?.upper
                            "
                            class="range-error-tip"
                          >
                            {{
                              rangeValidationErrors[`${paramId}_${index}`].upper
                            }}
                          </div>
                        </div>
                      </div>
                      <div class="range-cell">
                        <div class="range-input-wrapper">
                          <input
                            type="number"
                            :value="
                              parameterRanges[`${paramId}_${index}`]?.lower ??
                              null
                            "
                            @input="
                              (e) => {
                                const fieldKey = `${paramId}_${index}`;
                                const lowerFieldName =
                                  parameterFieldMapping[paramId]?.lowerFields[
                                    index
                                  ];
                                if (!parameterRanges[fieldKey]) {
                                  parameterRanges[fieldKey] = {
                                    upper: null,
                                    lower: null,
                                  };
                                }
                                const inputValue = e.target.value
                                  ? parseFloat(e.target.value)
                                  : null;

                                // 先更新值
                                parameterRanges[fieldKey].lower = inputValue;

                                // 然后验证
                                if (!rangeValidationErrors[fieldKey]) {
                                  rangeValidationErrors[fieldKey] = {};
                                }

                                if (inputValue !== null && lowerFieldName) {
                                  const validation = validateFieldValue(
                                    lowerFieldName,
                                    inputValue,
                                    false
                                  );
                                  if (!validation.valid) {
                                    rangeValidationErrors[fieldKey].lower =
                                      validation.message;
                                  } else {
                                    // 验证下限必须小于上限
                                    const currentUpper =
                                      parameterRanges[fieldKey].upper;
                                    if (
                                      currentUpper !== null &&
                                      inputValue >= currentUpper
                                    ) {
                                      rangeValidationErrors[fieldKey].lower =
                                        '下限必须小于上限';
                                    } else {
                                      rangeValidationErrors[fieldKey].lower =
                                        undefined;
                                    }
                                  }
                                } else {
                                  rangeValidationErrors[fieldKey].lower =
                                    undefined;
                                }
                              }
                            "
                            :class="[
                              'range-input',
                              {
                                'range-input-error':
                                  rangeValidationErrors[`${paramId}_${index}`]
                                    ?.lower,
                              },
                            ]"
                            placeholder="下限"
                            step="0.01"
                          />
                          <div
                            v-if="
                              rangeValidationErrors[`${paramId}_${index}`]
                                ?.lower
                            "
                            class="range-error-tip"
                          >
                            {{
                              rangeValidationErrors[`${paramId}_${index}`].lower
                            }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤6: 生成优化结果 -->
        <div v-if="currentStep === 6" class="step-content">
          <div class="step-title">
            <div class="step-title-left">
              <span class="arrow">→</span>
              生成优化结果
            </div>
          </div>
          <div class="results-content">
            <div v-if="isRunning" class="loading-section">
              <div class="loading-spinner"></div>
              <div class="loading-text">优化进行中...</div>
              <div class="progress-info">
                <div class="progress-bar-mini">
                  <div
                    class="progress-fill"
                    :style="{ width: progress + '%' }"
                  ></div>
                </div>
                <div class="progress-text">{{ progress.toFixed(1) }}%</div>
              </div>
            </div>
            <div v-else-if="optimizeResult" class="result-section">
              <!-- AAO优化结果详情 -->
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
                          getFieldValue("aao_influent_1_q_or") || "—"
                        }}</span>
                        <span class="param-unit">m³/d</span>
                      </div>
                      <div class="aao-param-row">
                        <label>2#AAO生化池进水流量:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_influent_2_q_or") || "—"
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
                          getFieldValue("aao_effluent_q_or") || "—"
                        }}</span>
                        <span class="param-unit">m³/d</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水化学需氧量:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_effluent_tcod_or") || "—"
                        }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水生化需氧量:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_effluent_tbod_or") || "—"
                        }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水悬浮固体浓度:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_effluent_ss_or") || "—"
                        }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水总磷:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_effluent_tp_or") || "—"
                        }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水总氮:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_effluent_tn_or") || "—"
                        }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水氨氮:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_effluent_snhx_or") || "—"
                        }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水硝氮:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_effluent_snox_or") || "—"
                        }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水正磷酸盐:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_effluent_spo4_or") || "—"
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
                          getFieldValue("aao_pac_q_or") || "—"
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
                          getFieldValue("aao_ras_1_q_or") || "—"
                        }}</span>
                        <span class="param-unit">m³/d</span>
                      </div>
                      <div class="aao-param-row">
                        <label>2#回流污泥流量:</label>
                        <span class="param-value">{{
                          getFieldValue("aao_ras_2_q_or") || "—"
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
                            getFieldValue("aao_cstr3_1_1_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段2曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr4_1_1_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段3曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr5_1_1_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段4曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr6_1_1_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段5曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr7_1_1_qair_ntp_or") || "—"
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
                            getFieldValue("aao_cstr3_1_2_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段2曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr4_1_2_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段3曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr5_1_2_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段4曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr6_1_2_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段5曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr7_1_2_qair_ntp_or") || "—"
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
                            getFieldValue("aao_cstr3_2_1_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段2曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr4_2_1_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段3曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr5_2_1_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段4曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr6_2_1_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段5曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr7_2_1_qair_ntp_or") || "—"
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
                            getFieldValue("aao_cstr3_2_2_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段2曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr4_2_2_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段3曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr5_2_2_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段4曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr6_2_2_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段5曝气量:</label>
                          <span class="param-value">{{
                            getFieldValue("aao_cstr7_2_2_qair_ntp_or") || "—"
                          }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 其他工艺类型的优化结果详情 -->
              <div
                v-else-if="optimizeResultData && processType !== 'AAO'"
                class="result-details"
              >
                <div class="details-title">优化结果详情</div>
                <div class="details-content">
                  <div class="result-category">
                    <div class="category-title">出水指标优化结果</div>
                    <div class="category-items">
                      <div class="result-item">
                        <span class="item-label">COD:</span>
                        <span class="item-value">{{
                          optimizeResultData.cod || "--"
                        }}</span>
                        <span class="item-unit">mg/L</span>
                      </div>
                      <div class="result-item">
                        <span class="item-label">NH3-N:</span>
                        <span class="item-value">{{
                          optimizeResultData.nh3n || "--"
                        }}</span>
                        <span class="item-unit">mg/L</span>
                      </div>
                      <div class="result-item">
                        <span class="item-label">TN:</span>
                        <span class="item-value">{{
                          optimizeResultData.tn || "--"
                        }}</span>
                        <span class="item-unit">mg/L</span>
                      </div>
                    </div>
                  </div>
                  <div class="result-category">
                    <div class="category-title">经济指标优化结果</div>
                    <div class="category-items">
                      <div class="result-item">
                        <span class="item-label">经济成本:</span>
                        <span class="item-value">{{
                          optimizeResultData.economicCost || "--"
                        }}</span>
                        <span class="item-unit">%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤7: 优化结果对比图 -->
        <div v-if="currentStep === 7" class="step-content">
          <div class="step-title">
            <span class="arrow">→</span>
            优化结果对比图
          </div>
          <div class="chart-container">
            <!-- 左侧参数选择 -->
            <div class="chart-params-panel">
              <div class="params-title">
                <span class="arrow">→</span>
                图表参数
              </div>
              <div class="params-categories">
                <div
                  v-for="category in Object.keys(categoryFieldsMap)"
                  :key="category"
                  class="category-item"
                  :class="{ active: selectedCategory === category }"
                  @click="selectedCategory = category"
                >
                  <span>{{ category }}</span>
                </div>
              </div>
              <button class="btn-refresh" @click="loadChartData">
                刷新图表
              </button>
            </div>

            <!-- 右侧图表 -->
            <div class="chart-display-panel">
              <div v-if="chartLoading" class="chart-loading">
                <div class="loading-spinner"></div>
                <div class="loading-text">加载图表数据中...</div>
              </div>
              <div v-else-if="chartError" class="chart-error">
                <div class="error-text">{{ chartError }}</div>
                <button class="btn-retry" @click="loadChartData">重试</button>
              </div>
              <div v-else-if="!selectedCategory" class="chart-empty">
                <div class="empty-text">请从左侧选择要查看的图表参数类别</div>
              </div>
              <div v-else class="charts-grid">
                <div
                  v-for="(fieldName, fieldIndex) in categoryFieldsMap[
                    selectedCategory
                  ]"
                  :key="`${selectedCategory}-${fieldIndex}`"
                  class="chart-item"
                >
                  <div class="chart-title">
                    {{ fieldDisplayNames[fieldName] || fieldName }}
                  </div>
                  <div
                    :id="`chart-${selectedCategory}-${fieldIndex}`"
                    class="chart-canvas-item"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="dialog-footer">
        <button
          v-if="currentStep > 1"
          class="btn btn-secondary"
          @click="prevStep"
        >
          上一步
        </button>
        <button
          v-if="currentStep < 6"
          class="btn btn-primary"
          @click="nextStep"
          :disabled="!canProceed"
        >
          下一步
        </button>
        <button
          v-if="currentStep === 6 && !isRunning"
          class="btn btn-primary"
          @click="startOptimization"
        >
          开始优化
        </button>
        <button
          v-if="currentStep === 6 && isRunning"
          class="btn btn-danger"
          @click="stopOptimization"
        >
          停止优化
        </button>
        <button
          v-if="currentStep === 6 && !isRunning && optimizeResult"
          class="btn btn-chart"
          @click="nextStep"
        >
          查看图表
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, nextTick, onBeforeUnmount } from "vue";
import {
  aaoSimulationService,
  type OptimizationRequest,
} from "@/api/aaoSimulation";
import { updateSystemParams } from "@/api/systemParams";
import * as echarts from "echarts";

// Props
const props = defineProps<{
  processType: "AAO" | "MBR";
}>();

// Emits
const emit = defineEmits<{
  close: [];
  complete: [result: any];
}>();

// 响应式数据
const currentStep = ref(1);
const isRunning = ref(false);
const progress = ref(0);
const optimizeResult = ref<any>(null);
const optimizeResultData = ref<any>(null);
const selectedAlgorithm = ref<string>("");
const selectedParameters = ref<string[]>([]);

// 参数范围数据
const parameterRanges = reactive<
  Record<string, { upper: number | null; lower: number | null }>
>({});

// 参数ID到数据库字段名的映射（根据用户提供的字段列表）
const parameterFieldMapping: Record<
  string,
  { upperFields: string[]; lowerFields: string[]; labels: string[] }
> = {
  aeration: {
    upperFields: [
      "upper_limit_aao_cstr_front_1_1_qair_ntp_sp",
      "upper_limit_aao_cstr_mid_1_1_qair_ntp_sp",
      "upper_limit_aao_cstr_terminal_1_1_qair_ntp_sp",
      "upper_limit_aao_cstr_front_1_2_qair_ntp_sp",
      "upper_limit_aao_cstr_mid_1_2_qair_ntp_sp",
      "upper_limit_aao_cstr_terminal_1_2_qair_ntp_sp",
      "upper_limit_aao_cstr_front_2_1_qair_ntp_sp",
      "upper_limit_aao_cstr_mid_2_1_qair_ntp_sp",
      "upper_limit_aao_cstr_terminal_2_1_qair_ntp_sp",
      "upper_limit_aao_cstr_front_2_2_qair_ntp_sp",
      "upper_limit_aao_cstr_mid_2_2_qair_ntp_sp",
      "upper_limit_aao_cstr_terminal_2_2_qair_ntp_sp",
    ],
    lowerFields: [
      "lower_limit_aao_cstr_front_1_1_qair_ntp_sp",
      "lower_limit_aao_cstr_mid_1_1_qair_ntp_sp",
      "lower_limit_aao_cstr_terminal_1_1_qair_ntp_sp",
      "lower_limit_aao_cstr_front_1_2_qair_ntp_sp",
      "lower_limit_aao_cstr_mid_1_2_qair_ntp_sp",
      "lower_limit_aao_cstr_terminal_1_2_qair_ntp_sp",
      "lower_limit_aao_cstr_front_2_1_qair_ntp_sp",
      "lower_limit_aao_cstr_mid_2_1_qair_ntp_sp",
      "lower_limit_aao_cstr_terminal_2_1_qair_ntp_sp",
      "lower_limit_aao_cstr_front_2_2_qair_ntp_sp",
      "lower_limit_aao_cstr_mid_2_2_qair_ntp_sp",
      "lower_limit_aao_cstr_terminal_2_2_qair_ntp_sp",
    ],
    labels: [
      "1-1#AAO好氧池曝气支管1",
      "1-1#AAO好氧池曝气支管2",
      "1-1#AAO好氧池曝气支管3",
      "1-2#AAO好氧池曝气支管1",
      "1-2#AAO好氧池曝气支管2",
      "1-2#AAO好氧池曝气支管3",
      "2-1#AAO好氧池曝气支管1",
      "2-1#AAO好氧池曝气支管2",
      "2-1#AAO好氧池曝气支管3",
      "2-2#AAO好氧池曝气支管1",
      "2-2#AAO好氧池曝气支管2",
      "2-2#AAO好氧池曝气支管3",
    ],
  },
  sludgeDischarge: {
    upperFields: [
      "upper_limit_aao_flowdivider3_1_sludge_q_sp",
      "upper_limit_aao_flowdivider3_2_sludge_q_sp",
    ],
    lowerFields: [
      "lower_limit_aao_flowdivider3_1_sludge_q_sp",
      "lower_limit_aao_flowdivider3_2_sludge_q_sp",
    ],
    labels: ["1号AAO生物池剩余污泥量", "2号AAO生物池剩余污泥量"],
  },
  internalRecycle: {
    upperFields: [
      "upper_limit_aao_flowdivider3_1_1_influx_sp",
      "upper_limit_aao_flowdivider3_1_2_influx_sp",
      "upper_limit_aao_flowdivider3_2_1_influx_sp",
      "upper_limit_aao_flowdivider3_2_2_influx_sp",
    ],
    lowerFields: [
      "lower_limit_aao_flowdivider3_1_1_influx_sp",
      "lower_limit_aao_flowdivider3_1_2_influx_sp",
      "lower_limit_aao_flowdivider3_2_1_influx_sp",
      "lower_limit_aao_flowdivider3_2_2_influx_sp",
    ],
    labels: [
      "1-1#AAO生物池内回流量",
      "1-2#AAO生物池内回流量",
      "2-1#AAO生物池内回流量",
      "2-2#AAO生物池内回流量",
    ],
  },
  externalRecycle: {
    upperFields: [
      "upper_limit_aao_clarifier_1_sludge_target_q_sp",
      "upper_limit_aao_clarifier_2_sludge_target_q_sp",
    ],
    lowerFields: [
      "lower_limit_aao_clarifier_1_sludge_target_q_sp",
      "lower_limit_aao_clarifier_2_sludge_target_q_sp",
    ],
    labels: ["1号AAO生物池污泥回流量", "2号AAO生物池污泥回流量"],
  },
  multiInlet: {
    upperFields: [
      "upper_limit_aao_influent_q_1_1_frselect_tol_sp",
      "upper_limit_aao_influent_q_1_1_franaerobic_anoxic_sp",
      "upper_limit_aao_influent_q_1_2_frselect_tol_sp",
      "upper_limit_aao_influent_q_1_2_franaerobic_anoxic_sp",
      "upper_limit_aao_influent_q_2_1_frselect_tol_sp",
      "upper_limit_aao_influent_q_2_1_franaerobic_anoxic_sp",
      "upper_limit_aao_influent_q_2_2_frselect_tol_sp",
      "upper_limit_aao_influent_q_2_2_franaerobic_anoxic_sp",
    ],
    lowerFields: [
      "lower_limit_aao_influent_q_1_1_frselect_tol_sp",
      "lower_limit_aao_influent_q_1_1_franaerobic_anoxic_sp",
      "lower_limit_aao_influent_q_1_2_frselect_tol_sp",
      "lower_limit_aao_influent_q_1_2_franaerobic_anoxic_sp",
      "lower_limit_aao_influent_q_2_1_frselect_tol_sp",
      "lower_limit_aao_influent_q_2_1_franaerobic_anoxic_sp",
      "lower_limit_aao_influent_q_2_2_frselect_tol_sp",
      "lower_limit_aao_influent_q_2_2_franaerobic_anoxic_sp",
    ],
    labels: [
      "1-1#AAO选择池进水水量与总进水水量比例",
      "1-1#AAO缺氧池进水水量与厌氧池进水水量比例",
      "1-2#AAO选择池进水水量与总进水水量比例",
      "1-2#AAO缺氧池进水水量与厌氧池进水水量比例",
      "2-1#AAO选择池进水水量与总进水水量比例",
      "2-1#AAO缺氧池进水水量与厌氧池进水水量比例",
      "2-2#AAO选择池进水水量与总进水水量比例",
      "2-2#AAO缺氧池进水水量与厌氧池进水水量比例",
    ],
  },
  do: {
    upperFields: [
      "upper_limit_aao_cstr3_1_1_so2_sp",
      "upper_limit_aao_cstr4_1_1_so2_sp",
      "upper_limit_aao_cstr5_1_1_so2_sp",
      "upper_limit_aao_cstr6_1_1_so2_sp",
      "upper_limit_aao_cstr7_1_1_so2_sp",
      "upper_limit_aao_cstr3_1_2_so2_sp",
      "upper_limit_aao_cstr4_1_2_so2_sp",
      "upper_limit_aao_cstr5_1_2_so2_sp",
      "upper_limit_aao_cstr6_1_2_so2_sp",
      "upper_limit_aao_cstr7_1_2_so2_sp",
      "upper_limit_aao_cstr3_2_1_so2_sp",
      "upper_limit_aao_cstr4_2_1_so2_sp",
      "upper_limit_aao_cstr5_2_1_so2_sp",
      "upper_limit_aao_cstr6_2_1_so2_sp",
      "upper_limit_aao_cstr7_2_1_so2_sp",
      "upper_limit_aao_cstr3_2_2_so2_sp",
      "upper_limit_aao_cstr4_2_2_so2_sp",
      "upper_limit_aao_cstr5_2_2_so2_sp",
      "upper_limit_aao_cstr6_2_2_so2_sp",
      "upper_limit_aao_cstr7_2_2_so2_sp",
    ],
    lowerFields: [
      "lower_limit_aao_cstr3_1_1_so2_sp",
      "lower_limit_aao_cstr4_1_1_so2_sp",
      "lower_limit_aao_cstr5_1_1_so2_sp",
      "lower_limit_aao_cstr6_1_1_so2_sp",
      "lower_limit_aao_cstr7_1_1_so2_sp",
      "lower_limit_aao_cstr3_1_2_so2_sp",
      "lower_limit_aao_cstr4_1_2_so2_sp",
      "lower_limit_aao_cstr5_1_2_so2_sp",
      "lower_limit_aao_cstr6_1_2_so2_sp",
      "lower_limit_aao_cstr7_1_2_so2_sp",
      "lower_limit_aao_cstr3_2_1_so2_sp",
      "lower_limit_aao_cstr4_2_1_so2_sp",
      "lower_limit_aao_cstr5_2_1_so2_sp",
      "lower_limit_aao_cstr6_2_1_so2_sp",
      "lower_limit_aao_cstr7_2_1_so2_sp",
      "lower_limit_aao_cstr3_2_2_so2_sp",
      "lower_limit_aao_cstr4_2_2_so2_sp",
      "lower_limit_aao_cstr5_2_2_so2_sp",
      "lower_limit_aao_cstr6_2_2_so2_sp",
      "lower_limit_aao_cstr7_2_2_so2_sp",
    ],
    labels: [
      "1-1#AAO好氧池1号廊道DO",
      "1-1#AAO好氧池2号廊道DO",
      "1-1#AAO好氧池3号廊道DO",
      "1-1#AAO好氧池4号廊道DO",
      "1-1#AAO好氧池5号廊道DO",
      "1-2#AAO好氧池1号廊道DO",
      "1-2#AAO好氧池2号廊道DO",
      "1-2#AAO好氧池3号廊道DO",
      "1-2#AAO好氧池4号廊道DO",
      "1-2#AAO好氧池5号廊道DO",
      "2-1#AAO好氧池1号廊道DO",
      "2-1#AAO好氧池2号廊道DO",
      "2-1#AAO好氧池3号廊道DO",
      "2-1#AAO好氧池4号廊道DO",
      "2-1#AAO好氧池5号廊道DO",
      "2-2#AAO好氧池1号廊道DO",
      "2-2#AAO好氧池2号廊道DO",
      "2-2#AAO好氧池3号廊道DO",
      "2-2#AAO好氧池4号廊道DO",
      "2-2#AAO好氧池5号廊道DO",
    ],
  },
  pac: {
    upperFields: [
      "upper_limit_aao_pac_1_1_q_sp",
      "upper_limit_aao_pac_1_2_q_sp",
      "upper_limit_aao_pac_2_1_q_sp",
      "upper_limit_aao_pac_2_2_q_sp",
      "upper_limit_aao_pac_q_sp",
    ],
    lowerFields: [
      "lower_limit_aao_pac_1_1_q_sp",
      "lower_limit_aao_pac_1_2_q_sp",
      "lower_limit_aao_pac_2_1_q_sp",
      "lower_limit_aao_pac_2_2_q_sp",
      "lower_limit_aao_pac_q_sp",
    ],
    labels: [
      "1-1#AAO好氧池末端PAC投加量",
      "1-2#AAO好氧池末端PAC投加量",
      "2-1#AAO好氧池末端PAC投加量",
      "2-2#AAO好氧池末端PAC投加量",
      "高效沉淀池PAC投加量",
    ],
  },
  carbonSource: {
    upperFields: [
      "upper_limit_aao_carbon_1_1_q_sp",
      "upper_limit_aao_carbon_1_2_q_sp",
      "upper_limit_aao_carbon_2_1_q_sp",
      "upper_limit_aao_carbon_2_2_q_sp",
    ],
    lowerFields: [
      "lower_limit_aao_carbon_1_1_q_sp",
      "lower_limit_aao_carbon_1_2_q_sp",
      "lower_limit_aao_carbon_2_1_q_sp",
      "lower_limit_aao_carbon_2_2_q_sp",
    ],
    labels: [
      "1-1#AAO碳源投加量",
      "1-2#AAO碳源投加量",
      "2-1#AAO碳源投加量",
      "2-2#AAO碳源投加量",
    ],
  },
  sludgeConcentration: {
    upperFields: [
      "upper_limit_aao_cstr7_1_1_xtss_sp",
      "upper_limit_aao_cstr7_1_2_xtss_sp",
      "upper_limit_aao_cstr7_2_1_xtss_sp",
      "upper_limit_aao_cstr7_2_2_xtss_sp",
    ],
    lowerFields: [
      "lower_limit_aao_cstr7_1_1_xtss_sp",
      "lower_limit_aao_cstr7_1_2_xtss_sp",
      "lower_limit_aao_cstr7_2_1_xtss_sp",
      "lower_limit_aao_cstr7_2_2_xtss_sp",
    ],
    labels: [
      "1-1#AAO生物池MLSS",
      "1-2#AAO生物池MLSS",
      "2-1#AAO生物池MLSS",
      "2-2#AAO生物池MLSS",
    ],
  },
};

// 字段上下限范围定义（用于验证和设置默认值）
const fieldRangeLimits: Record<string, { maxUpper: number; minLower: number }> =
  {
    // 曝气量
    upper_limit_aao_cstr_front_1_1_qair_ntp_sp: {
      maxUpper: 9600,
      minLower: 1000,
    },
    lower_limit_aao_cstr_front_1_1_qair_ntp_sp: {
      maxUpper: 9600,
      minLower: 1000,
    },
    upper_limit_aao_cstr_mid_1_1_qair_ntp_sp: {
      maxUpper: 4800,
      minLower: 1000,
    },
    lower_limit_aao_cstr_mid_1_1_qair_ntp_sp: {
      maxUpper: 4800,
      minLower: 1000,
    },
    upper_limit_aao_cstr_terminal_1_1_qair_ntp_sp: {
      maxUpper: 2400,
      minLower: 500,
    },
    lower_limit_aao_cstr_terminal_1_1_qair_ntp_sp: {
      maxUpper: 2400,
      minLower: 500,
    },
    upper_limit_aao_cstr_front_1_2_qair_ntp_sp: {
      maxUpper: 9600,
      minLower: 1000,
    },
    lower_limit_aao_cstr_front_1_2_qair_ntp_sp: {
      maxUpper: 9600,
      minLower: 1000,
    },
    upper_limit_aao_cstr_mid_1_2_qair_ntp_sp: {
      maxUpper: 4800,
      minLower: 1000,
    },
    lower_limit_aao_cstr_mid_1_2_qair_ntp_sp: {
      maxUpper: 4800,
      minLower: 1000,
    },
    upper_limit_aao_cstr_terminal_1_2_qair_ntp_sp: {
      maxUpper: 2400,
      minLower: 500,
    },
    lower_limit_aao_cstr_terminal_1_2_qair_ntp_sp: {
      maxUpper: 2400,
      minLower: 500,
    },
    upper_limit_aao_cstr_front_2_1_qair_ntp_sp: {
      maxUpper: 9600,
      minLower: 1000,
    },
    lower_limit_aao_cstr_front_2_1_qair_ntp_sp: {
      maxUpper: 9600,
      minLower: 1000,
    },
    upper_limit_aao_cstr_mid_2_1_qair_ntp_sp: {
      maxUpper: 4800,
      minLower: 1000,
    },
    lower_limit_aao_cstr_mid_2_1_qair_ntp_sp: {
      maxUpper: 4800,
      minLower: 1000,
    },
    upper_limit_aao_cstr_terminal_2_1_qair_ntp_sp: {
      maxUpper: 2400,
      minLower: 500,
    },
    lower_limit_aao_cstr_terminal_2_1_qair_ntp_sp: {
      maxUpper: 2400,
      minLower: 500,
    },
    upper_limit_aao_cstr_front_2_2_qair_ntp_sp: {
      maxUpper: 9600,
      minLower: 1000,
    },
    lower_limit_aao_cstr_front_2_2_qair_ntp_sp: {
      maxUpper: 9600,
      minLower: 1000,
    },
    upper_limit_aao_cstr_mid_2_2_qair_ntp_sp: {
      maxUpper: 4800,
      minLower: 1000,
    },
    lower_limit_aao_cstr_mid_2_2_qair_ntp_sp: {
      maxUpper: 4800,
      minLower: 1000,
    },
    upper_limit_aao_cstr_terminal_2_2_qair_ntp_sp: {
      maxUpper: 2400,
      minLower: 500,
    },
    lower_limit_aao_cstr_terminal_2_2_qair_ntp_sp: {
      maxUpper: 2400,
      minLower: 500,
    },

    // 内回流
    upper_limit_aao_flowdivider3_1_1_influx_sp: {
      maxUpper: 13000,
      minLower: 2000,
    },
    lower_limit_aao_flowdivider3_1_1_influx_sp: {
      maxUpper: 13000,
      minLower: 2000,
    },
    upper_limit_aao_flowdivider3_1_2_influx_sp: {
      maxUpper: 13000,
      minLower: 2000,
    },
    lower_limit_aao_flowdivider3_1_2_influx_sp: {
      maxUpper: 13000,
      minLower: 2000,
    },
    upper_limit_aao_flowdivider3_2_1_influx_sp: {
      maxUpper: 13000,
      minLower: 2000,
    },
    lower_limit_aao_flowdivider3_2_1_influx_sp: {
      maxUpper: 13000,
      minLower: 2000,
    },
    upper_limit_aao_flowdivider3_2_2_influx_sp: {
      maxUpper: 13000,
      minLower: 2000,
    },
    lower_limit_aao_flowdivider3_2_2_influx_sp: {
      maxUpper: 13000,
      minLower: 2000,
    },

    // 外回流
    upper_limit_aao_clarifier_1_sludge_target_q_sp: {
      maxUpper: 12498,
      minLower: 4167,
    },
    lower_limit_aao_clarifier_1_sludge_target_q_sp: {
      maxUpper: 12498,
      minLower: 4167,
    },
    upper_limit_aao_clarifier_2_sludge_target_q_sp: {
      maxUpper: 12498,
      minLower: 4167,
    },
    lower_limit_aao_clarifier_2_sludge_target_q_sp: {
      maxUpper: 12498,
      minLower: 4167,
    },

    // 排泥
    upper_limit_aao_flowdivider3_1_sludge_q_sp: { maxUpper: 800, minLower: 0 },
    lower_limit_aao_flowdivider3_1_sludge_q_sp: { maxUpper: 800, minLower: 0 },
    upper_limit_aao_flowdivider3_2_sludge_q_sp: { maxUpper: 800, minLower: 0 },
    lower_limit_aao_flowdivider3_2_sludge_q_sp: { maxUpper: 800, minLower: 0 },

    // 多点进水比例
    upper_limit_aao_influent_q_1_1_frselect_tol_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    lower_limit_aao_influent_q_1_1_frselect_tol_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    upper_limit_aao_influent_q_1_1_franaerobic_anoxic_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    lower_limit_aao_influent_q_1_1_franaerobic_anoxic_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    upper_limit_aao_influent_q_1_2_frselect_tol_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    lower_limit_aao_influent_q_1_2_frselect_tol_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    upper_limit_aao_influent_q_1_2_franaerobic_anoxic_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    lower_limit_aao_influent_q_1_2_franaerobic_anoxic_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    upper_limit_aao_influent_q_2_1_frselect_tol_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    lower_limit_aao_influent_q_2_1_frselect_tol_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    upper_limit_aao_influent_q_2_1_franaerobic_anoxic_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    lower_limit_aao_influent_q_2_1_franaerobic_anoxic_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    upper_limit_aao_influent_q_2_2_frselect_tol_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    lower_limit_aao_influent_q_2_2_frselect_tol_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    upper_limit_aao_influent_q_2_2_franaerobic_anoxic_sp: {
      maxUpper: 1,
      minLower: 0,
    },
    lower_limit_aao_influent_q_2_2_franaerobic_anoxic_sp: {
      maxUpper: 1,
      minLower: 0,
    },

    // 碳源
    upper_limit_aao_carbon_1_1_q_sp: { maxUpper: 680, minLower: 0 },
    lower_limit_aao_carbon_1_1_q_sp: { maxUpper: 680, minLower: 0 },
    upper_limit_aao_carbon_1_2_q_sp: { maxUpper: 680, minLower: 0 },
    lower_limit_aao_carbon_1_2_q_sp: { maxUpper: 680, minLower: 0 },
    upper_limit_aao_carbon_2_1_q_sp: { maxUpper: 680, minLower: 0 },
    lower_limit_aao_carbon_2_1_q_sp: { maxUpper: 680, minLower: 0 },
    upper_limit_aao_carbon_2_2_q_sp: { maxUpper: 680, minLower: 0 },
    lower_limit_aao_carbon_2_2_q_sp: { maxUpper: 680, minLower: 0 },

    // PAC
    upper_limit_aao_pac_1_1_q_sp: { maxUpper: 440, minLower: 0 },
    lower_limit_aao_pac_1_1_q_sp: { maxUpper: 440, minLower: 0 },
    upper_limit_aao_pac_1_2_q_sp: { maxUpper: 440, minLower: 0 },
    lower_limit_aao_pac_1_2_q_sp: { maxUpper: 440, minLower: 0 },
    upper_limit_aao_pac_2_1_q_sp: { maxUpper: 440, minLower: 0 },
    lower_limit_aao_pac_2_1_q_sp: { maxUpper: 440, minLower: 0 },
    upper_limit_aao_pac_2_2_q_sp: { maxUpper: 440, minLower: 0 },
    lower_limit_aao_pac_2_2_q_sp: { maxUpper: 440, minLower: 0 },
    upper_limit_aao_pac_q_sp: { maxUpper: 6800, minLower: 0 },
    lower_limit_aao_pac_q_sp: { maxUpper: 6800, minLower: 0 },

    // MLSS
    upper_limit_aao_cstr7_1_1_xtss_sp: { maxUpper: 8000, minLower: 3000 },
    lower_limit_aao_cstr7_1_1_xtss_sp: { maxUpper: 8000, minLower: 3000 },
    upper_limit_aao_cstr7_1_2_xtss_sp: { maxUpper: 8000, minLower: 3000 },
    lower_limit_aao_cstr7_1_2_xtss_sp: { maxUpper: 8000, minLower: 3000 },
    upper_limit_aao_cstr7_2_1_xtss_sp: { maxUpper: 8000, minLower: 3000 },
    lower_limit_aao_cstr7_2_1_xtss_sp: { maxUpper: 8000, minLower: 3000 },
    upper_limit_aao_cstr7_2_2_xtss_sp: { maxUpper: 8000, minLower: 3000 },
    lower_limit_aao_cstr7_2_2_xtss_sp: { maxUpper: 8000, minLower: 3000 },

    // DO
    upper_limit_aao_cstr3_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr3_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr4_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr4_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr5_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr5_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr6_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr6_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr7_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr7_1_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr3_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr3_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr4_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr4_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr5_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr5_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr6_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr6_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr7_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr7_1_2_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr3_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr3_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr4_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr4_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr5_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr5_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr6_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr6_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr7_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr7_2_1_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr3_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr3_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr4_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr4_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr5_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr5_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr6_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr6_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
    upper_limit_aao_cstr7_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
    lower_limit_aao_cstr7_2_2_so2_sp: { maxUpper: 4, minLower: 0 },
  };

// 获取字段的默认上下限值
const getFieldDefaultRange = (
  fieldName: string
): { upper: number; lower: number } | null => {
  const limit = fieldRangeLimits[fieldName];
  if (!limit) return null;
  return { upper: limit.maxUpper, lower: limit.minLower };
};

// 验证字段值是否在允许范围内
const validateFieldValue = (
  fieldName: string,
  value: number,
  isUpper: boolean
): { valid: boolean; message: string } => {
  const limit = fieldRangeLimits[fieldName];
  if (!limit) return { valid: true, message: "" };

  if (isUpper) {
    // 上限不能超过maxUpper，不能小于minLower
    if (value > limit.maxUpper) {
      return { valid: false, message: `上限不能超过 ${limit.maxUpper}` };
    }
    if (value < limit.minLower) {
      return { valid: false, message: `上限不能小于 ${limit.minLower}` };
    }
  } else {
    // 下限不能超过maxUpper，不能小于minLower
    if (value > limit.maxUpper) {
      return { valid: false, message: `下限不能超过 ${limit.maxUpper}` };
    }
    if (value < limit.minLower) {
      return { valid: false, message: `下限不能小于 ${limit.minLower}` };
    }
  }

  return { valid: true, message: "" };
};

// 图表相关数据
const selectedCategory = ref<string>(""); // 选中的类别（单选）
const chartLoading = ref(false);
const chartError = ref<string>("");
const chartData = ref<Record<string, number[]>>({}); // 优化数据
const realtimeChartData = ref<Record<string, number[]>>({}); // 真实数据
const chartTimes = ref<string[]>([]);
const chartInstances = ref<Map<string, echarts.ECharts>>(new Map());

// 类别与字段的映射关系
const categoryFieldsMap: Record<string, string[]> = {
  "1-1AAO曝气量": [
    "aao_cstr_front_1_1_qair_ntp_or",
    "aao_cstr_mid_1_1_qair_ntp_or",
    "aao_cstr_terminal_1_1_qair_ntp_or",
  ],
  "1-2AAO曝气量": [
    "aao_cstr_front_1_2_qair_ntp_or",
    "aao_cstr_mid_1_2_qair_ntp_or",
    "aao_cstr_terminal_1_2_qair_ntp_or",
  ],
  "2-1AAO曝气量": [
    "aao_cstr_front_2_1_qair_ntp_or",
    "aao_cstr_mid_2_1_qair_ntp_or",
    "aao_cstr_terminal_2_1_qair_ntp_or",
  ],
  "2-2AAO曝气量": [
    "aao_cstr_front_2_2_qair_ntp_or",
    "aao_cstr_mid_2_2_qair_ntp_or",
    "aao_cstr_terminal_2_2_qair_ntp_or",
  ],
  AAO内回流量: [
    "aao_flowdivider3_1_1_influx_or",
    "aao_flowdivider3_1_2_influx_or",
    "aao_flowdivider3_2_1_influx_or",
    "aao_flowdivider3_2_2_influx_or",
  ],
  AAO外回流量: ["aao_ras_1_q_or", "aao_ras_2_q_or"],
  AAO剩余污泥量: [
    "aao_flowdivider3_1_sludge_q_or",
    "aao_flowdivider3_2_sludge_q_or",
  ],
  AAO生物池污泥浓度: [
    "aao_cstr7_1_1_xtss_or",
    "aao_cstr7_1_2_xtss_or",
    "aao_cstr7_2_1_xtss_or",
    "aao_cstr7_2_2_xtss_or",
  ],
};

// 字段显示名称映射
const fieldDisplayNames: Record<string, string> = {
  aao_cstr_front_1_1_qair_ntp_or: "基准模拟1-1#AAO生化池曝气支管1曝气量",
  aao_cstr_mid_1_1_qair_ntp_or: "基准模拟1-1#AAO生化池曝气支管2曝气量",
  aao_cstr_terminal_1_1_qair_ntp_or: "基准模拟1-1#AAO生化池曝气支管3曝气量",
  aao_cstr_front_1_2_qair_ntp_or: "基准模拟1-2#AAO生化池曝气支管1曝气量",
  aao_cstr_mid_1_2_qair_ntp_or: "基准模拟1-2#AAO生化池曝气支管2曝气量",
  aao_cstr_terminal_1_2_qair_ntp_or: "基准模拟1-2#AAO生化池曝气支管3曝气量",
  aao_cstr_front_2_1_qair_ntp_or: "基准模拟2-1#AAO生化池曝气支管1曝气量",
  aao_cstr_mid_2_1_qair_ntp_or: "基准模拟2-1#AAO生化池曝气支管2曝气量",
  aao_cstr_terminal_2_1_qair_ntp_or: "基准模拟2-1#AAO生化池曝气支管3曝气量",
  aao_cstr_front_2_2_qair_ntp_or: "基准模拟2-2#AAO生化池曝气支管1曝气量",
  aao_cstr_mid_2_2_qair_ntp_or: "基准模拟2-2#AAO生化池曝气支管2曝气量",
  aao_cstr_terminal_2_2_qair_ntp_or: "基准模拟2-2#AAO生化池曝气支管3曝气量",
  aao_flowdivider3_1_1_influx_or: "离线模拟1-1#AAO生化池内回流量",
  aao_flowdivider3_1_2_influx_or: "离线模拟1-2#AAO生化池内回流量",
  aao_flowdivider3_2_1_influx_or: "离线模拟2-1#AAO生化池内回流量",
  aao_flowdivider3_2_2_influx_or: "离线模拟2-2#AAO生化池内回流量",
  aao_ras_1_q_or: "离线模拟1#回流污泥流量",
  aao_ras_2_q_or: "离线模拟2#回流污泥流量",
  aao_flowdivider3_1_sludge_q_or: "离线模拟1号二沉池剩余污泥量",
  aao_flowdivider3_2_sludge_q_or: "离线模拟2号二沉池剩余污泥量",
  aao_cstr7_1_1_xtss_or: "离线模拟1-1#AAO生化池混合液悬浮固体浓度",
  aao_cstr7_1_2_xtss_or: "离线模拟1-2#AAO生化池混合液悬浮固体浓度",
  aao_cstr7_2_1_xtss_or: "离线模拟2-1#AAO生化池混合液悬浮固体浓度",
  aao_cstr7_2_2_xtss_or: "离线模拟2-2#AAO生化池混合液悬浮固体浓度",
};

// 优化数据
const optimizeData = reactive({
  startTime: "",
  endTime: "",
  dataSource: "1",
  frequency: 120,
  psoIter: 10,
  size: 15,
  mpcSteps: 3,
  aaoConfigName: "",
  mbrConfigName: "mbr_nh4",
});

// 优化目标
const objectives = reactive({
  nh4: { target: 1, weight: 1 },
  tn: { target: 0, weight: 0 },
  tp: { target: 0, weight: 0 },
  ss: { target: 0, weight: 0 },
  cod: { target: 0, weight: 0 },
  useEconomicMode: false,
});

// 优化算法选项
const algorithms = [
  { id: "acpsoea", name: "KD-DD01", description: "算法描述1" },
  { id: "KD-DD02", name: "KD-DD02", description: "算法描述2" },
  { id: "KD-DD03", name: "KD-DD03", description: "算法描述3" },
];

// AAO优化参数选项
const aaoParamOptions = [
  { id: "aeration", name: "曝气量" },
  { id: "sludgeDischarge", name: "排泥" },
  { id: "internalRecycle", name: "内回流" },
  { id: "externalRecycle", name: "外回流" },
  { id: "multiInlet", name: "多点进水比例" },
  { id: "do", name: "DO" },
  { id: "pac", name: "PAC" },
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

// 计算属性
const steps = computed(() => [
  "模拟数据设置",
  "选择优化算法",
  "选择优化目标",
  "设置优化参数",
  "设置参数范围",
  "生成优化结果",
  "优化结果对比图",
]);

const progressScale = computed(() => {
  const totalSteps = steps.value.length;
  const currentStepIndex = currentStep.value - 1;

  if (currentStepIndex === 0) {
    return 0;
  }

  // 当到达最后一步时，进度线应该完全覆盖到最后一个圆
  if (currentStepIndex >= totalSteps - 1) {
    return 1;
  }

  const progressPercentage = currentStepIndex / (totalSteps - 1);
  return progressPercentage;
});

// 判断是否选择了参数配置(仅AAO类型,且选择了wry_tn或wry_tn_economy)
const isConfigSelected = computed(() => {
  if (props.processType !== "AAO") return false;
  const configName = optimizeData.aaoConfigName;
  return configName === "wry_tn" || configName === "wry_tn_economy";
});

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1:
      return (
        optimizeData.startTime &&
        optimizeData.endTime &&
        optimizeData.dataSource
      );
    case 2:
      return !!selectedAlgorithm.value;
    case 3:
      return true; // 优化目标设置是可选的
    case 4:
      // 如果选择了参数配置，则允许直接通过（参数已在配置中预设）
      if (isConfigSelected.value) {
        return true;
      }
      return selectedParameters.value.length > 0;
    case 5:
      // 步骤5：设置参数范围，需要验证所有已选参数的上下限是否都已填写
      return validateParameterRanges();
    default:
      return true;
  }
});

// 方法
const selectAlgorithm = (algorithmId: string) => {
  selectedAlgorithm.value = algorithmId;
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

// 验证参数范围是否都已填写
const validateParameterRanges = (): boolean => {
  // 如果选择了参数配置，跳过验证
  if (isConfigSelected.value) {
    return true;
  }

  // 检查是否有验证错误
  for (const fieldKey in rangeValidationErrors) {
    const errors = rangeValidationErrors[fieldKey];
    if (errors.upper || errors.lower) {
      return false;
    }
  }

  // 检查所有已选参数的每个字段的上下限是否都已填写
  for (const paramId of selectedParameters.value) {
    const mapping = parameterFieldMapping[paramId];
    if (!mapping) continue;

    // 检查每个字段的上下限
    for (let i = 0; i < mapping.upperFields.length; i++) {
      const fieldKey = `${paramId}_${i}`;
      const range = parameterRanges[fieldKey];
      if (!range || range.upper === null || range.lower === null) {
        return false;
      }
      // 验证上限必须大于下限
      if (range.upper <= range.lower) {
        return false;
      }

      // 验证值是否在允许范围内
      const upperFieldName = mapping.upperFields[i];
      const lowerFieldName = mapping.lowerFields[i];
      const upperValidation = validateFieldValue(
        upperFieldName,
        range.upper,
        true
      );
      const lowerValidation = validateFieldValue(
        lowerFieldName,
        range.lower,
        false
      );
      if (!upperValidation.valid || !lowerValidation.valid) {
        return false;
      }
    }
  }

  return true;
};

// 保存参数范围到数据库
const saveParameterRanges = async (): Promise<boolean> => {
  try {
    // 如果选择了参数配置，跳过保存
    if (isConfigSelected.value) {
      console.log("[参数范围保存] 已选择参数配置，跳过保存");
      return true;
    }

    // 构建要更新的字段对象
    const updateFields: Record<string, number> = {};

    console.log(
      "[参数范围保存] 开始构建更新字段，已选参数:",
      selectedParameters.value
    );

    // 遍历所有已选参数
    for (const paramId of selectedParameters.value) {
      const mapping = parameterFieldMapping[paramId];
      if (!mapping) {
        console.warn(`[参数范围保存] 参数 ${paramId} 没有映射关系`);
        continue;
      }

      console.log(
        `[参数范围保存] 处理参数 ${paramId}，字段数: ${mapping.upperFields.length}`
      );

      // 遍历每个字段
      for (let i = 0; i < mapping.upperFields.length; i++) {
        const fieldKey = `${paramId}_${i}`;
        const range = parameterRanges[fieldKey];
        const upperFieldName = mapping.upperFields[i];
        const lowerFieldName = mapping.lowerFields[i];

        if (range && range.upper !== null && range.lower !== null) {
          // 添加上限和下限字段
          updateFields[upperFieldName] = range.upper;
          updateFields[lowerFieldName] = range.lower;
          console.log(
            `[参数范围保存] 添加字段 ${upperFieldName} = ${range.upper}, ${lowerFieldName} = ${range.lower}`
          );
        } else {
          console.warn(
            `[参数范围保存] 字段 ${fieldKey} 的值为空，跳过 (upper: ${range?.upper}, lower: ${range?.lower})`
          );
        }
      }
    }

    console.log(
      `[参数范围保存] 构建完成，共 ${Object.keys(updateFields).length} 个字段`
    );
    console.log(
      "[参数范围保存] 更新字段列表:",
      Object.keys(updateFields).slice(0, 20),
      "..."
    );
    console.log(
      "[参数范围保存] 更新字段示例:",
      Object.entries(updateFields).slice(0, 5)
    );

    // 检查上下限字段
    const upperFields = Object.keys(updateFields).filter((k) =>
      k.includes("upper_limit")
    );
    const lowerFields = Object.keys(updateFields).filter((k) =>
      k.includes("lower_limit")
    );
    console.log(
      `[参数范围保存] 上限字段数: ${upperFields.length}, 下限字段数: ${lowerFields.length}`
    );

    // 调用API更新系统参数
    console.log("[参数范围保存] 开始调用API更新系统参数...");
    const response = await updateSystemParams(updateFields);
    console.log("[参数范围保存] API调用完成，响应:", response);

    if (response.success) {
      console.log("[参数范围保存] 保存成功");
      return true;
    } else {
      console.error("[参数范围保存] 保存失败:", response.message);
      return false;
    }
  } catch (error) {
    console.error("[参数范围保存] 保存异常:", error);
    if (error instanceof Error) {
      console.error("[参数范围保存] 错误堆栈:", error.stack);
    }
    return false;
  }
};

const nextStep = async () => {
  if (canProceed.value && currentStep.value < 7) {
    // 如果从步骤5进入步骤6，先保存参数范围
    if (currentStep.value === 5) {
      const saveSuccess = await saveParameterRanges();
      if (!saveSuccess) {
        alert("保存参数范围失败，请检查输入");
        return;
      }
    }
    currentStep.value++;
    // 如果进入步骤7，自动加载图表数据
    if (currentStep.value === 7 && selectedCategory.value) {
      loadChartData();
    }
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
  }
};

const getDataSourceName = (source: string) => {
  const sources: Record<string, string> = {
    "1": "原始数据",
    "2": "清洗数据",
    "3": "实验数据",
  };
  return sources[source] || "未知";
};

const getAlgorithmName = (algorithmId: string) => {
  const algorithm = algorithms.find((a) => a.id === algorithmId);
  return algorithm ? algorithm.name : "未知";
};

const getSelectedParametersNames = () => {
  return selectedParameters.value
    .map((id) => parameterOptions.value.find((p) => p.id === id)?.name)
    .filter(Boolean)
    .join(", ");
};

const startOptimization = async () => {
  // 开始优化时,解除禁用状态允许查看结果
  isRunning.value = true;
  progress.value = 0;

  try {
    // 构建API请求数据
    const requestData: OptimizationRequest = {
      start_time: formatTimeForAPI(optimizeData.startTime),
      end_time: formatTimeForAPI(optimizeData.endTime),
      frequency: optimizeData.frequency || 120,
      PSO_iter: optimizeData.psoIter || 10,
      size: optimizeData.size || 15,
      mpc_steps: optimizeData.mpcSteps || 3,
      optimize_algorithm_sp: selectedAlgorithm.value,
    };

    // 根据工艺类型添加相应的配置名称
    if (props.processType === "AAO") {
      requestData.aao_config_name = optimizeData.aaoConfigName || "wry_tn";
    } else if (props.processType === "MBR") {
      requestData.mbr_config_name = optimizeData.mbrConfigName || "mbr_nh4";
    }

    console.log("调用优化API:", requestData);

    // 调用相应的API
    let response;
    if (props.processType === "AAO") {
      response = await aaoSimulationService.startAAOOptimization(requestData);
    } else {
      response = await aaoSimulationService.startMBROptimization(requestData);
    }

    if (!response.success) {
      throw new Error(response.message || "优化启动失败");
    }

    // 模拟优化进度更新
    const interval = setInterval(async () => {
      // 尝试获取实际进度
      try {
        let progressResponse;
        if (props.processType === "AAO") {
          progressResponse =
            await aaoSimulationService.getAAOOptimizationProgress();
        } else {
          progressResponse =
            await aaoSimulationService.getMBROptimizationProgress();
        }

        if (progressResponse.success && progressResponse.data?.progress) {
          progress.value = Math.min(98, progressResponse.data.progress);
        } else {
          // 如果无法获取实际进度，使用模拟进度
          progress.value += Math.random() * 10 + 5;
        }
      } catch (error) {
        // 如果获取进度失败，使用模拟进度
        progress.value += Math.random() * 10 + 5;
      }

      if (progress.value >= 100) {
        progress.value = 100;
        clearInterval(interval);
        isRunning.value = false;
        optimizeResult.value = {
          success: true,
          message: `${props.processType}优化完成`,
        };

        // 加载优化结果数据
        await loadOptimizationResultData();
      }
    }, 2000);
  } catch (error) {
    console.error("优化失败:", error);
    isRunning.value = false;
    progress.value = 0;
    alert(error instanceof Error ? error.message : "优化启动失败");
  }
};

const stopOptimization = async () => {
  try {
    let response;
    if (props.processType === "AAO") {
      response = await aaoSimulationService.stopAAOOptimization();
    } else {
      response = await aaoSimulationService.stopMBROptimization();
    }

    if (response.success) {
      isRunning.value = false;
      progress.value = 0;
    } else {
      console.error("停止优化失败:", response.message);
    }
  } catch (error) {
    console.error("停止优化失败:", error);
    isRunning.value = false;
    progress.value = 0;
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

// 获取选中类别下的所有字段
const getSelectedFields = (): string[] => {
  if (!selectedCategory.value) {
    return [];
  }
  return categoryFieldsMap[selectedCategory.value] || [];
};

// 加载图表数据
const loadChartData = async () => {
  if (!optimizeData.startTime || !optimizeData.endTime) {
    chartError.value = "请先设置优化的开始时间和结束时间";
    return;
  }

  if (!selectedCategory.value) {
    chartError.value = "请选择一个类别";
    return;
  }

  chartLoading.value = true;
  chartError.value = "";

  try {
    const formattedStartTime = formatTimeForAPI(optimizeData.startTime);
    const formattedEndTime = formatTimeForAPI(optimizeData.endTime);
    const fieldsToQuery = getSelectedFields();

    const response = await aaoSimulationService.getOptimizationResultChartData({
      start_time: formattedStartTime,
      end_time: formattedEndTime,
      field_names: fieldsToQuery,
    });

    if (response.success && response.data) {
      chartData.value = response.data.data || {};
      realtimeChartData.value = response.data.realtime_data || {};
      chartTimes.value = response.data.times || [];

      // 延迟渲染，确保DOM已更新
      nextTick(() => {
        renderCharts();
      });
    } else {
      chartError.value = response.message || "获取图表数据失败";
    }
  } catch (error) {
    console.error("加载图表数据失败:", error);
    chartError.value =
      error instanceof Error ? error.message : "加载图表数据失败";
  } finally {
    chartLoading.value = false;
  }
};

// 渲染所有图表
const renderCharts = () => {
  // 清理旧的图表实例
  chartInstances.value.forEach((instance) => {
    instance.dispose();
  });
  chartInstances.value.clear();

  if (!selectedCategory.value) {
    return;
  }

  nextTick(() => {
    // 为选中类别下的每个字段创建图表
    const category = selectedCategory.value;
    const fields = categoryFieldsMap[category] || [];
    fields.forEach((fieldName, fieldIndex) => {
      const chartId = `chart-${category}-${fieldIndex}`;
      const chartElement = document.getElementById(chartId);

      if (!chartElement) {
        console.warn(`图表容器未找到: ${chartId}`);
        return;
      }

      const optimizeData = chartData.value[fieldName] || [];
      const realtimeData = realtimeChartData.value[fieldName] || [];

      // 初始化图表实例
      const chartInstance = echarts.init(chartElement);
      chartInstances.value.set(chartId, chartInstance);

      // 配置选项 - 显示优化数据和真实数据
      const series: any[] = [
        {
          name: "优化",
          type: "line",
          data: optimizeData,
          smooth: true,
          areaStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(255, 193, 7, 0.3)" },
                { offset: 1, color: "rgba(255, 193, 7, 0.05)" },
              ],
            },
          },
          lineStyle: {
            color: "#ffc107",
            width: 2,
          },
          itemStyle: {
            color: "#ffc107",
          },
        },
      ];

      // 如果有真实数据，添加真实数据系列
      if (realtimeData.length > 0) {
        series.push({
          name: "历史",
          type: "line",
          data: realtimeData,
          smooth: true,
          areaStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(59, 130, 246, 0.3)" },
                { offset: 1, color: "rgba(59, 130, 246, 0.05)" },
              ],
            },
          },
          lineStyle: {
            color: "#3b82f6",
            width: 2,
          },
          itemStyle: {
            color: "#3b82f6",
          },
        });
      }

      const option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross",
          },
          backgroundColor: "rgba(0, 0, 0, 0.8)",
          borderColor: "#00c9ff",
          borderWidth: 1,
          textStyle: {
            color: "#fff",
          },
          formatter: (params: any) => {
            if (!params || params.length === 0) return "";
            let result = `时间: ${params[0].axisValue}<br/>`;
            params.forEach((item: any) => {
              result += `${item.marker} ${item.seriesName}: ${
                item.value !== null && item.value !== undefined
                  ? item.value.toFixed(2)
                  : "无数据"
              }<br/>`;
            });
            return result;
          },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: chartTimes.value,
          axisLine: {
            lineStyle: {
              color: "#4a5568",
            },
          },
          axisLabel: {
            color: "#a0aec0",
            formatter: (value: string) => {
              // 格式化为 MM-DD HH:mm
              const date = new Date(value);
              const month = String(date.getMonth() + 1).padStart(2, "0");
              const day = String(date.getDate()).padStart(2, "0");
              const hours = String(date.getHours()).padStart(2, "0");
              const minutes = String(date.getMinutes()).padStart(2, "0");
              return `${month}-${day} ${hours}:${minutes}`;
            },
          },
        },
        yAxis: {
          type: "value",
          axisLine: {
            lineStyle: {
              color: "#4a5568",
            },
          },
          axisLabel: {
            color: "#a0aec0",
          },
          splitLine: {
            lineStyle: {
              color: "#2d3748",
            },
          },
        },
        series: series,
      };

      chartInstance.setOption(option);
    });
  });
};

// 监听选中类别变化，自动加载数据
watch(selectedCategory, (newCategory) => {
  if (newCategory && currentStep.value === 7) {
    loadChartData();
  }
});

// 监听步骤变化，处理图表窗口大小调整
watch(
  () => currentStep.value,
  (newStep) => {
    if (newStep === 7) {
      // 进入步骤7时，延迟调整图表大小
      nextTick(() => {
        chartInstances.value.forEach((instance) => {
          instance.resize();
        });
      });
      // 添加窗口大小监听
      window.addEventListener("resize", handleChartResize);
    } else {
      // 离开步骤7时，移除窗口大小监听
      window.removeEventListener("resize", handleChartResize);
    }
  }
);

const handleChartResize = () => {
  chartInstances.value.forEach((instance) => {
    instance.resize();
  });
};

// 组件卸载时清理
onBeforeUnmount(() => {
  chartInstances.value.forEach((instance) => {
    instance.dispose();
  });
  chartInstances.value.clear();
  window.removeEventListener("resize", handleChartResize);
});

// 初始化默认时间
const initDefaultTime = () => {
  // 设置开始时间为2024-05-15 01:00:00
  optimizeData.startTime = "2024-05-15T01:00";
  // 设置结束时间为2024-05-15 03:00:00
  optimizeData.endTime = "2024-05-15T03:00";
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

// 从后端加载优化结果数据
const loadOptimizationResultData = async () => {
  try {
    console.log("开始从后端加载优化结果数据...");

    // 根据开始时间查询数据（仅AAO类型）
    if (props.processType === "AAO" && optimizeData.startTime) {
      // 将ISO格式转换为后端需要的格式
      const formattedStartTime = formatTimeForAPI(optimizeData.startTime);
      console.log("根据开始时间查询优化结果数据:", formattedStartTime);

      const response =
        await aaoSimulationService.getOptimizationResultByStartTime(
          formattedStartTime
        );

      if (response.success && response.data) {
        console.log("成功获取优化结果:", response.data);
        optimizeResultData.value = response.data;
        return;
      }
    }

    // 如果查询失败，使用空数据
    console.warn("未获取到优化结果数据");
    optimizeResultData.value = null;
  } catch (error) {
    console.error("加载优化结果数据失败:", error);
    optimizeResultData.value = null;
  }
};

// 组件初始化时设置默认时间
initDefaultTime();

// 参数范围验证错误信息
const rangeValidationErrors = reactive<
  Record<string, { upper?: string; lower?: string }>
>({});

// 初始化参数范围
const initParameterRanges = () => {
  // 如果选择了参数配置，跳过初始化
  if (isConfigSelected.value) {
    return;
  }

  // 为每个已选参数初始化范围数据
  for (const paramId of selectedParameters.value) {
    const mapping = parameterFieldMapping[paramId];
    if (!mapping) continue;

    // 为每个字段初始化范围，设置默认值为对应的上下限
    for (let i = 0; i < mapping.upperFields.length; i++) {
      const fieldKey = `${paramId}_${i}`;
      const upperFieldName = mapping.upperFields[i];
      const lowerFieldName = mapping.lowerFields[i];

      // 获取默认值
      const upperDefault = getFieldDefaultRange(upperFieldName);
      const lowerDefault = getFieldDefaultRange(lowerFieldName);

      if (!parameterRanges[fieldKey]) {
        parameterRanges[fieldKey] = {
          upper: upperDefault?.upper ?? null,
          lower: lowerDefault?.lower ?? null,
        };
      } else {
        // 如果已存在但值为null，设置默认值
        if (parameterRanges[fieldKey].upper === null && upperDefault) {
          parameterRanges[fieldKey].upper = upperDefault.upper;
        }
        if (parameterRanges[fieldKey].lower === null && lowerDefault) {
          parameterRanges[fieldKey].lower = lowerDefault.lower;
        }
      }
    }
  }
};

// 监听器
watch(
  () => currentStep.value,
  (newStep) => {
    if (newStep === 1 && (!optimizeData.startTime || !optimizeData.endTime)) {
      initDefaultTime();
    }
    // 当进入步骤5时，初始化参数范围
    if (newStep === 5) {
      initParameterRanges();
    }
  }
);
</script>

<style scoped>
.offline-optimize-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  pointer-events: auto;
}

.offline-optimize-dialog {
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  pointer-events: auto;
  position: relative;
}

.dialog-header {
  position: relative;
  height: 60px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 50px 30px 0 30px;
}

.offtitle {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 20px;
  font-weight: bold;
  color: white;
  line-height: 40px;
  background: rgba(0, 0, 0, 0.4);
  padding: 4px 16px;
  border-radius: 10px;
  box-shadow: 0 0 8px rgba(0, 255, 255, 0.4);
  max-width: calc(100% - 100px);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.close-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.progress-bar {
  position: relative;
  padding: 30px 20px;
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

.dialog-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}

.step-content {
  min-height: 400px;
}

.step-title {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 18px;
  color: #ffffff;
}

.step-title:has(.config-select) {
  justify-content: space-between;
}

.step-title-left {
  display: flex;
  align-items: center;
}

.config-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 14px;
  cursor: pointer;
  min-width: 200px;
}

.config-select option {
  background: #1a1a2e;
  color: #ffffff;
}

.arrow {
  color: #4f46e5;
  margin-right: 10px;
  font-size: 20px;
}

.data-settings {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.form-row label {
  width: 120px;
  color: #ffffff;
  font-size: 14px;
}

.datetime-input,
.number-input,
.select-input {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 14px;
}

.number-input {
  width: 200px;
}

.select-input {
  width: 250px;
  cursor: pointer;
}

.select-input option {
  background: #1a1a2e;
  color: #ffffff;
}

.unit-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin-left: 8px;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-item {
  display: flex;
  align-items: center;
  color: #ffffff;
  cursor: pointer;
}

.radio-item input {
  margin-right: 8px;
}

.algorithm-selection {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
}

.algorithm-card {
  width: 150px;
  height: 100px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.algorithm-card.selected {
  background: #f59e0b;
  border-color: #f59e0b;
  transform: scale(1.05);
}

.algorithm-name {
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.algorithm-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

.check-icon {
  position: absolute;
  bottom: 5px;
  right: 5px;
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
}

.objectives-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-top: 20px;
}

.objectives-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.objectives-section.full-width {
  grid-column: 1 / -1;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}

.section-icon {
  color: #4f46e5;
  margin-right: 10px;
  font-size: 16px;
}

.section-title {
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
}

.aao-label {
  position: absolute;
  right: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.aao-label span {
  color: #4f46e5;
  font-size: 14px;
  font-weight: bold;
}

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
  color: #ffffff;
  font-size: 14px;
  font-weight: bold;
  text-align: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
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
  color: #ffffff;
  font-size: 14px;
}

.target-input,
.weight-input {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 12px;
  width: 60px;
}

.unit {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  min-width: 30px;
}

.objectives-note {
  margin-top: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  text-align: center;
}

.economic-mode-setting {
  padding: 15px;
}

.economic-mode-row {
  display: flex;
  align-items: center;
  gap: 15px;
}

.economic-mode-label {
  color: #ffffff;
  font-size: 14px;
  font-weight: bold;
}

.economic-mode-status {
  color: #4f46e5;
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
  background-color: #4f46e5;
}

.switch input:disabled + .slider {
  opacity: 0.5;
  cursor: not-allowed;
}

.switch input:checked + .slider:before {
  transform: translateX(26px);
}

/* AAO参数列表样式 */
.aao-params-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.aao-param-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
}

.aao-param-item:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(79, 70, 229, 0.5);
}

.aao-param-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.param-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.param-checkbox:disabled {
  cursor: not-allowed;
}

.param-label {
  color: #ffffff;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  flex: 1;
}

.aao-param-item.disabled .param-label {
  cursor: not-allowed;
}

.parameter-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.parameters-selection {
  margin-top: 30px;
}

.parameter-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.parameter-card {
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.parameter-card.selected {
  background: #f59e0b;
  border-color: #f59e0b;
}

.parameter-name {
  color: #ffffff;
  font-size: 14px;
  font-weight: bold;
}

.parameter-note {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  text-align: center;
}

.results-content {
  text-align: center;
  padding: 20px 0;
}

.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: #ffffff;
  font-size: 18px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-bar-mini {
  width: 200px;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4f46e5;
  transition: width 0.3s;
}

.progress-text {
  color: #ffffff;
  font-size: 14px;
}

.result-section {
  color: #ffffff;
}

.result-title {
  font-size: 24px;
  margin-bottom: 15px;
  color: #10b981;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  max-width: 100%;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 15px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border-left: 3px solid #4f46e5;
  min-height: 40px;
}

.summary-item .label {
  color: #ffffff;
  font-weight: bold;
  font-size: 12px;
}

.summary-item .value {
  color: #4f46e5;
  font-size: 12px;
}

.result-details {
  margin-top: 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 15px;
  max-width: 100%;
  overflow: hidden;
}

.details-title {
  font-size: 16px;
  color: #ffffff;
  margin-bottom: 15px;
  font-weight: bold;
  text-align: center;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-category {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
}

.category-title {
  font-size: 14px;
  color: #4f46e5;
  margin-bottom: 10px;
  font-weight: bold;
  border-bottom: 1px solid rgba(79, 70, 229, 0.3);
  padding-bottom: 6px;
}

.category-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border-left: 3px solid #4f46e5;
}

.item-label {
  color: #ffffff;
  font-size: 12px;
  flex: 1;
  min-width: 0;
}

.item-value {
  color: #10b981;
  font-size: 12px;
  font-weight: bold;
  min-width: 60px;
  text-align: right;
}

.item-unit {
  color: #6b7280;
  font-size: 11px;
  min-width: 35px;
}

.dialog-footer {
  padding: 20px 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #4f46e5;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: #4338ca;
}

.btn-primary:disabled {
  background: rgba(255, 255, 255, 0.2);
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-danger {
  background: #ef4444;
  color: #ffffff;
}

.btn-danger:hover {
  background: #dc2626;
}

/* AAO离线优化结果样式 */
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

/* 图表容器样式 */
.chart-container {
  display: flex;
  gap: 20px;
  height: 600px;
  margin-top: 20px;
}

.chart-params-panel {
  width: 300px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.params-title {
  font-size: 18px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 20px;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(0, 201, 255, 0.3);
}

.params-categories {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.category-item {
  padding: 12px 15px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s;
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}

.category-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(79, 70, 229, 0.5);
}

.category-item.active {
  background: rgba(124, 58, 237, 0.3);
  border-color: #7c3aed;
  color: #ffffff;
  box-shadow: 0 0 10px rgba(124, 58, 237, 0.5);
}

.btn-refresh {
  width: 100%;
  padding: 10px;
  margin-top: 20px;
  background: #4f46e5;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-refresh:hover {
  background: #4338ca;
}

.chart-display-panel {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.empty-text {
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 10px;
  overflow-y: auto;
  max-height: 100%;
}

.chart-item {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-title {
  font-size: 13px;
  color: #ffffff;
  margin-bottom: 10px;
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: 500;
}

.chart-canvas-item {
  width: 100%;
  height: 300px;
  min-height: 300px;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 20px;
}

.chart-loading .loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.chart-loading .loading-text {
  color: #ffffff;
  font-size: 16px;
}

.chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 20px;
}

.error-text {
  color: #ef4444;
  font-size: 16px;
  text-align: center;
}

.btn-retry {
  padding: 10px 20px;
  background: #4f46e5;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-retry:hover {
  background: #4338ca;
}

.btn-chart {
  background: #10b981;
  color: #ffffff;
}

.btn-chart:hover {
  background: #059669;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 参数范围样式 */
.parameter-ranges-container {
  margin-top: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.config-note {
  padding: 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.parameter-range-section {
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.parameter-range-title {
  font-size: 16px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(0, 201, 255, 0.3);
}

.parameter-range-table {
  width: 100%;
}

.range-table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 15px;
  margin-bottom: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.range-table-header .header-cell {
  color: #ffffff;
  font-size: 14px;
  font-weight: bold;
  text-align: center;
}

.range-table-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.range-table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  align-items: center;
}

.range-cell {
  display: flex;
  align-items: center;
}

.range-cell:first-child {
  color: #ffffff;
  font-size: 13px;
}

.range-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 13px;
}

.range-input:focus {
  outline: none;
  border-color: #4f46e5;
  background: rgba(255, 255, 255, 0.15);
}

.range-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.range-input-wrapper {
  position: relative;
  width: 100%;
}

.range-input-error {
  border-color: #ef4444 !important;
  background: rgba(239, 68, 68, 0.1) !important;
}

.range-error-tip {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  font-size: 11px;
  color: #ef4444;
  white-space: nowrap;
  z-index: 10;
  background: rgba(0, 0, 0, 0.8);
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #ef4444;
}
</style>
