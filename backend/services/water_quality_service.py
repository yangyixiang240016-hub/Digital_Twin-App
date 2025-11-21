from models.tdengine import get_latest_row
from models.tdengine import get_earliest_row

# ---------------------------------------------------
# 实时水质参数（从 realtime_data 表中读取）
# ---------------------------------------------------

def get_realtime_inflow_quality():
    """
    获取全场进水水质的实时数据（来自 aao_influent_1_1_xxx_rd 字段）
    表：realtime_data
    """
    row = get_latest_row(
        table="realtime_data",
        cols=[
            "aao_influent_1_1_tcod_rd",  # COD
            "aao_influent_1_1_snhx_rd",  # NH3-N
            "aao_influent_1_1_tn_rd",    # TN
            "aao_influent_1_1_tp_rd",    # TP
            "aao_influent_1_1_ph_rd",    # pH
            "aao_influent_1_1_t_rd",     # T
        ]
    )
    return {
        "cod": row.get("aao_influent_1_1_tcod_rd"),
        "nh3n": row.get("aao_influent_1_1_snhx_rd"),
        "tn": row.get("aao_influent_1_1_tn_rd"),
        "tp": row.get("aao_influent_1_1_tp_rd"),
        "ph": row.get("aao_influent_1_1_ph_rd"),
        "t": row.get("aao_influent_1_1_t_rd")
    }

# ---------------------------------------------------
# 预测水质参数（从 predict_input_aao 表中读取）
# ---------------------------------------------------

def get_predicted_inflow_quality():
    """
    获取全场进水水质的预测数据（来自 aao_influent_1_1_xxx_pi 字段）
    表：predict_input_aao
    """
    row = get_latest_row(
        table="predict_input_aao",
        cols=[
            "aao_influent_1_1_tcod_pi",  # COD
            "aao_influent_1_1_snhx_pi",  # NH3-N
            "aao_influent_1_1_tn_pi",    # TN
            "aao_influent_1_1_tp_pi",    # TP
            "aao_influent_1_1_ph_pi",    # pH
            "aao_influent_1_1_t_pi",     # T
        ]
    )
    return {
        "cod": row.get("aao_influent_1_1_tcod_pi"),
        "nh3n": row.get("aao_influent_1_1_snhx_pi"),
        "tn": row.get("aao_influent_1_1_tn_pi"),
        "tp": row.get("aao_influent_1_1_tp_pi"),
        "ph": row.get("aao_influent_1_1_ph_pi"),
        "t": row.get("aao_influent_1_1_t_pi")
    }

# ---------------------------------------------------
# ✅ 实时出水水质参数（来自 realtime_data 表）
# ---------------------------------------------------

def get_realtime_outflow_quality():
    """
    获取全场出水水质的实时数据
    表：realtime_data
    字段：
        - effluent_tol_cod_rd   → COD
        - effluent_tol_snhx_rd  → NH3-N
        - effluent_tol_tn_rd    → TN
        - effluent_tol_tp_rd    → TP
        - effluent_tol_ss_rd    → SS
        - effluent_tol_ph_rd    → pH
    """
    row = get_latest_row(
        table="realtime_data",
        cols=[
            "effluent_tol_cod_rd",
            "effluent_tol_snhx_rd",
            "effluent_tol_tn_rd",
            "effluent_tol_tp_rd",
            "effluent_tol_ss_rd",
            "effluent_tol_ph_rd"
        ]
    )
    return {
        "cod": row.get("effluent_tol_cod_rd"),
        "nh3n": row.get("effluent_tol_snhx_rd"),
        "tn": row.get("effluent_tol_tn_rd"),
        "tp": row.get("effluent_tol_tp_rd"),
        "ss": row.get("effluent_tol_ss_rd"),
        "ph": row.get("effluent_tol_ph_rd")
    }

# ---------------------------------------------------
# ✅ 模拟出水水质参数（来自 simulate_result_effluent 表）
# ---------------------------------------------------

def get_simulated_outflow_quality():
    """
    获取全场出水水质的模拟结果
    表：simulate_result_aao
    字段：
        - aao_effluent_tcod_sr   → COD
        - aao_effluent_snhx_sr   → NH3-N
        - aao_effluent_tn_sr     → TN
        - aao_effluent_tp_sr     → TP
        - aao_effluent_ss_sr     → SS
    """
    row = get_latest_row(
        table="simulate_result_aao",
        cols=[
            "aao_effluent_tcod_sr",
            "aao_effluent_snhx_sr",
            "aao_effluent_tn_sr",
            "aao_effluent_tp_sr",
            "aao_effluent_ss_sr",
        ]
    )
    return {
        "cod": row.get("aao_effluent_tcod_sr"),
        "nh3n": row.get("aao_effluent_snhx_sr"),
        "tn": row.get("aao_effluent_tn_sr"),
        "tp": row.get("aao_effluent_tp_sr"),
        "ss": row.get("aao_effluent_ss_sr"),
        "ph": row.get("aao_effluent_ph_sr") if "aao_effluent_ph_sr" in row else None
    }

# ---------------------------------------------------
# ✅ 预测出水水质参数（来自 predict_output_effluent 表）
# ---------------------------------------------------

def get_predicted_outflow_quality():
    """
    获取全场出水水质的预测值
    表：predict_output_aao
    字段：
        - aao_effluent_tcod_po   → COD
        - aao_effluent_snhx_po   → NH3-N
        - aao_effluent_tn_po     → TN
        - aao_effluent_tp_po     → TP
        - aao_effluent_ss_po     → SS
    """
    row = get_latest_row(
        table="predict_output_aao",
        cols=[
            "aao_effluent_tcod_po",
            "aao_effluent_snhx_po",
            "aao_effluent_tn_po",
            "aao_effluent_tp_po",
            "aao_effluent_ss_po",
        ]
    )
    return {
        "cod": row.get("aao_effluent_tcod_po"),
        "nh3n": row.get("aao_effluent_snhx_po"),
        "tn": row.get("aao_effluent_tn_po"),
        "tp": row.get("aao_effluent_tp_po"),
        "ss": row.get("aao_effluent_ss_po"),
        "ph": row.get("aao_effluent_ph_po") if "aao_effluent_ph_po" in row else None
    }
