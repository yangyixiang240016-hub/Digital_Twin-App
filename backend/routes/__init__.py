from .inflow import inflow_bp
from .outflow import outflow_bp
from .water_quality import water_bp
from .trend import trend_bp
from .offline import offline_bp
from .offline_result import offline_result_bp
from .data_clean import data_clean_bp
from .history_data import history_data_bp
from .system_params import system_params_bp
from models.tdengine import get_index_blueprint
# 后续添加：
# from .simulate import simulate_bp
# from .cleaning import cleaning_bp
# from .optimize import optimize_bp

def register_routes(app):
    app.register_blueprint(get_index_blueprint()) 
    app.register_blueprint(inflow_bp, url_prefix='/api')
    app.register_blueprint(water_bp, url_prefix='/api')
    app.register_blueprint(outflow_bp, url_prefix='/api')
    app.register_blueprint(trend_bp, url_prefix='/api')
    app.register_blueprint(offline_bp, url_prefix='/api')
    app.register_blueprint(offline_result_bp, url_prefix='/api')
    app.register_blueprint(data_clean_bp, url_prefix='/api')
    app.register_blueprint(history_data_bp, url_prefix='/api')
    app.register_blueprint(system_params_bp, url_prefix='/api')
    # app.register_blueprint(simulate_bp)
    # app.register_blueprint(cleaning_bp)
    # app.register_blueprint(optimize_bp)
