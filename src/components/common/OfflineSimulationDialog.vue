<template>
  <div class="offline-simulation-mask" @click.self="$emit('close')">
    <div class="offline-simulation-dialog" @click.stop>
      <!-- 标题栏 -->
      <div class="dialog-header">
        <div class="offtitle">{{ dialogTitle }}</div>
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
        <div class="progress-line" :style="{ width: progressWidth }"></div>
      </div>

      <!-- 内容区域 -->
      <div class="dialog-content">
        <!-- 步骤1: 选择模拟类型 -->
        <div v-if="currentStep === 1" class="step-content">
          <div class="step-title">
            <span class="arrow">→</span>
            选择动态/稳态模拟
          </div>
          <div class="simulation-type-options">
            <div
              class="type-card dynamic"
              :class="{ selected: simulationType === 'dynamic' }"
              @click="selectSimulationType('dynamic')"
            >
              <div class="type-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"
                  />
                </svg>
              </div>
              <div class="type-label">动态模拟</div>
            </div>
            <div
              class="type-card steady"
              :class="{ selected: simulationType === 'steady' }"
              @click="selectSimulationType('steady')"
            >
              <div class="type-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
                  />
                </svg>
              </div>
              <div class="type-label">稳态模拟</div>
            </div>
          </div>
        </div>

        <!-- 步骤2: 数据设置 -->
        <div v-if="currentStep === 2" class="step-content">
          <div class="step-title">
            <span class="arrow">→</span>
            模拟数据设置
          </div>
          <div class="data-settings">
            <div class="settings-section">
              <div class="section-title">动态数据模拟设置</div>
              <div class="form-row">
                <label>开始日期:</label>
                <input
                  type="datetime-local"
                  v-model="simulationData.startTime"
                  class="datetime-input"
                />
              </div>
              <div class="form-row">
                <label>结束日期:</label>
                <input
                  type="datetime-local"
                  v-model="simulationData.endTime"
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
                      v-model="simulationData.dataSource"
                    />
                    <span>原始数据</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="2"
                      v-model="simulationData.dataSource"
                    />
                    <span>清洗数据</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="3"
                      v-model="simulationData.dataSource"
                    />
                    <span>化验室数据</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤3: 参数设置 -->
        <div v-if="currentStep === 3" class="step-content">
          <!-- AAO设置独立区域 -->
          <div v-if="processType === 'AAO'" class="aao-main-settings">
            <div class="aao-header-with-button">
              <div class="aao-title">
                <span class="arrow">→</span>
                AAO工艺参数设置
              </div>
              <button
                class="original-data-btn"
                :class="{ active: useOriginalData }"
                @click="useOriginalData = !useOriginalData"
              >
                {{ useOriginalData ? "✓" : "" }} 使用原始数据
              </button>
            </div>
            <div class="aao-parameters-container">
              <div class="parameters-grid">
                <!-- 曝气参数 -->
                <div class="param-section">
                  <div class="section-title">曝气参数</div>
                  <div class="bioreactor-group">
                    <div
                      v-for="bioreactor in aaoBioreactors"
                      :key="bioreactor.id"
                      class="bioreactor"
                    >
                      <div class="bioreactor-title">{{ bioreactor.name }}</div>
                      <div class="zones">
                        <div
                          v-for="zone in bioreactor.zones"
                          :key="zone.id"
                          class="zone"
                        >
                          <label>{{ zone.name }}:</label>
                          <input
                            type="number"
                            v-model.number="zone.value"
                            class="param-input"
                            :disabled="useOriginalData"
                          />
                          <span class="unit">{{ zone.unit }}</span>
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
                      v-for="bioreactor in aaoInletBioreactors"
                      :key="bioreactor.id"
                      class="bioreactor"
                    >
                      <div class="bioreactor-title">{{ bioreactor.name }}</div>
                      <div class="zones">
                        <div
                          v-for="zone in bioreactor.zones"
                          :key="zone.id"
                          class="zone"
                        >
                          <label>{{ zone.name }}:</label>
                          <input
                            type="number"
                            step="0.1"
                            v-model.number="zone.value"
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
                    <div
                      v-for="bioreactor in aaoRecycleBioreactors"
                      :key="bioreactor.id"
                      class="bioreactor"
                    >
                      <div class="bioreactor-title">{{ bioreactor.name }}</div>
                      <div class="zones">
                        <div
                          v-for="zone in bioreactor.zones"
                          :key="zone.id"
                          class="zone"
                        >
                          <label>{{ zone.name }}:</label>
                          <input
                            type="number"
                            v-model.number="zone.value"
                            class="param-input"
                            :disabled="useOriginalData"
                          />
                          <span class="unit">{{ zone.unit }}</span>
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
                      v-for="bioreactor in aaoInternalRecycleBioreactors"
                      :key="bioreactor.id"
                      class="bioreactor"
                    >
                      <div class="bioreactor-title">{{ bioreactor.name }}</div>
                      <div class="zones">
                        <div
                          v-for="zone in bioreactor.zones"
                          :key="zone.id"
                          class="zone"
                        >
                          <label>{{ zone.name }}:</label>
                          <input
                            type="number"
                            v-model.number="zone.value"
                            class="param-input"
                            :disabled="useOriginalData"
                          />
                          <span class="unit">{{ zone.unit }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- MBR设置独立区域 -->
          <div v-if="processType === 'MBR'" class="mbr-main-settings">
            <div class="mbr-title">MBR工艺参数设置</div>
            <div class="mbr-parameters-container">
              <div class="parameters-grid">
                <!-- MBR出水参数 -->
                <div class="param-section">
                  <div class="section-title">MBR出水参数</div>
                  <div class="param-group">
                    <div class="sub-section">
                      <div class="sub-title">水量</div>
                      <div class="param-row">
                        <label>总出水量:</label>
                        <input
                          type="number"
                          v-model.number="mbrParams.totalEffluentRate"
                          class="param-input"
                        />
                        <span class="unit">m³/d</span>
                      </div>
                    </div>
                    <div class="sub-section">
                      <div class="sub-title">水质</div>
                      <div class="param-row">
                        <label>COD:</label>
                        <input
                          type="number"
                          v-model.number="mbrParams.cod"
                          class="param-input"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="param-row">
                        <label>NH3-N:</label>
                        <input
                          type="number"
                          v-model.number="mbrParams.nh3n"
                          class="param-input"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="param-row">
                        <label>TN:</label>
                        <input
                          type="number"
                          v-model.number="mbrParams.tn"
                          class="param-input"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="param-row">
                        <label>TP:</label>
                        <input
                          type="number"
                          v-model.number="mbrParams.tp"
                          class="param-input"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="param-row">
                        <label>SS:</label>
                        <input
                          type="number"
                          v-model.number="mbrParams.ss"
                          class="param-input"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="param-row">
                        <label>NO3:</label>
                        <input
                          type="number"
                          v-model.number="mbrParams.no3"
                          class="param-input"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                      <div class="param-row">
                        <label>PH:</label>
                        <input
                          type="number"
                          v-model.number="mbrParams.ph"
                          class="param-input"
                        />
                        <span class="unit">mg/L</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 曝气参数 -->
                <div class="param-section">
                  <div class="section-title">曝气参数</div>
                  <div class="param-group">
                    <div class="param-row">
                      <label>好氧区1:</label>
                      <input
                        type="number"
                        v-model.number="mbrParams.aerobicZone1"
                        class="param-input"
                      />
                      <span class="unit">Nm³/d</span>
                    </div>
                    <div class="param-row">
                      <label>好氧区2:</label>
                      <input
                        type="number"
                        v-model.number="mbrParams.aerobicZone2"
                        class="param-input"
                      />
                      <span class="unit">Nm³/d</span>
                    </div>
                    <div class="param-row">
                      <label>好氧区3:</label>
                      <input
                        type="number"
                        v-model.number="mbrParams.aerobicZone3"
                        class="param-input"
                      />
                      <span class="unit">Nm³/d</span>
                    </div>
                    <div class="param-row">
                      <label>好氧区4:</label>
                      <input
                        type="number"
                        v-model.number="mbrParams.aerobicZone4"
                        class="param-input"
                      />
                      <span class="unit">Nm³/d</span>
                    </div>
                  </div>
                </div>

                <!-- 投加参数 -->
                <div class="param-section">
                  <div class="section-title">投加参数</div>
                  <div class="param-group">
                    <div class="param-row">
                      <label>PAC投加量:</label>
                      <input
                        type="number"
                        v-model.number="mbrParams.pacDosage"
                        class="param-input"
                      />
                      <span class="unit">mg/L</span>
                    </div>
                  </div>
                </div>

                <!-- 内外回流 -->
                <div class="param-section">
                  <div class="section-title">内外回流</div>
                  <div class="param-group">
                    <div class="param-row">
                      <label>MLR回流流量:</label>
                      <input
                        type="number"
                        v-model.number="mbrParams.mlrReturnFlow"
                        class="param-input"
                      />
                      <span class="unit">m³/d</span>
                    </div>
                    <div class="param-row">
                      <label>RAS回流流量:</label>
                      <input
                        type="number"
                        v-model.number="mbrParams.rasReturnFlow"
                        class="param-input"
                      />
                      <span class="unit">m³/d</span>
                    </div>
                    <div class="param-row">
                      <label>SAS污泥量:</label>
                      <input
                        type="number"
                        v-model.number="mbrParams.sasSludgeRate"
                        class="param-input"
                      />
                      <span class="unit">m³/d</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤4: 结果展示 -->
        <div v-if="currentStep === 4" class="step-content">
          <div class="step-title">
            <span class="arrow">→</span>
            生成模拟结果
          </div>
          <div class="results-content">
            <div v-if="isRunning" class="loading-section">
              <div class="loading-spinner"></div>
              <div class="loading-text">模拟进行中...</div>
              <div class="progress-info">
                <div class="progress-bar-mini">
                  <div
                    class="progress-fill"
                    :style="{ width: progress + '%' }"
                  ></div>
                </div>
                <div class="progress-text">{{ progress.toFixed(2) }}%</div>
              </div>
            </div>
            <div v-else-if="simulationResult" class="result-section">
              <!-- AAO离线模拟结果详情 -->
              <div v-if="simulationResultData && processType === 'AAO'" class="aao-result-details">
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
                        <span class="param-value">{{ getFieldValue('aao_influent_1_q_ted') || '—' }}</span>
                        <span class="param-unit">m³/d</span>
                </div>
                      <div class="aao-param-row">
                        <label>2#AAO生化池进水流量:</label>
                        <span class="param-value">{{ getFieldValue('aao_influent_2_q_ted') || '—' }}</span>
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
                        <span class="param-value">{{ getFieldValue('aao_effluent_q_ted') || '—' }}</span>
                        <span class="param-unit">m³/d</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水化学需氧量:</label>
                        <span class="param-value">{{ getFieldValue('aao_effluent_tcod_ted') || '—' }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水生化需氧量:</label>
                        <span class="param-value">{{ getFieldValue('aao_effluent_tbod_ted') || '—' }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水悬浮固体浓度:</label>
                        <span class="param-value">{{ getFieldValue('aao_effluent_ss_ted') || '—' }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水总磷:</label>
                        <span class="param-value">{{ getFieldValue('aao_effluent_tp_ted') || '—' }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水总氮:</label>
                        <span class="param-value">{{ getFieldValue('aao_effluent_tn_ted') || '—' }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水氨氮:</label>
                        <span class="param-value">{{ getFieldValue('aao_effluent_snhx_ted') || '—' }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水硝氮:</label>
                        <span class="param-value">{{ getFieldValue('aao_effluent_snox_ted') || '—' }}</span>
                        <span class="param-unit">mg/L</span>
                      </div>
                      <div class="aao-param-row">
                        <label>出水正磷酸盐:</label>
                        <span class="param-value">{{ getFieldValue('aao_effluent_spo4_ted') || '—' }}</span>
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
                        <span class="param-value">{{ getFieldValue('aao_pac_q_ted') || '—' }}</span>
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
                        <span class="param-value">{{ getFieldValue('aao_ras_1_q_ted') || '—' }}</span>
                        <span class="param-unit">m³/d</span>
                      </div>
                      <div class="aao-param-row">
                        <label>2#回流污泥流量:</label>
                        <span class="param-value">{{ getFieldValue('aao_ras_2_q_ted') || '—' }}</span>
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
                          <span class="param-value">{{ getFieldValue('aao_cstr3_1_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段2曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr4_1_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段3曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr5_1_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段4曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr6_1_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段5曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr7_1_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                      </div>
                      <!-- 1-2#AAO生化池 -->
                      <div class="aao-bioreactor-group">
                        <div class="aao-bioreactor-title">1-2#AAO生化池</div>
                        <div class="aao-param-row">
                          <label>好氧段1曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr3_1_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段2曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr4_1_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段3曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr5_1_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段4曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr6_1_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段5曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr7_1_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                      </div>
                      <!-- 2-1#AAO生化池 -->
                      <div class="aao-bioreactor-group">
                        <div class="aao-bioreactor-title">2-1#AAO生化池</div>
                        <div class="aao-param-row">
                          <label>好氧段1曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr3_2_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段2曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr4_2_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段3曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr5_2_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段4曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr6_2_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段5曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr7_2_1_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                      </div>
                      <!-- 2-2#AAO生化池 -->
                      <div class="aao-bioreactor-group">
                        <div class="aao-bioreactor-title">2-2#AAO生化池</div>
                        <div class="aao-param-row">
                          <label>好氧段1曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr3_2_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段2曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr4_2_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段3曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr5_2_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段4曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr6_2_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                        <div class="aao-param-row">
                          <label>好氧段5曝气量:</label>
                          <span class="param-value">{{ getFieldValue('aao_cstr7_2_2_qair_ntp_ted') || '—' }}</span>
                          <span class="param-unit">Nm³/d</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- MBR或其他工艺类型的模拟结果详情 -->
              <div v-else-if="simulationResultData && processType !== 'AAO'" class="result-details">
                <div class="details-title">模拟结果详情</div>
                <div class="details-content">
                  <div
                    v-for="(category, categoryName) in groupedResults"
                    :key="categoryName"
                    class="result-category"
                  >
                    <div class="category-title">{{ categoryName }}</div>
                    <div class="category-items">
                      <div
                        v-for="item in category"
                        :key="item.fieldName"
                        class="result-item"
                      >
                        <span class="item-label">{{ item.displayName }}:</span>
                        <span class="item-value">{{ item.value }}</span>
                        <span class="item-unit">{{ item.unit }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤5: 模拟结果图 -->
        <div v-if="currentStep === 5" class="step-content">
          <div class="step-title">
            <span class="arrow">→</span>
            模拟结果图
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
              <button class="btn-refresh" @click="loadChartData">刷新图表</button>
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
                  v-for="(fieldName, fieldIndex) in categoryFieldsMap[selectedCategory]" 
                  :key="`${selectedCategory}-${fieldIndex}`"
                  class="chart-item"
                >
                  <div class="chart-title">{{ fieldDisplayNames[fieldName] || fieldName }}</div>
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
          v-if="currentStep < 4"
          class="btn btn-primary"
          @click="nextStep"
          :disabled="!canProceed"
        >
          下一步
        </button>
        <button
          v-if="currentStep === 4 && !isRunning && !simulationResult"
          class="btn btn-primary"
          @click="startSimulation"
        >
          开始模拟
        </button>
        <button
          v-if="currentStep === 4 && isRunning"
          class="btn btn-danger"
          @click="stopSimulation"
        >
          停止模拟
        </button>
        <button
          v-if="currentStep === 4 && !isRunning && simulationResult"
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
  type SimulationRequest,
} from "@/api/aaoSimulation";
import * as echarts from "echarts";
import {
  aaoOfflineFieldMappings,
  mbrOfflineFieldMappings,
  getFieldDisplayName,
  getMBRFieldDisplayName,
  getFieldUnit,
  getMBRFieldUnit,
  getFieldCategory,
  getMBRFieldCategory,
  getFieldMappingsByCategory,
  getMBRFieldMappingsByCategory,
} from "@/utils/fieldMapping";

// Props
const props = defineProps<{
  processType: "AAO" | "MBR";
  mode: "simulate" | "optimize";
}>();

// Emits
const emit = defineEmits<{
  close: [];
  complete: [result: any];
}>();

// 响应式数据
const currentStep = ref(1);
const simulationType = ref<"dynamic" | "steady">("dynamic");
const isRunning = ref(false);
const progress = ref(0);
const simulationResult = ref<any>(null);
const simulationResultData = ref<any>(null);

// 使用原始数据标志
const useOriginalData = ref(false);

// 图表相关数据
const selectedCategory = ref<string>(""); // 选中的类别（单选）
const chartLoading = ref(false);
const chartError = ref<string>("");
const chartData = ref<Record<string, number[]>>({});
const chartTimes = ref<string[]>([]);
const chartInstances = ref<Map<string, echarts.ECharts>>(new Map());

// 类别与字段的映射关系
const categoryFieldsMap: Record<string, string[]> = {
  '1-1AAO曝气量': [
    'aao_cstr_front_1_1_qair_ntp_ted',
    'aao_cstr_mid_1_1_qair_ntp_ted',
    'aao_cstr_terminal_1_1_qair_ntp_ted',
  ],
  '1-2AAO曝气量': [
    'aao_cstr_front_1_2_qair_ntp_ted',
    'aao_cstr_mid_1_2_qair_ntp_ted',
    'aao_cstr_terminal_1_2_qair_ntp_ted',
  ],
  '2-1AAO曝气量': [
    'aao_cstr_front_2_1_qair_ntp_ted',
    'aao_cstr_mid_2_1_qair_ntp_ted',
    'aao_cstr_terminal_2_1_qair_ntp_ted',
  ],
  '2-2AAO曝气量': [
    'aao_cstr_front_2_2_qair_ntp_ted',
    'aao_cstr_mid_2_2_qair_ntp_ted',
    'aao_cstr_terminal_2_2_qair_ntp_ted',
  ],
  'AAO内回流量': [
    'aao_flowdivider3_1_1_influx_ted',
    'aao_flowdivider3_1_2_influx_ted',
    'aao_flowdivider3_2_1_influx_ted',
    'aao_flowdivider3_2_2_influx_ted',
  ],
  'AAO外回流量': [
    'aao_ras_1_q_ted',
    'aao_ras_2_q_ted',
  ],
  'AAO剩余污泥量': [
    'aao_flowdivider3_1_sludge_q_ted',
    'aao_flowdivider3_2_sludge_q_ted',
  ],
  'AAO生物池污泥浓度': [
    'aao_cstr7_1_1_xtss_ted',
    'aao_cstr7_1_2_xtss_ted',
    'aao_cstr7_2_1_xtss_ted',
    'aao_cstr7_2_2_xtss_ted',
  ],
};

// 字段显示名称映射
const fieldDisplayNames: Record<string, string> = {
  'aao_cstr_front_1_1_qair_ntp_ted': '基准模拟1-1#AAO生化池曝气支管1曝气量',
  'aao_cstr_mid_1_1_qair_ntp_ted': '基准模拟1-1#AAO生化池曝气支管2曝气量',
  'aao_cstr_terminal_1_1_qair_ntp_ted': '基准模拟1-1#AAO生化池曝气支管3曝气量',
  'aao_cstr_front_1_2_qair_ntp_ted': '基准模拟1-2#AAO生化池曝气支管1曝气量',
  'aao_cstr_mid_1_2_qair_ntp_ted': '基准模拟1-2#AAO生化池曝气支管2曝气量',
  'aao_cstr_terminal_1_2_qair_ntp_ted': '基准模拟1-2#AAO生化池曝气支管3曝气量',
  'aao_cstr_front_2_1_qair_ntp_ted': '基准模拟2-1#AAO生化池曝气支管1曝气量',
  'aao_cstr_mid_2_1_qair_ntp_ted': '基准模拟2-1#AAO生化池曝气支管2曝气量',
  'aao_cstr_terminal_2_1_qair_ntp_ted': '基准模拟2-1#AAO生化池曝气支管3曝气量',
  'aao_cstr_front_2_2_qair_ntp_ted': '基准模拟2-2#AAO生化池曝气支管1曝气量',
  'aao_cstr_mid_2_2_qair_ntp_ted': '基准模拟2-2#AAO生化池曝气支管2曝气量',
  'aao_cstr_terminal_2_2_qair_ntp_ted': '基准模拟2-2#AAO生化池曝气支管3曝气量',
  'aao_flowdivider3_1_1_influx_ted': '离线模拟1-1#AAO生化池内回流量',
  'aao_flowdivider3_1_2_influx_ted': '离线模拟1-2#AAO生化池内回流量',
  'aao_flowdivider3_2_1_influx_ted': '离线模拟2-1#AAO生化池内回流量',
  'aao_flowdivider3_2_2_influx_ted': '离线模拟2-2#AAO生化池内回流量',
  'aao_ras_1_q_ted': '离线模拟1#回流污泥流量',
  'aao_ras_2_q_ted': '离线模拟2#回流污泥流量',
  'aao_flowdivider3_1_sludge_q_ted': '离线模拟1号二沉池剩余污泥量',
  'aao_flowdivider3_2_sludge_q_ted': '离线模拟2号二沉池剩余污泥量',
  'aao_cstr7_1_1_xtss_ted': '离线模拟1-1#AAO生化池混合液悬浮固体浓度',
  'aao_cstr7_1_2_xtss_ted': '离线模拟1-2#AAO生化池混合液悬浮固体浓度',
  'aao_cstr7_2_1_xtss_ted': '离线模拟2-1#AAO生化池混合液悬浮固体浓度',
  'aao_cstr7_2_2_xtss_ted': '离线模拟2-2#AAO生化池混合液悬浮固体浓度',
};

// 模拟数据
const simulationData = reactive({
  startTime: "",
  endTime: "",
  dataSource: "1",
});

// MBR参数
const mbrParams = reactive({
  totalEffluentRate: 0,
  cod: 0,
  nh3n: 0,
  tn: 0,
  tp: 0,
  ss: 0,
  no3: 0,
  ph: 0,
  aerobicZone1: 0,
  aerobicZone2: 0,
  aerobicZone3: 0,
  aerobicZone4: 0,
  pacDosage: 0,
  mlrReturnFlow: 0,
  rasReturnFlow: 0,
  sasSludgeRate: 0,
});

// AAO生物池数据
const aaoBioreactors = reactive([
  {
    id: "1-1",
    name: "1-1#AAO生物池",
    zones: [
      { id: "front", name: "好氧前段", value: 2200, unit: "m³/d" },
      { id: "middle", name: "好氧中段", value: 1100, unit: "m³/d" },
      { id: "rear", name: "好氧后段", value: 600, unit: "m³/d" },
    ],
  },
  {
    id: "1-2",
    name: "1-2#AAO生物池",
    zones: [
      { id: "front", name: "好氧前段", value: 2200, unit: "m³/d" },
      { id: "middle", name: "好氧中段", value: 1100, unit: "m³/d" },
      { id: "rear", name: "好氧后段", value: 600, unit: "m³/d" },
    ],
  },
  {
    id: "2-1",
    name: "2-1#AAO生物池",
    zones: [
      { id: "front", name: "好氧前段", value: 2200, unit: "m³/d" },
      { id: "middle", name: "好氧中段", value: 1100, unit: "m³/d" },
      { id: "rear", name: "好氧后段", value: 600, unit: "m³/d" },
    ],
  },
  {
    id: "2-2",
    name: "2-2#AAO生物池",
    zones: [
      { id: "front", name: "好氧前段", value: 2200, unit: "m³/d" },
      { id: "middle", name: "好氧中段", value: 1100, unit: "m³/d" },
      { id: "rear", name: "好氧后段", value: 600, unit: "m³/d" },
    ],
  },
]);

const aaoInletBioreactors = reactive([
  {
    id: "1-1",
    name: "1-1#AAO生物池",
    zones: [
      { id: "selection", name: "选择区", value: 0.1 },
      { id: "anaerobic", name: "厌氧区", value: 0.3 },
      { id: "anoxic", name: "缺氧区", value: 0.6 },
    ],
  },
  {
    id: "1-2",
    name: "1-2#AAO生物池",
    zones: [
      { id: "selection", name: "选择区", value: 0.1 },
      { id: "anaerobic", name: "厌氧区", value: 0.3 },
      { id: "anoxic", name: "缺氧区", value: 0.6 },
    ],
  },
  {
    id: "2-1",
    name: "2-1#AAO生物池",
    zones: [
      { id: "selection", name: "选择区", value: 0.1 },
      { id: "anaerobic", name: "厌氧区", value: 0.3 },
      { id: "anoxic", name: "缺氧区", value: 0.6 },
    ],
  },
  {
    id: "2-2",
    name: "2-2#AAO生物池",
    zones: [
      { id: "selection", name: "选择区", value: 0.1 },
      { id: "anaerobic", name: "厌氧区", value: 0.3 },
      { id: "anoxic", name: "缺氧区", value: 0.6 },
    ],
  },
]);

const aaoRecycleBioreactors = reactive([
  {
    id: "1",
    name: "1#AAO",
    zones: [
      { id: "external", name: "外回流量", value: 9000, unit: "m³/d" },
      { id: "sludge", name: "剩余污泥量", value: 120, unit: "m³/d" },
    ],
  },
  {
    id: "2",
    name: "2#AAO",
    zones: [
      { id: "external", name: "外回流量", value: 9000, unit: "m³/d" },
      { id: "sludge", name: "剩余污泥量", value: 120, unit: "m³/d" },
    ],
  },
]);

const aaoInternalRecycleBioreactors = reactive([
  {
    id: "1",
    name: "1#AAO生物池",
    zones: [
      { id: "internal1", name: "1-1#内回流量", value: 6250, unit: "m³/d" },
      { id: "internal2", name: "1-2#内回流量", value: 6250, unit: "m³/d" },
    ],
  },
  {
    id: "2",
    name: "2#AAO生物池",
    zones: [
      { id: "internal3", name: "2-1#内回流量", value: 6250, unit: "m³/d" },
      { id: "internal4", name: "2-2#内回流量", value: 6250, unit: "m³/d" },
    ],
  },
]);

// 计算属性
const dialogTitle = computed(() => {
  const modeText = props.mode === "simulate" ? "模拟" : "优化";
  return `离线模式——${props.processType}${modeText}`;
});

const steps = computed(() => [
  "动态/稳态模拟",
  "模拟数据设置",
  "设置模拟参数",
  "生成模拟结果",
  "模拟结果图",
]);

const progressWidth = computed(() => {
  // 计算进度线应该覆盖的宽度
  // 进度线从第一个圆圈中心到当前步骤圆圈中心
  const totalSteps = steps.value.length;
  const currentStepIndex = currentStep.value - 1; // 转换为0-based索引

  if (currentStepIndex === 0) {
    return "0%"; // 第一步时进度线为0
  }

  // 使用更简单的计算方式
  // 进度线应该覆盖到当前步骤的圆圈中心
  // 由于使用了flex布局，每个步骤占用相等的空间
  const progressPercentage = (currentStepIndex / (totalSteps - 1)) * 100;
  return `${progressPercentage}%`;
});

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1:
      return !!simulationType.value;
    case 2:
      return (
        simulationData.startTime &&
        simulationData.endTime &&
        simulationData.dataSource
      );
    case 3:
      return true; // 参数设置是可选的
    default:
      return true;
  }
});

// 处理模拟结果数据，按分类分组
const groupedResults = computed(() => {
  if (!simulationResultData.value) return {};

  const grouped: Record<string, any[]> = {};

  // 根据工艺类型选择相应的字段映射
  const fieldMappings =
    props.processType === "AAO"
      ? aaoOfflineFieldMappings
      : mbrOfflineFieldMappings;

  // 遍历所有字段映射
  fieldMappings.forEach((mapping) => {
    const value = simulationResultData.value[mapping.fieldName];
    if (value !== undefined && value !== null) {
      const category = mapping.category || "其他";
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push({
        fieldName: mapping.fieldName,
        displayName: mapping.displayName,
        value: value,
        unit: mapping.unit || "",
      });
    }
  });

  return grouped;
});

// 方法
const selectSimulationType = (type: "dynamic" | "steady") => {
  simulationType.value = type;
};

const nextStep = () => {
  if (canProceed.value && currentStep.value < 5) {
    currentStep.value++;
    // 如果进入第五步，自动加载图表数据
    if (currentStep.value === 5) {
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
    "3": "化验室数据",
  };
  return sources[source] || "未知";
};

// 生成模拟数据（实际应用中应该从API获取）
const generateMockSimulationData = () => {
  const mockData: Record<string, number> = {};

  if (props.processType === "AAO") {
    // 生成AAO进水量数据
    mockData.aao_influent_1_q_ted = Math.round(Math.random() * 20000 + 30000); // 30000-50000 m³/d
    mockData.aao_influent_2_q_ted = Math.round(Math.random() * 20000 + 30000); // 30000-50000 m³/d

    // 生成AAO出水参数数据
    mockData.aao_effluent_q_ted = Math.round(Math.random() * 50000 + 40000); // 40000-90000 m³/d
    mockData.aao_effluent_tcod_ted =
      Math.round((Math.random() * 10 + 20) * 100) / 100; // 20-30 mg/L
    mockData.aao_effluent_tbod_ted =
      Math.round((Math.random() * 5 + 5) * 100) / 100; // 5-10 mg/L
    mockData.aao_effluent_ss_ted =
      Math.round((Math.random() * 10 + 5) * 100) / 100; // 5-15 mg/L
    mockData.aao_effluent_tp_ted =
      Math.round((Math.random() * 0.4 + 0.3) * 100) / 100; // 0.3-0.7 mg/L
    mockData.aao_effluent_tn_ted =
      Math.round((Math.random() * 4 + 6) * 100) / 100; // 6-10 mg/L
    mockData.aao_effluent_snhx_ted =
      Math.round((Math.random() * 1 + 1.5) * 100) / 100; // 1.5-2.5 mg/L
    mockData.aao_effluent_snox_ted =
      Math.round((Math.random() * 2 + 3) * 100) / 100; // 3-5 mg/L
    mockData.aao_effluent_spo4_ted =
      Math.round((Math.random() * 0.2 + 0.1) * 100) / 100; // 0.1-0.3 mg/L

    // 生成AAO曝气参数数据 - 1-1#AAO生化池好氧段1-5
    mockData.aao_cstr3_1_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000); // 2000-3000 Nm³/d
    mockData.aao_cstr4_1_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr5_1_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr6_1_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr7_1_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);

    // 生成AAO曝气参数数据 - 1-2#AAO生化池好氧段1-5
    mockData.aao_cstr3_1_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr4_1_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr5_1_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr6_1_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr7_1_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);

    // 生成AAO曝气参数数据 - 2-1#AAO生化池好氧段1-5
    mockData.aao_cstr3_2_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr4_2_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr5_2_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr6_2_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr7_2_1_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);

    // 生成AAO曝气参数数据 - 2-2#AAO生化池好氧段1-5
    mockData.aao_cstr3_2_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr4_2_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr5_2_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr6_2_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);
    mockData.aao_cstr7_2_2_qair_ntp_ted = Math.round(Math.random() * 1000 + 2000);

    // 生成AAO投加参数
    mockData.aao_pac_q_ted = Math.round((Math.random() * 10 + 5) * 100) / 100; // 5-15 mg/L

    // 生成AAO回流参数
    mockData.aao_ras_1_q_ted = Math.round(Math.random() * 2000 + 5000); // 5000-7000 m³/d
    mockData.aao_ras_2_q_ted = Math.round(Math.random() * 2000 + 5000); // 5000-7000 m³/d
  } else {
    // 生成MBR出水参数数据
    mockData.mbr_effluent_q_ted = Math.round(Math.random() * 30000 + 20000); // 20000-50000 m³/d
    mockData.mbr_effluent_cod_ted =
      Math.round((Math.random() * 5 + 15) * 100) / 100; // 15-20 mg/L
    mockData.mbr_effluent_nh3n_ted =
      Math.round((Math.random() * 0.5 + 0.5) * 100) / 100; // 0.5-1.0 mg/L
    mockData.mbr_effluent_tn_ted =
      Math.round((Math.random() * 2 + 3) * 100) / 100; // 3-5 mg/L
    mockData.mbr_effluent_tp_ted =
      Math.round((Math.random() * 0.1 + 0.1) * 100) / 100; // 0.1-0.2 mg/L
    mockData.mbr_effluent_ss_ted =
      Math.round((Math.random() * 2 + 1) * 100) / 100; // 1-3 mg/L
    mockData.mbr_effluent_no3_ted =
      Math.round((Math.random() * 1 + 2) * 100) / 100; // 2-3 mg/L
    mockData.mbr_effluent_ph_ted =
      Math.round((Math.random() * 0.5 + 6.5) * 100) / 100; // 6.5-7.0

    // 生成MBR曝气参数数据
    const zones = ["zone1", "zone2", "zone3", "zone4"];
    zones.forEach((zone) => {
      const fieldName = `mbr_aerobic_${zone}_qair_ted`;
      mockData[fieldName] = Math.round(Math.random() * 500 + 1000); // 1000-1500 Nm³/d
    });

    // 生成MBR投加参数
    mockData.mbr_pac_dosage_ted =
      Math.round((Math.random() * 5 + 2) * 100) / 100; // 2-7 mg/L

    // 生成MBR回流参数
    mockData.mbr_mlr_return_flow_ted = Math.round(Math.random() * 1000 + 2000); // 2000-3000 m³/d
    mockData.mbr_ras_return_flow_ted = Math.round(Math.random() * 500 + 1000); // 1000-1500 m³/d
    mockData.mbr_sas_sludge_rate_ted = Math.round(Math.random() * 100 + 200); // 200-300 m³/d
  }

  return mockData;
};

// 从后端加载模拟结果数据
const loadSimulationResultData = async () => {
  try {
    console.log("开始从后端加载模拟结果数据...");

    // 根据开始时间查询数据
    if (props.processType === "AAO" && simulationData.startTime) {
      // 将ISO格式转换为后端需要的格式
      const formattedStartTime = formatTimeForAPI(simulationData.startTime);
      console.log("根据开始时间查询数据:", formattedStartTime);
      
      const response = await aaoSimulationService.getOfflineResultByStartTime(formattedStartTime);

      if (response.success && response.data) {
        console.log("成功获取模拟结果:", response.data);

        // 转换数据格式以匹配前端显示需求
        const formattedData: Record<string, number> = {};

        if (response.data.fields) {
          // 如果返回的是包含fields的数据结构
          Object.keys(response.data.fields).forEach((fieldName) => {
            const fieldData = response.data.fields[fieldName];
            if (fieldData && typeof fieldData.value !== "undefined" && fieldData.value !== null) {
              formattedData[fieldName] = fieldData.value;
            }
          });
        } else {
          // 如果返回的是直接的字段数据
          Object.keys(response.data).forEach((fieldName) => {
            if (
              fieldName !== "timestamp" &&
              typeof response.data[fieldName] === "number"
            ) {
              formattedData[fieldName] = response.data[fieldName];
            }
          });
        }

        simulationResultData.value = formattedData;
        console.log("模拟结果数据已设置:", formattedData);
        return;
      }
    }

    // 如果AAO类型查询失败，或者不是AAO类型，尝试获取最新数据
    const response = await aaoSimulationService.getLatestOfflineResult();

    if (response.success && response.data) {
      console.log("成功获取最新模拟结果:", response.data);

      // 转换数据格式以匹配前端显示需求
      const formattedData: Record<string, number> = {};

      if (response.data.fields) {
        // 如果返回的是包含fields的数据结构
        Object.keys(response.data.fields).forEach((fieldName) => {
          const fieldData = response.data.fields[fieldName];
          if (fieldData && typeof fieldData.value !== "undefined" && fieldData.value !== null) {
            formattedData[fieldName] = fieldData.value;
          }
        });
      } else {
        // 如果返回的是直接的字段数据
        Object.keys(response.data).forEach((fieldName) => {
          if (
            fieldName !== "timestamp" &&
            typeof response.data[fieldName] === "number"
          ) {
            formattedData[fieldName] = response.data[fieldName];
          }
        });
      }

      simulationResultData.value = formattedData;
      console.log("模拟结果数据已设置:", formattedData);
    } else {
      console.warn("未获取到模拟结果数据，使用模拟数据");
      // 如果无法获取真实数据，使用模拟数据作为备选
      simulationResultData.value = generateMockSimulationData();
    }
  } catch (error) {
    console.error("加载模拟结果数据失败:", error);
    // 出错时使用模拟数据
    simulationResultData.value = generateMockSimulationData();
  }
};

// 获取字段值的辅助函数
const getFieldValue = (fieldName: string): string => {
  if (!simulationResultData.value) return "";
  const value = simulationResultData.value[fieldName];
  if (value === null || value === undefined) return "";
  // 格式化数值显示，保留2位小数
  if (typeof value === "number") {
    return value.toFixed(2);
  }
  return String(value);
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

const startSimulation = async () => {
  isRunning.value = true;
  progress.value = 0;

  // 进度定时器
  let progressInterval: number | null = null;

  try {
    // 构建API请求数据
    let requestData: any = {
      start_time: formatTimeForAPI(simulationData.startTime),
      end_time: formatTimeForAPI(simulationData.endTime),
      data_source: parseInt(simulationData.dataSource),
    };

    // 如果不使用原始数据且是AAO模式，添加所有参数
    if (!useOriginalData.value && props.processType === "AAO") {
      // 曝气参数
      aaoBioreactors.forEach((bioreactor, idx) => {
        const index = idx + 1;
        bioreactor.zones.forEach((zone) => {
          if (zone.id === "front") {
            requestData[`opt1_aao_aer_fro_air_${index}`] = zone.value;
          } else if (zone.id === "middle") {
            requestData[`opt1_aao_aer_mid_air_${index}`] = zone.value;
          } else if (zone.id === "rear") {
            requestData[`opt1_aao_aer_bac_air_${index}`] = zone.value;
          }
        });
      });

      // 外回流和剩余污泥量
      aaoRecycleBioreactors.forEach((bioreactor, idx) => {
        const index = idx + 1;
        bioreactor.zones.forEach((zone) => {
          if (zone.id === "external") {
            requestData[`opt1_aao_ras_flow_${index}`] = zone.value;
          } else if (zone.id === "sludge") {
            requestData[`opt1_aao_was_flow_${index}`] = zone.value;
          }
        });
      });

      // 内回流
      aaoInternalRecycleBioreactors.forEach((bioreactor) => {
        bioreactor.zones.forEach((zone, zoneIdx) => {
          let paramIndex;
          if (bioreactor.id === "1") {
            paramIndex = zoneIdx + 1; // 1-1对应1, 1-2对应2
          } else {
            paramIndex = zoneIdx + 3; // 2-1对应3, 2-2对应4
          }
          requestData[`opt1_aao_int_ref_flow_${paramIndex}`] = zone.value;
        });
      });

      // 多点进水比例
      aaoInletBioreactors.forEach((bioreactor, idx) => {
        const index = idx + 1;
        bioreactor.zones.forEach((zone) => {
          if (zone.id === "selection") {
            requestData[`opt1_aao_sel_inf_rat_${index}`] = zone.value;
          } else if (zone.id === "anaerobic") {
            requestData[`opt1_aao_ana_inf_rat_${index}`] = zone.value;
          } else if (zone.id === "anoxic") {
            requestData[`opt1_aao_ano_inf_rat_${index}`] = zone.value;
          }
        });
      });
    }

    console.log("调用API:", requestData);
    console.log("使用原始数据:", useOriginalData.value);
    console.log("原始时间数据:", {
      startTime: simulationData.startTime,
      endTime: simulationData.endTime,
      formattedStartTime: formatTimeForAPI(simulationData.startTime),
      formattedEndTime: formatTimeForAPI(simulationData.endTime),
    });

    // 先启动进度更新到70%
    const progressPromise = new Promise<void>((resolve) => {
      progressInterval = window.setInterval(() => {
        if (progress.value < 70) {
          // 随机增加进度，直到达到70%
          const increment = Math.random() * 3 + 1; // 每次增加1-4
          progress.value = Math.min(70, progress.value + increment);
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
    const apiPromise = props.processType === "AAO"
      ? aaoSimulationService.startAAOSimulation(requestData)
      : aaoSimulationService.startMBRSimulation(requestData);

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
      throw new Error(response.message || "模拟启动失败");
    }

    // API成功返回后，从70%增加到100%
    const finalInterval = window.setInterval(() => {
      if (progress.value < 100) {
        // 从70%平滑增加到100%
        const increment = Math.random() * 5 + 2; // 每次增加2-7
        progress.value = Math.min(100, progress.value + increment);
      } else {
        progress.value = 100;
        clearInterval(finalInterval);
        isRunning.value = false;
        simulationResult.value = {
          success: true,
          message: `${props.processType}模拟完成`,
        };

        // 设置模拟结果数据（从后端API获取真实数据）
        loadSimulationResultData();
      }
    }, 200);
  } catch (error) {
    // 出错时清除进度定时器
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    console.error("模拟失败:", error);
    isRunning.value = false;
    progress.value = 0;
    // 这里可以显示错误信息
    alert(error instanceof Error ? error.message : "模拟启动失败");
  }
};

const stopSimulation = async () => {
  try {
    let response;
    if (props.processType === "AAO") {
      response = await aaoSimulationService.stopAAOSimulation();
    } else {
      response = await aaoSimulationService.stopMBRSimulation();
    }

    if (response.success) {
      isRunning.value = false;
      progress.value = 0;
    } else {
      console.error("停止模拟失败:", response.message);
    }
  } catch (error) {
    console.error("停止模拟失败:", error);
    isRunning.value = false;
    progress.value = 0;
  }
};

// 初始化默认时间（使用API示例值）
const initDefaultTime = () => {
  // 使用API示例值：2024-05-15 01:00:00 和 2024-05-15 03:00:00
  const startDate = new Date("2024-05-15T01:00:00");
  const endDate = new Date("2024-05-15T03:00:00");

  // 格式化为 datetime-local 需要的格式 (YYYY-MM-DDTHH:mm)
  const formatDate = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  simulationData.startTime = formatDate(startDate);
  simulationData.endTime = formatDate(endDate);
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
  if (!simulationData.startTime || !simulationData.endTime) {
    chartError.value = "请先设置模拟的开始时间和结束时间";
    return;
  }

  if (!selectedCategory.value) {
    chartError.value = "请选择一个类别";
    return;
  }

  chartLoading.value = true;
  chartError.value = "";

  try {
    const formattedStartTime = formatTimeForAPI(simulationData.startTime);
    const formattedEndTime = formatTimeForAPI(simulationData.endTime);
    const fieldsToQuery = getSelectedFields();

    console.log("=== 图表数据请求参数 ===");
    console.log("开始时间:", formattedStartTime);
    console.log("结束时间:", formattedEndTime);
    console.log("查询字段:", fieldsToQuery);
    console.log("选中的类别:", selectedCategory.value);

    const response = await aaoSimulationService.getSimulationResultChartData({
      start_time: formattedStartTime,
      end_time: formattedEndTime,
      field_names: fieldsToQuery,
    });

    console.log("=== API返回数据 ===");
    console.log("完整响应:", response);
    console.log("响应成功:", response.success);
    console.log("响应数据:", response.data);
    
    if (response.success && response.data) {
      console.log("图表数据:", response.data.data);
      console.log("时间序列:", response.data.times);
      console.log("数据字段:", Object.keys(response.data.data || {}));
      
      chartData.value = response.data.data || {};
      chartTimes.value = response.data.times || [];
      
      // 延迟渲染，确保DOM已更新
      nextTick(() => {
        renderCharts();
      });
    } else {
      console.error("获取数据失败:", response.message);
      chartError.value = response.message || "获取图表数据失败";
    }
  } catch (error) {
    console.error("加载图表数据失败:", error);
    chartError.value = error instanceof Error ? error.message : "加载图表数据失败";
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

        const data = chartData.value[fieldName] || [];
        console.log(`渲染图表 ${chartId}, 字段: ${fieldName}, 数据长度: ${data.length}`);

        // 初始化图表实例
        const chartInstance = echarts.init(chartElement);
        chartInstances.value.set(chartId, chartInstance);

        // 配置选项 - 只显示模拟数据
        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
            },
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            borderColor: '#00c9ff',
            borderWidth: 1,
            textStyle: {
              color: '#fff',
            },
            formatter: (params: any) => {
              if (!params || params.length === 0) return '';
              let result = `时间: ${params[0].axisValue}<br/>`;
              params.forEach((item: any) => {
                result += `${item.marker} ${item.seriesName}: ${item.value !== null && item.value !== undefined ? item.value.toFixed(2) : '无数据'}<br/>`;
              });
              return result;
            },
          },
          legend: {
            data: ['模拟'],
            top: 10,
            right: 20,
            textStyle: {
              color: '#fff',
            },
            itemWidth: 15,
            itemHeight: 10,
          },
          grid: {
            left: '8%',
            right: '8%',
            bottom: '15%',
            top: '18%',
            containLabel: true,
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: chartTimes.value,
            axisLabel: {
              color: '#9cc3ff',
              fontSize: 11,
              formatter: (value: string) => {
                // 格式化时间显示，如 "10-9 15:00"
                if (!value) return '';
                const date = new Date(value);
                const month = date.getMonth() + 1;
                const day = date.getDate();
                const hours = date.getHours().toString().padStart(2, '0');
                const minutes = date.getMinutes().toString().padStart(2, '0');
                return `${month}-${day} ${hours}:${minutes}`;
              },
            },
            axisLine: {
              lineStyle: {
                color: 'rgba(255,255,255,.25)',
              },
            },
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              color: '#9cc3ff',
              fontSize: 11,
            },
            axisLine: {
              lineStyle: {
                color: 'rgba(255,255,255,.25)',
              },
            },
            splitLine: {
              lineStyle: {
                color: 'rgba(255,255,255,.12)',
              },
            },
          },
          series: [
            {
              name: '模拟',
              type: 'line',
              data: data,
              smooth: true,
              lineStyle: {
                width: 2,
                color: '#ffcc00',
              },
              itemStyle: {
                color: '#ffcc00',
              },
              areaStyle: {
                color: {
                  type: 'linear',
                  x: 0,
                  y: 0,
                  x2: 0,
                  y2: 1,
                  colorStops: [
                    { offset: 0, color: 'rgba(255, 204, 0, 0.3)' },
                    { offset: 1, color: 'rgba(255, 204, 0, 0)' },
                  ],
                },
              },
              symbol: 'circle',
              symbolSize: 4,
            },
          ],
          animation: true,
          animationDuration: 1000,
        };

        chartInstance.setOption(option, true);
        chartInstance.resize();
    });
  });
};

// 监听选中类别变化，自动更新图表
watch(selectedCategory, () => {
  if (currentStep.value === 5 && selectedCategory.value) {
    loadChartData();
  } else if (currentStep.value === 5 && !selectedCategory.value) {
    // 清空图表
    chartInstances.value.forEach((instance) => {
      instance.dispose();
    });
    chartInstances.value.clear();
    chartData.value = {};
    chartTimes.value = [];
  }
});

// 监听窗口大小变化，调整图表大小
const handleResize = () => {
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
  window.removeEventListener('resize', handleResize);
});

// 监听器
watch(
  () => currentStep.value,
  (newStep) => {
    if (
      newStep === 2 &&
      (!simulationData.startTime || !simulationData.endTime)
    ) {
      initDefaultTime();
    }
    if (newStep === 5) {
      // 进入第五步时，添加窗口大小监听
      nextTick(() => {
        window.addEventListener('resize', handleResize);
      });
    } else {
      window.removeEventListener('resize', handleResize);
    }
  }
);
</script>

<style scoped>
.offline-simulation-mask {
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

.offline-simulation-dialog {
  width: 90%;
  max-width: 1200px;
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
  padding: 0 30px;
}

.offtitle {
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
  left: 20px; /* 从第一个圆圈中心开始 */
  height: 3px;
  background: linear-gradient(90deg, #4f46e5 0%, #10b981 100%);
  transition: all 0.3s;
  z-index: 1;
  border-radius: 2px;
  transform-origin: left center;
  /* 确保进度线能够正确覆盖到圆圈中心 */
  box-sizing: border-box;
  /* 添加一个小的偏移来确保进度线能够覆盖到圆圈中心 */
  margin-left: 20px; /* 圆圈半径的一半 */
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

.arrow {
  color: #4f46e5;
  margin-right: 10px;
  font-size: 20px;
}

.simulation-type-options {
  display: flex;
  gap: 30px;
  justify-content: center;
  margin-top: 50px;
}

.type-card {
  width: 200px;
  height: 200px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.type-card.dynamic {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.type-card.steady {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.type-card.selected {
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.type-icon {
  width: 60px;
  height: 60px;
  color: #ffffff;
  margin-bottom: 15px;
}

.type-label {
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
}

.data-settings {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

.settings-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  color: #ffffff;
  margin-bottom: 15px;
  font-weight: bold;
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

.datetime-input {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 14px;
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

.parameters-settings {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

/* AAO主设置区域 */
.aao-main-settings {
  width: 100%;
  padding: 0;
}

.aao-header-with-button {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.aao-title {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  color: #00c9ff;
  flex: 1;
  margin-right: 20px;
}

.aao-title .arrow {
  margin-right: 10px;
  font-size: 18px;
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
  white-space: nowrap;
}

.original-data-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.original-data-btn.active {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.aao-parameters-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 25px;
}

/* MBR主设置区域 */
.mbr-main-settings {
  width: 100%;
  padding: 0;
}

.mbr-title {
  font-size: 20px;
  font-weight: bold;
  color: #ffffff;
  text-align: center;
  margin-bottom: 30px;
  padding: 15px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
}

.mbr-parameters-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 25px;
}

.aao-settings {
  position: relative;
}

.settings-label {
  position: absolute;
  left: -20px;
  top: 50%;
  transform: translateY(-50%) rotate(-90deg);
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
  white-space: nowrap;
}

.parameters-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 25px;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

.param-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 15px;
}

.bioreactor-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  width: 100%;
}

.bioreactor {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 12px;
  width: 100%;
  min-width: 0;
}

.bioreactor-title {
  font-size: 12px;
  color: #ffffff;
  margin-bottom: 8px;
  font-weight: bold;
}

.zones {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.zone {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-width: 0;
}

.zone label {
  font-size: 12px;
  color: #ffffff;
  min-width: 70px;
  flex-shrink: 0;
}

.param-input {
  flex: 1;
  min-width: 0;
  padding: 6px 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 12px;
  width: 100%;
}

.unit {
  font-size: 11px;
  color: #ffffff;
  min-width: 35px;
  flex-shrink: 0;
}

.mbr-settings {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 25px;
  width: 100%;
  max-width: 100%;
}

.param-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.sub-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  padding: 10px;
}

.sub-title {
  font-size: 14px;
  color: #ffffff;
  margin-bottom: 8px;
  font-weight: bold;
}

.param-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  width: 100%;
  min-width: 0;
}

.param-row label {
  min-width: 90px;
  font-size: 12px;
  color: #ffffff;
  flex-shrink: 0;
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


/* 结果详情样式 */
.result-details {
  margin-top: 30px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 20px;
}

.details-title {
  font-size: 18px;
  color: #ffffff;
  margin-bottom: 20px;
  font-weight: bold;
  text-align: center;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-category {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
}

.category-title {
  font-size: 16px;
  color: #4f46e5;
  margin-bottom: 15px;
  font-weight: bold;
  border-bottom: 1px solid rgba(79, 70, 229, 0.3);
  padding-bottom: 8px;
}

.category-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 12px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border-left: 3px solid #4f46e5;
}

.item-label {
  color: #ffffff;
  font-size: 14px;
  flex: 1;
  min-width: 0;
}

.item-value {
  color: #10b981;
  font-size: 14px;
  font-weight: bold;
  min-width: 80px;
  text-align: right;
}

.item-unit {
  color: #6b7280;
  font-size: 12px;
  min-width: 40px;
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

.btn-chart {
  background: #10b981;
  color: #ffffff;
}

.btn-chart:hover {
  background: #059669;
}

/* AAO离线模拟结果样式 */
.aao-result-details {
  margin-top: 0;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 25px;
  border: 2px dashed rgba(255, 255, 255, 0.2);
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


.param-value {
  font-size: 13px;
  color: #10b981;
  font-weight: bold;
  min-width: 80px;
  text-align: right;
  flex-shrink: 0;
}

.param-unit {
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

.param-category {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 12px;
  border-left: 3px solid #4f46e5;
}

.category-header {
  font-size: 14px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.param-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffffff;
  font-size: 12px;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background 0.2s;
}

.param-checkbox:hover {
  background: rgba(255, 255, 255, 0.05);
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
</style>
