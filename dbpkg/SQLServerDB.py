#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pymssql是python中用于SQL Server的开发包，开发该模块的目的是对pymssql进行封装，对外提供
统一的标准化接口。简化数据库的调用，并且可以轻松的在不同数据库之间切换。
pymssql开发文档：http://www.pymssql.org/。

历史记录（按照以下格式依次添加）：
   日期        人员	      改动情况
2023-11-06    崔树标    创建。
2023-11-18    崔树标    调试及测试。
2023-11-19    崔树标    测试用例及文档测试。
2023-11-20    崔树标    v1.0发布。
2023-12-21    崔树标    增加tables()，has_table()，describe()三个函数。
"""

import inspect
import logging
import os
import pymssql


from . import DBBase
logger = logging.getLogger("DigitalTwinApp")

class SQLServerDB(DBBase.DBBase):
    """封装pymssql库，对外提供统一的标准化接口。

    Examples:
        # 连接数据库
        >>> db = SQLServerDB()
        >>> db.connect(host="192.168.2.56", user="sa", password="123456", database="test_database", charset="UTF8")
        True

        # 判断表是否存在
        >>> db.has_table("Persons")
        False

        # 创建一张新表
        >>> table_name = "Persons"
        >>> db.create_table(table_name, ["ID int", "Name nvarchar(32) NOT NULL",
        ...                 "Gender nvarchar(4)", "Age tinyint"])
        True

        # 查询表结构
        >>> db.describe("Persons")[0]["COLUMN_NAME"]
        'ID'

        # 插入若干条记录，可以一条一条插入，也可以一次插入多条
        >>> db.insert(table_name, [{"ID": 20230001, "Name": "赵三", "Gender": "男", "Age": 34}])
        True
        >>> db.insert(table_name, [[20230002, "周七", "女", 11]])
        True
        >>> db.insert(table_name, [{"ID": 20230003, "Name": "钱四", "Gender": "女", "Age": 18}, 
        ...     {"ID": 20230004, "Name": "孙五", "Gender": "男", "Age": 38}, 
        ...     {"ID": 20230005, "Name": "李六", "Gender": "男", "Age": 89}, 
        ...     [20230006, "吴八", "男", 12], 
        ...     [20230007, "郑九", "女", 24], 
        ...     [20230008, "王十", "男", 28]])
        True

        # 查询数据库
        >>> db.query(table_name)[0]
        {'ID': 20230001, 'Name': '赵三', 'Gender': '男', 'Age': 34}
        >>> db.query(table_name, ["Name", "Gender", "Age"])[0]
        {'Name': '赵三', 'Gender': '男', 'Age': 34}
        >>> db.query(table_name,
        ...          select_cols=["ID", "Name", "Gender", "Age"], 
        ...          fetch_type=3,
        ...          conditions="Gender='男' AND Age>18", 
        ...          order_cols=["Age"],
        ...          order_by=[DBBase.ORDER_DESC])[2]
        {'ID': 20230001, 'Name': '赵三', 'Gender': '男', 'Age': 34}

        # 修改记录，将吴八的年龄修改为100
        >>> db.update(table_name, {"Age": 100}, "Name='吴八'")
        True
        >>> data = db.query(table_name)
        >>> data[5]
        {'ID': 20230006, 'Name': '吴八', 'Gender': '男', 'Age': 100}

        # 修改记录，将所有人的年龄+100
        >>> for record in data:
        ...     name = record["Name"]
        ...     db.update(table_name, {"Age": record["Age"] + 100}, f"Name='{name}'")
        True
        True
        True
        True
        True
        True
        True
        True
        >>> db.query(table_name)[-1]
        {'ID': 20230008, 'Name': '王十', 'Gender': '男', 'Age': 128}

        # 删除记录，如删除150岁以下的人员
        >>> db.delete(table_name, "Age<150")
        True
        >>> sql = "SELECT * FROM Persons"
        >>> db.execute(sql)[0]
        {'ID': 20230005, 'Name': '李六', 'Gender': '男', 'Age': 189}

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
        super(SQLServerDB, self).__init__(**kw)

    def connect(self, **kw) -> bool:
        """连接数据库。

        如：connect(host="192.168.2.56", user="sa", password="123456", database="test_database")。

        Arguments:
            host: 数据库服务器的IP地址。
            user: 用户或者账户名。
            password: 密码。
            database: 数据库名称。
            charset: 字符串编码类型，缺省为UTF8。
            as_dict: 查询结果是否采用字典格式存储。
        Returns:
            连接成功返回True，否则返回False。
        """
        self._host = kw.get("host", "")             # 数据库服务器的IP地址
        self._user = kw.get("user", "")             # 用户名
        self._password = kw.get("password", "")     # 密码
        self._database = kw.get("database", "")     # 数据库名称
        self._charset = kw.get("charset", "UTF8")   # 字符集
        self._as_dict = kw.get("as_dict", True)     # 查询结果用列表还是字典存储，True为字典，否则为列表

        assert self._host, "请指定数据库服务器的IP地址！"
        assert self._database, "请指定数据库名称！"

        # 连接数据库
        logger.info(f"""host={self._host}, user={self._user}, password={self._password}, database={self._database}""")

        try:
            self._connect = pymssql.connect(host=self._host,
                                            user=self._user,
                                            password=self._password,
                                            database=self._database,
                                            charset=self._charset,
                                            as_dict=self._as_dict)
        except Exception as e:
            logger.error(e)
            return False

        # 设置数据库的游标
        try:
            self._cursor = self._connect.cursor()
        except Exception as e:
            logger.error(e)
            return False

        logger.info("数据库连接成功！")
        return True

    def create_table(self, table_name: str, args: list) -> bool:
        """通过输入的list创建一张新表。

        每个字段用一个字符串表示，顺序为："字段名 数据类型 约束条件等"。
        如: 创建一张名为Persons的新表，包含4个字段：
            字段一为ID，数据类型为int；
            字段二为Name，数据类型为nvarchar，最大长度为32，该字段不允许空值；
            字段三为Gender，数据类型为nvarchar，最大长度为4；
            字段四为Age，数据类型为tinyint。
            create_table(table_name, ["ID int", "Name nvarchar(32) NOT NULL", 
                         "Gender nvarchar(4)", "Age tinyint"])

        Arguments:
            table_name: 表名。
            args: 定义表每一列（字段）的名称、数据类型、约束条件等。
        Returns:
            新表创建成功返回True，否则返回False。
        """
        assert table_name, "表名不能为空！"
        assert len(args), "创建表时，至少要定义一个字段！"
        assert self._cursor, "请先调用connect()连接数据库！"

        # 拼接成SQL语句
        fields = ",".join(args)
        sql = f"CREATE TABLE {table_name} ({fields})"

        try:
            # 执行SQL语句，创建表
            logger.debug(sql)
            self._cursor.execute(sql)
            self._connect.commit()
        except Exception as e:
            logger.error(e)
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

        sql = f"DROP TABLE {table_name}"

        try:
            # 执行SQL语句，删除表
            logger.debug(sql)
            self._cursor.execute(sql)
            self._connect.commit()
        except Exception as e:
            logger.error(e)
            return False

        return True

    def tables(self) -> list:
        """列出数据库中所有的表名。

        Returns:
            返回一个list，存储了数据库中所有的表名。
        """
        assert self._cursor, "请先调用connect()连接数据库！"

        # 方法一：sys.tables是SQL Server中存储表信息的系统视图之一，通过查询这个视图，
        # 可以获取数据库中所有表的信息，包括表名、模式名、创建日期等。
        sql = "SELECT name FROM sys.tables"

        # 方法二：INFORMATION_SCHEMA.TABLES是SQL Server中另一个存储表信息的系统视图，
        # 它提供了与sys.tables相似的功能，可以查询数据库中所有表的信息。
        # sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE ='BASE TABLE'"

        # 方法三：sys.objects是SQL Server中存储所有对象信息的系统视图，通过查询这个视图，
        # 可以获取数据库中所有表的信息，包括表名、模式名、类型等。
        # sql = "SELECT name FROM sys.objects WHERE type = 'U'"

        try:
            # 执行SQL语句
            logger.debug(sql)
            self._cursor.execute(sql)
        except Exception as e:
            logger.error(e)
            return None

        return [list(table.values())[0] for table in self._cursor.fetchall()]

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

        查看表的结构，获得表中每个字段的信息，类似于如下：
        [{'TABLE_CATALOG': 'test_database', 'TABLE_SCHEMA': 'dbo', 'TABLE_NAME': 'Persons', 'COLUMN_NAME': 'ID', 
          'ORDINAL_POSITION': 1, 'COLUMN_DEFAULT': None, 'IS_NULLABLE': 'YES', 'DATA_TYPE': 'int', 
          'CHARACTER_MAXIMUM_LENGTH': None, 'CHARACTER_OCTET_LENGTH': None, 'NUMERIC_PRECISION': 10, 
          'NUMERIC_PRECISION_RADIX': 10, 'NUMERIC_SCALE': 0, 'DATETIME_PRECISION': None, 'CHARACTER_SET_CATALOG': None, 
          'CHARACTER_SET_SCHEMA': None, 'CHARACTER_SET_NAME': None, 'COLLATION_CATALOG': None, 'COLLATION_SCHEMA': None, 
          'COLLATION_NAME': None, 'DOMAIN_CATALOG': None, 'DOMAIN_SCHEMA': None, 'DOMAIN_NAME': None}, ……]

        Arguments:
            table_name: 表名。
        Returns:
            返回表结构的信息。
        """
        assert table_name, "表名不能为空！"

        sql = f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
        try:
            # 执行SQL语句
            logger.debug(sql)
            self._cursor.execute(sql)
        except Exception as e:
            logger.error(e)
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
            logger.debug(sql)
            self._cursor.execute(sql)
            command = sql[:6].upper()
            if command != "SELECT":
                # 提交到数据库执行
                self._connect.commit()
        except Exception as e:
            # 发生错误时回滚
            self._connect.rollback()
            logger.error(e)
            # 此处不能返回None，因为SQL语句的执行结果可能是None，就无法和失败区分开
            return False

        # 非查询的SQL语句, 返回的可能是None
        return self._cursor.fetchall()

    def query(self, table_name: str, select_cols: list = None, fetch_type: int = DBBase.FETCH_ALL, 
              conditions: str = None, order_cols: list = None, order_by: list = None) -> (dict | list):
        """通过SQL语句及参数查询数据库。

        如：一、查询所有记录。
            query(table_name)。
            二、查询"Name", "Gender", "Age"三个字段。
            query(table_name, ["Name", "Gender", "Age"])。
            三、查询"ID", "Name", "Gender", "Age"四个字段，Gender='男'且Age>18，只取前3条记录，根据"Age"倒序排序。
            query(table_name, select_cols=["ID", "Name", "Gender", "Age"], fetch_type=3, 
                  conditions="Gender='男' AND Age>18", order_cols=["Age"], order_by=[DBBase.ORDER_DESC]))

        Arguments:
            table_name: 表名。
            select_cols: 要查询的字段，列表格式的字符串，空列表则表示查询所有字段。
            fetch_type: 指定查询后返回的记录数量，缺省为FETCH_ALL，返回查询到的所有记录。fetch_type=FETCH_ONE=-1时
                只返回查询结果中最上面的第一条记录；fetch_type=FETCH_ALL=0时返回查询到的所有记录；如果fetch_type>0，
                则使用TOP指令，从数据库中选取指定数量的记录。
            conditions: 查询的条件，即WHERE语句。
            order_cols: 用于排序的字段，字符串列表，空列表则不排序。
            order_by: 排序方式为升序或降序，ORDER_ASC或ORDER_DESC的整数列表。
        Returns:
            返回值查询结果，默认为字典格式。
        """
        assert table_name, "表名不能为空！"
        assert self._cursor, "请先调用connect()连接数据库！"

        # 如果fetch_type>0，则需要使用TOP指令，从数据库中选取指定数量的记录
        if fetch_type > 0:
            sql = f"SELECT TOP {fetch_type}"
        else:
            sql = "SELECT"

        # 加入待查询字段
        if select_cols and len(select_cols) > 0:
            columns = ",".join(select_cols)
            sql += f" {columns} FROM {table_name}"
        else:
            sql += f" * FROM {table_name}"

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

        try:
            # 执行SQL语句
            logger.debug(sql)
            self._cursor.execute(sql)
            if fetch_type < 0:
                return self._cursor.fetchone()
            else:
                return self._cursor.fetchall()
        except Exception as e:
            logger.error(e)

        return None

    def insert(self, table_name: str, keyvalues: list) -> bool:
        """添加记录。

        如：一、一条一条记录插入。
            insert(table_name, [{"ID": 20230001, "Name": "赵三", "Gender": "男", "Age": 34}])
            insert(table_name, [[20230006, "吴八", "男", 12]])
            二、一次插入多条记录。
            insert(table_name, [{"ID": 20230003, "Name": "孙五", "Gender": "男", "Age": 38}, 
                   [20230008, "王十", "男", 28]])

        Arguments:
            table_name: 表名。
            keyvalues: 待插入的数据，二维的list，里面的元素如果是list，只需
                提供每一列待插入的数值即可，但必须与表的字段顺序一一对应，如：
                    [[20230005, "周七", "女", 11]]
                如果里面的元素是字典，则key作为字段名，value作为值，按照键值对插入表格，顺序随意，如：
                    [{"ID": 20230001, "Name": "赵三", "Gender": "男", "Age": 34}]
                因为是二维数组，所以可以一次性插入多条记录，如：
                    [{"ID": 20230003, "Name": "孙五", "Gender": "男", "Age": 38}, 
                     [20230007, "郑九", "女", 24]]
        Returns:
            插入成功返回True，否则返回False。
        """
        assert table_name, '表名不能为空！'

        for row in keyvalues:
            if isinstance(row, list):
                # 无需指定要插入数据的列名，只提供被插入的值
                values = str(row).replace("[", "").replace("]", "")
                sql = f"INSERT INTO {table_name} VALUES ({values})"
            elif isinstance(row, dict):
                # 指定要插入的列名及值
                columns = ','.join(list(row.keys()))
                values = str(list(row.values())).replace("[", "").replace("]", "")
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            else:
                logger.warning(f"{row} 不是列表或字典，已跳过！")
                continue

            try:
                # 执行SQL语句
                logger.debug(sql)
                self._cursor.execute(sql)
                # 提交到数据库执行
                self._connect.commit()
            except Exception as e:
                # 发生错误时回滚
                self._connect.rollback()
                logger.error(e)
                return False

        return True

    def delete(self, table_name: str, conditions: str = None) -> bool:
        """删除记录。

        删除记录时要格外小心！因为不能撤销！！不能重来！！！

        Arguments:
            table_name: 表名。
            conditions: 删除条件，用于指定要删除哪些数据，即WHERE语句。如果不指定删除条件，则删除表中所有数据，
                SQL语句"TRUNCATE TABLE table_name"，也是类似的功能
        Returns:
            删除成功返回True，否则返回False。
        """
        assert table_name, "表名不能为空！"
        assert self._cursor, "请先调用connect()连接数据库！"

        if conditions:
            sql = f"DELETE FROM {table_name} WHERE {conditions}"
        else:
            # 在不删除表的情况下，删除表中所有行，表的结构、属性、索引将保持不变
            sql = f"DELETE FROM {table_name}"

        try:
            # 执行SQL语句
            logger.debug(sql)
            self._cursor.execute(sql)
            # 提交到数据库执行
            self._connect.commit()
        except Exception as e:
            # 发生错误时回滚
            self._connect.rollback()
            logger.error(e)
            return False

        return True

    def update(self, table_name: str, keyvalues: dict, conditions: str) -> bool:
        """更新表中已存在的记录。

        如：一、将吴八的年龄修改为100
            update(table_name, {"Age": 100}, "Name='吴八'")
            二、将所有人的年龄+100
            data = query(table_name)
            for record in data:
                name = record["Name"]
                update(table_name, {"Age": record["Age"] + 100}, f"Name='{name}'")

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

        data = ",".join([f"{k}={v}" for k, v in keyvalues.items()])
        if conditions:
            sql = f"UPDATE {table_name} SET {data} WHERE {conditions}"
        else:
            sql = f"UPDATE {table_name} SET {data}"

        try:
            # 执行SQL语句
            logger.debug(sql)
            self._cursor.execute(sql)
            # 提交到数据库执行
            self._connect.commit()
        except Exception as e:
            # 发生错误时回滚
            self._connect.rollback()
            logger.error(e)
            return False

        return True

