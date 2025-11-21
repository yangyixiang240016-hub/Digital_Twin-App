<template>
  <div class="online-simulation-mask" @click.self="$emit('close')">
    <div class="online-simulation-dialog" @click.stop>
      <!-- 关闭按钮 -->
      <div class="close-btn" @click="$emit('close')">×</div>

      <!-- 标题 -->
      <div class="dialog-title">
        在线模式——{{ processType }}{{ mode === "simulate" ? "模拟" : "优化" }}
      </div>

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
        <!-- 步骤1: 在线模式模拟/优化 -->
        <div v-if="currentStep === 1" class="step-panel">
          <div class="step-title">
            <span class="arrow">→</span>
            在线模式{{ mode === "simulate" ? "模拟" : "优化" }}
          </div>
          <div class="mode-description">
            <p>
              在线模式将实时获取当前系统数据，基于当前工况进行{{
                mode === "simulate" ? "模拟" : "优化"
              }}分析。
            </p>
            <p>系统将自动获取以下实时数据：</p>
            <ul>
              <li>进水水质参数（COD、NH3-N、TN、TP、SS等）</li>
              <li>出水水质参数</li>
              <li>生物池运行参数（MLSS、DO等）</li>
              <li>设备运行状态</li>
            </ul>
          </div>
          <div class="step-actions">
            <button class="next-btn" @click="nextStep">下一步</button>
          </div>
        </div>

        <!-- 步骤2: 模拟数据设置 -->
        <div v-if="currentStep === 2" class="step-panel">
          <div class="step-title">
            <span class="arrow">→</span>
            模拟数据设置
          </div>

          <div class="online-params-settings">
            <div class="params-section">
              <div class="param-row">
                <label class="param-label">数据源:</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="0"
                      v-model="onlineParams.dataSource"
                    />
                    <span>原始数据</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="1"
                      v-model="onlineParams.dataSource"
                    />
                    <span>清洗后数据</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="2"
                      v-model="onlineParams.dataSource"
                    />
                    <span>化验室数据</span>
                  </label>
                </div>
              </div>

              <div class="param-row">
                <label class="param-label">预测步长:</label>
                <input
                  type="number"
                  v-model.number="onlineParams.forecastStep"
                  class="param-number-input"
                  placeholder="默认6"
                />
              </div>

              <div class="param-row">
                <label class="param-label">运行频率:</label>
                <input
                  type="number"
                  v-model.number="onlineParams.frequency"
                  class="param-number-input"
                  placeholder="默认120"
                />
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="prev-btn" @click="prevStep">上一步</button>
            <button class="next-btn" @click="nextStep">下一步</button>
          </div>
        </div>

        <!-- 步骤3: 设置模拟参数 -->
        <div
          v-if="currentStep === 3 && processType === 'AAO'"
          class="step-panel"
        >
          <div class="step-header-with-button">
            <div class="step-title">
              <span class="arrow">→</span>
              设置模拟参数
            </div>
            <button
              class="original-data-btn"
              :class="{ active: useOriginalData }"
              @click="useOriginalData = !useOriginalData"
            >
              {{ useOriginalData ? "✓" : "" }} 使用原始数据
            </button>
          </div>

          <div class="simulation-params-container">
            <div class="parameters-grid">
              <!-- 曝气参数 -->
              <div class="param-section">
                <div class="section-title">曝气参数</div>
                <div class="bioreactor-group">
                  <div
                    class="bioreactor"
                    v-for="(bioreactor, idx) in [
                      { id: '1-1', index: 1 },
                      { id: '1-2', index: 2 },
                      { id: '2-1', index: 3 },
                      { id: '2-2', index: 4 },
                    ]"
                    :key="bioreactor.id"
                  >
                    <div class="bioreactor-title">
                      {{ bioreactor.id }}#AAO生物池
                    </div>
                    <div class="zones">
                      <div class="zone">
                        <label>好氧前段:</label>
                        <input
                          type="number"
                          v-model.number="
                            aaoSimulationParams[
                              `opt1_aao_aer_fro_air_${bioreactor.index}`
                            ]
                          "
                          class="param-input"
                          :disabled="useOriginalData"
                        />
                        <span class="unit">m³/h</span>
                      </div>
                      <div class="zone">
                        <label>好氧中段:</label>
                        <input
                          type="number"
                          v-model.number="
                            aaoSimulationParams[
                              `opt1_aao_aer_mid_air_${bioreactor.index}`
                            ]
                          "
                          class="param-input"
                          :disabled="useOriginalData"
                        />
                        <span class="unit">m³/h</span>
                      </div>
                      <div class="zone">
                        <label>好氧后段:</label>
                        <input
                          type="number"
                          v-model.number="
                            aaoSimulationParams[
                              `opt1_aao_aer_bac_air_${bioreactor.index}`
                            ]
                          "
                          class="param-input"
                          :disabled="useOriginalData"
                        />
                        <span class="unit">m³/h</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 多点进水比例 -->
              <div class="param-section">
                <div class="section-title">多点进水比例</div>
                <div class="bioreactor-group">
                  <div
                    class="bioreactor"
                    v-for="(bioreactor, idx) in [
                      { id: '1-1', index: 1 },
                      { id: '1-2', index: 2 },
                      { id: '2-1', index: 3 },
                      { id: '2-2', index: 4 },
                    ]"
                    :key="bioreactor.id"
                  >
                    <div class="bioreactor-title">
                      {{ bioreactor.id }}#AAO生物池
                    </div>
                    <div class="zones">
                      <div class="zone">
                        <label>选择区:</label>
                        <input
                          type="number"
                          step="0.1"
                          v-model.number="
                            aaoSimulationParams[
                              `opt1_aao_sel_inf_rat_${bioreactor.index}`
                            ]
                          "
                          class="param-input"
                          :disabled="useOriginalData"
                        />
                      </div>
                      <div class="zone">
                        <label>厌氧区:</label>
                        <input
                          type="number"
                          step="0.1"
                          v-model.number="
                            aaoSimulationParams[
                              `opt1_aao_ana_inf_rat_${bioreactor.index}`
                            ]
                          "
                          class="param-input"
                          :disabled="useOriginalData"
                        />
                      </div>
                      <div class="zone">
                        <label>缺氧区:</label>
                        <input
                          type="number"
                          step="0.1"
                          v-model.number="
                            aaoSimulationParams[
                              `opt1_aao_ano_inf_rat_${bioreactor.index}`
                            ]
                          "
                          class="param-input"
                          :disabled="useOriginalData"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 外回流及排泥设置 -->
              <div class="param-section">
                <div class="section-title">外回流及排泥设置</div>
                <div class="bioreactor-group">
                  <div class="bioreactor" v-for="idx in [1, 2]" :key="idx">
                    <div class="bioreactor-title">{{ idx }}#AAO</div>
                    <div class="zones">
                      <div class="zone">
                        <label>外回流量:</label>
                        <input
                          type="number"
                          v-model.number="
                            aaoSimulationParams[`opt1_aao_ras_flow_${idx}`]
                          "
                          class="param-input"
                          :disabled="useOriginalData"
                        />
                        <span class="unit">m³/h</span>
                      </div>
                      <div class="zone">
                        <label>剩余污泥量:</label>
                        <input
                          type="number"
                          v-model.number="
                            aaoSimulationParams[`opt1_aao_was_flow_${idx}`]
                          "
                          class="param-input"
                          :disabled="useOriginalData"
                        />
                        <span class="unit">m³/h</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 内回流设置 -->
              <div class="param-section">
                <div class="section-title">内回流设置</div>
                <div class="bioreactor-group">
                  <div
                    class="bioreactor"
                    v-for="bioreactor in [
                      {
                        id: '1',
                        name: '1#AAO生物池',
                        flows: [
                          { label: '1-1#内回流量', param: 1 },
                          { label: '1-2#内回流量', param: 2 },
                        ],
                      },
                      {
                        id: '2',
                        name: '2#AAO生物池',
                        flows: [
                          { label: '2-1#内回流量', param: 3 },
                          { label: '2-2#内回流量', param: 4 },
                        ],
                      },
                    ]"
                    :key="bioreactor.id"
                  >
                    <div class="bioreactor-title">{{ bioreactor.name }}</div>
                    <div class="zones">
                      <div
                        class="zone"
                        v-for="flow in bioreactor.flows"
                        :key="flow.param"
                      >
                        <label>{{ flow.label }}:</label>
                        <input
                          type="number"
                          v-model.number="
                            aaoSimulationParams[
                              `opt1_aao_int_ref_flow_${flow.param}`
                            ]
                          "
                          class="param-input"
                          :disabled="useOriginalData"
                        />
                        <span class="unit">m³/h</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="prev-btn" @click="prevStep">上一步</button>
            <button class="start-simulate-btn" @click="handleStartSimulation">
              开始模拟
            </button>
          </div>
        </div>

        <!-- 步骤3: 设置模拟参数 (MBR模式) -->
        <div
          v-if="currentStep === 3 && processType === 'MBR'"
          class="step-panel"
        >
          <div class="step-header-with-button">
            <div class="step-title">
              <span class="arrow">→</span>
              设置模拟参数
            </div>
            <button
              class="original-data-btn"
              :class="{ active: useOriginalData }"
              @click="useOriginalData = !useOriginalData"
            >
              {{ useOriginalData ? "✓" : "" }} 使用原始数据
            </button>
          </div>
          <div class="step-actions">
            <button class="prev-btn" @click="prevStep">上一步</button>
            <button class="start-simulate-btn" @click="handleStartSimulation">
              开始模拟
            </button>
          </div>
        </div>

        <!-- 步骤4: 生成模拟/优化结果 -->
        <div v-if="currentStep === 4" class="step-panel">
          <div class="step-title">
            <span class="arrow">→</span>
            生成{{ mode === "simulate" ? "模拟" : "优化" }}结果
          </div>

          <!-- 生成进度条 -->
          <div class="generation-progress-box">
            <div class="generation-progress-bar">
              <div
                class="generation-progress-fill"
                :style="{ width: progress + '%' }"
              ></div>
            </div>
          </div>

          <div class="progress-container">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: progress + '%' }"
              ></div>
            </div>
            <div class="progress-text">{{ progress.toFixed(2) }}%</div>
            <div class="progress-status">{{ progressStatus }}</div>
          </div>

          <div class="real-time-data">
            <div class="data-title">实时数据监控</div>
            <div class="data-grid">
              <div class="data-item">
                <span>进水流量:</span>
                <span class="value"
                  >{{ realTimeData.inflow?.toFixed(2) || "--" }} m³/d</span
                >
              </div>
              <div class="data-item">
                <span>出水流量:</span>
                <span class="value"
                  >{{ realTimeData.outflow?.toFixed(2) || "--" }} m³/d</span
                >
              </div>
              <div class="data-item">
                <span>COD:</span>
                <span class="value"
                  >{{ realTimeData.cod?.toFixed(2) || "--" }} mg/L</span
                >
              </div>
              <div class="data-item">
                <span>NH3-N:</span>
                <span class="value"
                  >{{ realTimeData.nh3n?.toFixed(2) || "--" }} mg/L</span
                >
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="prev-btn" @click="prevStep">上一步</button>
            <button
              class="stop-btn"
              @click="stopSimulation"
              v-if="progress < 100"
            >
              停止{{ mode === "simulate" ? "模拟" : "优化" }}
            </button>
            <button class="next-btn" @click="nextStep" v-if="progress >= 100">
              查看结果
            </button>
          </div>
        </div>

        <!-- 步骤5: 结果展示 -->
        <div v-if="currentStep === 5" class="step-panel">
          <div class="step-title">
            <span class="arrow">→</span>
            {{ mode === "simulate" ? "模拟" : "优化" }}结果展示
          </div>

          <!-- AAO在线模拟结果详情 -->
          <div
            v-if="
              simulationResultData &&
              processType === 'AAO' &&
              mode === 'simulate'
            "
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
                      getFieldValue("aao_influent_1_q_ted") || "—"
                    }}</span>
                    <span class="param-unit">m³/d</span>
                  </div>
                  <div class="aao-param-row">
                    <label>2#AAO生化池进水流量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_influent_2_q_ted") || "—"
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
                      getFieldValue("aao_effluent_q_ted") || "—"
                    }}</span>
                    <span class="param-unit">m³/d</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水化学需氧量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_tcod_ted") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水生化需氧量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_tbod_ted") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水悬浮固体浓度:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_ss_ted") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水总磷:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_tp_ted") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水总氮:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_tn_ted") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水氨氮:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_snhx_ted") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水硝氮:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_snox_ted") || "—"
                    }}</span>
                    <span class="param-unit">mg/L</span>
                  </div>
                  <div class="aao-param-row">
                    <label>出水正磷酸盐:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_effluent_spo4_ted") || "—"
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
                      getFieldValue("aao_pac_q_ted") || "—"
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
                      getFieldValue("aao_ras_1_q_ted") || "—"
                    }}</span>
                    <span class="param-unit">m³/d</span>
                  </div>
                  <div class="aao-param-row">
                    <label>2#回流污泥流量:</label>
                    <span class="param-value">{{
                      getFieldValue("aao_ras_2_q_ted") || "—"
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
                        getFieldValue("aao_cstr3_1_1_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段2曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr4_1_1_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段3曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr5_1_1_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段4曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr6_1_1_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段5曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr7_1_1_qair_ntp_ted") || "—"
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
                        getFieldValue("aao_cstr3_1_2_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段2曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr4_1_2_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段3曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr5_1_2_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段4曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr6_1_2_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段5曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr7_1_2_qair_ntp_ted") || "—"
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
                        getFieldValue("aao_cstr3_2_1_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段2曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr4_2_1_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段3曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr5_2_1_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段4曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr6_2_1_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段5曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr7_2_1_qair_ntp_ted") || "—"
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
                        getFieldValue("aao_cstr3_2_2_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段2曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr4_2_2_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段3曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr5_2_2_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段4曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr6_2_2_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                    <div class="aao-param-row">
                      <label>好氧段5曝气量:</label>
                      <span class="param-value">{{
                        getFieldValue("aao_cstr7_2_2_qair_ntp_ted") || "—"
                      }}</span>
                      <span class="param-unit">Nm³/d</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="prev-btn" @click="prevStep">上一步</button>
            <button class="complete-btn" @click="completeSimulation">
              完成
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import axios from "axios";
import {
  aaoSimulationService,
  type OnlineSimulationRequest,
} from "@/api/aaoSimulation";

const props = defineProps<{
  processType: "AAO" | "MBR";
  mode: "simulate" | "optimize";
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "complete", result: any): void;
}>();

// 响应式数据
const currentStep = ref(1);
const progress = ref(0);
const progressStatus = ref("准备中...");
const simulationResultData = ref<any>(null);
const simulationStartTime = ref<string>("");

// 在线参数设置
const onlineParams = reactive({
  dataSource: "1", // 0-原始数据 1-清洗后数据 2-化验室数据
  forecastStep: 6, // 预测步长，默认6
  frequency: 120, // 运行频率，默认120分钟
});

// 使用原始数据标志
const useOriginalData = ref(false);

// AAO模拟参数设置（初始值来自API示例）
const aaoSimulationParams = reactive({
  // 曝气参数
  opt1_aao_aer_fro_air_1: 2200,
  opt1_aao_aer_mid_air_1: 1100,
  opt1_aao_aer_bac_air_1: 600,
  opt1_aao_aer_fro_air_2: 2200,
  opt1_aao_aer_mid_air_2: 1100,
  opt1_aao_aer_bac_air_2: 600,
  opt1_aao_aer_fro_air_3: 2200,
  opt1_aao_aer_mid_air_3: 1100,
  opt1_aao_aer_bac_air_3: 600,
  opt1_aao_aer_fro_air_4: 2200,
  opt1_aao_aer_mid_air_4: 1100,
  opt1_aao_aer_bac_air_4: 600,
  // 外回流参数
  opt1_aao_ras_flow_1: 9000,
  opt1_aao_ras_flow_2: 9000,
  // 剩余污泥量
  opt1_aao_was_flow_1: 120,
  opt1_aao_was_flow_2: 120,
  // 内回流
  opt1_aao_int_ref_flow_1: 6250,
  opt1_aao_int_ref_flow_2: 6250,
  opt1_aao_int_ref_flow_3: 6250,
  opt1_aao_int_ref_flow_4: 6250,
  // 多点进水比例
  opt1_aao_sel_inf_rat_1: 0.1,
  opt1_aao_ana_inf_rat_1: 0.3,
  opt1_aao_ano_inf_rat_1: 0.6,
  opt1_aao_sel_inf_rat_2: 0.1,
  opt1_aao_ana_inf_rat_2: 0.3,
  opt1_aao_ano_inf_rat_2: 0.6,
  opt1_aao_sel_inf_rat_3: 0.1,
  opt1_aao_ana_inf_rat_3: 0.3,
  opt1_aao_ano_inf_rat_3: 0.6,
  opt1_aao_sel_inf_rat_4: 0.1,
  opt1_aao_ana_inf_rat_4: 0.3,
  opt1_aao_ano_inf_rat_4: 0.6,
});

// 步骤定义
const steps = [
  "在线模式模拟",
  "模拟数据设置",
  "设置模拟参数",
  "生成模拟结果",
  "结果展示",
];

// 进度比例计算
const progressScale = computed(() => {
  return currentStep.value / steps.length;
});

// 实时数据
const realTimeData = reactive({
  inflow: 0,
  outflow: 0,
  cod: 0,
  nh3n: 0,
});

// 获取实时进水数据
const fetchRealTimeData = async () => {
  try {
    // 获取进水流量
    const inflowRes = await axios.get("/api/inflow");
    realTimeData.inflow = inflowRes.data.value || 0;

    // 获取出水流量
    const outflowRes = await axios.get("/api/outflow");
    realTimeData.outflow = outflowRes.data.value || 0;

    // 获取出水水质实时数据
    const outflowQualityRes = await axios.get("/api/realtime/outflow/quality");
    const quality = outflowQualityRes.data || {};
    realTimeData.cod = quality.cod || 0;
    realTimeData.nh3n = quality.nh3n || 0;
  } catch (error) {
    console.error("获取实时数据失败:", error);
  }
};

// 结果数据
const results = reactive({
  efficiency: 95.2,
  energySaving: 12.5,
  compliance: 98.7,
});

// 实时数据定时器
let realTimeInterval: number | null = null;

// 方法
const nextStep = () => {
  if (currentStep.value < 5) {
    currentStep.value++;
  }
};

// 开始模拟（从步骤3调用）
const handleStartSimulation = () => {
  // 立即获取实时数据显示
  fetchRealTimeData();

  // 启动定时器，每5秒更新实时数据
  if (realTimeInterval) {
    clearInterval(realTimeInterval);
  }
  realTimeInterval = window.setInterval(() => {
    fetchRealTimeData();
  }, 5000);

  // 启动模拟API调用
  startSimulation();

  // 跳转到步骤4（生成模拟结果）
  currentStep.value = 4;
};

const prevStep = () => {
  if (currentStep.value > 1) {
    // 如果从步骤3返回，清除实时数据定时器
    if (currentStep.value === 3 && realTimeInterval) {
      clearInterval(realTimeInterval);
      realTimeInterval = null;
    }
    currentStep.value--;
  }
};

const startSimulation = async () => {
  progress.value = 0;
  progressStatus.value = "正在启动模拟...";

  // 记录模拟开始时间
  simulationStartTime.value = new Date()
    .toISOString()
    .slice(0, 16)
    .replace("T", " ");

  // 进度定时器
  let progressInterval: number | null = null;

  try {
    // 构建API请求数据
    let requestData: any = {
      data_source: parseInt(onlineParams.dataSource),
      forecast_step: onlineParams.forecastStep,
      frequency: onlineParams.frequency,
    };

    // 如果不使用原始数据，添加所有参数
    if (!useOriginalData.value && props.processType === "AAO") {
      requestData = {
        ...requestData,
        ...aaoSimulationParams,
      };
    }

    console.log("调用在线模拟API:", requestData);
    console.log("使用原始数据:", useOriginalData.value);

    // 先启动进度更新到70%
    progressStatus.value = "正在启动模拟...";

    // 启动进度更新的Promise
    const progressPromise = new Promise<void>((resolve) => {
      progressInterval = window.setInterval(() => {
        if (progress.value < 70) {
          // 随机增加进度，直到达到70%
          const increment = Math.random() * 3 + 1; // 每次增加1-4
          progress.value = Math.min(70, progress.value + increment);
          progressStatus.value = getProgressStatus(progress.value);
        } else {
          // 达到70%后停止这个定时器并resolve
          if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
          }
          resolve();
        }
      }, 200);
    });

    // 调用相应的API（异步等待）
    const apiPromise =
      props.processType === "AAO"
        ? aaoSimulationService.startAAOOnlineSimulation(requestData)
        : aaoSimulationService.startMBROnlineSimulation(requestData);

    // 等待进度达到70%和API调用完成
    const [, response] = await Promise.all([progressPromise, apiPromise]);

    // API调用完成后，确保清除之前的进度定时器
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }

    // 如果进度还没到70%，确保设置为70%
    if (progress.value < 70) {
      progress.value = 70;
    }

    if (!response.success) {
      throw new Error(response.message || "在线模拟启动失败");
    }

    // API成功返回后，从70%增加到100%
    progressStatus.value = "正在生成结果...";
    const finalInterval = window.setInterval(async () => {
      if (progress.value < 100) {
        // 从70%平滑增加到100%
        const increment = Math.random() * 5 + 2; // 每次增加2-7
        progress.value = Math.min(100, progress.value + increment);
      } else {
        progress.value = 100;
        progressStatus.value = "完成";
        clearInterval(finalInterval);
        // 加载模拟结果数据
        await loadOnlineSimulationResultData();
      }
    }, 200);
  } catch (error) {
    // 出错时清除进度定时器
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    console.error("在线模拟失败:", error);
    progress.value = 0;
    progressStatus.value = "模拟失败";
    alert(error instanceof Error ? error.message : "在线模拟启动失败");
  }
};

const getProgressStatus = (progress: number) => {
  if (progress < 30) return "正在获取实时数据...";
  if (progress < 60) return "正在分析水质参数...";
  if (progress < 90) return "正在计算优化方案...";
  return "正在生成结果...";
};

// 获取字段值的辅助函数
const getFieldValue = (fieldName: string) => {
  if (!simulationResultData.value || !simulationResultData.value.fields) {
    return null;
  }
  const fieldData = simulationResultData.value.fields[fieldName];
  if (
    fieldData &&
    typeof fieldData.value !== "undefined" &&
    fieldData.value !== null
  ) {
    return fieldData.value;
  }
  return null;
};

// 从后端加载在线模拟结果数据
const loadOnlineSimulationResultData = async () => {
  try {
    console.log("开始从后端加载在线模拟结果数据...");

    // 查询最新一条数据（仅AAO类型且为模拟模式）
    if (props.processType === "AAO" && props.mode === "simulate") {
      const response =
        await aaoSimulationService.getOnlineSimulationResultByStartTime();

      if (response.success && response.data) {
        console.log("成功获取在线模拟结果:", response.data);
        simulationResultData.value = response.data;
        return;
      }
    }

    // 如果查询失败，使用空数据
    console.warn("未获取到在线模拟结果数据");
    simulationResultData.value = null;
  } catch (error) {
    console.error("加载在线模拟结果数据失败:", error);
    simulationResultData.value = null;
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

const stopSimulation = () => {
  // 清除实时数据定时器
  if (realTimeInterval) {
    clearInterval(realTimeInterval);
    realTimeInterval = null;
  }
  emit("close");
};

const completeSimulation = () => {
  // 清除实时数据定时器
  if (realTimeInterval) {
    clearInterval(realTimeInterval);
    realTimeInterval = null;
  }
  emit("complete", {
    processType: props.processType,
    mode: props.mode,
    params: onlineParams,
    results: results,
  });
};

onMounted(() => {
  // 组件挂载时可以预先获取一次实时数据（可选）
  // fetchRealTimeData();
});
</script>

<style scoped>
.online-simulation-mask {
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

.online-simulation-dialog {
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
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
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
  font-size: 20px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 30px;
}

.arrow {
  margin-right: 10px;
  font-size: 18px;
}

.mode-description {
  background: rgba(0, 160, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.mode-description p {
  margin-bottom: 10px;
  line-height: 1.6;
}

.mode-description ul {
  margin-left: 20px;
  margin-top: 10px;
}

.mode-description li {
  margin-bottom: 5px;
}

.online-params-settings {
  background: rgba(0, 160, 255, 0.05);
  padding: 25px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.params-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.param-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 15px;
}

.param-row:last-child {
  margin-bottom: 0;
}

.param-label {
  min-width: 100px;
  font-size: 15px;
  font-weight: bold;
  color: #00c9ff;
}

.radio-group {
  display: flex;
  gap: 30px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: white;
  font-size: 14px;
}

.radio-item input[type="radio"] {
  cursor: pointer;
  width: 18px;
  height: 18px;
}

.param-number-input {
  width: 200px;
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
}

.param-number-input:focus {
  outline: none;
  border-color: #00c9ff;
  box-shadow: 0 0 5px rgba(0, 201, 255, 0.5);
}

.param-unit {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.mode-info {
  background: rgba(0, 160, 255, 0.1);
  padding: 15px 20px;
  border-radius: 8px;
}

.mode-info p {
  margin-bottom: 10px;
  line-height: 1.6;
  font-size: 14px;
}

.mode-info ul {
  margin-left: 20px;
  margin-top: 10px;
}

.mode-info li {
  margin-bottom: 5px;
  font-size: 13px;
}

/* 生成进度条 */
.generation-progress-box {
  width: 100%;
  height: 30px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  margin-bottom: 30px;
  padding: 3px;
  box-sizing: border-box;
}

.generation-progress-bar {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.generation-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00c9ff 0%, #007bff 100%);
  border-radius: 6px;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(0, 201, 255, 0.5);
}

.progress-container {
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
  margin-bottom: 5px;
}

.progress-status {
  text-align: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.real-time-data {
  background: rgba(0, 160, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.data-title {
  font-size: 16px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 15px;
  text-align: center;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
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

.results-container {
  margin-bottom: 30px;
}

.result-summary {
  background: rgba(0, 160, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.summary-title {
  font-size: 18px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 15px;
  text-align: center;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.result-charts {
  background: rgba(0, 160, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
}

.chart-title {
  font-size: 16px;
  font-weight: bold;
  color: #00c9ff;
  margin-bottom: 15px;
  text-align: center;
}

.chart-placeholder {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

/* AAO在线模拟结果样式 */
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

.chart-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 6px;
}

.chart-label {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  text-align: center;
}

.chart-content {
  height: 100px;
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
  margin-bottom: 10px;
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
.complete-btn {
  background: #007bff;
  color: white;
}

.next-btn:hover,
.complete-btn:hover {
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

.stop-btn {
  background: #dc3545;
  color: white;
}

.stop-btn:hover {
  background: #c82333;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 步骤3参数设置样式 */
.step-header-with-button {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.original-data-btn {
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.original-data-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.original-data-btn.active {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.simulation-params-container {
  background: rgba(0, 160, 255, 0.05);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  max-height: 500px;
  overflow-y: auto;
}

.parameters-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  width: 100%;
}

.param-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 10px;
}

.bioreactor-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  width: 100%;
}

.bioreactor {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 10px;
  width: 100%;
  min-width: 0;
}

.bioreactor-title {
  font-size: 12px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 8px;
  text-align: center;
}

.zones {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.zone {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  min-width: 0;
}

.zone label {
  min-width: 70px;
  font-size: 12px;
  color: #ffffff;
  flex-shrink: 0;
}

.param-input {
  flex: 0 0 auto;
  width: 70px;
  max-width: 70px;
  padding: 4px 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 12px;
}

.param-input:focus {
  outline: none;
  border-color: #00c9ff;
  box-shadow: 0 0 3px rgba(0, 201, 255, 0.5);
}

.param-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.05);
}

.unit {
  font-size: 11px;
  color: #ffffff;
  min-width: 35px;
  flex-shrink: 0;
}

.start-simulate-btn {
  background: #10b981;
  color: white;
  padding: 10px 30px;
}

.start-simulate-btn:hover {
  background: #059669;
}
</style>
