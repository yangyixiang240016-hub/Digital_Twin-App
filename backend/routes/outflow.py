from flask import Blueprint, jsonify
from services.outflow_service import get_latest_outflow_data

outflow_bp = Blueprint('outflow', __name__)

@outflow_bp.route('/outflow', methods=['GET'])
def get_outflow():
    try:
        result = get_latest_outflow_data()
        return jsonify({"value": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500