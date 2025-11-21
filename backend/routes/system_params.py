from flask import Blueprint, request, jsonify
from services.system_params_service import get_system_params_service

system_params_bp = Blueprint('system_params', __name__)

@system_params_bp.route('/system-params', methods=['GET'])
def get_system_params():
    """获取系统参数全集"""
    try:
        service = get_system_params_service()
        result = service.get_system_params()
        status = 200 if result.get("success") else 500
        return jsonify(result), status
    except Exception as e:
        return jsonify({
            "success": False,
            "data": None,
            "message": f"获取失败: {str(e)}"
        }), 500


@system_params_bp.route('/system-params', methods=['POST'])
def update_system_params():
    """更新系统参数"""
    import logging
    logger = logging.getLogger("DigitalTwinApp")
    
    try:
        payload = request.get_json(force=True, silent=True) or {}
        logger.info(f"[参数范围更新] 路由层收到POST请求")
        logger.info(f"[参数范围更新] 请求payload类型: {type(payload)}")
        logger.info(f"[参数范围更新] 请求payload键数量: {len(payload)}")
        logger.info(f"[参数范围更新] 请求payload键列表: {list(payload.keys())[:30]}...")  # 显示前30个键
        
        # 检查上下限字段
        upper_limit_keys = [k for k in payload.keys() if 'upper_limit' in k]
        lower_limit_keys = [k for k in payload.keys() if 'lower_limit' in k]
        logger.info(f"[参数范围更新] 路由层检测到上限字段数: {len(upper_limit_keys)}")
        logger.info(f"[参数范围更新] 路由层检测到下限字段数: {len(lower_limit_keys)}")
        if upper_limit_keys:
            logger.info(f"[参数范围更新] 路由层示例上限字段: {upper_limit_keys[:5]}")
            logger.info(f"[参数范围更新] 路由层示例上限值: {[(k, payload[k]) for k in upper_limit_keys[:3]]}")
        if lower_limit_keys:
            logger.info(f"[参数范围更新] 路由层示例下限字段: {lower_limit_keys[:5]}")
            logger.info(f"[参数范围更新] 路由层示例下限值: {[(k, payload[k]) for k in lower_limit_keys[:3]]}")
        
        service = get_system_params_service()
        result = service.update_system_params(payload)
        
        logger.info(f"[参数范围更新] 路由层返回结果: success={result.get('success')}, message={result.get('message')}")
        
        if result.get("success"):
            return jsonify(result), 200
        message = result.get("message", "")
        if isinstance(message, str) and message.startswith("更新失败: "):
            trimmed = message.replace("更新失败: ", "", 1)
            try:
                err_data = eval(trimmed) if trimmed.startswith("{") else {}
                if isinstance(err_data, dict) and err_data.get("message"):
                    return jsonify(result), 400
            except Exception:
                pass
        return jsonify(result), 500
    except Exception as e:
        logger.error(f"[参数范围更新] 路由层异常: {str(e)}")
        import traceback
        logger.error(f"[参数范围更新] 路由层异常堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"更新失败: {str(e)}"
        }), 500


@system_params_bp.route('/system-params/predict-algorithm', methods=['GET'])
def get_predict_algorithm():
    """获取当前预测算法"""
    try:
        service = get_system_params_service()
        result = service.get_predict_algorithm()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "algorithm": "arima",
            "value": 0,
            "message": f"获取失败: {str(e)}"
        }), 500

@system_params_bp.route('/system-params/predict-algorithm', methods=['POST'])
def update_predict_algorithm():
    """更新预测算法"""
    try:
        data = request.get_json()
        algorithm = data.get('algorithm')
        
        if not algorithm:
            return jsonify({
                "success": False,
                "message": "缺少algorithm参数"
            }), 400
        
        if algorithm not in ["arima", "transformer"]:
            return jsonify({
                "success": False,
                "message": "algorithm参数只能是arima或transformer"
            }), 400
        
        service = get_system_params_service()
        result = service.update_predict_algorithm(algorithm)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"更新失败: {str(e)}"
        }), 500

