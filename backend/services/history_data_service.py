#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史数据服务层
提供从realtime_data表中读取每天0点数据的功能
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dbpkg.TDengineDB import TDengineDB
import dbpkg.DBBase

logger = logging.getLogger("DigitalTwinApp")


class HistoryDataService:
    """历史数据服务类"""
    
    def __init__(self):
        self.db = None
        self.table_name = "realtime_data"
        
        # 需要查询的字段列表（所有字段都是_rd结尾）
        self.fields = {
            "总进水量": "influent_tol_q_rd",
            "AAO流量": "aao_influent_q_rd",
            "MBR流量": "mbr_influent_q_rd",
            "COD": "aao_influent_1_1_tcod_rd",
            "NH3-N": "aao_influent_1_1_snhx_rd",
            "TN": "aao_influent_1_1_tn_rd",
            "TP": "aao_influent_1_1_tp_rd"
        }
        
        # 清洗过的历史数据字段列表（所有字段都是_cd结尾）
        self.fields_cleaned = {
            "总进水量": "influent_tol_q_cd",
            "AAO流量": "aao_influent_q_cd",
            "MBR流量": "mbr_influent_q_cd",
            "COD": "aao_influent_1_1_tcod_cd",
            "NH3-N": "aao_influent_1_1_snhx_cd",
            "TN": "aao_influent_1_1_tn_cd",
            "TP": "aao_influent_1_1_tp_cd"
        }
    
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
    
    def get_history_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        获取历史数据（每天0点的数据）
        
        Args:
            start_date: 开始日期，格式：'YYYY-MM-DD'
            end_date: 结束日期，格式：'YYYY-MM-DD'
        
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
            
            # 解析日期
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                
                # 结束日期加一天，确保包含结束日期当天的0点数据
                end_dt = end_dt + timedelta(days=1)
                
            except ValueError as e:
                return {
                    "success": False,
                    "data": [],
                    "count": 0,
                    "message": f"日期格式错误，应为 'YYYY-MM-DD': {str(e)}"
                }
            
            # 构建查询条件：查询每天0点的数据
            # TDengine中，我们可以使用时间戳格式匹配每天0点
            # 生成每天的0点时间戳列表
            daily_zero_times = []
            current_date = start_dt
            while current_date < end_dt:
                zero_time = current_date.strftime('%Y-%m-%d 00:00:00')
                daily_zero_times.append(f"'{zero_time}'")
                current_date += timedelta(days=1)
            
            if not daily_zero_times:
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "message": "查询成功，但在指定时间范围内未找到历史数据"
                }
            
            # 构建条件：查询这些特定时间点的数据
            start_time = start_dt.strftime('%Y-%m-%d 00:00:00')
            end_time = end_dt.strftime('%Y-%m-%d 00:00:00')
            
            # 使用IN条件匹配每天的0点时间
            conditions = (
                f"ts >= '{start_time}' AND ts < '{end_time}' "
                f"AND ts IN ({', '.join(daily_zero_times)})"
            )
            
            logger.info(f"查询条件: {conditions}")
            
            # 执行查询
            # 需要查询的字段：时间戳 + 业务字段
            select_cols = ['ts'] + list(self.fields.values())
            
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
                    
                    # 处理其他字段，使用中文名称作为key
                    for field_name, field_key in self.fields.items():
                        if field_key in row:
                            value = row[field_key]
                            # 处理None值
                            if value is None:
                                data_dict[field_name] = None
                            else:
                                data_dict[field_name] = float(value) if isinstance(value, (int, float)) else value
                        else:
                            data_dict[field_name] = None
                    
                    data_list.append(data_dict)
                
                logger.info(f"查询成功，共 {len(data_list)} 条记录")
                
                return {
                    "success": True,
                    "data": data_list,
                    "count": len(data_list),
                    "message": f"查询成功，共获取 {len(data_list)} 条历史数据"
                }
            else:
                logger.warning("查询返回空结果")
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "message": "查询成功，但在指定时间范围内未找到历史数据"
                }
                
        except Exception as e:
            error_msg = f"查询历史数据时发生错误: {str(e)}"
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
    
    def get_cleaned_history_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        获取清洗过的历史数据（每天0点的数据）
        
        Args:
            start_date: 开始日期，格式：'YYYY-MM-DD'
            end_date: 结束日期，格式：'YYYY-MM-DD'
        
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
            
            # 解析日期
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                
                # 结束日期加一天，确保包含结束日期当天的0点数据
                end_dt = end_dt + timedelta(days=1)
                
            except ValueError as e:
                return {
                    "success": False,
                    "data": [],
                    "count": 0,
                    "message": f"日期格式错误，应为 'YYYY-MM-DD': {str(e)}"
                }
            
            # 构建查询条件：查询每天0点的数据
            # 生成每天的0点时间戳列表
            daily_zero_times = []
            current_date = start_dt
            while current_date < end_dt:
                zero_time = current_date.strftime('%Y-%m-%d 00:00:00')
                daily_zero_times.append(f"'{zero_time}'")
                current_date += timedelta(days=1)
            
            if not daily_zero_times:
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "message": "查询成功，但在指定时间范围内未找到清洗过的历史数据"
                }
            
            # 构建条件：查询这些特定时间点的数据
            start_time = start_dt.strftime('%Y-%m-%d 00:00:00')
            end_time = end_dt.strftime('%Y-%m-%d 00:00:00')
            
            # 使用IN条件匹配每天的0点时间
            conditions = (
                f"ts >= '{start_time}' AND ts < '{end_time}' "
                f"AND ts IN ({', '.join(daily_zero_times)})"
            )
            
            logger.info(f"查询清洗过的历史数据条件: {conditions}")
            
            # 执行查询
            # 需要查询的字段：时间戳 + 业务字段
            select_cols = ['ts'] + list(self.fields_cleaned.values())
            
            result = self.db.query(
                table_name="online_cleaning_data",
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
                    
                    # 处理其他字段，使用中文名称作为key
                    for field_name, field_key in self.fields_cleaned.items():
                        if field_key in row:
                            value = row[field_key]
                            # 处理None值
                            if value is None:
                                data_dict[field_name] = None
                            else:
                                data_dict[field_name] = float(value) if isinstance(value, (int, float)) else value
                        else:
                            data_dict[field_name] = None
                    
                    data_list.append(data_dict)
                
                logger.info(f"查询清洗过的历史数据成功，共 {len(data_list)} 条记录")
                
                return {
                    "success": True,
                    "data": data_list,
                    "count": len(data_list),
                    "message": f"查询成功，共获取 {len(data_list)} 条清洗过的历史数据"
                }
            else:
                logger.warning("查询清洗过的历史数据返回空结果")
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "message": "查询成功，但在指定时间范围内未找到清洗过的历史数据"
                }
                
        except Exception as e:
            error_msg = f"查询清洗过的历史数据时发生错误: {str(e)}"
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

