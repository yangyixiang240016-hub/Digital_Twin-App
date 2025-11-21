#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库封装的基础类，封装共性的函数和变量。

历史记录（按照以下格式依次添加）：
   日期        人员	      改动情况
2023-11-06    崔树标    创建。
2023-12-18    崔树标    添加TDengine相关的定义和变量。
"""

# 数据库查询时的常用指令类型
FETCH_ONE = -1      # 只返回查询结果中最上面的第一条记录
FETCH_ALL = 0       # 返回查询到的所有记录
ORDER_ASC = 0       # 查询结果升序
ORDER_DESC = 1      # 查询结果降序

# TDengine数据库连接方式
NATIVE_LINK = 0     # 原生连接，通过客户端驱动程序taosc直接与服务端程序taosd建立连接
REST_LINK = 1       # REST连接，通过taosAdapter组件提供的REST API建立与taosd的连接

class DBBase(object):
    """数据库基类。

    所有数据库封装类都要从该类派生。

    Examples:
        >>> db = DBBase()
        >>> db.database
        (None, None)
        >>> db.database_config
        (None, None, None, None, None, None, None, None, 0, None, None, 30)
    """
    def __init__(self) -> None:
        self._connect = None            # 数据库对象
        self._cursor = None             # 数据库游标

        # 连接数据库时，可能用到的参数
        self._host = None               # 数据库服务器的IP地址
        self._port = None               # 数据库服务器的端口
        self._user = None               # 用户名
        self._password = None           # 密码
        self._database = None           # 数据库名称
        self._charset = None            # 字符集
        self._autocommit = None         # 是否自动提交
        self._as_dict = None            # 查询结果用列表还是字典存储，True为字典，否则为列表

        # TDengine的参数
        self._link_mode = NATIVE_LINK   # 默认用原生连接
        self._config = None             # 客户端配置文件路径
        self._timezone = None           # 使用的时区
        self._timeout = 30              # HTTP请求超时时间

    def __del__(self) -> None:
        """确保数据库正常关闭。

        当用户忘记调用close()函数关闭数据库时，等数据库对象析构的时候主动关闭数据库。
        """
        self.close()

    def close(self) -> None:
        """关闭游标及数据库。"""
        if self._cursor:
            self._cursor.close()
            self._cursor = None
        if self._connect:
            self._connect.close()
            self._connect = None

    @property
    def database(self):
        """获取数据库对象及游标。

        当前提供的接口无法满足要求时，可以通过该函数获取数据库对象及游标，来实现需要的功能。
        非到必要时，不建议使用该方式，可能会破坏封装结构，应该考虑提供更多的接口来满足新的要求。

        Returns:
            返回数据库对象及游标。
        """
        return self._connect, self._cursor

    @property
    def database_config(self):
        """获取数据库相关配置信息。

        Returns:
            返回数据库服务器的IP、端口、用户名、密码、数据库名称、字符集、是否自动提交、
            查询结果是否采用字典存储、连接模式、配置文件路径、时区、HTTP请求超时时间等。
        """
        return (self._host, self._port, self._user, self._password, self._database, self._charset, 
                self._autocommit, self._as_dict, self._link_mode, self._config, self._timezone, self._timeout)

