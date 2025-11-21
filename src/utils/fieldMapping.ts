// 离线模拟结果字段映射配置
export interface FieldMapping {
  fieldName: string;
  displayName: string;
  unit?: string;
  category?: string;
}

// AAO离线模拟结果字段映射
export const aaoOfflineFieldMappings: FieldMapping[] = [
  // 出水参数
  {
    fieldName: "aao_effluent_q_ted",
    displayName: "总出水流量",
    unit: "m³/d",
    category: "出水参数",
  },
  {
    fieldName: "aao_effluent_tcod_ted",
    displayName: "离线模拟出水化学需氧量",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "aao_effluent_tbod_ted",
    displayName: "离线模拟出水生化需氧量",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "aao_effluent_ss_ted",
    displayName: "离线模拟出水悬浮固体浓度",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "aao_effluent_tp_ted",
    displayName: "离线模拟出水总磷",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "aao_effluent_tn_ted",
    displayName: "离线模拟出水总氮",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "aao_effluent_snhx_ted",
    displayName: "离线模拟出水氨氮",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "aao_effluent_snox_ted",
    displayName: "离线模拟出水硝氮",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "aao_effluent_spo4_ted",
    displayName: "离线模拟出水正磷酸盐",
    unit: "mg/L",
    category: "出水参数",
  },

  // 曝气参数 - 1-1#AAO生化池
  {
    fieldName: "aao_cstr_front_1_1_qair_ntp_ted",
    displayName: "离线模拟1-1#AAO生化池曝气支管1曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "aao_cstr_mid_1_1_qair_ntp_ted",
    displayName: "离线模拟1-1#AAO生化池曝气支管2曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "aao_cstr_terminal_1_1_qair_ntp_ted",
    displayName: "离线模拟1-1#AAO生化池曝气支管3曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },

  // 曝气参数 - 1-2#AAO生化池
  {
    fieldName: "aao_cstr_front_1_2_qair_ntp_ted",
    displayName: "离线模拟1-2#AAO生化池曝气支管1曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "aao_cstr_mid_1_2_qair_ntp_ted",
    displayName: "离线模拟1-2#AAO生化池曝气支管2曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "aao_cstr_terminal_1_2_qair_ntp_ted",
    displayName: "离线模拟1-2#AAO生化池曝气支管3曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },

  // 曝气参数 - 2-1#AAO生化池
  {
    fieldName: "aao_cstr_front_2_1_qair_ntp_ted",
    displayName: "离线模拟2-1#AAO生化池曝气支管1曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "aao_cstr_mid_2_1_qair_ntp_ted",
    displayName: "离线模拟2-1#AAO生化池曝气支管2曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "aao_cstr_terminal_2_1_qair_ntp_ted",
    displayName: "离线模拟2-1#AAO生化池曝气支管3曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },

  // 曝气参数 - 2-2#AAO生化池
  {
    fieldName: "aao_cstr_front_2_2_qair_ntp_ted",
    displayName: "离线模拟2-2#AAO生化池曝气支管1曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "aao_cstr_mid_2_2_qair_ntp_ted",
    displayName: "离线模拟2-2#AAO生化池曝气支管2曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "aao_cstr_terminal_2_2_qair_ntp_ted",
    displayName: "离线模拟2-2#AAO生化池曝气支管3曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },

  // 投加参数
  {
    fieldName: "aao_pac_q_ted",
    displayName: "离线模拟2号加药间聚合氯化铝投加量",
    unit: "mg/L",
    category: "投加参数",
  },

  // 回流参数
  {
    fieldName: "aao_flowdivider3_1_1_influx_ted",
    displayName: "离线模拟1-1#AAO生化池内回流量",
    unit: "m³/d",
    category: "回流参数",
  },
  {
    fieldName: "aao_flowdivider3_1_2_influx_ted",
    displayName: "离线模拟1-2#AAO生化池内回流量",
    unit: "m³/d",
    category: "回流参数",
  },
  {
    fieldName: "aao_flowdivider3_2_1_influx_ted",
    displayName: "离线模拟2-1#AAO生化池内回流量",
    unit: "m³/d",
    category: "回流参数",
  },
  {
    fieldName: "aao_flowdivider3_2_2_influx_ted",
    displayName: "离线模拟2-2#AAO生化池内回流量",
    unit: "m³/d",
    category: "回流参数",
  },
];

// MBR离线模拟结果字段映射
export const mbrOfflineFieldMappings: FieldMapping[] = [
  // 出水参数
  {
    fieldName: "mbr_effluent_q_ted",
    displayName: "MBR总出水流量",
    unit: "m³/d",
    category: "出水参数",
  },
  {
    fieldName: "mbr_effluent_cod_ted",
    displayName: "MBR离线模拟出水化学需氧量",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "mbr_effluent_nh3n_ted",
    displayName: "MBR离线模拟出水氨氮",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "mbr_effluent_tn_ted",
    displayName: "MBR离线模拟出水总氮",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "mbr_effluent_tp_ted",
    displayName: "MBR离线模拟出水总磷",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "mbr_effluent_ss_ted",
    displayName: "MBR离线模拟出水悬浮固体浓度",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "mbr_effluent_no3_ted",
    displayName: "MBR离线模拟出水硝氮",
    unit: "mg/L",
    category: "出水参数",
  },
  {
    fieldName: "mbr_effluent_ph_ted",
    displayName: "MBR离线模拟出水pH值",
    unit: "",
    category: "出水参数",
  },

  // 曝气参数 - 好氧区
  {
    fieldName: "mbr_aerobic_zone1_qair_ted",
    displayName: "MBR离线模拟好氧区1曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "mbr_aerobic_zone2_qair_ted",
    displayName: "MBR离线模拟好氧区2曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "mbr_aerobic_zone3_qair_ted",
    displayName: "MBR离线模拟好氧区3曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },
  {
    fieldName: "mbr_aerobic_zone4_qair_ted",
    displayName: "MBR离线模拟好氧区4曝气量",
    unit: "Nm³/d",
    category: "曝气参数",
  },

  // 投加参数
  {
    fieldName: "mbr_pac_dosage_ted",
    displayName: "MBR离线模拟PAC投加量",
    unit: "mg/L",
    category: "投加参数",
  },

  // 回流参数
  {
    fieldName: "mbr_mlr_return_flow_ted",
    displayName: "MBR离线模拟MLR回流流量",
    unit: "m³/d",
    category: "回流参数",
  },
  {
    fieldName: "mbr_ras_return_flow_ted",
    displayName: "MBR离线模拟RAS回流流量",
    unit: "m³/d",
    category: "回流参数",
  },
  {
    fieldName: "mbr_sas_sludge_rate_ted",
    displayName: "MBR离线模拟SAS污泥量",
    unit: "m³/d",
    category: "回流参数",
  },
];

// 根据字段名获取显示名称
export function getFieldDisplayName(fieldName: string): string {
  const mapping = aaoOfflineFieldMappings.find(
    (m) => m.fieldName === fieldName
  );
  return mapping ? mapping.displayName : fieldName;
}

// 根据字段名获取MBR显示名称
export function getMBRFieldDisplayName(fieldName: string): string {
  const mapping = mbrOfflineFieldMappings.find(
    (m) => m.fieldName === fieldName
  );
  return mapping ? mapping.displayName : fieldName;
}

// 根据字段名获取单位
export function getFieldUnit(fieldName: string): string {
  const mapping = aaoOfflineFieldMappings.find(
    (m) => m.fieldName === fieldName
  );
  return mapping ? mapping.unit || "" : "";
}

// 根据字段名获取MBR单位
export function getMBRFieldUnit(fieldName: string): string {
  const mapping = mbrOfflineFieldMappings.find(
    (m) => m.fieldName === fieldName
  );
  return mapping ? mapping.unit || "" : "";
}

// 根据字段名获取分类
export function getFieldCategory(fieldName: string): string {
  const mapping = aaoOfflineFieldMappings.find(
    (m) => m.fieldName === fieldName
  );
  return mapping ? mapping.category || "其他" : "其他";
}

// 根据字段名获取MBR分类
export function getMBRFieldCategory(fieldName: string): string {
  const mapping = mbrOfflineFieldMappings.find(
    (m) => m.fieldName === fieldName
  );
  return mapping ? mapping.category || "其他" : "其他";
}

// 按分类分组字段映射
export function getFieldMappingsByCategory(): Record<string, FieldMapping[]> {
  const grouped: Record<string, FieldMapping[]> = {};

  aaoOfflineFieldMappings.forEach((mapping) => {
    const category = mapping.category || "其他";
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(mapping);
  });

  return grouped;
}

// 按分类分组MBR字段映射
export function getMBRFieldMappingsByCategory(): Record<
  string,
  FieldMapping[]
> {
  const grouped: Record<string, FieldMapping[]> = {};

  mbrOfflineFieldMappings.forEach((mapping) => {
    const category = mapping.category || "其他";
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(mapping);
  });

  return grouped;
}
