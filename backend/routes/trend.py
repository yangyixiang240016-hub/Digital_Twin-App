from flask import Blueprint, request, jsonify
from services.trend_service import get_trend_data

trend_bp = Blueprint('trend', __name__)

@trend_bp.route('/trend', methods=['GET'])
def get_trend():
    try:
        param = request.args.get("param", "flow")
        data = get_trend_data(param)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
