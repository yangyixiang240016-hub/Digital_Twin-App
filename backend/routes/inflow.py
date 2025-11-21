from flask import Blueprint, jsonify
from services.inflow_service import get_latest_inflow_data

inflow_bp = Blueprint('inflow', __name__)

@inflow_bp.route('/inflow', methods=['GET'])
def get_inflow():
    try:
        result = get_latest_inflow_data()
        return jsonify({"value": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
