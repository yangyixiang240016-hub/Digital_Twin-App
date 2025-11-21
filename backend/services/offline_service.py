import random
import time
from datetime import datetime, timedelta
import json

class OfflineSimulationService:
    """离线模拟服务类"""
    
    def __init__(self):
        self.process_configs = {
            'AAO': {
                'zones': ['aerZone1', 'aerZone2', 'aerZone3', 'aerZone4'],
                'parameters': ['MLR', 'RAS', 'SAS', 'PAC'],
                'targets': ['TN', 'NH3N', 'NO3', 'TP', 'COD']
            },
            'MBR': {
                'zones': ['aerZone1', 'aerZone2', 'aerZone3'],
                'parameters': ['MLR', 'RAS', 'SAS', 'PAC'],
                'targets': ['TN', 'NH3N', 'NO3', 'TP', 'COD']
            }
        }
    
    def run_simulation(self, params):
        """运行模拟"""
        process = params.get('process', 'AAO')
        sim_type = params.get('type', 'dynamic')
        mode = params.get('mode', 'aeration')
        source = params.get('source', 'cleaned')
        
        # 生成模拟结果
        result = {
            'kpi': self._generate_kpi_data(process, sim_type),
            'charts': self._generate_chart_data(process, sim_type),
            'tables': self._generate_table_data(process, sim_type),
            'metadata': {
                'process': process,
                'type': sim_type,
                'mode': mode,
                'source': source,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return result
    
    def _generate_kpi_data(self, process, sim_type):
        """生成KPI数据"""
        base_values = {
            'AAO': {
                'inflow_q': 80000,
                'effluent_q': 78000,
                'influent': {'COD': 200, 'TN': 45, 'NH3N': 35, 'TP': 4, 'SS': 150},
                'influent_pred': {'COD': 195, 'TN': 43, 'NH3N': 33, 'TP': 3.8, 'SS': 145},
                'effluent_real': {'COD': 25, 'TN': 8, 'NH3N': 2, 'TP': 0.5, 'SS': 10},
                'effluent_sim': {'COD': 23, 'TN': 7.5, 'NH3N': 1.8, 'TP': 0.4, 'SS': 8},
                'effluent_pred': {'COD': 22, 'TN': 7.2, 'NH3N': 1.6, 'TP': 0.35, 'SS': 7}
            },
            'MBR': {
                'inflow_q': 80000,
                'effluent_q': 79000,
                'influent': {'COD': 200, 'TN': 45, 'NH3N': 35, 'TP': 4, 'SS': 150},
                'influent_pred': {'COD': 195, 'TN': 43, 'NH3N': 33, 'TP': 3.8, 'SS': 145},
                'effluent_real': {'COD': 15, 'TN': 5, 'NH3N': 1, 'TP': 0.2, 'SS': 2},
                'effluent_sim': {'COD': 13, 'TN': 4.5, 'NH3N': 0.8, 'TP': 0.15, 'SS': 1.5},
                'effluent_pred': {'COD': 12, 'TN': 4.2, 'NH3N': 0.7, 'TP': 0.12, 'SS': 1.2}
            }
        }
        
        # 添加随机变化
        kpi_data = base_values.get(process, base_values['AAO']).copy()
        for key, value in kpi_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (int, float)):
                        variation = random.uniform(0.9, 1.1)
                        kpi_data[key][sub_key] = round(sub_value * variation, 2)
            elif isinstance(value, (int, float)):
                variation = random.uniform(0.95, 1.05)
                kpi_data[key] = round(value * variation, 2)
        
        return kpi_data
    
    def _generate_chart_data(self, process, sim_type):
        """生成图表数据"""
        # 生成时间序列数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        time_points = []
        current_time = start_time
        while current_time <= end_time:
            time_points.append(current_time.strftime('%Y-%m-%d %H:%M'))
            current_time += timedelta(hours=2)
        
        # 生成各参数的时间序列
        chart_data = {
            'time': time_points,
            'influent': {
                'COD': [random.uniform(180, 220) for _ in time_points],
                'TN': [random.uniform(40, 50) for _ in time_points],
                'NH3N': [random.uniform(30, 40) for _ in time_points],
                'TP': [random.uniform(3.5, 4.5) for _ in time_points],
                'SS': [random.uniform(140, 160) for _ in time_points]
            },
            'effluent_real': {
                'COD': [random.uniform(20, 30) for _ in time_points],
                'TN': [random.uniform(6, 10) for _ in time_points],
                'NH3N': [random.uniform(1.5, 2.5) for _ in time_points],
                'TP': [random.uniform(0.3, 0.7) for _ in time_points],
                'SS': [random.uniform(5, 15) for _ in time_points]
            },
            'effluent_sim': {
                'COD': [random.uniform(18, 28) for _ in time_points],
                'TN': [random.uniform(5.5, 9.5) for _ in time_points],
                'NH3N': [random.uniform(1.2, 2.2) for _ in time_points],
                'TP': [random.uniform(0.25, 0.65) for _ in time_points],
                'SS': [random.uniform(4, 14) for _ in time_points]
            }
        }
        
        return chart_data
    
    def _generate_table_data(self, process, sim_type):
        """生成表格数据"""
        table_data = []
        
        # 生成参数优化结果表格
        if sim_type == 'dynamic':
            for i in range(10):
                table_data.append({
                    'time': (datetime.now() - timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M'),
                    'aerZone1': round(random.uniform(1000, 2000), 2),
                    'aerZone2': round(random.uniform(1000, 2000), 2),
                    'aerZone3': round(random.uniform(1000, 2000), 2),
                    'aerZone4': round(random.uniform(1000, 2000), 2) if process == 'AAO' else None,
                    'MLR': round(random.uniform(20000, 40000), 2),
                    'RAS': round(random.uniform(30000, 50000), 2),
                    'SAS': round(random.uniform(1000, 3000), 2),
                    'PAC': round(random.uniform(5, 15), 2),
                    'effluent_COD': round(random.uniform(20, 30), 2),
                    'effluent_TN': round(random.uniform(6, 10), 2),
                    'effluent_NH3N': round(random.uniform(1.5, 2.5), 2),
                    'effluent_TP': round(random.uniform(0.3, 0.7), 2),
                    'effluent_SS': round(random.uniform(5, 15), 2)
                })
        else:
            # 稳态模拟结果
            table_data.append({
                'parameter': 'Aeration Zone 1',
                'current': round(random.uniform(1000, 2000), 2),
                'optimized': round(random.uniform(1000, 2000), 2),
                'improvement': round(random.uniform(-10, 10), 2)
            })
            table_data.append({
                'parameter': 'Aeration Zone 2',
                'current': round(random.uniform(1000, 2000), 2),
                'optimized': round(random.uniform(1000, 2000), 2),
                'improvement': round(random.uniform(-10, 10), 2)
            })
            table_data.append({
                'parameter': 'MLR Return Flow',
                'current': round(random.uniform(20000, 40000), 2),
                'optimized': round(random.uniform(20000, 40000), 2),
                'improvement': round(random.uniform(-10, 10), 2)
            })
        
        return table_data
