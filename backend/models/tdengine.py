from dbpkg.TDengineDB import TDengineDB
import dbpkg.DBBase

def get_latest_row(table, cols):
    db = TDengineDB()
    db.connect(
        host="192.168.3.92",
        user="root",
        password="taosdata",
        database="beihu_dt",
        port=6041,
        link_mode=dbpkg.DBBase.REST_LINK
    )
    result = db.query(
        table_name=table,
        select_cols=cols,
        conditions="1=1 ORDER BY ts DESC LIMIT 1"
    )
    return result[0] if result else {}

def get_earliest_row(table, cols):
    """
    获取最早一条数据
    """
    db = TDengineDB()
    db.connect(
        host="192.168.3.92",
        user="root",
        password="taosdata",
        database="beihu_dt",
        port=6041,
        link_mode=dbpkg.DBBase.REST_LINK
    )

    condition_str = "1=1 ORDER BY ts ASC LIMIT 1"

    result = db.query(
        table_name=table,
        select_cols=cols,
        conditions=condition_str
    )
    return result[0] if result else {}


# ✅ 添加欢迎页注册支持（用于 routes/__init__.py 中引用）
def get_index_blueprint():
    from flask import Blueprint
    index_bp = Blueprint('index', __name__)

    @index_bp.route('/')
    def index():
        return '✅ 欢迎使用北湖数字孪生系统后端 API 服务'

    return index_bp

def query_raw(sql: str):
    """
    执行原始 SQL 查询，返回 tuple 列表，例如 [(ts, value), (ts, value), ...]
    """
    db = TDengineDB()
    db.connect(
        host="192.168.3.92",
        user="root",
        password="taosdata",
        database="beihu_dt",
        port=6041,
        link_mode=dbpkg.DBBase.REST_LINK,
        as_dict=False  # 必须返回 tuple，便于处理 (ts, val)
    )
    return db._query(sql, as_dict=True)