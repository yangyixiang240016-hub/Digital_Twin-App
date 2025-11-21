from models.tdengine import get_latest_row

def get_latest_outflow_data():
    row = get_latest_row(
        table="realtime_data",
        cols=["effluent_tol_q_rd"]  
    )
    return row.get("effluent_tol_q_rd", None)
