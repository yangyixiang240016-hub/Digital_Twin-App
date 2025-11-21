from models.tdengine import query_raw
from datetime import datetime, timedelta

# 参数配置映射
param_map = {
    "total_flow": {
        "unit": "m³/d",
        "realtime_in": ("online_cleaning_data", "influent_tol_q_cd"),
        "predict_in": None,  # 预测进水无总流量
        "realtime_out": ("realtime_data", "effluent_tol_q_rd"),
        "predict_out": None  # 预测出水无总流量
    },
    "aao_flow": {
        "unit": "m³/d",
        "realtime_in": ("online_cleaning_data", "aao_influent_q_cd"),
        "predict_in": ("predict_input_aao", "aao_influent_q_pi", "predict_time_pi"),
        "realtime_out": ("realtime_data", "aao_effluent_dis1_q_rd"),
        "predict_out": ("predict_output_aao", "aao_effluent_q_po", "predict_time_po")
    },
    "cod": {
        "unit": "mg/L",
        "realtime_in": ("online_cleaning_data", "aao_influent_1_1_tcod_cd"),
        "predict_in": ("predict_input_aao", "aao_influent_1_1_tcod_pi", "predict_time_pi"),
        "realtime_out": ("realtime_data", "effluent_tol_cod_rd"),
        "predict_out": ("predict_output_aao", "aao_effluent_tcod_po", "predict_time_po")
    },
    "nh3n": {
        "unit": "mg/L",
        "realtime_in": ("online_cleaning_data", "aao_influent_1_1_snhx_cd"),
        "predict_in": ("predict_input_aao", "aao_influent_1_1_snhx_pi", "predict_time_pi"),
        "realtime_out": ("realtime_data", "effluent_tol_snhx_rd"),
        "predict_out": ("predict_output_aao", "aao_effluent_snhx_po", "predict_time_po")
    },
    "tn": {
        "unit": "mg/L",
        "realtime_in": ("online_cleaning_data", "aao_influent_1_1_tn_cd"),
        "predict_in": ("predict_input_aao", "aao_influent_1_1_tn_pi", "predict_time_pi"),
        "realtime_out": ("realtime_data", "effluent_tol_tn_rd"),
        "predict_out": ("predict_output_aao", "aao_effluent_tn_po", "predict_time_po")
    },
    "tp": {
        "unit": "mg/L",
        "realtime_in": ("online_cleaning_data", "aao_influent_1_1_tp_cd"),
        "predict_in": ("predict_input_aao", "aao_influent_1_1_tp_pi", "predict_time_pi"),
        "realtime_out": ("realtime_data", "effluent_tol_tp_rd"),
        "predict_out": ("predict_output_aao", "aao_effluent_tp_po", "predict_time_po")
    },
    "ss": {
        "unit": "mg/L",
        "realtime_in": ("online_cleaning_data", "aao_influent_1_1_ss_cd"),
        "predict_in": None,  # 预测进水无SS
        "realtime_out": ("realtime_data", "effluent_tol_ss_rd"),
        "predict_out": ("predict_output_aao", "aao_effluent_ss_po", "predict_time_po")
    }
}


def get_trend_data(param: str):
    if param not in param_map:
        raise ValueError(f"不支持的参数类型: {param}")
    mapping = param_map[param]

    # 获取实时数据的时间轴（最近24小时奇数小时点数据，每两小时采样一次，如1点、3点、5点等）
    realtime_times = get_recent_24_hours_int()
    
    # 获取预测数据的时间轴
    predict_in_times = []
    predict_out_times = []
    
    if mapping.get("predict_in"):
        predict_in_times = get_predict_input_times()
    
    if mapping.get("predict_out"):
        predict_out_times = get_predict_output_times()
    
    # 合并所有时间轴
    all_times = set(realtime_times)
    all_times.update(predict_in_times)
    all_times.update(predict_out_times)
    all_times = sorted(list(all_times))
    
    # 转换为字符串格式用于显示
    times_str = [ts_to_str(t) for t in all_times]

    result = {"times": times_str, "unit": mapping.get("unit", "")}

    # 获取实时进水数据
    if mapping.get("realtime_in"):
        table, column = mapping["realtime_in"]
        values = fetch_realtime_data(table, column, all_times)
    else:
        values = [None] * len(all_times)
    result["realtime_in"] = values

    # 获取预测进水数据
    if mapping.get("predict_in"):
        table, column, time_col = mapping["predict_in"]
        values = fetch_predict_input_data(table, column, time_col, all_times)
    else:
        values = [None] * len(all_times)
    result["predict_in"] = values

    # 获取实时出水数据
    if mapping.get("realtime_out"):
        table, column = mapping["realtime_out"]
        values = fetch_realtime_data(table, column, all_times)
    else:
        values = [None] * len(all_times)
    result["realtime_out"] = values

    # 获取预测出水数据
    if mapping.get("predict_out"):
        table, column, time_col = mapping["predict_out"]
        values = fetch_predict_output_data(table, column, time_col, all_times)
    else:
        values = [None] * len(all_times)
    result["predict_out"] = values

    return result


def ts_to_str(ts: int) -> str:
    """将时间戳（毫秒）转换为字符串格式"""
    return datetime.fromtimestamp(ts / 1000).strftime("%m/%d %H:%M")


def to_timestamp_ms(value):
    """将时间值转换为毫秒时间戳（支持datetime对象或整数时间戳）"""
    if isinstance(value, datetime):
        return int(value.timestamp() * 1000)
    elif isinstance(value, (int, float)):
        # 如果是整数或浮点数，假设已经是毫秒时间戳
        return int(value)
    elif isinstance(value, str):
        # 如果是字符串，尝试解析
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        except:
            return int(value)
    else:
        raise ValueError(f"无法转换时间值: {type(value)}")


def get_recent_24_hours_int():
    """获取最近24小时的奇数小时整点时间戳（毫秒）列表（每两小时采样一次，如1点、3点、5点等）"""
    # 计算24小时前的时间戳（毫秒）
    now = datetime.now()
    hours_24_ago = now - timedelta(hours=24)
    hours_24_ago_ts = int(hours_24_ago.timestamp() * 1000)
    
    # 从两个表中查询整点时间戳，然后合并去重，只保留奇数小时
    # online_cleaning_data 用于实时进水
    # realtime_data 用于实时出水
    hour_set = set()
    
    # 查询 online_cleaning_data 表的整点时间戳
    sql1 = f"""
        SELECT DISTINCT FLOOR(ts / 3600000) * 3600000 AS hour_ts
        FROM online_cleaning_data
        WHERE ts >= {hours_24_ago_ts}
    """
    try:
        rows1 = query_raw(sql1)
        if rows1:
            for r in rows1:
                hour_ts = int(r["hour_ts"])
                # 将时间戳转换为datetime对象，检查是否为奇数小时
                hour_dt = datetime.fromtimestamp(hour_ts / 1000)
                # 只保留奇数小时（1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23）
                if hour_dt.hour % 2 == 1:
                    hour_set.add(hour_ts)
    except Exception as e:
        print(f"[get_recent_24_hours_int] 查询 online_cleaning_data 失败: {str(e)}")
    
    # 查询 realtime_data 表的整点时间戳
    sql2 = f"""
        SELECT DISTINCT FLOOR(ts / 3600000) * 3600000 AS hour_ts
        FROM realtime_data
        WHERE ts >= {hours_24_ago_ts}
    """
    try:
        rows2 = query_raw(sql2)
        if rows2:
            for r in rows2:
                hour_ts = int(r["hour_ts"])
                # 将时间戳转换为datetime对象，检查是否为奇数小时
                hour_dt = datetime.fromtimestamp(hour_ts / 1000)
                # 只保留奇数小时（1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23）
                if hour_dt.hour % 2 == 1:
                    hour_set.add(hour_ts)
    except Exception as e:
        print(f"[get_recent_24_hours_int] 查询 realtime_data 失败: {str(e)}")
    
    # 返回排序后的奇数小时整点时间戳列表
    return sorted(list(hour_set))


def get_predict_steps_sp():
    """从system_parameters表中获取最新的predict_steps_sp值"""
    sql = """
        SELECT predict_steps_sp
        FROM system_parameters
        ORDER BY ts DESC
        LIMIT 1
    """
    try:
        rows = query_raw(sql)
        if rows and rows[0].get("predict_steps_sp") is not None:
            return int(rows[0]["predict_steps_sp"])
        # 如果查询失败或值为空，返回默认值12
        return 12
    except Exception as e:
        print(f"[get_predict_steps_sp] 查询失败: {str(e)}")
        return 12


def get_predict_input_times():
    """获取预测进水的时间轴（按ts排序获取最新的predict_steps_sp+1条数据，返回它们的predict_time_pi）"""
    predict_steps = get_predict_steps_sp()
    limit_count = predict_steps + 1
    
    sql = f"""
        SELECT ts, predict_time_pi
        FROM predict_input_aao
        WHERE predict_time_pi IS NOT NULL
        ORDER BY ts DESC
        LIMIT {limit_count}
    """
    try:
        rows = query_raw(sql)
        if not rows:
            return []
        # 反转以便按时间顺序排列
        rows.reverse()
        # 返回predict_time_pi的时间戳
        result = []
        for r in rows:
            predict_time = r.get("predict_time_pi")
            if predict_time is not None:
                result.append(to_timestamp_ms(predict_time))
        return result
    except Exception as e:
        print(f"[get_predict_input_times] 查询失败: {str(e)}")
        return []


def get_predict_output_times():
    """获取预测出水的时间轴（按ts排序获取最新的predict_steps_sp+1条数据，返回它们的predict_time_po）"""
    predict_steps = get_predict_steps_sp()
    limit_count = predict_steps + 1
    
    sql = f"""
        SELECT ts, predict_time_po
        FROM predict_output_aao
        WHERE predict_time_po IS NOT NULL
        ORDER BY ts DESC
        LIMIT {limit_count}
    """
    try:
        rows = query_raw(sql)
        if not rows:
            return []
        # 反转以便按时间顺序排列
        rows.reverse()
        # 返回predict_time_po的时间戳
        result = []
        for r in rows:
            predict_time = r.get("predict_time_po")
            if predict_time is not None:
                result.append(to_timestamp_ms(predict_time))
        return result
    except Exception as e:
        print(f"[get_predict_output_times] 查询失败: {str(e)}")
        return []


def fetch_realtime_data(table: str, column: str, time_axis: list):
    """获取实时数据（根据ts字段，最近24小时奇数小时点数据，每两小时采样一次，如1点、3点、5点等）"""
    if not time_axis:
        return []
    
    # 对于每个整点时间戳，查询最接近该整点的数据
    value_map = {}
    
    for hour_ts in time_axis:
        # 先尝试精确匹配整点时刻
        sql_exact = f"""
            SELECT ts, {column} AS val
            FROM {table}
            WHERE ts = {hour_ts}
              AND {column} IS NOT NULL
            LIMIT 1
        """
        
        found = False
        try:
            rows = query_raw(sql_exact)
            if rows and rows[0]["val"] is not None:
                value_map[hour_ts] = float(rows[0]["val"])
                found = True
        except Exception as e:
            print(f"[fetch_realtime_data] 精确查询失败: {table}.{column}, hour_ts={hour_ts} -> {str(e)}")
        
        # 如果精确匹配失败，则查询该小时内最接近整点的数据（整点之后5分钟内）
        if not found:
            window_end = hour_ts + 300000  # 整点后5分钟
            sql_close = f"""
                SELECT ts, {column} AS val
                FROM {table}
                WHERE ts > {hour_ts} AND ts <= {window_end}
                  AND {column} IS NOT NULL
                ORDER BY ts ASC
                LIMIT 1
            """
            try:
                rows = query_raw(sql_close)
                if rows and rows[0]["val"] is not None:
                    value_map[hour_ts] = float(rows[0]["val"])
            except Exception as e:
                print(f"[fetch_realtime_data] 接近查询失败: {table}.{column}, hour_ts={hour_ts} -> {str(e)}")
    
    # 根据时间轴返回对应的值
    return [value_map.get(ts, None) for ts in time_axis]


def fetch_predict_input_data(table: str, column: str, time_col: str, time_axis: list):
    """获取预测进水数据（按ts排序获取最新的predict_steps_sp+1条数据，使用predict_time_pi匹配时间轴）"""
    if not time_axis:
        return []
    
    predict_steps = get_predict_steps_sp()
    limit_count = predict_steps + 1
    
    # 按ts排序获取最新的predict_steps_sp+1条数据
    sql = f"""
        SELECT ts, {time_col} AS predict_time, {column} AS val
        FROM {table}
        WHERE {time_col} IS NOT NULL AND {column} IS NOT NULL
        ORDER BY ts DESC
        LIMIT {limit_count}
    """
    try:
        rows = query_raw(sql)
        if not rows:
            return [None] * len(time_axis)
        
        # 反转以便按时间顺序排列
        rows.reverse()
        
        # 构建predict_time到值的映射
        value_map = {}
        for r in rows:
            predict_time = r.get("predict_time")
            if predict_time is not None:
                predict_time_ts = to_timestamp_ms(predict_time)
                if r.get("val") is not None:
                    value_map[predict_time_ts] = float(r["val"])
        
        # 根据时间轴返回对应的值
        return [value_map.get(ts, None) for ts in time_axis]
    except Exception as e:
        print(f"[fetch_predict_input_data] 查询失败: {table}.{column} -> {str(e)}")
        return [None] * len(time_axis)


def fetch_predict_output_data(table: str, column: str, time_col: str, time_axis: list):
    """获取预测出水数据（按ts排序获取最新的predict_steps_sp+1条数据，使用predict_time_po匹配时间轴）"""
    if not time_axis:
        return []
    
    predict_steps = get_predict_steps_sp()
    limit_count = predict_steps + 1
    
    # 按ts排序获取最新的predict_steps_sp+1条数据
    sql = f"""
        SELECT ts, {time_col} AS predict_time, {column} AS val
        FROM {table}
        WHERE {time_col} IS NOT NULL AND {column} IS NOT NULL
        ORDER BY ts DESC
        LIMIT {limit_count}
    """
    try:
        rows = query_raw(sql)
        if not rows:
            return [None] * len(time_axis)
        
        # 反转以便按时间顺序排列
        rows.reverse()
        
        # 构建predict_time到值的映射
        value_map = {}
        for r in rows:
            predict_time = r.get("predict_time")
            if predict_time is not None:
                predict_time_ts = to_timestamp_ms(predict_time)
                if r.get("val") is not None:
                    value_map[predict_time_ts] = float(r["val"])
        
        # 根据时间轴返回对应的值
        return [value_map.get(ts, None) for ts in time_axis]
    except Exception as e:
        print(f"[fetch_predict_output_data] 查询失败: {table}.{column} -> {str(e)}")
        return [None] * len(time_axis)
