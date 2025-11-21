from models.tdengine import get_latest_row

def get_latest_inflow_data():
    row = get_latest_row(
        table="realtime_data",
        cols=["influent_tol_q_rd"]
    )
    return row.get("influent_tol_q_rd", None)
