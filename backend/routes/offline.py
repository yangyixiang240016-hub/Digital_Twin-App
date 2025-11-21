from flask import Blueprint, jsonify, request
from services.offline_service import OfflineSimulationService
import uuid
import threading
import time

offline_bp = Blueprint('offline', __name__)

# 全局任务存储
tasks = {}

@offline_bp.route('/offline/sim/run', methods=['POST'])
def start_offline_simulation():
    """启动离线模拟任务"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['process', 'type', 'mode', 'source']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必需参数: {field}"}), 400
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务信息
        task_info = {
            'taskId': task_id,
            'status': 'running',
            'progress': 0,
            'process': data['process'],
            'type': data['type'],
            'mode': data['mode'],
            'source': data['source'],
            'startTime': time.time(),
            'message': '任务已启动'
        }
        
        # 存储任务
        tasks[task_id] = task_info
        
        # 启动后台任务
        thread = threading.Thread(
            target=run_simulation_task,
            args=(task_id, data)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({"jobId": task_id, "status": "started"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offline_bp.route('/offline/sim/status', methods=['GET'])
def get_simulation_status():
    """获取模拟任务状态"""
    try:
        job_id = request.args.get('jobId')
        if not job_id:
            return jsonify({"error": "缺少jobId参数"}), 400
        
        if job_id not in tasks:
            return jsonify({"error": "任务不存在"}), 404
        
        task = tasks[job_id]
        return jsonify({
            "status": task['status'],
            "progress": task['progress'],
            "message": task.get('message', ''),
            "taskId": job_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offline_bp.route('/offline/sim/result', methods=['GET'])
def get_simulation_result():
    """获取模拟结果"""
    try:
        job_id = request.args.get('jobId')
        if not job_id:
            return jsonify({"error": "缺少jobId参数"}), 400
        
        if job_id not in tasks:
            return jsonify({"error": "任务不存在"}), 404
        
        task = tasks[job_id]
        
        if task['status'] != 'done':
            return jsonify({"error": "任务尚未完成"}), 400
        
        # 返回模拟结果
        result = task.get('result', {})
        return jsonify({
            "kpi": result.get('kpi', {}),
            "charts": result.get('charts', {}),
            "tables": result.get('tables', []),
            "taskId": job_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_simulation_task(task_id, params):
    """后台运行模拟任务"""
    try:
        service = OfflineSimulationService()
        
        # 更新进度
        tasks[task_id]['progress'] = 10
        tasks[task_id]['message'] = '正在准备数据...'
        
        # 模拟数据处理
        time.sleep(2)
        tasks[task_id]['progress'] = 30
        tasks[task_id]['message'] = '正在运行模拟...'
        
        # 运行模拟
        result = service.run_simulation(params)
        
        # 更新进度
        tasks[task_id]['progress'] = 80
        tasks[task_id]['message'] = '正在生成结果...'
        
        # 模拟结果生成
        time.sleep(3)
        
        # 完成任务
        tasks[task_id]['status'] = 'done'
        tasks[task_id]['progress'] = 100
        tasks[task_id]['message'] = '任务完成'
        tasks[task_id]['result'] = result
        
    except Exception as e:
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['message'] = f'任务失败: {str(e)}'
        tasks[task_id]['progress'] = 0

@offline_bp.route('/offline/task/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """取消任务"""
    try:
        if task_id not in tasks:
            return jsonify({"error": "任务不存在"}), 404
        
        tasks[task_id]['status'] = 'cancelled'
        tasks[task_id]['message'] = '任务已取消'
        
        return jsonify({"status": "cancelled", "taskId": task_id})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
