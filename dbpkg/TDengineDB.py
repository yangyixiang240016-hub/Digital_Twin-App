#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开发该模块的目的是对TDengine进行封装，对外提供统一的标准化接口。简化数据库的调用，并且
可以轻松的在不同数据库之间切换。
TDengine开发文档：https://docs.taosdata.com/。

历史记录（按照以下格式依次添加）：
   日期        人员	      改动情况
2023-12-11    崔树标    创建。
"""

import logging
import traceback
import taos
import taosrest
from .settings import DATABASES


from . import DBBase
logger = logging.getLogger("DigitalTwinApp")

class TDengineDB(DBBase.DBBase):
    """封装TDengine库，对外提供统一的标准化接口。

    Examples:
        # 采用原生连接的方式连接数据库---------------------------------------------
        >>> db = TDengineDB()
        >>> db.connect(host="192.168.2.38", user="root", password="taosdata", database="test_dbpkg", 
        ...            port=6030, link_mode=DBBase.NATIVE_LINK, as_dict=True)
        True

        # 判断表是否存在
        >>> table_name = "persons"
        >>> db.has_table("table_name")
        False

        # 创建一张新表
        >>> db.create_table(table_name, ["id INT", 
        ...                              "name NCHAR(32)", 
        ...                              "gender NCHAR(4)", 
        ...                              "age TINYINT UNSIGNED"])
        True

        # 查询表结构
        >>> db.describe(table_name)[0:2]
        [('ts', 'TIMESTAMP', 8, ''), ('id', 'INT', 4, '')]

        # 插入若干条记录，可以一条一条插入，也可以一次插入多条
        >>> db.insert(table_name, [{"ts": "2023-12-23 10:16:01.001001", "id": 20230001, "name": "赵三", "gender": "男", "age": 34}])
        True
        >>> db.insert(table_name, [["2023-12-23 10:16:02.001002", 20230002, "周七", "女", 11]])
        True
        >>> db.insert(table_name, [{"ts": "2023-12-23 10:16:03.001003", "id": 20230003, "name": "钱四", "gender": "女", "age": 18}, 
        ...     {"ts": "2023-12-23 10:16:04.001004", "id": 20230004, "name": "孙五", "gender": "男", "age": 38}, 
        ...     {"ts": "2023-12-23 10:16:05.001005", "id": 20230005, "name": "李六", "gender": "男", "age": 89}, 
        ...     ["2023-12-23 10:16:06.001006", 20230006, "吴八", "男", 12], 
        ...     ["2023-12-23 10:16:07.001007", 20230007, "郑九", "女", 24], 
        ...     ["2023-12-23 10:16:08.001008", 20230008, "王十", "男", 28]])
        True

        # 查询数据库
        >>> db.query(table_name)[0]
        {'ts': datetime.datetime(2023, 12, 23, 10, 16, 1, 1000), 'id': 20230001, 'name': '赵三', 'gender': '男', 'age': 34}
        >>> db.query(table_name, ["name", "gender", "age"])[0]
        {'name': '赵三', 'gender': '男', 'age': 34}
        >>> db.query(table_name,
        ...          select_cols=["id", "name", "gender", "age"], 
        ...          fetch_type=3,
        ...          conditions="gender='男' AND age>18", 
        ...          order_cols=["age"],
        ...          order_by=[DBBase.ORDER_DESC])[0]
        {'id': 20230005, 'name': '李六', 'gender': '男', 'age': 89}

        # 修改记录，将吴八的年龄修改为100
        >>> db.update(table_name, {"age": 100}, "name='吴八'")
        True
        >>> data = db.query(table_name)
        >>> data[5]
        {'ts': datetime.datetime(2023, 12, 23, 10, 16, 6, 1000), 'id': 20230006, 'name': '吴八', 'gender': '男', 'age': 100}

        # 修改记录，将所有人的年龄+100
        >>> for record in data:
        ...     name = record["name"]
        ...     db.update(table_name, {"age": record["age"] + 100}, f"name='{name}'")
        True
        True
        True
        True
        True
        True
        True
        True
        >>> db.query(table_name)[-1]
        {'ts': datetime.datetime(2023, 12, 23, 10, 16, 8, 1000), 'id': 20230008, 'name': '王十', 'gender': '男', 'age': 128}

        # 删除记录，如删除150岁以下的人员
        >>> db.delete(table_name, "age<150")
        True
        >>> sql = "SELECT * FROM persons"
        >>> db.execute(sql)[0]
        {'ts': datetime.datetime(2023, 12, 23, 10, 16, 5, 1000), 'id': 20230005, 'name': '李六', 'gender': '男', 'age': 189}

        # 删除表中所有数据
        >>> db.delete(table_name)
        True
        >>> db.query(table_name)       
        []

        # 测试完成，删除表
        >>> db.delete_table(table_name)
        True

        # 关闭数据库
        >>> db.close()

        # 采用REST连接的方式连接数据库--------------------------------------------
        >>> db = TDengineDB()
        >>> db.connect(host="192.168.2.38", user="root", password="taosdata", database="test_dbpkg", 
        ...            port=6041, link_mode=DBBase.REST_LINK, as_dict=True)
        True

        # 判断表是否存在
        >>> table_name = "persons"
        >>> db.has_table("table_name")
        False

        # 创建一张新表
        >>> db.create_table(table_name, ["id INT", 
        ...                              "name NCHAR(32)", 
        ...                              "gender NCHAR(4)", 
        ...                              "age TINYINT UNSIGNED"])
        True

        # 查询表结构
        >>> db.describe(table_name)[0:2]
        [['ts', 'TIMESTAMP', 8, ''], ['id', 'INT', 4, '']]

        # 插入若干条记录，可以一条一条插入，也可以一次插入多条
        >>> db.insert(table_name, [{"ts": "2023-12-23 10:16:01.001001", "id": 20230001, "name": "赵三", "gender": "男", "age": 34}])
        True
        >>> db.insert(table_name, [["2023-12-23 10:16:02.001002", 20230002, "周七", "女", 11]])
        True
        >>> db.insert(table_name, [{"ts": "2023-12-23 10:16:03.001003", "id": 20230003, "name": "钱四", "gender": "女", "age": 18}, 
        ...     {"ts": "2023-12-23 10:16:04.001004", "id": 20230004, "name": "孙五", "gender": "男", "age": 38}, 
        ...     {"ts": "2023-12-23 10:16:05.001005", "id": 20230005, "name": "李六", "gender": "男", "age": 89}, 
        ...     ["2023-12-23 10:16:06.001006", 20230006, "吴八", "男", 12], 
        ...     ["2023-12-23 10:16:07.001007", 20230007, "郑九", "女", 24], 
        ...     ["2023-12-23 10:16:08.001008", 20230008, "王十", "男", 28]])
        True

        # 查询数据库
        >>> db.query(table_name)[0]
        {'ts': datetime.datetime(2023, 12, 23, 10, 16, 1, 1000), 'id': 20230001, 'name': '赵三', 'gender': '男', 'age': 34}
        >>> db.query(table_name, ["name", "gender", "age"])[0]
        {'name': '赵三', 'gender': '男', 'age': 34}
        >>> db.query(table_name,
        ...          select_cols=["id", "name", "gender", "age"], 
        ...          fetch_type=3,
        ...          conditions="gender='男' AND age>18", 
        ...          order_cols=["age"],
        ...          order_by=[DBBase.ORDER_DESC])[0]
        {'id': 20230005, 'name': '李六', 'gender': '男', 'age': 89}

        # 修改记录，将吴八的年龄修改为100
        >>> db.update(table_name, {"age": 100}, "name='吴八'")
        True
        >>> data = db.query(table_name)
        >>> data[5]
        {'ts': datetime.datetime(2023, 12, 23, 10, 16, 6, 1000), 'id': 20230006, 'name': '吴八', 'gender': '男', 'age': 100}

        # 修改记录，将所有人的年龄+100
        >>> for record in data:
        ...     name = record["name"]
        ...     db.update(table_name, {"age": record["age"] + 100}, f"name='{name}'")
        True
        True
        True
        True
        True
        True
        True
        True
        >>> db.query(table_name)[-1]
        {'ts': datetime.datetime(2023, 12, 23, 10, 16, 8, 1000), 'id': 20230008, 'name': '王十', 'gender': '男', 'age': 128}

        # 删除记录，如删除150岁以下的人员
        >>> db.delete(table_name, "age<150")
        True
        >>> sql = "SELECT * FROM persons"
        >>> db.execute(sql)[0]
        {'ts': datetime.datetime(2023, 12, 23, 10, 16, 5, 1000), 'id': 20230005, 'name': '李六', 'gender': '男', 'age': 189}

        # 删除表中所有数据
        >>> db.delete(table_name)
        True
        >>> db.query(table_name)       
        []

        # 测试完成，删除表
        >>> db.delete_table(table_name)
        True

        # 关闭数据库
        >>> db.close()
    """
    def __init__(self, **kw) -> None:
        super(TDengineDB, self).__init__(**kw)

    def connect(self, **kw) -> bool:
        """连接数据库。

        如：connect(host="192.168.2.38", user="root", password="taosdata", 
                   database="test_dbpkg", port=6041, link_mode=DBBase.REST_LINK)

        Arguments:
            host: 数据库服务器的IP地址，即要连接的节点的FQDN。
            user: 用户或者账户名，默认值是root。
            password: 密码，默认值是taosdata。
            database: 数据库名称。
            port: 要连接的数据节点的端口，即serverPort配置，默认值是6030。
            link_mode: 连接方式，默认为原生连接。
            config: 只用于原生连接，设置客户端配置文件路径。在Windows上默认是C:\\TDengine\\cfg，在Linux/macOS系统上默认是/etc/taos/。
            timezone: 只用于原生连接，设置使用的时区，默认为本地时区。
            timeout: 只用于REST连接，设置HTTP请求超时时间，单位为秒，默认为30秒，一般无需配置。
            as_dict: 查询结果存储方式，True为字典列表，否则为元组列表，默认为字典列表。
        Returns:
            数据库连接成功时返回True，否则返回False。
        """
        self._host = kw.get("host", "")                             # 数据库服务器的IP地址
        self._user = kw.get("user", "root")                         # 用户名
        self._password = kw.get("password", "taosdata")             # 密码
        self._database = kw.get("database", "")                     # 数据库名称
        self._port = kw.get("port", 6030)                           # 端口 6030 6041
        self._link_mode = kw.get("link_mode", DBBase.NATIVE_LINK)   # 连接方式
        self._config = kw.get("config", "C:\\TDengine\\cfg")        # 配置文件的路径
        self._timezone = kw.get("timezone", "Asia/Shanghai")        # 时区
        self._timeout = kw.get("timeout", 30)                       # HTTP请求超时时间
        self._as_dict = kw.get("as_dict", True)                     # 查询结果存储方式，True为字典列表，否则为元组列表

        assert self._host, "请指定数据库服务器的IP地址！"
        assert self._database, "请指定数据库名称！"

        # 连接数据库
        logger.info((f"host={self._host}, user={self._user}, password={self._password}, database={self._database}, "
                     f"port={self._port}, link_mode={self._link_mode}, config={self._config}, timezone={self._timezone}"))

        if self._link_mode == DBBase.NATIVE_LINK: # 原生连接
            try:
                self._connect: taos.TaosConnection = taos.connect(host=self._host,
                                                                  user=self._user,
                                                                  password=self._password,
                                                                  database=self._database,
                                                                  port=self._port)
            except taos.Error as e:
                logger.error(e)
                logger.error(f"exception class: {e.__class__.__name__}")
                logger.error(f"error number: {e.errno}")
                logger.error(f"error message: {e.msg}")
                return False
            except BaseException as other:
                logger.error("exception occur")
                logger.error(other)
                return False

            # 设置数据库的游标
            try:
                self._cursor: taos.TaosCursor = self._connect.cursor()
            except taos.Error as e:
                logger.error(e)
                logger.error(f"exception class: {e.__class__.__name__}")
                logger.error(f"error number: {e.errno}")
                logger.error(f"error message: {e.msg}")
                return False
        elif self._link_mode == DBBase.REST_LINK:   # REST连接
            try:
                self._connect: taosrest.TaosRestConnection = taosrest.connect(url=f"{self._host}:{self._port}", 
                                                                              user=self._user, 
                                                                              password=self._password, 
                                                                              database=self._database, 
                                                                              timeout=self._timeout)
            except taosrest.Error as e:
                logger.error(e)
                logger.error(f"exception class: {e.__class__.__name__}")
                logger.error(f"error number: {e.errno}")
                logger.error(f"error message: {e.msg}")
                return False
            except BaseException as other:
                logger.error("exception occur")
                logger.error(other)
                return False

            # 设置数据库的游标
            try:
                self._cursor: taosrest.TaosRestCursor = self._connect.cursor()
            except taosrest.Error as e:
                logger.error(e)
                logger.error(f"exception class: {e.__class__.__name__}")
                logger.error(f"error number: {e.errno}")
                logger.error(f"error message: {e.msg}")
                return False
        else:
            logger.warning(f"不支持的数据库连接方式：{self._link_mode}！只能是{DBBase.NATIVE_LINK}或{DBBase.REST_LINK}")
            return False

        logger.info(f"数据库已连接！connect={type(self._connect)}, cursor={type(self._cursor)}")
        return True

    def connect_default(self) -> bool:
        """连接默认的数据库。

        Arguments:
            无。
        Returns:
            数据库连接成功时返回True，否则返回False。
        """
        return self.connect(host=DATABASES["default"]["HOST"], 
                            user=DATABASES["default"]["USER"], 
                            password=DATABASES["default"]["PASSWORD"], 
                            database=DATABASES["default"]["NAME"])

    def create_table(self, table_name: str, args: list) -> bool:
        """通过输入的list创建一张新表。

        每个字段用一个字符串表示，顺序为："字段名 数据类型 约束条件等"。
        如: 创建一张名为persons的新表，包含5个字段：
            字段一为ts，数据类型为TIMESTAMP，TDengine规定第一个字段必须为时间戳，因此创建表的时候自动加入该字段；
            字段二为id，数据类型为INT；
            字段三为name，数据类型为NCHAR，最大长度为32；
            字段四为gender，数据类型为NCHAR，最大长度为4；
            字段五为age，数据类型为TINYINT。
            create_table(table_name, ["id INT", "name NCHAR(32)", "gender NCHAR(4)", "age TINYINT UNSIGNED"])

        Arguments:
            table_name: 表名。
            args: 定义表每一列（字段）的名称、数据类型、约束条件等。
        Returns:
            新表创建成功返回True，否则返回False。
        """
        assert table_name, "表名不能为空！"
        assert len(args), "创建表时，至少要定义一个字段！"
        assert self._cursor, "请先调用connect()连接数据库！"

        # 拼接成SQL语句，TDengine要求第一列必须为时间戳，所以创建表的时候自动加入第一列时间戳
        fields = "ts TIMESTAMP," + ",".join(args)
        sql = f"CREATE TABLE {self._database}.{table_name} ({fields})"

        try:
            # 执行SQL语句，创建表
            logger.debug(sql)
            self._cursor.execute(sql)
            self._connect.commit()
        except Exception as e:
            logger.error(traceback.format_exc())
            return False

        return True

    def delete_table(self, table_name: str) -> bool:
        """删除一张表。

        Arguments:
            table_name: 表名。
        Returns:
            删除成功返回True，否则返回False。
        """
        assert table_name, "表名不能为空！"
        assert self._cursor, "请先调用connect()连接数据库！"

        sql = f"DROP TABLE {self._database}.{table_name}"

        try:
            # 执行SQL语句，删除表
            logger.debug(sql)
            self._cursor.execute(sql)
            self._connect.commit()
        except Exception as e:
            logger.error(traceback.format_exc())
            return False

        return True

    def tables(self) -> list:
        """列出数据库中所有的表名。

        Returns:
            返回一个list，存储了数据库中所有的表名。
        """
        assert self._cursor, "请先调用connect()连接数据库！"

        sql = "SHOW TABLES"
        try:
            # 执行SQL语句
            logger.debug(sql)
            self._cursor.execute(sql)
        except Exception as e:
            logger.error(traceback.format_exc())
            return None

        all_tables = self._cursor.fetchall()
        return [table[0] for table in all_tables]

    def has_table(self, table_name: str) -> bool:
        """判断数据库中是否存在指定的表。

        Arguments:
            table_name: 表名。
        Returns:
            数据库中存在指定的表时返回True，否则返回False。
        """
        assert table_name, "表名不能为空！"

        all_tables = self.tables()
        if all_tables:
            return table_name in all_tables

        return False

    def describe(self, table_name: str) -> list:
        """查询表结构。

        查看表的结构，获得表中每个字段的详细信息，类似如下的信息：
        [('ts', 'TIMESTAMP', 8, ''), ('id', 'INT', 4, ''), ('name', 'NCHAR', 32, ''), 
         ('gender', 'NCHAR', 4, ''), ('age', 'TINYINT UNSIGNED', 1, '')]

        Arguments:
            table_name: 表名。
        Returns:
            返回值是元组列表，列表中的元素是元组，每个元组描述一个字段的信息。
        """
        assert table_name, "表名不能为空！"

        sql = f"DESCRIBE {self._database}.{table_name}"
        try:
            # 执行SQL语句
            logger.debug(sql)
            self._cursor.execute(sql)
        except Exception:
            logger.error(traceback.format_exc())
            return None

        return self._cursor.fetchall()

    def execute(self, sql: str) -> (dict | list | bool):
        """执行SQL语句。

        该函数功能过于强大，不推荐使用，除非调用者对输入的SQL语句十分熟悉。

        Arguments:
            sql: SQL语句。
        Returns:
            返回SQL语句执行后的结果，返回False表示SQL语句执行失败。
        """
        assert sql, "SQL语句不能为空！"
        assert self._cursor, "请先调用connect()连接数据库！"

        try:
            # 执行SQL语句
            command = sql[:6].upper()
            if command == "SELECT":
                return self._query(sql, self._as_dict)
            else:
                # logger.debug(sql)
                # 提交到数据库执行
                result = self._connect.execute(sql)
                self._connect.commit()
                return result
        except Exception:
            # 发生错误时回滚
            logger.error(traceback.format_exc())
            self._connect.rollback()

        # 此处不能返回None，因为SQL语句的执行结果可能是None，就无法和失败区分开
        return False

    def _query(self, sql: str, as_dict: bool = True) -> list:
        """通过SQL语句查询数据库。

        因为TDengine的原生连接和REST连接在查询数据库时，还是略有差异，因此特别封装该
        函数，用于执行数据库查询SQL语句，并根据模块参数，返回二维列表或者字典列表。

        Arguments:
            sql: SQL语句。
            as_dict: 查询结果返回字典列表，还是二维列表？默认为字典列表。
        Returns:
            返回查询结果，默认为字典列表，也可以是二维列表。
        """
        assert sql, "SQL语句不能为空！"
        assert self._cursor, "请先调用connect()连接数据库！"

        try:
            # 执行SQL语句
            # logger.debug(sql)
            logger.debug(sql)
            if self._link_mode == DBBase.REST_LINK:   # REST连接
                self._cursor.execute(sql)
                if as_dict:
                    cols = [meta[0] for meta in self._cursor.description]
                    rows = self._cursor.fetchall()
                    records = []
                    for row in rows:
                        records.append(dict(zip(cols, [value for value in row])))
                    return records
                else:
                    return self._cursor.fetchall()
            else:    # 原生连接
                result = self._connect.query(sql)
                if as_dict:
                    return result.fetch_all_into_dict()
                else:
                    return result.fetch_all()
        except Exception:
            logger.info(sql)
            logger.error(traceback.format_exc())

        return None

    def query(self, table_name: str, select_cols: list = None, fetch_type: int = DBBase.FETCH_ALL, 
              conditions: str = None, order_cols: list = None, order_by: list = None) -> (dict | list):
        """通过SQL语句及参数查询数据库。

        如：一、查询所有记录。
            query(table_name)。
            二、查询"name", "gender", "age"三个字段。
            query(table_name, ["name", "gender", "age"])。
            三、查询"id", "name", "gender", "age"四个字段，gender='男'且age>18，只取前3条记录，根据"age"倒序排序。
            query(table_name, select_cols=["id", "name", "gender", "age"], fetch_type=3, 
                  conditions="gender='男' AND age>18", order_cols=["age"], order_by=[DBBase.ORDER_DESC]))

        Arguments:
            table_name: 表名。
            select_cols: 要查询的字段，列表格式的字符串，空列表则表示查询所有字段。
            fetch_type: 指定查询后返回的记录数量，缺省为FETCH_ALL，返回查询到的所有记录。fetch_type=FETCH_ONE=-1时
                只返回查询结果中最上面的第一条记录；fetch_type=FETCH_ALL=0时返回查询到的所有记录；如果fetch_type>0，
                则使用LIMIT指令，从数据库中选取指定数量的记录。
            conditions: 查询的条件，即WHERE语句。
            order_cols: 用于排序的字段，字符串列表，空列表则表示不指定排序的字段。
            order_by: 排序方式为升序或降序，ORDER_ASC或ORDER_DESC的整数列表。
        Returns:
            返回查询结果，默认为字典格式。
        """
        assert table_name, "表名不能为空！"
        assert self._cursor, "请先调用connect()连接数据库！"

        # 加入待查询字段
        if select_cols and len(select_cols) > 0:
            columns = ",".join(select_cols)
            sql = f"SELECT {columns} FROM {self._database}.{table_name}"
        else:
            sql = f"SELECT * FROM {self._database}.{table_name}"

        # 加入筛选条件
        if conditions:
            sql += f" WHERE {conditions}"

        # 加入排序字段和排序方法
        order_bys = []
        if order_cols and len(order_cols) > 0 and order_by and len(order_by) > 0:
            orders = []
            for order_con in zip(order_cols, order_by):
                if order_con[1] == DBBase.ORDER_ASC:
                    orders.append(f"{order_con[0]} ASC")
                else:
                    orders.append(f"{order_con[0]} DESC")

            order_conditions = " ORDER BY "+ ",".join(orders)
            sql += order_conditions

        # 如果fetch_type!=0，则需要使用LIMIT指令，从数据库中选取指定数量的记录
        if fetch_type == DBBase.FETCH_ONE:
            sql += " LIMIT 1"
        elif fetch_type > 0:
            sql += f" LIMIT {fetch_type}"
        return self._query(sql, self._as_dict)

    def insert(self, table_name: str, keyvalues: list) -> bool:
        """添加记录。

        如：一、一条一条记录插入。
            insert(table_name, [{"ts": "2023-12-23 10:16:21.005588", "id": 20230001, "name": "赵三", "gender": "男", "age": 34}])
            insert(table_name, [["2023-12-23 10:16:21.005588", 20230006, "吴八", "男", 12]])
            二、一次插入多条记录。
            insert(table_name, [{"ts": "2023-12-23 10:16:21.005588", "id": 20230003, "name": "孙五", "gender": "男", "age": 38}, 
                   ["2023-12-23 10:16:21.005588", 20230008, "王十", "男", 28]])

        Arguments:
            table_name: 表名。
            keyvalues: 待插入的数据，二维的list，里面的元素如果是list，只需
                提供每一列待插入的数值即可，但必须与表的字段顺序一一对应，如：
                    [["2023-12-23 10:16:21.005588", 20230005, "周七", "女", 11]]
                如果里面的元素是字典，则key作为字段名，value作为值，按照键值对插入表格，顺序随意，如：
                    [{"ts": "2023-12-23 10:16:21.005588", "id": 20230001, "name": "赵三", "gender": "男", "age": 34}]
                因为是二维数组，所以可以一次性插入多条记录，如：
                    [{"ts": "2023-12-23 10:16:21.005588", "id": 20230003, "name": "孙五", "gender": "男", "age": 38}, 
                     ["2023-12-23 10:16:21.005588", 20230007, "郑九", "女", 24]]
        Returns:
            插入成功返回True，否则返回False。
        """
        assert table_name, '表名不能为空！'

        for row in keyvalues:
            if isinstance(row, list):
                # 无需指定要插入数据的列名，只提供被插入的值
                values = str(row).replace("[", "").replace("]", "")
                sql = f"INSERT INTO {self._database}.{table_name} VALUES ({values})"
            elif isinstance(row, dict):
                # 指定要插入的列名及值
                columns = ','.join(list(row.keys()))
                values = str(list(row.values())).replace("[", "").replace("]", "")
                sql = f"INSERT INTO {self._database}.{table_name} ({columns}) VALUES ({values})"
            else:
                logger.warning(f"{row} 不是列表或字典，已跳过！")
                continue

            try:
                # 执行SQL语句
                # logger.debug(sql)
                self._cursor.execute(sql)
                # 提交到数据库执行
                self._connect.commit()
            except Exception as e:
                logger.info(sql)
                self._connect.rollback()
                logger.error(traceback.format_exc())
                return False

        return True
    
    def insert_many(self, table_name: str, list_dics: list) -> bool:
        """添加记录。
        一次插入多条记录
            和insert 函数区别：
            insert 函数对于批量传入多条待插入数据库的数据，会逐条插入(请参考原函数代码)
            例如：insert(table_name, [["2023-12-23 10:16:21.005588", 20230008, "李三", "女", 28], 
                                      ["2023-12-23 10:16:21.005588", 20230008, "张九", "女", 28],
                                     ["2023-12-23 10:16:21.005588", 20230008, "王十", "男", 28]])
            insert 函数 会再函数体内分别执行三次 插入操作
            当前insert_many 函数，list_dic 中传入的是字典列表
             [{"ts": "2023-12-23 10:16:21.005588", "id": 20230003, "name": "孙五", "gender": "男", "age": 38},  
             {"ts": "2023-12-23 10:16:21.005588", "id": 20230003, "name": "孙五", "gender": "男", "age": 38}]
        Arguments:
            table_name: 表名。
            list_dics：待插入数据库中的数据列表，列表里的每一个元素是一个元组，每个元组包含有待插入数据库值的“全集”
        Returns:
            插入成功返回True，否则返回False。
        """
        assert table_name, '表名不能为空！'
        assert len(list_dics), '插入内容不能为空'
        if not isinstance(list_dics, list):
            logger.error("list_dics not instance of list")
            return False
        
        tmp_dic = list_dics[0]
        columns = ','.join(list(tmp_dic[0].keys())) # 获取表里面待插入的所有字段 该字段可以不指定，主要方便代码维护
        datas = [] # 待插入的数据合集
        for element in list_dics:
            for row in element:
               datas.append(tuple(list(row.values())))
        # 指定要插入的列名及值     
        sql = f"INSERT INTO {self._database}.{table_name} ({columns}) VALUES"
        try:
            # 执行SQL语句
            # logger.debug(f"{sql} {datas}")
            self._cursor.execute_many(sql,datas)
            # 提交到数据库执行
            self._connect.commit()
        except Exception as e:
            # 发生错误时回滚
            logger.debug(f"{sql} {datas}")
            self._connect.rollback()
            logger.error(traceback.format_exc())
            return False

        return True

    def delete(self, table_name: str, conditions: str = None) -> bool:
        """删除记录。

        删除记录时要格外小心！因为不能撤销！！不能重来！！！

        Arguments:
            table_name: 表名。
            conditions: 指定删除数据的过滤条件，不指定过滤条件则为表中所有数据，请慎重使用。
                特别说明，这里的WHERE条件中只支持对第一列时间戳的过滤。
        Returns:
            删除成功返回True，否则返回False。
        """
        assert table_name, "表名不能为空！"
        assert self._cursor, "请先调用connect()连接数据库！"

        if conditions:
            # 如果过滤条件用的是时间戳，则可以直接使用该过滤条件
            # TDEngine 只支持 ts = '2023-12-23 10:16:21.005588',一条一条删除，不支持批量，这里如果ts>='xx' ts<'xx' 应该不满足
            if conditions[:3] == "ts=":
                sql = f"DELETE FROM {self._database}.{table_name} WHERE {conditions}"
            # 因为TDengine在删除记录时只支持对第一列时间戳的过滤，因此先利用过滤条件查询
            # 出所有要删除的记录，提取出每一条记录的时间戳，再根据时间戳逐一删除记录
            else:
                # 先筛选出所有符合条件的记录
                sql = f"SELECT * FROM {self._database}.{table_name} WHERE {conditions}"
                try:
                    # 执行SQL语句
                    records = self._query(sql)

                    for record in records:
                        ts = record["ts"]
                        sql = f"DELETE FROM {self._database}.{table_name} WHERE ts='{ts}'"
                        # 执行SQL语句
                        logger.debug(sql)
                        self._cursor.execute(sql)
                        # 提交到数据库执行
                        self._connect.commit()

                    return True
                except Exception as e:
                    # 发生错误时回滚
                    logger.debug(sql)
                    self._connect.rollback()
                    logger.error(traceback.format_exc())
                    return False
        else:
            # 在不删除表的情况下，删除表中所有行，表的结构、属性、索引将保持不变
            sql = f"DELETE FROM {self._database}.{table_name}"

        try:
            # 执行SQL语句
            logger.debug(sql)
            self._cursor.execute(sql)
            # 提交到数据库执行
            self._connect.commit()
        except Exception as e:
            # 发生错误时回滚
            self._connect.rollback()
            logger.error(traceback.format_exc())
            return False

        return True

    def update(self, table_name: str, keyvalues: dict, conditions: str = None) -> bool:
        """更新表中已存在的记录。

        因为TDengine不支持UPDATE指令，而是采用INSERT的方式来修改记录，因此需要先根据
        筛选条件查询出所有符合要求的记录，然后用传入的参数修改记录，再插入到表中，TDengine
        根据ts字段来更新记录。
        如：一、将吴八的年龄修改为100
            update(table_name, {"age": 100}, "name='吴八'")
            二、将所有人的年龄+100
            data = query(table_name)
            for record in data:
                name = record["name"]
                update(table_name, {"age": record["age"] + 100}, f"name='{name}'")

        Arguments:
            table_name: 表名。
            keyvalues: 待更新的数据，key作为字段名，value作为值，按照键值来更新表格。
            conditions: 筛选条件，即WHERE语句。如果省略了WHERE子句，则UPDATE指令会将
                表中所有行的指定键值对全部修改，执行没有WHERE子句的UPDATE要慎重！再慎重！！！
        Returns:
            更新成功返回True，否则返回False。
        """
        assert table_name, "表名不能为空！"
        assert self._cursor, "请先调用connect()连接数据库！"

        # 先根据筛选条件查询出所有符合要求的记录
        if conditions:
            sql = f"SELECT * FROM {self._database}.{table_name} WHERE {conditions}"
        else:
            sql = f"SELECT * FROM {self._database}.{table_name}"
        try:
            # 执行SQL语句
            records = self._query(sql)
        except Exception as e:
            logger.error(traceback.format_exc())
            return False

        # 如果根据指定的查询条件，查询到的记录为0，则直接返回False
        if not len(records):
            return False

        # 逐一更新每一条记录的指定字段
        for record in records:
            record['ts'] = f"{record['ts']}"
            # 得到所有的字段名
            columns = ','.join(list(record.keys()))
            # 用传入的参数修改记录
            for k, v in keyvalues.items():
                record[k] = v
            values = str(list(record.values())).replace("[", "").replace("]", "")
            sql = f"INSERT INTO {self._database}.{table_name} ({columns}) VALUES ({values})"

            try:
                # 执行SQL语句
                logger.debug(sql)
                self._cursor.execute(sql)
                # 提交到数据库执行
                self._connect.commit()
            except Exception as e:
                # 发生错误时回滚
                logger.error(sql)
                self._connect.rollback()
                logger.error(traceback.format_exc())
                return False

        return True

# MCP_test = TDengineDB()
# MCP_test.connect(host="192.168.3.92", user="root", password="taosdata", 
#                    database="beihu_dt", port=6041, link_mode=DBBase.REST_LINK)
# result = MCP_test.query("offline_simulation_data_aao", select_cols=["id", "simulate_time_ted"], fetch_type=3)
# print(result)