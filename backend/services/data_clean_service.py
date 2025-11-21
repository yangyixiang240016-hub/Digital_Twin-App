#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗服务层
提供从offline_cleaning_data表中读取整十分钟时间点数据的功能
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dbpkg.TDengineDB import TDengineDB
import dbpkg.DBBase

logger = logging.getLogger("DigitalTwinApp")


class DataCleanService:
    """数据清洗服务类"""
    
    def __init__(self):
        self.db = None
        self.table_name = "offline_cleaning_data"
        
        # 需要查询的字段列表
        # 注意：realtime_data 表中字段以 _rd 结尾
        self.fields = [
            "influent_tol_q_rd",      # 总进水量
            "aao_influent_q_rd",      # AAO流量
            "mbr_influent_q_rd",      # MBR流量
            "aao_influent_1_1_tcod_rd",  # COD
            "aao_influent_1_1_snhx_rd",  # NH3-N
            "aao_influent_1_1_tn_rd",    # TN
            "aao_influent_1_1_tp_rd"     # TP
        ]
        
        # offline_cleaning_data 表中字段以 _cd 结尾（清洗后的数据）
        self.fields_cleaned = [
            "influent_tol_q_cd",      # 总进水量
            "aao_influent_q_cd",      # AAO流量
            "mbr_influent_q_cd",      # MBR流量
            "aao_influent_1_1_tcod_cd",  # COD
            "aao_influent_1_1_snhx_cd",  # NH3-N
            "aao_influent_1_1_tn_cd",    # TN
            "aao_influent_1_1_tp_cd"     # TP
        ]
    
    def connect_database(self) -> bool:
        """连接数据库"""
        try:
            if self.db is None:
                self.db = TDengineDB()
            
            result = self.db.connect(
                host="192.168.3.92",
                user="root",
                password="taosdata",
                database="beihu_dt",
                port=6041,
                link_mode=dbpkg.DBBase.REST_LINK
            )
            
            if result:
                logger.info("数据库连接成功")
                return True
            else:
                logger.error("数据库连接失败")
                return False
                
        except Exception as e:
            logger.error(f"数据库连接异常: {str(e)}")
            return False
    
    def get_cleaning_data(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        获取数据清洗数据（整十分钟时间点）
        
        Args:
            start_time: 开始时间，格式：'YYYY-MM-DD HH:MM:SS'
            end_time: 结束时间，格式：'YYYY-MM-DD HH:MM:SS'
        
        Returns:
            包含查询结果的字典，格式：
            {
                "success": bool,
                "data": List[Dict],  # 查询到的数据列表
                "count": int,        # 数据条数
                "message": str       # 消息
            }
        """
        try:
            # 连接数据库
            if not self.connect_database():
                return {
                    "success": False,
                    "data": [],
                    "count": 0,
                    "message": "数据库连接失败"
                }
            
            # 构建查询条件
            # 使用TIMEDIFF函数筛选整十分钟的时间戳
            # TIMEDIFF('2024-01-01 01:00:00.000', ts, 1m) % 10 = 0 表示分钟数为10的倍数
            # 注意：TIMEDIFF返回分钟差值，取模10为0表示是整十分钟的时间点
            conditions = (
                f"ts >= '{start_time}' AND ts < '{end_time}' "
                f"AND TIMEDIFF('2024-01-01 01:00:00.000', ts, 1m) % 10 = 0"
            )
            
            logger.info(f"查询条件: {conditions}")
            logger.info(f"查询字段: {self.fields_cleaned}")
            
            # 执行查询
            # 需要查询的字段：时间戳 + 业务字段（清洗数据使用 _cd 后缀）
            select_cols = ['ts'] + self.fields_cleaned
            
            result = self.db.query(
                table_name=self.table_name,
                select_cols=select_cols,
                conditions=conditions,
                order_cols=['ts'],
                order_by=[dbpkg.DBBase.ORDER_ASC]
            )
            
            # 处理查询结果
            if result:
                # 转换数据格式，确保时间戳可序列化
                data_list = []
                for row in result:
                    data_dict = {}
                    # 处理时间戳
                    if 'ts' in row:
                        ts_value = row['ts']
                        # 如果是datetime对象，转换为字符串
                        if isinstance(ts_value, datetime):
                            data_dict['ts'] = ts_value.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            data_dict['ts'] = str(ts_value)
                    
                    # 处理其他字段（使用清洗数据的字段名）
                    for field in self.fields_cleaned:
                        if field in row:
                            value = row[field]
                            # 处理None值
                            if value is None:
                                data_dict[field] = None
                            else:
                                data_dict[field] = float(value) if isinstance(value, (int, float)) else value
                        else:
                            data_dict[field] = None
                    
                    data_list.append(data_dict)
                
                logger.info(f"查询成功，共 {len(data_list)} 条记录")
                
                return {
                    "success": True,
                    "data": data_list,
                    "count": len(data_list),
                    "message": f"查询成功，共获取 {len(data_list)} 条整十分钟时间点的数据"
                }
            else:
                logger.warning("查询返回空结果")
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "message": "查询成功，但在指定时间范围内未找到整十分钟时间点的数据"
                }
                
        except Exception as e:
            error_msg = f"查询数据时发生错误: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": error_msg
            }
        finally:
            # 关闭数据库连接
            if self.db:
                try:
                    self.db.close()
                except:
                    pass
    
    def get_raw_data(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        获取原始数据（优先查询整十分钟时间点，如果没有则查询所有数据）
        
        Args:
            start_time: 开始时间，格式：'YYYY-MM-DD HH:MM:SS'
            end_time: 结束时间，格式：'YYYY-MM-DD HH:MM:SS'
        
        Returns:
            包含查询结果的字典，格式：
            {
                "success": bool,
                "data": List[Dict],  # 查询到的数据列表
                "count": int,        # 数据条数
                "message": str       # 消息
            }
        """
        try:
            # 连接数据库
            if not self.connect_database():
                return {
                    "success": False,
                    "data": [],
                    "count": 0,
                    "message": "数据库连接失败"
                }
            
            # 先尝试查询整十分钟的数据
            # 使用TIMEDIFF函数筛选整十分钟的时间戳
            # TIMEDIFF('2024-01-01 01:00:00.000', ts, 1m) % 10 = 0 表示分钟数为10的倍数
            conditions_ten_min = (
                f"ts >= '{start_time}' AND ts < '{end_time}' "
                f"AND TIMEDIFF('2024-01-01 01:00:00.000', ts, 1m) % 10 = 0"
            )
            
            logger.info(f"查询原始数据条件（整十分钟）: {conditions_ten_min}")
            logger.info(f"查询字段: {self.fields}")
            
            # 执行查询
            # 需要查询的字段：时间戳 + 业务字段
            select_cols = ['ts'] + self.fields
            
            # 使用realtime_data表，先查询整十分钟的数据
            result = self.db.query(
                table_name="realtime_data",
                select_cols=select_cols,
                conditions=conditions_ten_min,
                order_cols=['ts'],
                order_by=[dbpkg.DBBase.ORDER_ASC]
            )
            
            # 如果整十分钟的数据为空，则查询所有数据
            if not result:
                logger.info("未找到整十分钟时间点的数据，改为查询所有数据")
                conditions_all = (
                    f"ts >= '{start_time}' AND ts < '{end_time}'"
                )
                result = self.db.query(
                    table_name="realtime_data",
                    select_cols=select_cols,
                    conditions=conditions_all,
                    order_cols=['ts'],
                    order_by=[dbpkg.DBBase.ORDER_ASC]
                )
            
            # 处理查询结果
            if result:
                # 转换数据格式，确保时间戳可序列化
                data_list = []
                for row in result:
                    data_dict = {}
                    # 处理时间戳
                    if 'ts' in row:
                        ts_value = row['ts']
                        # 如果是datetime对象，转换为字符串
                        if isinstance(ts_value, datetime):
                            data_dict['ts'] = ts_value.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            data_dict['ts'] = str(ts_value)
                    
                    # 处理其他字段（原始数据使用 _rd 后缀）
                    for field in self.fields:
                        if field in row:
                            value = row[field]
                            # 处理None值
                            if value is None:
                                data_dict[field] = None
                            else:
                                data_dict[field] = float(value) if isinstance(value, (int, float)) else value
                        else:
                            data_dict[field] = None
                    
                    data_list.append(data_dict)
                
                logger.info(f"原始数据查询成功，共 {len(data_list)} 条记录")
                
                # 判断是否包含整十分钟的数据
                # 检查前几条数据的分钟数是否为10的倍数
                is_ten_min_data = False
                if data_list:
                    sample_ts = data_list[0].get('ts', '')
                    if isinstance(sample_ts, str) and ':' in sample_ts:
                        try:
                            # 提取分钟数，例如从 "2025-10-30 01:31:00" 中提取 "31"
                            minutes = int(sample_ts.split(':')[1])
                            is_ten_min_data = (minutes % 10 == 0)
                        except (ValueError, IndexError):
                            pass
                
                if is_ten_min_data:
                    message = f"查询成功，共获取 {len(data_list)} 条整十分钟时间点的原始数据"
                else:
                    message = f"查询成功，共获取 {len(data_list)} 条原始数据（未找到整十分钟时间点，返回所有数据）"
                
                return {
                    "success": True,
                    "data": data_list,
                    "count": len(data_list),
                    "message": message
                }
            else:
                logger.warning("原始数据查询返回空结果")
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "message": "查询成功，但在指定时间范围内未找到原始数据"
                }
                
        except Exception as e:
            error_msg = f"查询原始数据时发生错误: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": error_msg
            }
        finally:
            # 关闭数据库连接
            if self.db:
                try:
                    self.db.close()
                except:
                    pass
    
    def get_fields_info(self) -> Dict[str, Any]:
        """获取字段信息"""
        return {
            "table_name": self.table_name,
            "fields": {
                "influent_tol_q_rd": "总进水量（原始数据）",
                "aao_influent_q_rd": "AAO流量（原始数据）",
                "mbr_influent_q_rd": "MBR流量（原始数据）",
                "aao_influent_1_1_tcod_rd": "COD（原始数据）",
                "aao_influent_1_1_snhx_rd": "NH3-N（原始数据）",
                "aao_influent_1_1_tn_rd": "TN（原始数据）",
                "aao_influent_1_1_tp_rd": "TP（原始数据）"
            },
            "fields_cleaned": {
                "influent_tol_q_cd": "总进水量（清洗数据）",
                "aao_influent_q_cd": "AAO流量（清洗数据）",
                "mbr_influent_q_cd": "MBR流量（清洗数据）",
                "aao_influent_1_1_tcod_cd": "COD（清洗数据）",
                "aao_influent_1_1_snhx_cd": "NH3-N（清洗数据）",
                "aao_influent_1_1_tn_cd": "TN（清洗数据）",
                "aao_influent_1_1_tp_cd": "TP（清洗数据）"
            }
        }
