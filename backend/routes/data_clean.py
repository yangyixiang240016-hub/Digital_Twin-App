#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗路由层
提供数据清洗相关的API接口
"""

from flask import Blueprint, jsonify, request
from services.data_clean_service import DataCleanService
import logging

logger = logging.getLogger("DigitalTwinApp")

data_clean_bp = Blueprint('data_clean', __name__)


@data_clean_bp.route('/data-clean/get-data', methods=['POST'])
def get_cleaning_data():
    """
    获取数据清洗数据API
    接收start_time和end_time参数，返回整十分钟时间点的数据
    
    请求体格式：
    {
        "start_time": "2024-01-01 00:00:00",
        "end_time": "2024-01-02 00:00:00"
    }
    
    返回格式：
    {
        "success": bool,
        "data": List[Dict],
        "count": int,
        "message": str
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "请求体为空"
            }), 400
        
        # 验证必需参数
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if not start_time:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "缺少必需参数: start_time"
            }), 400
        
        if not end_time:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "缺少必需参数: end_time"
            }), 400
        
        # 验证时间格式
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            
            if start_dt >= end_dt:
                return jsonify({
                    "success": False,
                    "data": [],
                    "count": 0,
                    "message": "开始时间必须早于结束时间"
                }), 400
                
        except ValueError as e:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": f"时间格式错误，应为 'YYYY-MM-DD HH:MM:SS': {str(e)}"
            }), 400
        
        logger.info(f"收到数据清洗查询请求: start_time={start_time}, end_time={end_time}")
        
        # 调用服务层获取数据
        service = DataCleanService()
        result = service.get_cleaning_data(start_time, end_time)
        
        # 根据结果返回相应的HTTP状态码
        if result.get("success"):
            status_code = 200
        else:
            status_code = 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        error_msg = f"处理请求时发生错误: {str(e)}"
        logger.error(error_msg)
        logger.exception(e)
        return jsonify({
            "success": False,
            "data": [],
            "count": 0,
            "message": error_msg
        }), 500


@data_clean_bp.route('/data-clean/get-raw-data', methods=['POST'])
def get_raw_data():
    """
    获取原始数据API
    接收start_time和end_time参数，返回整十分钟时间点的原始数据
    
    请求体格式：
    {
        "start_time": "2024-01-01 00:00:00",
        "end_time": "2024-01-02 00:00:00"
    }
    
    返回格式：
    {
        "success": bool,
        "data": List[Dict],
        "count": int,
        "message": str
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "请求体为空"
            }), 400
        
        # 验证必需参数
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if not start_time:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "缺少必需参数: start_time"
            }), 400
        
        if not end_time:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "缺少必需参数: end_time"
            }), 400
        
        # 验证时间格式
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            
            if start_dt >= end_dt:
                return jsonify({
                    "success": False,
                    "data": [],
                    "count": 0,
                    "message": "开始时间必须早于结束时间"
                }), 400
                
        except ValueError as e:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": f"时间格式错误，应为 'YYYY-MM-DD HH:MM:SS': {str(e)}"
            }), 400
        
        logger.info(f"收到原始数据查询请求: start_time={start_time}, end_time={end_time}")
        
        # 调用服务层获取数据
        service = DataCleanService()
        result = service.get_raw_data(start_time, end_time)
        
        # 根据结果返回相应的HTTP状态码
        if result.get("success"):
            status_code = 200
        else:
            status_code = 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        error_msg = f"处理请求时发生错误: {str(e)}"
        logger.error(error_msg)
        logger.exception(e)
        return jsonify({
            "success": False,
            "data": [],
            "count": 0,
            "message": error_msg
        }), 500


@data_clean_bp.route('/data-clean/fields-info', methods=['GET'])
def get_fields_info():
    """
    获取字段信息API
    返回表名和字段映射关系
    """
    try:
        service = DataCleanService()
        info = service.get_fields_info()
        return jsonify({
            "success": True,
            "data": info,
            "message": "获取字段信息成功"
        }), 200
        
    except Exception as e:
        error_msg = f"获取字段信息时发生错误: {str(e)}"
        logger.error(error_msg)
        logger.exception(e)
        return jsonify({
            "success": False,
            "data": {},
            "message": error_msg
        }), 500
