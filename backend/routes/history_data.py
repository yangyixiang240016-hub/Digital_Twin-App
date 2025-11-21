#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史数据路由层
提供历史数据相关的API接口
"""

from flask import Blueprint, jsonify, request
from services.history_data_service import HistoryDataService
import logging

logger = logging.getLogger("DigitalTwinApp")

history_data_bp = Blueprint('history_data', __name__)


@history_data_bp.route('/history-data/query', methods=['POST'])
def query_history_data():
    """
    查询历史数据API
    接收start_date和end_date参数，返回每天0点的数据
    
    请求体格式：
    {
        "start_date": "2024-01-01",
        "end_date": "2024-01-07"
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
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "缺少必需参数: start_date"
            }), 400
        
        if not end_date:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "缺少必需参数: end_date"
            }), 400
        
        # 验证日期格式
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_dt > end_dt:
                return jsonify({
                    "success": False,
                    "data": [],
                    "count": 0,
                    "message": "开始日期必须早于或等于结束日期"
                }), 400
                
        except ValueError as e:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": f"日期格式错误，应为 'YYYY-MM-DD': {str(e)}"
            }), 400
        
        logger.info(f"收到历史数据查询请求: start_date={start_date}, end_date={end_date}")
        
        # 调用服务层获取数据
        service = HistoryDataService()
        result = service.get_history_data(start_date, end_date)
        
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


@history_data_bp.route('/history-data/query-cleaned', methods=['POST'])
def query_cleaned_history_data():
    """
    查询清洗过的历史数据API
    接收start_date和end_date参数，返回每天0点的清洗数据
    
    请求体格式：
    {
        "start_date": "2024-01-01",
        "end_date": "2024-01-07"
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
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "缺少必需参数: start_date"
            }), 400
        
        if not end_date:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": "缺少必需参数: end_date"
            }), 400
        
        # 验证日期格式
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_dt > end_dt:
                return jsonify({
                    "success": False,
                    "data": [],
                    "count": 0,
                    "message": "开始日期必须早于或等于结束日期"
                }), 400
                
        except ValueError as e:
            return jsonify({
                "success": False,
                "data": [],
                "count": 0,
                "message": f"日期格式错误，应为 'YYYY-MM-DD': {str(e)}"
            }), 400
        
        logger.info(f"收到清洗过的历史数据查询请求: start_date={start_date}, end_date={end_date}")
        
        # 调用服务层获取数据
        service = HistoryDataService()
        result = service.get_cleaned_history_data(start_date, end_date)
        
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
