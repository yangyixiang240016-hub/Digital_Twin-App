#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
离线模拟结果路由
提供离线模拟结果数据的API接口

历史记录：
2024-12-19    系统    创建离线模拟结果路由
"""

from flask import Blueprint, jsonify, request, make_response
from services.offline_result_service import OfflineResultService
import logging

logger = logging.getLogger("DigitalTwinApp")
offline_result_bp = Blueprint('offline_result', __name__)

# 创建服务实例
offline_result_service = OfflineResultService()

@offline_result_bp.route('/offline/result/latest', methods=['GET', 'OPTIONS'])
def get_latest_offline_result():
    """获取最新的离线模拟结果"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        result = offline_result_service.get_latest_offline_simulation_data()
        
        if 'error' in result:
            response = jsonify({
                "success": False,
                "error": result['error']
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        response = jsonify({
            "success": True,
            "data": result,
            "message": "获取最新离线模拟结果成功"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"获取最新离线模拟结果失败: {str(e)}")
        response = jsonify({
            "success": False,
            "error": f"获取最新离线模拟结果失败: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@offline_result_bp.route('/offline/result/data', methods=['GET', 'OPTIONS'])
def get_offline_result_data():
    """获取离线模拟结果数据"""
    try:
        # 获取查询参数
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', 100, type=int)
        
        # 验证参数
        if limit > 1000:
            limit = 1000  # 限制最大返回数量
        
        result = offline_result_service.get_offline_simulation_data(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        if 'error' in result:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
        
        return jsonify({
            "success": True,
            "data": result.get('data', []),
            "total": result.get('total', 0),
            "message": result.get('message', '获取数据成功')
        })
        
    except Exception as e:
        logger.error(f"获取离线模拟结果数据失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取离线模拟结果数据失败: {str(e)}"
        }), 500

@offline_result_bp.route('/offline/result/chart-data', methods=['POST', 'OPTIONS'])
def get_simulation_result_chart_data():
    """获取模拟结果图表数据"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体为空"
            }), 400
        
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        field_names = data.get('field_names')  # 可选参数
        
        if not start_time or not end_time:
            return jsonify({
                "success": False,
                "error": "缺少必需参数: start_time 或 end_time"
            }), 400
        
        result = offline_result_service.get_simulation_result_chart_data(
            start_time=start_time,
            end_time=end_time,
            field_names=field_names
        )
        
        if 'error' in result:
            response = jsonify({
                "success": False,
                "error": result['error']
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        response = jsonify({
            "success": True,
            "data": result.get('data', {}),
            "times": result.get('times', []),
            "message": result.get('message', '获取数据成功')
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"获取模拟结果图表数据失败: {str(e)}")
        response = jsonify({
            "success": False,
            "error": f"获取模拟结果图表数据失败: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@offline_result_bp.route('/offline/result/by-start-time', methods=['GET', 'OPTIONS'])
def get_offline_result_by_start_time():
    """根据开始时间获取离线模拟结果数据"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        # 获取查询参数
        start_time = request.args.get('start_time')
        
        if not start_time:
            response = jsonify({
                "success": False,
                "error": "缺少start_time参数"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        result = offline_result_service.get_offline_result_by_start_time(start_time)
        
        if 'error' in result:
            response = jsonify({
                "success": False,
                "error": result['error']
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        response = jsonify({
            "success": True,
            "data": result.get('data', [])[0] if result.get('data') else {},
            "total": result.get('total', 0),
            "message": result.get('message', '获取数据成功')
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"根据开始时间获取离线模拟结果数据失败: {str(e)}")
        response = jsonify({
            "success": False,
            "error": f"获取数据失败: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@offline_result_bp.route('/offline/optimization/by-start-time', methods=['GET', 'OPTIONS'])
def get_optimization_result_by_start_time():
    """根据开始时间获取离线优化结果数据"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        # 获取查询参数
        start_time = request.args.get('start_time')
        
        if not start_time:
            response = jsonify({
                "success": False,
                "error": "缺少start_time参数"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        result = offline_result_service.get_optimization_result_by_start_time(start_time)
        
        if 'error' in result:
            response = jsonify({
                "success": False,
                "error": result['error']
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        response = jsonify({
            "success": True,
            "data": result.get('data'),
            "total": result.get('total', 0),
            "message": result.get('message', '获取数据成功')
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"根据开始时间获取离线优化结果数据失败: {str(e)}")
        response = jsonify({
            "success": False,
            "error": f"获取数据失败: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@offline_result_bp.route('/online/simulation/by-start-time', methods=['GET', 'OPTIONS'])
def get_online_simulation_result_by_start_time():
    """获取在线模拟结果数据（最新一条）"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        # start_time参数已废弃，不再使用，直接查询最新一条数据
        start_time = request.args.get('start_time')  # 保留参数以兼容旧接口
        
        result = offline_result_service.get_online_simulation_result_by_start_time(start_time)
        
        if 'error' in result:
            response = jsonify({
                "success": False,
                "error": result['error']
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        response = jsonify({
            "success": True,
            "data": result.get('data'),
            "total": result.get('total', 0),
            "message": result.get('message', '获取数据成功')
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"获取在线模拟结果数据失败: {str(e)}")
        response = jsonify({
            "success": False,
            "error": f"获取数据失败: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@offline_result_bp.route('/online/optimization/by-start-time', methods=['GET', 'OPTIONS'])
def get_online_optimization_result_by_start_time():
    """获取在线优化结果数据（最新一条）"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        # start_time参数已废弃，不再使用，直接查询最新一条数据
        start_time = request.args.get('start_time')  # 保留参数以兼容旧接口
        
        result = offline_result_service.get_online_optimization_result_by_start_time(start_time)
        
        if 'error' in result:
            response = jsonify({
                "success": False,
                "error": result['error']
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        response = jsonify({
            "success": True,
            "data": result.get('data'),
            "total": result.get('total', 0),
            "message": result.get('message', '获取数据成功')
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"获取在线优化结果数据失败: {str(e)}")
        response = jsonify({
            "success": False,
            "error": f"获取数据失败: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@offline_result_bp.route('/offline/result/categories', methods=['GET'])
def get_field_categories():
    """获取字段分类信息"""
    try:
        categories = offline_result_service.get_field_categories()
        
        return jsonify({
            "success": True,
            "data": categories,
            "message": "获取字段分类信息成功"
        })
        
    except Exception as e:
        logger.error(f"获取字段分类信息失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取字段分类信息失败: {str(e)}"
        }), 500

@offline_result_bp.route('/offline/result/fields', methods=['GET', 'OPTIONS'])
def get_field_mappings():
    """获取字段映射信息"""
    try:
        # 获取字段分类
        categories = offline_result_service.get_field_categories()
        
        # 构建字段映射信息
        field_mappings = {}
        for category, fields in categories.items():
            for field in fields:
                field_mappings[field] = {
                    'display_name': offline_result_service._get_field_display_name(field),
                    'unit': offline_result_service._get_field_unit(field),
                    'category': category
                }
        
        return jsonify({
            "success": True,
            "data": field_mappings,
            "message": "获取字段映射信息成功"
        })
        
    except Exception as e:
        logger.error(f"获取字段映射信息失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取字段映射信息失败: {str(e)}"
        }), 500

@offline_result_bp.route('/offline/result/summary', methods=['GET'])
def get_result_summary():
    """获取离线模拟结果摘要信息"""
    try:
        # 获取最新数据
        latest_data = offline_result_service.get_latest_offline_simulation_data()
        
        if 'error' in latest_data:
            return jsonify({
                "success": False,
                "error": latest_data['error']
            }), 500
        
        # 构建摘要信息
        summary = {
            "timestamp": latest_data.get('timestamp', ''),
            "total_fields": len(latest_data.get('fields', {})),
            "categories": {}
        }
        
        # 按分类统计字段数量
        categories = offline_result_service.get_field_categories()
        for category, fields in categories.items():
            count = 0
            for field in fields:
                if field in latest_data.get('fields', {}):
                    count += 1
            summary["categories"][category] = count
        
        return jsonify({
            "success": True,
            "data": summary,
            "message": "获取结果摘要信息成功"
        })
        
    except Exception as e:
        logger.error(f"获取结果摘要信息失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"获取结果摘要信息失败: {str(e)}"
        }), 500

@offline_result_bp.route('/offline/result/optimization-chart-data', methods=['POST', 'OPTIONS'])
def get_optimization_result_chart_data():
    """获取优化结果图表数据"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体为空"
            }), 400
        
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        field_names = data.get('field_names')
        
        if not start_time or not end_time:
            return jsonify({
                "success": False,
                "error": "缺少必需参数: start_time 或 end_time"
            }), 400
        
        result = offline_result_service.get_optimization_result_chart_data(
            start_time=start_time,
            end_time=end_time,
            field_names=field_names
        )
        
        if 'error' in result:
            response = jsonify({
                "success": False,
                "error": result['error']
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        response = jsonify({
            "success": True,
            "data": result.get('data', {}),
            "realtime_data": result.get('realtime_data', {}),
            "times": result.get('times', []),
            "message": result.get('message', '获取数据成功')
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"获取优化结果图表数据失败: {str(e)}")
        response = jsonify({
            "success": False,
            "error": f"获取数据失败: {str(e)}"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@offline_result_bp.route('/offline/result/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        if not offline_result_service.db:
            return jsonify({
                "success": False,
                "error": "数据库未连接"
            }), 500
        
        # 检查表是否存在
        table_name = "offline_simulation_data_aao"
        if not offline_result_service.db.has_table(table_name):
            return jsonify({
                "success": False,
                "error": f"表 {table_name} 不存在"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "服务健康状态正常",
            "database_connected": True,
            "table_exists": True
        })
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"健康检查失败: {str(e)}"
        }), 500

@offline_result_bp.route('/offline/result/debug', methods=['GET'])
def debug_tables():
    """调试接口 - 查看数据库中的表"""
    try:
        if not offline_result_service.db:
            return jsonify({
                "success": False,
                "error": "数据库未连接"
            }), 500
        
        # 可能的表名列表
        possible_tables = [
            "offline_simulation_data_aao",
            "aao_simulation_data", 
            "offline_simulation_data",
            "simulation_data_aao",
            "aao_offline_data",
            "aao_sim_data",
            "simulation_results",
            "offline_results"
        ]
        
        found_tables = []
        for table_name in possible_tables:
            try:
                if offline_result_service.db.has_table(table_name):
                    # 查询这个表的数据数量
                    sql = f"SELECT COUNT(*) as count FROM {table_name}"
                    result = offline_result_service.db.query(sql, fetch_type=3)
                    count = result[0].get('count', 0) if result else 0
                    
                    # 查询最新时间戳
                    sql = f"SELECT ts FROM {table_name} ORDER BY ts DESC LIMIT 1"
                    result = offline_result_service.db.query(sql, fetch_type=3)
                    latest_ts = result[0].get('ts', 'N/A') if result else 'N/A'
                    
                    found_tables.append({
                        "table_name": table_name,
                        "exists": True,
                        "count": count,
                        "latest_timestamp": latest_ts
                    })
                else:
                    found_tables.append({
                        "table_name": table_name,
                        "exists": False,
                        "count": 0,
                        "latest_timestamp": "N/A"
                    })
            except Exception as table_error:
                found_tables.append({
                    "table_name": table_name,
                    "exists": False,
                    "error": str(table_error)
                })
        
        return jsonify({
            "success": True,
            "data": found_tables,
            "message": "调试信息获取成功"
        })
        
    except Exception as e:
        logger.error(f"调试接口失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"调试接口失败: {str(e)}"
        }), 500

# 添加字段显示名称映射方法到服务类
def _get_field_display_name(self, field_name: str) -> str:
    """根据字段名获取显示名称"""
    display_name_mapping = {
        # 出水参数
        'aao_effluent_q_ted': '总出水流量',
        'aao_effluent_tcod_ted': '离线模拟出水化学需氧量',
        'aao_effluent_tbod_ted': '离线模拟出水生化需氧量',
        'aao_effluent_ss_ted': '离线模拟出水悬浮固体浓度',
        'aao_effluent_tp_ted': '离线模拟出水总磷',
        'aao_effluent_tn_ted': '离线模拟出水总氮',
        'aao_effluent_snhx_ted': '离线模拟出水氨氮',
        'aao_effluent_snox_ted': '离线模拟出水硝氮',
        'aao_effluent_spo4_ted': '离线模拟出水正磷酸盐',
        
        # 曝气参数 - 1-1#AAO生化池
        'aao_cstr_front_1_1_qair_ntp_ted': '离线模拟1-1#AAO生化池曝气支管1曝气量',
        'aao_cstr_mid_1_1_qair_ntp_ted': '离线模拟1-1#AAO生化池曝气支管2曝气量',
        'aao_cstr_terminal_1_1_qair_ntp_ted': '离线模拟1-1#AAO生化池曝气支管3曝气量',
        
        # 曝气参数 - 1-2#AAO生化池
        'aao_cstr_front_1_2_qair_ntp_ted': '离线模拟1-2#AAO生化池曝气支管1曝气量',
        'aao_cstr_mid_1_2_qair_ntp_ted': '离线模拟1-2#AAO生化池曝气支管2曝气量',
        'aao_cstr_terminal_1_2_qair_ntp_ted': '离线模拟1-2#AAO生化池曝气支管3曝气量',
        
        # 曝气参数 - 2-1#AAO生化池
        'aao_cstr_front_2_1_qair_ntp_ted': '离线模拟2-1#AAO生化池曝气支管1曝气量',
        'aao_cstr_mid_2_1_qair_ntp_ted': '离线模拟2-1#AAO生化池曝气支管2曝气量',
        'aao_cstr_terminal_2_1_qair_ntp_ted': '离线模拟2-1#AAO生化池曝气支管3曝气量',
        
        # 曝气参数 - 2-2#AAO生化池
        'aao_cstr_front_2_2_qair_ntp_ted': '离线模拟2-2#AAO生化池曝气支管1曝气量',
        'aao_cstr_mid_2_2_qair_ntp_ted': '离线模拟2-2#AAO生化池曝气支管2曝气量',
        'aao_cstr_terminal_2_2_qair_ntp_ted': '离线模拟2-2#AAO生化池曝气支管3曝气量',
        
        # 投加参数
        'aao_pac_q_ted': '离线模拟2号加药间聚合氯化铝投加量',
        
        # 回流参数
        'aao_flowdivider3_1_1_influx_ted': '离线模拟1-1#AAO生化池内回流量',
        'aao_flowdivider3_1_2_influx_ted': '离线模拟1-2#AAO生化池内回流量',
        'aao_flowdivider3_2_1_influx_ted': '离线模拟2-1#AAO生化池内回流量',
        'aao_flowdivider3_2_2_influx_ted': '离线模拟2-2#AAO生化池内回流量'
    }
    
    return display_name_mapping.get(field_name, field_name)

# 将方法添加到服务类
OfflineResultService._get_field_display_name = _get_field_display_name
