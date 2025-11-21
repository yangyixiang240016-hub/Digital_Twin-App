#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
离线模拟结果服务
用于从数据库中读取离线模拟结果数据

历史记录：
2024-12-19    系统    创建离线模拟结果服务
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dbpkg.TDengineDB import TDengineDB
import dbpkg.DBBase

logger = logging.getLogger("DigitalTwinApp")

class OfflineResultService:
    """离线模拟结果服务类"""
    
    def __init__(self):
        self.db = None
        self.connect_database()
    
    def connect_database(self):
        """连接数据库"""
        try:
            self.db = TDengineDB()
            # 使用与现有代码相同的连接配置
            success = self.db.connect(
                host="192.168.3.92",
                user="root",
                password="taosdata",
                database="beihu_dt",
                port=6041,
                link_mode=dbpkg.DBBase.REST_LINK,  # 使用REST连接
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
    
    def get_offline_simulation_data(self, start_time: str = None, end_time: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        获取离线模拟数据
        
        Args:
            start_time: 开始时间，格式：'2024-05-15 01:00:00'
            end_time: 结束时间，格式：'2024-05-15 03:00:00'
            limit: 返回记录数限制
            
        Returns:
            包含模拟结果的字典
        """
        try:
            if not self.db:
                logger.error("数据库未连接")
                return {"error": "数据库未连接"}
            
            # 构建查询SQL
            table_name = "offline_simulation_data_aao"
            
            # 检查表是否存在
            if not self.db.has_table(table_name):
                logger.error(f"表 {table_name} 不存在")
                return {"error": f"表 {table_name} 不存在"}
            
            # 构建WHERE条件
            where_conditions = []
            if start_time:
                where_conditions.append(f"ts >= '{start_time}'")
            if end_time:
                where_conditions.append(f"ts <= '{end_time}'")
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # 构建查询字段列表
            field_mappings = self._get_field_mappings()
            
            # 检查表中实际存在的字段
            try:
                table_structure = self.db.describe(table_name)
                if not table_structure:
                    logger.error("无法获取表结构")
                    return {"error": "无法获取表结构"}
                
                # 获取表中实际存在的字段名
                actual_fields = [field[0] for field in table_structure]
                logger.info(f"表中实际字段数量: {len(actual_fields)}")
                
                # 过滤出存在的字段，不进行单独测试（因为我们已经知道字段存在）
                existing_fields = {}
                for field_name, display_name in field_mappings.items():
                    if field_name in actual_fields:
                        existing_fields[field_name] = display_name
                        logger.info(f"字段 {field_name} 存在于表中")
                    else:
                        logger.warning(f"字段 {field_name} 在表中不存在")
                
                logger.info(f"存在的字段数量: {len(existing_fields)}")
                
                # 如果没有字段存在，返回空数据结构
                if not existing_fields:
                    logger.warning("表中没有匹配的字段，返回空数据结构")
                    empty_data_item = {
                        'timestamp': '',
                        'fields': {}
                    }
                    
                    # 为所有字段创建null值结构
                    for field_name, display_name in field_mappings.items():
                        empty_data_item['fields'][field_name] = {
                            'value': None,
                            'display_name': display_name,
                            'unit': self._get_field_unit(field_name),
                            'is_null': True
                        }
                    
                    return {
                        "success": True,
                        "data": [empty_data_item],
                        "total": 1,
                        "message": "表中没有匹配的字段，返回空数据结构"
                    }
                
                # 使用存在的字段构建查询，限制字段数量避免SQL过长
                select_fields = ['ts'] + list(existing_fields.keys())[:20]  # 限制最多20个字段
                select_clause = ', '.join(select_fields)
                
            except Exception as structure_error:
                logger.error(f"检查表结构失败: {str(structure_error)}")
                return {"error": f"检查表结构失败: {str(structure_error)}"}
            
            # 分批查询，避免SQL过长
            logger.info(f"开始分批查询，共 {len(existing_fields)} 个字段")
            
            # 将字段分批，每批最多10个字段
            field_batches = []
            field_list = list(existing_fields.keys())
            batch_size = 10
            
            for i in range(0, len(field_list), batch_size):
                batch = field_list[i:i + batch_size]
                field_batches.append(batch)
            
            logger.info(f"分为 {len(field_batches)} 批查询")
            
            # 存储所有批次查询的结果（按批次存储）
            batch_results = []
            
            for batch_idx, field_batch in enumerate(field_batches):
                try:
                    logger.info(f"执行第 {batch_idx + 1} 批查询，字段: {field_batch}")
                    
                    # 使用TDengineDB的query方法，而不是直接执行SQL
                    result = self.db.query(
                        table_name=table_name,
                        select_cols=['ts'] + field_batch,
                        fetch_type=1,  # 只取第一条（最新的）
                        conditions=where_clause.replace('WHERE ', '') if where_clause else None,
                        order_cols=['ts'],
                        order_by=[dbpkg.DBBase.ORDER_DESC]
                    )
                    
                    if result:
                        logger.info(f"第 {batch_idx + 1} 批查询成功，获得 {len(result)} 条记录")
                        batch_results.append(result[0])  # 只取第一条记录
                    else:
                        logger.warning(f"第 {batch_idx + 1} 批查询返回空结果")
                        batch_results.append({})  # 添加空字典以保持批次对应关系
                        
                except Exception as batch_error:
                    logger.error(f"第 {batch_idx + 1} 批查询失败: {str(batch_error)}")
                    batch_results.append({})  # 添加空字典以保持批次对应关系
                    continue
            
            # 合并所有批次的结果到一个字典中
            merged_result = {}
            if batch_results:
                # 获取时间戳（从第一个非空结果中获取）
                for batch_result in batch_results:
                    if batch_result and 'ts' in batch_result:
                        merged_result['ts'] = batch_result['ts']
                        break
                
                # 合并所有批次的字段数据
                for batch_result in batch_results:
                    if batch_result:
                        merged_result.update(batch_result)
                
                logger.info(f"合并查询结果完成，共包含 {len(merged_result) - 1} 个字段（不包括ts）")
                result = [merged_result]
            else:
                logger.warning("所有批次查询都未返回数据")
                result = None
            
            if not result:
                logger.warning("未查询到数据，返回空数据结构")
                # 即使没有数据，也返回一个包含所有字段结构的空数据项
                empty_data_item = {
                    'timestamp': '',
                    'fields': {}
                }
                
                # 为所有字段创建null值结构
                for field_name, display_name in field_mappings.items():
                    empty_data_item['fields'][field_name] = {
                        'value': None,
                        'display_name': display_name,
                        'unit': self._get_field_unit(field_name),
                        'is_null': True
                    }
                
                return {
                    "success": True,
                    "data": [empty_data_item],
                    "total": 1,
                    "message": "表存在但无数据，返回空数据结构"
                }
            
            # 处理查询结果
            processed_data = []
            for row in result:
                data_item = {
                    'timestamp': row.get('ts', ''),
                    'fields': {}
                }
                
                # 处理每个字段 - 只处理存在的字段
                for field_name, display_name in existing_fields.items():
                    value = row.get(field_name)
                    # 即使value是None也返回，方便调试
                    data_item['fields'][field_name] = {
                        'value': float(value) if isinstance(value, (int, float)) else value,
                        'display_name': display_name,
                        'unit': self._get_field_unit(field_name),
                        'is_null': value is None
                    }
                
                # 为不存在的字段添加null值
                for field_name, display_name in field_mappings.items():
                    if field_name not in existing_fields:
                        data_item['fields'][field_name] = {
                            'value': None,
                            'display_name': display_name,
                            'unit': self._get_field_unit(field_name),
                            'is_null': True
                        }
                
                processed_data.append(data_item)
            
            return {
                "success": True,
                "data": processed_data,
                "total": len(processed_data),
                "message": "数据获取成功"
            }
            
        except Exception as e:
            logger.error(f"获取离线模拟数据失败: {str(e)}")
            return {"error": f"获取数据失败: {str(e)}"}
    
    def get_latest_offline_simulation_data(self) -> Dict[str, Any]:
        """
        获取最新的离线模拟数据
        
        Returns:
            包含最新模拟结果的字典
        """
        try:
            # 先尝试查询原始表
            result = self.get_offline_simulation_data(limit=1)
            if result.get('success') and result.get('data'):
                return result['data'][0]
            
            # 如果原始表没有数据，尝试查询其他可能的表
            logger.info("原始表无数据，尝试查询其他可能的表...")
            
            # 可能的表名列表
            possible_tables = [
                "offline_simulation_data_aao",
                "aao_simulation_data", 
                "offline_simulation_data",
                "simulation_data_aao",
                "aao_offline_data",
                "aao_sim_data",
                "simulation_results",
                "offline_results",
                "aao_results",
                "sim_data_aao"
            ]
            
            for table_name in possible_tables:
                try:
                    if self.db.has_table(table_name):
                        logger.info(f"找到表: {table_name}")
                        
                        # 检查表结构，只查询存在的字段
                        try:
                            table_structure = self.db.describe(table_name)
                            if not table_structure:
                                continue
                            
                            actual_fields = [field[0] for field in table_structure]
                            field_mappings = self._get_field_mappings()
                            
                            # 过滤出存在的字段
                            existing_fields = {}
                            for field_name, display_name in field_mappings.items():
                                if field_name in actual_fields:
                                    existing_fields[field_name] = display_name
                            
                            if not existing_fields:
                                logger.warning(f"表 {table_name} 中没有匹配的字段")
                                continue
                            
                            # 使用TDengineDB的query方法查询
                            try:
                                result = self.db.query(
                                    table_name=table_name,
                                    select_cols=['ts'] + list(existing_fields.keys()),
                                    fetch_type=3,
                                    order_cols=['ts'],
                                    order_by=[dbpkg.DBBase.ORDER_DESC]
                                )
                                if result:
                                    logger.info(f"表 {table_name} 有数据")
                                else:
                                    logger.warning(f"表 {table_name} 查询返回空结果")
                                    continue
                            except Exception as query_error:
                                logger.warning(f"表 {table_name} 查询失败: {str(query_error)}")
                                continue
                            
                            if result:
                                # 处理数据格式
                                data_item = {
                                    'timestamp': result[0].get('ts', result[0].get('timestamp', result[0].get('time', ''))),
                                    'fields': {}
                                }
                                
                                # 处理存在的字段
                                for field_name, display_name in existing_fields.items():
                                    value = result[0].get(field_name)
                                    data_item['fields'][field_name] = {
                                        'value': float(value) if isinstance(value, (int, float)) else value,
                                        'display_name': display_name,
                                        'unit': self._get_field_unit(field_name),
                                        'is_null': value is None
                                    }
                                
                                # 为不存在的字段添加null值
                                for field_name, display_name in field_mappings.items():
                                    if field_name not in existing_fields:
                                        data_item['fields'][field_name] = {
                                            'value': None,
                                            'display_name': display_name,
                                            'unit': self._get_field_unit(field_name),
                                            'is_null': True
                                        }
                                
                                return data_item
                                
                        except Exception as structure_error:
                            logger.warning(f"检查表 {table_name} 结构失败: {str(structure_error)}")
                            continue
                            
                except Exception as table_error:
                    logger.warning(f"查询表 {table_name} 失败: {str(table_error)}")
                    continue
            
            return {"error": "未找到最新数据"}
        except Exception as e:
            logger.error(f"获取最新离线模拟数据失败: {str(e)}")
            return {"error": f"获取最新数据失败: {str(e)}"}
    
    def _get_field_mappings(self) -> Dict[str, str]:
        """获取字段映射"""
        return {
            # 进水量
            'aao_influent_1_q_ted': '1#AAO生化池进水流量',
            'aao_influent_2_q_ted': '2#AAO生化池进水流量',
            
            # 出水参数
            'aao_effluent_q_ted': '出水流量',
            'aao_effluent_tcod_ted': '出水化学需氧量',
            'aao_effluent_tbod_ted': '出水生化需氧量',
            'aao_effluent_ss_ted': '出水悬浮固体浓度',
            'aao_effluent_tp_ted': '出水总磷',
            'aao_effluent_tn_ted': '出水总氮',
            'aao_effluent_snhx_ted': '出水氨氮',
            'aao_effluent_snox_ted': '出水硝氮',
            'aao_effluent_spo4_ted': '出水正磷酸盐',
            
            # 曝气参数 - 1-1#AAO生化池好氧段1-5
            'aao_cstr3_1_1_qair_ntp_ted': '1-1#AAO生化池好氧段1曝气量',
            'aao_cstr4_1_1_qair_ntp_ted': '1-1#AAO生化池好氧段2曝气量',
            'aao_cstr5_1_1_qair_ntp_ted': '1-1#AAO生化池好氧段3曝气量',
            'aao_cstr6_1_1_qair_ntp_ted': '1-1#AAO生化池好氧段4曝气量',
            'aao_cstr7_1_1_qair_ntp_ted': '1-1#AAO生化池好氧段5曝气量',
            
            # 曝气参数 - 1-2#AAO生化池好氧段1-5
            'aao_cstr3_1_2_qair_ntp_ted': '1-2#AAO生化池好氧段1曝气量',
            'aao_cstr4_1_2_qair_ntp_ted': '1-2#AAO生化池好氧段2曝气量',
            'aao_cstr5_1_2_qair_ntp_ted': '1-2#AAO生化池好氧段3曝气量',
            'aao_cstr6_1_2_qair_ntp_ted': '1-2#AAO生化池好氧段4曝气量',
            'aao_cstr7_1_2_qair_ntp_ted': '1-2#AAO生化池好氧段5曝气量',
            
            # 曝气参数 - 2-1#AAO生化池好氧段1-5
            'aao_cstr3_2_1_qair_ntp_ted': '2-1#AAO生化池好氧段1曝气量',
            'aao_cstr4_2_1_qair_ntp_ted': '2-1#AAO生化池好氧段2曝气量',
            'aao_cstr5_2_1_qair_ntp_ted': '2-1#AAO生化池好氧段3曝气量',
            'aao_cstr6_2_1_qair_ntp_ted': '2-1#AAO生化池好氧段4曝气量',
            'aao_cstr7_2_1_qair_ntp_ted': '2-1#AAO生化池好氧段5曝气量',
            
            # 曝气参数 - 2-2#AAO生化池好氧段1-5
            'aao_cstr3_2_2_qair_ntp_ted': '2-2#AAO生化池好氧段1曝气量',
            'aao_cstr4_2_2_qair_ntp_ted': '2-2#AAO生化池好氧段2曝气量',
            'aao_cstr5_2_2_qair_ntp_ted': '2-2#AAO生化池好氧段3曝气量',
            'aao_cstr6_2_2_qair_ntp_ted': '2-2#AAO生化池好氧段4曝气量',
            'aao_cstr7_2_2_qair_ntp_ted': '2-2#AAO生化池好氧段5曝气量',
            
            # 药剂参数
            'aao_pac_q_ted': '2号加药间聚合氯化铝投加量',
            
            # 回流参数
            'aao_ras_1_q_ted': '1#回流污泥流量',
            'aao_ras_2_q_ted': '2#回流污泥流量'
        }
    
    def _get_field_unit(self, field_name: str) -> str:
        """
        根据字段名获取单位
        
        Args:
            field_name: 字段名
            
        Returns:
            单位字符串
        """
        unit_mapping = {
            # 进水量
            'aao_influent_1_q_ted': 'm³/d',
            'aao_influent_2_q_ted': 'm³/d',
            
            # 出水参数
            'aao_effluent_q_ted': 'm³/d',
            'aao_effluent_tcod_ted': 'mg/L',
            'aao_effluent_tbod_ted': 'mg/L',
            'aao_effluent_ss_ted': 'mg/L',
            'aao_effluent_tp_ted': 'mg/L',
            'aao_effluent_tn_ted': 'mg/L',
            'aao_effluent_snhx_ted': 'mg/L',
            'aao_effluent_snox_ted': 'mg/L',
            'aao_effluent_spo4_ted': 'mg/L',
            
            # 曝气参数 - 1-1#AAO生化池
            'aao_cstr3_1_1_qair_ntp_ted': 'Nm³/d',
            'aao_cstr4_1_1_qair_ntp_ted': 'Nm³/d',
            'aao_cstr5_1_1_qair_ntp_ted': 'Nm³/d',
            'aao_cstr6_1_1_qair_ntp_ted': 'Nm³/d',
            'aao_cstr7_1_1_qair_ntp_ted': 'Nm³/d',
            
            # 曝气参数 - 1-2#AAO生化池
            'aao_cstr3_1_2_qair_ntp_ted': 'Nm³/d',
            'aao_cstr4_1_2_qair_ntp_ted': 'Nm³/d',
            'aao_cstr5_1_2_qair_ntp_ted': 'Nm³/d',
            'aao_cstr6_1_2_qair_ntp_ted': 'Nm³/d',
            'aao_cstr7_1_2_qair_ntp_ted': 'Nm³/d',
            
            # 曝气参数 - 2-1#AAO生化池
            'aao_cstr3_2_1_qair_ntp_ted': 'Nm³/d',
            'aao_cstr4_2_1_qair_ntp_ted': 'Nm³/d',
            'aao_cstr5_2_1_qair_ntp_ted': 'Nm³/d',
            'aao_cstr6_2_1_qair_ntp_ted': 'Nm³/d',
            'aao_cstr7_2_1_qair_ntp_ted': 'Nm³/d',
            
            # 曝气参数 - 2-2#AAO生化池
            'aao_cstr3_2_2_qair_ntp_ted': 'Nm³/d',
            'aao_cstr4_2_2_qair_ntp_ted': 'Nm³/d',
            'aao_cstr5_2_2_qair_ntp_ted': 'Nm³/d',
            'aao_cstr6_2_2_qair_ntp_ted': 'Nm³/d',
            'aao_cstr7_2_2_qair_ntp_ted': 'Nm³/d',
            
            # 药剂参数
            'aao_pac_q_ted': 'mg/L',
            
            # 回流参数
            'aao_ras_1_q_ted': 'm³/d',
            'aao_ras_2_q_ted': 'm³/d'
        }
        
        return unit_mapping.get(field_name, '')
    
    def get_field_categories(self) -> Dict[str, List[str]]:
        """
        获取字段分类信息
        
        Returns:
            字段分类字典
        """
        return {
            "进水量": [
                'aao_influent_1_q_ted',
                'aao_influent_2_q_ted'
            ],
            "出水参数": [
                'aao_effluent_q_ted',
                'aao_effluent_tcod_ted',
                'aao_effluent_tbod_ted',
                'aao_effluent_ss_ted',
                'aao_effluent_tp_ted',
                'aao_effluent_tn_ted',
                'aao_effluent_snhx_ted',
                'aao_effluent_snox_ted',
                'aao_effluent_spo4_ted'
            ],
            "曝气参数": [
                'aao_cstr3_1_1_qair_ntp_ted',
                'aao_cstr4_1_1_qair_ntp_ted',
                'aao_cstr5_1_1_qair_ntp_ted',
                'aao_cstr6_1_1_qair_ntp_ted',
                'aao_cstr7_1_1_qair_ntp_ted',
                'aao_cstr3_1_2_qair_ntp_ted',
                'aao_cstr4_1_2_qair_ntp_ted',
                'aao_cstr5_1_2_qair_ntp_ted',
                'aao_cstr6_1_2_qair_ntp_ted',
                'aao_cstr7_1_2_qair_ntp_ted',
                'aao_cstr3_2_1_qair_ntp_ted',
                'aao_cstr4_2_1_qair_ntp_ted',
                'aao_cstr5_2_1_qair_ntp_ted',
                'aao_cstr6_2_1_qair_ntp_ted',
                'aao_cstr7_2_1_qair_ntp_ted',
                'aao_cstr3_2_2_qair_ntp_ted',
                'aao_cstr4_2_2_qair_ntp_ted',
                'aao_cstr5_2_2_qair_ntp_ted',
                'aao_cstr6_2_2_qair_ntp_ted',
                'aao_cstr7_2_2_qair_ntp_ted'
            ],
            "药剂参数": [
                'aao_pac_q_ted'
            ],
            "回流参数": [
                'aao_ras_1_q_ted',
                'aao_ras_2_q_ted'
            ]
        }
    
    def get_offline_result_by_start_time(self, start_time: str) -> Dict[str, Any]:
        """
        根据开始时间查询对应的ts时间戳的数据
        
        Args:
            start_time: 开始时间，格式：'2024-05-15 01:00:00'
            
        Returns:
            包含模拟结果的字典
        """
        try:
            if not self.db:
                logger.error("数据库未连接")
                return {"error": "数据库未连接"}
            
            table_name = "offline_simulation_data_aao"
            
            if not self.db.has_table(table_name):
                logger.error(f"表 {table_name} 不存在")
                return {"error": f"表 {table_name} 不存在"}
            
            # 根据开始时间查询最接近的ts时间戳
            # 查找最接近开始时间的记录（允许一定的时间误差，比如前后1小时内）
            try:
                # 尝试使用query方法查询最接近的时间
                query_result = self.db.query(
                    table_name=table_name,
                    select_cols=['ts'],
                    conditions=f"ts >= '{start_time}' - 1h AND ts <= '{start_time}' + 1h",
                    order_cols=['ts'],
                    order_by=[dbpkg.DBBase.ORDER_ASC],
                    fetch_type=1
                )
                
                if query_result and len(query_result) > 0:
                    # 找到最接近开始时间的记录
                    matched_ts = query_result[0].get('ts')
                    logger.info(f"找到匹配的时间戳: {matched_ts}")
                    
                    # 使用匹配到的ts查询该时间点的所有数据
                    return self.get_offline_simulation_data(
                        start_time=str(matched_ts),
                        end_time=str(matched_ts),
                        limit=1
                    )
                else:
                    logger.warning(f"未找到接近开始时间 {start_time} 的数据，尝试直接使用开始时间查询")
                    # 如果找不到，直接使用开始时间作为ts查询
                    return self.get_offline_simulation_data(
                        start_time=start_time,
                        end_time=start_time,
                        limit=1
                    )
                
            except Exception as query_error:
                logger.error(f"查询开始时间对应的ts失败: {str(query_error)}")
                # 如果查询失败，尝试直接使用开始时间作为ts查询
                return self.get_offline_simulation_data(
                    start_time=start_time,
                    end_time=start_time,
                    limit=1
                )
                
        except Exception as e:
            logger.error(f"根据开始时间获取离线模拟数据失败: {str(e)}")
            return {"error": f"获取数据失败: {str(e)}"}
    
    def _get_optimization_field_mappings(self) -> Dict[str, str]:
        """
        获取离线优化结果的字段映射（字段名 -> 显示名称）
        
        Returns:
            字段映射字典
        """
        return {
            # 进水量
            'aao_influent_1_q_or': '1#AAO生化池进水流量',
            'aao_influent_2_q_or': '2#AAO生化池进水流量',
            
            # 出水参数
            'aao_effluent_q_or': '出水流量',
            'aao_effluent_tcod_or': '出水化学需氧量',
            'aao_effluent_tbod_or': '出水生化需氧量',
            'aao_effluent_ss_or': '出水悬浮固体浓度',
            'aao_effluent_tp_or': '出水总磷',
            'aao_effluent_tn_or': '出水总氮',
            'aao_effluent_snhx_or': '出水氨氮',
            'aao_effluent_snox_or': '出水硝氮',
            'aao_effluent_spo4_or': '出水正磷酸盐',
            
            # 曝气参数 - 1-1#AAO生化池好氧段1-5
            'aao_cstr3_1_1_qair_ntp_or': '1-1#AAO生化池好氧段1曝气量',
            'aao_cstr4_1_1_qair_ntp_or': '1-1#AAO生化池好氧段2曝气量',
            'aao_cstr5_1_1_qair_ntp_or': '1-1#AAO生化池好氧段3曝气量',
            'aao_cstr6_1_1_qair_ntp_or': '1-1#AAO生化池好氧段4曝气量',
            'aao_cstr7_1_1_qair_ntp_or': '1-1#AAO生化池好氧段5曝气量',
            
            # 曝气参数 - 1-2#AAO生化池好氧段1-5
            'aao_cstr3_1_2_qair_ntp_or': '1-2#AAO生化池好氧段1曝气量',
            'aao_cstr4_1_2_qair_ntp_or': '1-2#AAO生化池好氧段2曝气量',
            'aao_cstr5_1_2_qair_ntp_or': '1-2#AAO生化池好氧段3曝气量',
            'aao_cstr6_1_2_qair_ntp_or': '1-2#AAO生化池好氧段4曝气量',
            'aao_cstr7_1_2_qair_ntp_or': '1-2#AAO生化池好氧段5曝气量',
            
            # 曝气参数 - 2-1#AAO生化池好氧段1-5
            'aao_cstr3_2_1_qair_ntp_or': '2-1#AAO生化池好氧段1曝气量',
            'aao_cstr4_2_1_qair_ntp_or': '2-1#AAO生化池好氧段2曝气量',
            'aao_cstr5_2_1_qair_ntp_or': '2-1#AAO生化池好氧段3曝气量',
            'aao_cstr6_2_1_qair_ntp_or': '2-1#AAO生化池好氧段4曝气量',
            'aao_cstr7_2_1_qair_ntp_or': '2-1#AAO生化池好氧段5曝气量',
            
            # 曝气参数 - 2-2#AAO生化池好氧段1-5
            'aao_cstr3_2_2_qair_ntp_or': '2-2#AAO生化池好氧段1曝气量',
            'aao_cstr4_2_2_qair_ntp_or': '2-2#AAO生化池好氧段2曝气量',
            'aao_cstr5_2_2_qair_ntp_or': '2-2#AAO生化池好氧段3曝气量',
            'aao_cstr6_2_2_qair_ntp_or': '2-2#AAO生化池好氧段4曝气量',
            'aao_cstr7_2_2_qair_ntp_or': '2-2#AAO生化池好氧段5曝气量',
            
            # 药剂参数
            'aao_pac_q_or': '2号加药间聚合氯化铝投加量',
            
            # 回流参数
            'aao_ras_1_q_or': '1#回流污泥流量',
            'aao_ras_2_q_or': '2#回流污泥流量'
        }
    
    def _get_optimization_field_unit(self, field_name: str) -> str:
        """
        根据字段名获取单位（离线优化结果）
        
        Args:
            field_name: 字段名
            
        Returns:
            单位字符串
        """
        unit_mapping = {
            # 进水量
            'aao_influent_1_q_or': 'm³/d',
            'aao_influent_2_q_or': 'm³/d',
            
            # 出水参数
            'aao_effluent_q_or': 'm³/d',
            'aao_effluent_tcod_or': 'mg/L',
            'aao_effluent_tbod_or': 'mg/L',
            'aao_effluent_ss_or': 'mg/L',
            'aao_effluent_tp_or': 'mg/L',
            'aao_effluent_tn_or': 'mg/L',
            'aao_effluent_snhx_or': 'mg/L',
            'aao_effluent_snox_or': 'mg/L',
            'aao_effluent_spo4_or': 'mg/L',
            
            # 曝气参数 - 1-1#AAO生化池
            'aao_cstr3_1_1_qair_ntp_or': 'Nm³/d',
            'aao_cstr4_1_1_qair_ntp_or': 'Nm³/d',
            'aao_cstr5_1_1_qair_ntp_or': 'Nm³/d',
            'aao_cstr6_1_1_qair_ntp_or': 'Nm³/d',
            'aao_cstr7_1_1_qair_ntp_or': 'Nm³/d',
            
            # 曝气参数 - 1-2#AAO生化池
            'aao_cstr3_1_2_qair_ntp_or': 'Nm³/d',
            'aao_cstr4_1_2_qair_ntp_or': 'Nm³/d',
            'aao_cstr5_1_2_qair_ntp_or': 'Nm³/d',
            'aao_cstr6_1_2_qair_ntp_or': 'Nm³/d',
            'aao_cstr7_1_2_qair_ntp_or': 'Nm³/d',
            
            # 曝气参数 - 2-1#AAO生化池
            'aao_cstr3_2_1_qair_ntp_or': 'Nm³/d',
            'aao_cstr4_2_1_qair_ntp_or': 'Nm³/d',
            'aao_cstr5_2_1_qair_ntp_or': 'Nm³/d',
            'aao_cstr6_2_1_qair_ntp_or': 'Nm³/d',
            'aao_cstr7_2_1_qair_ntp_or': 'Nm³/d',
            
            # 曝气参数 - 2-2#AAO生化池
            'aao_cstr3_2_2_qair_ntp_or': 'Nm³/d',
            'aao_cstr4_2_2_qair_ntp_or': 'Nm³/d',
            'aao_cstr5_2_2_qair_ntp_or': 'Nm³/d',
            'aao_cstr6_2_2_qair_ntp_or': 'Nm³/d',
            'aao_cstr7_2_2_qair_ntp_or': 'Nm³/d',
            
            # 药剂参数
            'aao_pac_q_or': 'mg/L',
            
            # 回流参数
            'aao_ras_1_q_or': 'm³/d',
            'aao_ras_2_q_or': 'm³/d'
        }
        
        return unit_mapping.get(field_name, '')
    
    def get_optimization_result_by_start_time(self, start_time: str) -> Dict[str, Any]:
        """
        根据开始时间查询对应的ts时间戳的离线优化结果数据
        
        Args:
            start_time: 开始时间，格式：'2024-05-15 01:00:00' 或 '2024-5-15 01:00:00'
            
        Returns:
            包含优化结果的字典
        """
        try:
            if not self.db:
                logger.error("数据库未连接")
                return {"error": "数据库未连接"}
            
            table_name = "optimize_result_aao"
            
            if not self.db.has_table(table_name):
                logger.error(f"表 {table_name} 不存在")
                return {"error": f"表 {table_name} 不存在"}
            
            # 标准化时间格式，确保月份和日期有前导零
            try:
                from datetime import datetime
                import re
                # 先尝试标准格式
                try:
                    dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                    normalized_start_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    # 如果失败，尝试处理没有前导零的格式（如 2024-5-15）
                    # 使用正则表达式替换月份和日期为有前导零的格式
                    pattern = r'(\d{4})-(\d{1,2})-(\d{1,2})'
                    def pad_date(match):
                        year = match.group(1)
                        month = match.group(2).zfill(2)
                        day = match.group(3).zfill(2)
                        return f'{year}-{month}-{day}'
                    
                    normalized_time_str = re.sub(pattern, pad_date, start_time)
                    dt = datetime.strptime(normalized_time_str, '%Y-%m-%d %H:%M:%S')
                    normalized_start_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    logger.info(f"时间格式已标准化: {start_time} -> {normalized_start_time}")
            except Exception as time_error:
                # 如果都失败，使用原始字符串
                normalized_start_time = start_time.replace(' ', 'T')  # TDengine可能需要T分隔符
                logger.warning(f"无法标准化时间格式，使用原始时间: {start_time}, 错误: {str(time_error)}")
            
            # 根据开始时间查询最接近的ts时间戳
            try:
                # 使用query方法查询最接近的时间
                query_result = self.db.query(
                    table_name=table_name,
                    select_cols=['ts'],
                    conditions=f"ts >= '{normalized_start_time}' - 1h AND ts <= '{normalized_start_time}' + 1h",
                    order_cols=['ts'],
                    order_by=[dbpkg.DBBase.ORDER_ASC],
                    fetch_type=1  # 只取第一条
                )
                
                matched_ts = None
                if query_result and len(query_result) > 0:
                    matched_ts = query_result[0].get('ts')
                    # 如果matched_ts是datetime对象，转换为字符串
                    if hasattr(matched_ts, 'strftime'):
                        matched_ts = matched_ts.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    logger.info(f"找到匹配的时间戳: {matched_ts}")
                else:
                    logger.warning(f"未找到接近开始时间 {normalized_start_time} 的数据，尝试直接使用开始时间查询")
                    matched_ts = normalized_start_time
                
                # 获取字段映射
                field_mappings = self._get_optimization_field_mappings()
                
                # 检查表中实际存在的字段
                table_structure = self.db.describe(table_name)
                if not table_structure:
                    logger.error("无法获取表结构")
                    return {"error": "无法获取表结构"}
                
                actual_fields = [field[0] for field in table_structure]
                existing_fields = {}
                for field_name, display_name in field_mappings.items():
                    if field_name in actual_fields:
                        existing_fields[field_name] = display_name
                
                if not existing_fields:
                    logger.warning(f"表 {table_name} 中没有匹配的字段")
                    return {"error": f"表 {table_name} 中没有匹配的字段"}
                
                # 查询数据，使用query方法
                select_cols = ['ts'] + list(existing_fields.keys())
                result = self.db.query(
                    table_name=table_name,
                    select_cols=select_cols,
                    conditions=f"ts = '{matched_ts}'",
                    fetch_type=1  # 只取第一条
                )
                
                if not result:
                    logger.warning(f"未找到时间戳 {matched_ts} 的数据")
                    return {
                        "success": True,
                        "data": None,
                        "total": 0,
                        "message": "未找到数据"
                    }
                
                # 处理查询结果
                row = result[0]  # 只取第一条
                data_item = {
                    'timestamp': row.get('ts', ''),
                    'fields': {}
                }
                
                # 处理每个字段
                for field_name, display_name in existing_fields.items():
                    value = row.get(field_name)
                    data_item['fields'][field_name] = {
                        'value': float(value) if isinstance(value, (int, float)) else value,
                        'display_name': display_name,
                        'unit': self._get_optimization_field_unit(field_name),
                        'is_null': value is None
                    }
                
                return {
                    "success": True,
                    "data": data_item,
                    "total": 1,
                    "message": "数据获取成功"
                }
                
            except Exception as query_error:
                logger.error(f"查询开始时间对应的ts失败: {str(query_error)}")
                return {"error": f"查询失败: {str(query_error)}"}
                
        except Exception as e:
            logger.error(f"根据开始时间获取离线优化数据失败: {str(e)}")
            return {"error": f"获取数据失败: {str(e)}"}
    
    def _get_online_optimization_field_mappings(self) -> Dict[str, str]:
        """
        获取在线优化结果的字段映射（字段名 -> 显示名称）
        
        Returns:
            字段映射字典
        """
        return {
            # 进水量
            'aao_influent_1_q_oor': '1#AAO生化池进水流量',
            'aao_influent_2_q_oor': '2#AAO生化池进水流量',
            
            # 出水参数
            'aao_effluent_q_oor': '出水流量',
            'aao_effluent_tcod_oor': '出水化学需氧量',
            'aao_effluent_tbod_oor': '出水生化需氧量',
            'aao_effluent_ss_oor': '出水悬浮固体浓度',
            'aao_effluent_tp_oor': '出水总磷',
            'aao_effluent_tn_oor': '出水总氮',
            'aao_effluent_snhx_oor': '出水氨氮',
            'aao_effluent_snox_oor': '出水硝氮',
            'aao_effluent_spo4_oor': '出水正磷酸盐',
            
            # 曝气参数 - 1-1#AAO生化池好氧段1-5
            'aao_cstr3_1_1_qair_ntp_oor': '1-1#AAO生化池好氧段1曝气量',
            'aao_cstr4_1_1_qair_ntp_oor': '1-1#AAO生化池好氧段2曝气量',
            'aao_cstr5_1_1_qair_ntp_oor': '1-1#AAO生化池好氧段3曝气量',
            'aao_cstr6_1_1_qair_ntp_oor': '1-1#AAO生化池好氧段4曝气量',
            'aao_cstr7_1_1_qair_ntp_oor': '1-1#AAO生化池好氧段5曝气量',
            
            # 曝气参数 - 1-2#AAO生化池好氧段1-5
            'aao_cstr3_1_2_qair_ntp_oor': '1-2#AAO生化池好氧段1曝气量',
            'aao_cstr4_1_2_qair_ntp_oor': '1-2#AAO生化池好氧段2曝气量',
            'aao_cstr5_1_2_qair_ntp_oor': '1-2#AAO生化池好氧段3曝气量',
            'aao_cstr6_1_2_qair_ntp_oor': '1-2#AAO生化池好氧段4曝气量',
            'aao_cstr7_1_2_qair_ntp_oor': '1-2#AAO生化池好氧段5曝气量',
            
            # 曝气参数 - 2-1#AAO生化池好氧段1-5
            'aao_cstr3_2_1_qair_ntp_oor': '2-1#AAO生化池好氧段1曝气量',
            'aao_cstr4_2_1_qair_ntp_oor': '2-1#AAO生化池好氧段2曝气量',
            'aao_cstr5_2_1_qair_ntp_oor': '2-1#AAO生化池好氧段3曝气量',
            'aao_cstr6_2_1_qair_ntp_oor': '2-1#AAO生化池好氧段4曝气量',
            'aao_cstr7_2_1_qair_ntp_oor': '2-1#AAO生化池好氧段5曝气量',
            
            # 曝气参数 - 2-2#AAO生化池好氧段1-5
            'aao_cstr3_2_2_qair_ntp_oor': '2-2#AAO生化池好氧段1曝气量',
            'aao_cstr4_2_2_qair_ntp_oor': '2-2#AAO生化池好氧段2曝气量',
            'aao_cstr5_2_2_qair_ntp_oor': '2-2#AAO生化池好氧段3曝气量',
            'aao_cstr6_2_2_qair_ntp_oor': '2-2#AAO生化池好氧段4曝气量',
            'aao_cstr7_2_2_qair_ntp_oor': '2-2#AAO生化池好氧段5曝气量',
            
            # 药剂参数
            'aao_pac_q_oor': '2号加药间聚合氯化铝投加量',
            
            # 回流参数
            'aao_ras_1_q_oor': '1#回流污泥流量',
            'aao_ras_2_q_oor': '2#回流污泥流量'
        }
    
    def _get_online_optimization_field_unit(self, field_name: str) -> str:
        """
        根据字段名获取单位（在线优化结果）
        
        Args:
            field_name: 字段名
            
        Returns:
            单位字符串
        """
        unit_mapping = {
            # 进水量
            'aao_influent_1_q_oor': 'm³/d',
            'aao_influent_2_q_oor': 'm³/d',
            
            # 出水参数
            'aao_effluent_q_oor': 'm³/d',
            'aao_effluent_tcod_oor': 'mg/L',
            'aao_effluent_tbod_oor': 'mg/L',
            'aao_effluent_ss_oor': 'mg/L',
            'aao_effluent_tp_oor': 'mg/L',
            'aao_effluent_tn_oor': 'mg/L',
            'aao_effluent_snhx_oor': 'mg/L',
            'aao_effluent_snox_oor': 'mg/L',
            'aao_effluent_spo4_oor': 'mg/L',
            
            # 曝气参数 - 1-1#AAO生化池
            'aao_cstr3_1_1_qair_ntp_oor': 'Nm³/d',
            'aao_cstr4_1_1_qair_ntp_oor': 'Nm³/d',
            'aao_cstr5_1_1_qair_ntp_oor': 'Nm³/d',
            'aao_cstr6_1_1_qair_ntp_oor': 'Nm³/d',
            'aao_cstr7_1_1_qair_ntp_oor': 'Nm³/d',
            
            # 曝气参数 - 1-2#AAO生化池
            'aao_cstr3_1_2_qair_ntp_oor': 'Nm³/d',
            'aao_cstr4_1_2_qair_ntp_oor': 'Nm³/d',
            'aao_cstr5_1_2_qair_ntp_oor': 'Nm³/d',
            'aao_cstr6_1_2_qair_ntp_oor': 'Nm³/d',
            'aao_cstr7_1_2_qair_ntp_oor': 'Nm³/d',
            
            # 曝气参数 - 2-1#AAO生化池
            'aao_cstr3_2_1_qair_ntp_oor': 'Nm³/d',
            'aao_cstr4_2_1_qair_ntp_oor': 'Nm³/d',
            'aao_cstr5_2_1_qair_ntp_oor': 'Nm³/d',
            'aao_cstr6_2_1_qair_ntp_oor': 'Nm³/d',
            'aao_cstr7_2_1_qair_ntp_oor': 'Nm³/d',
            
            # 曝气参数 - 2-2#AAO生化池
            'aao_cstr3_2_2_qair_ntp_oor': 'Nm³/d',
            'aao_cstr4_2_2_qair_ntp_oor': 'Nm³/d',
            'aao_cstr5_2_2_qair_ntp_oor': 'Nm³/d',
            'aao_cstr6_2_2_qair_ntp_oor': 'Nm³/d',
            'aao_cstr7_2_2_qair_ntp_oor': 'Nm³/d',
            
            # 药剂参数
            'aao_pac_q_oor': 'mg/L',
            
            # 回流参数
            'aao_ras_1_q_oor': 'm³/d',
            'aao_ras_2_q_oor': 'm³/d'
        }
        
        return unit_mapping.get(field_name, '')
    
    def get_online_optimization_result_by_start_time(self, start_time: str = None) -> Dict[str, Any]:
        """
        查询在线优化结果数据（读取最新一条数据）
        
        Args:
            start_time: 已废弃，保留参数以兼容旧接口，不再使用
            
        Returns:
            包含优化结果的字典
        """
        try:
            if not self.db:
                logger.error("数据库未连接")
                return {"error": "数据库未连接"}
            
            table_name = "optimize_online_result_aao"
            
            if not self.db.has_table(table_name):
                logger.error(f"表 {table_name} 不存在")
                return {"error": f"表 {table_name} 不存在"}
            
            try:
                # 获取字段映射
                field_mappings = self._get_online_optimization_field_mappings()
                
                # 检查表中实际存在的字段
                table_structure = self.db.describe(table_name)
                if not table_structure:
                    logger.error("无法获取表结构")
                    return {"error": "无法获取表结构"}
                
                actual_fields = [field[0] for field in table_structure]
                existing_fields = {}
                for field_name, display_name in field_mappings.items():
                    if field_name in actual_fields:
                        existing_fields[field_name] = display_name
                
                if not existing_fields:
                    logger.warning(f"表 {table_name} 中没有匹配的字段")
                    return {"error": f"表 {table_name} 中没有匹配的字段"}
                
                # 查询最新一条数据，按ts降序排列
                select_cols = ['ts'] + list(existing_fields.keys())
                result = self.db.query(
                    table_name=table_name,
                    select_cols=select_cols,
                    conditions=None,
                    order_cols=['ts'],
                    order_by=[dbpkg.DBBase.ORDER_DESC],
                    fetch_type=1  # 只取第一条（最新一条）
                )
                
                if not result:
                    logger.warning(f"未找到在线优化结果数据")
                    return {
                        "success": True,
                        "data": None,
                        "total": 0,
                        "message": "未找到数据"
                    }
                
                # 处理查询结果
                row = result[0]  # 只取第一条（最新一条）
                data_item = {
                    'timestamp': row.get('ts', ''),
                    'fields': {}
                }
                
                # 处理每个字段
                for field_name, display_name in existing_fields.items():
                    value = row.get(field_name)
                    data_item['fields'][field_name] = {
                        'value': float(value) if isinstance(value, (int, float)) else value,
                        'display_name': display_name,
                        'unit': self._get_online_optimization_field_unit(field_name),
                        'is_null': value is None
                    }
                
                return {
                    "success": True,
                    "data": data_item,
                    "total": 1,
                    "message": "数据获取成功"
                }
                
            except Exception as query_error:
                logger.error(f"查询在线优化结果失败: {str(query_error)}")
                return {"error": f"查询失败: {str(query_error)}"}
                
        except Exception as e:
            logger.error(f"获取在线优化结果数据失败: {str(e)}")
            return {"error": f"获取数据失败: {str(e)}"}
    
    def get_online_simulation_result_by_start_time(self, start_time: str = None) -> Dict[str, Any]:
        """
        查询在线模拟结果数据（读取最新一条数据）
        
        Args:
            start_time: 已废弃，保留参数以兼容旧接口，不再使用
            
        Returns:
            包含模拟结果的字典
        """
        try:
            if not self.db:
                logger.error("数据库未连接")
                return {"error": "数据库未连接"}
            
            table_name = "online_simulation_data_aao"
            
            if not self.db.has_table(table_name):
                logger.error(f"表 {table_name} 不存在")
                return {"error": f"表 {table_name} 不存在"}
            
            try:
                # 获取字段映射（使用离线模拟的字段映射，因为字段名相同）
                field_mappings = self._get_field_mappings()
                
                # 检查表中实际存在的字段
                table_structure = self.db.describe(table_name)
                if not table_structure:
                    logger.error("无法获取表结构")
                    return {"error": "无法获取表结构"}
                
                actual_fields = [field[0] for field in table_structure]
                existing_fields = {}
                for field_name, display_name in field_mappings.items():
                    if field_name in actual_fields:
                        existing_fields[field_name] = display_name
                
                if not existing_fields:
                    logger.warning(f"表 {table_name} 中没有匹配的字段")
                    return {"error": f"表 {table_name} 中没有匹配的字段"}
                
                # 查询最新一条数据，按ts降序排列
                select_cols = ['ts'] + list(existing_fields.keys())
                result = self.db.query(
                    table_name=table_name,
                    select_cols=select_cols,
                    conditions=None,
                    order_cols=['ts'],
                    order_by=[dbpkg.DBBase.ORDER_DESC],
                    fetch_type=1  # 只取第一条（最新一条）
                )
                
                if not result:
                    logger.warning(f"未找到在线模拟结果数据")
                    return {
                        "success": True,
                        "data": None,
                        "total": 0,
                        "message": "未找到数据"
                    }
                
                # 处理查询结果
                row = result[0]  # 只取第一条（最新一条）
                data_item = {
                    'timestamp': row.get('ts', ''),
                    'fields': {}
                }
                
                # 处理每个字段
                for field_name, display_name in existing_fields.items():
                    value = row.get(field_name)
                    data_item['fields'][field_name] = {
                        'value': float(value) if isinstance(value, (int, float)) else value,
                        'display_name': display_name,
                        'unit': self._get_field_unit(field_name),
                        'is_null': value is None
                    }
                
                return {
                    "success": True,
                    "data": data_item,
                    "total": 1,
                    "message": "数据获取成功"
                }
                
            except Exception as query_error:
                logger.error(f"查询在线模拟结果失败: {str(query_error)}")
                return {"error": f"查询失败: {str(query_error)}"}
                
        except Exception as e:
            logger.error(f"获取在线模拟结果数据失败: {str(e)}")
            return {"error": f"获取数据失败: {str(e)}"}
    
    def get_simulation_result_chart_data(self, start_time: str, end_time: str, field_names: List[str] = None) -> Dict[str, Any]:
        """
        获取模拟结果图表数据（从offline_simulation_data_aao表）
        
        Args:
            start_time: 开始时间，格式：'2024-05-15 01:00:00'
            end_time: 结束时间，格式：'2024-05-15 09:00:00'
            field_names: 要查询的字段名列表，如果为None则查询所有可用字段
            
        Returns:
            包含时间序列数据的字典
        """
        try:
            if not self.db:
                logger.error("数据库未连接")
                return {"error": "数据库未连接"}
            
            table_name = "offline_simulation_data_aao"
            
            if not self.db.has_table(table_name):
                logger.error(f"表 {table_name} 不存在")
                return {"error": f"表 {table_name} 不存在"}
            
            # 计算步数和采样点
            try:
                # 标准化时间格式，处理月份和日期没有前导零的情况（如 2024-5-15）
                def normalize_time(time_str):
                    import re
                    # 匹配日期格式，将单数字的月份和日期补零
                    pattern = r'(\d{4})-(\d{1,2})-(\d{1,2})'
                    def pad_date(match):
                        year = match.group(1)
                        month = match.group(2).zfill(2)
                        day = match.group(3).zfill(2)
                        return f'{year}-{month}-{day}'
                    normalized = re.sub(pattern, pad_date, time_str)
                    return normalized
                
                normalized_start_time = normalize_time(start_time)
                normalized_end_time = normalize_time(end_time)
                
                start_dt = datetime.strptime(normalized_start_time, '%Y-%m-%d %H:%M:%S')
                end_dt = datetime.strptime(normalized_end_time, '%Y-%m-%d %H:%M:%S')
                time_diff = end_dt - start_dt
                step_seconds = 2 * 3600  # 步长是2小时
                total_seconds = time_diff.total_seconds()
                steps = int(total_seconds / step_seconds)
                
                # 生成采样点时间列表（从开始时间开始，每隔2小时一个采样点）
                # 注意：不包括结束时间本身，只包括小于结束时间的采样点
                time_points = []
                for i in range(steps + 1):
                    point_time = start_dt + timedelta(seconds=i * step_seconds)
                    if point_time < end_dt:
                        time_points.append(point_time.strftime('%Y-%m-%d %H:%M:%S'))
            except Exception as time_error:
                logger.error(f"时间计算失败: {str(time_error)}")
                return {"error": f"时间计算失败: {str(time_error)}"}
            
            # 如果没有指定字段，使用默认字段列表（根据用户提供的字段）
            if field_names is None:
                field_names = [
                    # 1-1AAO曝气量
                    'aao_cstr_front_1_1_qair_ntp_ted',
                    'aao_cstr_mid_1_1_qair_ntp_ted',
                    'aao_cstr_terminal_1_1_qair_ntp_ted',
                    # 1-2AAO曝气量
                    'aao_cstr_front_1_2_qair_ntp_ted',
                    'aao_cstr_mid_1_2_qair_ntp_ted',
                    'aao_cstr_terminal_1_2_qair_ntp_ted',
                    # 2-1AAO曝气量
                    'aao_cstr_front_2_1_qair_ntp_ted',
                    'aao_cstr_mid_2_1_qair_ntp_ted',
                    'aao_cstr_terminal_2_1_qair_ntp_ted',
                    # 2-2AAO曝气量
                    'aao_cstr_front_2_2_qair_ntp_ted',
                    'aao_cstr_mid_2_2_qair_ntp_ted',
                    'aao_cstr_terminal_2_2_qair_ntp_ted',
                    # AAO内回流量
                    'aao_flowdivider3_1_1_influx_ted',
                    'aao_flowdivider3_1_2_influx_ted',
                    'aao_flowdivider3_2_1_influx_ted',
                    'aao_flowdivider3_2_2_influx_ted',
                    # AAO外回流量
                    'aao_ras_1_q_ted',
                    'aao_ras_2_q_ted',
                    # AAO剩余污泥量
                    'aao_flowdivider3_1_sludge_q_ted',
                    'aao_flowdivider3_2_sludge_q_ted',
                    # AAO生物池污泥浓度
                    'aao_cstr7_1_1_xtss_ted',
                    'aao_cstr7_1_2_xtss_ted',
                    'aao_cstr7_2_1_xtss_ted',
                    'aao_cstr7_2_2_xtss_ted',
                ]
            
            # 检查表中实际存在的字段
            try:
                table_structure = self.db.describe(table_name)
                if not table_structure:
                    logger.error("无法获取表结构")
                    return {"error": "无法获取表结构"}
                
                actual_fields = [field[0] for field in table_structure]
                existing_fields = [f for f in field_names if f in actual_fields]
                
                if not existing_fields:
                    logger.warning(f"指定的字段在表中都不存在")
                    return {
                        "success": True,
                        "data": [],
                        "times": time_points,
                        "message": "指定的字段在表中都不存在"
                    }
                
            except Exception as structure_error:
                logger.error(f"检查表结构失败: {str(structure_error)}")
                return {"error": f"检查表结构失败: {str(structure_error)}"}
            
            # 查询数据：根据时间范围查询
            try:
                select_cols = ['ts'] + existing_fields
                conditions = f"ts >= '{normalized_start_time}' AND ts < '{normalized_end_time}' ORDER BY ts ASC"
                
                result = self.db.query(
                    table_name=table_name,
                    select_cols=select_cols,
                    conditions=conditions
                )
                
                if not result:
                    return {
                        "success": True,
                        "data": {},
                        "times": time_points,
                        "message": "未查询到数据"
                    }
                
                # 处理查询结果：按字段组织数据
                chart_data = {}
                for field_name in existing_fields:
                    chart_data[field_name] = []
                
                # 将查询结果按时间点组织
                result_dict = {}
                for row in result:
                    ts = row.get('ts')
                    if ts:
                        if hasattr(ts, 'strftime'):
                            ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            ts_str = str(ts)
                        result_dict[ts_str] = row
                
                # 为每个时间点填充数据
                for time_point in time_points:
                    row = result_dict.get(time_point)
                    
                    for field_name in existing_fields:
                        if row and field_name in row:
                            value = row[field_name]
                            if value is None:
                                chart_data[field_name].append(None)
                            else:
                                try:
                                    chart_data[field_name].append(float(value))
                                except (ValueError, TypeError):
                                    chart_data[field_name].append(None)
                        else:
                            chart_data[field_name].append(None)
                
                return {
                    "success": True,
                    "data": chart_data,
                    "times": time_points,
                    "message": "数据获取成功"
                }
                
            except Exception as query_error:
                logger.error(f"查询数据失败: {str(query_error)}")
                return {"error": f"查询数据失败: {str(query_error)}"}
                
        except Exception as e:
            logger.error(f"获取模拟结果图表数据失败: {str(e)}")
            return {"error": f"获取数据失败: {str(e)}"}
    
    def get_optimization_result_chart_data(self, start_time: str, end_time: str, field_names: List[str] = None) -> Dict[str, Any]:
        """
        获取优化结果图表数据（从optimize_result_aao表和realtime_data表）
        
        Args:
            start_time: 开始时间，格式：'2024-05-15 01:00:00'
            end_time: 结束时间，格式：'2024-05-15 09:00:00'
            field_names: 要查询的字段名列表（_or后缀），如果为None则查询所有可用字段
            
        Returns:
            包含时间序列数据的字典，包含优化数据（_or）和真实数据（_rd）
        """
        try:
            if not self.db:
                logger.error("数据库未连接")
                return {"error": "数据库未连接"}
            
            table_name = "optimize_result_aao"
            
            if not self.db.has_table(table_name):
                logger.error(f"表 {table_name} 不存在")
                return {"error": f"表 {table_name} 不存在"}
            
            # 计算步数和采样点
            try:
                # 标准化时间格式，处理月份和日期没有前导零的情况（如 2024-5-15）
                def normalize_time(time_str):
                    import re
                    pattern = r'(\d{4})-(\d{1,2})-(\d{1,2})'
                    def pad_date(match):
                        year = match.group(1)
                        month = match.group(2).zfill(2)
                        day = match.group(3).zfill(2)
                        return f'{year}-{month}-{day}'
                    normalized = re.sub(pattern, pad_date, time_str)
                    return normalized
                
                normalized_start_time = normalize_time(start_time)
                normalized_end_time = normalize_time(end_time)
                
                start_dt = datetime.strptime(normalized_start_time, '%Y-%m-%d %H:%M:%S')
                end_dt = datetime.strptime(normalized_end_time, '%Y-%m-%d %H:%M:%S')
                time_diff = end_dt - start_dt
                step_seconds = 2 * 3600  # 步长是2小时
                total_seconds = time_diff.total_seconds()
                steps = int(total_seconds / step_seconds)
                
                # 生成采样点时间列表（从开始时间开始，每隔2小时一个采样点）
                # 注意：不包括结束时间本身，只包括小于结束时间的采样点
                time_points = []
                for i in range(steps + 1):
                    point_time = start_dt + timedelta(seconds=i * step_seconds)
                    if point_time < end_dt:
                        time_points.append(point_time.strftime('%Y-%m-%d %H:%M:%S'))
            except Exception as time_error:
                logger.error(f"时间计算失败: {str(time_error)}")
                return {"error": f"时间计算失败: {str(time_error)}"}
            
            # 字段映射关系：优化字段(_or) -> 真实数据字段(_rd)
            field_mapping = {
                # 1-1AAO曝气量
                'aao_cstr_front_1_1_qair_ntp_or': 'aao_cstr_front_1_1_qair_ntp_rd',
                'aao_cstr_mid_1_1_qair_ntp_or': 'aao_cstr_mid_1_1_qair_ntp_rd',
                'aao_cstr_terminal_1_1_qair_ntp_or': 'aao_cstr_terminal_1_1_qair_ntp_rd',
                # 1-2AAO曝气量
                'aao_cstr_front_1_2_qair_ntp_or': 'aao_cstr_front_1_2_qair_ntp_rd',
                'aao_cstr_mid_1_2_qair_ntp_or': 'aao_cstr_mid_1_2_qair_ntp_rd',
                'aao_cstr_terminal_1_2_qair_ntp_or': 'aao_cstr_terminal_1_2_qair_ntp_rd',
                # 2-1AAO曝气量
                'aao_cstr_front_2_1_qair_ntp_or': 'aao_cstr_front_2_1_qair_ntp_rd',
                'aao_cstr_mid_2_1_qair_ntp_or': 'aao_cstr_mid_2_1_qair_ntp_rd',
                'aao_cstr_terminal_2_1_qair_ntp_or': 'aao_cstr_terminal_2_1_qair_ntp_rd',
                # 2-2AAO曝气量
                'aao_cstr_front_2_2_qair_ntp_or': 'aao_cstr_front_2_2_qair_ntp_rd',
                'aao_cstr_mid_2_2_qair_ntp_or': 'aao_cstr_mid_2_2_qair_ntp_rd',
                'aao_cstr_terminal_2_2_qair_ntp_or': 'aao_cstr_terminal_2_2_qair_ntp_rd',
                # AAO内回流量 - 没有真实数据，不映射
                # 'aao_flowdivider3_1_1_influx_or': None,
                # 'aao_flowdivider3_1_2_influx_or': None,
                # 'aao_flowdivider3_2_1_influx_or': None,
                # 'aao_flowdivider3_2_2_influx_or': None,
                # AAO外回流量
                'aao_ras_1_q_or': 'mbr_ras_1_1_q_rd',
                'aao_ras_2_q_or': 'mbr_ras_1_2_q_rd',
                # AAO剩余污泥量
                'aao_flowdivider3_1_sludge_q_or': 'aao_flowdivider3_1_sludge_q_rd',
                'aao_flowdivider3_2_sludge_q_or': 'aao_flowdivider3_2_sludge_q_rd',
                # AAO生物池污泥浓度
                'aao_cstr7_1_1_xtss_or': 'aao_cstr7_1_1_xtss_rd',
                'aao_cstr7_1_2_xtss_or': 'aao_cstr7_1_2_xtss_rd',
                'aao_cstr7_2_1_xtss_or': 'aao_cstr7_2_1_xtss_rd',
                'aao_cstr7_2_2_xtss_or': 'aao_cstr7_2_2_xtss_rd',
            }
            
            # 如果没有指定字段，使用默认字段列表
            if field_names is None:
                field_names = list(field_mapping.keys())
            
            # 检查表中实际存在的字段
            try:
                table_structure = self.db.describe(table_name)
                if not table_structure:
                    logger.error("无法获取表结构")
                    return {"error": "无法获取表结构"}
                
                actual_fields = [field[0] for field in table_structure]
                existing_fields = [f for f in field_names if f in actual_fields]
                
                if not existing_fields:
                    logger.warning(f"指定的字段在表中都不存在")
                    return {
                        "success": True,
                        "data": [],
                        "times": time_points,
                        "message": "指定的字段在表中都不存在"
                    }
                
            except Exception as structure_error:
                logger.error(f"检查表结构失败: {str(structure_error)}")
                return {"error": f"检查表结构失败: {str(structure_error)}"}
            
            # 查询优化数据：根据时间范围查询
            try:
                select_cols = ['ts'] + existing_fields
                conditions = f"ts >= '{normalized_start_time}' AND ts < '{normalized_end_time}' ORDER BY ts ASC"
                
                optimize_result = self.db.query(
                    table_name=table_name,
                    select_cols=select_cols,
                    conditions=conditions
                )
                
                # 查询真实数据：从realtime_data表查询
                realtime_table_name = "realtime_data"
                realtime_data = {}
                
                if self.db.has_table(realtime_table_name):
                    # 获取需要查询的真实数据字段
                    realtime_fields = []
                    for or_field in existing_fields:
                        if or_field in field_mapping:
                            rd_field = field_mapping[or_field]
                            if rd_field:  # 如果映射存在且不为None
                                realtime_fields.append(rd_field)
                    
                    if realtime_fields:
                        # 检查realtime_data表中实际存在的字段
                        try:
                            realtime_table_structure = self.db.describe(realtime_table_name)
                            if realtime_table_structure:
                                realtime_actual_fields = [field[0] for field in realtime_table_structure]
                                realtime_existing_fields = [f for f in realtime_fields if f in realtime_actual_fields]
                                
                                if realtime_existing_fields:
                                    # 查询真实数据
                                    realtime_select_cols = ['ts'] + realtime_existing_fields
                                    realtime_result = self.db.query(
                                        table_name=realtime_table_name,
                                        select_cols=realtime_select_cols,
                                        conditions=conditions
                                    )
                                    
                                    # 将真实数据按时间点组织
                                    if realtime_result:
                                        for row in realtime_result:
                                            ts = row.get('ts')
                                            if ts:
                                                if hasattr(ts, 'strftime'):
                                                    ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
                                                else:
                                                    ts_str = str(ts)
                                                realtime_data[ts_str] = row
                        except Exception as realtime_error:
                            logger.warning(f"查询真实数据失败: {str(realtime_error)}")
                
                # 处理查询结果：按字段组织数据
                chart_data = {}
                realtime_chart_data = {}
                
                for field_name in existing_fields:
                    chart_data[field_name] = []
                    # 如果该字段有对应的真实数据字段，也初始化
                    if field_name in field_mapping and field_mapping[field_name]:
                        realtime_chart_data[field_name] = []
                
                # 将优化查询结果按时间点组织
                optimize_result_dict = {}
                if optimize_result:
                    for row in optimize_result:
                        ts = row.get('ts')
                        if ts:
                            if hasattr(ts, 'strftime'):
                                ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                ts_str = str(ts)
                            optimize_result_dict[ts_str] = row
                
                # 为每个时间点填充数据
                for time_point in time_points:
                    optimize_row = optimize_result_dict.get(time_point)
                    realtime_row = realtime_data.get(time_point)
                    
                    for field_name in existing_fields:
                        # 优化数据
                        if optimize_row and field_name in optimize_row:
                            value = optimize_row[field_name]
                            if value is None:
                                chart_data[field_name].append(None)
                            else:
                                try:
                                    chart_data[field_name].append(float(value))
                                except (ValueError, TypeError):
                                    chart_data[field_name].append(None)
                        else:
                            chart_data[field_name].append(None)
                        
                        # 真实数据
                        if field_name in field_mapping and field_mapping[field_name]:
                            rd_field = field_mapping[field_name]
                            if realtime_row and rd_field in realtime_row:
                                value = realtime_row[rd_field]
                                if value is None:
                                    realtime_chart_data[field_name].append(None)
                                else:
                                    try:
                                        realtime_chart_data[field_name].append(float(value))
                                    except (ValueError, TypeError):
                                        realtime_chart_data[field_name].append(None)
                            else:
                                realtime_chart_data[field_name].append(None)
                
                return {
                    "success": True,
                    "data": chart_data,
                    "realtime_data": realtime_chart_data,
                    "times": time_points,
                    "message": "数据获取成功"
                }
                
            except Exception as query_error:
                logger.error(f"查询数据失败: {str(query_error)}")
                return {"error": f"查询数据失败: {str(query_error)}"}
                
        except Exception as e:
            logger.error(f"获取优化结果图表数据失败: {str(e)}")
            return {"error": f"获取数据失败: {str(e)}"}
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.db:
            try:
                self.db.close()
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接失败: {str(e)}")
