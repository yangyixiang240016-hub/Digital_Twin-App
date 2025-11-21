# -*- coding: utf-8 -*-

"""
数据库封装包，提供了Access、SQL Server、TDengine数据库的封装。

AccessDB封装了pyodbc，提供了对Access数据库的基本操作。
SQLServerDB封装了pymssql，提供了对SQL Server数据库的基本操作。
TDengineDB封装了taos和taosrest，提供了对TDengine数据库的基本操作。

用户可以根据自己的需要，做一个重定向或者别名，就可以方便的在不同的数据库之间切换，如：
    Database = AccessDB
然后在应用层的代码中使用Database，因为Database = AccessDB，所以实际上使用的是AccessDB。
如果要切换到其他数据库，如SQL Server，只需修改：
    Database = SQLServerDB
应用层的代码可不做任何修改，就可以切换到SQL Server数据库。

历史记录（按照以下格式依次添加）：
   日期        人员	      改动情况
2023-11-21    崔树标    创建。
"""

from . import AccessDB
from . import SQLServerDB
from . import TDengineDB
 
# # 根据需要，重定向Database即可
Database = TDengineDB
