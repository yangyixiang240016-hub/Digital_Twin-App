from flask import Blueprint, jsonify
from services.water_quality_service import (
    get_realtime_inflow_quality,
    get_predicted_inflow_quality,
    get_realtime_outflow_quality,
    get_simulated_outflow_quality,
    get_predicted_outflow_quality
)

water_bp = Blueprint('water_quality', __name__)

# ✅ 实时进水水质
@water_bp.route('/realtime/inflow/quality', methods=['GET'])
def get_realtime_inflow_quality_api():
    try:
        result = get_realtime_inflow_quality()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ 预测进水水质
@water_bp.route('/predict/inflow/quality', methods=['GET'])
def get_predicted_inflow_quality_api():
    try:
        result = get_predicted_inflow_quality()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 兼容旧路径
@water_bp.route('/water-quality', methods=['GET'])  
def get_water_quality_legacy():
    return get_realtime_inflow_quality_api()

# ✅ 实时出水水质
@water_bp.route('/realtime/outflow/quality', methods=['GET'])
def get_realtime_outflow_quality_api():
    try:
        result = get_realtime_outflow_quality()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ 模拟出水水质
@water_bp.route('/simulate/outflow/quality', methods=['GET'])
def get_simulated_outflow_quality_api():
    try:
        result = get_simulated_outflow_quality()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ 预测出水水质
@water_bp.route('/predict/outflow/quality', methods=['GET'])
def get_predicted_outflow_quality_api():
    try:
        result = get_predicted_outflow_quality()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
