#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统参数服务
用于处理system_parameters表的读取和更新操作

历史记录：
2024-12-19    系统    创建系统参数服务
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from dbpkg.TDengineDB import TDengineDB
import dbpkg.DBBase

logger = logging.getLogger("DigitalTwinApp")

# 默认值（数据库字段级别）
DEFAULT_DB_VALUES: Dict[str, Any] = {
    "predict_algorithm_sp": 0,
    "predict_steps_sp": 12,
    "simulate_interval_sp": 120,
    "data_type_sp": 0,
    "calibration_period_sp": 30,
    "optimize_algorithm_sp": None,
    "cleaning_algorithm_sp": 0,
    "tolerance_cod_sp": 0,
    "tolerance_snhx_sp": 0,
    "tolerance_xtss_sp": 0,
    "tolerance_tp_sp": 0,
    "tolerance_tn_sp": 0,
    "tolerance_do_1_1_sp": 0,
    "tolerance_do_1_2_sp": 0,
    "tolerance_do_2_1_sp": 0,
    "tolerance_do_2_2_sp": 0,
    "hyper_p_iterations_sp": 0,
    "hyper_p_threshold_sp": 0,
    "hyper_p_size_sp": 0,
    "hyper_p_chaosfactor_sp": 0,
    "hyper_p_stepsize_sp": 0,
    "cleaning_objects_sp": "",
    "limit_cod_sp": 0,
    "limit_nh3_n_sp": 0,
    "limit_tp_sp": 0,
    "limit_tn_sp": 0,
    "limit_ss_sp": 0,
    "update_time_sp": None,
}

# 有限取值校验
ENUM_VALUE_MAP = {
    "predict_algorithm_sp": {0, 1},
    "predict_steps_sp": {6, 12, 24},
    "simulate_interval_sp": {60, 120, 240, 1440},
    "data_type_sp": {0, 1, 2},
    "cleaning_algorithm_sp": {0, 1, 2},
}

CLEANING_OBJECT_ALLOWED = {"AAODO", "COD", "MBRDO", "NH3-N", "SS", "TN", "TP"}

class SystemParamsService:
    """系统参数服务类"""
    
    def __init__(self):
        self.db = None
        self.connect_database()
    
    def connect_database(self):
        """连接数据库"""
        try:
            self.db = TDengineDB()
            success = self.db.connect(
                host="192.168.3.92",
                user="root",
                password="taosdata",
                database="beihu_dt",
                port=6041,
                link_mode=dbpkg.DBBase.REST_LINK,
                as_dict=True
            )
            if not success:
                logger.error("数据库连接失败")
                return False
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接异常: {str(e)}")
            return False
    
    def _get_latest_row(self) -> Optional[Dict[str, Any]]:
        """获取system_parameters表最新一行"""
        if not self.db:
            self.connect_database()
        result = self.db.query(
            table_name="system_parameters",
            select_cols=["*"],
            conditions="1=1 ORDER BY ts DESC LIMIT 1"
        )
        if result and len(result) > 0:
            return result[0]
        return None

    @staticmethod
    def _parse_cleaning_objects(value: Optional[Any]) -> List[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return []

    def _build_response_data(self, row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """将数据库原始行转换为API返回格式"""
        data = dict(DEFAULT_DB_VALUES)
        if row:
            for key in data.keys():
                if key in row and row[key] is not None:
                    data[key] = row[key]
            # 保留可能存在的其它字段（例如扩展字段）
            for key, value in row.items():
                if key not in data and key != "id":
                    data[key] = value
        # 清洗对象返回数组形式
        data["cleaning_objects_sp"] = self._parse_cleaning_objects(data.get("cleaning_objects_sp"))
        return data

    def _prepare_db_record(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """根据最新记录与更新内容构造待插入行"""
        logger.info(f"[参数范围更新] 收到更新请求，字段数量: {len(updates)}")
        logger.info(f"[参数范围更新] 更新字段列表: {list(updates.keys())}")
        logger.info(f"[参数范围更新] 更新字段值: {updates}")
        
        latest_row = self._get_latest_row()
        if latest_row:
            logger.info(f"[参数范围更新] 获取到最新记录，包含字段数: {len(latest_row)}")
        else:
            logger.warning("[参数范围更新] 未获取到最新记录，将使用默认值")
        
        record = dict(DEFAULT_DB_VALUES)
        allowed_keys = set(DEFAULT_DB_VALUES.keys())

        # 先复制最新记录的所有字段（包括不在DEFAULT_DB_VALUES中的字段）
        # 但是排除上下限字段，因为上下限字段应该只保留本次更新的值
        if latest_row:
            for key, value in latest_row.items():
                if key != "id" and key != "ts":  # 排除id和时间戳
                    # 排除所有上下限字段，这些字段应该只保留本次更新的值
                    if "upper_limit" in key or "lower_limit" in key:
                        logger.debug(f"[参数范围更新] 跳过复制上下限字段: {key} (将使用本次更新的值)")
                        continue
                    record[key] = value
                    logger.debug(f"[参数范围更新] 从最新记录复制字段: {key} = {value}")

        # 处理更新字段
        for key, value in updates.items():
            if key == "cleaning_objects_sp":
                if isinstance(value, list):
                    filtered = [str(item).strip() for item in value if str(item).strip()]
                    record[key] = ",".join(filtered)
                elif value is None:
                    record[key] = ""
                else:
                    record[key] = str(value)
                logger.info(f"[参数范围更新] 更新字段 {key} = {record[key]}")
            elif key in allowed_keys:
                # 标准字段，进行类型处理
                if isinstance(value, str) and value.strip() == "":
                    record[key] = None
                else:
                    record[key] = value
                logger.info(f"[参数范围更新] 更新标准字段 {key} = {record[key]}")
            else:
                # 不在allowed_keys中的字段（如新的上下限字段），直接添加
                if isinstance(value, str) and value.strip() == "":
                    record[key] = None
                else:
                    record[key] = value
                logger.info(f"[参数范围更新] 更新扩展字段 {key} = {record[key]} (不在DEFAULT_DB_VALUES中)")

        # 校验枚举值
        for enum_key, allowed in ENUM_VALUE_MAP.items():
            if enum_key in record and record[enum_key] is not None:
                if record[enum_key] not in allowed:
                    raise ValueError(f"{enum_key} 取值非法: {record[enum_key]}")

        # 校验清洗对象
        if "cleaning_objects_sp" in record and record["cleaning_objects_sp"]:
            selected = [item.strip() for item in record["cleaning_objects_sp"].split(",") if item.strip()]
            invalid = [item for item in selected if item not in CLEANING_OBJECT_ALLOWED]
            if invalid:
                raise ValueError(f"cleaning_objects_sp 包含非法选项: {invalid}")

        current_ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        record["ts"] = current_ts_str
        if "update_time_sp" in record:
            record["update_time_sp"] = current_ts_str
        record.pop("id", None)

        # 统计要更新的字段
        updated_field_count = len([k for k in updates.keys() if k in record])
        logger.info(f"[参数范围更新] 准备插入记录，总字段数: {len(record)}, 更新字段数: {updated_field_count}")
        logger.info(f"[参数范围更新] 最终记录包含的上下限字段: {[k for k in record.keys() if 'upper_limit' in k or 'lower_limit' in k]}")
        logger.debug(f"[参数范围更新] 完整记录: {record}")
        return record

    @staticmethod
    def _convert_value_for_sql(value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, str):
            escaped_value = value.replace("'", "''")
            return f"'{escaped_value}'"
        if isinstance(value, bool):
            return "1" if value else "0"
        return str(value)

    def _execute_insert_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """执行插入操作"""
        columns = ",".join(record.keys())
        values = ",".join(self._convert_value_for_sql(v) for v in record.values())
        sql = f"INSERT INTO system_parameters ({columns}) VALUES ({values})"

        try:
            logger.info(f"[参数范围更新] 准备执行SQL，字段数: {len(record.keys())}")
            logger.info(f"[参数范围更新] SQL字段列表: {list(record.keys())[:20]}...")  # 只显示前20个字段
            logger.info(f"[参数范围更新] 执行SQL: {sql[:500]}...")  # 只显示前500个字符
            
            # 检查上下限字段是否在SQL中
            upper_limit_fields = [k for k in record.keys() if 'upper_limit' in k]
            lower_limit_fields = [k for k in record.keys() if 'lower_limit' in k]
            logger.info(f"[参数范围更新] SQL中包含上限字段数: {len(upper_limit_fields)}")
            logger.info(f"[参数范围更新] SQL中包含下限字段数: {len(lower_limit_fields)}")
            if upper_limit_fields:
                logger.info(f"[参数范围更新] 示例上限字段: {upper_limit_fields[:5]}")
            if lower_limit_fields:
                logger.info(f"[参数范围更新] 示例下限字段: {lower_limit_fields[:5]}")
            
            self.db.execute(sql)
            logger.info("[参数范围更新] SQL执行成功")
            return {"success": True, "message": "系统参数更新成功"}
        except Exception as sql_error:
            logger.error(f"[参数范围更新] SQL执行失败: {sql_error}")
            logger.error(f"[参数范围更新] 执行的SQL: {sql[:1000]}...")  # 显示前1000个字符
            import traceback
            logger.error(f"[参数范围更新] 错误堆栈: {traceback.format_exc()}")
            return {"success": False, "message": f"更新失败: {sql_error}"}

    def get_system_params(self) -> Dict[str, Any]:
        """获取系统参数全集"""
        try:
            if not self.db:
                self.connect_database()
            latest_row = self._get_latest_row()
            data = self._build_response_data(latest_row)
            return {
                "success": True,
                "data": data,
                "message": "获取成功"
            }
        except Exception as e:
            logger.error(f"获取系统参数失败: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"获取失败: {str(e)}"
            }

    def update_system_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """更新系统参数，params 采用数据库字段命名"""
        try:
            logger.info(f"[参数范围更新] update_system_params 被调用，收到参数类型: {type(params)}")
            if not isinstance(params, dict):
                raise ValueError("参数必须是JSON对象")
            
            logger.info(f"[参数范围更新] 参数键列表: {list(params.keys())[:20]}...")  # 显示前20个键
            logger.info(f"[参数范围更新] 参数总数: {len(params)}")
            
            # 检查上下限字段
            upper_limit_params = {k: v for k, v in params.items() if 'upper_limit' in k}
            lower_limit_params = {k: v for k, v in params.items() if 'lower_limit' in k}
            logger.info(f"[参数范围更新] 收到的上限字段数: {len(upper_limit_params)}")
            logger.info(f"[参数范围更新] 收到的下限字段数: {len(lower_limit_params)}")
            if upper_limit_params:
                logger.info(f"[参数范围更新] 示例上限字段和值: {dict(list(upper_limit_params.items())[:3])}")
            if lower_limit_params:
                logger.info(f"[参数范围更新] 示例下限字段和值: {dict(list(lower_limit_params.items())[:3])}")
            
            if not self.db:
                self.connect_database()

            record = self._prepare_db_record(params)
            result = self._execute_insert_record(record)
            if result.get("success"):
                response_data = self._build_response_data(record)
                result["data"] = response_data
                logger.info("[参数范围更新] 更新成功，已返回响应数据")
            else:
                logger.error(f"[参数范围更新] 更新失败: {result.get('message')}")
            return result
        except Exception as e:
            logger.error(f"[参数范围更新] 更新系统参数失败: {str(e)}")
            import traceback
            logger.error(f"[参数范围更新] 错误堆栈: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"更新失败: {str(e)}"
            }

    def get_predict_algorithm(self) -> Dict[str, Any]:
        """
        获取当前预测算法
        返回: {
            "success": bool,
            "algorithm": "arima" | "transformer",
            "value": int,  # 0代表arima, 1代表transformer
            "message": str
        }
        """
        try:
            result = self.get_system_params()
            if not result.get("success"):
                return {
                    "success": False,
                    "algorithm": "arima",
                    "value": 0,
                    "message": result.get("message", "获取失败")
                }
            data = result.get("data") or {}
            predict_value = data.get("predict_algorithm_sp", 0)
            algorithm = "transformer" if predict_value == 1 else "arima"
            return {
                "success": True,
                "algorithm": algorithm,
                "value": predict_value,
                "message": "获取成功"
            }
            
        except Exception as e:
            logger.error(f"获取预测算法失败: {str(e)}")
            return {
                "success": False,
                "algorithm": "arima",
                "value": 0,
                "message": f"获取失败: {str(e)}"
            }
    
    def update_predict_algorithm(self, algorithm: str) -> Dict[str, Any]:
        """
        更新预测算法
        参数:
            algorithm: "arima" 或 "transformer"
        返回: {
            "success": bool,
            "message": str
        }
        """
        try:
            if algorithm not in ["arima", "transformer"]:
                return {
                    "success": False,
                    "message": f"无效的算法值: {algorithm}，只能是arima或transformer"
                }
            
            predict_algorithm_sp = 1 if algorithm == "transformer" else 0
            result = self.update_system_params({"predict_algorithm_sp": predict_algorithm_sp})
            if result.get("success"):
                result["message"] = "预测算法更新成功"
            return result
                
        except Exception as e:
            logger.error(f"更新预测算法失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": f"更新失败: {str(e)}"
            }
    
    def close(self):
        """关闭数据库连接"""
        if self.db:
            try:
                self.db.close()
            except Exception as e:
                logger.error(f"关闭数据库连接失败: {str(e)}")

# 创建全局服务实例
_system_params_service = None

def get_system_params_service():
    """获取系统参数服务实例（单例模式）"""
    global _system_params_service
    if _system_params_service is None:
        _system_params_service = SystemParamsService()
    return _system_params_service

